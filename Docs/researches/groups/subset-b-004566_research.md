# subset-b-004566 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_csr.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_csr.h

## Purpose

`fbnic_csr.h` is the central hardware contract for the Meta FBNIC Ethernet driver. It defines descriptor bit layouts, BAR0/BAR4 CSR register indices, queue register geometry, mailbox descriptor format, firmware version gates, interrupt constants, statistics counter addresses, TCAM/RSS table layouts, MAC/PCS/PTP/RXB/RPC/PUL register fields, and the exported register self-test enum/prototype. It has no executable control flow, but almost every runtime file depends on these constants to build descriptors, program hardware, decode debug output, collect stats, test interrupts, and communicate with firmware.

## Important APIs, Types, And Functions

Important macro families include `CSR_BIT()`, `CSR_GENMASK()`, `DESC_BIT()`, `DESC_GENMASK()`, and `FW_VER_CODE()`. Firmware compatibility gates are `MIN_FW_VER_CODE`, `MIN_FW_VER_CODE_LOG`, and `MIN_FW_VER_CODE_HIST`; they are used by firmware bringup and log enablement to reject unsupported firmware or avoid known mailbox flooding behavior. Descriptor definitions cover Tx work descriptors (`FBNIC_TWD_*`), Tx completion descriptors (`FBNIC_TCD_*`), Rx buffer descriptors (`FBNIC_BD_*`), and Rx completion descriptors (`FBNIC_RCD_*`).

Register sections are bracketed by `FBNIC_CSR_START_*` and `FBNIC_CSR_END_*` delimiters. They cover global interrupt registers, per-completion interrupt coalescing, global QM Tx/Rx registers, TCE/TMI/PTP/RXB/RPC/RPC RAM/FAB/Master/PCS/RSFEC/MAC/SIG/MAC_STAT/PUL registers, and per-queue register windows. `FBNIC_QUEUE(n)` plus `FBNIC_QUEUE_STRIDE` define the per-queue CSR window used by Tx/Rx setup, debugfs, stats, and interrupt moderation. BAR4 mailbox constants include `FBNIC_IPC_MBX_DESC_LEN`, `FBNIC_IPC_MBX()`, `FBNIC_IPC_MBX_DESC_*`, and mailbox direction indices.

The only declared function is `fbnic_csr_regs_test(struct fbnic_dev *fbd)`, returning `enum fbnic_reg_self_test_codes`. Other register dump helpers (`fbnic_csr_get_regs()` and `fbnic_csr_regs_len()`) are declared in `fbnic.h`, but use the register map from this header.

## Control Flow

There is no runtime control flow in this header. Its constants drive control flow elsewhere. `fbnic_debugfs.c` uses descriptor masks to render live Tx/Rx rings and mailbox descriptors. `fbnic_fw.c` uses mailbox register offsets and descriptor bits to initialize, publish, poll, and recycle DMA mailbox pages. `fbnic_irq.c` uses interrupt masks, vectors, and MSI-X control registers to request mailbox/MAC/NAPI interrupts and exercise the MSI-X self-test. `fbnic_hw_stats.c` uses TCE/TMI/RXB/RPC/PUL/MAC/PCS register addresses to reset and accumulate hardware counters. `fbnic_ethtool.c` uses queue/coalescing/RSS/TCAM limits and masks to validate user input and expose stats.

## State And Persistence

The file itself stores no state. It defines how state is represented in device registers and descriptors. Persistent driver behavior depends on these definitions remaining aligned with firmware and silicon: queue head/tail state, DMA addresses, descriptor ownership bits, mailbox completion bits, TCAM entries, RSS key/table storage, hardware stats, interrupt masks, and firmware version encodings are all interpreted through these masks.

## Dependencies And Integration Points

The header depends on Linux bit helpers and `FIELD_PREP/FIELD_GET` users in including files. It is included directly or indirectly by nearly all FBNIC modules through `fbnic.h` and more targeted headers. Integration points include Linux netdev Tx/Rx descriptor handling, ethtool register dump/self-test paths, firmware mailbox TLVs, devlink firmware flash/coredump health paths, debugfs visibility, and hardware monitor sensor reads through MAC-specific helpers.

## Risks And Edge Cases

Register or bitfield drift is the primary risk: a wrong mask silently corrupts descriptors or programs the wrong hardware register. Queue register formulas must stay in CSR-index units rather than byte offsets; call sites add these indices to `u32 __iomem *` BAR pointers. The page-size-dependent Rx buffer fragment macros are subtle because they encode both page address and fragment ID behavior for systems with pages larger than 4 KiB. Firmware version constants gate safety-sensitive features; lowering them can expose unsupported firmware paths, while raising them can reject otherwise usable devices. The mailbox descriptor length and address masks must remain consistent with firmware's DMA interpretation.

## Test Signals

Useful validation includes register self-test success, ethtool register dump size/version sanity, MSI-X self-test pass, successful mailbox bringup across reset, debugfs descriptor decode matching live queue movement, hardware stats increasing without obvious wrap artifacts, RSS key/table programming tests, and firmware log gating on versions below and above the documented thresholds. No executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_csr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_debugfs.c

## Purpose

`fbnic_debugfs.c` exposes FBNIC runtime diagnostics through debugfs. It renders queue descriptors, queue head/tail positions, programmed MAC/IP/action TCAM state, firmware mailbox descriptors, cached firmware logs, and PCIe outbound counters. The file is observational: it creates debugfs directories/files and formats current in-memory or CSR state through seq_file callbacks, with the only refresh side effect being explicit hardware stats collection for the PCIe stats file.

## Important APIs, Types, And Functions

Top-level lifecycle functions are `fbnic_dbg_init()` and `fbnic_dbg_exit()`, which create and remove the driver root named by `fbnic_driver_name`. Per-device functions `fbnic_dbg_fbd_init()` and `fbnic_dbg_fbd_exit()` create/remove files such as `pcie_stats`, `mac_addr`, `tce_tcam`, `act_tcam`, `ip_src`, `ip_dst`, `ipo_src`, `ipo_dst`, `fw_mbx`, and `fw_log`. Per-NAPI functions `fbnic_dbg_nv_init()` and `fbnic_dbg_nv_exit()` create `nv.%03d` subdirectories and ring descriptor files (`twq0`, `twq1`, `tcq`, `hpq`, `ppq`, `rcq`).

