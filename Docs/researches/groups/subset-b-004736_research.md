# subset-b-004736 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/mac.h

Purpose: Declares the ath11k MAC-layer interface used by the driver to connect firmware/WMI/DP/HIF state to mac80211 and cfg80211. It is a header-only contract for capability bit definitions, vdev/ar lookup helpers, scanning, rate conversion, beacon handling, keepalive programming, regulatory TPC fill, and firmware stats requests.

Important APIs, types, and constants: `struct ath11k_generic_iter` is a small iterator result carrier for mac80211 interface walks. The WMI host-rate-control flags (`WMI_HOST_RC_*`) describe peer rate-control capabilities such as HT/VHT, SGI, STBC, UAPSD, WEP/TKIP, and RTS/CTS. HT/VHT capability macros define the bit layout used when advertising target capabilities to firmware and mac80211, including default masks and STBC stream masks. Bandwidth/NSS macros (`ATH11K_BW_NSS_MAP_ENABLE`, `ATH11K_PEER_RX_NSS_160MHZ`, `ATH11K_PEER_RX_NSS_80_80MHZ`) support peer capability translation. OBSS PD macros encode spatial-reuse threshold fields. Exported functions include `ath11k_mac_register()`, `ath11k_mac_unregister()`, `ath11k_mac_allocate()`, 11d scan helpers, vdev/pdev lookup helpers, rate conversion helpers, `ath11k_mac_drain_tx()`, `ath11k_mac_peer_cleanup_all()`, beacon and beacon-miss handlers, `ath11k_mac_vif_set_keepalive()`, `ath11k_mac_fill_reg_tpc_info()`, and `ath11k_mac_fw_stats_request()`.

Control flow: This header does not implement behavior; it defines the call surface used by core, WMI event handlers, regulatory code, data path, and bus code. Core initialization allocates/registers MAC instances through these declarations. WMI/regulatory paths call the lookup helpers to translate firmware vdev or pdev identifiers into `struct ath11k`/`struct ath11k_vif`. Scan and 11d paths use `ath11k_mac_11d_scan_start()`, stop variants, and scan-finish helpers to coordinate firmware scans with mac80211 state. TX/RX status paths use rate and HE RU/GI conversion helpers to translate firmware encodings into nl80211/mac80211 values.

State and persistence behavior: The header owns no runtime state, but its constants encode persistent ABI assumptions between ath11k, firmware WMI commands/events, and mac80211 capability reporting. The keepalive constants deliberately use very high idle/unresponsive values so hostapd-owned keepalive behavior wins over firmware behavior. Correctness depends on surrounding structures in `core.h` and `wmi.h` retaining fields such as vdev IDs, pdev IDs, channel contexts, and firmware stats request state.

Dependencies and integration points: Depends on mac80211, cfg80211, WMI definitions, HTT RX ring filters, HAL encryption types, and ath11k core types. It is included by code paths such as P2P NOA, regulatory handling, WMI event processing, DP TX encryption mapping, and bus/core lifecycle code. The public function declarations bridge firmware-specific encoding to Linux wireless stack abstractions.

Risks and edge cases: Capability bit masks are firmware ABI sensitive; a wrong shift or default mask can advertise unsupported HT/VHT/STBC/LDPC behavior or suppress valid capabilities. `WMI_VHT_CAP_MAX_AMPDU_LEN_EXP_SHIT` appears to preserve an existing misspelled macro name, so renaming would be a source compatibility change. Lookup helpers must cope with stale vdev IDs during teardown/recovery. Keepalive constants rely on firmware interpreting seconds consistently. Rate conversion helpers must reject unknown firmware ratecodes without corrupting mac80211 rate reporting.

Test signals: Build ath11k with `W=1` to catch signature drift between headers and implementations. Runtime coverage should include multi-radio vdev lookups, 11d scan start/stop during user regulatory changes, HT/VHT/HE capability advertisement on supported hardware, legacy/CCK/OFDM rate conversion, beacon miss events, keepalive configuration, firmware stats requests, and regulatory TPC fill for active channel contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/mhi.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/mhi.c

Purpose: Implements ath11k's integration with the Linux MHI bus for PCIe-connected Qualcomm WLAN devices. It configures MHI channels/events, wires MSI vectors, selects firmware images, powers firmware up/down, handles MHI execution-environment callbacks, and exposes suspend/resume/coredump helpers to the PCI HIF layer.

Important APIs, types, and functions: Static `mhi_channel_config`, `mhi_event_config`, and `mhi_controller_config` instances describe IPCR channel 20/21 and control/data event rings for QCA6390/WCN6855/QCA2066/QCA6698AQ and QCN9074. `ath11k_mhi_register()` allocates and registers an `mhi_controller`, fills firmware image or embedded AMSS data, MSI IRQ array, IOVA range, RDDM/SBL/FBC sizing, callback hooks, and hardware-specific MHI config. `ath11k_mhi_start()` prepares and synchronously powers up MHI. `ath11k_mhi_stop()` powers down normally or via `mhi_power_down_keep_dev()` for suspend. `ath11k_mhi_suspend()` and `ath11k_mhi_resume()` wrap MHI PM entry points, with resume forced for devices that remain functional outside M3. `ath11k_mhi_coredump()` downloads RDDM data. Register helpers clear MHI/PCIe vector doorbell/status registers and set `MHICTRL_RESET`.

Control flow: PCI probe initializes BAR/MSI/core state, then calls `ath11k_mhi_register()`. That function selects firmware data from `firmware-N.bin` AMSS data when present or falls back to the legacy `amss.bin` path, obtains the "MHI" MSI assignment through `pcic`, computes IOVA ranges from fixed memory DT or DMA mask, chooses config by `ab->hw_rev`, and calls `mhi_register_controller()`. Power-up sets a long boot timeout, calls `mhi_prepare_for_power_up()`, then `mhi_sync_power_up()`. Power-down chooses suspend or normal MHI power-down and unprepares. MHI status callbacks log transitions; SYS_ERROR warns, and first consecutive RDDM queues `ab->reset_work` unless the device is unregistering.

