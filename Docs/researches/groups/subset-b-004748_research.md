# Research: subset-b-004748

Grouped research for ath12k MAC, PCI/MHI/QMI, peer, P2P, and regulatory files. Each section preserves the source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/mac.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/mac.h

## Purpose

`mac.h` is the public contract for ath12k's mac80211 integration layer. It does not implement behavior itself; it centralizes constants, small data structures, and declarations used by the driver to expose radios, links, virtual interfaces, peers, scan state, management TX, regulatory TPC, MLO, and mac80211 callbacks.

## Important APIs, Types, And Constants

- `struct ath12k_generic_iter` and `struct ath12k_mac_get_any_chanctx_conf_arg` are iterator payloads used when walking mac80211 objects.
- `enum ath12k_supported_bw`, `enum ath12k_gi`, and `enum ath12k_ltf` translate firmware rate concepts into cfg80211/mac80211 rate reporting.
- `struct ath12k_chan_power_info` and `struct ath12k_reg_tpc_power_info` model 6 GHz transmit power/TPE data that regulatory and MAC code later converts into firmware commands.
- Constants such as `ATH12K_KEEPALIVE_*`, `ATH12K_KICKOUT_THRESHOLD`, `ATH12K_SCAN_LINKS_MASK`, `ATH12K_NUM_MAX_ACTIVE_LINKS_PER_DEVICE`, and OBSS PD thresholds encode policy shared across interface, station, scan, and power code.
- Declarations cover the whole mac80211 operations surface: start/stop, add/remove interface, channel context operations, key install, STA state and link changes, AMPDU, survey, flush, remain-on-channel, TX power, management TX, and MLO multicast address handling.

## Control Flow And Integration

The file sits above lower layers. mac80211 invokes `ath12k_mac_op_*` callbacks registered by the MAC implementation; those functions call WMI, DP, peer, regulatory, PCI/HIF, and firmware-stat helpers. Driver-internal users call lookup helpers such as `ath12k_mac_get_arvif_by_vdev_id()`, `ath12k_mac_get_ar_by_vdev_id()`, and `ath12k_get_ar_by_vif()` to bind firmware vdev or link identifiers back to host objects. Regulatory code uses `ath12k_mac_update_freq_range()` and `ath12k_mac_fill_reg_tpc_info()`. P2P code exposes `ath12k_mac_add_p2p_noa_ie()` for beacon/probe-response updates.

## State And Persistence

No storage is allocated here, but the header defines shared state shapes and invariants. Link IDs distinguish default, invalid, and scan-only links. TPC structures retain per-channel power calculations in memory for later firmware programming. Many declared callbacks assume caller-held mac80211 wiphy locks, per-radio locks, or ath12k data locks in their implementations.

## Dependencies

It depends on `net/mac80211.h`, `net/cfg80211.h`, and ath12k `wmi.h`. The declarations reference core driver types (`ath12k`, `ath12k_base`, `ath12k_hw`, `ath12k_hw_group`), Linux networking types (`ieee80211_hw`, `ieee80211_vif`, `ieee80211_sta`, channel contexts), and firmware/WMI types.

## Risks And Test Signals

This is a high-blast-radius header: signature drift breaks many compilation units. Link/MLO constants must stay aligned with mac80211 limits and firmware assumptions. TPC array sizing assumes at most sixteen 20 MHz chunks for 320 MHz channels. Test signals are mainly build coverage plus runtime mac80211 smoke tests for interface creation, scanning, STA association, MLO link activation, management TX, and regulatory power updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/mhi.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/mhi.c

## Purpose

`mhi.c` adapts ath12k PCI devices to the Linux MHI bus. It registers an `mhi_controller`, supplies firmware image information, binds MSI vectors, drives the MHI power-state machine, handles firmware crash/RDDM callbacks, and exposes helpers used by PCI reset and coredump code.

## Important APIs And Functions