Descriptor output flows through `fbnic_dbg_desc_open()` and `fbnic_dbg_desc_fops`. It selects a show function from the ring doorbell offset: `fbnic_dbg_twq_desc_seq_show()`, `fbnic_dbg_tcq_desc_seq_show()`, `fbnic_dbg_bdq_desc_seq_show()`, or `fbnic_dbg_rcq_desc_seq_show()`. Decoders use CSR descriptor masks from `fbnic_csr.h` to print Tx work descriptors, Tx completion descriptors, Rx buffer descriptor IDs/addresses, and Rx completion metadata/action/timestamp/error fields.

Other show functions render classifier and firmware state: `fbnic_dbg_mac_addr_show()`, `fbnic_dbg_tce_tcam_show()`, `fbnic_dbg_act_tcam_show()`, `fbnic_dbg_ip_addr_show()` plus wrappers, `fbnic_dbg_fw_mbx_show()`, `fbnic_dbg_fw_log_show()`, and `fbnic_dbg_pcie_stats_show()`.

## Control Flow

Initialization is hierarchical. The module root is created once. Each device gets a PCI-name directory under that root. Each NAPI vector gets a subdirectory under the device directory, and the code walks the vector's Tx and Rx triads to derive hardware queue indices from `fbnic_ring_csr_base()` relative to `fbd->uc_addr0[FBNIC_QUEUE(0)]`.

When a ring file is read, `single_open()` stores the ring in `seq_file->private`. The show path first prints software ring metadata and reads hardware head/tail registers based on the ring doorbell offset. It then iterates the descriptor storage if allocated. If `ring->desc` is NULL, it reports that the ring is not allocated instead of dereferencing it.

Firmware mailbox output prints both Rx and Tx mailbox software readiness/head/tail and every raw mailbox descriptor read via `__fbnic_mbx_rd_desc()`. Firmware log output checks `fbnic_fw_log_ready()`, takes `fw_log.lock` with IRQ save, and walks entries in reverse list order to print newest-to-oldest cached messages. PCIe stats output takes RTNL, calls `fbnic_get_hw_stats()`, and prints selected `fbd->hw_stats.pcie` counters.

## State And Persistence

Debugfs dentries are kept in `fbnic_dbg_root`, `fbd->dbg_fbd`, and `nv->dbg_nv`. They are runtime-only and removed recursively during teardown. File contents are generated on read from current software state (`struct fbnic_ring`, `struct fbnic_dev`, TCAM arrays, mailbox state, firmware log buffer) and current hardware registers. Firmware log reads use the circular in-memory log buffer owned by `fbnic_fw_log.c`.

## Dependencies And Integration Points

The file depends on Linux debugfs, seq_file, PCI naming, RTNL, FBNIC ring helpers from `fbnic_txrx.h`, mailbox helpers from `fbnic_fw.c`, stats from `fbnic_hw_stats.c`, and classifier arrays maintained by MAC/RPC/RX mode code. It is integrated into device and NAPI lifecycle paths outside this file, which must call the init/exit helpers when devices and vectors appear or disappear.

## Risks And Edge Cases

Debugfs callbacks race with live device activity by design. Descriptor data can change while being printed; output should be treated as a snapshot best effort. The ring-doorbell switch assumes known FBNIC ring types; an unexpected doorbell offset returns `-EINVAL`. Firmware log display holds a spinlock while formatting each entry, so very large output could extend lock hold time. Device removal must call recursive debugfs removal before backing state is freed, or readers could access stale pointers. The PCIe stats file takes RTNL and reads hardware, so it has stronger side effects than the other views.

## Test Signals

Useful checks are debugfs tree creation/removal across probe/remove, reads of every ring file while rings are allocated and after they are freed, mailbox descriptor reads before and after firmware bringup, firmware log read returning `-ENXIO` before log init and formatted output after logs arrive, and `pcie_stats` values increasing after traffic. No executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_devlink.c

## Purpose

`fbnic_devlink.c` implements the driver's devlink surface: device allocation/registration, devlink info reporting, PLDM firmware flashing, firmware and OTP health reporters, firmware coredump collection, and helper reporting into both devlink health and the firmware log cache. It bridges Linux devlink/PLDM firmware infrastructure to FBNIC firmware mailbox TLVs and selected BAR4 OTP registers.

## Important APIs, Types, And Functions

`fbnic_devlink_alloc()`, `fbnic_devlink_free()`, `fbnic_devlink_register()`, and `fbnic_devlink_unregister()` wrap devlink allocation and lifecycle. Allocation stores the `struct fbnic_dev` in devlink private memory, sets PCI driver data, captures BAR mappings (`uc_addr0`, `uc_addr4`), DSN, PCIe MPS/read request/relaxed ordering values, and initializes `mac_addr_boundary`.

`fbnic_devlink_info_get()` publishes running and stored firmware, bootloader, UNDI versions, commit strings, and DSN serial number. Helper functions `fbnic_version_running_put()` and `fbnic_version_stored_put()` format version codes with `fbnic_mk_fw_ver_str()` and optionally add `.commit` entries.

Firmware flash uses PLDM callbacks `fbnic_pldm_match_record()` and `fbnic_flash_component()` via `fbnic_pldmfw_ops`, exposed through `fbnic_devlink_flash_update()`. Flashing maps QSPI component IDs to names, starts upgrade with `fbnic_fw_xmit_fw_start_upgrade()`, waits for firmware chunk requests, sends chunks with `fbnic_fw_xmit_fw_write_chunk()`, validates offset/length sequencing, and reports progress through devlink status notifications.

Health reporting uses `fbnic_fw_ops` and `fbnic_otp_ops`. `fbnic_fw_reporter_dump()` forces/reads firmware coredumps in TLV-sized chunks and emits a binary fmsg. `fbnic_fw_reporter_diagnose()` reports last heartbeat firmware uptime. `fbnic_devlink_fw_report()` and `fbnic_devlink_otp_check()` raise health reports and mirror messages into firmware logs when available.

## Control Flow

Info get is linear: add running mgmt, running bootloader, stored mgmt, stored bootloader, stored UNDI, then optional DSN serial. Each devlink call can abort on error.

PLDM flashing first validates PCI identity through `pldmfw_op_pci_match_record()`, then scans vendor-defined descriptors for `AntiRollbackVer`. Images older than `fbd->fw_cap.anti_rollback_version` are rejected with a devlink status update. For each supported component, a completion for `FW_WRITE_CHUNK_REQ` is registered before `FW_START_UPGRADE_REQ` so the driver can catch both firmware ACK and first chunk request. The loop waits for a completion, validates `offset == previous offset + previous length`, rejects oversized or out-of-range requests, sends data chunks, and terminates when firmware sends a finish request that collapses length to zero. On error it sends a cancel/error chunk response.