State and persistence behavior: State is per `struct ath11k_pci`: `mhi_ctrl`, allocated `irq` array, `mhi_pre_cb`, AMSS path, and MHI images owned by the MHI core. It persists across firmware running time and is freed by `ath11k_mhi_unregister()`. No state is durable after device removal. The RDDM image persists in MHI controller memory long enough for PCI coredump collection. Fixed memory systems set `iova_start/stop` from DT memory resources rather than the PCI DMA mask.

Dependencies and integration points: Depends on Linux MHI, PCI/MSI, firmware loading, DT memory parsing, MMIO read/write, and ath11k PCI common register access. It is called by `pci.c` HIF power and coredump paths, and it relies on `pcic.c` MSI assignment and register window access. Firmware image selection integrates with ath11k core firmware packaging. MHI crash callbacks integrate with ath11k recovery workqueues.

Risks and edge cases: MSI assignment must match the MHI channel event IRQ indexes; one-vector fallback changes IRQ sharing and balancing assumptions. Fixed memory DT parsing assumes a usable "memory" node and reserves an offset from its start. Consecutive RDDM suppression uses `mhi_pre_cb`; missed state reset could suppress a valid later crash signal. `mhi_power_down_keep_dev()` is a suspend workaround and differs from normal cleanup, so resume tests must cover both paths. Register clear/reset sequencing is hardware sensitive and uses fixed delays.

Test signals: Probe/power-cycle QCA6390, WCN6855/QCA2066/QCA6698AQ, and QCN9074 variants with multi-MSI and one-MSI fallback. Exercise embedded AMSS vs legacy AMSS file loading, fixed-memory DT IOVA mode, MHI SYS_ERROR/RDDM recovery, suspend/resume including forced resume, coredump RDDM download, unregister after failed registration, and compile coverage for all supported `hw_rev` cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/mhi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/mhi.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/mhi.h

Purpose: Declares the ath11k MHI-facing API and the PCIe/MHI register offsets used by reset and vector-clear logic. It is the small boundary between PCI/HIF lifecycle code and the MHI implementation.

Important APIs and constants: Register constants define TX/RX vector doorbell/status offsets (`PCIE_TXVECDB`, `PCIE_TXVECSTATUS`, `PCIE_RXVECDB`, `PCIE_RXVECSTATUS`) and MHI control/status offsets (`MHISTATUS`, `MHICTRL`, `MHICTRL_RESET_MASK`). Public functions are `ath11k_mhi_register()`, `ath11k_mhi_unregister()`, `ath11k_mhi_start()`, `ath11k_mhi_stop()`, `ath11k_mhi_suspend()`, `ath11k_mhi_resume()`, `ath11k_mhi_set_mhictrl_reset()`, `ath11k_mhi_clear_vector()`, and `ath11k_mhi_coredump()`.

Control flow: `pci.c` includes this header to register MHI during probe, start MHI during power-up, stop it during power-down/suspend, clear vectors and reset MHI during software reset, and fetch RDDM data during devcoredump. The reset helpers are used before or after SoC global reset to restore the MHI block to a known state.

State and persistence behavior: The header has no own state, but it exposes functions that mutate `struct ath11k_pci` and `struct mhi_controller` lifecycle state. Register constants are stable hardware ABI values and must stay aligned with target PCIe/MHI register maps.

Dependencies and integration points: Includes `pci.h` for `struct ath11k_pci` and implicitly depends on MHI controller declarations through included PCI/core headers. It integrates with Linux MHI, ath11k PCI reset paths, and coredump collection.

Risks and edge cases: Wrong register offsets or reset mask values can leave firmware in SYSERR, miss vector cleanup, or break post-reset MHI boot. Function declarations must remain synchronized with `mhi.c`; signature drift breaks HIF build. The coredump declaration exposes an `mhi_controller` pointer, so callers must ensure the controller remains registered while downloading RDDM.

Test signals: Build with PCI/MHI ath11k enabled. Runtime validation should include warm reset after firmware crash, suspend/resume, vector clear around SoC reset, and coredump invocation before MHI unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/mhi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/p2p.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/p2p.c

Purpose: Builds and stores Wi-Fi Direct P2P Notice of Absence (NOA) information elements from firmware WMI P2P NOA events. The generated vendor-specific IE is cached on the AP vif so beacon/probe-response code can advertise opportunistic power-save and absence schedules.

Important APIs, types, and functions: `ath11k_p2p_noa_ie_len_compute()` derives the exact IE length from descriptor count and OPPPS state. `ath11k_p2p_noa_ie_fill()` writes the P2P vendor IE header, WFA OUI/type, NOA attribute ID/length, index, OPPPS CTWindow, and each `ieee80211_p2p_noa_desc` in little endian. `ath11k_p2p_noa_ie_assign()` frees the old `arvif->u.ap.noa_data` and updates the cached pointer/length under `ar->data_lock`. `ath11k_p2p_noa_update()` is the public locked update entry point. `ath11k_p2p_noa_update_by_vdev_id()` iterates active mac80211 interfaces atomically and updates the matching vdev.

Control flow: A WMI P2P NOA event supplies `struct ath11k_wmi_p2p_noa_info`. The by-vdev helper packages vdev ID and NOA pointer into `ath11k_p2p_noa_arg`, then uses `ieee80211_iterate_active_interfaces_atomic()` to find the `ath11k_vif`. The update path takes `data_lock`, clears any previous NOA IE, computes whether a new IE is needed, allocates it with `GFP_ATOMIC`, fills it, and stores it for later beacon/probe response use. Empty descriptor count with OPPPS disabled removes the cached IE.

