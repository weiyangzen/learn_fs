# Research: subset-b-004376

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt.h

Purpose: This is the central private header for the Broadcom NetXtreme-C/E `bnxt_en` Ethernet driver. It defines hardware descriptor formats, completion formats, ring sizing and index macros, doorbell helpers, software ring state, firmware capability and health state, link state, SR-IOV/PF/VF state, RSS/VNIC/filter structures, backing-store context memory, stats layouts, and the cross-file function prototypes used by the rest of the driver.

Important APIs, types, and functions: The header declares TX/RX descriptors (`tx_bd`, `tx_bd_ext`, `rx_bd`), completion records (`tx_cmp`, `rx_cmp`, `rx_cmp_ext`, TPA start/end completions, NQ completions), software ring containers (`bnxt_tx_ring_info`, `bnxt_rx_ring_info`, `bnxt_cp_ring_info`, `bnxt_napi`), resource/state containers (`bnxt_hw_resc`, `bnxt_pf_info`, `bnxt_vf_info`, `bnxt_ctx_mem_info`, `bnxt_fw_health`, `bnxt_link_info`), flow/filter structures (`bnxt_l2_filter`, `bnxt_ntuple_filter`, `bnxt_tc_info`), and the main `struct bnxt`. Inline helpers include `bnxt_tx_avail()`, `bnxt_init_ext_bd()`, 64-bit doorbell writers, `bnxt_db_write_relaxed()`, `bnxt_db_write()`, `bnxt_sriov_cfg()`, and `bnxt_rss_ext_op()`. Exported prototypes connect to RX allocation, HWRM resource setup, VNIC/RSS/filter programming, link configuration, coredump/debug register reads, NIC open/close, firmware reset/recovery, DIM coalescing, and stats.

Control flow: This header does not implement the full driver lifecycle, but it encodes the control-flow contract used by source files in this directory. Fast-path TX/RX code fills descriptors, advances masked producer/consumer indices, validates completion toggle bits against `bp->cp_bit`, and rings chip-generation-specific doorbells through `bnxt_db_write*()`. Device lifecycle code allocates and initializes `struct bnxt`, populates capability flags from HWRM responses, reserves rings/resources, opens NAPI/rings/VNICs, and uses `state`/`sp_event` bits plus delayed work for link changes, firmware resets, and health recovery. Auxiliary code such as DCB, devlink, debugfs, coredump, PTP, SR-IOV, RDMA ULP, and TC offload all share the `bp` fields defined here.

State and persistence behavior: Runtime state is almost entirely in memory under `struct bnxt`: PCI BAR mappings, netdev/pci pointers, ring arrays, NAPI contexts, RSS and VNIC tables, queue/TC mappings, firmware caps, HWRM command state, link settings, port/ring stats DMA buffers, work items/timers, firmware health counters, SR-IOV resources, filter hash tables, ethtool link settings, devlink/debugfs pointers, crash dump backing memory, backing-store trace wrap state, and auxiliary-device state. Persistent device configuration is not stored by this header directly; HWRM/NVM consumers store persistent settings in firmware/NVM while this header provides fields and constants to cache them.

Dependencies and integration points: It depends on Linux networking, PCI, ethtool, XDP, page pool, DIM, devlink, crash dump, rhashtable, and Broadcom HSI/ULP interfaces. It is included by nearly every `bnxt` implementation file and is the glue between the Linux netdev lifecycle, HWRM firmware command layer, devlink health/reload/params, DCB netlink, debugfs DIM introspection, ethtool stats/coredump, SR-IOV representors, RDMA auxiliary devices, and hardware rings.

Risks: The header is a high-risk ABI-like contract with the NIC firmware and hardware. Descriptor bitfields, endian conversions, ring masks, completion valid-bit handling, and doorbell ordering must match silicon generation rules. `struct bnxt` is broad shared mutable state, so lifecycle bits, firmware reset bits, and locks (`hwrm_cmd_lock`, `link_lock`, filter locks, auxdev lock, doorbell lock on 32-bit) must be used consistently by implementation files. Capability macros often gate chip-generation behavior; wrong flags can program unsupported firmware commands, mis-size rings, or expose invalid devlink/DCB features.

