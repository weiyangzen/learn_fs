# subset-b-004728 ath11k AHB/CE/CFR/Core Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/ahb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/ahb.c

## Purpose
`ahb.c` is the platform-bus host interface for ath11k SoCs exposed through device tree compatibles such as `qcom,ipq8074-wifi`, `qcom,ipq6018-wifi`, `qcom,ipq5018-wifi`, and hybrid WCN6750. It binds a `platform_driver`, selects AHB or PCIC-style HIF operations, maps device resources, boots the Q6 remote processor, configures firmware memory, and wires copy-engine and datapath interrupts into the ath11k core.

## Important APIs, Types, And Functions
The file owns `ath11k_ahb_probe()`, `ath11k_ahb_remove()`, and `ath11k_ahb_shutdown()` for driver lifecycle. `ath11k_ahb_hif_ops_ipq8074` supplies direct MMIO read/write, CE/ext IRQ enable/disable, service-to-pipe mapping, and remoteproc power control. `ath11k_ahb_hif_ops_wcn6750` delegates most register and IRQ work to PCIC helpers while keeping AHB remoteproc power and SMP2P suspend/resume. IRQ setup is split across `ath11k_ahb_config_irq()`, `ath11k_ahb_config_ext_irq()`, CE tasklets, and NAPI polling. Resource paths include `ath11k_ahb_setup_resources()`, `ath11k_ahb_ce_remap()`, `ath11k_ahb_fw_resources_init()`, `ath11k_ahb_setup_msi_resources()`, and `ath11k_ahb_setup_smp2p_handle()`.

## Control Flow
Probe reads the matched hardware revision, allocates `ath11k_base` with AHB private storage, registers optional PCI ops, initializes hardware params, maps MMIO or MSI resources, remaps CE space when required, initializes fixed firmware memory/IOMMU mappings, sets SMP2P handles, initializes HAL SRNG, allocates CE pipes, fills QMI CE config, obtains the remoteproc, initializes core services, requests IRQs, and triggers QMI cold-boot reset handling. Runtime start enables CE interrupts and posts CE RX buffers. External datapath IRQs disable their group, schedule NAPI, service SRNGs through `ath11k_dp_service_srng()`, then re-enable IRQs after budget completion. Removal waits for recovery if needed, marks unregistering, cancels restart/QMI work, deinitializes core, destroys firmware state, frees IRQs, SRNGs, SMP2P handles, IOMMU mappings, CE pipes, and core memory.

## State And Persistence
State is held in `ath11k_base` plus `struct ath11k_ahb` private data: remoteproc handle, firmware memory addresses/sizes, IOMMU domain, firmware platform device, TrustZone-vs-IOMMU selection, and SMP2P sequence/state. IRQ numbers are cached in `ab->irq_num`, and ext IRQ group membership is derived from hardware ring masks. There is no persistent storage, but the driver consumes device tree memory regions and optional firmware child nodes.

## Dependencies And Integration Points
This file integrates with Linux platform, OF, reserved memory, IOMMU, DMA mapping, remoteproc, qcom SMEM state, NAPI, tasklets, HAL SRNG, CE, QMI, HIF, PCIC, and DP. It is tightly coupled to `core.c` initialization and `ce.c` buffer posting/cleanup.

## Risks And Test Signals
Risk concentrates around error unwinding, IRQ lifecycle, and platform description correctness. `ath11k_ahb_config_ext_irq()` logs request failures but continues, so missing IRQs can surface later as stalled rings. Fixed firmware memory setup has multi-step IOMMU/platform-device unwind paths. Suspend/resume depends on `device_may_wakeup()`, wake IRQ selection, SMP2P sequence updates, and wake completion timing. Useful test signals include successful probe/unprobe on all compatibles, IRQ storm/stall checks under traffic, firmware boot/restart, WoW suspend/resume on WCN6750, and fault injection in IOMMU, remoteproc, and IRQ request paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/ahb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/ahb.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/ahb.h

## Purpose
`ahb.h` defines the private AHB transport state used by `ahb.c` and constants for recovery and SMP2P power-save messages. It is the small contract that lets the generic `ath11k_base` carry AHB-specific remoteproc, firmware memory, and SMEM state without exposing those fields to unrelated transports.