State and persistence behavior: NOA state is volatile per AP `ath11k_vif` in `arvif->u.ap.noa_data` and `noa_len`. Updates replace the whole cached IE and free the previous allocation. There is no durable persistence; state disappears when the vif is removed. Locking relies on `ar->data_lock` because the update can run in atomic interface-iteration context and because beacon composition may read the same cached IE.

Dependencies and integration points: Depends on ath11k core/vif layout, WMI P2P NOA bit definitions, mac80211 active-interface iteration, `ieee80211_p2p_noa_attr` layouts, WLAN OUI constants, and kernel bitfield/endian helpers. It integrates with WMI event delivery and the MAC beacon path through the cached `arvif->u.ap` NOA fields.

Risks and edge cases: Descriptor count is trusted from firmware bitfields; it must not exceed the descriptor array capacity in the WMI structure or the IE buffer layout. Allocation uses `GFP_ATOMIC`, so memory pressure silently drops NOA advertisement after clearing the previous IE. Length fields use `len - 2` and a 16-bit NOA attribute length; callers must keep lengths in valid vendor-IE range. The checked-out source has `ath11k_p2p_noa_ie_assign(arvif, ie, len); }` on one line, which may be harmless formatting but should be compile-checked. Readers must not dereference old `noa_data` after replacement.

Test signals: Build ath11k with P2P enabled and run static analysis for descriptor bounds and brace syntax. Runtime tests should inject WMI NOA events with zero descriptors/no OPPPS, OPPPS-only, one and multiple descriptors, malformed maximum descriptor counts, repeated updates, AP vif teardown during update, and beacon/probe response inspection for correct P2P IE header, attribute length, little-endian descriptor fields, CTWindow, and OPPPS bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/p2p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/p2p.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/p2p.h

Purpose: Declares the public P2P NOA update interface for ath11k. It keeps WMI P2P NOA event handling decoupled from the implementation that builds and stores beacon-ready P2P NOA IEs.

Important APIs and types: `struct ath11k_p2p_noa_arg` carries a firmware `vdev_id` and `struct ath11k_wmi_p2p_noa_info` pointer into mac80211 interface iteration. `ath11k_p2p_noa_update()` updates a known `ath11k_vif`. `ath11k_p2p_noa_update_by_vdev_id()` locates the vif by vdev ID before updating. The header forward-declares `struct ath11k_wmi_p2p_noa_info` and includes WMI definitions needed by users.

Control flow: WMI event code can call the by-vdev helper when only a vdev ID is known. MAC/vif-specific code can call the direct helper when it already holds the `ath11k_vif`. Both routes converge in `p2p.c` and update cached AP NOA data under the radio data lock.

State and persistence behavior: The header has no own state. Its declared helpers mutate per-vif NOA cache state in the implementation. The `noa` pointer in `ath11k_p2p_noa_arg` is borrowed for the duration of interface iteration and must outlive that synchronous call.

Dependencies and integration points: Depends on ath11k core types, WMI P2P structures, and mac80211 interface iteration through the implementation. It is an integration point between firmware event decoding and AP beacon/probe-response generation.

Risks and edge cases: Callers must pass a valid `ath11k_vif` or vdev ID matching an active interface; otherwise the update is ignored. Since by-vdev iteration is atomic, the implementation must not sleep. The borrowed NOA pointer must not point to stack data that expires before iteration completes.

Test signals: Compile coverage for WMI users of the header, direct and by-vdev update paths, missing vdev ID handling, and AP teardown with pending NOA updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/p2p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/pci.c

Purpose: Implements the PCI bus driver and HIF backend for PCIe ath11k devices. It claims PCI resources, maps BAR registers, handles register windows, configures MSI, boots firmware through MHI/QMI, manages power/reset/suspend/resume, exposes HIF ops to core code, and optionally packages firmware crash dumps.

Important APIs, types, and functions: The PCI ID table matches QCA6390, WCN6855, and QCN9074. `struct ath11k_pci_ops` instances provide wake/release and windowed register access for QCA6390-like and QCN9074-like hardware. `ath11k_pci_window_read32()`/`write32()` select dynamic or static register windows. Reset helpers include `ath11k_pci_sw_reset()`, `ath11k_pci_soc_global_reset()`, `ath11k_pci_clear_dbg_registers()`, `ath11k_pci_enable_ltssm()`, and L1SS fixups. MSI helpers allocate multi-vector or one-vector fallback and refresh endpoint MSI data after IRQ request. `ath11k_pci_probe()` and `ath11k_pci_remove()` own device lifecycle. HIF ops map core calls to PCI/MHI/PCIC functions. Devcoredump helpers calculate and copy paging, RDDM, and QMI target memory segments into an ath11k dump file.

Control flow: Probe allocates `ath11k_base`, claims BAR0, sets DMA masks, maps memory, chooses PCI ops and `hw_rev` from PCI ID plus SoC version/subversion registers, initializes MSI config, allocates MSI vectors, runs core pre-init, sets IRQ affinity, registers MHI, initializes HAL SRNG, allocates CE pipes, initializes QMI CE config, configures CE/DP IRQs through `pcic`, refreshes MSI data, and calls `ath11k_core_init()`. Power-up performs software reset, disables ASPM during firmware download, enables MSI, starts MHI, and selects static windows where applicable. Core start later restores ASPM for multi-MSI systems and enables PCIC. Removal cancels reset/dump work, deinitializes core/QMI/firmware/MHI/IRQ/MSI/BAR/HAL/CE in reverse order, with a special path for QMI boot failures.

State and persistence behavior: Per-device state lives in `struct ath11k_pci`: PCI device pointer, device ID, MHI controller, AMSS path, register window cache protected by `window_lock`, ASPM restore flag/link control, and DMA mask. `ab->mem`/`mem_ce`, MSI base address/data, `dev_flags`, firmware images, CE/SRNG state, and QMI state persist while the device is bound. No disk persistence exists, but firmware/BDF files are loaded from the firmware tree and devcoredump exposes crash data to userspace. ASPM state is saved and restored around firmware boot unless one-vector fallback requires leaving ASPM disabled.

