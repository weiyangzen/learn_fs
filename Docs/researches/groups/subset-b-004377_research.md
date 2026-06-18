# subset-b-004377 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_ethtool.c

## Purpose

`bnxt_ethtool.c` is the Broadcom NetXtreme-C/E driver's ethtool control surface. It binds the netdev ethtool operations table to driver state and firmware HWRM commands for coalescing, ring/channel sizing, RSS and RX flow classification, link modes, FEC, pause, EEE, WOL, NVM/firmware flashing, module EEPROM access, diagnostics, dumps, timestamp capability reporting, and standardized statistics.

The file is mostly synchronous control-plane code. It translates Linux ethtool requests into `struct bnxt` fields and HWRM messages, often closing/reopening the NIC when a setting requires ring or VNIC reprogramming. There is no filesystem persistence; lasting effects are in firmware/NVM for flash and NVM writes, in device firmware state for link/FEC/LED/PTP filter settings, and in `struct bnxt` runtime fields for driver-visible configuration.

## Important APIs and functions

- `bnxt_ethtool_ops` exports the full ethtool operation table, including coalesce, rings, channels, RSS, RX NFC, link settings, FEC, pause, EEPROM/NVM, module EEPROM by page, self-test, dump, timestamp, RMON, MAC/PHY/control, and PTP stats callbacks.
- Coalesce and ring/channel sizing:
  - `bnxt_get_coalesce()` and `bnxt_set_coalesce()` expose RX/TX completion moderation, IRQ moderation, adaptive RX DIM, CQE timer-reset mode, and stats timer coalescing.
  - `bnxt_get_ringparam()` and `bnxt_set_ringparam()` expose descriptor counts and TCP data split/HDS constraints, including the larger TX minimum needed when software UDP GSO is active.
  - `bnxt_get_channels()` and `bnxt_set_channels()` negotiate shared versus separate RX/TX rings, XDP TX rings, traffic classes, firmware ring resource limits, RSS indirection resizing, and reopen/reserve flows.
- Statistics:
  - Static string/offset tables enumerate ring, TPA, software, port, extended port, priority-to-CoS, FEC, RMON, MAC, PHY, pause, PTP, and link-ext stats.
  - `bnxt_get_sset_count()`, `bnxt_get_strings()`, and `bnxt_get_ethtool_stats()` must stay aligned so ethtool string counts match the produced values.
  - `bnxt_get_fec_stats()`, `bnxt_get_eth_phy_stats()`, `bnxt_get_eth_mac_stats()`, `bnxt_get_eth_ctrl_stats()`, `bnxt_get_rmon_stats()`, `bnxt_get_ptp_stats()`, and `bnxt_get_link_ext_stats()` feed newer ethtool statistic groups from the same DMA-backed port stats snapshots and PTP counters.
- RX classification and RSS:
  - `bnxt_get_rxnfc()` and `bnxt_set_rxnfc()` implement flow rule listing, retrieval, insertion, and deletion.
  - `bnxt_add_l2_cls_rule()` programs legacy L2 destination MAC/VLAN filters.
  - `bnxt_add_ntuple_cls_rule()` validates IPv4/IPv6/TCP/UDP/ICMP flow specs, maps ethtool masks into driver `flow_keys`/`bnxt_flow_masks`, supports drop, ring destination, and RSS context actions, and allocates firmware CFA ntuple filters.
  - `bnxt_get_rxfh()`, `bnxt_set_rxfh()`, `bnxt_create_rxfh_context()`, `bnxt_modify_rxfh_context()`, and `bnxt_remove_rxfh_context()` expose default and per-context RSS indirection/key operations.
  - `bnxt_get_rxfh_fields()` and `bnxt_set_rxfh_fields()` translate ethtool RX hash field selection into firmware RSS hash-type bits and enforce capability gates for UDP, AH/ESP, and IPv6 flow-label hashing.
- Link, pause, FEC, and EEE:
  - `bnxt_get_link_ksettings()` maps firmware link info into ethtool supported/advertising/lp-advertising mode bitmaps across media, NRZ/PAM4/PAM4-112 signaling, lanes, autoneg, pause, and FEC.
  - `bnxt_set_link_ksettings()` updates advertised speeds for autoneg or forces a supported non-autoneg speed through `bnxt_force_link_speed()`.
  - `bnxt_get_fecparam()` and `bnxt_set_fecparam()` convert firmware FEC capability/configuration to ethtool AUTO/OFF/BASER/RS/LLRS and apply HWRM PHY config.
  - `bnxt_get_pauseparam()` and `bnxt_set_pauseparam()` manage flow-control autoneg and forced pause settings under `link_lock`.
  - `bnxt_get_eee()` and `bnxt_set_eee()` maintain `bp->eee`, validate autoneg and advertised EEE modes, and call link-setting firmware programming.
- NVM, firmware, and package update:
  - `bnxt_hwrm_nvm_get_dev_info()`, `bnxt_find_nvram_item()`, `bnxt_get_nvram_item()`, `bnxt_flash_nvram()`, `bnxt_get_nvram_directory()`, `bnxt_get_eeprom()`, and `bnxt_set_eeprom()` implement ethtool EEPROM/NVRAM access through HWRM.
  - `bnxt_flash_device()` dispatches ethtool flash requests to package install or raw firmware/microcode/NVM item writes.
  - `bnxt_flash_firmware()` validates APE-bin headers and CRC before writing and requesting a firmware reset.
  - `bnxt_flash_microcode()` validates the trailer signature, directory type, trailer length, and CRC before writing.
  - `bnxt_flash_package_from_fw_obj()` resizes/defrags the UPDATE NVM entry if needed, streams a package through HWRM_NVM_MODIFY in batch chunks, runs HWRM_NVM_INSTALL_UPDATE, retries selected defrag/no-space paths, and maps firmware package errors to Linux errors/extack strings.
- Module EEPROM and LEDs:
  - `bnxt_get_module_info()`, `bnxt_get_module_eeprom()`, `bnxt_get_module_eeprom_by_page()`, and `bnxt_set_module_eeprom_by_page()` read/write optical module EEPROM pages through HWRM I2C operations, with trusted-VF, module status, firmware version, and bank-select checks.
  - `bnxt_set_phys_id()` drives adapter LEDs using `HWRM_PORT_LED_CFG`.
- Diagnostics and dumps:
  - `bnxt_self_test()` combines firmware self-tests, IRQ tests, and offline MAC/PHY/external loopback tests.
  - `bnxt_run_loopback()` builds a test SKB, maps it for DMA, transmits one descriptor, polls completions, and validates returned RX data.
  - `bnxt_reset()` implements ethtool reset for chip and application processor reset bits with PF, VF-assignment, firmware-version, and hot-reset checks.
  - `bnxt_set_dump()`, `bnxt_get_dump_flag()`, and `bnxt_get_dump_data()` configure and retrieve firmware/driver coredumps.
- Initialization:
  - `bnxt_ethtool_init()` queries PCIe stats length, package version, and firmware self-test names/masks/timeouts.
  - `bnxt_ethtool_free()` releases `bp->test_info`.

## Control flow

Most ethtool callbacks start by deriving `struct bnxt *bp = netdev_priv(dev)`, validating PF/VF, firmware capability, link/ring state, and requested values, then either update cached driver fields directly or allocate an HWRM request with `hwrm_req_init()`. Requests that need response contents use `hwrm_req_hold()` and always call `hwrm_req_drop()` after parsing.