## Important APIs, Types, And Functions
`ATH11K_AHB_RECOVERY_TIMEOUT` bounds removal waits while firmware recovery is active. `ATH11K_AHB_SMP2P_SMEM_MSG`, `ATH11K_AHB_SMP2P_SMEM_SEQ_NO`, and `ATH11K_AHB_SMP2P_SMEM_VALUE_MASK` describe the packed SMEM state value used to enter and exit power save. `enum ath11k_ahb_smp2p_msg_id` provides the `ATH11K_AHB_POWER_SAVE_ENTER` and `ATH11K_AHB_POWER_SAVE_EXIT` command IDs. `struct ath11k_ahb` stores `tgt_rproc`, firmware memory/IOMMU state, and SMP2P state. `ath11k_ahb_priv()` casts `ab->drv_priv` to the AHB private structure.

## Control Flow
The header itself has no runtime flow, but its fields are filled during `ath11k_ahb_probe()` resource setup, consumed during remoteproc power up/down, used by fixed firmware-memory initialization/deinitialization, and updated during WCN6750 HIF suspend/resume when SMP2P messages are sent.

## State And Persistence
All state is in-memory for the device lifetime. The nested `fw` state tracks whether firmware memory is controlled through TrustZone (`use_tz`) or a local IOMMU domain, plus MSA and CE physical regions. The nested `smp2p_info` carries an incrementing sequence number, SMEM bit, and `qcom_smem_state` handle.

## Dependencies And Integration Points
The header includes `core.h`, so it depends on the main ath11k object model and Linux types brought in through core. Its contents are used only by the AHB platform implementation and indirectly by HIF power-management hooks.

## Risks And Test Signals
The key risk is that this private layout must match the `priv_size` passed to `ath11k_core_alloc()` in `ahb.c`; misuse would corrupt driver-private state. SMP2P bit packing must remain consistent with firmware expectations. Test signals are successful AHB probe/remove, WoW suspend/resume SMEM messages, and fixed-memory firmware boot on platforms with `wifi-firmware` nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/ahb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/ce.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/ce.c

## Purpose
`ce.c` implements ath11k Copy Engine host-side rings. Copy Engines move HTC, WMI, HTT, pktlog, and raw/control traffic between host and firmware. The file provides hardware-family CE attribute tables, DMA-coherent ring allocation, HAL SRNG setup, TX submission/completion, RX buffer posting/completion, shadow-register handling, and cleanup.

## Important APIs, Types, And Functions
Exported entry points include `ath11k_ce_alloc_pipes()`, `ath11k_ce_init_pipes()`, `ath11k_ce_free_pipes()`, `ath11k_ce_send()`, `ath11k_ce_per_engine_service()`, `ath11k_ce_rx_post_buf()`, `ath11k_ce_cleanup_pipes()`, `ath11k_ce_get_shadow_config()`, `ath11k_ce_stop_shadow_timers()`, and `ath11k_ce_get_attr_flags()`. The main configuration tables are `ath11k_host_ce_config_ipq8074`, `ath11k_host_ce_config_qca6390`, and `ath11k_host_ce_config_qcn9074`, each defining source/destination ring sizes, max buffer sizes, callbacks, and interrupt-disabling flags.

## Control Flow
Allocation initializes `ab->ce.ce_lock`, creates per-pipe source, destination, and status rings according to hardware params, and uses DMA-coherent descriptor memory aligned to `CE_DESC_RING_ALIGN`. Initialization turns those rings into HAL SRNGs and sets MSI interrupt parameters when interrupts are enabled. TX via `ath11k_ce_send()` optionally polls disabled-interrupt rings, rejects crash flush, obtains a HAL source descriptor, writes the DMA address/length/transfer ID, stores the skb at the write index, and starts the CE4 shadow timer workaround when needed. RX posting allocates skbs, DMA-maps them, queues destination descriptors, and later `ath11k_ce_recv_process_cb()` unmaps, validates lengths, passes skb lists to receive callbacks, and replenishes buffers. Interrupt handlers in bus layers call `ath11k_ce_per_engine_service()` to reap both TX and RX.

## State And Persistence
Per-ring state includes host and CE DMA addresses, software/write indices, HAL ring ID, and skb slots. Per-pipe state includes callbacks, buffer size, interrupt tasklet, and `rx_buf_needed`. State is volatile; descriptor memory and skb DMA mappings are created and destroyed per device lifecycle. The RX replenish retry timer in `ath11k_base` persists across temporary allocation failures until cleanup.