Test signals: Build coverage across `CONFIG_BNXT_SRIOV`, `CONFIG_BNXT_DCB`, `CONFIG_BNXT_FLOWER_OFFLOAD`, `CONFIG_DEBUG_FS`, `CONFIG_BNXT_HWMON`, and 32-bit doorbell paths is important. Runtime signals include TX/RX traffic with TSO/GRO/LRO/XDP, RSS context changes, link mode/FEC changes, SR-IOV enable/disable, DCB ETS/PFC changes, firmware reset/recovery, devlink health dump/reload, ethtool stats and coredump reads, and DMA/debug instrumentation for ring wrap and completion validity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_coredump.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_coredump.c

Purpose: Implements firmware, crash, and driver-context coredump collection for `bnxt_en`. It packages HWRM firmware coredump segments, the HWRM version response, driver backing-store context memory, and final coredump metadata into the binary format declared by `bnxt_coredump.h`.

Important APIs, types, and functions: Public entry points are `bnxt_get_coredump()`, `bnxt_hwrm_get_dump_len()`, `bnxt_get_coredump_length()`, and `bnxt_fill_coredump_seg_hdr()`. Internal helpers include `bnxt_hwrm_dbg_dma_data()` for sequenced DMA-based debug HWRM transfers, `bnxt_hwrm_dbg_coredump_list()`, `bnxt_hwrm_dbg_coredump_initiate()`, `bnxt_hwrm_dbg_coredump_retrieve()`, `bnxt_get_ctx_coredump()` for driver backing-store capture, `bnxt_copy_crash_dump()` for pre-collected crash memory, and metadata fillers for command line and final records.

Control flow: Live coredump collection starts by emitting a synthetic HWRM_VER_GET segment, then either appends driver context segments for `BNXT_DUMP_DRIVER` or asks firmware for a segment list, initiates each segment, retrieves segment data into the caller buffer, and writes one segment header per firmware segment. The same path supports a length-only pass with `buf == NULL`, allowing ethtool/devlink callers to size allocations before collection. Crash dump collection is separate: if firmware advertises host DDR crashdump support, the driver copies from `bp->fw_crash_mem`; if TEE SOC DDR support is compiled and advertised, it delegates to `tee_bnxt_copy_coredump()`.

State and persistence behavior: The file reads transient firmware state through HWRM debug commands and local driver state from `bp->ver_resp`, `bp->chip_num`, `bp->ctx`, `bp->bs_trace`, `bp->fw_dbg_cap`, `bp->fw_crash_mem`, and `bp->fw_crash_len`. Captured crash memory may have been persisted by firmware in host/SOC DDR before the read, but this code itself only copies it to the caller's buffer. It tracks backing-store trace wrap by flushing log buffers and updating `bnxt_bs_trace_info`.

Dependencies and integration points: It depends on `bnxt_hwrm.h` request helpers, HSI debug command structs, `bnxt_copy_ctx_mem()`, `bnxt_bs_trace_avail()`, `bnxt_bstore_to_trace[]`, optional TEE firmware support, kernel time/utsname/current task state, and netdev logging. Devlink health dump code and ethtool dump code consume `bnxt_get_coredump_length()` and `bnxt_get_coredump()`.

Risks: Buffer accounting is critical because firmware-reported segment sizes are copied through fixed 4 KiB DMA slices and must leave room for the trailing `bnxt_coredump_record`. Error handling can still write segment headers with per-segment status, but `-ENOBUFS` aborts. Length-only and data-copy passes must stay consistent or callers can allocate the wrong size. Crash dump availability assumes the first four bytes are nonzero and depends on `fw_crash_mem` page-table depth being correct.

Test signals: Exercise `BNXT_DUMP_LIVE`, `BNXT_DUMP_DRIVER`, and `BNXT_DUMP_CRASH` through ethtool/devlink. Test length-only then copy paths, firmware segment-list failures, oversized firmware data returning `-ENOBUFS`, host DDR crashdump with populated and empty signatures, backing-store trace buffers with wrap detection, optional TEE SOC DDR support, and low-memory allocation failures in segment list retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_coredump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_coredump.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_coredump.h

Purpose: Defines the private coredump file format and debug DMA helper contracts used by `bnxt_coredump.c`. It names the component/segment IDs used for firmware version, driver-owned backing-store memory, firmware trace backing stores, and crash dump sizing.

Important APIs, types, and functions: Key format types are `bnxt_coredump_segment_hdr`, `bnxt_coredump_record`, `bnxt_driver_segment_record`, `bnxt_coredump`, `bnxt_hwrm_dbg_dma_info`, `hwrm_dbg_cmn_input`, and `hwrm_dbg_cmn_output`. The header exports `bnxt_fill_coredump_seg_hdr()`, `bnxt_get_coredump()`, `bnxt_hwrm_get_dump_len()`, and `bnxt_get_coredump_length()`. Constants include segment signatures, `BNXT_VER_GET_COMP_ID`, `BNXT_DRV_COMP_ID`, context-memory segment IDs, 8 MiB crash dump default length, and debug DMA slice sizes.