Settings that affect live rings or VNIC topology generally close the NIC, mutate `bp` configuration, and reopen it. `bnxt_set_ringparam()` closes only if running, updates ring sizes and HDS flags, calls `bnxt_set_ring_params()`, reopens, then calls `netdev_update_features()`. `bnxt_set_channels()` validates the requested ring layout and RSS table resize, closes with reset-style semantics if running, resizes ethtool RSS contexts when needed, updates ring counts and flags, recomputes completion rings, and either reopens or reserves rings while down. RSS hash-field changes and default RSS key/table changes also close/reopen when the device is running.

RX classification flows are protected by RCU while listing or finding existing filters. Insertions allocate a new driver filter, take a default L2 filter reference for ntuple filters, reject unsupported masks/actions, check duplicates in the hash table, insert into driver tables, then allocate the firmware filter. If firmware allocation fails, the driver table entry is removed and the allocation is freed. Deletions locate the filter under RCU, then call the matching HWRM free routine and driver deletion helper outside the read-side critical section.

Link setting flow holds `bp->link_lock` around shared `bnxt_link_info` updates. Autoneg requests update advertising masks with `bnxt_set_ethtool_speeds()` and may preserve pause autoneg. Forced speed requests reject Base-T and half duplex, derive firmware speed/signaling/lanes through `bnxt_force_link_speed()`, and program firmware if the netdev is running.

Firmware flashing has two paths. Region values over 16 bits or all-regions are treated as package installs: request firmware from the kernel firmware loader, ensure UPDATE area size, stream chunks to HWRM_NVM_MODIFY, then run HWRM_NVM_INSTALL_UPDATE. Small region values are treated as a directory type: executable APE-bin and microcode formats are validated with header/trailer/CRC helpers before writing, while non-executable NVM items are written directly. Successful executable firmware writes may trigger firmware reset requests.

Self-tests are split between online firmware tests and offline loopback tests. Offline tests reject active VFs/shared PF conditions, close the NIC, run firmware tests, half-open rings, enable MAC/PHY/external loopback, send and poll a synthetic packet, then close half-open state and reopen the NIC.

## State and persistence behavior

- Runtime driver state updated here includes `bp->msg_enable`, `rx_coal`, `tx_coal`, `stats_coal_ticks`, `current_interval`, ring sizes/counts, `BNXT_FLAG_DIM`, `BNXT_FLAG_SHARED_RINGS`, `BNXT_FLAG_HDS`, RSS hash config/delta/key/table flags, `num_rss_ctx`, filter tables/counts, WOL flag, EEE settings, `dump_flag`, `num_tests`, `test_info`, `pcie_stat_len`, and appended package version in `fw_ver_str`.
- Link state mutations are staged in `bp->link_info` and become device state when HWRM PHY/MAC config succeeds.
- RSS contexts persist in the kernel ethtool xarray and private `struct bnxt_rss_ctx`, with DMA coherent VNIC RSS tables owned by driver VNIC cleanup helpers.
- NVM writes, package installs, firmware flashes, UPDATE entry resize/defrag, and directory erases persist in device nonvolatile memory.
- Firmware resets, LED states, PFC watchdog timeout, WOL filters, module EEPROM writes, and timestamp filters persist in device/firmware state at least until reset or later reconfiguration.
- Statistics are read from DMA-backed or accumulated driver counters; this file does not own their producer side.

## Dependencies and integration points

- Linux ethtool core, including legacy ioctl-style callbacks and netlink-aware extack variants.
- Linux netdev/rtnl assumptions for callbacks that close/open NICs, update features, resize RSS contexts, and interact with netdev queues.
- Firmware/HWRM support via `bnxt_hwrm.h`, `<linux/bnxt/hsi.h>`, and driver helpers in `bnxt.c`, `bnxt_hwrm.c`, `bnxt_ptp.c`, `bnxt_coredump.c`, filter/VNIC code, and ring setup code.
- DMA coherent slices from the HWRM request framework for NVM, PCIe stats, module EEPROM, and package update buffers.
- Kernel firmware loader for `flash_device` paths.
- PTP integration via `bnxt_get_ts_info()` and PTP stats from `bp->ptp_cfg`.
- XDP and software UDP GSO constraints via `bnxt_xdp.h` and `bnxt_gso.h`.

## Risks and edge cases

- String/count/stat arrays must remain exactly aligned. Capability-dependent stat counts make off-by-one or stale string exposure easy when firmware stat structures grow.
- Closing/reopening the NIC in ethtool setters can race conceptually with traffic, XDP, ULP/RDMA, and VF state; callers rely on broader netdev serialization and driver open/close correctness.
- `bnxt_set_ringparam()` only allows enabling TCP data split from disabled/unknown states and rejects disabling from enabled through one path; HDS/XDP interactions must be preserved.
- RSS table resizing must coordinate default and per-context indirection arrays; failed `ethtool_rxfh_ctxs_can_resize()` or inability to resize while contexts exist must leave old state untouched.
- RX classification supports only a constrained subset of ethtool masks. Incorrect acceptance can program overly broad or unsupported firmware filters; incorrect rejection can break user workflows.
- NVM/package update is high risk: chunk flags, UPDATE entry sizing, defrag retry state, response ownership, and firmware error-code mapping all affect persistent device contents.
- `bnxt_parse_pkglog()` mutates the NVM log buffer in place and assumes tab/newline field formatting.
- Module EEPROM write support is gated but still writes transceiver EEPROM through firmware; page/bank/offset validation is largely delegated to firmware.
- Offline self-test changes loopback and link state and depends on half-open ring state; failure before reopen can leave device down if surrounding cleanup changes regress.
- `bnxt_reset()` deliberately leaves reset bits set if unsupported or failed; callers inspect `*flags` to know what was handled.

## Test signals

- Build with PF/VF, P5/P7, `CONFIG_PTP_1588_CLOCK`, `CONFIG_BNXT_HWMON`, XDP, and UDP GSO feature combinations.
- Ettool smoke tests: `-c/-C`, `-g/-G`, `-l/-L`, `-k/-K` feature recalculation, `-x/-X`, `--show-rxfh-context`, RSS context create/modify/delete, `-n/-N`, `--show-fec/--set-fec`, pause, EEE, WOL, reset, dump, stats, and module EEPROM by page.
- Firmware/NVM fault injection for HWRM timeouts, busy, access denied, no space, anti-rollback, invalid package, defrag retry, and DMA allocation failures.
- Ring/channel live-change tests with traffic, multiple traffic classes, XDP attached, software UDP GSO enabled, and RSS contexts present.
- RX filter tests for L2, IPv4/IPv6 user flows, TCP/UDP, ICMP, drop action, ring action, RSS context action, duplicate filters, deletion, and VF ring cookie validation.
- Link tests across copper, backplane, DAC, fiber, NRZ/PAM4/PAM4-112, lane counts, autoneg fallback, unsupported forced speed, FEC modes, pause autoneg, and link-ext-state reasons.
- Self-test validation should include online-only, offline, external loopback requested/not available, RDMA loaded, active VFs, DMA mapping failure, and IRQ selftest failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_ethtool.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_ethtool.h

## Purpose

`bnxt_ethtool.h` is the shared declaration header for the BNXT ethtool implementation. It exposes the driver's `struct ethtool_ops`, public helper functions used by other BNXT modules, LED request layout helpers, firmware reset bit masks, register dump length, and flow-rule protocol constants.

## Important APIs, types, and macros