## Dependencies And Integration Points
CE sits between HIF interrupt code, HAL SRNG operations, HTC callbacks, DP HTT handlers, DMA APIs, and hardware params from `core.c`. Shadow-register workarounds integrate with DP shadow timer helpers. HIF start/stop and QMI firmware startup expect CE rings and QMI CE config to be ready.

## Risks And Test Signals
Risk areas include ring index correctness, DMA map/unmap pairing, buffer exhaustion, crash-flush races, disabled-interrupt CE polling, and partial initialization cleanup. Comments explicitly note incomplete cleanup questions for TX buffers and partial ring init. Test signals include WMI/HTC boot traffic, high-throughput HTT TX/RX, repeated firmware restart, RX replenish failure injection, big-endian byte-swap coverage, and KASAN/KMSAN/lockdep checks around `ce_lock` and SRNG locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/ce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/ce.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/ce.h

## Purpose
`ce.h` declares Copy Engine constants, shared firmware configuration records, host ring structures, and public CE APIs. It is the compile-time contract between core/HIF/QMI/HTC/DP code and the CE implementation.

## Important APIs, Types, And Functions
Key constants include `CE_COUNT_MAX`, `CE_ATTR_BYTE_SWAP_DATA`, `CE_ATTR_DIS_INTR`, pipe direction values, CE interrupt-enable register addresses, `CE_RING_IDX_INCR()`, and `ATH11K_CE_RX_POST_RETRY_JIFFIES`. `struct service_to_pipe` and `struct ce_pipe_config` are little-endian records shared with firmware through QMI. `struct ce_attr` describes host ring sizing and callbacks. `struct ath11k_ce_ring`, `struct ath11k_ce_pipe`, and `struct ath11k_ce` hold runtime ring, pipe, and aggregate CE state. Public functions cover pipe allocation/init/free, send, RX posting, service, polling, shadow config, and attr lookup.

## Control Flow
The header supports a lifecycle where hardware params expose CE config arrays, `ath11k_ce_alloc_pipes()` creates rings from `ce_attr`, `ath11k_ce_init_pipes()` registers them with HAL, HIF code enables interrupts, CE service functions process completions, and cleanup/free functions unwind buffers and descriptor memory.

## State And Persistence
The structs define all CE in-memory state. `ath11k_ce_ring` owns descriptor memory addresses and skb tracking slots. `ath11k_ce_pipe` owns callbacks, tasklet, and per-pipe counters. `ath11k_ce` contains the global lock and per-CE shadow timers. No state is persistent across module reload or device re-probe.

## Dependencies And Integration Points
The API depends on Linux skb, DMA, spinlock, and ath11k HAL/DP types. QMI consumes `ce_pipe_config` and `service_to_pipe`; HIF code uses CE attr flags to request and mask interrupts; HTC/DP provide callbacks stored in `ce_attr`.

## Risks And Test Signals
Because firmware consumes some structures directly, field order, endian annotations, and sizes must remain stable. Ring sizes are assumed to be powers of two after allocation, so callers must not bypass rounding. Test signals include build coverage on big-endian and little-endian configs, QMI CE map validation, and ring wraparound under sustained traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/ce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/cfr.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/cfr.c

## Purpose
`cfr.c` implements Channel Frequency Response capture support when firmware and hardware advertise CFR. It configures a direct-buffer ring, exposes debugfs controls, sends per-peer WMI capture commands, correlates DMA buffer release events with WMI TX capture events, and relays binary CFR records to userspace through relayfs.

## Important APIs, Types, And Functions
Main external functions are `ath11k_cfr_init()`, `ath11k_cfr_deinit()`, `ath11k_cfr_get_dbring()`, `ath11k_cfr_lut_update_paddr()`, `ath11k_process_cfr_capture_event()`, `ath11k_cfr_send_peer_cfr_capture_cmd()`, unassociated-peer pool helpers, and `ath11k_cfr_update_phymode()`. Internal helpers calculate tones from DMA headers, fill metadata headers, correlate events in `ath11k_cfr_correlate_and_relay()`, process DBR data in `ath11k_cfr_process_data()`, and manage debugfs/relayfs files.