Control flow: There is no executable control flow in the header. It provides the structure layout consumed by the coredump implementation: each data segment gets a segment header, optional driver segment records can precede backing-store data, and the whole dump ends with a `bnxt_coredump_record` containing system/time/status metadata.

State and persistence behavior: The definitions describe serialized diagnostic state. Most fields are little-endian on output and become part of the coredump artifact handed to userspace through ethtool/devlink style consumers. The header itself has no mutable state.

Dependencies and integration points: It includes kernel utsname/time/rtc declarations and relies on Broadcom HSI identifiers pulled through including source files. It is directly paired with `bnxt_coredump.c` and indirectly with devlink health dump and ethtool dump paths.

Risks: Structure layout and endian fields are externally visible to dump parsers, so changing sizes or signatures can break tooling. `BNXT_COREDUMP_BUF_LEN(len)` subtracts the trailing record size and is used in bounds checks; misuse with small lengths can underflow if callers are not careful. Context segment ID mappings must stay aligned with `bnxt.h` backing-store type constants.

Test signals: Compile-test coredump users, verify generated dumps have `sEgM` segment signatures and final `cOrE` records, check driver-context segment IDs against backing-store types, and run parsers against live, crash, and driver dumps after any format change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_coredump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_dcb.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_dcb.c

Purpose: Implements Data Center Bridging support for `bnxt_en` when `CONFIG_BNXT_DCB` is enabled. It maps Linux dcbnl IEEE ETS, PFC, DCBX mode, RoCE app priority, and DSCP-to-priority operations onto Broadcom HWRM queue and structured-data commands.

Important APIs, types, and functions: Public functions are `bnxt_dcb_init()` and `bnxt_dcb_free()`. The installed `dcbnl_rtnl_ops` callbacks include `bnxt_dcbnl_ieee_getets()`, `bnxt_dcbnl_ieee_setets()`, `bnxt_dcbnl_ieee_getpfc()`, `bnxt_dcbnl_ieee_setpfc()`, `bnxt_dcbnl_ieee_setapp()`, `bnxt_dcbnl_ieee_delapp()`, `bnxt_dcbnl_getdcbx()`, and `bnxt_dcbnl_setdcbx()`. HWRM helpers configure/query priority-to-CoS, CoS-to-bandwidth, PFC enable masks, DCBX app structured data, DSCP capabilities, and DSCP-to-priority entries.

Control flow: Initialization checks HWRM spec level, queries DSCP support, derives DCBX capability flags from PF/VF status and firmware LLDP/DCBX agents, then installs dcbnl ops. ETS set validates priority-to-TC and TSA/bandwidth totals, configures Linux multi-queue TC layout through `bnxt_setup_mq_tc()`, sends HWRM CoS bandwidth and priority mapping, then caches the settings. PFC set derives priority and TC masks from cached ETS, remaps TCs onto lossless queues if necessary, possibly closes/reopens a running NIC, sends the PFC enable mask, then caches PFC. App set/delete updates kernel dcb app state and mirrors RoCE/DSCP mappings into firmware.

State and persistence behavior: DCB state is cached in `bp->ieee_ets`, `bp->ieee_pfc`, `bp->dcbx_cap`, `bp->max_dscp_value`, queue profile arrays, and TC-to-queue mapping. Firmware/NVM may retain DCBX settings when managed by firmware, but host-managed changes here are runtime HWRM programming plus kernel cache. `bnxt_dcb_free()` releases cached ETS/PFC memory.

Dependencies and integration points: It integrates with Linux dcbnl, rtnl/netdev state, RDMA constants for RoCE app selectors, Broadcom HWRM queue commands, `bnxt_open_nic()`/`bnxt_close_nic()` for remap, `bnxt_setup_mq_tc()` for netdev TC layout, `bp->port_stats.hw_stats` for PFC counters, and `bnxt.h` queue/capability state.

Risks: ETS validation has to prevent bandwidth sums over 100 percent and starvation when zero-weight ETS TCs coexist with a full allocation. PFC requires a cached ETS map; enabling PFC on more lossless TCs than supported returns `-EINVAL`. Queue remap while the NIC is running temporarily closes and reopens the device, so failures can disrupt traffic. DCBX capability transitions must reject unsupported host control when firmware LLDP/DCBX agents own the configuration.