- `struct bnxt_led_cfg` mirrors the packed LED fields embedded in `struct hwrm_port_led_cfg_input`; `bnxt_set_phys_id()` casts the firmware request LED field area to this structure.
- `BNXT_LED_DFLT_ENA`, `BNXT_LED_DFLT_ENA_SHIFT`, and `BNXT_LED_DFLT_ENABLES(x)` build the per-LED `enables` bitmask for HWRM LED configuration.
- `BNXT_FW_RESET_AP` and `BNXT_FW_RESET_CHIP` define ethtool reset bitmasks shifted into `ETH_RESET_SHARED_SHIFT`.
- `BNXT_PXP_REG_LEN` defines the base PCIe/register dump region length before optional PCIe stats.
- `BNXT_IP_PROTO_FULL_MASK` and `BNXT_IP_PROTO_WILDCARD` define ethtool ntuple protocol-mask conventions used for IP_USER/IPV6_USER flow validation.
- Public exports include RSS indirection size, link-speed conversion helpers, NVM get/find/read/write helpers, firmware reset, firmware package flashing from an already-loaded firmware object, package info extraction, and ethtool init/free.

## Control flow role

The header itself has no executable control flow, but it forms the interface between `bnxt_ethtool.c` and the rest of the driver. Link-speed conversion helpers are reused outside ethtool for translating firmware speeds. NVM helpers are callable by other modules that need package or directory access without duplicating HWRM details. `bnxt_ethtool_init()` and `bnxt_ethtool_free()` are lifecycle hooks called from device setup/teardown.

## State and persistence behavior

No state is stored in this header. Its declarations operate on `struct bnxt`, `struct net_device`, firmware responses, and NVM data buffers owned by callers. The reset and NVM helpers declared here can trigger persistent firmware/NVM changes when implemented in `bnxt_ethtool.c`.

## Dependencies and integration points

- Requires BNXT core types such as `struct bnxt`, `struct net_device`, HWRM NVM response types, and kernel `struct firmware`.
- Includes firmware constants from HWRM headers indirectly through users.
- Integrated by BNXT core initialization for `bnxt_ethtool_ops` registration and by modules that need link/NVM helpers.

## Risks and edge cases

- The file declares `bnxt_find_nvram_item()` twice with identical signatures. This is harmless in C but is a maintenance smell and can hide future prototype drift.
- `struct bnxt_led_cfg` relies on matching the firmware request field layout exactly; packing or field-size changes in HWRM structures would break the cast in `bnxt_set_phys_id()`.
- Reset masks must remain aligned with Linux ethtool reset semantics and the driver's implementation in `bnxt_reset()`.

## Test signals

- Compile coverage for all translation units including this header.
- Ettool LED identification, reset, link-speed conversion, and NVM helper users should build without prototype mismatch.
- Static checks should flag duplicate declarations or endian field misuse if signatures change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_ethtool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_fw_hdr.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_fw_hdr.h

## Purpose

`bnxt_fw_hdr.h` defines the on-file binary header and trailer formats used by BNXT firmware and microcode flashing paths. `bnxt_ethtool.c` uses these definitions to validate firmware image signatures, code type, device family, trailer metadata, and CRC placement before writing images to device NVM.

## Important APIs, types, and macros

- `BNXT_FIRMWARE_BIN_SIGNATURE` identifies APE-bin style firmware images.
- `BNXT_UCODE_TRAILER_SIGNATURE` identifies microcode/pre-boot trailer records.
- `enum SUPPORTED_FAMILY` names legacy Broadcom device families; `bnxt_flash_firmware()` currently requires `DEVICE_CUMULUS_FAMILY` for this driver path.
- `enum SUPPORTED_CODE` enumerates firmware code types such as bootcode, APE patch, KONG, BONO, and ChiMP patch. The flashing code maps NVM directory types to these values.
- `enum SUPPORTED_MEDIA` is a firmware-image metadata field.
- `struct bnxt_fw_header` describes the leading APE-bin header, including signature, flags, code type, device family, media, version string, and version bytes.
- `struct bnxt_ucode_trailer` describes the trailing microcode metadata, including RSA signature bytes, flags, version fields, directory type, trailer length, trailer signature, and CRC.

## Control flow role

The header is passive. `bnxt_flash_firmware()` casts firmware data to `struct bnxt_fw_header`, checks the signature/code type/device family, and validates the final CRC word. `bnxt_flash_microcode()` casts the end of the firmware data to `struct bnxt_ucode_trailer`, checks the signature, directory type, and trailer length, then validates CRC.

## State and persistence behavior

No runtime state is defined. These structures describe persistent firmware files and NVM payload metadata. Incorrect interpretation can affect whether persistent firmware is accepted or rejected before flashing.

## Dependencies and integration points

- Uses Linux fixed-width endian types such as `__le16` and `__le32`.
- Integrated by `bnxt_ethtool.c` flash paths and indirectly by ethtool `flash_device`.
- Tied to Broadcom firmware package/file format contracts, not to Linux kernel-internal persistence.

## Risks and edge cases

- Structures are not explicitly marked packed; the field layout relies on natural C layout matching the binary format. Current fields are byte arrays and little-endian integers arranged to avoid surprising padding, but format changes must be checked carefully.
- Firmware validation currently hard-codes accepted device family for APE-bin images; broader hardware support would require deliberate changes.
- CRC location is assumed to be the last 32 bits of the image, independent of the trailer's internal `chksum` field.

## Test signals

- Unit-style validation with known-good and malformed firmware buffers for short size, bad signature, wrong code type, wrong device family, bad trailer length, wrong directory type, and CRC mismatch.
- Build checks on 32-bit and 64-bit architectures for structure size/layout assumptions.
- Flash dry-run or firmware-loader tests should confirm each NVM directory type selects the expected header or trailer validation path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_fw_hdr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_gso.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_gso.c

## Purpose

`bnxt_gso.c` implements software UDP L4 GSO/USO fallback for BNXT hardware that lacks native UDP segmentation offload. It converts one large UDP GSO SKB into multiple hardware TX packets by building per-segment inline headers, mapping payload chunks through the kernel TSO helper, emitting normal BNXT TX descriptors, and preserving a single SKB ownership model until the final segment completes.

## Important APIs and functions

- `bnxt_sw_gso_lhint()` maps a segment's total length to BNXT TX length-hint flags.
- `bnxt_sw_udp_gso_xmit()` is the exported transmit path used by the main BNXT TX code when `NETIF_F_GSO_UDP_L4` is requested but `BNXT_FLAG_UDP_GSO_CAP` is absent.
- It uses kernel TSO helpers: `tso_start()`, `tso_build_hdr()`, `tso_dma_map_init()`, `tso_dma_map_count()`, `tso_dma_map_next()`, and `tso_dma_map_completion_save()`.
- It uses BNXT TX helpers/macros from the main data path: `bnxt_tx_avail()`, `bnxt_inline_avail()`, `bnxt_xmit_get_cfa_action()`, `bnxt_init_ext_bd()`, `SET_TX_OPAQUE()`, `TX_BD_CNT()`, `NEXT_TX()`, `RING_TX()`, `TX_RING()`, `TX_IDX()`, and `bnxt_db_write()`.

## Control flow

The function starts by deriving header length, MSS, total UDP payload, and segment count. It drops malformed cases where only one segment would be produced. Before touching descriptors, it computes an upper bound of required BDs as `3 * num_segs + nr_frags + 1`, checks TX descriptor availability, and separately checks inline-header slot availability because per-segment headers live in `txr->tx_inline_buf`.

After initializing a TSO DMA map, it prepares VLAN/CFA metadata and checksum offload flags. For each segment, it selects an inline header slot, builds the segment header, clears stale UDP and IPv4 checksum fields because hardware will recompute them, syncs the inline header DMA range, calculates payload BD count, emits a long TX BD and extension BD, then walks payload mappings to emit one payload BD per chunk. The last payload BD for each segment gets `TX_BD_FLAGS_PACKET_END`.

Payload DMA unmapping is deliberately deferred to the last BD touching each mapped region. The code tracks `last_unmap_buf`, `last_unmap_addr`, and `last_unmap_len`, assigning the actual DMA unmap metadata only once it knows a later BD has superseded the same region. The last segment's first software BD is marked `BNXT_SW_GSO_LAST` and stores TSO completion state; earlier segment starts are marked `BNXT_SW_GSO_MID`.