Firmware coredump dump first asks for size, handles firmware errors or zero size, allocates one completion large enough for a pointer table plus dump bytes, issues chunk reads sequentially, waits and reinitializes completion after each chunk, verifies each expected chunk pointer was consumed by the parser, then emits the full binary through devlink fmsg.

## State And Persistence

The devlink object owns `struct fbnic_dev` memory. Runtime device state includes firmware capability data, DSN, PCIe attributes, health reporter pointers, and BAR mappings. Flashing does not persist in host files; it writes device firmware storage through firmware mailbox protocol. Health reporter state persists while reporters are registered. Firmware logs are mirrored into the in-memory log ring when `fbnic_fw_log_ready()` is true.

## Dependencies And Integration Points

Dependencies include Linux devlink, PLDM firmware flashing, PCI helpers, unaligned endian helpers, FBNIC firmware mailbox functions, TLV maximum sizes, OTP CSR definitions, and firmware log support. It integrates with probe/remove lifecycle, `fbnic_fw.c` mailbox completions, `fbnic_fw_log.c` log storage, and ethtool/devlink userspace tooling.

## Risks And Edge Cases

Firmware flashing is sequencing-sensitive. Completion setup must precede the start request or the first firmware chunk request can be missed. Offset/length validation prevents malformed firmware requests from reading outside the image; changes must preserve those guards. Anti-rollback parsing assumes a vendor-defined descriptor shape of at least 21 bytes with a specific marker. Coredump allocation size is `sizeof(void *) * index_count + size`; large dumps can fail allocation. The coredump loop treats a still-non-NULL data pointer as missing data because the parser nulls entries after copying. Health reporter destroy must run for both reporters if OTP creation fails after FW reporter creation.

## Test Signals

Useful signals include `devlink dev info` showing all expected running/stored versions and serial, PLDM flash success/failure across each component ID, rejection of old anti-rollback images, timeout and malformed chunk negative paths, firmware coredump dump with multi-chunk payloads, health reports on heartbeat/OTP faults, and probe/remove reporter lifecycle. No executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_drvinfo.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_drvinfo.h

## Purpose

`fbnic_drvinfo.h` is a tiny driver identity header. It defines `DRV_NAME` as `fbnic` and `DRV_SUMMARY` as `Meta(R) Host Network Interface Driver`. These constants are used by the driver registration and metadata paths outside this file to keep the module name and user-facing summary centralized.

## Important APIs, Types, And Functions

The file exports two preprocessor constants only: `DRV_NAME` and `DRV_SUMMARY`. It declares no functions, types, or state.

## Control Flow

There is no control flow. Inclusion substitutes the driver name and summary strings at compile time.

## State And Persistence

There is no runtime state. The values become compiled-in metadata and can affect module/device names, logs, debugfs naming through nearby driver-name plumbing, and user-visible driver identification.

## Dependencies And Integration Points

The file has no includes and no direct dependencies. Integration is by consumers that include it for registration or reporting strings. Changes here ripple to any path that expects the canonical driver name.

## Risks And Edge Cases

The main risk is identity drift: changing `DRV_NAME` can alter module aliases, logs, debugfs roots, or userspace expectations. The file lacks include guards, but because it only defines idempotent string macros, repeated inclusion is normally harmless unless a caller predefines either macro differently.

## Test Signals

Useful validation is build success and checking module/device metadata, log prefixes, and user-facing driver identity after changes. No executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_drvinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_ethtool.c

## Purpose

`fbnic_ethtool.c` implements the netdev `ethtool_ops` surface for FBNIC. It exposes driver/firmware info, register dumps, coalescing, ring sizes, channel counts, RSS key/table/context management, RSS hash-field selection, RXNFC classifier rules, statistics, self-tests, timestamping, module EEPROM reads, PFC prevention tunables, pause/FEC/PHY/MAC/RMON stats, and link settings delegated to phylink. It is the main userspace control surface for changing live queue topology and receive steering state.

## Important APIs, Types, And Functions

The exported entry point is `fbnic_set_ethtool_ops()`, assigning `fbnic_ethtool_ops` to the netdev. `struct fbnic_stat` describes ethtool string, size, and offset for stats extraction. Static stats arrays cover fixed hardware stats, RXB enqueue/fifo/dequeue groups, per-Rx-queue hardware counters, and XDP queue counters. Self-test strings map to register, MSI-X, and mailbox tests.

Configuration callbacks include `fbnic_get_coalesce()`/`fbnic_set_coalesce()`, `fbnic_get_ringparam()`/`fbnic_set_ringparam()`, `fbnic_get_channels()`/`fbnic_set_channels()`, `fbnic_get_rxfh()`/`fbnic_set_rxfh()`, RXFH context create/modify/remove, `fbnic_get_rss_hash_opts()`/`fbnic_set_rss_hash_opts()`, and RXNFC get/set helpers. Live ring/channel changes use clone helpers (`fbnic_clone_create()`, `fbnic_clone_swap_cfg()`, `fbnic_clone_swap()`, `fbnic_clone_free()`) to allocate a replacement configuration before stopping the current datapath.

Classifier helpers include `fbnic_get_cls_rule_all()`, `fbnic_get_cls_rule()`, `fbnic_set_cls_rule_ins()`, `fbnic_set_cls_rule_del()`, `fbnic_clear_nfc_macda()`, and `fbnic_clear_nfc_ip_addr()`. They translate ethtool flow specs to/from FBNIC action TCAM, MAC DA TCAM, and IP TCAM state.

## Control Flow

Simple getters read cached `struct fbnic_net` or `struct fbnic_dev` state and format ethtool output. Stats collection calls `fbnic_get_hw_stats()`, snapshots `fbd->hw_stats` under its spinlock, then appends XDP ring counters with per-ring u64 stats synchronization.

Coalescing setters validate rx/tx usec and Rx frame limits against CSR field maxima, update `fbn` fields, and if the netdev is running, reprogram every NAPI vector with `fbnic_config_txrx_usecs()` and `fbnic_config_rx_frames()`.