Dependencies and integration points: Depends on Linux PCI/MSI/PM, DMA mapping, MHI, QMI, ath11k core/HIF/HAL/CE/PCIC/debug/coredump layers, firmware APIs, device tree reserved memory flags, and cfg80211/mac80211 via core init. It provides the `ath11k_hif_ops` used by common ath11k code and consumes `pcic.c` for shared MSI/IRQ/register operations.

Risks and edge cases: Probe has many partially initialized resources; unwind ordering must match allocation order or leak IRQs, MHI controllers, CE pipes, SRNGs, or BAR mappings. Register window selection is lock-sensitive and must be restored after SoC global reset. One-MSI fallback changes interrupt sharing and leaves ASPM disabled to avoid MHI M2 hangs. Device subversion matching for WCN6855/QCA2066/QCA6698AQ is hardware-specific; unknown variants fail probe. Devcoredump copies from IO memory and QMI target memory, so segment sizes and validity must be checked carefully. Suspend callbacks intentionally return success in some failure cases to let system suspend continue.

Test signals: Build with `CONFIG_ATH11K_PCI`, MHI, PM, and devcoredump permutations. Runtime tests should cover probe/remove failure injection at each stage, QCA6390/WCN6855/QCA2066/QCA6698AQ/QCN9074 revision detection, multi-MSI and single-MSI fallback, dynamic/static register windows, firmware boot and QMI failure path, reset/recovery, suspend/resume/late suspend/early resume, shutdown, ASPM restore policy, coredump after firmware crash, and hot reset/link-down behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/pci.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/pci.h

Purpose: Defines PCIe hardware register constants and the per-device PCI private state used by ath11k's PCI HIF implementation. It is consumed by PCI, MHI, and PCIC code.

Important APIs, types, and constants: Register constants cover SoC global reset, WLAON warm/reset cause registers, Q6 cookie, PCIe wake scratch, LTSSM/hot reset, interrupt clear, QSERDES/PCS L1SS fixup registers from `hw_params`, QFPROM power control, and reset mask values. `enum ath11k_pci_flags` currently tracks whether ASPM should be restored. `struct ath11k_pci` stores the `pci_dev`, `ath11k_base`, device ID, AMSS path, MHI controller, MSI config pointer, previous MHI callback, register window cache and lock, flags, saved link control, and DMA mask. `ath11k_pci_priv()` casts `ab->drv_priv`, and `ath11k_pci_get_msi_irq()` exposes PCI vector lookup.

Control flow: `pci.c` initializes `struct ath11k_pci` at probe, fills hardware IDs and MHI/PCI state, and uses the register constants during reset/power sequencing. `mhi.c` uses the MHI controller pointer and AMSS path and calls `ath11k_pci_get_msi_irq()`. `pcic.c` uses common PCI ops installed by the PCI layer to access register windows and MSI vectors.

State and persistence behavior: The header declares runtime state but does not manage it. `register_window` caches the selected register window and must be protected by `window_lock`. `link_ctl` persists the pre-boot ASPM state so it can be restored. `dma_mask` is derived from PCI DMA mask configuration and later used for MHI IOVA range setup.

Dependencies and integration points: Depends on Linux MHI, PCI core through implementation users, and ath11k core structures. It bridges bus-specific private state into the common `ath11k_base` allocation.

Risks and edge cases: Register constants are hardware ABI values; incorrect offsets can wedge reset, wake, or L1SS behavior. `ath11k_pci_priv()` assumes `drv_priv` was allocated with `sizeof(struct ath11k_pci)`. Saved ASPM state must only be restored when it was actually cleared. The AMSS path buffer size must remain large enough for firmware paths built by core helpers.

Test signals: Compile all PCI/MHI users, probe supported PCI IDs, run reset and L1SS fixup paths on hardware with and without static register maps, validate ASPM save/restore, and verify MSI vector lookup with multi-vector and one-vector fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/pcic.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/pcic.c

Purpose: Provides PCI-common support shared by ath11k PCI-style bus implementations. It owns hardware-revision MSI layouts, register read/write wrappers with optional wakeup, CE and DP interrupt allocation/enable/disable, NAPI scheduling for external rings, service-to-CE mapping, and registration of bus-specific PCI ops.

Important APIs, types, and functions: `ath11k_msi_config[]` maps hardware revisions to vector users: MHI, CE, WAKE, and DP. `ath11k_pcic_init_msi_config()` selects the matching layout. `ath11k_pcic_read32()`, `write32()`, and `read()` access BAR/windowed registers, waking devices when initialized and reading offsets beyond the always-accessible range. MSI helpers expose address/data and user assignments. IRQ configuration functions request CE tasklet IRQs and DP external IRQ groups with NAPI dummy netdevs. `ath11k_pcic_start()` enables device-init flag, CE IRQs, and CE RX buffers; `ath11k_pcic_stop()` disables/synchronizes/kills CE IRQ tasklets and cleans pipes. `ath11k_pcic_map_service_to_pipe()` maps WMI/HTC service IDs to UL/DL CE pipes.

Control flow: PCI probe calls `ath11k_pcic_init_msi_config()` after hardware revision detection, then `ath11k_pcic_config_irq()` after CE/HAL setup. CE IRQ handlers timestamp, disable the IRQ, and schedule a tasklet that services the CE engine and re-enables the IRQ. DP external IRQ handlers disable all IRQs in a group and schedule NAPI; poll services SRNGs and re-enables group IRQs when work is below budget. Start/stop gates CE IRQ state with `ATH11K_FLAG_CE_IRQ_ENABLED`; external IRQ enable/disable gates DP NAPI with `ATH11K_FLAG_EXT_IRQ_ENABLED`. Register reads/writes optionally call bus wake/release hooks around accesses above `ATH11K_PCI_ACCESS_ALWAYS_OFF`.

