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