At the end it advances `tx_inline_prod`, accounts the full original SKB length to the queue, publishes `tx_prod`, executes a write memory barrier, rings the TX doorbell, and may stop the netdev queue if descriptor space is low. On drop/error paths it frees the original SKB and increments TX dropped stats.

## State and persistence behavior

- Advances `txr->tx_prod` and `txr->tx_inline_prod` for normal TX ring and inline header ring consumption.
- Populates `txr->tx_buf_ring` entries with SKB ownership, fragment counts, software-GSO state, DMA unmap metadata, and completion state.
- Writes hardware TX descriptors into `txr->tx_desc_ring`.
- Uses queue accounting through `netdev_tx_sent_queue()` and queue stop helpers.
- No durable persistence exists; all state is in TX rings, DMA mappings, and SKB ownership until completions clean them.

## Dependencies and integration points

- Linux networking SKB, UDP/IP/IPv6, queue stop, and TSO segmentation helper APIs.
- PCI DMA APIs for header sync and payload mapping state.
- BNXT TX completion logic must understand `is_sw_gso`, `BNXT_SW_GSO_MID`, `BNXT_SW_GSO_LAST`, and saved TSO completion state.
- `bnxt_gso.h` supplies descriptor and inline-slot sizing assumptions used by ringparam validation and queue availability checks.

## Risks and edge cases

- Descriptor upper-bound math and cleanup assumptions must stay aligned with the main TX completion path; otherwise software USO can overwrite descriptors or leak mappings.
- Inline header ring availability is separate from TX BD availability. Missing this check would corrupt headers still referenced by in-flight DMA.
- The original SKB is referenced by every segment-start BD but must be freed exactly once, on the final software-GSO completion.
- DMA unmap metadata is assigned to the last BD touching a region; regressions in `tso_dma_map_next()` usage can double-unmap or leak payload mappings.
- IPv6 has no header checksum field to clear, while IPv4 does. The UDP checksum is always cleared before hardware offload.
- `num_segs` is bounded indirectly by `gso_max_segs` from `bnxt_gso.h`; if that cap changes, descriptor and inline buffer sizing must change with it.

## Test signals

- UDP GSO transmit on hardware without native USO for IPv4 and IPv6.
- Boundary cases at 2 segments, `BNXT_SW_USO_MAX_SEGS`, maximum SKB frags, VLAN-tagged SKBs, CFA action metadata, and short/large length hints.
- DMA mapping fault injection in `tso_dma_map_init()` and payload iteration.
- Queue stop/wake behavior when descriptor availability or inline slots are exhausted.
- TX completion tests that verify SKB free once, DMA unmap balance, and `tx_inline_cons` advancement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_gso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_gso.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_gso.h

## Purpose

`bnxt_gso.h` defines the public interface and sizing rules for BNXT software UDP segmentation offload fallback. It lets the rest of the driver cap advertised UDP GSO, reserve enough TX descriptors, and call the fallback transmit implementation when hardware lacks native UDP GSO.

## Important APIs and macros

- `BNXT_SW_USO_MAX_SEGS` caps software UDP GSO packets at 64 segments for NICs without hardware USO.
- `BNXT_SW_USO_MAX_DESCS` defines the worst-case descriptor budget for one software USO SKB: three descriptors per segment plus payload-fragment boundary overhead.
- `bnxt_inline_avail()` computes remaining inline header slots from `tx_inline_prod - tx_inline_cons`.
- `bnxt_min_tx_desc_cnt()` returns the larger software-USO descriptor minimum when UDP GSO is enabled without hardware capability, otherwise the normal `BNXT_MIN_TX_DESC_CNT`.
- `bnxt_sw_udp_gso_xmit()` is the exported fallback transmit routine.

## Control flow role

This header gates two caller decisions. Feature and ring sizing code uses `bnxt_min_tx_desc_cnt()` to reject rings too small for software USO. The main transmit path calls `bnxt_sw_udp_gso_xmit()` for eligible UDP GSO SKBs when hardware USO is unavailable.

## State and persistence behavior

No standalone state is stored here. The inline helper reads `struct bnxt_tx_ring_info` producer/consumer fields with `READ_ONCE()` on the consumer side because completions may update it asynchronously. The descriptor minimum depends on `bp->flags` and netdev feature bits.

## Dependencies and integration points

- Depends on BNXT TX ring structures and netdev feature flags.
- Tightly coupled to `bnxt_gso.c` descriptor emission and to TX completion handling of software-GSO state.
- Referenced by ethtool ringparam validation so users cannot shrink TX rings below the fallback's worst-case needs.

## Risks and edge cases

- The descriptor formula assumes each segment needs a long BD, extension BD, and payload BDs, with fragment-boundary overhead bounded by `num_segs + nr_frags`. Any descriptor format change must revisit this constant.
- `BNXT_SW_USO_MAX_SEGS` must match inline header ring allocation depth; otherwise availability checks and buffer indexing diverge.
- `bnxt_min_tx_desc_cnt()` only applies the larger minimum when `NETIF_F_GSO_UDP_L4` is enabled and hardware lacks the capability.

## Test signals

- Compile coverage with UDP GSO enabled/disabled and hardware USO capability present/absent.
- Ettool ring-size validation should reject TX rings smaller than `2 * BNXT_SW_USO_MAX_DESCS` when software USO is active, as enforced in `bnxt_ethtool.c`.
- Runtime software USO tests should confirm `bnxt_inline_avail()` backpressure prevents inline buffer overwrite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_gso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_hwmon.c

## Purpose

`bnxt_hwmon.c` exposes BNXT adapter temperature telemetry through the Linux hwmon subsystem when `CONFIG_BNXT_HWMON` is enabled. It queries firmware temperature sensors through HWRM, registers `temp1_*` attributes, reports warning/critical/emergency thresholds and alarms, optionally exposes shutdown threshold attributes, and notifies hwmon on asynchronous thermal threshold events.

## Important APIs and functions

- `bnxt_hwmon_init()` probes firmware temperature support and registers an hwmon device with `hwmon_device_register_with_info()`.
- `bnxt_hwmon_uninit()` unregisters the hwmon device.
- `bnxt_hwmon_notify_event()` maps firmware thermal event threshold type to hwmon alarm attributes and emits `hwmon_notify_event()`.
- `bnxt_hwrm_temp_query()` sends `HWRM_TEMP_MONITOR_QUERY`; with a non-NULL temp pointer it returns current temperature, and with NULL it caches firmware threshold capability and threshold values in `struct bnxt`.
- `bnxt_hwmon_is_visible()` controls which standard temp attributes are visible based on firmware threshold support.
- `bnxt_hwmon_read()` serves `temp1_input`, max/crit/emergency thresholds, and alarm booleans.
- `temp1_shutdown_show()` and `temp1_shutdown_alarm_show()` implement extra sysfs attributes for the firmware shutdown threshold.

## Control flow

Initialization calls `bnxt_hwrm_temp_query(bp, NULL)`. If firmware denies access or does not support the command, any existing hwmon device is unregistered and init returns. Otherwise, if no hwmon device is registered yet, the driver registers one named `DRV_MODULE_NAME`, using `bp` as drvdata and passing both standard channel info and optional extra shutdown attribute groups.

Read callbacks either query firmware for live temperature or return cached thresholds from `bp`. Alarm reads query live temperature and compare it against cached warning, critical, fatal, or shutdown thresholds. Visibility callbacks hide threshold and alarm files when firmware did not report threshold values, and hide shutdown attributes when the shutdown threshold is zero.