State and persistence behavior: MSI layout is stored in `ab->pci.msi.config`; IRQ numbers are cached in `ab->irq_num`. CE tasklets live in `ab->ce.ce_pipe[]`. External IRQ group state (`ab`, group ID, IRQ list, NAPI dummy netdev, timestamp, enabled flag) persists until `ath11k_pcic_free_irq()`. Device flags track whether CE/DP/device-init paths are active. No durable persistence exists.

Dependencies and integration points: Depends on Linux IRQ, tasklet, NAPI, dummy netdev, MSI, ath11k CE, DP SRNG service, core flags, hardware params/ring masks, and bus-specific `ath11k_pci_ops`. It is called by `pci.c` HIF ops and by MHI/QMI code for MSI assignments and register access.

Risks and edge cases: One-MSI fallback bypasses per-vector enable/disable in several helpers, making shared IRQ behavior different from multi-MSI. Error unwinding in external IRQ allocation must free both requested IRQs and allocated dummy netdevs. `ath11k_pcic_read()` continues after wakeup failure to collect crash clues, so callers must treat data as possibly invalid. Service-to-pipe mapping returns `-ENOENT` if either direction is missing and warns on duplicates. NAPI enable/disable must be synchronized with IRQ disable to avoid polls after teardown. `irq_name` indexing must stay aligned with `ATH11K_PCI_IRQ_*` offsets.

Test signals: Build PCI-common users for all supported `hw_rev` MSI layouts. Runtime coverage should include CE IRQ service and tasklet kill, DP NAPI budget and IRQ re-enable, one-MSI vs multi-MSI interrupt sharing, start/stop/restart, wakeup-required register access, coredump register reads after failed wake, service-to-pipe mapping for all configured services, IRQ allocation failure injection, and device removal while NAPI/tasklets are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/pcic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/pcic.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/pcic.h

Purpose: Declares the PCI-common ath11k interface and shared PCI window/IRQ constants used by PCI HIF and related modules.

Important APIs and constants: IRQ offsets define CE IRQ base `ATH11K_PCI_IRQ_CE0_OFFSET`, DP IRQ base `ATH11K_PCI_IRQ_DP_OFFSET`, and the special CE wake IRQ. Window constants define enable bit, selector register, value mask, window start, window range mask, and the always-accessible BAR offset threshold. Public functions cover MSI assignment/address lookup, register read/write/range read, CE MSI index calculation, IRQ config/free/start/stop, external IRQ enable/disable, CE IRQ enable/disable-sync, MSI config selection, PCI ops registration, service-to-pipe mapping, and wake-IRQ-preserving CE IRQ toggles.

Control flow: Bus-specific PCI code registers mandatory PCI ops, initializes MSI config, configures IRQs, and exposes these helpers through HIF ops. MHI asks for the MHI MSI assignment. QMI/HTC code maps services to CE pipes. Power and recovery paths use start/stop and selective CE IRQ helpers.

State and persistence behavior: The header has no state but defines stable offsets and function contracts that mutate `ath11k_base` PCI/IRQ/CE/DP state. The window constants define how high register offsets are mapped through BAR window selection.

Dependencies and integration points: Includes ath11k core definitions and depends on bus-specific `ath11k_pci_ops` being present in `ab->pci.ops`. Integrates with Linux IRQ/NAPI through the implementation and with MHI/QMI/HIF through exported functions.

Risks and edge cases: Offset constants must match hardware and `irq_name`/MSI layouts. Callers must not use register helpers before PCI ops are registered. Range reads use inclusive `start`/`end` and assume 32-bit alignment. Selective CE IRQ helpers must keep the wake IRQ enabled/disabled as intended during WoW or low-power flows.

Test signals: Compile all declaration users, validate register window access above and below the always-accessible range, verify MHI/CE/DP MSI assignment for each hardware revision, and exercise CE IRQ except-wake helpers in suspend/resume scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/pcic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/peer.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/peer.c

Purpose: Manages ath11k peer lifetime and lookup state. It reconciles firmware HTT peer map/unmap events with host-created peer records, maintains list and rhashtable lookups by ID/address, waits for firmware peer create/delete completion, and cleans stale peers during vdev teardown.

Important APIs, types, and functions: Lookup helpers include list-backed `ath11k_peer_find()`, address rhashtable `ath11k_peer_find_by_addr()`, ID rhashtable `ath11k_peer_find_by_id()`, and vdev lookup. Firmware event handlers are `ath11k_peer_map_event()` and `ath11k_peer_unmap_event()`. Peer lifecycle functions are `ath11k_peer_create()`, `ath11k_peer_delete()`, `ath11k_wait_for_peer_delete_done()`, and `ath11k_peer_cleanup()`. Rhashtable functions initialize/destroy ID/address tables and add/delete peer entries. Wait logic uses `ath11k_wait_for_peer_common()` and `ab->peer_mapping_wq`.

Control flow: Firmware peer-map events create a list entry if one does not exist, fill vdev ID, peer ID, AST hash, HW peer ID, MAC address, and wake waiters. Host peer creation first checks peer limits and same-address conflicts, removes a conflicting roaming peer from rhashtable if needed, sends WMI peer create, waits for the peer-map event, then adds the mapped peer to both rhashtables, stores pdev/STA metadata, updates STA TCL metadata, initializes open security types, and increments `ar->num_peers`. Deletion removes the correct peer from rhashtables, sends WMI peer delete, waits for unmap and delete response completion, then decrements `num_peers`. Unmap events remove the list entry, free it, and wake waiters.