Test signals: Test with `CONFIG_BNXT_DCB=y` and disabled, PF and VF devices, firmware-managed and host-managed DCBX, ETS strict/ETS bandwidth edge cases, PFC enabling on lossless and non-lossless queues, live queue remap while traffic is running, RoCE v1/v2 app add/delete, DSCP app bounds, and PFC stats readback from port stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_dcb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_dcb.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_dcb.h

Purpose: Declares the private DCB support structures and helper macros used by `bnxt_dcb.c` to translate Linux DCB configuration into HWRM queue data.

Important APIs, types, and functions: The header defines `bnxt_dcb`, `bnxt_cos2bw_cfg`, `bnxt_dscp2pri_entry`, `BNXT_LLQ()`, `BNXT_CNPQ()`, `BW_VALUE_UNIT_PERCENT1_100`, `HWRM_STRUCT_DATA_SUBTYPE_HOST_OPERATIONAL`, and the `bnxt_dcb_init()`/`bnxt_dcb_free()` prototypes.

Control flow: No executable flow lives here. `bnxt_dcb.c` uses the packed `bnxt_cos2bw_cfg` layout to copy queue bandwidth records into HWRM request slots, uses `BNXT_LLQ()` to decide whether a hardware queue profile is lossless for PFC remapping, and uses `bnxt_dscp2pri_entry` for one-entry DSCP priority updates.

State and persistence behavior: `bnxt_dcb` is a compact DCB state container, but current `struct bnxt` carries the active fields directly under `CONFIG_BNXT_DCB`. The header itself stores no state and defines runtime-only structures.

Dependencies and integration points: It depends on `<net/dcbnl.h>` and HSI queue profile constants included by implementation context. It is private to the bnxt driver DCB path and must align with HWRM queue command layouts.

Risks: The packed group inside `bnxt_cos2bw_cfg` is copied directly into firmware command arrays; layout drift would corrupt queue bandwidth programming. Queue profile macros depend on HSI constant values staying semantically stable.