## Control Flow
Initialization checks `WMI_TLV_SERVICE_CFR_CAPTURE_SUPPORT` and `hw_params.cfr_support`, then for each radio obtains DBR capabilities, initializes IDR and locks, allocates a LUT capped by `CFR_MAX_LUT_ENTRIES`, sets up the direct-buffer SRNG, fills buffers, sends WMI ring configuration, and creates `enable_cfr`, `cfr_unassoc`, and `cfr_capture` debugfs/relayfs files. Data flow has two asynchronous halves: DBR release processing stores DMA data, PPDU ID, metadata, buffer pointer, and timestamp in the LUT; WMI TX capture event processing looks up the same LUT entry by buffer address and fills peer/radio metadata. When both halves arrive and PPDU IDs match, the header, data, and end magic are written to relayfs and the buffer is replenished. Mismatches clear TX state and count DMA aborts.

## State And Persistence
`struct ath11k_cfr` stores runtime locks, LUT, relay/debugfs dentries, peer count, event counters, last success timestamp, phymode, and unassociated peer pool. Peer CFR settings are cached in `ath11k_sta::cfr_capture` and are not persistent. Relayfs output is transient; userspace must consume it live.

## Dependencies And Integration Points
CFR depends on WMI capture service, DBR infrastructure, debugfs, relayfs, mac80211 peer state, firmware TX status fields, and `ath11k_dbring_buffer_release_event()`. The feature is compiled out through `CONFIG_ATH11K_CFR` stubs in the header.

## Risks And Test Signals
Race and lifetime risks center on LUT locking, held buffers, peer count accounting, and deinit while events are in flight. Buffer data length is inferred from DMA header tone and chain fields; malformed firmware data can reject the capture. Useful tests include enabling/disabling CFR via debugfs, per-peer and unassociated peer commands, CFR capture under peer powersave/failure statuses, DBR-before-TX and TX-before-DBR ordering, PPDU mismatch/abort counters, relayfs output validation, and deinit/reinit during traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/cfr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/cfr.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/cfr.h

## Purpose
`cfr.h` defines the CFR feature contract: metadata formats, DMA header bitfields, correlation state, per-radio CFR state, public APIs, and no-op stubs when `CONFIG_ATH11K_CFR` is disabled.

## Important APIs, Types, And Functions
Important constants include `ATH11K_CFR_NUM_RESP_PER_EVENT`, `ATH11K_CFR_EVENT_TIMEOUT_MS`, `ATH11K_CFR_NUM_RING_ENTRIES`, `ATH11K_MAX_CFR_ENABLED_CLIENTS`, `CFR_MAX_LUT_ENTRIES`, magic values, vendor/platform identifiers, tone counts, and `CFIR_DMA_HDR_*` bitfields. Types include `ath11k_cfr_peer_tx_param`, packed `cfr_metadata`, packed `ath11k_csi_cfr_header`, `ath11k_cfr_dma_hdr`, `ath11k_look_up_table`, `cfr_unassoc_pool_entry`, and `ath11k_cfr`. APIs cover init/deinit, DBR lookup/update, peer count/pool updates, WMI command send, event processing, LUT release, and phymode update.

## Control Flow
The header enables `core.c` to initialize/deinitialize CFR, `dbring.c` to find the CFR DBR ring and update LUT physical addresses, WMI event handlers to pass TX capture parameters into CFR correlation, and MAC peer code to configure or clear per-peer CFR state. When CFR is disabled at build time, inline stubs make callers compile without runtime feature checks.

## State And Persistence
The declared state is runtime-only. `ath11k_cfr` contains the DBR ring, locks, LUT, debugfs/relayfs handles, counters, phymode, and unassociated pool. `ath11k_look_up_table` is the correlation record binding a DMA buffer address, DBR data, TX event data, timestamps, and relay header.

## Dependencies And Integration Points
The header includes `dbring.h` and `wmi.h`, and references `ath11k`, `ath11k_sta`, and `ath11k_per_peer_cfr_capture` from the core/MAC object model. Packed binary output structs are consumed by userspace relayfs readers, so their layout is an external ABI-like surface.

## Risks And Test Signals
Layout changes in packed metadata can break CFR consumers. Counter and pool fields require consistent locking in implementation. The disabled-feature stubs return success for some APIs, so call sites must not assume active CFR merely from a zero return. Test signals include compile coverage with and without `CONFIG_ATH11K_CFR`, struct size/layout checks for userspace tooling, and event correlation tests using all supported bandwidth/preamble combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/cfr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/core.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/core.c