Ring and channel setters have a two-path model. If the device is down, they update sizes/counts directly. If running, they allocate a clone, set requested config on the clone, allocate NAPI vectors/resources, stop the current datapath with `fbnic_down_noidle()`, wait for queues idle, set netif queue counts, flush old rings, swap clone and original pointers/config, bring the original netdev back up, and free old resources through the clone. Error paths restart the original stack and free partial clone resources.

RXNFC insertion only accepts `RX_CLS_LOC_ANY`, finds an unused action TCAM slot, rejects overwrites, translates supported IPv4/IPv6 TCP/UDP/user and Ethernet flows, allocates referenced MAC/IP TCAM entries through sync helpers, fills action TCAM value/mask words and destination bits, marks the rule `FBNIC_TCAM_S_UPDATE`, and writes rules/MAC/IP tables if running. Deletion marks the action TCAM for delete, unsyncs referenced MAC/IP entries, and writes updated hardware tables if running.

RSS key/table setters validate Toeplitz hash only, update packed driver key/table state, and reinitialize RSS hardware if live. Hash-field setters validate allowed RXH bits by flow category and refresh RSS/rules if live.

## State And Persistence

All state is in memory and device hardware. `struct fbnic_net` stores queue sizes, queue counts, NAPI count, coalescing values, HDS threshold, RSS key, RSS indirection tables, RSS flow hash fields, XDP program/rings, and timestamp stats. `struct fbnic_dev` stores hardware stats and TCAM arrays. Live setters persist changes to hardware registers/TCAM/RSS tables when the netdev is running; otherwise changes remain cached until open/reinit. No filesystem persistence exists.

## Dependencies And Integration Points

Dependencies include Linux ethtool netlink and classic APIs, netdevice, PCI, IPv6 helpers, phylink callbacks, FBNIC netdev lifecycle, Tx/Rx resource allocation, RSS/RPC/TCAM writers, hardware stats, firmware mailbox QSFP EEPROM reads, PTP clock, MAC pause/FEC/stats helpers, and register/MSI-X/mailbox self-tests. This file is tightly coupled to `fbnic_netdev.h`, `fbnic_txrx.h`, `fbnic_hw_stats.*`, `fbnic_fw.*`, `fbnic_mac.h`, `fbnic_rpc.c`, and phylink/time support.

## Risks And Edge Cases

Live queue reconfiguration is the highest-risk path: it must allocate all replacement resources before stopping traffic and must not fail after the "nothing can fail" point. RSS table and queue count changes interact; channel changes reset the indirection table. RXNFC insertion mutates auxiliary MAC/IP TCAM state before final action TCAM installation and must roll back newly added IP entries on allocation failure. IPv6 outer-IP handling uses `IPPROTO_IPV6` as a special user-flow signal. Overwrite is intentionally rejected until old referenced TCAM cleanup is implemented. The stats extractor assumes fields are u64-sized where registered; wrong `fbnic_stat` metadata would read invalid offsets. Module EEPROM reads only support I2C address `0x50` and rely on firmware response validation.

## Test Signals

Useful tests include `ethtool -i`, register dump, coalesce get/set including max-boundary failures, ring resizing while down and while traffic is running, channel resizing with queue-count/RSS reset checks, stats string/count alignment, XDP stats with absent rings, RXFH key/table/context create/modify/remove, RSS hash-field validation, RXNFC insert/list/get/delete for supported flow types and invalid masks/queues, offline self-tests, timestamp stats/info, QSFP EEPROM reads and timeout handling, pause/FEC/MAC/PHY/RMON stats. No executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_fw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_fw.c

## Purpose

`fbnic_fw.c` implements the FBNIC host-to-firmware mailbox and TLV protocol handling. It initializes BAR4 mailbox descriptor rings, maps DMA-backed page messages, tracks completion slots, parses firmware responses, sends requests for capabilities, ownership, heartbeats, coredumps, firmware upgrades, QSFP EEPROM reads, thermal/voltage sensor reads, log streaming, and RPC MAC sync, and exposes a mailbox self-test. It is the central runtime bridge between the driver and management firmware.

## Important APIs, Types, And Functions

Mailbox lifecycle functions are `fbnic_mbx_init()`, `fbnic_mbx_clean()`, `fbnic_mbx_poll_tx_ready()`, `fbnic_mbx_poll()`, `fbnic_mbx_flush_tx()`, `fbnic_mbx_set_cmpl()`, and `fbnic_mbx_clear_cmpl()`. Low-level descriptor helpers include `__fbnic_mbx_wr_desc()`, `__fbnic_mbx_invalidate_desc()`, `__fbnic_mbx_rd_desc()`, and reset/clean/map/unmap helpers. DMA pages are tracked in `struct fbnic_fw_mbx::buf_info`.

Request transmitters include `fbnic_fw_xmit_test_msg()`, `fbnic_fw_xmit_ownership_msg()`, `fbnic_fw_xmit_coredump_info_msg()`, `fbnic_fw_xmit_coredump_read_msg()`, `fbnic_fw_xmit_fw_start_upgrade()`, `fbnic_fw_xmit_fw_write_chunk()`, `fbnic_fw_xmit_qsfp_read_msg()`, `fbnic_fw_xmit_tsene_read_msg()`, `fbnic_fw_xmit_send_logs()`, and `fbnic_fw_xmit_rpc_macda_sync()`. Completion allocation is provided by `__fbnic_fw_alloc_cmpl()`, `fbnic_fw_alloc_cmpl()`, and `fbnic_fw_put_cmpl()`.

Parser tables use `struct fbnic_tlv_index` arrays and `fbnic_fw_tlv_parser[]`. Notable parsers handle firmware capabilities, ownership/heartbeat uptime, coredump info/data, firmware update start/chunk/finish handshakes, QSFP read responses, TSENE sensor responses, firmware logs, and TLV parser self-test echo responses.

## Control Flow

Mailbox initialization clears capability state, initializes the Tx lock, resets both descriptor rings, configures firmware interrupt auto-clear behavior, and clears stale mailbox causes. `fbnic_mbx_poll_tx_ready()` repeatedly resets the Tx ring until firmware signals an interrupt event, enables DMA read/write attributes for Tx/Rx rings, preallocates Rx pages, sends `HOST_CAP_REQ`, and polls until the parsed firmware capability response sets a management version at or above `MIN_FW_VER_CODE`.

Tx messages are allocated as TLV pages, optionally reserve a completion slot under `fw_tx_lock`, DMA-map into the Tx mailbox ring, and publish descriptors by writing upper then lower halves. Tx polling frees messages whose descriptors have firmware-complete set. Rx polling syncs DMA pages for CPU, validates descriptor length, parses TLVs, logs parse failures with a hex dump, then recycles the same page to the Rx tail.