- `ath12k_mhi_register()` allocates and initializes `struct mhi_controller`, selects dual-MAC or normal AMSS firmware from `firmware-N.bin` or the legacy `mhi.bin` path, assigns MSI IRQs, sets DMA/iova limits and callbacks, then calls `mhi_register_controller()`.
- `ath12k_mhi_unregister()` releases the controller, allocated IRQ array, and ath12k pointer.
- `ath12k_mhi_start()` transitions through `ATH12K_MHI_INIT` and `ATH12K_MHI_POWER_ON`; `ath12k_mhi_stop()` powers down, optionally with `mhi_power_down_keep_dev()` during suspend, then deinitializes.
- `ath12k_mhi_suspend()` and `ath12k_mhi_resume()` call MHI PM suspend/resume through the same guarded state helper.
- `ath12k_mhi_set_mhictrl_reset()` and `ath12k_mhi_clear_vector()` reset MHI/PCI vector registers after global reset or before rebooting firmware.
- `ath12k_mhi_coredump()` delegates RDDM image download to the MHI core.

## Control Flow

PCI probe calls `ath12k_mhi_register()` after MSI allocation and before HAL/CE setup. PCI power-up later calls `ath12k_mhi_start()`, which uses `mhi_prepare_for_power_up()` followed by synchronous MHI power-up so QRTR channels are ready before resume paths continue. Power-down reverses this by calling MHI power down and unprepare. MHI status callbacks translate MHI events into ath12k recovery behavior: `MHI_CB_EE_RDDM` sets crash/recovery flags and queues `reset_work`, while consecutive RDDM callbacks are suppressed by `mhi_pre_cb`.

## State And Persistence

State is stored in `ath12k_pci::mhi_ctrl`, `mhi_state`, `mhi_pre_cb`, and firmware buffer/path fields. `ath12k_mhi_set_state_bit()` records coarse state bits for init, power-on, suspend, trigger-RDDM, and RDDM-done; `ath12k_mhi_check_state_bit()` prevents invalid transitions and logs current bit state. Firmware buffers are owned by ath12k core firmware mappings or by the MHI firmware image path.

## Dependencies And Integration

The file depends on Linux MHI, PCI/MSI, firmware, IRQ, and bit helpers. It integrates tightly with `pci.c` for register access and MSI assignment, `core.h` for firmware blobs and recovery flags, and `debug.h` for diagnostics. It relies on hardware parameters for MHI config, RDDM size, OTP board-id register, and firmware layout.

## Risks And Test Signals

Risks include incorrect MHI state transitions, missing IRQ cleanup on register failure, firmware selection mismatches for dual-MAC board IDs, and recovery storms if RDDM callbacks repeat. Suspend uses a keep-device workaround because normal power-down can break resume. Test signals include PCI probe/tear-down, firmware boot to mission mode, suspend/resume, forced firmware crash with RDDM collection, one-vector and multi-vector MSI configurations, and fallback loading from legacy `mhi.bin`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/mhi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/mhi.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/mhi.h

## Purpose

`mhi.h` is the shared MHI interface for the PCI-backed ath12k bus. It defines the register offsets used by reset/vector cleanup, the driver-local MHI state enum, and the exported lifecycle helpers implemented in `mhi.c`.

## Important APIs And Types

- Register constants `PCIE_TXVECDB`, `PCIE_TXVECSTATUS`, `PCIE_RXVECDB`, and `PCIE_RXVECSTATUS` identify vector doorbell/status registers cleared during PCI reset.
- `MHISTATUS`, `MHICTRL`, and `MHICTRL_RESET_MASK` support clearing SYSERR-like MHI controller state after SoC global reset.
- `enum ath12k_mhi_state` enumerates driver-requested transitions: init/deinit, power on/off, keep-device power off, forced power off, suspend/resume, trigger RDDM, RDDM, and RDDM done.
- Public functions include register/unregister, start/stop, suspend/resume, vector clearing, reset-bit setting, and coredump download.

## Control Flow And Integration

`pci.c` includes this header to call `ath12k_mhi_register()` during probe, `ath12k_mhi_start()` during power-up, `ath12k_mhi_stop()` during power-down, and suspend/resume wrappers in HIF PM callbacks. Reset paths call `ath12k_mhi_clear_vector()` and `ath12k_mhi_set_mhictrl_reset()` around PCI global reset. Coredump code calls `ath12k_mhi_coredump()` to enter/download RDDM.

## State And Persistence

The header does not allocate state, but its enum values are used as bit positions in `ath12k_pci::mhi_state`. That means enum ordering is semantically important. The declared functions mutate PCI registers, MHI core state, and ath12k recovery state through `struct ath12k_pci` and `struct ath12k_base`.

## Dependencies, Risks, And Test Signals