## Purpose
`core.c` is the central ath11k lifecycle and hardware-parameter implementation. It defines module parameters, the hardware revision table, firmware/board-data lookup, SoC and pdev creation/destruction, firmware boot handoff, suspend/resume policy, crash recovery, reset orchestration, and allocation of the top-level `ath11k_base`.

## Important APIs, Types, And Functions
Exported functions include `ath11k_core_pre_init()`, `ath11k_core_init()`, `ath11k_core_deinit()`, `ath11k_core_alloc()`, `ath11k_core_free()`, `ath11k_core_qmi_firmware_ready()`, firmware/board-data helpers, suspend/resume hooks, recovery preconfiguration, PM notifier unregister, firmware usecase lookup, and fw stats helpers. The `ath11k_hw_params[]` table maps each hardware revision to firmware directory, CE configs, QMI service ID, ring masks, HAL ops, interface modes, monitor/suspend/regdb/CFR capabilities, memory model, and platform quirks. Module parameters include `debug_mask`, `crypto_mode`, `frame_mode`, and `ftm_mode`.

## Control Flow
Bus drivers allocate `ath11k_base`, set `hw_rev` and HIF ops, then call `ath11k_core_pre_init()` to copy matching hardware params and pre-init firmware metadata. `ath11k_core_init()` sets PM policy from DMI quirks, registers a PM notifier, creates QMI/debugfs SoC state, and powers up HIF. When QMI reports firmware ready, `ath11k_core_qmi_firmware_ready()` applies crypto/raw mode flags, starts firmware, initializes CE pipes, allocates DP, starts WMI/HTC/HIF/HTT, waits for service/unified ready events, allocates MAC objects, initializes REO rings, sends WMI init, creates pdev facilities, and enables HIF IRQs. Deinit reverses pdev, core, HIF power, MAC, SoC, and notifier setup.

## State And Persistence
Persistent-on-disk firmware and board data are requested through Linux firmware APIs; runtime state lives in `ath11k_base` and per-radio `ath11k` objects. Board-data resolution tries API2 names with variant, fallback without variant, chip ID, then legacy `board.bin`; regdb lookup has similar API2 then legacy fallback. Suspend state is mediated by `pm_policy` and `actual_pm_policy`. Recovery uses flags, completions, counters, workqueues, and vdev/peer reset state; no driver state persists across unload.

## Dependencies And Integration Points
`core.c` integrates nearly every subsystem: HIF, QMI, WMI, HTC, DP TX/RX, HAL, MAC/mac80211, debugfs, thermal, spectral, CFR, WoW, firmware loader, DMI, OF, regulatory, coredump, and workqueue/completion primitives. It is called by bus modules such as AHB/PCI and in turn calls feature modules during pdev creation and cleanup.

## Risks And Test Signals
The highest risks are ordering-sensitive startup/teardown, hardware param drift, firmware file lookup regressions, crash recovery races, and suspend/resume corner cases. Error labels often unwind partially initialized subsystems; tests should exercise failure injection at WMI attach, HIF start, service ready, DP allocation, pdev create, and firmware start. Runtime signals include clean boot on each hw revision, board/regdb fallback logs, mac80211 registration, WoW/default suspend resume, repeated firmware crash recovery without wedging, coredump collection, and lockdep checks for `core_lock`, `conf_mutex`, and base/data locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/core.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/core.h

## Purpose
`core.h` is the shared ath11k object model. It defines global constants, enums, skb control blocks, vif/sta/radio/SoC state, firmware stats, debug state, PCI ops, MSI config, PM policy, and prototypes for core lifecycle and firmware helpers.

## Important APIs, Types, And Functions
Major enums cover supported bandwidth, BDF search mode, WME ACs, crypto mode, skb flags, hardware revisions, firmware modes, scan/11d states, device flags, monitor flags, packet/stat counters, ath11k radio state, and PM policy. Core types include `ath11k_skb_cb`, `ath11k_skb_rxcb`, `ath11k_ext_irq_grp`, `ath11k_smbios_bdf`, `ath11k_he`, `ath11k_vif`, `ath11k_sta`, `ath11k`, `ath11k_pdev`, `ath11k_board_data`, `ath11k_pci_ops`, MSI structs, and `ath11k_base`. Inline helpers map TID to AC, convert mac80211 private objects, map MAC ID to radio, build firmware paths, stringify bus and scan states, and expose skb control blocks.