Completion slots are keyed by expected message type and protected by `fw_tx_lock`. Parsers find completions with `fbnic_fw_get_cmpl_by_type()`, fill result-specific union fields, complete waiters, and drop krefs. `fbnic_mbx_flush_tx()` disables new Tx, evicts all outstanding completions with `-EPIPE`, and waits for already-published Tx descriptors to be consumed.

Heartbeat control uses ownership and heartbeat responses to update `last_heartbeat_response`, `firmware_time`, and `prev_firmware_time`. `fbnic_fw_check_heartbeat()` periodically detects missing responses or firmware uptime rollback, disables heartbeat reporting after a fault, and sends another heartbeat request.

## State And Persistence

State lives in `struct fbnic_dev`: `mbx[]` readiness/head/tail/buffer info, `fw_tx_lock`, `cmpl_data[]`, `fw_cap`, heartbeat jiffies, firmware uptime fields, and `fw_heartbeat_enabled`. Firmware capability parsing populates running/stored version/commit data, BMC presence/MAC addresses/allmulti flags, link speed/FEC, active slot, anti-rollback version, and BMC reinit flags. Runtime mailbox state is not persistent across reset; `fbnic_mbx_clean()` unmaps/frees DMA pages and rings are rebuilt.

## Dependencies And Integration Points

The file depends on DMA mapping, bitfield helpers, completions/krefs, delays, `fbnic_tlv` builders/parsers, CSR mailbox and PUL registers, firmware log storage, MAC/RPC TCAM state, and interrupt code that calls `fbnic_mbx_poll()`. Devlink uses coredump and firmware upgrade transmitters. Ethtool uses mailbox self-test and QSFP reads. HWMON/MAC sensor paths use TSENE reads through MAC helpers. RX mode synchronization can send RPC MAC sync messages to firmware.

## Risks And Edge Cases

Mailbox descriptor ordering is delicate: upper/lower write order differs for publish versus invalidate so firmware can detect stable descriptors. Ring-full detection leaves one unused slot; changing the ring length requires preserving power-of-two assumptions in modulo logic. Completion slots are limited (`FBNIC_MBX_CMPL_SLOTS`), so concurrent operations can return `-EXFULL` or `-EEXIST`. The capability parser disables the Tx mailbox if firmware is too old. Log parsing rejects `length >= FBNIC_FW_MAX_LOG_HISTORY`, so firmware's length convention is important. Firmware coredump and update parsers validate offsets and lengths to avoid buffer corruption. `fbnic_fw_mbx_self_test()` does not initialize its enum to success explicitly before waits; success depends on parser setting `cmpl->result` to zero and the local variable not being used on the success path except after conditions.

## Test Signals

Useful tests include mailbox ready polling on probe, capability parsing with old and current firmware, ownership take/release, heartbeat timeout and uptime rollback reporting, TLV self-test, firmware log enable/disable and historical log gating, coredump info/read multi-chunk validation, PLDM update chunk sequencing, QSFP/TSENE read success and mismatched response failures, completion slot exhaustion, mailbox flush during teardown, and DMA mapping failure injection. No executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_fw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_fw.h

## Purpose

`fbnic_fw.h` declares the firmware mailbox data structures, completion payloads, firmware capability model, mailbox APIs, firmware request APIs, firmware version formatting helpers, QSPI section IDs, heartbeat timing, TLV message IDs, capability attribute IDs, and firmware link-mode/FEC enums. It is the interface between firmware protocol implementation (`fbnic_fw.c`) and users such as devlink, ethtool, IRQ, hwmon, debugfs, MAC/RPC sync, and probe/remove lifecycle code.

## Important APIs, Types, And Functions

`struct fbnic_fw_mbx` stores mailbox readiness, head/tail indices, and per-descriptor TLV page/DMA address info. `struct fbnic_fw_ver` stores a packed version code plus commit string. `struct fbnic_fw_cap` stores running/stored firmware and bootloader versions, stored UNDI version, active slot, BMC MAC addresses, BMC flags, link speed/FEC, and anti-rollback version. `struct fbnic_fw_completion` wraps a completion, kref, result, response message type, and a union of payloads for coredump info/data, firmware update chunk offsets, QSFP EEPROM data, and sensor values.

Public APIs include mailbox lifecycle and polling (`fbnic_mbx_init()`, `fbnic_mbx_clean()`, `fbnic_mbx_set_cmpl()`, `fbnic_mbx_clear_cmpl()`, `fbnic_mbx_poll()`, `fbnic_mbx_poll_tx_ready()`, `fbnic_mbx_flush_tx()`), mailbox self-test, ownership/heartbeat, coredump, firmware upgrade, QSFP, TSENE, log streaming, RPC MAC sync, completion allocation/free, and firmware version string formatting. `fbnic_mbx_wait_for_cmpl()` waits up to `FBNIC_MBX_RX_TO_SEC`.

## Control Flow

The header defines no executable flow beyond the inline completion wait and version-format macros. It shapes flow in callers by pairing each xmit helper with the matching response message ID and completion union member. Message IDs distinguish requests and responses for host capabilities, ownership, heartbeat, coredump, firmware update, QSFP read, TSENE read, firmware logs, and RPC MAC sync.

## State And Persistence

The declared structures are embedded in `struct fbnic_dev` or allocated per mailbox operation. Firmware capability state persists in memory across normal operation and is reset by mailbox init. Completion objects persist until their kref reaches zero; parsers and waiters share them. Constants such as `FBNIC_FW_LOG_MAX_SIZE`, `FBNIC_FW_MAX_LOG_HISTORY`, and commit string sizes constrain runtime buffers and parser behavior.

## Dependencies And Integration Points

The file depends on Linux completions, Ethernet address sizing, integer types, and CSR firmware-version masks. It integrates with `fbnic_fw.c` for implementation, `fbnic_devlink.c` for info/flash/coredump, `fbnic_ethtool.c` for firmware version and EEPROM/self-test, `fbnic_fw_log.c` for log enablement, `fbnic_irq.c` for mailbox IRQ lifecycle, and MAC/RPC/hwmon paths for sensor and MAC synchronization.

## Risks And Edge Cases