Async thermal events set `bp->thermal_threshold_type` elsewhere, then call `bnxt_hwmon_notify_event()`, which selects the matching hwmon alarm type and notifies userspace.

## State and persistence behavior

- `bp->hwmon_dev` stores the registered hwmon device pointer.
- `bp->fw_cap` gains `BNXT_FW_CAP_THRESHOLD_TEMP_SUPPORTED` when firmware reports threshold values.
- Threshold caches include `warn_thresh_temp`, `crit_thresh_temp`, `fatal_thresh_temp`, and `shutdown_thresh_temp`.
- `bp->thermal_threshold_type` drives event notification mapping.
- No durable persistence is performed; all threshold values are queried/cached firmware data.

## Dependencies and integration points

- Linux hwmon and hwmon-sysfs APIs.
- HWRM request framework and `HWRM_TEMP_MONITOR_QUERY` firmware command.
- BNXT async event handling, which invokes `bnxt_hwmon_notify_event()` after thermal events.
- Conditional compilation wrapper in `bnxt_hwmon.h`.

## Risks and edge cases

- If firmware supports current temperature but not thresholds, only `temp1_input` should be visible.
- `bnxt_hwrm_temp_query(bp, NULL)` mutates `bp->fw_cap` and threshold caches; repeated init/probe calls should preserve consistent visibility.
- Alarm reads return `-EIO` for shutdown alarm query failure but return raw HWRM errors for standard alarm reads.
- The hwmon event notification uses `&bp->pdev->dev` rather than `bp->hwmon_dev`; this must match hwmon expectations for the registered parent device.

## Test signals

- Build with `CONFIG_BNXT_HWMON=y` and disabled.
- Simulate HWRM success with thresholds, success without thresholds, `-EACCES`, `-EOPNOTSUPP`, and transient read failures.
- Verify sysfs visibility for standard and shutdown attributes under each threshold configuration.
- Verify alarm values at temperatures just below/equal/above thresholds.
- Verify async thermal events produce max, crit, and emergency hwmon notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_hwmon.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_hwmon.h

## Purpose

`bnxt_hwmon.h` provides the conditional public interface for BNXT hwmon support. It declares real initialization, teardown, and notification functions when `CONFIG_BNXT_HWMON` is enabled, and no-op inline stubs otherwise so the rest of the driver can call hwmon hooks unconditionally.

## Important APIs

- `bnxt_hwmon_notify_event(struct bnxt *bp)` reports firmware thermal events to hwmon.
- `bnxt_hwmon_uninit(struct bnxt *bp)` unregisters any hwmon device.
- `bnxt_hwmon_init(struct bnxt *bp)` probes and registers hwmon temperature attributes.
- Disabled-config stubs are empty inline functions.

## Control flow role

BNXT core and async event code can call these hooks without local `#ifdef`s. The compile-time config selects either the implementation in `bnxt_hwmon.c` or no-op behavior.

## State and persistence behavior

The header stores no state. The real implementation mutates `bp->hwmon_dev` and temperature threshold caches; the stubs deliberately leave all state unchanged.

## Dependencies and integration points

- Depends on `struct bnxt` being visible to users.
- Integrates with driver probe/remove and firmware async event paths.
- Shields the rest of the driver from direct dependency on Linux hwmon APIs when the feature is disabled.

## Risks and edge cases

- Callers must not assume hwmon registration happened; with the config disabled every hook is a no-op.
- Any new hwmon hook should be added to both the enabled declarations and disabled stubs to keep call sites config-independent.

## Test signals

- Compile with `CONFIG_BNXT_HWMON=y` and `CONFIG_BNXT_HWMON=n`.
- Probe/remove and thermal async event paths should build and run with no conditional call-site changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_hwmon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_hwrm.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_hwrm.c

## Purpose

`bnxt_hwrm.c` is the BNXT Host Wire Resource Manager request framework. It allocates DMA-backed request/response contexts, validates request ownership with sentinels, supports indirect DMA slices, sends requests through CHIMP or KONG firmware mailboxes, waits for completion by polling or completion-ring token updates, maps firmware error codes to Linux errno values, and releases all resources consistently.

## Important APIs and functions

- Request lifecycle:
  - `__hwrm_req_init()` allocates a DMA-pool buffer, lays out request, response, and context regions, initializes common request fields, and returns a typed request pointer.
  - `hwrm_req_hold()` marks the context caller-owned and returns the response pointer so callers can inspect response data or reuse a request.
  - `hwrm_req_drop()` releases owned or unsent requests and any associated slice.
  - `__hwrm_ctx_drop()` frees external slices, invalidates the context, and returns the backing buffer to the DMA pool.
- Request customization:
  - `hwrm_req_timeout()` sets per-request timeout.
  - `hwrm_req_alloc_flags()` changes GFP flags for future DMA slice allocation.
  - `hwrm_req_flags()` applies public behavior flags such as silent logging or full wait.
  - `hwrm_req_replace()` copies or references prebuilt request data while preserving managed response DMA resources.
  - `hwrm_req_dma_slice()` suballocates indirect DMA memory from unused request-buffer space or allocates one external coherent slice.
- Send/completion:
  - `hwrm_req_send()` validates the context and calls `__hwrm_send()`.
  - `hwrm_req_send_silent()` sets silent logging then sends.
  - `__hwrm_send()` chooses CHIMP/KONG channel, assigns a sequence token, optionally wraps large/short-command requests in `hwrm_short_input`, writes the mailbox, rings the doorbell, waits for response, validates response sequence and valid bit, maps firmware error codes, and consumes or preserves the context based on ownership.
  - `hwrm_update_token()` is called from completion handling to mark a pending CHIMP token as deferred/complete/cancelled.
- Support helpers:
  - `hwrm_calc_sentinel()` and `__hwrm_ctx()` detect invalid request pointers or use-after-free.
  - `__hwrm_to_stderr()` maps HWRM error codes to Linux errno.
  - `bnxt_kong_hwrm_message()` is declared inline in the header and used to route CFA/KONG-targeted messages.

## Control flow

Callers allocate a request with `hwrm_req_init()` or `__hwrm_req_init()`, fill request-specific fields, optionally allocate DMA slices or hold the request, and call `hwrm_req_send()` or `hwrm_req_send_silent()`. Unheld requests are consumed automatically on send completion or error. Held requests remain valid after send and must be dropped by the caller.

`__hwrm_send()` first clears a previously dirty response for held/reused requests, validates firmware access, rejects oversized requests, and routes KONG mailbox traffic when needed. It acquires a wait token under `bp->hwrm_cmd_lock`; CHIMP tokens are inserted into an RCU pending list so completion interrupts can update them, while KONG tokens are local because KONG ring completions are not supported.

For short command mode or messages larger than the maximum inline mailbox request length, the function builds a `struct hwrm_short_input` pointing at the full DMA request buffer. It writes the request words into BAR0 mailbox space, zeroes remaining mailbox words, rings the firmware doorbell, and then waits.

If the request uses a completion ring, it waits for `hwrm_update_token()` to mark the token complete. Otherwise, it polls `ctx->resp->resp_len`, checks the response sequence id, tolerates and logs out-of-sequence responses, then waits for the final response valid byte. In both paths it aborts on fatal firmware state or unhealthy firmware status when health registers are reliable.

After a valid response, it clears the valid byte for forward compatibility, reads `error_code`, logs non-success errors unless silent, maps the error, releases the token, and either marks a held response dirty for future reuse or drops the context.

## State and persistence behavior