## Control Flow
The header enables all ath11k modules to share a common state graph. Bus drivers allocate `ath11k_base`; core creates per-radio `ath11k`; MAC code stores `ath11k_vif` and `ath11k_sta` in mac80211 private areas; CE/DP/WMI/QMI/debug/coredump modules read or update fields under documented locks and completions. Firmware path creation consults device tree `firmware-name`, usecase firmware mapping, and hardware firmware directories.

## State And Persistence
`ath11k_base` holds SoC-wide state: HIF bus/ops, QMI/WMI/HTC/DP/CE/HAL state, IRQ arrays, ext IRQ groups, hardware params, firmware data, coredump buffer, peer tables, regulatory domains, workqueues, reset/recovery counters, direct-buffer capabilities, MSI data, and private transport storage. `ath11k` holds per-radio mac80211 state, scan/vdev/peer/key completions, locks, tx management IDR, survey/regulatory work, WoW, debug, spectral, thermal, CFR, firmware stats, and power-save fields. State is volatile except firmware files requested through the kernel firmware loader.

## Dependencies And Integration Points
The header pulls in QMI, HTC, WMI, HAL, DP, CE, MAC, HW, RX, regulatory, thermal, DBRing, spectral, WoW, firmware, coredump, and CFR headers. That makes it a high-fanout integration point and a source of compile coupling across the driver.

## Risks And Test Signals
Risk comes from structure size/layout expectations, lock ownership comments that implementations must honor, feature-guarded fields, and helper assumptions such as skb control-block size. Changes need broad build coverage across config combinations (`DEBUGFS`, `SPECTRAL`, `CFR`, testmode), runtime smoke on PCI/AHB buses, mac80211 attach/detach tests, and lockdep/KASAN coverage for peer/vif/radio lifetimes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/coredump.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/coredump.c

## Purpose
`coredump.c` is the devcoredump handoff for ath11k firmware crash data. It classifies firmware memory regions into dump TLV types, triggers HIF-specific dump collection, and uploads the assembled dump buffer to the kernel devcoredump facility.

## Important APIs, Types, And Functions
`ath11k_coredump_get_dump_type()` maps firmware region types such as host DDR, M3, and pageable memory to `enum ath11k_fw_crash_dump_type`, while ignoring BDF/CALDB regions. `ath11k_coredump_collect()` delegates collection to `ath11k_hif_coredump_download()`. `ath11k_coredump_upload()` is the workqueue callback that calls `dev_coredumpv()` with `ab->dump_data` and `ab->ath11k_coredump_len`.

## Control Flow
Crash/reset flow in `core.c` calls `ath11k_coredump_collect()`, allowing the active HIF implementation to download and assemble crash data into `ab->dump_data`. `ath11k_core_alloc()` initializes `ab->dump_work` to `ath11k_coredump_upload()`. When scheduled, upload logs a message, passes ownership of the dump buffer to devcoredump, and clears `ab->dump_data`.

## State And Persistence
The file uses `ath11k_base::dump_data` and `ath11k_coredump_len` as transient ownership state. Persistence is delegated to devcoredump, whose retention and userspace retrieval are kernel-managed.

## Dependencies And Integration Points
It depends on `CONFIG_DEV_COREDUMP`, Linux `devcoredump.h`, HIF coredump download support, and the dump-format definitions in `coredump.h`. It is integrated into reset recovery through `core.c`.

## Risks And Test Signals
The primary risk is buffer ownership: after `dev_coredumpv()` the driver must not free or reuse the buffer. Dump type mapping must stay aligned with firmware region identifiers. Test signals include forced firmware crash, presence of devcoredump artifact, correct TLV type classification, no double-free on dump upload, and graceful no-op behavior when devcoredump is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/coredump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/coredump.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/coredump.h

## Purpose
`coredump.h` defines ath11k firmware crash dump types and binary file/TLV layouts, plus enabled or stubbed coredump APIs depending on `CONFIG_DEV_COREDUMP`.

## Important APIs, Types, And Functions
`ATH11K_FW_CRASH_DUMP_V2` is the dump file version. `enum ath11k_fw_crash_dump_type` classifies paging, RDDM, remote memory, pageable, M3, and ignored dump data. `struct ath11k_tlv_dump_data` is a packed TLV payload with type and length. `struct ath11k_dump_file_data` is the packed top-level dump header containing magic, length, version, chip/QRTR/bus IDs, GUID, timestamp, reserved bytes, and flexible data. Prototypes cover dump type mapping, upload, and collect; stubs are emitted when devcoredump is off.