Flexible array completion payloads require callers to allocate enough private storage through `__fbnic_fw_alloc_cmpl()`. `FBNIC_FW_CAP_RESP_COMMIT_MAX_SIZE` depends on ethtool firmware version string length and formatted prefix length; longer firmware commit strings are truncated. Message IDs and attribute IDs must stay synchronized with firmware. `fbnic_mbx_wait_for_cmpl()` is a long blocking wait, so callers must use it only where sleeping is allowed. The mailbox buffer model assumes single-page TLV messages and descriptor length limits from CSR definitions.

## Test Signals

Useful checks include compile-time coverage of all declared helpers, firmware version string formatting with and without commit strings, completion allocation sizes for coredump/QSFP payloads, timeout behavior from `fbnic_mbx_wait_for_cmpl()`, and ABI alignment of message/attribute IDs with firmware. No executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_fw_log.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_fw_log.c

## Purpose

`fbnic_fw_log.c` implements the driver's in-memory firmware log cache and log-stream enable/disable helpers. It allocates a fixed-size vmalloc buffer, stores variable-length firmware log entries in a circular layout, maintains a list of live entries, and asks firmware to start or stop sending logs. Debugfs and devlink health reporting consume or write this cache.

## Important APIs, Types, And Functions

Public functions are `fbnic_fw_log_init()`, `fbnic_fw_log_free()`, `fbnic_fw_log_enable()`, `fbnic_fw_log_disable()`, and `fbnic_fw_log_write()`. `fbnic_fw_log_enable()` checks readiness and suppresses historical-log requests for firmware older than `MIN_FW_VER_CODE_HIST`, then calls `fbnic_fw_xmit_send_logs()`. `fbnic_fw_log_disable()` sends a disable request and warns on unexpected errors. `fbnic_fw_log_write()` inserts a log entry with index, firmware timestamp, and message text.

## Control Flow

Initialization rejects double init, vmallocs `FBNIC_FW_LOG_SIZE`, initializes the spinlock/list, and records buffer start/end pointers. Free clears the list, zeroes size, releases the vmalloc region, and nulls pointers.

Write flow first checks `fbnic_fw_log_ready()`. Under `fw_log.lock`, it chooses the next entry address: buffer start for an empty list, otherwise 8-byte aligned after the current head entry. If the new entry would pass `data_end`, it wraps to `data_start`. It then walks the list from the tail backward and removes entries whose memory range overlaps the new entry. Finally it fills metadata, copies the string with `strscpy()`, and adds the entry at the list head.

## State And Persistence

State is `struct fbnic_fw_log` embedded in `struct fbnic_dev`: vmalloc data range, total size, entry list, and spinlock. Entries are stored inside the vmalloc buffer as `struct fbnic_fw_log_entry` plus flexible message bytes. Logs persist only in memory until driver unload, device removal, or explicit free.

## Dependencies And Integration Points

The file depends on vmalloc, spinlocks, firmware version gates, firmware send-logs TLV transmitters, and `fbnic_fw_log_ready()` from the header. It integrates with `fbnic_fw.c` log TLV parsing, `fbnic_debugfs.c` firmware log display, and `fbnic_devlink.c` health-report mirroring.

## Risks And Edge Cases

The circular allocator must remove every overlapped old entry before linking the new one. Very long messages are bounded by firmware/TLV max sizes but `msg_len` accounting includes the NUL and the code computes `entry_end = entry->msg + msg_len + 1`, so entry capacity assumptions should be audited if sizes change. Writes from unexpected firmware log messages before initialization return `-ENOSPC` and emit an error. Enablement intentionally disables historical replay on older firmware to avoid mailbox flooding from a known firmware bug.

## Test Signals

Useful tests include init/free idempotence, writing enough messages to wrap and evict old entries, debugfs newest-to-oldest output, enable requests with and without historical logs across firmware version thresholds, disable errors, and concurrent write/read lock behavior. No executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_fw_log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_fw_log.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_fw_log.h

## Purpose

`fbnic_fw_log.h` declares the firmware log cache layout and APIs. It defines the fixed log buffer size, debugfs print format, log entry structure, log container structure, readiness predicate, and init/free/enable/disable/write functions used by firmware parsing, debugfs, and devlink health paths.

## Important APIs, Types, And Functions

`FBNIC_FW_LOG_SIZE` is a 512 KiB buffer size. `FBNIC_FW_LOG_FMT` formats log index and Zephyr-like `DD:HH:MM:SS.MMM` firmware timestamp. `struct fbnic_fw_log_entry` stores list linkage, log index, timestamp, message length, and flexible message bytes. `struct fbnic_fw_log` stores buffer start/end pointers, size, list head, and spinlock. `fbnic_fw_log_ready(fbd)` checks whether `data_start` is non-NULL.

## Control Flow

The header has no runtime control flow beyond the readiness macro. It defines the contract implemented by `fbnic_fw_log.c` and consumed by callers before enabling, writing, or reading firmware logs.

## State And Persistence

The structures describe in-memory, per-device log state. Nothing is persisted to disk. The list entries live inside the vmalloc buffer owned by `struct fbnic_fw_log`.

## Dependencies And Integration Points

The header depends on Linux spinlock and integer types and forward-declares `struct fbnic_dev`. It is included by `fbnic.h`, `fbnic_fw_log.c`, `fbnic_fw.c`, `fbnic_debugfs.c`, and `fbnic_devlink.c`.

## Risks And Edge Cases

Changing `FBNIC_FW_LOG_FMT` can break debugfs consumers. Changing structure layout or buffer size affects circular allocation in `fbnic_fw_log_write()`. The flexible message array uses `__counted_by(len)`, so `len` must match allocated/stored bytes. Callers must check readiness before reading unless they intentionally want `-ENXIO`/error behavior.

## Test Signals

Useful validation includes build coverage with flexible array annotations, debugfs formatting, readiness before/after init/free, and wraparound behavior in the implementation. No executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_fw_log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_hw_stats.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_hw_stats.c

## Purpose

`fbnic_hw_stats.c` reads, resets, and accumulates FBNIC hardware statistics. It converts raw 32-bit and split 64-bit hardware counters into monotonically increasing software counters, grouped by PHY/FEC/PCS, MAC, TMI, TTI, RPC, RXB, per-queue RDE, and PCIe/PUL categories. Ethtool and debugfs use these accumulated counters for user-visible stats.

## Important APIs, Types, And Functions