State and persistence behavior: Peer state is volatile in `ab->peers`, two optional rhashtables, `ar->num_peers`, and per-peer fields including key pointers, RX TIDs, security type, authorization, and DP setup status. `ab->base_lock` protects list/rhashtable lookup from interrupt context, while `ab->tbl_mtx_lock` serializes rhashtable mutation and table lifecycle. `ar->conf_mutex` is required for create/delete/cleanup. No state persists beyond driver lifetime.

Dependencies and integration points: Depends on ath11k core, WMI peer create/delete commands, HTT map/unmap events, wait queues, completions, spinlocks, mutexes, rhashtable, mac80211 STA/vif state, DP RX TID structures, and TCL metadata definitions. It is central to MAC station/vdev operations, DP RX/TX peer lookup, crypto key tracking, and recovery cleanup.

Risks and edge cases: Firmware map/unmap events are asynchronous; timeouts can leave peers in list-only or rhashtable-removed states. Same MAC address on different vdevs during band transition is handled by removing the old peer from rhashtable, so address lookups may temporarily miss a valid list peer. `ath11k_peer_unmap_event()` frees the peer without rhashtable deletion; host deletion must remove rhashtable entries before requesting firmware unmap. Lock ordering between `tbl_mtx_lock` and `base_lock` is important. Peer count must not underflow during cleanup/failure fallback. Crash flush wakes waits but may leave normal completion absent.

Test signals: Exercise peer create/delete for STA/AP/mesh-like vdevs, same-address roaming across bands, firmware create timeout, delete timeout, delete response timeout, crash flush during waits, stale cleanup during vdev teardown, rhashtable init/destroy failure injection, duplicate ID/address insertions, concurrent DP lookups under traffic, key/TID cleanup after unmap, and peer limit enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/peer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/peer.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/peer.h

Purpose: Defines ath11k peer state and declares peer-management APIs. It is the shared contract for MAC, WMI, HTT/DP, and crypto code that needs to create, find, update, or remove firmware peers.

Important APIs and types: `struct ath11k_peer` contains list linkage, mac80211 STA pointer, vdev ID, MAC address, firmware peer ID, AST hash, pdev index, HW peer ID, key pointers indexed by WMI key slot, DP RX TID state for all TIDs plus management, rhashtable heads for ID/address lookup, MIC verification key indexes, security types, authorization state, and DP setup status. Declared functions cover map/unmap event handling, lookup by vdev/address/ID, cleanup, create/delete/wait-delete, rhashtable table init/destroy, and rhashtable deletion.

Control flow: WMI/HTT event handlers call map/unmap declarations when firmware reports peer ID association changes. MAC station/vdev code calls create/delete and waits for firmware completion. Data path code can look up peers by address or ID to process RX/TX metadata and security state. Recovery and teardown call cleanup and table destroy.

State and persistence behavior: The structure represents runtime peer state only. Fields annotated as protected by `ab->data_lock` must be accessed under that lock, while list/rhash fields are managed under `base_lock` and `tbl_mtx_lock` in the implementation. Key pointers are non-owning references to mac80211 key configuration and must be cleared when keys are removed.

Dependencies and integration points: Depends on list/rhashtable infrastructure, mac80211 STA/key types, WMI key constants, DP RX TID structures, and core ath11k locks. It integrates peer security, DP reorder/TID handling, firmware peer IDs, and MAC station state.

Risks and edge cases: Consumers must honor lock ownership or risk stale peer pointers after unmap. Address and ID rhashtable entries can be absent during create/delete transitions even while a list entry exists. Same-address peers on different vdevs need vdev-sensitive checks. `rx_tid[IEEE80211_NUM_TIDS + 1]` includes an extra management/non-QoS slot; users must index consistently.

Test signals: Compile users after structure changes, run lockdep under station association/disassociation, validate peer lookup by ID/address under traffic, add/remove keys across peer deletion, and test recovery cleanup with outstanding peer map/unmap events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/peer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/qmi.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/qmi.c

Purpose: Implements the ath11k QMI WLAN firmware control path. It registers with the Qualcomm WLFW service, advertises host capabilities, handles firmware memory requests, downloads board/regdb/calibration/M3 data, requests target capabilities/device info, starts/stops firmware modes, processes cold-boot calibration, and drives firmware-ready/recovery events through an ordered workqueue.

Important APIs, types, and functions: The first half of the file defines `qmi_elem_info` tables for host capability, indication registration, memory request/response, target capability, device info, BDF download, M3 info, WLAN mode/config/INI, and indications. `ath11k_qmi_host_cap_send()` advertises memory mode, BDF support, M3 support, calibration status, sleep clock, global reset, and PME D3cold capability. `ath11k_qmi_fw_ind_register_send()` subscribes to WLFW indications. Memory helpers allocate/free/assign target memory chunks for DMA or fixed DT/reserved-memory modes and respond to firmware. `ath11k_qmi_request_target_cap()` fills chip/board/SOC/firmware/eeprom info. `ath11k_qmi_load_bdf_qmi()` and `ath11k_qmi_load_file_target_mem()` download regdb/BDF/cal/eeprom data. `ath11k_qmi_wlanfw_m3_info_send()`, `ath11k_qmi_firmware_start()`, and `ath11k_qmi_firmware_stop()` control firmware boot mode. `ath11k_qmi_driver_event_work()` serializes events.

Control flow: `ath11k_qmi_init_service()` initializes the QMI handle, ordered event workqueue, event list, and service lookup. When a WLFW server appears, `ath11k_qmi_ops_new_server()` connects the QRTR socket and posts SERVER_ARRIVE; the worker registers indications and sends host capabilities, and for fixed firmware-memory targets immediately loads BDF. For dynamic memory targets, firmware sends REQUEST_MEM; the callback stores segment requirements, allocates/assigns memory, and posts REQUEST_MEM; the worker responds with addresses. FW_MEM_READY then triggers capability/device-info request, regdb/BDF/cal download, and M3 info. FW_INIT_DONE or FW_READY clears recovery flags and calls `ath11k_core_qmi_firmware_ready()`, or runs cold-boot calibration first. Firmware stop sends WLAN mode OFF. Server exit marks crash flush/recovery and starts pre-reconfigure recovery if not already resetting.