## Control Flow
HIF coredump code is expected to assemble `ath11k_dump_file_data` containing `ath11k_tlv_dump_data` records. Core reset code calls collect, then upload work eventually exposes that file to devcoredump. Disabled builds compile out collection/upload.

## State And Persistence
The structs define the serialized dump format consumed after a crash. Runtime storage is owned by `ath11k_base` until devcoredump takes it.

## Dependencies And Integration Points
This header is included from `core.h` and `coredump.c`, and indirectly used by bus/HIF-specific dump download implementations. Its packed layouts form an external diagnostic artifact, so compatibility matters beyond the kernel module.

## Risks And Test Signals
Changing packed fields or enum semantics can break dump parsers. Build tests must cover `CONFIG_DEV_COREDUMP=y/n`. Runtime tests should validate dump magic/version/length, TLV alignment, timestamps, GUID presence, and that ignored BDF/CALDB regions are not uploaded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/coredump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dbring.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dbring.c

## Purpose
`dbring.c` implements the generic direct-buffer ring service used by modules such as spectral scan and CFR. It allocates refill SRNGs, allocates and DMA-maps payload buffers, configures firmware via WMI, handles firmware buffer-release events, invokes module handlers, and replenishes buffers.

## Important APIs, Types, And Functions
Public functions include `ath11k_dbring_srng_setup()`, `ath11k_dbring_buf_setup()`, `ath11k_dbring_set_cfg()`, `ath11k_dbring_wmi_cfg_setup()`, `ath11k_dbring_get_cap()`, `ath11k_dbring_buffer_release_event()`, `ath11k_dbring_bufs_replenish()`, cleanup helpers, and `ath11k_dbring_validate_buffer()`. Internal helpers fill buffers with `ATH11K_DB_MAGIC_VALUE` and bulk-fill initial buffers.

## Control Flow
A feature module sets up an RXDMA direct-buffer SRNG, sets response/event parameters and a handler, fills buffers according to firmware-reported capabilities, and sends WMI ring configuration with base/head/tail physical addresses. Replenish aligns the payload, writes magic values, maps it for DMA_FROM_DEVICE, allocates an IDR buffer ID, writes a HAL RX buffer descriptor with a cookie containing pdev and buffer ID, optionally updates the CFR LUT with the physical address, and records debugfs DBR activity. On release events, the code validates pdev/module/counts, finds the active radio, selects spectral or CFR ring, reaps each buffer by cookie, removes its IDR entry, unmaps DMA, calls the module handler, and either holds the buffer for correlation or clears/replenishes it.

## State And Persistence
`struct ath11k_dbring` owns the refill SRNG, IDR, locks, head/tail physical addresses, buffer sizing/alignment, pdev ID, WMI response settings, and handler. Each `ath11k_dbring_element` owns one payload allocation and DMA address. State is runtime-only and freed during feature deinit.

## Dependencies And Integration Points
DBRing depends on HAL SRNG, DP SRNG setup/cleanup, WMI direct-buffer configuration and release event formats, debugfs DBR logging, spectral and CFR module hooks, DMA APIs, IDR, and RCU-protected active pdev tracking.

## Risks And Test Signals
Risk areas include IDR lifetime, DMA map/unmap pairing, held CFR buffers that are not immediately replenished, event count mismatches, single-pdev pdev ID remapping, and cleanup while firmware events arrive. Tests should cover spectral and CFR release paths, invalid module/pdev events, buffer exhaustion, handler hold/release behavior, magic-value validation, and memory leak checks across deinit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dbring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dbring.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dbring.h

## Purpose
`dbring.h` declares the generic direct-buffer ring data structures and API used by spectral/CFR-style firmware DMA streams.

## Important APIs, Types, And Functions
`struct ath11k_dbring_element` tracks a payload allocation and DMA address. `struct ath11k_dbring_data` is passed to feature handlers with aligned data, metadata, buffer pointer, and buffer ID. `struct ath11k_dbring_buf_release_event` normalizes WMI release event parts. `struct ath11k_dbring_cap` mirrors firmware capability for pdev, module, element count, size, and alignment. `struct ath11k_dbring` stores the refill SRNG, IDR, locks, head/tail addresses, buffer parameters, response settings, and handler. Prototypes expose setup, WMI config, replenish, release processing, capability lookup, cleanup, and validation.