Public functions are `fbnic_stat_rd64()`, `fbnic_reset_hw_stats()`, `fbnic_init_hw_stats()`, `fbnic_get_hw_q_stats()`, `fbnic_get_hw_stats32()`, and `fbnic_get_hw_stats()`. Internal helpers are organized per stats block: reset/get for TMI, TTI, RPC, RXB fifo/enqueue/dequeue, per-queue Rx hardware stats, PCIe stats, PHY stats, and MAC stats.

`fbnic_hw_stat_rst32()`/`fbnic_hw_stat_rd32()` snapshot and accumulate 32-bit counters. `fbnic_hw_stat_rst64()`/`fbnic_hw_stat_rd64()` do the same for split 64-bit counters using `fbnic_stat_rd64()`. `fbnic_stat_rd64()` reads upper-lower-upper and returns a stable full value when upper does not change, or only the upper bits with a warning when the upper half changes too quickly.

## Control Flow

Initialization calls `spin_lock_init()` and then `fbnic_reset_hw_stats()`. Reset paths record current hardware counter baselines without clearing `value`, allowing counters to continue across device resets or power transitions after the initial zeroed allocation. `fbnic_reset_hw_stats()` resets spinlock-protected PHY/TMI/TTI/RPC/RXB/RDE/PCIe state, then resets MAC stats outside the spinlock under RTNL assumptions once a netdev exists.

`fbnic_get_hw_stats32()` locks `hw_stats.lock` and updates only 32-bit-style counters plus PHY 32-bit callbacks. `fbnic_get_hw_stats()` locks, updates 32-bit counters first, then reads wider byte/PCIe counters. Per-queue helper `fbnic_get_hw_q_stats()` updates RDE queue counters under the same lock. MAC stats are fetched via `fbd->mac` callbacks in reset and via ethtool-specific paths outside this file.

## State And Persistence

Each `struct fbnic_stat_counter` stores accumulated `value`, old hardware snapshot, and a `reported` flag used by MAC/ethtool code. State is in `fbd->hw_stats` and persists in memory for the life of the device object. Baseline snapshots are reset after hardware reset, but `value` is intentionally not cleared except by initial allocation.

## Dependencies And Integration Points

The file depends on CSR register definitions, `rd32()`, device warnings, spinlocks, RTNL assertions, and MAC operation callbacks for FEC/PCS/MAC/pause/control/RMON stats. It integrates with `fbnic_ethtool.c` stats callbacks, `fbnic_debugfs.c` PCIe stats display, and device reset/open paths that call reset/init.

## Risks And Edge Cases

Split 64-bit reads can be inconsistent under very fast counter updates; the implementation warns once and drops lower bits for that sample. Resetting baselines without clearing `value` is deliberate; code that expects reset-to-zero after PCI recovery would be wrong. `fbnic_reset_rxb_stats()` iterates `FBNIC_RXB_INTF_INDICES` for enqueue/dequeue arrays, which must remain compatible with array sizes from the header. MAC stats rely on RTNL rather than the hw_stats spinlock once registered, so callers must respect that locking contract.

## Test Signals

Useful tests include stats starting at zero after probe despite nonzero hardware counters, monotonic increases across traffic and reset, wraparound handling for 32-bit counters, split-64 warning behavior under simulated fast updates, per-queue stats bounded by `fbd->max_num_queues`, ethtool stats string/value alignment, and debugfs PCIe stats refresh. No executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_hw_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_hw_stats.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_hw_stats.h

## Purpose

`fbnic_hw_stats.h` declares the software statistics model used by FBNIC hardware stat collection and ethtool/debugfs reporting. It defines counter wrappers, grouped hardware statistic structures, the aggregate `struct fbnic_hw_stats`, and public stats collection/reset APIs.

## Important APIs, Types, And Functions

`struct fbnic_stat_counter` is the base type: accumulated `value`, old 32-bit or 64-bit hardware snapshot, and `reported` flag. `struct fbnic_hw_stat` pairs frame and byte counters. Group structures include FEC, PCS lane symbol errors, Ethernet control stats, RMON histograms, pause stats, Ethernet MAC stats, PHY stats, MAC stats, TMI, TTI, RPC, RXB enqueue/fifo/dequeue, per-queue hardware stats, PCIe stats, and the aggregate `struct fbnic_hw_stats`.

Public functions are `fbnic_stat_rd64()`, `fbnic_reset_hw_stats()`, `fbnic_init_hw_stats()`, `fbnic_get_hw_q_stats()`, `fbnic_get_hw_stats32()`, and `fbnic_get_hw_stats()`.

## Control Flow

The header declares data and functions only. Runtime flow is implemented in `fbnic_hw_stats.c`, while ethtool and debugfs access the structures directly for reporting.

## State And Persistence

`struct fbnic_hw_stats` is embedded in `struct fbnic_dev`. Its spinlock protects most stats access. Counter values persist in memory across hardware resets because reset code refreshes baselines rather than clearing accumulated values. Some MAC-related subgroups are explicitly not updated by `fbnic_get_hw_stats()` and are fetched by MAC/ethtool-specific callbacks.

## Dependencies And Integration Points

The header depends on Linux ethtool histogram sizing, spinlocks, and CSR constants such as `FBNIC_PCS_MAX_LANES`, `FBNIC_RXB_*_INDICES`, and `FBNIC_MAX_QUEUES`. It is included through `fbnic.h` and consumed by stats implementation, ethtool, debugfs, and MAC-specific stats helpers.

## Risks And Edge Cases

Any structure layout change must be reflected in `fbnic_ethtool.c` offset tables. Array sizes are hardware-defined; changing CSR constants changes memory footprint and ethtool stats count. The `reported` flag is meaningful for MAC callbacks and must be maintained when adding counters. Locking comments for not-updated-by-`fbnic_get_hw_stats()` subgroups must remain accurate.

## Test Signals

Useful checks include compile-time struct offset users, ethtool stats count/string alignment, no out-of-bounds access for queue/RXB arrays, and locking validation around stats readers. No executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_hw_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_hwmon.c

## Purpose

`fbnic_hwmon.c` registers a Linux hwmon device for FBNIC temperature and voltage readings. It maps hwmon sensor types to FBNIC MAC sensor IDs and delegates actual sensor reads to the active MAC implementation.

## Important APIs, Types, And Functions

Public functions are `fbnic_hwmon_register()` and `fbnic_hwmon_unregister()`. Internal callbacks are `fbnic_hwmon_sensor_id()`, `fbnic_hwmon_is_visible()`, and `fbnic_hwmon_read()`. `fbnic_hwmon_ops`, `fbnic_hwmon_info`, and `fbnic_chip_info` describe the hwmon chip with one temperature input channel and one voltage input channel.