State and persistence behavior: Runtime state lives in `ab->qmi`: QMI handle/socket address, ordered workqueue and event list, CE config copied from hardware params, target memory chunks, target info, memory mode/delayed flag, calibration done flag, M3 DMA buffer, service instance ID, and cold-boot waitqueue. Target memory may be reused across firmware reloads when size/type match; otherwise it is freed/reallocated or deliberately delayed to request smaller chunks. Fixed memory paths ioremap reserved regions or fixed BDF/caldb addresses. No persistent storage is written, but firmware files are read from the firmware filesystem and calibration may be fetched from cal files or EEPROM.

Dependencies and integration points: Depends on Linux QMI/QRTR, firmware loader, ELF magic detection, DMA coherent allocation, DT reserved memory/ioremap, workqueues, wait queues, ath11k core firmware/BDF helpers, HIF power control, hardware params, CE/service maps, MHI/PCI memory mapping through device info, and recovery flags. It is the major boot-time bridge between PCI/MHI transport readiness and core/mac80211 registration.

Risks and edge cases: QMI message schemas are offset/length sensitive; malformed element tables break interop silently. Memory request length is warned but still assigned to `mem_seg_count`, so bounds handling must be scrutinized. Delayed memory negotiation intentionally sends an empty/failing response for large contiguous requests; this relies on firmware retrying with smaller segments. Fixed memory assignment depends on DT reserved memory size/order and CALDB/BDF address conventions. BDF download has different semantics for fixed-address and EEPROM modes, and `total_size` is set to remaining segment size rather than original full size. Event work exits early on unregistering and may leave queued events freed only up to that point. Cold-boot calibration can delay boot up to 60 seconds and may power-cycle firmware after success.

Test signals: Build with QMI, OF reserved memory, PCI/MHI, and firmware split/combined images. Runtime tests should cover server arrive/exit, indication registration failure, host-cap fields for sleep clock/global reset/M3, dynamic memory request large-chunk retry and small-chunk success, fixed memory DT assignment, target capability parsing, hybrid bus device info ioremap, regdb+BDF+caldata download, EEPROM caldata mode, fixed BDF address mode, missing caldata in FTM vs normal mode, M3 load from firmware-N.bin and legacy `m3.bin`, firmware start/stop, FW_READY and FW_INIT_DONE paths, cold-boot calibration timeout/restart, recovery server exit, and deinit while events are queued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/qmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/qmi.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/qmi.h

Purpose: Defines ath11k's QMI/WLFW protocol structures, constants, runtime QMI state, memory chunk descriptors, target capability storage, and public QMI service APIs. It is the schema contract used by `qmi.c` and by core/PCI code that starts, stops, and tears down firmware.

Important APIs, types, and constants: Constants define WLFW service IDs/versions/instances, timeouts, max response/build/file lengths, indication IDs, max memory segments, calibration/BDF sizes, cold-boot delay, and device BAR size. Enumerations cover QMI file type, BDF type, and internal driver event types. `struct ath11k_qmi` owns QMI handle/socket, event workqueue/list/lock, CE config, target memory array, memory mode/delayed flag, calibration state, target info, M3 memory, service instance, and cold-boot waitqueue. Wire structs describe host capability, indication register, memory request/response, target capability, device info, BDF download, M3 info, WLAN mode/config/INI, and placeholder indications. Public functions are `ath11k_qmi_init_service()`, `ath11k_qmi_deinit_service()`, `ath11k_qmi_free_resource()`, `ath11k_qmi_firmware_start()`, `ath11k_qmi_firmware_stop()`, and `ath11k_qmi_fwreset_from_cold_boot()`.

Control flow: PCI/core code initializes `ab->qmi.ce_cfg` and service instance, then calls `ath11k_qmi_init_service()` to start looking for WLFW. QMI event handlers fill the runtime structs declared here and drive boot sequencing. Firmware start uses WLAN config/mode request structures; stop uses mode OFF. Deinit/free-resource paths free target memory and M3 memory represented by the header types.

State and persistence behavior: `struct target_mem_chunk` stores requested size/type, previous size/type for reuse, physical address, and either DMA virtual, IO remap, or generic address pointer. `struct target_info` caches chip family, board ID, SOC ID, firmware version/build strings, BDF extension, and EEPROM calibration support. `struct ath11k_qmi` persists for the device lifetime but is reset on service init/deinit. No durable state is stored in this header.

Dependencies and integration points: Depends on Linux mutex/QMI headers, ath11k base, CE pipe/service map types, firmware memory conventions, QRTR service discovery, and hardware params. It integrates with PCI/MHI boot, core firmware loading, recovery, coredump memory segment collection, and calibration flows.

Risks and edge cases: Wire-structure field order and max lengths must stay synchronized with `qmi_elem_info` arrays in `qmi.c` and firmware WLFW definitions. `ATH11K_QMI_WLANFW_MAX_NUM_MEM_SEG_V01` sizes a fixed array; any firmware indication with a larger length must be rejected before writes. Event enum values must remain aligned with worker switch handling. Union address fields require callers to choose the correct free/unmap path based on memory mode. Service instance IDs differ by hardware and must be configured before lookup.

Test signals: Compile schema users after changing any struct, run QMI boot against all supported service instances, fuzz/validate memory segment counts and variable-array lengths, verify target capability string truncation, test fixed and DMA memory chunk lifecycle, and run firmware start/stop/deinit/recovery paths under KASAN/lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/qmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/reg.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/reg.c

Purpose: Implements ath11k regulatory-domain handling. It translates firmware WMI regulatory channel-list events into cfg80211 regdomains, applies/intersects them, handles user country-code requests, updates firmware scan channel lists after regulatory changes, supports 6 GHz AP/client rule selection, and manages regulatory memory cleanup.