## Control Flow
Feature modules obtain capabilities, initialize an `ath11k_dbring`, configure it with a callback, fill buffers, inform firmware, then receive release events through the common event handler. The handler callback decides whether a buffer can be replenished immediately or must be held.

## State And Persistence
All declared state is per-feature/per-radio runtime state. The IDR maps firmware cookies to live buffer elements; the handler pointer is the module-specific processing hook.

## Dependencies And Integration Points
The header depends on Linux types, IDR, spinlocks, and `dp.h` for `dp_srng`. It references WMI direct-buffer modules and release metadata through included dependencies. It is consumed by CFR, spectral, WMI event handling, and debug code.

## Risks And Test Signals
The callback contract is subtle: `ATH11K_CORRELATE_STATUS_HOLD` means ownership remains with the feature until later replenish. Misusing that status can leak buffers or race cleanup. Compile tests should cover modules that include this header, and runtime tests should validate capability lookup, IDR cleanup, and handler ownership rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dbring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debug.c

## Purpose
`debug.c` centralizes ath11k logging wrappers and debug hex dumps. It routes informational, warning, error, and conditional debug messages to device logging and tracepoints.

## Important APIs, Types, And Functions
Exported always-on wrappers are `ath11k_info()`, `ath11k_err()`, and `ath11k_warn()`. Under `CONFIG_ATH11K_DEBUG`, `__ath11k_dbg()` and `ath11k_dbg_dump()` are exported. The wrappers use `struct va_format` so the same formatted message can be sent to `dev_*` logging and `trace_ath11k_log_*` tracepoints.

## Control Flow
Info/error/warn functions build a varargs format and emit to `dev_info`, `dev_err`, or rate-limited `dev_warn`, then trace. Debug logging checks `ath11k_debug_mask` before printing to the device, but it always sends matching tracepoint data when `__ath11k_dbg()` is invoked. `ath11k_dbg_dump()` prints 16-byte hex lines when the mask is enabled and also traces the full dump buffer with null-safe strings.

## State And Persistence
The only external state is the module-global `ath11k_debug_mask` defined in `core.c`. Logs are transient kernel log/trace data; no driver-private persistent state is stored.

## Dependencies And Integration Points
The file depends on `core.h`, `debug.h`, tracepoint definitions, Linux device logging, and hex dump helpers. It is used across nearly all ath11k modules for consistent diagnostics.

## Risks And Test Signals
Risk is mostly diagnostic overhead and format correctness. Warnings are rate-limited, so repeated failures may be hidden in stress logs. Debug dumps can be large when enabled. Test signals include build coverage with and without `CONFIG_ATH11K_DEBUG`, tracepoint enablement, dynamic `debug_mask` changes, and ensuring no NULL `ab`/`dev` callers reach these wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debug.h

## Purpose
`debug.h` defines ath11k debug mask bits, debug string mapping, logging prototypes, disabled-debug stubs, and the `ath11k_dbg()` macro used throughout the driver.

## Important APIs, Types, And Functions
`enum ath11k_debug_mask` assigns bitmasks for AHB, WMI, HTC, DP/HTT, MAC, boot, QMI, data, management, regulatory, testmode, HAL, PCI, DP TX/RX, CE, CFR, and CFR dumps. `ath11k_dbg_str()` maps each mask to a printable prefix. Prototypes cover info/error/warn and, when enabled, debug/dump functions. The `ath11k_dbg()` macro calls `__ath11k_dbg()` when either the mask is enabled or the debug tracepoint is active.

## Control Flow
Callers use `ath11k_dbg(ab, MASK, ...)`; the macro avoids debug formatting work unless logging or tracing needs it. For non-debug builds, inline stubs compile out debug printing and dump behavior while preserving call sites.

## State And Persistence
The header declares `extern unsigned int ath11k_debug_mask`, set through the module parameter in `core.c`. No persistent state is defined.

## Dependencies And Integration Points
It includes `trace.h` and `debugfs.h`, making it the bridge between driver logging, tracepoints, and debugfs-related declarations. Nearly every source file in ath11k can include it.

## Risks And Test Signals
Adding a debug mask requires updating `ath11k_dbg_str()` because there is intentionally no default case. Build tests catch missing enum handling. Runtime tests should verify that tracepoint-only debug still emits through `ath11k_dbg()` even when `debug_mask` is zero, and that disabled-debug builds do not leave unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debug.h -->