- Per-request state lives in `struct bnxt_hwrm_ctx`: DMA handle, request/response pointers, optional external slice, request length, flags, timeout, allocation watermark, GFP flags, and sentinel.
- Global sequencing state lives in `bp->hwrm_cmd_seq`, `bp->hwrm_cmd_kong_seq`, `bp->hwrm_cmd_lock`, and `bp->hwrm_pending_list`.
- Firmware health state is observed through `bp->fw_health`, `BNXT_STATE_FW_FATAL_COND`, and health register reads.
- No durable persistence exists. The framework sends commands that may cause persistent side effects in caller-specific HWRM operations, such as NVM writes.

## Dependencies and integration points

- DMA pool allocation (`bp->hwrm_dma_pool`) and coherent DMA for indirect slices.
- PCI BAR0 mailbox/register access with `__iowrite32_copy()`, `writel()`, and firmware-specific CHIMP/KONG offsets.
- RCU pending-list integration with completion handlers in the RX/TX/completion path.
- Firmware health monitoring helpers and BNXT state bits.
- HWRM request/response wire structures from `<linux/bnxt/hsi.h>`.
- Callers across nearly every BNXT module, including ethtool, PTP, hwmon, link, VNIC, filters, rings, and NVM.

## Risks and edge cases

- The request pointer is a managed pointer into a larger DMA buffer; passing copied, stale, or external pointers trips sentinel checks and indicates driver bugs.
- Held requests require strict `hwrm_req_drop()` discipline. Missing drops leak DMA pool buffers or external coherent slices.
- Only one external DMA slice is supported per request; repeated large slice requests log stack traces and fail.
- The suballocation math in `hwrm_req_dma_slice()` must avoid overlap with request payload and prior allocations.
- Short-command mode and request replacement must preserve `resp_addr` and sentinel correctness even when the request body is externally supplied.
- Sequence handling is critical. Out-of-sequence responses are logged and ignored; persistent sequence confusion leads to timeouts.
- Completion-ring waits require `hwrm_update_token()` from interrupt context. Missed completions or wrong sequence id cause timeouts.
- The valid-byte clearing assumes response length is valid and nonzero; malformed firmware responses can still lead to timeout/error paths.
- KONG commands reject completion-ring usage; callers must use polling semantics.

## Test signals

- Request lifecycle tests for unheld send, held send/drop, reuse after dirty response, aborted unsent drop, replacement request, and slice allocation/free.
- Fault injection for DMA pool allocation failure, coherent slice allocation failure, oversized request, invalid request pointer, duplicate hold, duplicate drop, and repeated external slice allocation.
- Firmware simulation for success, busy, invalid params, access denied, no buffer, unsupported command, PF unavailable, out-of-sequence responses, missing valid bit, timeout, deferred token, and fatal firmware health.
- Runtime tracing should confirm all HWRM callers drop held requests and that `bp->hwrm_pending_list` is empty after command completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_hwrm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_hwrm.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_hwrm.h

## Purpose

`bnxt_hwrm.h` defines the public BNXT HWRM request-management API and the private context/token structures used by `bnxt_hwrm.c`. It centralizes request buffer layout constants, timeout constants, request flags, wait-token states, CHIMP/KONG channel routing helpers, and typed initialization/send/drop/dma-slice prototypes.

## Important APIs, types, and macros

- `enum bnxt_hwrm_ctx_flags` controls request ownership internals and caller-visible behavior: silent errors and full timeout.
- `struct bnxt_hwrm_ctx` records managed request/response DMA state, optional indirect DMA slice, request length, flags, timeout, allocation watermark, and GFP flags.
- `enum bnxt_hwrm_wait_state` and `struct bnxt_hwrm_wait_token` model pending/deferred/complete/cancelled mailbox completions.
- `enum bnxt_hwrm_chnl` distinguishes CHIMP and KONG mailbox channels.
- Layout constants define one DMA buffer containing request, context, and response regions: `BNXT_HWRM_DMA_SIZE`, `BNXT_HWRM_RESP_OFFSET`, `BNXT_HWRM_CTX_OFFSET`, alignment, reserved response size, and request size limits.
- Timeout constants define short initial sleeps, normal sleep ranges, maximum command timeouts, reset timeout, and valid-bit wait.
- `bnxt_cfa_hwrm_message()` and `bnxt_kong_hwrm_message()` route CFA and explicit KONG-targeted commands to the KONG mailbox when firmware supports it.
- Public API prototypes include request init, hold, drop, flags, timeout, send, silent send, replacement, allocation flags, DMA slices, and token updates.
- `bnxt_hwrm_func_cfg_short_req_init()` initializes a shortened HWRM_FUNC_CFG request for older devices with smaller max request lengths.

## Control flow role

Callers use the `hwrm_req_init(bp, req, TYPE)` macro to allocate a typed request based on `sizeof(*req)`. They fill fields, optionally call customization helpers, and call send/drop helpers. Header inline routing functions are evaluated by `__hwrm_send()` to select the firmware mailbox channel. The short FUNC_CFG helper lets callers avoid `-E2BIG` by intentionally truncating fields not needed by older firmware.

## State and persistence behavior

The header defines state structures but does not instantiate them. Instances are embedded in managed DMA buffers or allocated as wait tokens at runtime. No persistent storage is managed here, but HWRM commands declared through this API can produce persistent firmware/device side effects.

## Dependencies and integration points

- Includes `<linux/bnxt/hsi.h>` for HWRM request IDs, target IDs, and wire structures.
- Requires `struct bnxt`, DMA APIs, RCU list handling, and firmware capability bits defined in BNXT core headers.
- Used across the BNXT driver as the standard firmware command API.

## Risks and edge cases

- Any layout constant change must preserve the non-overlapping request/context/response memory map expected by `bnxt_hwrm.c`.
- Adding public flags requires updating `HWRM_API_FLAGS`; internal flags must not be settable by callers.
- KONG routing depends on a maintained list of CFA request types. New CFA commands can accidentally go to CHIMP unless added.
- `BNXT_HWRM_MAX_REQ_LEN` is macro-expanded from `bp`; it is only valid in scopes where `bp` exists.
- Short FUNC_CFG requests intentionally use `min(sizeof, bp->hwrm_max_ext_req_len)` and must only be used when omitted trailing fields are not needed.

## Test signals

- Compile all HWRM users after adding new request types or flags.
- Exercise KONG-routed CFA commands and CHIMP-routed ordinary commands.
- Verify old-firmware short FUNC_CFG paths avoid oversized request failures.
- Static analysis for misuse of request ownership flags and invalid macro contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_hwrm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_nvm_defs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_nvm_defs.h

## Purpose

`bnxt_nvm_defs.h` defines BNXT NVM directory type IDs, directory ordinal/extension/attribute constants, and package-log field indexes used by ethtool NVM and firmware package flows. It is a compact contract between driver code and Broadcom firmware's NVM directory layout.

## Important APIs, types, and macros

- `enum bnxt_nvm_directory_type` names NVM item directory types, including package log, UPDATE area, firmware/patch images for CHIMP/APE/KONG/BONO/TANG, bootcode, VPD, PCIe, external PHY, shared/port/function/management configuration, and management logs.
- `BNX_DIR_ORDINAL_FIRST` is the default ordinal used by lookup and flash helpers.
- `BNX_DIR_EXT_NONE`, `BNX_DIR_EXT_INACTIVE`, and `BNX_DIR_EXT_UPDATE` encode directory extension flags.
- `BNX_DIR_ATTR_NONE`, `BNX_DIR_ATTR_NO_CHKSUM`, and `BNX_DIR_ATTR_PROP_STREAM` encode NVM item attributes.
- `enum bnxnvm_pkglog_field_index` identifies tab-separated package log fields, with package version used by `bnxt_get_pkginfo()`.

## Control flow role

The header is passive. `bnxt_ethtool.c` uses the directory type enum to route flash requests to package, firmware, microcode, or raw NVM write paths; to find UPDATE and PKG_LOG entries; and to decide which firmware reset processor is affected. Package-log field indexes drive in-place parsing of the NVM package log.