Important APIs, types, and functions: `ath11k_reg_init()` configures the wiphy as self-managed and installs `ath11k_reg_notifier()`. The notifier processes driver-initiated regd updates and user country hints, sending either current-country or init-country WMI commands and stopping 11d scans. `ath11k_reg_update_chan_list()` builds a `scan_chan_list_params` from enabled cfg80211 channels and either sends it immediately or queues work. `ath11k_regd_update()` chooses latest/default/world regdomain and calls `regulatory_set_wiphy_regd()`. Mapping helpers translate firmware DFS/regulatory/PHY flags to nl80211 flags. `ath11k_reg_build_regd()` builds a regdomain from `cur_regulatory_info`, including 2/5/6 GHz rules, PSD, AUTO_BW, HE-disable flags, ETSI weather radar splits, and optional intersection with default regd. `ath11k_reg_handle_chan_list()` owns WMI event processing. Cleanup is via `ath11k_reg_reset_info()` and `ath11k_reg_free()`.

Control flow: Firmware sends a regulatory channel-list event decoded into `cur_regulatory_info`; `ath11k_reg_handle_chan_list()` validates status/pdev, skips duplicate default updates, decides whether to intersect with the default regdomain, determines current vdev type, builds a regdomain, stores it as default or new regd under `base_lock`, and queues `regd_update_work` for already-registered pdevs. The work calls `ath11k_regd_update()`, which copies the selected regdomain and passes it to cfg80211. User regulatory requests go through the notifier: driver-initiated requests update the firmware channel list; user hints optionally send country code to firmware and mark `regdom_set_by_user`. Channel-list update work waits for 11d and hardware scans to complete before sending WMI scan channel lists.

State and persistence behavior: State is volatile in `ab->default_regd[]`, `ab->new_regd[]`, `ab->reg_info_store[]`, `ab->dfs_region`, `ar->alpha2`, `ar->regdom_set_by_user`, channel update queues, scan/11d completions, and wiphy regulatory state. `default_regd` is retained for intersection; `new_regd` is replaced on country changes. `reg_info_store` owns dynamically allocated rule arrays and must be reset before overwrite/free. No disk persistence exists.

Dependencies and integration points: Depends on cfg80211/mac80211 regulatory APIs, rtnetlink RCU access, WMI regulatory and scan-channel commands, ath11k MAC 11d scan helpers, workqueues, spinlocks, completions, and hardware params for 6 GHz regulatory support. It integrates firmware's regulatory model with Linux self-managed wiphys and userspace regulatory hints.

Risks and edge cases: Regulatory correctness is safety/compliance sensitive. Rule counts and array pointers from firmware must be consistent; allocation uses `GFP_ATOMIC`. ETSI weather-radar splitting mutates the loop index and depends on extra reserved rule slots. Intersection with `default_regd` assumes it exists and has sane rules. The code falls back with `WARN_ON(1)` but does not fully revert firmware when host processing fails. The first active vif decides vdev type for regdomain selection, which is explicitly not concurrency-complete. Queued channel updates can wait on scans and time out, leaving firmware/host channel lists temporarily inconsistent.

Test signals: Regulatory tests should cover default world fallback, firmware default regd, user country change with and without dynamic hints, current-country vs init-country command paths, duplicate default event suppression, pdev out-of-range/single-pdev fallback, 2/5/6 GHz AP and STA rule construction for LPI/SP/VLP, PSD flags, HE-disable phybitmap, AUTO_BW flags, ETSI DFS weather radar split, default/current intersection, regdomain memory cleanup under KASAN, queued channel-list updates during 11d/hardware scans, and cfg80211 visible channel flags after update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/reg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/reg.h

Purpose: Declares the ath11k regulatory API and firmware DFS-region/PHY-flag constants used to translate WMI regulatory information into Linux cfg80211 regdomains and firmware scan-channel lists.

Important APIs, types, and constants: `enum ath11k_dfs_region` maps firmware DFS domains such as FCC, ETSI, MKK, CN, KR, and undefined values. `ATH11K_REG_PHY_BITMAP_NO11AX` is a firmware PHY bitmap flag that maps to `NL80211_RRF_NO_HE`. Public functions initialize/free regulatory state, reset decoded regulatory info, handle regdomain and channel-list work, build regdomains, update cfg80211 regd, update firmware scan channel lists, convert 6 GHz AP power type, handle WMI channel-list events, and send country code updates.

Control flow: Core/MAC setup calls `ath11k_reg_init()` during wiphy registration. WMI event handling calls `ath11k_reg_handle_chan_list()` with decoded firmware regulatory info. Workqueue callbacks declared here apply cfg80211 updates and firmware channel-list updates. User regulatory hints eventually call `ath11k_reg_set_cc()` through the notifier in `reg.c`.

State and persistence behavior: The header owns no state, but its APIs manipulate per-radio/per-base regulatory domains, stored WMI regulatory info, DFS region state, channel update queues, and wiphy regulatory settings. These are runtime-only and freed by `ath11k_reg_free()`.

Dependencies and integration points: Includes Linux kernel and cfg80211 regulatory headers and forward-declares ath11k core types. It integrates WMI regulatory event decoding with cfg80211, mac80211, 11d scan control, and firmware scan-channel programming.

Risks and edge cases: DFS-region mappings must match firmware semantics and country compliance requirements. `ath11k_reg_build_regd()` callers must pass a valid `cur_regulatory_info` with owned rule arrays and a valid AP power/vdev type for 6 GHz rules. Workqueue callbacks must only be scheduled while the owning `ath11k` remains alive.

Test signals: Compile users after changing function signatures or enum values. Runtime validation should cover DFS region mapping, 6 GHz AP power conversion, country-code set, regulatory event handling, channel-list update work, and regulatory cleanup during device removal/recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/reg.h -->