Test signals: Build with `CONFIG_BNXT_DCB=y`, verify HWRM CoS-to-bandwidth requests for queue 0 and additional queues have correct byte layout, and exercise PFC remap on queue profiles classified by `BNXT_LLQ()`/`BNXT_CNPQ()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_dcb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_debugfs.c

Purpose: Provides debugfs visibility into per-completion-ring DIM state for `bnxt_en` when debugfs is enabled. It creates a `bnxt_en` root and per-PCI-device `dim/<ring>` files that expose the kernel DIM state used for interrupt moderation tuning.

Important APIs, types, and functions: Public lifecycle functions are `bnxt_debug_init()`, `bnxt_debug_exit()`, `bnxt_debug_dev_init()`, and `bnxt_debug_dev_exit()`. Internal helpers are `debugfs_dim_read()` and `debugfs_dim_ring_init()`, backed by `debugfs_dim_fops`.

Control flow: Module init calls `bnxt_debug_init()` to create the root directory. Device init creates a PCI-name directory, a `dim` subdirectory, then iterates `bp->cp_nr_rings` and creates one read-only-style file per RX-capable completion ring. Reads format `struct dim` fields into a temporary string and copy it to userspace once. Device/module exit remove the relevant debugfs trees recursively.

State and persistence behavior: The only module-level state is `bnxt_debug_mnt`, the debugfs root dentry. Per-device state is `bp->debugfs_pdev`. Files expose live in-memory DIM state (`state`, `profile_ix`, `mode`, `tune_state`, `steps_right`, `steps_left`, `tired`) and do not persist values or allow writes.

Dependencies and integration points: It depends on Linux debugfs, module/file operations, PCI names, `struct dim`, and `struct bnxt` ring/NAPI layout from `bnxt.h`. It complements `bnxt_dim.c`, which mutates the DIM profile and applies coalescing.

Risks: `debugfs_dim_ring_init()` uses a static `qname[12]` buffer for file creation names; debugfs copies names during creation, but this pattern would be risky if an API retained the pointer. Reads require caller buffer length at least the formatted output length and return `-ENOSPC` otherwise, which is stricter than many debugfs readers expect. There is no explicit locking around DIM fields, so snapshots may be slightly inconsistent while tuning runs.

Test signals: Build with `CONFIG_DEBUG_FS=y`, load the driver, verify `/sys/kernel/debug/bnxt_en/<pci>/dim/<ring>` files exist only for RX rings, read them during traffic with DIM enabled, test removal on device unload, and build with debugfs disabled to ensure stubs are used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_debugfs.h

Purpose: Declares the bnxt debugfs lifecycle hooks and provides no-op stubs when `CONFIG_DEBUG_FS` is disabled.

Important APIs, types, and functions: Exposes `bnxt_debug_init()`, `bnxt_debug_exit()`, `bnxt_debug_dev_init()`, and `bnxt_debug_dev_exit()` as real prototypes under `CONFIG_DEBUG_FS` and static inline empty functions otherwise.

Control flow: There is no runtime flow in the header beyond compile-time selection. Driver init/remove and device probe/remove paths can call these hooks unconditionally because the header supplies stubs for non-debugfs builds.

State and persistence behavior: The header does not define state. State is owned by `bnxt_debugfs.c` through debugfs dentries when compiled in.

Dependencies and integration points: It includes Broadcom HSI and `bnxt.h` so `struct bnxt` is available for device-level hooks. It integrates the optional debugfs implementation with the always-built driver lifecycle.

Risks: Since stubs silently do nothing, tests for debugfs behavior must ensure the config option is enabled. Including broad headers from a small interface can increase compile coupling.

Test signals: Compile both `CONFIG_DEBUG_FS=y` and `n`, verify call sites need no ifdefs, and confirm no unresolved symbols or dead references when debugfs is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_devlink.c

Purpose: Implements the bnxt devlink interface: device registration, PF devlink port setup, firmware health reporter, flash update, reload actions, selftest, device info reporting, live patch activation/info, runtime remote reset control, and NVM-backed devlink parameters.

Important APIs, types, and functions: Public functions are `bnxt_dl_register()`, `bnxt_dl_unregister()`, `bnxt_dl_fw_reporters_create()`, `bnxt_dl_fw_reporters_destroy()`, `bnxt_devlink_health_fw_report()`, `bnxt_dl_health_fw_status_update()`, and `bnxt_dl_health_fw_recovery_done()`. Devlink ops include `bnxt_dl_flash_update()`, `bnxt_dl_reload_down()`, `bnxt_dl_reload_up()`, `bnxt_dl_info_get()`, selftest callbacks, and SR-IOV eswitch callbacks when enabled. Health reporter callbacks are `bnxt_fw_diagnose()`, `bnxt_fw_dump()`, and `bnxt_fw_recover()`. Parameter helpers handle NVM get/set/validation for SR-IOV, ARI, MSI-X vector min/max, RoCE enable, GRE version check, and remote reset.

Control flow: Registration allocates a devlink object with PF or VF ops, stores `bp` in private devlink state, defaults remote reset enabled, registers a physical devlink port and params for PFs, then registers devlink. Flash update delegates package flashing to ethtool/NVM helpers with devlink progress notifications. Reload down handles driver reinit by stopping ULPs, locking rtnl/netdev, rejecting active SR-IOV, closing NIC, freeing VF reps, unregistering from firmware, clearing reservations, and freeing context memory; reload up reinitializes firmware state, VF reps, NIC, SR-IOV, and PTP PPS. Firmware activation either activates live patches with no reset or requests firmware reset and waits in reload up for reset completion bits. Health reporting diagnoses firmware status, can dump a live coredump via `bnxt_coredump.c`, and triggers reset/exception recovery.

State and persistence behavior: Runtime devlink state is in `bp->dl`, `bp->dl_port`, `bp->fw_health->fw_reporter`, `struct bnxt_dl.remote_reset`, firmware health counters/severity/remedy, and reload state bits such as `BNXT_STATE_FW_ACTIVATE` and `BNXT_STATE_RECOVER`. NVM-backed devlink params persist in firmware NVM through `HWRM_NVM_SET_VARIABLE`. Live patch status is queried from firmware/NVM and activation/deactivation changes firmware patch state. Device info is a read-only snapshot from driver fields, HWRM version output, and NVM package info.

Dependencies and integration points: This file connects to Linux devlink, PCI, netdev locking, HWRM/NVM helpers, bnxt ethtool flashing helpers, VF representor management, ULP stop/start, PTP PPS reapply, coredump generation, firmware reset and health status machinery, and optional SR-IOV eswitch support. It relies heavily on capability bits from `bnxt.h` to hide unsupported params and reload modes.

Risks: Reload paths are lock- and state-sensitive; missing unlocks or inconsistent ULP restart can leave the device closed or resources leaked. Firmware activation waits for asynchronous reset state and must handle closed devices, abort bits, and timeout. NVM param bit/byte conversion and inverted GRE version-check semantics can easily write the wrong persistent value. Health dump allocates potentially large vmalloc buffers and is unsupported from health-report private contexts. Remote reset support must be reprogrammed after recovery because firmware reset can lose runtime state.

Test signals: Exercise `devlink dev info`, flash update success/failure, NVM param get/set for all registered params, invalid MSI-X/RDMA validation, remote reset toggling, flash selftest, live patch activation with no-reset reload, driver-reinit reload with netdev up/down, firmware-activate reload with timeout and success, health reporter diagnose/dump/recover, PF/VF registration, SR-IOV active rejection, and unregister cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_devlink.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_devlink.h

Purpose: Defines the private devlink state and constants for bnxt devlink integration. It provides helpers for mapping devlink objects back to `struct bnxt`, tracking remote reset preference, emitting remote reload notifications, and describing NVM-backed devlink parameters.

Important APIs, types, and functions: Defines `struct bnxt_dl`, `bnxt_get_bp_from_dl()`, `bnxt_dl_remote_reload()`, `bnxt_dl_get_remote_reset()`, `bnxt_dl_set_remote_reset()`, NVM offsets, MSI-X validation limits, `enum bnxt_nvm_dir_type`, `struct bnxt_dl_nvm_param`, `enum bnxt_dl_version_type`, and devlink public prototypes.

Control flow: Inline helpers are used by `bnxt_devlink.c` and firmware recovery code. `bnxt_dl_remote_reload()` reports that a remote reload performed driver reinit and firmware activate actions. Get/set helpers read and update `remote_reset` inside devlink private data.

State and persistence behavior: `struct bnxt_dl` stores the runtime back pointer and a runtime `remote_reset` boolean. NVM offsets describe persistent firmware variables but do not store them directly.

Dependencies and integration points: It depends on Linux devlink types and `struct bnxt` from `bnxt.h`. The NVM offsets and directory type constants are consumed by the devlink parameter get/set code, while health and register prototypes are called from probe/remove and firmware health paths.

Risks: `devlink_priv(dl)` must always contain `struct bnxt_dl`; using helpers with another devlink allocation would corrupt casts. NVM offsets are firmware ABI constants; mistakes can change unrelated persistent settings. The remote reload action mask should stay aligned with devlink reload actions exposed by `bnxt_devlink.c`.

Test signals: Compile devlink users, verify PF/VF devlink registration stores and retrieves `bp`, toggle remote reset and confirm state survives until recovery reprogramming, and validate each NVM offset against firmware documentation or device behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_devlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_dim.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_dim.c

Purpose: Applies Linux net DIM workqueue decisions to bnxt RX interrupt coalescing. It is the small bridge from generic DIM profile selection to the driver's HWRM ring coalescing command.

Important APIs, types, and functions: The only function is `bnxt_dim_work(struct work_struct *work)`. It derives `struct dim`, containing `bnxt_cp_ring_info`, containing `bnxt_napi`, then calls `net_dim_get_rx_moderation()` and `bnxt_hwrm_set_ring_coal()`.

Control flow: When DIM schedules work, this function obtains the current RX moderation profile for `dim->mode` and `dim->profile_ix`, writes the selected usec and packet thresholds into `cpr->rx_ring_coal`, sends the updated coalescing configuration to firmware for that NAPI/ring, and resets DIM state to `DIM_START_MEASURE`.

State and persistence behavior: It mutates per-completion-ring runtime coalescing fields (`coal_ticks`, `coal_bufs`) and DIM state. Firmware receives the new ring coalescing values through HWRM, but no persistent NVM setting is changed.

Dependencies and integration points: It depends on `<linux/dim.h>`, `struct bnxt_cp_ring_info` and `struct bnxt_napi` from `bnxt.h`, and the HWRM coalescing function implemented elsewhere. Debugfs reads the same `struct dim` state exposed by this work item.

Risks: The nested `container_of()` chain assumes `dim` is embedded in `bnxt_cp_ring_info`, which is embedded as `bnxt_napi.cp_ring`; this helper is not valid for non-primary completion rings unless the layout matches. HWRM failures are not checked here, so failed coalescing updates may silently leave firmware using old values while DIM restarts measurement.

Test signals: Enable DIM, generate RX traffic with varying packet rates, observe profile changes through debugfs, verify HWRM coalescing commands are issued per RX ring, and inject `bnxt_hwrm_set_ring_coal()` failures to confirm the driver remains stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_dim.c -->