## State and persistence behavior

No memory state is stored. These constants identify persistent NVM entries and attributes. Operations using them may create, resize, erase, read, or overwrite NVM contents.

## Dependencies and integration points

- Integrated by `bnxt_ethtool.c` NVM get/set/flash/package helpers.
- Must match firmware-defined NVM directory IDs and package log format.
- Used with HWRM NVM commands such as FIND_DIR_ENTRY, READ, WRITE, MODIFY, INSTALL_UPDATE, DEFRAG, and ERASE_DIR_ENTRY.

## Risks and edge cases

- Directory type numeric values are firmware ABI. Renumbering breaks NVM access and flashing.
- Missing newer directory types can force otherwise valid firmware regions down unsupported/default paths.
- Package-log field indexes assume the firmware log remains tab-separated and stable.
- Executable versus non-executable classification is implemented in `bnxt_ethtool.c`; new enum values need corresponding classification updates.

## Test signals

- NVM directory lookup tests for PKG_LOG and UPDATE entries.
- Flash dispatch tests for every executable directory type.
- Package version parsing tests with complete, missing, malformed, and nonnumeric package version fields.
- Firmware ABI review whenever HWRM/NVM directory definitions are updated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_nvm_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_ptp.c

## Purpose

`bnxt_ptp.c` implements Precision Time Protocol and hardware timestamp support for BNXT devices. It registers a PHC with the Linux PTP subsystem, maps and reads device reference-clock registers, maintains a timecounter/cyclecounter, configures hardware timestamp filters, handles TX/RX timestamp conversion, supports PTP PPS/TSIO pins, queries firmware timestamps, provides optional cross-timestamping on x86 PTM-capable systems, and cleans up PTP resources on device teardown/reset.

## Important APIs and functions

- Clock operations:
  - `bnxt_ptp_settime()`, `bnxt_ptp_gettimex()`, `bnxt_ptp_adjtime()`, and `bnxt_ptp_adjfine()` implement `ptp_clock_info` time set/read/phase/frequency adjustment callbacks.
  - `bnxt_ptp_cfg_settime()`, `bnxt_ptp_adjphc()`, and `bnxt_ptp_adjfine_rtc()` program firmware/hardware RTC modes through HWRM.
  - `bnxt_ptp_timecounter_init()` and `bnxt_ptp_rtc_timecounter_init()` initialize local conversion state.
- Clock reads and conversion:
  - `__bnxt_refclk_read()`, `bnxt_refclk_read()`, and `bnxt_refclk_read_low()` read 48-bit or low 32-bit mapped reference-clock registers with system timestamp bracketing and reset serialization.
  - `bnxt_cc_read()` feeds the kernel cyclecounter.
  - `bnxt_extend_cycles_32b_to_48b()` in the header extends RX 32-bit packet timestamps using cached high bits.
  - `bnxt_ptp_update_current_time()` and `bnxt_ptp_get_current_time()` refresh `current_time` and `old_time`.
- Packet timestamp configuration:
  - `bnxt_hwtstamp_set()` validates userspace `kernel_hwtstamp_config`, maps RX filters to BNXT PTP message masks/all-packet timestamp flags, updates TX enable state, and applies hardware config.
  - `bnxt_hwtstamp_get()` returns cached hardware timestamp config.
  - `bnxt_hwrm_ptp_cfg()` and `bnxt_ptp_cfg_tstamp_filters()` program MAC timestamp capture flags.
- TX/RX timestamp data path:
  - `bnxt_ptp_parse()` classifies PTP packets and extracts sequence id/header offset for firmware timestamp queries.
  - `bnxt_ptp_get_txts_prod()` reserves one of four TX timestamp slots.
  - `bnxt_get_tx_ts_p5()` stores a TX SKB in a slot and schedules the PTP aux worker.
  - `bnxt_ptp_ts_aux_work()` polls pending TX timestamp requests, periodically refreshes timecounter state, and prevents 48-bit overflow drift.
  - `bnxt_stamp_tx_skb()` queries firmware for a TX timestamp and calls `skb_tstamp_tx()`.
  - `bnxt_tx_ts_cmp()` handles timestamp completions that carry the timestamp directly in completion rings.
  - `bnxt_get_rx_ts_p5()` converts 32-bit packet RX timestamps to extended cycles for receive code.
- PPS and pins:
  - `bnxt_ptp_pps_event()` converts async PPS event data to PTP clock events.
  - `bnxt_ptp_cfg_pin()`, `bnxt_ptp_cfg_event()`, `bnxt_ptp_perout_cfg()`, `bnxt_ptp_enable()`, `bnxt_ptp_verify()`, `bnxt_ptp_pps_init()`, and `bnxt_ptp_reapply_pps()` implement external timestamp, periodic output, and PPS pin configuration.
- Lifecycle:
  - `bnxt_map_ptp_regs()` and `bnxt_unmap_ptp_regs()` map reference-clock registers through a GRC window on P5 or direct offsets on P7.
  - `bnxt_ptp_init_rtc()`, `bnxt_ptp_init()`, `bnxt_ptp_free()`, and `bnxt_ptp_clear()` initialize/register/unregister/clear PTP resources.
  - `bnxt_ptp_free_txts_skbs()` cancels worker activity and frees queued TX timestamp SKBs.
- Optional x86 cross timestamp:
  - `bnxt_phc_get_syncdevicetime()` and `bnxt_ptp_getcrosststamp()` integrate firmware PTM query results with `get_device_system_crosststamp()` when PTM and ART are available.

## Control flow

Initialization maps PTP registers, tears down/rebuilds the PHC when PPS capability changed, initializes locks and TX timestamp slot accounting, initializes the timecounter in RTC or non-RTC mode, registers driver events with firmware, optionally queries PPS pin configuration, installs cross-timestamp support on capable x86 systems, registers the PTP clock, resets timestamp stats, and starts the aux worker for P5-plus chips.

Userspace timestamp configuration enters through `bnxt_hwtstamp_set()`. The function validates TX type and RX filter, saves the old cached state, updates `ptp->rxctl`, `rx_filter`, and `tx_tstamp_en`, then calls `bnxt_hwrm_ptp_cfg()` to program MAC timestamp capture. On firmware failure it restores the old cached config.

TX timestamping has two variants. For P5 query-based timestamps, the TX path reserves a slot with `bnxt_ptp_get_txts_prod()`, stores sequence/header metadata and SKB elsewhere, then `bnxt_get_tx_ts_p5()` publishes timeout and SKB and schedules the aux worker. The worker calls `bnxt_stamp_tx_skb()`, which queries firmware using the stored sequence/header offset, converts device cycles to ns, timestamps the SKB, updates stats, and frees the SKB. For completion-based timestamps, `bnxt_tx_ts_cmp()` receives a completion, finds the original TX buffer from the opaque field, converts the 48-bit timestamp, and timestamps the SKB if no hardware timestamp error is set.

Clock reads use seqlocks to serialize register access with firmware reset and timecounter mutation. `bnxt_ptp_gettimex()` reads the low 32-bit reference clock, extends it using cached high bits, converts it through the timecounter, and returns a timespec. Periodic aux work refreshes current time every second and forces a `timecounter_read()` every 18 minutes to avoid overflow with the 23-bit shifted cyclecounter.

PPS requests from the PTP subsystem use `bnxt_ptp_enable()`, which finds a compatible pin, configures its firmware usage/state, and configures the firmware PPS event or periodic output phase. Async firmware PPS events are converted to `PTP_CLOCK_PPSUSR` or `PTP_CLOCK_EXTTS` events.

## State and persistence behavior