## Control Flow

Registration first checks `IS_REACHABLE(CONFIG_HWMON)`. If hwmon support is unavailable, it does nothing. Otherwise it calls `hwmon_device_register_with_info()` with chip name `fbnic`, driver data `fbd`, and the chip info. Registration failures are logged as notices and stored as NULL. Unregister similarly returns early if hwmon is unavailable or no hwmon device is registered.

Read flow receives a hwmon type and attribute, maps supported types (`hwmon_temp`, `hwmon_in`) to `FBNIC_SENSOR_TEMP` or `FBNIC_SENSOR_VOLTAGE`, and calls `fbd->mac->get_sensor(fbd, id, val)`. Visibility exposes only `temp_input` and `in_input` as read-only (`0444`).

## State And Persistence

The only state is `fbd->hwmon`, a registered hwmon device pointer. Sensor values are read on demand and not cached here. There is no persistence beyond device lifetime.

## Dependencies And Integration Points

The file depends on Linux hwmon APIs, `fbnic.h`, and `fbnic_mac.h` sensor IDs and MAC operation callbacks. Sensor retrieval likely uses firmware TSENE mailbox helpers through MAC-specific code, but this file remains MAC-agnostic.

## Risks And Edge Cases

If `fbd->mac` or `mac->get_sensor` is not initialized before registration/read, hwmon reads can fail or dereference invalid callbacks; lifecycle ordering must ensure MAC ops are ready. Only one voltage and one temperature channel are exposed, with no labels or limits. The `IS_REACHABLE(CONFIG_HWMON)` guard allows the same object to build when hwmon is modular/unavailable, but callers should not assume `fbd->hwmon` is non-NULL after register.

## Test Signals

Useful checks include registration with hwmon enabled/disabled, sysfs visibility for temp and voltage input only, successful reads returning MAC-provided values, error propagation from `get_sensor`, and clean unregister on remove. No executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_irq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_irq.c

## Purpose

`fbnic_irq.c` owns MSI-X vector allocation, firmware mailbox interrupt setup/teardown, MAC/PCS link interrupt setup/teardown, generic IRQ request/free wrappers, the MSI-X self-test, and NAPI vector IRQ sharing/refcounting. It connects PCI IRQ vectors and FBNIC interrupt CSRs to mailbox polling, phylink link-change reporting, and Tx/Rx NAPI cleanup.

## Important APIs, Types, And Functions

Firmware mailbox lifecycle is `fbnic_fw_request_mbx()` and `fbnic_fw_free_mbx()`, with handler `fbnic_fw_msix_intr()` and helper `__fbnic_fw_enable_mbx()`. MAC link IRQ lifecycle is `fbnic_mac_request_irq()` and `fbnic_mac_free_irq()`, with handler `fbnic_mac_msix_intr()`. Generic wrappers are `fbnic_synchronize_irq()`, `fbnic_request_irq()`, and `fbnic_free_irq()`.

MSI-X test support uses `struct fbnic_msix_test_data`, `fbnic_irq_test()`, and `fbnic_msix_test()`. NAPI IRQ functions are `fbnic_napi_name_irqs()`, `fbnic_napi_request_irq()`, and `fbnic_napi_free_irq()`. Global vector allocation is handled by `fbnic_alloc_irqs()` and `fbnic_free_irqs()`.

## Control Flow

`fbnic_alloc_irqs()` requests MSI-X vectors from PCI, with a minimum of non-NAPI vectors plus one data vector and a target of non-NAPI vectors plus up to online CPUs/Rx queue maximum. It records `fbd->num_irqs` and warns if fewer than desired were allocated.

Mailbox IRQ request obtains vector `FBNIC_FW_MSIX_ENTRY`, requests a threaded IRQ with `IRQF_ONESHOT | IRQF_NO_AUTOEN`, initializes/polls the mailbox ready state, enables the IRQ, and unmasks the firmware interrupt bit. The mailbox handler polls firmware messages and unmasks the vector through `FBNIC_INTR_MASK_CLEAR(0)`.

MAC IRQ request obtains vector `FBNIC_PCS_MSIX_ENTRY`, installs a hard IRQ handler, maps PCS cause to the vector through `FBNIC_INTR_MSIX_CTRL()`, and clears an RXB mapping. The MAC handler asks MAC ops for a link event; no-event paths unmask and exit, while link-down detection calls `phylink_pcs_change(fbn->pcs, false)`.

`fbnic_msix_test()` requests temporary IRQ handlers for NAPI vectors, then for each vector tests masked set, unmask delivery, no duplicate delivery on mask clear, unmasked delivery, status clear, and mask set behavior. It cleans up hardware status/mask bits and frees IRQs on all paths.

NAPI request/free uses `fbd->napi_irq[i].users` so multiple NAPI vector users can share an IRQ allocation and free it only when the last user releases it.

## State And Persistence

State is in `fbd->fw_msix_vector`, `fbd->mac_msix_vector`, `fbd->num_irqs`, and `fbd->napi_irq[]` names/user counts. Interrupt masks and MSI-X control mappings live in device CSRs. IRQ allocations persist until explicit free or PCI vector free.

## Dependencies And Integration Points

The file depends on Linux PCI IRQ vector APIs, request/free IRQ, FBNIC CSR interrupt registers, mailbox polling from `fbnic_fw.c`, MAC ops and phylink, netdev-private `struct fbnic_net`, and Tx/Rx NAPI handler `fbnic_msix_clean_rings()`. Ethtool offline self-test calls `fbnic_msix_test()`.

## Risks And Edge Cases

Mailbox request sets `fbd->fw_msix_vector` after attempting enable; if enable fails and the vector is freed, the stored vector is still assigned before return in the current code path, so callers must handle failure carefully or this may leave stale state. IRQ teardown must mask/synchronize before freeing to avoid handlers re-unmasking disabled vectors. MSI-X self-test temporarily requests all data-vector IRQs and manipulates global interrupt masks/status; it should only run offline. NAPI IRQ user refcounts must remain balanced or vectors leak or are freed while still in use.

## Test Signals

Useful tests include successful vector allocation with expected warning when fewer vectors are available, mailbox IRQ bringup and teardown across reset, MAC link-down interrupt propagation to phylink, NAPI IRQ request/free refcount balance, offline MSI-X self-test pass and each failure code under fault injection, and no interrupts after free. No executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_irq.c -->