It includes `pci.h`, so users get `struct ath12k_pci` and `struct ath12k_base` definitions. Risks are mostly ABI-like: changing enum order can corrupt bit-state checks, and changing register constants can break reset recovery. Test signals are successful build across PCI and MHI units plus runtime boot, suspend/resume, reset, and crash-dump tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/mhi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/p2p.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/p2p.c

## Purpose

`p2p.c` maintains Wi-Fi Direct Notice of Absence (NOA) information for AP/P2P GO interfaces. Firmware reports NOA state through WMI; this code converts it into a vendor-specific P2P IE and stores it on the ath12k vif so beacon and probe-response generation can include current absence scheduling.

## Important Functions

- `ath12k_p2p_noa_ie_len_compute()` decides whether a NOA IE is needed and computes its exact length from descriptor count and opportunistic power-save bits.
- `ath12k_p2p_noa_ie_fill()` writes the vendor IE header, WFA OUI/type, NOA attribute, index, OPPPS/CTWindow, and descriptor array.
- `ath12k_p2p_noa_ie_assign()` frees the previous `ahvif->u.ap.noa_data` and installs a new pointer/length under `ar->data_lock`.
- `ath12k_p2p_noa_update()` is the direct exported updater for a known link vif.
- `ath12k_p2p_noa_update_by_vdev_id()` iterates active mac80211 interfaces atomically and updates the default link matching the radio and firmware `vdev_id`.

## Control Flow

The update path clears any old IE first, computes whether firmware state is non-empty, allocates with `GFP_ATOMIC` while under a bottom-half spinlock, fills the IE, and assigns it. The vdev-id path builds `struct ath12k_p2p_noa_arg`, walks active interfaces with `ieee80211_iterate_active_interfaces_atomic()`, checks `is_created`, radio pointer, and vdev ID, then calls the locked updater.

## State And Persistence

NOA state is transient in memory: `ahvif->u.ap.noa_data` and `noa_len`. The old allocation is always freed before storing new state or clearing. There is no disk persistence. The data remains until the next WMI NOA update, interface removal cleanup, or explicit zero-length update.

## Dependencies And Integration

The file depends on mac80211 P2P IE structures, WMI NOA bit definitions, `core.h`, `mac.h`, and `p2p.h`. It feeds `ath12k_mac_add_p2p_noa_ie()`, which attaches the cached IE to outgoing beacon/probe-response SKBs.

## Risks And Test Signals