- `struct bnxt_ptp_cfg` stores PHC registration, cyclecounter/timecounter, seqlock, TX timestamp spinlock, current time/high-bit cache, periodic worker deadlines, clock multiplier, TX timestamp slots, timestamp filters, RX filter/mask, TX enable bit, PTP register offsets, timeout, PPS pin state, and stats.
- Hardware/firmware state includes PTP set time, phase/frequency adjustment, MAC timestamp capture filters, PPS pin configuration, PPS event mode, periodic output phase, and mapped GRC window.
- SKB ownership for query-based TX timestamps is transferred into `ptp->txts_req[]` until the aux worker timestamps or drops it.
- `ptp->stats` persists packet/lost/error counts until PTP reinit.
- No filesystem persistence exists.

## Dependencies and integration points

- Linux PTP clock subsystem, `ptp_clock_info`, aux workers, pin configuration, PPS/extts/perout events, and cross timestamp APIs.
- Linux timestamping and SKB APIs: `kernel_hwtstamp_config`, `skb_tstamp_tx()`, `skb_shared_hwtstamps`.
- Timekeeping helpers: seqlock, cyclecounter, timecounter, system timestamp bracketing, ART cross timestamp on x86.
- BNXT HWRM commands for FUNC_PTP_CFG, FUNC_PTP_PIN_CFG/QCFG, PORT_MAC_CFG, PORT_TS_QUERY, and FUNC_PTP_TS_QUERY.
- BNXT TX/RX paths call parse/reserve/store/completion/RX conversion helpers.
- Firmware reset paths must coordinate with PTP register reads and reapply PPS/timestamp settings.

## Risks and edge cases

- Register reads during firmware reset return `-EIO`; missing serialization can read invalid BAR/GRC windows.
- 32-bit RX timestamp extension depends on `old_time` being refreshed often enough and on monotonic low-bit behavior.
- Query-based TX timestamp slots are limited to four. Exhaustion increments `ts_err`; lost queries increment `ts_lost` and free SKBs.
- Memory barriers around `abs_txts_tmo` and `tx_skb` publication are required so the aux worker sees a consistent slot.
- `bnxt_ptp_pps_event()` assumes event type is one of the handled values before calling `ptp_clock_event()` with initialized fields.
- PPS pin arrays are capped by `BNXT_MAX_TSIO_PINS`; firmware reporting more pins would need bounds review.
- `bnxt_pps_config_ok()` uses a compact boolean expression that is easy to misread; it tests whether firmware PPS capability and pin_config presence agree.
- RTC versus non-RTC modes choose different adjustment mechanisms; wrong `BNXT_PTP_USE_RTC()` behavior can double-apply or miss adjustments.
- `bnxt_unmap_ptp_regs()` clears the P5 GRC window even on P7 paths; the fixed register write should remain harmless but is platform-specific.

## Test signals

- PHC registration/read/set/adjtime/adjfine tests in RTC and non-RTC modes.
- Hardware timestamp config tests for TX on/off, RX none/all/PTP event/sync/delay request, unsupported all-RX firmware, and rollback on HWRM failure.
- TX timestamp tests for query success, query timeout before and after absolute timeout, slot exhaustion, SKB freeing, completion-based success/error, and stats.
- RX timestamp conversion tests around low-32-bit wrap and periodic `old_time` refresh.
- PPS tests for pin query, extts, perout, PPS, disable paths, invalid pin/function, firmware failures, and reapply after reset.
- Cross timestamp tests on x86 PTM+ART systems and build tests on non-x86.
- Reset/unmap tests to ensure PTP register access fails cleanly during firmware reset and resources are unregistered once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_ptp.h

## Purpose

`bnxt_ptp.h` defines BNXT PTP constants, timestamp/PPS data structures, helper macros, exported PTP functions, and inline timestamp conversion helpers shared by the BNXT TX/RX, ethtool, async event, and lifecycle code.

## Important APIs, types, and macros

- Register and clock constants: `BNXT_PTP_GRC_WIN`, `BNXT_PTP_GRC_WIN_BASE`, `BNXT_MAX_PHC_DRIFT`, `BNXT_CYCLES_SHIFT`, `BNXT_DEVCLK_FREQ`, low/high timer masks, default TX timestamp timeout, query timeout, and query enable flags.
- PPS event extraction macros: `EVENT_DATA2_PPS_EVENT_TYPE()`, `EVENT_DATA2_PPS_PIN_NUM()`, and `EVENT_PPS_TS()`.
- PPS pin usage constants define disabled, PPS input/output, sync input/output, and internal/external event modes.
- `struct pps_pin` and `struct bnxt_pps` store per-pin event, usage, and state for up to four TSIO pins.
- `struct bnxt_ptp_stats` stores timestamped packet, lost timestamp, and error counters.
- `struct bnxt_ptp_tx_req` stores one pending TX timestamp SKB plus PTP sequence id, header offset, and absolute timeout.
- `struct bnxt_ptp_cfg` is the central PTP state object: PTP clock info/handle, cyclecounter/timecounter, PPS info, locks, current time/high-bit cache, worker deadlines, multiplier, TX request slots, timestamp filters, register mapping, timeout, producer/consumer indices, and stats.
- `BNXT_PTP_INC_TX_AVAIL()` safely returns a TX timestamp slot under `ptp_tx_lock`.
- Exported functions cover PTP packet parse, current-time update, PPS events, timestamp filter reconfiguration, PPS reapply, hwtstamp get/set, TX timestamp SKB cleanup/reservation/storage/completion, RX timestamp extension, RTC init, PTP init, and PTP clear.
- `bnxt_timecounter_cyc2time()` reads the timecounter under seqlock retry.
- `bnxt_extend_cycles_32b_to_48b()` extends packet timestamps using cached high timer bits and low-bit wrap detection.

## Control flow role

The header lets the data path reserve TX timestamp slots and convert RX timestamps without depending on all of `bnxt_ptp.c` internals. Ettool timestamp reporting uses the presence and fields of `bp->ptp_cfg`. Async event handling calls PPS event and reapply hooks. Device init/teardown calls PTP init/clear and RTC helpers.

## State and persistence behavior

The main state defined here is runtime-only `struct bnxt_ptp_cfg`. It persists while the BNXT device instance is alive and is reset during PTP init/clear. Hardware timestamp/PPS state is applied by functions declared here but stored in firmware/hardware, not in this header.

## Dependencies and integration points

- Linux PTP and timecounter headers.
- BNXT firmware constants for timestamp query flags and async PPS event fields.
- BNXT TX path uses `BNXT_MAX_TX_TS`, `NEXT_TXTS()`, slot reservation, and completion helpers.
- BNXT RX path uses cycle-extension and conversion helpers.
- Ettool uses PTP stats and hwtstamp configuration functions.

## Risks and edge cases

- `BNXT_MAX_TX_TS` is four and `NEXT_TXTS()` assumes it is a power of two.
- `BNXT_PTP_INC_TX_AVAIL()` uses a macro with locking side effects; callers must avoid invoking it with expressions that have side effects.
- `bnxt_extend_cycles_32b_to_48b()` depends on timely `old_time` refresh and assumes at most one low-timer wrap relative to the cached high bits.
- `struct bnxt_ptp_cfg` embeds `struct ptp_clock_info`; reinitialization must preserve or rebuild pin_config carefully to avoid leaks.
- Comments mention `cyclecoutner`; typo is harmless but near timing-sensitive documentation.

## Test signals

- Compile data path users with PTP enabled and disabled through higher-level config combinations.
- TX timestamp ring wrap and slot availability tests across `BNXT_MAX_TX_TS`.
- RX timestamp wrap conversion tests for low timestamp below and above cached low bits.
- PTP clear/reinit leak checks for embedded `ptp_info.pin_config` and registered clock handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_ptp.h -->