The code trusts firmware descriptor count to fit the destination `ieee80211_p2p_noa_attr::desc[]`; malformed or future firmware counts are a bounds risk unless upstream struct sizing and WMI validation constrain them. Allocation failure silently drops the IE. Test signals include P2P GO operation with NOA/OPPPS changes, beacon/probe-response capture verifying vendor IE encoding, interface iteration under RCU, and lockdep coverage for `ar->data_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/p2p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/p2p.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/p2p.h

## Purpose

`p2p.h` declares the minimal P2P NOA update API used by WMI/event code and MAC management-frame generation. It keeps P2P-specific details out of broader MAC headers except where cached NOA IEs are appended.

## Important APIs And Types

- `struct ath12k_p2p_noa_arg` is the iterator payload for vdev-based NOA updates. It carries the target `vdev_id`, `struct ath12k *ar`, and firmware `struct ath12k_wmi_p2p_noa_info *`.
- `ath12k_p2p_noa_update()` updates a known `struct ath12k_link_vif`.
- `ath12k_p2p_noa_update_by_vdev_id()` resolves an update by firmware vdev ID through active mac80211 interface iteration.

## Control Flow, State, And Integration

The header exposes functions implemented in `p2p.c`. Callers usually receive WMI P2P NOA data, then either already know the link vif or only know a firmware vdev ID. The implementation updates `ath12k_vif` AP state under the radio data lock and later MAC code appends cached data to management frames.

## Dependencies, Risks, And Test Signals

It includes `wmi.h` for the firmware NOA type and relies on ath12k core type declarations from including contexts. API risk is low, but signature changes affect WMI event consumers and management TX paths. Test signals are build coverage and P2P GO NOA updates producing expected beacon/probe-response IEs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/p2p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/pci.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/pci.c

## Purpose

`pci.c` is the HIF/bus implementation for PCI ath12k devices. It claims and maps BAR0, manages register windowing, allocates MSI vectors, configures CE and DP interrupts, initializes QMI CE configuration, powers firmware through MHI, handles reset and coredump paths, implements probe/remove/shutdown/PM callbacks, and exposes registration for device-family-specific PCI drivers.

## Important APIs And Functions

- Register access: `ath12k_pci_read32()` and `ath12k_pci_write32()` handle low BAR offsets, dynamic/static window selection, MHI region special casing, optional wake/release callbacks, and export read access.
- IRQ setup: `ath12k_pci_msi_alloc()`, `ath12k_pci_get_user_msi_assignment()`, `ath12k_pci_config_irq()`, CE IRQ handlers/workqueues, DP ext IRQ handlers, and NAPI polling bridge MSI vectors to CE and datapath rings.
- Power/reset: `ath12k_pci_sw_reset()`, `ath12k_pci_soc_global_reset()`, `ath12k_pci_power_up()`, and `ath12k_pci_power_down()` sequence LTSSM, interrupt clear, vector clear, debug register clear, MHI reset, ASPM, MSI, QRTR node ID, and MHI state.
- HIF ops: `ath12k_pci_hif_ops` wires start/stop/read/write/power/PM/IRQ/MSI/service-to-pipe/coredump callbacks into core.
- Probe/remove: `ath12k_pci_probe()` allocates core state, claims PCI resources, discovers device-family ops, allocates MSI, pre-inits core, registers MHI, initializes HAL SRNG/CE/IRQs, runs arch init, then starts ath12k core. `ath12k_pci_remove()` unwinds QMI/core/MHI/IRQ/MSI/BAR/HAL/CE resources.
- Device-family module API: `ath12k_pci_register_driver()` and `ath12k_pci_unregister_driver()` maintain the family driver table and register a real `pci_driver`.

## Control Flow

Probe is linear with labeled error unwinds. After resources are claimed, MHI is registered before HAL/CE IRQs, because firmware boot later depends on MHI. Core power-up calls HIF `power_up`, which resets hardware, disables ASPM for firmware download, enables MSI, writes a unique QRTR node when needed, starts MHI synchronously, and optionally selects static windows. Runtime `start` marks init done, restores ASPM for multi-vector devices, enables CE IRQs, and posts RX buffers. Interrupt flow disables the IRQ source, services CE in a bottom-half workqueue or DP rings through NAPI, then re-enables interrupts after work completes.

## State And Persistence

State lives in `struct ath12k_pci`: PCI device, BAR/register window cache, MSI base data and flags, MHI controller, qmi instance, DMA mask, ASPM link control backup, family ops, and register bases. Device flags track CE/DP IRQ enable and init state. There is no disk persistence, but coredump code assembles a vmalloc crash artifact from MHI FBC/RDDM images and QMI target memory, then queues devcoredump work.

## Dependencies And Integration

The file depends on Linux PCI/MSI/IRQ/NAPI/PM/vmalloc APIs and ath12k core, HIF, MHI, HAL, CE, DP, QMI, and debug infrastructure. It is the integration point between generic ath12k core and family-specific PCI modules such as QCN9274/WCN7850.

## Risks And Test Signals

Risks include BAR window races, incorrect MSI fallback behavior, IRQ leaks on partial probe failure, ASPM/MHI resume interactions, reset timing uncertainty, QRTR instance collisions on multi-device systems, and coredump size/copy errors. Test signals include module probe/remove under every supported family, one-MSI and multi-MSI operation, CE/DP traffic under NAPI, suspend/resume, firmware recovery, devcoredump generation, service-to-pipe mapping, register access across static/dynamic windows, and fault-injection of each probe error label.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/pci.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/pci.h

## Purpose

`pci.h` defines the PCI bus contract and shared data structures for ath12k. It collects hardware register offsets, MSI configuration types, PCI state flags, device-family callbacks, the private `struct ath12k_pci`, and the HIF-facing helper declarations implemented in `pci.c`.

## Important APIs, Types, And Constants

- Register constants cover SoC global reset, WLAON/Q6 cookie and reset-cause registers, wake handshakes, LTSSM/hot reset, interrupt clear, QSERDES/PCS oscillator config, QFPROM power/board ID, QRTR node ID, BAR window ranges, and MHI register ranges.
- `struct ath12k_msi_user` and `struct ath12k_msi_config` partition MSI vectors among MHI, CE, WAKE, and DP users.
- `enum ath12k_pci_flags` tracks init done, 64-bit MSI, ASPM restore, and multi-vector MSI mode.
- `struct ath12k_pci_ops` provides optional wake/release hooks for register access.
- `struct ath12k_pci_device_family_ops` and `struct ath12k_pci_driver` allow chip-family modules to provide probe/arch init/deinit, ID tables, and register bases while sharing common PCI logic.
- `struct ath12k_pci` stores PCI, MHI, MSI, window, ASPM, QMI instance, DMA, and family-specific state.

## Control Flow And Integration

Family modules register with `ath12k_pci_register_driver()`. Generic PCI probe allocates `struct ath12k_base` with this private state and fills HIF ops. MHI uses MSI helpers declared here. QMI CE setup uses service-to-pipe and MSI metadata. Core HIF calls use the declared start/stop/power/IRQ/read/write functions.

## State And Persistence

The header defines in-memory driver state only. `register_window` is protected by `window_lock`; `mhi_state` is a bitset using values from `mhi.h`; `flags` stores `enum ath12k_pci_flags`; `link_ctl` preserves ASPM state for restoration. No persistent storage is involved.

## Dependencies, Risks, And Test Signals

It depends on Linux MHI/PCI and `core.h`. Register constants and masks are hardware ABI: wrong values can break boot or reset. Struct layout is internal but broad; changes must be synchronized with family drivers and MHI/QMI code. Test signals include compile coverage of all family modules, PCI probe/power/IRQ paths, and register access on chips with different `reg_base` and static-window settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/peer.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/peer.c

## Purpose

`peer.c` manages firmware and datapath peer lifecycle for ath12k stations and vdevs. It coordinates WMI peer create/delete commands, waits for DP peer map/unmap events, updates per-radio peer counts, fills MLO peer metadata, deletes all link peers for MLO stations, and maintains a reverse-address hash table for link station lookup.

## Important APIs And Functions

- `ath12k_peer_create()` validates peer capacity and duplicate pdev/address state, sends WMI peer create, waits for DP map, fills `ath12k_dp_link_peer` fields, updates STA/MLO metadata, increments `ar->num_peers`, and assigns the peer to DP hardware.
- `ath12k_peer_delete()` unassigns DP mapping, sends WMI delete, waits for DP unmap and `peer_delete_done`, then decrements peer count.
- `ath12k_peer_cleanup()` removes stale DP peers for a vdev under `dp_lock`.
- `ath12k_peer_mlo_link_peers_delete()` sends delete for all MLO link peers before waiting for all responses, matching firmware expectations.
- `ath12k_peer_ml_alloc()` allocates an MLO peer ID from a bitmap.
- `ath12k_link_sta_rhash_*()` initializes, inserts, deletes, destroys, and looks up `ath12k_link_sta` by MAC address.

## Control Flow

Map/unmap waits use `ath12k_wait_for_dp_link_peer_common()`, which sleeps on `ab->peer_mapping_wq` while checking the DP peer list under `dp_lock`, and exits early if crash flush is set. Create sends WMI first, waits for map, then rechecks the DP peer object; if missing after a successful wait, it attempts cleanup by sending delete and waiting for delete completion. Delete reinitializes completion before sending WMI and waits for both DP and firmware completion signals.

## State And Persistence

Persistent driver state is in memory: DP peer list, peer fields (`pdev_idx`, `sta`, link ID, ML ID, ML address, primary-link flag, MLO flag), `ar->num_peers`, `ah->free_ml_peer_id_map`, and `ab->rhead_sta_addr`. There is no disk persistence. Peer state is synchronized by wiphy lock, `dp_lock`, and `base_lock` depending on operation.

## Dependencies And Integration

The file depends on ath12k core, DP peer helpers, WMI peer commands, debugfs, rhashtable, completions, and mac80211 STA/VIF objects. MAC station-state code calls peer create/delete, DP event handling wakes waits, and MLO link management depends on all-link delete ordering.

## Risks And Test Signals

Risks include timeouts when firmware/DP map events are lost, peer count imbalance on partial create/delete failures, MLO delete ordering regressions, duplicate-peer races if locks are not held, and stale rhashtable entries. Test signals include association/disassociation loops, AP and STA peer churn, MLO association/deletion across multiple links, firmware crash during peer operations, peer table exhaustion, lockdep, and rhashtable duplicate/remove fault cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/peer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/peer.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/peer.h

## Purpose

`peer.h` declares ath12k peer lifecycle and link-station lookup APIs used by MAC, DP, and MLO code. It is the compact interface to the implementation in `peer.c`.

## Important APIs

- `ath12k_peer_create()`, `ath12k_peer_delete()`, and `ath12k_peer_cleanup()` manage firmware and DP peer objects for one vdev.
- `ath12k_wait_for_peer_delete_done()` exposes the wait path when callers send deletes separately.
- `ath12k_peer_mlo_link_peers_delete()` deletes all link peers belonging to an MLO station.
- `ath12k_peer_ml_alloc()` allocates a multi-link peer ID.
- `ath12k_link_sta_rhash_tbl_init()`, `destroy()`, `add()`, `delete()`, and `find_by_addr()` manage the address-indexed `ath12k_link_sta` table.
- `ath12k_peer_ml_find()` is declared for multi-link peer lookup by address.

## Control Flow, State, And Integration

Callers are expected to hold the appropriate mac80211 wiphy or base lock depending on operation. The implementation mutates DP peer lists, per-radio peer counters, MLO peer ID bitmaps, and rhashtable state. MAC station-state transitions and MLO link changes are primary consumers.

## Risks And Test Signals

The header's risks are contract drift: changing prototypes affects peer lifecycle across MAC/DP. Locking expectations are not encoded in types, so implementation lockdep assertions are the main guard. Test signals include build coverage, station create/delete, MLO link peer deletion, and address lookup under concurrent association churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/peer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/qmi.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/qmi.c

## Purpose

`qmi.c` implements the ath12k WLAN firmware QMI control plane. It defines QMI element-info schemas for WLFW messages, discovers firmware service arrival, advertises host/MLO capabilities, responds to firmware memory requests, downloads board/regdb/calibration data, supplies M3 and auxiliary microcode memory, starts/stops WLAN firmware mode, and processes asynchronous firmware-ready events through an ordered workqueue.

## Important APIs And Functions

- QMI schema tables (`qmi_wlanfw_*_ei`) define the wire encoding for host capability, PHY capability, indication registration, memory request/response, target capability, BDF download, M3/AUX info, WLAN config/mode/INI, and firmware-ready indications.
- `ath12k_qmi_init_service()` initializes the QMI handle, event list/lock/workqueue, and QRTR lookup for `service_ins_id`; `ath12k_qmi_deinit_service()` releases QMI and allocated firmware memory.
- `ath12k_qmi_event_server_arrive()` requests PHY capability, registers indications, blocks host-cap event processing until all devices in the hardware group are ready, then triggers host cap.
- `ath12k_qmi_host_cap_send()` sends host memory mode, BDF/M3/calibration support, feature bitmap, internal sleep clock flags, and MLO chip/link metadata.
- `ath12k_qmi_msg_mem_request_cb()` parses firmware memory requests, allocates or maps target memory, then posts `REQUEST_MEM`; `ath12k_qmi_respond_fw_mem_request()` replies with physical addresses.
- `ath12k_qmi_event_load_bdf()` requests target capabilities, downloads regdb and board data, optional calibration, M3, and optional AUX microcode.
- `ath12k_qmi_firmware_start()` sends WLAN INI, CE/service/shadow register config, then mode; `ath12k_qmi_firmware_stop()` sends mode off.

## Control Flow

QMI callbacks are thin and asynchronous: QRTR new-server and firmware indications post `ath12k_qmi_driver_event` entries to an ordered workqueue. The workqueue ignores events during unregistering and otherwise dispatches server arrival, memory request, firmware-memory-ready, firmware-ready, and host-cap events. Firmware boot sequencing is therefore: service arrival, PHY cap, indication registration, grouped host-cap gating, firmware memory request, host memory response, firmware memory ready, target-cap/BDF/regdb/cal/M3/AUX download, firmware ready, and finally `ath12k_core_qmi_firmware_ready()`.

## State And Persistence

All state is in memory under `struct ath12k_qmi`: QRTR socket address, event queue, CE config, target memory chunks, target info, M3/AUX buffers, memory mode, calibration done, service instance, and device memory descriptors. MLO global memory is shared through `ath12k_hw_group::mlo_mem` under the group mutex and can be reset when no devices are started. DMA allocations are reused across recovery/resume when sizes match; fixed memory regions are ioremapped reserved memory.

## Dependencies And Integration

The file depends on Linux QMI/QRTR, firmware loader, DMA coherent memory, reserved memory/OF/ACPI/SMBIOS helpers, ELF detection, workqueues, and ath12k core/HIF/QMI headers. PCI initializes QMI CE config and unique service instance. Core firmware startup waits on QMI events. Board/regdb/calibration download integrates with ath12k firmware APIs.

## Risks And Test Signals

Risks include QMI ABI table mismatches, firmware memory segment overflows, delayed allocation handling for large contiguous DMA requests, MLO host-cap gating deadlocks, service instance collisions, missing cleanup of event workqueue on init failure, and partial boot failures leaving QMI fail flags. Test signals include QMI boot on every chip family, fixed and dynamic memory modes, large-memory retry path, multi-device MLO boot, regdb/BDF/calibration fallback paths, M3/AUX loading from bundled and legacy files, firmware-ready recovery path, service deletion/crash handling, and deinit leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/qmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/qmi.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/qmi.h

## Purpose

`qmi.h` is the WLFW QMI ABI and state definition for ath12k. It defines message IDs, maximum payload sizes, firmware file types, memory-region types, event types, host capability structures, target capability structures, BDF/M3/AUX/WLAN config messages, and `struct ath12k_qmi`.

## Important APIs And Types

- Constants define WLFW service ID/version/instance IDs, response limits, timeout, data segment size, memory segment counts, BDF/caldb sizing, and firmware mode off.
- `enum ath12k_qmi_event_type` lists workqueue events for service arrival/exit, memory request, firmware memory ready, firmware ready, host cap, and legacy placeholders.
- `struct ath12k_qmi` stores QMI handle/socket, ordered event workqueue, event list/lock, CE config, target memory array, memory mode/delay flag, block-event flag, target info, M3/AUX memory, service instance, and device memory descriptors.
- QMI request/response structs mirror firmware ABI for host cap including MLO metadata, PHY cap, indication registration, memory request/response, target cap, BDF download, M3/AUX info, WLAN mode/config/INI.
- Inline helpers `ath12k_qmi_set_event_block()` and `ath12k_qmi_get_event_block()` enforce event-lock ownership.

## Control Flow And Integration

`qmi.c` uses these structures with `qmi_send_request()`, `qmi_txn_wait()`, and QMI indication decoding. PCI fills `ath12k_qmi_ce_cfg`; core calls init/deinit, firmware start/stop, resource free, host-cap trigger, and MLO memory reset. The structs are also used by firmware file loading, reserved-memory mapping, and multi-device MLO boot coordination.

## State And Persistence

The header defines state ownership. Target memory chunks may be DMA coherent allocations or fixed ioremaps; M3/AUX regions carry total and active sizes for reuse; target info caches firmware-reported chip, board, SoC, and build identifiers. State is transient and released during QMI deinit/resource free.

## Risks And Test Signals

Wire-ABI drift is the main risk: message IDs, max lengths, enum values, and struct fields must match firmware and QMI element tables in `qmi.c`. Array bounds such as max memory segments, MLO chips/links, and BDF data size are critical. Test signals include compile coverage, QMI transaction success across all request types, malformed/oversized indication handling, MLO boot, and firmware resource cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/qmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/reg.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/reg.c

## Purpose

`reg.c` converts firmware regulatory events into cfg80211 regdomains, handles user country hints, updates firmware scan channel lists, maintains per-band frequency ranges, and releases regulatory memory. It is the bridge between firmware WMI regulatory information and Linux regulatory/mac80211 state.

## Important APIs And Functions

- `ath12k_reg_init()` marks the wiphy self-managed and installs `ath12k_reg_notifier()`.
- `ath12k_reg_notifier()` handles driver-initiated and user-initiated regdomain changes, optionally sends WMI current/init country commands to every radio, stops 11d scans, and triggers firmware channel-list updates after driver regd changes.
- `ath12k_reg_update_chan_list()` builds `ath12k_wmi_scan_chan_list_arg` from enabled mac80211 channels within the radio frequency range and either sends it immediately or queues work.
- `ath12k_regd_update()` waits for firmware regulatory completion, updates per-radio frequency ranges, selects default/new firmware regdomain, copies it, and calls `regulatory_set_wiphy_regd()`.
- `ath12k_reg_build_regd()` combines 2 GHz, 5 GHz, and optional 6 GHz AP/client rules into an `ieee80211_regdomain`, maps DFS/NO_IR/radar/PHY/PSD flags, updates band frequency ranges, and splits ETSI weather radar rules to apply 10-minute CAC.
- `ath12k_reg_handle_chan_list()` stores default or new regdomains and queues update work after registration.
- `ath12k_reg_validate_reg_info()` drops, accepts, or falls back firmware regulatory events based on status and pdev index.
- `ath12k_reg_free()` frees stored reg info and regdomain pointers.

## Control Flow

Firmware WMI events are parsed elsewhere into `struct ath12k_reg_info`, validated, and passed to `ath12k_reg_handle_chan_list()`. Before MAC registration, generated regdomains are stored as defaults. After registration, new regdomains are stored and `regd_update_work` applies them asynchronously. User regulatory hints flow through the notifier, which sends country commands to firmware and marks the update as user-driven. Channel-list updates wait for 11d/hardware scans to complete before sending firmware scan channel lists.

## State And Persistence

State is in `ab->default_regd[]`, `ab->new_regd[]`, `ab->reg_info[]`, `ab->dfs_region`, `ab->reg_freq_2ghz/5ghz/6ghz`, `ah->regd_updated`, per-radio completions, and queued channel-list arguments. Regulatory domains are heap allocated and freed when replaced or during `ath12k_reg_free()`. No disk persistence exists.

## Dependencies And Integration

The file depends on cfg80211/regulatory APIs, rtnl/RCU access to wiphy regd, WMI country/channel commands, MAC scan state and frequency-range helpers, workqueues, spinlocks, mutexes, and firmware regulatory constants. It integrates with mac80211 self-managed regulatory behavior and with firmware scan/channel programming.

## Risks And Test Signals

Risks include incorrect 6 GHz AP/client rule selection, missed freeing of nested regulatory rule arrays, racey replacement of regdomains, timeouts waiting for firmware completion, channel lists becoming inconsistent during scans, and fallback behavior that is still TODO. Test signals include boot with default firmware regd, user country change, dynamic hints enabled/disabled, 2/5/6 GHz channel availability, ETSI weather radar CAC values, disabled channel filtering, 11d scan interaction, WMI channel-list contents, and cleanup leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/reg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/reg.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/reg.h

## Purpose

`reg.h` defines ath12k's regulatory data model and public regulatory APIs. It describes firmware-derived country/status values, regulatory rules, complete regulatory event information including 6 GHz AP/client matrices, PHY capability flags, validation status, and functions implemented in `reg.c`.

## Important APIs And Types

- Constants define regulatory update timeout and frequency boundaries separating 2 GHz and 5 GHz handling.
- `enum ath12k_dfs_region` maps firmware DFS domains; `enum ath12k_reg_cc_code` maps firmware country-setting status codes.
- `struct ath12k_reg_rule` is the compact firmware rule representation: start/end frequency, max bandwidth, power, antenna gain, flags, PSD state, and PSD EIRP.
- `struct ath12k_reg_info` owns parsed regulatory event state for one PHY, including 2/5 GHz rules, extended 6 GHz AP and client rules, bandwidth limits, domains, client type, AP usability flags, and PHY bitmap.
- `enum ath12k_reg_phy_bitmap` disables 11ax/11be when firmware marks them unavailable; `enum ath12k_reg_status` reports validate/drop/fallback.
- Function declarations cover init/free, regdomain building/updating, scan channel-list programming, reg-info reset/validation, event handling, and AP power conversion.

## Control Flow And Integration

WMI regulatory event parsers fill `ath12k_reg_info` and call validation/handling. `reg.c` builds cfg80211 `ieee80211_regdomain` objects from these structures, stores them on `ath12k_base`, and updates mac80211. MAC code calls channel-list and TPC helpers downstream of this regulatory state.

## State And Persistence

The struct contains many owned pointers to rule arrays; `ath12k_reg_reset_reg_info()` must free the 2/5 GHz pointers and all extended 6 GHz AP/client pointers. The state is transient per firmware event but may be cached as default/new regdomain state in `ath12k_base`.

## Risks And Test Signals

Risks are pointer ownership mistakes, matrix index mistakes for 6 GHz AP/client rules, and ABI drift with WMI regulatory events. Test signals include parser/build coverage for classic and extended regulatory events, 6 GHz LPI/SP/VLP behavior, no-11ax/no-11be flags, invalid pdev fallback/drop decisions, and cleanup under repeated country changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/reg.h -->
