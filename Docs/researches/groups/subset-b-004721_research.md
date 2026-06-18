# Research: subset-b-004721

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/mac.h

## Purpose

`mac.h` is the ath10k mac80211-facing API header. It declares the core MAC lifecycle, scan/off-channel work, management-frame work, beacon handling, TX scheduling/locking, rate mapping, rfkill, and helper routines implemented mostly by the ath10k MAC layer. It also defines small shared structures used by other ath10k files and one inline TX sequence-number helper.

The header is not hardware specific. It is the integration boundary between ath10k core/HIF/WMI code and Linux `mac80211` objects such as `struct ieee80211_hw`, `struct ieee80211_vif`, `struct ieee80211_txq`, and `struct ieee80211_supported_band`.

## Important APIs, Types, and Functions

Important local definitions:

- `WEP_KEYID_SHIFT` identifies the WEP key-id bit placement used by MAC code.
- `struct ath10k_generic_iter` carries an `ath10k` pointer plus return status through mac80211 interface iteration callbacks.
- `struct rfc1042_hdr` describes the packed LLC/SNAP RFC1042 header used when classifying or constructing Ethernet-over-802.11 payloads.
- `ath10k_tx_h_seq_no()` is an inline transmit-header helper that assigns per-vif sequence numbers when mac80211 sets `IEEE80211_TX_CTL_ASSIGN_SEQ`.

Declared lifecycle and registration APIs:

- `ath10k_mac_create()`, `ath10k_mac_destroy()`, `ath10k_mac_register()`, and `ath10k_mac_unregister()` allocate, tear down, register, and unregister the ath10k mac80211 device.
- `ath10k_halt()` and `ath10k_drain_tx()` provide broader MAC shutdown and TX-drain hooks.

Declared operational APIs:

- `ath10k_get_arvif()` maps firmware vdev IDs back to ath10k vif state.
- `__ath10k_scan_finish()`, `ath10k_scan_finish()`, and `ath10k_scan_timeout_work()` finish scan state from normal and timeout paths.
- `ath10k_offchan_tx_*()` and `ath10k_mgmt_over_wmi_tx_*()` purge or process queued off-channel/management-over-WMI transmissions.
- `ath10k_mac_vif_beacon_free()`, `ath10k_mac_handle_beacon()`, and `ath10k_mac_handle_beacon_miss()` support AP/STA beacon lifecycle and firmware events.
- `ath10k_mac_handle_tx_pause_vdev()` handles firmware TX pause/unpause events for a vdev.
- `ath10k_mac_hw_rate_to_idx()` and `ath10k_mac_bitrate_to_idx()` convert firmware/bitrate values into mac80211 rate indexes.
- `ath10k_mac_tx_lock()`, `ath10k_mac_tx_unlock()`, `ath10k_mac_vif_tx_lock()`, and `ath10k_mac_vif_tx_unlock()` expose driver-wide and per-vif TX flow-control gates.
- `ath10k_mac_tx_frm_has_freq()`, `ath10k_mac_tx_push_pending()`, `ath10k_mac_tx_push_txq()`, and `ath10k_mac_txq_lookup()` provide airtime/TXQ scheduling plumbing.
- `ath10k_mac_ext_resource_config()`, `ath10k_mac_wait_tx_complete()`, and `ath10k_mac_rfkill_enable_radio()` configure extended resources, wait for TX completion, and toggle radio state.

## Control Flow

Most code includes this header to call into the central MAC implementation rather than to execute logic here. The only in-header control flow is `ath10k_tx_h_seq_no()`: it reads `IEEE80211_SKB_CB(skb)`, checks `IEEE80211_TX_CTL_ASSIGN_SEQ`, lazily initializes `arvif->tx_seq_no` to `0x1000`, increments by `0x10` only for first fragments, preserves the fragment bits in `hdr->seq_ctrl`, and writes the new sequence-control field in little-endian form.

The declared functions support common driver flows: core creation registers a `struct ieee80211_hw`; firmware vdev events use `ath10k_get_arvif()` before notifying MAC code; scan timeout work finishes scans asynchronously; TX pause events lock or unlock queues; and off-channel/management work drains WMI-backed queues during normal operation and shutdown.

## State and Persistence Behavior

This header defines no global storage. Its function contracts mutate long-lived ath10k state in `struct ath10k`, `struct ath10k_vif`, queued `sk_buff` lists, scan/off-channel work items, mac80211 TXQs, and firmware-backed vdev state.

The inline sequence helper persists a monotonically increasing per-vif `arvif->tx_seq_no` value. It directly edits the 802.11 header in the outgoing skb. Callers must ensure the skb contains a writable 802.11 header and that `vif->drv_priv` is a valid `struct ath10k_vif`.

## Dependencies and Integration Points

`mac.h` depends on `<net/mac80211.h>` and `core.h`, and forward-declares WMI TLV TX-pause enums. Its declarations are consumed by PCI/SNOC/AHB HIF code, WMI event handlers, HTT/HTC completion paths, debug and recovery paths, and files such as `p2p.c` that update per-vif MAC-visible state.

The sequence helper integrates with mac80211 TX flags and Linux byte-order helpers (`cpu_to_le16`). The rate helpers integrate firmware rate encodings with mac80211 supported-band tables.

## Risks and Edge Cases

- `ath10k_tx_h_seq_no()` assumes `vif` is non-null and `vif->drv_priv` points to ath10k private data. It is appropriate only for ath10k-owned mac80211 TX paths.
- Sequence assignment preserves fragment bits but otherwise overwrites `seq_ctrl`; callers must use it only when mac80211 has delegated sequence assignment.
- The many raw pointer API declarations make implementation-side locking important. For example, lookup and TXQ helpers typically depend on `conf_mutex`, `data_lock`, RCU, or mac80211 serialization in their implementations.
- Forward declarations of WMI TLV enum types mean prototype drift with WMI headers would be caught only at compile time.

## Test Signals

- Build all ath10k bus variants and WMI variants that include `mac.h`.
- TX tests with fragmented management/data frames should verify sequence-control assignment and fragment preservation.
- Scan timeout/off-channel work cancellation tests should show no stale work after device stop or recovery.
- AP/P2P GO tests should exercise beacon updates, beacon misses, NOA integration, and TX pause events.
- Static analysis should focus on callers passing vdev IDs, TXQ pointers, and skbs without appropriate lifetime or locking guarantees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/p2p.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/p2p.c

## Purpose

`p2p.c` maintains Wi-Fi Direct Notice of Absence (NOA) information for ath10k AP/P2P-GO virtual interfaces. Firmware reports NOA timing through WMI, and this file converts the firmware `struct wmi_p2p_noa_info` into a vendor-specific P2P information element stored on `struct ath10k_vif`. Beacon/probe-response update code can then include the current NOA IE.

The file is deliberately small: it does not negotiate P2P roles or configure firmware. It only transforms and publishes NOA state into MAC-layer vif storage.

## Important APIs, Types, and Functions

Exported functions:

- `ath10k_p2p_noa_update()` updates one `struct ath10k_vif` from a `struct wmi_p2p_noa_info`.
- `ath10k_p2p_noa_update_by_vdev_id()` finds the active mac80211 interface whose `arvif->vdev_id` matches a firmware vdev ID and updates that interface.

Local helpers:

- `ath10k_p2p_noa_ie_len_compute()` returns zero when there are no NOA descriptors and Opportunistic Power Save is not enabled; otherwise it computes the complete vendor IE length including element ID, length byte, WFA OUI/type, NOA attribute header, index, CTWindow/OppPS byte, and descriptor array.
- `ath10k_p2p_noa_ie_fill()` serializes the P2P vendor IE and embedded `struct ieee80211_p2p_noa_attr` into a caller-provided buffer.
- `ath10k_p2p_noa_ie_assign()` replaces `arvif->u.ap.noa_data` and `arvif->u.ap.noa_len`, freeing the previous allocation.
- `__ath10k_p2p_noa_update()` clears existing NOA data, computes the new size, allocates with `GFP_ATOMIC`, fills the IE, and installs it.
- `ath10k_p2p_noa_update_vdev_iter()` is the mac80211 active-interface iterator callback.
- `struct ath10k_p2p_noa_arg` carries a target vdev ID and WMI NOA pointer through the iterator.

## Control Flow

The direct update path enters through `ath10k_p2p_noa_update()`, takes `ar->data_lock` with bottom halves disabled, calls `__ath10k_p2p_noa_update()`, and releases the lock. The internal helper first assigns `(NULL, 0)` to remove stale NOA data. It then computes the length; if the WMI event indicates no descriptors and no OppPS bit, the function exits with no IE installed. Otherwise it allocates an atomic buffer, serializes the IE, and stores the new pointer and length under the same lock.

The vdev-ID path enters through `ath10k_p2p_noa_update_by_vdev_id()`. It builds an iterator argument and calls `ieee80211_iterate_active_interfaces_atomic()` with `ATH10K_ITER_NORMAL_FLAGS`. The callback compares each active `arvif->vdev_id` to the requested ID and invokes the direct update path for the match.

`ath10k_p2p_noa_ie_fill()` writes the vendor-specific IE layout in order: WLAN vendor element ID and length, WFA OUI and P2P type, `IEEE80211_P2P_ATTR_ABSENCE_NOTICE`, little-endian attribute length, NOA index, CTWindow/OppPS byte, and each NOA descriptor. It converts `type_count` from WMI little-endian storage with `__le32_to_cpu()` and copies duration, interval, and start time as represented in the firmware structure.

## State and Persistence Behavior

Persistent state is per-vif AP storage:

- `arvif->u.ap.noa_data` owns the currently serialized P2P NOA IE allocation or is `NULL`.
- `arvif->u.ap.noa_len` stores the current IE length.

Updates occur under `ar->data_lock`, and helper functions assert that lock for assignment and internal update. Old NOA allocations are freed before new data is installed, so allocation failure leaves the vif with no NOA IE rather than stale data.

## Dependencies and Integration Points

The file includes `core.h`, `wmi.h`, `mac.h`, and `p2p.h`. It depends on:

- WMI P2P NOA definitions and bit fields such as `WMI_P2P_OPPPS_CTWINDOW_OFFSET` and `WMI_P2P_OPPPS_ENABLE_BIT`.
- mac80211 P2P structures/constants such as `struct ieee80211_p2p_noa_attr`, `struct ieee80211_p2p_noa_desc`, `IEEE80211_P2P_ATTR_ABSENCE_NOTICE`, and `IEEE80211_P2P_OPPPS_ENABLE_BIT`.
- cfg80211/mac80211 vendor IE constants `WLAN_EID_VENDOR_SPECIFIC`, `WLAN_OUI_WFA`, and `WLAN_OUI_TYPE_WFA_P2P`.
- `ieee80211_iterate_active_interfaces_atomic()` for vdev-to-vif resolution.

Beacon/probe response generation in the MAC layer is the main consumer of the stored `noa_data`.

## Risks and Edge Cases

- The fill helper trusts the computed length and `noa->num_descriptors`; if firmware ever reports more descriptors than the mac80211 NOA array representation supports, serialization could overrun the allocated shape. Correctness depends on WMI struct limits matching the P2P descriptor array contract.
- Allocation uses `GFP_ATOMIC` because updates run under spinlock/atomic iteration. Memory pressure silently drops the NOA IE after clearing the old one.
- The update-by-vdev path can call `ath10k_p2p_noa_update()` from inside an atomic iterator; that is compatible with spin locking but makes blocking allocations impossible.
- `ath10k_p2p_noa_ie_fill()` stores descriptor duration, interval, and start time without explicit endian conversion in this file. That is correct only if `struct wmi_p2p_noa_info` fields are already in the endianness expected by `struct ieee80211_p2p_noa_desc`.

## Test Signals

- P2P GO beacon/probe-response captures should show a vendor P2P NOA IE when firmware reports descriptors or OppPS, and no IE when both are absent.
- WMI event tests should verify replacement, clearing, and allocation-failure behavior for `arvif->u.ap.noa_data`.
- Lockdep should stay quiet for `data_lock` assertions and active-interface atomic iteration.
- Fuzz or synthetic WMI tests should cover zero descriptors, maximum descriptors, OppPS-only events, and CTWindow bit extraction.
- Memory-leak checks should verify old NOA buffers are freed on repeated updates and interface teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/p2p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/p2p.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/p2p.h

## Purpose

`p2p.h` is the public ath10k header for P2P Notice of Absence updates. It exposes the two update entry points implemented in `p2p.c` and forward-declares the ath10k and WMI structures needed by those prototypes.

## Important APIs, Types, and Functions

Declared APIs:

- `ath10k_p2p_noa_update(struct ath10k_vif *arvif, const struct wmi_p2p_noa_info *noa)` updates one ath10k virtual interface with serialized NOA IE state.
- `ath10k_p2p_noa_update_by_vdev_id(struct ath10k *ar, u32 vdev_id, const struct wmi_p2p_noa_info *noa)` resolves a firmware vdev ID to an active vif and applies the same update.

Forward declarations:

- `struct ath10k_vif`
- `struct ath10k`
- `struct wmi_p2p_noa_info`

## Control Flow and Integration

This header lets WMI event handling code publish firmware NOA reports to the P2P/MAC helper without depending on the implementation details. The direct API is used when the caller already owns an `ath10k_vif`; the vdev-ID API is used when firmware events carry only a numeric vdev identifier.

The implementation stores results in `arvif->u.ap.noa_data` and `arvif->u.ap.noa_len` under `ar->data_lock`, making this header part of the bridge between firmware event parsing and beacon/probe-response generation.

## State and Persistence Behavior

The header has no storage. Its APIs are stateful: they replace per-vif NOA allocation state and can clear previous NOA information if the incoming WMI structure has no active descriptor/OppPS content.

## Dependencies and Integration Points

`p2p.h` intentionally avoids including large headers. Users must include suitable ath10k core/WMI definitions when they need complete type information. The implementation depends on mac80211 active interface iteration, P2P IE definitions, and WMI NOA fields.

## Risks and Contract Notes

- The prototypes use raw pointers and do not express locking. Callers should rely on the implementation to take `data_lock`, but must provide live `ath10k`, `ath10k_vif`, and WMI NOA objects.
- The header forward-declares `struct ath10k` through use in the second prototype without declaring it locally. This is harmless for current include order if a prior header declares it, but standalone inclusion can produce a compile error unless `struct ath10k` is already visible.
- Vdev-ID updates operate only on active mac80211 interfaces; events for removed or not-yet-active vdevs are ignored by the implementation.

## Test Signals

- Compile units that include `p2p.h` both directly and through broader ath10k headers to catch missing forward declarations.
- WMI P2P NOA event tests should exercise both direct and vdev-ID update paths.
- Interface removal/recovery tests should ensure stale events do not dereference destroyed vifs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/p2p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/pci.c

## Purpose

`pci.c` is the ath10k PCIe/AHB host interface implementation for Qualcomm Atheros 802.11ac devices such as QCA988X, QCA6174, QCA99X0, QCA9984, QCA9888, QCA9377, and QCA9887. It owns PCI probing/removal, BAR mapping, DMA mask setup, Copy Engine (CE) pipe configuration, firmware boot-time target configuration, BMI transport, diagnostic memory access, interrupt/NAPI handling, power-save wake/sleep gating, firmware crash dumps, chip reset sequences, EEPROM calibration fetch, suspend/resume handling, and module registration.

The file is the bus-specific layer under ath10k core. It presents `struct ath10k_hif_ops` to the common core/HTC/HTT/WMI code and translates those operations into PCI MMIO, CE rings, DMA buffers, and firmware host-interest writes.

## Important APIs, Types, and Functions

Module parameters and device tables:

- `irq_mode` selects auto, legacy INTx, or MSI.
- `reset_mode` selects automatic reset or warm-only reset.
- `ath10k_pci_id_table` lists supported PCI device IDs.
- `ath10k_pci_supp_chips` validates device ID plus chip revision.

CE configuration:

- `pci_host_ce_config_wlan[]` describes host-side CE ring sizes, directions, callbacks, polling, and interrupt-disabling flags.
- `pci_target_ce_config_wlan[]` is copied to firmware so the target understands CE layout.
- `pci_target_service_to_ce_map_wlan[]` maps HTC services to uplink/downlink CE pipe numbers.
- `ath10k_pci_override_ce_config()` adjusts CE5/service mapping for QCA6174/QCA9377.

Public bus/HIF helpers:

- `ath10k_pci_read32()`, `ath10k_pci_write32()`, `ath10k_pci_soc_read32()`, `ath10k_pci_soc_write32()`, `ath10k_pci_reg_read32()`, and `ath10k_pci_reg_write32()` perform bounds-checked, wake-protected MMIO accesses through CE bus ops.
- `ath10k_pci_hif_tx_sg()` submits scatter/gather CE TX descriptors.
- `ath10k_pci_hif_diag_read()` and `ath10k_pci_diag_write_mem()` read/write target memory through the diagnostic CE.
- `ath10k_pci_hif_exchange_bmi_msg()` exchanges BMI bootloader messages over CE.
- `ath10k_pci_hif_map_service_to_pipe()` and `ath10k_pci_hif_get_default_pipe()` resolve HTC service pipes.
- `ath10k_pci_hif_send_complete_check()` polls CE completions when resources are low or forced.
- `ath10k_pci_hif_power_up()`, `ath10k_pci_hif_power_down()`, `ath10k_pci_hif_start()`, and `ath10k_pci_hif_stop()` implement HIF lifecycle.
- `ath10k_pci_alloc_pipes()`, `ath10k_pci_init_pipes()`, `ath10k_pci_free_pipes()`, `ath10k_pci_ce_deinit()`, `ath10k_pci_rx_post()`, `ath10k_pci_flush()`, `ath10k_pci_setup_resource()`, and `ath10k_pci_release_resource()` manage CE/NAPI/resources.

Power and interrupt helpers:

- `ath10k_pci_wake()`, `ath10k_pci_sleep()`, `ath10k_pci_force_wake()`, `ath10k_pci_force_sleep()`, `ath10k_pci_sleep_sync()`, and `ath10k_pci_ps_timer()` manage SoC wake references and delayed sleep.
- `ath10k_pci_irq_pending()`, `ath10k_pci_disable_and_clear_intx_irq()`, `ath10k_pci_enable_intx_irq()`, `ath10k_pci_irq_msi_fw_mask()`, `ath10k_pci_irq_msi_fw_unmask()`, `ath10k_pci_interrupt_handler()`, and `ath10k_pci_napi_poll()` implement interrupt masking, NAPI scheduling, and firmware-crash detection.

Reset/probe APIs:

- `ath10k_pci_wait_for_target_init()` waits for firmware initialization bits.
- `ath10k_pci_cold_reset()`, `ath10k_pci_warm_reset()`, and chip-specific reset wrappers perform hardware reset sequencing.
- `ath10k_pci_probe()` creates and registers ath10k core state for a PCI device.
- `ath10k_pci_remove()` unregisters and frees it.
- `ath10k_pci_pm_suspend()` and `ath10k_pci_pm_resume()` bridge device PM.

Crash/debug/calibration:

- `ath10k_pci_fw_dump_work()`, `ath10k_pci_dump_registers()`, and memory dump helpers collect firmware register and RAM dumps.
- `ath10k_pci_hif_fetch_cal_eeprom()` enables/read QCA9887 EEPROM calibration data and validates its checksum.

## Control Flow

Probe starts in `ath10k_pci_probe()`. It maps the PCI device ID to an ath10k hardware revision, PCI power-save policy, reset functions, and target-address conversion function. It then creates `struct ath10k`, fills `struct ath10k_pci`, sets CE bus ops, initializes CE/PCI resources, claims the PCI BAR with a 32-bit DMA mask, wakes the device, deinitializes any stale CE state, disables interrupts, initializes IRQ mode/NAPI, requests the IRQ, optionally validates early QCA988X chip IDs, resets the chip, reads and validates the final chip ID, and calls `ath10k_core_register()`. Error paths unwind IRQs, CE/NAPI resources, sleep state, BAR mapping, pipes, and core allocation.

HIF power-up disables ASPM temporarily, resets the chip, initializes CE pipes, writes target boot configuration with `ath10k_pci_init_config()`, and interrupts the target CPU to continue firmware initialization. `ath10k_pci_init_config()` reads the firmware `hi_interconnect_state` pointer, writes CE target pipe config and service-to-pipe map through diagnostic CE, clears PCIe L1 enable in firmware config flags, sets early allocation bank information, and sets `HI_OPTION_EARLY_CFG_DONE`.

HIF start enables NAPI, unmasks CE/INTx/MSI-firmware interrupts, posts RX buffers to all RX CE pipes, and restores saved ASPM bits. HIF stop disables interrupts, synchronizes IRQ, disables NAPI, cancels crash-dump work, performs a safe chip reset to stop device DMA/interrupts, flushes RX retry and CE buffers, and checks wake references.

TX uses `ath10k_pci_hif_tx_sg()`: it locks `ce_lock`, verifies ring space, submits all but the last item with `CE_SEND_FLAG_GATHER`, submits the final descriptor without gather, and reverts descriptors on failure. HTC and HTT TX completion callbacks drain completed CE sends and notify higher layers, unmapping HTT DMA where needed.

RX buffers are posted by `ath10k_pci_rx_post_pipe()`, which allocates skbs, DMA maps them, records physical addresses in skb control blocks, and posts them to CE destination rings. Completion callbacks drain CE receive completions, unmap or sync DMA, validate lengths, append data to skbs, call HTC/HTT/pktlog handlers, and repost or recycle buffers. CE1/CE5 callbacks also service CE4 polling because host-to-target HTT interrupts can be disabled/polled.

Interrupt handling wakes the device, filters shared INTx when needed, masks/clears interrupts, and schedules NAPI. NAPI first handles firmware crash indication, then services CE engines and HTT TX/RX completions. If work is below budget, it completes NAPI, checks for a pending CE summary race, and unmasks interrupts.

Diagnostic reads/writes use `ce_diag_mutex`, a coherent bounce buffer, CE address translation, CE send/receive polling loops, and strict timeout/length/address checks. BMI exchanges similarly DMA-map request/response buffers, post a receive buffer when needed, send on BMI CE, poll send/receive completion until timeout, and copy response data back.

Reset flow is chip-specific. QCA988X tries several warm resets and verifies CE access before optionally falling back to cold reset. QCA6174 performs cold then warm reset. QCA99X0-style devices perform cold reset. Warm reset disables interrupts, toggles SI0/CPU/CE reset bits, reinitializes pipes, waits for target init, clears LF timer, and verifies final target initialization.

## State and Persistence Behavior

Long-lived driver state includes:

- `struct ath10k_pci` private state: PCI device, BAR mapping, IRQ mode, CE pipes, diagnostic CE, resource arrays, timers, work item, saved link control, power-save wake refcount/awake cache, reset/address callbacks, and optional AHB continuation state.
- CE rings and per-transfer contexts, including skb DMA mappings and completion callbacks.
- Firmware-visible target state written through host-interest addresses: CE config, service map, PCIe config flags, early allocation, and option flags.
- Interrupt/NAPI registration state and MSI enable state.
- Runtime power-save state in `ps_wake_refcount`, `ps_awake`, and `ps_timer`.
- ath10k stats counters for firmware warm/cold reset and crash count.
- Core registration state through `ath10k_core_register()` and `ath10k_core_unregister()`.

No user-facing persistent storage is written. Firmware files are declared through `MODULE_FIRMWARE()` metadata.

## Dependencies and Integration Points

Direct dependencies include Linux PCI, module, interrupt, spinlock, DMA, NAPI, timer, workqueue, and PM APIs. ath10k dependencies include `core.h`, `debug.h`, `coredump.h`, `targaddrs.h`, `bmi.h`, `hif.h`, `htc.h`, `ce.h`, and `pci.h`.

Integration points:

- ath10k core consumes `ath10k_pci_hif_ops` for boot, HTC/WMI/HTT transport, diagnostic access, suspend/resume, and calibration fetch.
- CE code provides pipe allocation, ring management, interrupt summary, and per-engine service.
- HTC/HTT receive and transmit completion handlers consume skbs delivered by CE callbacks.
- Firmware host-interest symbols define boot-time target memory addresses.
- mac80211 integration occurs indirectly through ath10k core registration and NAPI.
- The module also initializes/exits AHB support from the same init/exit functions.

## Risks and Edge Cases

- MMIO reads return `0xffffffff` on wake failure and zero on out-of-bounds reads; callers must distinguish device-gone from valid values.
- PCI power-save wake reference balancing is critical. Missing `ath10k_pci_sleep()` after wake can block sleep; extra sleeps trigger warnings and could let the device sleep during MMIO.
- Diagnostic CE loops are synchronous busy-wait/poll paths with fixed timeouts. Firmware/CE stalls can fail boot, coredump, or BMI operations.
- RX posting failure schedules a retry timer; teardown must delete the timer before freeing CE/skbs, which `ath10k_pci_rx_retry_sync()` handles.
- `ath10k_pci_hif_tx_sg()` rollback reverts descriptors already submitted in the current batch; callers still own DMA mappings and skb lifetimes on failure.
- INTx/MSI masking has chip-specific TODOs for QCA99X0-style MSI firmware interrupt masking, making reset/stop ordering important to prevent stray interrupts.
- Warm reset comments document known CE recovery failures and host-hang risk on some cold reset scenarios.
- QCA6174/QCA9377 CE5 override changes service mapping; regressions here can break HTT RX or firmware boot.
- EEPROM calibration is QCA9887-specific and treats checksum failure as `-EINVAL`; platform data must match hardware.

## Test Signals

- Build with PCI, AHB, PM, coredump, and multiple ath10k hardware revisions enabled.
- Probe/remove tests on each supported PCI ID should verify BAR claim/release, DMA mask, IRQ mode selection, NAPI lifecycle, and core registration.
- Firmware boot tests should trace target init bits, CE config writes, service map writes, BMI exchange, and HIF start.
- MSI and INTx interrupt tests should cover shared IRQ filtering, pending-interrupt races in NAPI, crash indication, and IRQ teardown.
- Suspend/resume tests should validate forced sleep/wake and PCI config retry-timeout restoration.
- Fault injection should target DMA mapping, skb allocation, CE ring full, diagnostic CE timeout, MSI enable failure, chip reset failure, and board/calibration read failure.
- Recovery tests should verify firmware crash dump collection, safe reset, CE buffer cleanup, and no leaked DMA mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/pci.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/pci.h

## Purpose

`pci.h` declares the ath10k PCIe host-interface data structures, constants, and exported functions used by the PCI and AHB implementations. It defines the shared firmware-visible PCIe state block, per-CE-pipe host state, supported chip metadata, IRQ mode selection, and the `struct ath10k_pci` private state embedded behind `ar->drv_priv`.

## Important APIs, Types, and Functions

Key constants:

- `DIAG_TRANSFER_LIMIT`, `DIAG_ACCESS_CE_TIMEOUT_US`, and `DIAG_ACCESS_CE_WAIT_US` bound diagnostic CE operations.
- `ATH10K_PCI_RX_POST_RETRY_MS`, `ATH_PCI_RESET_WAIT_MAX`, `PCIE_WAKE_TIMEOUT`, `PCIE_WAKE_LATE_US`, and `ATH10K_PCI_SLEEP_GRACE_PERIOD_MSEC` tune RX retry, reset, wake, and delayed sleep behavior.
- `BAR_NUM`, `CDC_WAR_MAGIC_STR`, and `CDC_WAR_DATA_CE` identify PCI BAR and hardware workaround values.

Types:

- `struct bmi_xfer` tracks BMI CE send/receive completion, response length, and whether a response is expected.
- `struct pcie_state` is a firmware-shared all-32-bit layout containing target addresses for CE config/service maps, MSI request/grant/address/data fields, power-management method, and config flags. Firmware discovers it through `HOST_INTEREST->hi_interconnect_state`.
- `struct ath10k_pci_pipe` stores one CE pipe handle, pipe number, back pointer to ath10k, buffer size, and a pipe lock for send/completion accounting.
- `struct ath10k_pci_supp_chip` pairs a PCI device ID with a supported chip revision.
- `enum ath10k_pci_irq_mode` selects automatic, INTx, or MSI operation.
- `struct ath10k_pci` is the main PCI private state: PCI device, mapped BAR, IRQ mode, pipe array, diagnostic CE/mutex, dump work, CE state, RX retry timer, saved PCIe link control, power-save lock/refcount/timer/cache, reset and address-conversion callbacks, mutable CE config arrays, and trailing AHB private storage.

Exported functions:

- MMIO helpers: `ath10k_pci_write32()`, `ath10k_pci_read32()`, `ath10k_pci_soc_*()`, and `ath10k_pci_reg_*()`.
- HIF/CE helpers: `ath10k_pci_hif_tx_sg()`, `ath10k_pci_hif_diag_read()`, `ath10k_pci_diag_write_mem()`, `ath10k_pci_hif_exchange_bmi_msg()`, `ath10k_pci_hif_map_service_to_pipe()`, `ath10k_pci_hif_get_default_pipe()`, `ath10k_pci_hif_send_complete_check()`, `ath10k_pci_hif_get_free_queue_number()`.
- Lifecycle/resource helpers: `ath10k_pci_hif_power_down()`, `ath10k_pci_alloc_pipes()`, `ath10k_pci_free_pipes()`, `ath10k_pci_init_pipes()`, `ath10k_pci_ce_deinit()`, `ath10k_pci_init_napi()`, `ath10k_pci_rx_post()`, `ath10k_pci_flush()`, `ath10k_pci_setup_resource()`, and `ath10k_pci_release_resource()`.
- Interrupt helpers: `ath10k_pci_enable_intx_irq()`, `ath10k_pci_irq_pending()`, `ath10k_pci_disable_and_clear_intx_irq()`, and `ath10k_pci_irq_msi_fw_mask()`.
- Boot helper: `ath10k_pci_wait_for_target_init()`.

## Control Flow and Integration

The header lets `pci.c`, AHB glue, and common ath10k code share one bus-private shape. Typical flow is: allocate `struct ath10k` with enough private bytes for `struct ath10k_pci`, access it with `ath10k_pci_priv()`, initialize CE resources and IRQ/NAPI, power/reset the target, write `struct pcie_state`-referenced CE tables into firmware memory, start HIF, exchange HTC/HTT/WMI traffic, then stop and release resources on remove or recovery.

`struct pcie_state` is part of the boot protocol with firmware. Host software writes target addresses for `ce_pipe_config` and `service_to_pipe` arrays, while firmware reads MSI and power-management fields from the same shared state.

## State and Persistence Behavior

This header defines structures for long-lived in-kernel state but no storage by itself. Persistent runtime state includes BAR mapping, CE ring ownership, diagnostic CE serialization, timers/work items, IRQ mode, saved ASPM bits, and power-save wake reference counts. The trailing flexible `struct ath10k_ahb ahb[]` allows AHB support to extend the same private allocation without a second top-level private object.

## Dependencies and Integration Points

`pci.h` includes Linux interrupt/mutex APIs plus `hw.h`, `ce.h`, and `ahb.h`. It is consumed by PCI implementation, AHB code that reuses CE/HIF logic, and ath10k core paths that need exported PCI helpers.

The declared functions integrate with Linux PCI/MMIO/DMA, ath10k CE rings, HTC/HTT transport, BMI bootloader messaging, firmware target-address definitions, and mac80211-facing NAPI.

## Risks and Contract Notes

- `struct pcie_state` is shared with firmware, so field sizes, order, and 32-bit alignment are ABI-sensitive.
- `struct ath10k_pci_priv()` blindly casts `ar->drv_priv`; callers must ensure the ath10k instance is PCI/AHB-backed.
- Power-save comments warn that accessing most MMIO while asleep can corrupt host memory or return invalid readouts; all users should go through wake-protected helpers unless a reset path intentionally bypasses them.
- The `pci_ps` flag changes wake/sleep behavior substantially. QCA988X/QCA99X0 disable frequent power-save register locking, while QCA6174/QCA9377 depend on delayed sleep.
- Function prototypes expose raw pipe IDs and addresses; callers must validate pipe range, target address mapping, and DMA lifetimes.

## Test Signals

- Compile both PCI and AHB variants that include this header.
- ABI-sensitive checks should compare `struct pcie_state` offsets with firmware expectations.
- Probe/recovery tests should verify every timer/work/mutex/spinlock field is initialized before use and released after teardown.
- Static analysis should flag raw pipe/address calls without range validation.
- Power-save stress tests should exercise wake refcount balance across MMIO, interrupt, suspend, and reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/qmi.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/qmi.c

## Purpose

`qmi.c` implements ath10k's Qualcomm WLFW QMI client for SNOC/WCN3990-style devices. It discovers and connects to the firmware QMI service over QRTR, registers for indications, negotiates host capabilities, shares MSA memory information and permissions, downloads board data, reports calibration metadata, switches firmware WLAN modes, fetches firmware/chip capability information, controls firmware log mode, and converts asynchronous QMI indications into ordered ath10k SNOC firmware events.

The file is the control-plane companion to the SNOC HIF path. It does not carry HTT data traffic; it prepares firmware and memory ownership so the WLAN subsystem can boot and run.

## Important APIs, Types, and Functions

Exported APIs:

- `ath10k_qmi_init()` allocates and starts the QMI client, workqueue, message handlers, and service lookup.
- `ath10k_qmi_deinit()` releases the QMI handle, drains event work, destroys the workqueue, and frees state.
- `ath10k_qmi_wlan_enable()` sends WLAN configuration and mode requests.
- `ath10k_qmi_wlan_disable()` switches firmware to `QMI_WLFW_OFF_V01`.
- `ath10k_qmi_set_fw_log_mode()` sends the WLFW INI request to enable/disable firmware logging.

MSA memory and permissions:

- `ath10k_qmi_msa_mem_info_send_sync_msg()` sends host MSA base/size, receives firmware memory-region subranges, validates they fit inside allocated MSA, and records them in `qmi->mem_region`.
- `ath10k_qmi_setup_msa_permissions()` assigns memory to MSS_MSA/WLAN and optionally WLAN_CE through `qcom_scm_assign_mem()`.
- `ath10k_qmi_remove_msa_permission()` returns memory ownership to HLOS.
- `ath10k_qmi_msa_ready_send_sync_msg()` notifies firmware that MSA memory is ready.

Firmware configuration and data:

- `ath10k_qmi_cfg_send_sync_msg()` sends CE target config, service config, and shadow register config.
- `ath10k_qmi_mode_send_sync_msg()` sends WLFW mode changes.
- `ath10k_qmi_cap_send_sync_msg()` retrieves chip, board, SoC, firmware version, build timestamp, build ID, and MAC count capability data.
- `ath10k_qmi_host_cap_send_sync()` sends host capability/daemon support, using an 8-bit quirk encoder when required.
- `ath10k_qmi_bdf_dnld_send_sync()` chunks and downloads board data in `QMI_WLFW_MAX_DATA_SIZE_V01` segments.
- `ath10k_qmi_send_cal_report_req()` reports available calibration IDs and optional XO calibration data.
- `ath10k_qmi_fetch_board_file()` maps QMI chip/board IDs into ath10k board-file lookup.

Events and QMI plumbing:

- `ath10k_qmi_driver_event_post()` queues internal events under `event_lock` and wakes an ordered workqueue.
- `ath10k_qmi_driver_event_work()` serially handles server arrival/exit, FW ready, and MSA ready events.
- `ath10k_qmi_new_server()` connects the QMI socket and posts server-arrive.
- `ath10k_qmi_del_server()` posts server-exit when the real firmware service disappears.
- `qmi_msg_handler[]` maps WLFW FW_READY and MSA_READY indications to posting callbacks.

## Control Flow

Initialization allocates `struct ath10k_qmi`, stores it in `ath10k_snoc`, reads device-tree booleans `qcom,msa-fixed-perm` and `qcom,no-msa-ready-indicator`, initializes a QMI handle with the maximum BDF download request size and message handlers, creates an ordered workqueue, initializes the event list and lock, registers a WLFW service lookup, and marks state `ATH10K_QMI_STATE_INIT_DONE`.

When QRTR discovers the WLFW server, `ath10k_qmi_new_server()` records the node/port, connects the socket, and posts `SERVER_ARRIVE`. The ordered worker handles arrival by registering indications. If firmware already reported ready in the registration response, it immediately informs SNOC of FW ready. Otherwise it optionally sends host capabilities, sends MSA memory info, waits 20 ms for an SDM845 security-workaround gap, assigns MSA permissions unless fixed by platform, sends MSA ready, and requests capabilities.

MSA ready can arrive as a QMI indication or be synthesized immediately for platforms with `no_msa_ready_indicator`. The worker then fetches the board file using QMI chip/board IDs, downloads it in segmented QMI requests, and sends a calibration report request. Firmware ready indication is translated into `ath10k_snoc_fw_indication(ar, ATH10K_QMI_EVENT_FW_READY_IND)`.

WLAN enable sends config first, then mode. Config copies caller-provided CE target/service/shadow register arrays into the WLFW request, clamping lengths to QMI maximums. Mode sends the requested `enum wlfw_driver_mode_enum_v01` plus `hw_debug = 0`. WLAN disable is the same mode path with `OFF`.

Server exit removes MSA permissions, frees board files, triggers a SNOC firmware crash dump unless unregistering or modem-stopped flags are set, sends a FW_DOWN indication, and logs disconnect. Deinit sets state to DEINIT before releasing the QMI handle so client-triggered del-server events are ignored.

## State and Persistence Behavior

Long-lived state is stored in `struct ath10k_qmi`:

- QMI handle and QRTR sockaddr.
- Ordered event workqueue, event list, and spinlock.
- MSA memory region count and region metadata.
- Firmware/chip/board/SoC IDs, firmware version, build ID, and build timestamp.
- Calibration data metadata pointers.
- Platform booleans for fixed MSA permissions and missing MSA-ready indication.
- `fw_ready` and init/deinit state.

The file changes memory ownership through SCM calls; those permissions persist outside normal kernel pointer lifetime until explicitly unmapped or firmware/service exit occurs. It also writes firmware build ID into Qualcomm SMEM image version table when present.

## Dependencies and Integration Points

Linux dependencies include QMI/QRTR, completions/transactions, ordered workqueues, device tree, SCM memory assignment, SMEM, firmware loading, and sockets.

ath10k dependencies include `debug.h`, `snoc.h`, ath10k core board-file lookup/freeing, SNOC firmware indication/crash dump functions, SNOC quirk flags, and the WLFW schema from `qmi_wlfw_v01.h/.c`.

Firmware-facing dependencies include WLFW service ID/version, request/response message IDs, `qmi_elem_info` encoder arrays, and QMI response result/error conventions.

## Risks and Edge Cases

- MSA region validation must prevent overflow and out-of-range firmware-provided addresses. The code checks region start, size, and end against the allocated MSA range; future changes should preserve those checks.
- MSA permission assignment is multi-region and must unwind already-mapped regions on partial failure.
- `ath10k_qmi_msa_ready_send_sync_msg()` returns success at the end even after a rejected response sets `ret = -EINVAL`; this path should be reviewed because it appears to lose the error before returning.
- Board-data download treats a final-segment malformed-message result as non-fatal for known firmware/BDF CRC behavior. Tests should ensure only that expected condition is ignored.
- Event queue allocation uses `GFP_ATOMIC`; memory pressure can drop QMI events and stall boot/recovery.
- Server exit behavior intentionally distinguishes real firmware service removal from local QMI handle release through `qmi->state`.
- The host capability request has an 8-bit daemon-support quirk; using the wrong encoder can break older firmware.
- `ath10k_qmi_cfg_send_sync_msg()` accepts a `version` argument but does not send it (`host_version_valid = 0`), so callers should not expect version propagation.

## Test Signals

- Boot tests on WCN3990/SNOC platforms should trace server discovery, indication registration, MSA info, SCM permission assignment, MSA ready, capability read, board download, cal report, and FW ready.
- Device-tree variants should cover fixed MSA permissions and missing MSA-ready indication.
- QMI fault injection should cover rejected responses, transaction timeouts, oversized memory-region counts, out-of-range memory regions, BDF segment failures, and event allocation failure.
- Recovery tests should verify server exit frees board files, removes permissions, sends FW_DOWN, and triggers crash dump only when expected.
- Firmware log tests should validate `ath10k_qmi_set_fw_log_mode()` with accepted and rejected INI responses.
- SMEM update tests should confirm firmware build IDs are copied only when the SMEM table exists and is large enough.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/qmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/qmi.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/qmi.h

## Purpose

`qmi.h` declares ath10k's SNOC/WCN3990 WLFW QMI client state, configuration structures, event types, and exported control APIs. It is the contract between SNOC bus code, ath10k core, and the QMI implementation in `qmi.c`.

## Important APIs, Types, and Functions

Constants:

- `MAX_NUM_MEMORY_REGIONS`, `MAX_TIMESTAMP_LEN`, `MAX_BUILD_ID_LEN`, and `MAX_NUM_CAL_V01` mirror WLFW limits for local ath10k state.

Event and state enums:

- `enum ath10k_qmi_driver_event_type` covers server arrival/exit, FW ready/down, MSA ready, and max sentinel.
- `enum ath10k_qmi_state` distinguishes initialized from deinitializing/deinitialized QMI client state.

State structures:

- `struct ath10k_msa_mem_info` records a physical address, size, and secure flag for one MSA memory region.
- `struct ath10k_qmi_chip_info`, `struct ath10k_qmi_board_info`, and `struct ath10k_qmi_soc_info` store IDs returned by firmware.
- `struct ath10k_qmi_cal_data` stores one calibration ID, total size, and data pointer.
- `struct ath10k_tgt_pipe_cfg`, `struct ath10k_svc_pipe_cfg`, and `struct ath10k_shadow_reg_cfg` describe CE target/service/shadow-register configuration sent to firmware.
- `struct ath10k_qmi_wlan_enable_cfg` bundles CE config arrays and counts for WLAN enable.
- `struct ath10k_qmi_driver_event` is the internal workqueue event node.
- `struct ath10k_qmi` holds the QMI handle, QRTR endpoint, event workqueue/list/lock, MSA region state, firmware identity strings, calibration data, platform flags, readiness flag, and lifecycle state.

Exported APIs:

- `ath10k_qmi_wlan_enable()`
- `ath10k_qmi_wlan_disable()`
- `ath10k_qmi_init()`
- `ath10k_qmi_deinit()`
- `ath10k_qmi_set_fw_log_mode()`

## Control Flow and Integration

SNOC code allocates core ath10k state, calls `ath10k_qmi_init()` with the MSA size, waits for QMI events to prepare firmware memory and board data, and later uses `ath10k_qmi_wlan_enable()` to send CE/shadow-register config and switch firmware into a requested WLFW mode. Shutdown or recovery calls `ath10k_qmi_wlan_disable()` and `ath10k_qmi_deinit()`.

The structures in this header bridge local CE configuration to the generated WLFW schema. For example, `ath10k_qmi_wlan_enable_cfg` carries host-native arrays that `qmi.c` copies into `wlfw_wlan_cfg_req_msg_v01`.

## State and Persistence Behavior

`struct ath10k_qmi` is long-lived from `ath10k_qmi_init()` until `ath10k_qmi_deinit()`. Its memory-region and permission-related fields reflect ownership that may also be changed in secure firmware through SCM. Firmware identity fields persist for board-file selection and logging. The event list persists queued asynchronous QMI state changes until the ordered worker processes them.

## Dependencies and Integration Points

The header includes Linux QMI and QRTR types and the generated WLFW schema `qmi_wlfw_v01.h`. It references `struct ath10k`, SNOC private state indirectly through the implementation, Qualcomm SCM/SMEM through implementation code, and ath10k core board-file paths.

## Risks and Contract Notes

- Several count-plus-pointer fields in `ath10k_qmi_wlan_enable_cfg` must remain valid for the duration of the synchronous QMI config call.
- `MAX_*` local constants intentionally match WLFW schema sizes; divergence can cause truncation or overrun risk in implementation code.
- Event `data` is a raw `void *`, though current events use `NULL`. If future events attach payloads, ownership and freeing rules must be explicit.
- `struct ath10k_qmi` exposes mutable fields such as `fw_ready` and `state`; callers outside `qmi.c` should avoid changing them directly.

## Test Signals

- Compile SNOC/QMI builds to catch schema/header drift.
- Unit or fault-injection tests should exercise lifecycle ordering: init, server arrive, WLAN enable/disable, server exit, deinit.
- Static analysis should verify count fields are clamped before copying into WLFW fixed-size arrays.
- Recovery tests should ensure event-list work is drained before freeing `struct ath10k_qmi`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/qmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/qmi_wlfw_v01.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/qmi_wlfw_v01.c

## Purpose

`qmi_wlfw_v01.c` is the generated/static QMI TLV description table set for the ath10k WLFW v01 service used by WCN3990/SNOC firmware. Each exported `const struct qmi_elem_info ..._ei[]` array describes how the Linux QMI framework encodes or decodes one WLFW request, response, indication, or nested structure declared in `qmi_wlfw_v01.h`.

The file contains no device-control logic by itself. It is protocol metadata consumed by `qmi.c` through `qmi_send_request()`, `qmi_txn_init()`, and QMI indication handlers.

## Important APIs, Types, and Functions

Nested schema arrays:

- `wlfw_ce_tgt_pipe_cfg_s_v01_ei`, `wlfw_ce_svc_pipe_cfg_s_v01_ei`, `wlfw_shadow_reg_cfg_s_v01_ei`, and `wlfw_shadow_reg_v2_cfg_s_v01_ei` describe CE and shadow register config structures.
- `wlfw_memory_region_info_s_v01_ei`, `wlfw_mem_cfg_s_v01_ei`, `wlfw_mem_seg_s_v01_ei`, and `wlfw_mem_seg_resp_s_v01_ei` describe MSA/DDR memory request and response structures.
- `wlfw_rf_chip_info_s_v01_ei`, `wlfw_rf_board_info_s_v01_ei`, `wlfw_soc_info_s_v01_ei`, and `wlfw_fw_version_info_s_v01_ei` describe capability substructures.

Exported message arrays include:

- Indication registration and indications: `wlfw_ind_register_req_msg_v01_ei`, `wlfw_ind_register_resp_msg_v01_ei`, `wlfw_fw_ready_ind_msg_v01_ei`, `wlfw_msa_ready_ind_msg_v01_ei`, `wlfw_pin_connect_result_ind_msg_v01_ei`, `wlfw_mem_ready_ind_msg_v01_ei`, `wlfw_fw_init_done_ind_msg_v01_ei`, `wlfw_rejuvenate_ind_msg_v01_ei`, and `wlfw_xo_cal_ind_msg_v01_ei`.
- WLAN mode/config/capability: `wlfw_wlan_mode_req_msg_v01_ei`, `wlfw_wlan_mode_resp_msg_v01_ei`, `wlfw_wlan_cfg_req_msg_v01_ei`, `wlfw_wlan_cfg_resp_msg_v01_ei`, `wlfw_cap_req_msg_v01_ei`, and `wlfw_cap_resp_msg_v01_ei`.
- Board/calibration: `wlfw_bdf_download_req_msg_v01_ei`, `wlfw_bdf_download_resp_msg_v01_ei`, `wlfw_cal_report_req_msg_v01_ei`, `wlfw_cal_report_resp_msg_v01_ei`, `wlfw_cal_download_req_msg_v01_ei`, `wlfw_cal_download_resp_msg_v01_ei`, `wlfw_cal_update_req_msg_v01_ei`, and `wlfw_cal_update_resp_msg_v01_ei`.
- Memory and diagnostics: `wlfw_msa_info_req_msg_v01_ei`, `wlfw_msa_info_resp_msg_v01_ei`, `wlfw_msa_ready_req_msg_v01_ei`, `wlfw_msa_ready_resp_msg_v01_ei`, `wlfw_request_mem_ind_msg_v01_ei`, `wlfw_respond_mem_req_msg_v01_ei`, `wlfw_respond_mem_resp_msg_v01_ei`, `wlfw_athdiag_read_*_ei`, and `wlfw_athdiag_write_*_ei`.
- Miscellaneous control: `wlfw_ini_req_msg_v01_ei`, `wlfw_ini_resp_msg_v01_ei`, `wlfw_vbatt_*_ei`, `wlfw_mac_addr_*_ei`, `wlfw_host_cap_req_msg_v01_ei`, `wlfw_host_cap_8bit_req_msg_v01_ei`, `wlfw_host_cap_resp_msg_v01_ei`, `wlfw_rejuvenate_ack_*_ei`, `wlfw_dynamic_feature_mask_*_ei`, and `wlfw_m3_info_*_ei`.

## Control Flow

There is no runtime branching beyond QMI framework interpretation of the arrays. Each array is a sequence of element descriptors ending with `{}`. Descriptors define data type, element count, element size, array kind, TLV type, struct offset, and nested `ei_array` when the field is itself a struct.

The QMI framework uses these arrays during request send and response/indication decode. For example, `ath10k_qmi_cfg_send_sync_msg()` passes `wlfw_wlan_cfg_req_msg_v01_ei`; the framework serializes optional flags, variable-length CE target/service arrays, and shadow register arrays into TLVs. For a capability response, `wlfw_cap_resp_msg_v01_ei` decodes a mandatory QMI response TLV plus optional chip, board, SoC, firmware version, build ID, and MAC-count TLVs.

## State and Persistence Behavior

The file defines read-only global constant arrays. It does not allocate memory, perform I/O, or mutate driver state. Persistence concerns are schema stability: TLV types, offsets, array lengths, and signedness are ABI between host driver and firmware.

## Dependencies and Integration Points

The file includes `<linux/soc/qcom/qmi.h>`, `<linux/types.h>`, and `qmi_wlfw_v01.h`. It depends on:

- Linux QMI data types such as `QMI_UNSIGNED_*`, `QMI_SIGNED_4_BYTE_ENUM`, `QMI_STRING`, `QMI_STRUCT`, `QMI_OPT_FLAG`, and `QMI_DATA_LEN`.
- Array kinds `NO_ARRAY`, `STATIC_ARRAY`, and `VAR_LEN_ARRAY`.
- `qmi_response_type_v01_ei` for standard response TLVs.
- Exact struct layouts from `qmi_wlfw_v01.h`.

`qmi.c` is the primary consumer, and firmware is the peer that must match this schema.

## Risks and Edge Cases

- Offset/type mismatches silently corrupt QMI encoding or decoding. Any change to message structs in the header must be reflected here.
- Several length fields are declared as `u32` in structs but encoded with `elem_size = sizeof(u8)` or `sizeof(u16)` where the QMI protocol length field is narrower. Values must be clamped before encoding, as `qmi.c` does for CE arrays and BDF segments.
- `wlfw_host_cap_8bit_req_msg_v01_ei` intentionally encodes only daemon support as an 8-bit field for old firmware quirks; using it for normal firmware would omit capabilities.
- Empty indication/request arrays are valid zero-length messages; callers must still use the correct max message length and message ID.
- Variable-length arrays depend on matching `QMI_DATA_LEN` descriptors immediately preceding array descriptors for the same TLV.

## Test Signals

- Compile-time coverage catches missing exported arrays referenced by `qmi.c`.
- QMI boot tests should verify successful encode/decode for indication registration, MSA info/ready, capability, BDF download, config, mode, and INI requests.
- Protocol tests should exercise max-length BDF/calibration/athdiag payloads, zero-length messages, and maximum CE/service/shadow-register arrays.
- Firmware compatibility tests should cover the normal and 8-bit host-capability encoders.
- Static checks should compare each `offsetof()` target, `elem_size`, `elem_len`, and TLV type against the WLFW IDL/source schema.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/qmi_wlfw_v01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/qmi_wlfw_v01.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/qmi_wlfw_v01.h

## Purpose

`qmi_wlfw_v01.h` declares the WLFW v01 QMI protocol used by ath10k WCN3990/SNOC firmware. It contains service identifiers, message IDs, maximum message sizes, protocol limits, enums, bit masks, request/response/indication structures, and extern declarations for the encoder/decoder arrays implemented in `qmi_wlfw_v01.c`.

This header is the host-side protocol ABI for firmware-management QMI traffic. It is consumed by `qmi.c` and the Linux QMI framework rather than by data-plane HTT/HTC traffic.

## Important APIs, Types, and Functions

Service and message identifiers:

- `WLFW_SERVICE_ID_V01` and `WLFW_SERVICE_VERS_V01` identify the QRTR/QMI service.
- `QMI_WLFW_*_REQ/RESP/IND_V01` constants define message IDs for indication registration, FW ready, WLAN mode/config, capability, BDF/calibration transfer, MSA memory, firmware log INI, athdiag, host capability, dynamic feature mask, M3 info, rejuvenation, and XO calibration.

Protocol limits and bit masks:

- Limits include `QMI_WLFW_MAX_DATA_SIZE_V01`, `QMI_WLFW_MAX_ATHDIAG_DATA_SIZE_V01`, `QMI_WLFW_MAX_NUM_CE_V01`, `QMI_WLFW_MAX_NUM_SVC_V01`, `QMI_WLFW_MAX_NUM_SHADOW_REG_V01`, `QMI_WLFW_MAX_MEM_REG_V01`, `QMI_WLFW_MAX_NUM_MEM_SEG_V01`, build/timestamp/string lengths, and MAC address size.
- CE attribute flags define no-snoop, byte-swap, descriptor swizzle, interrupt disable, and polling.
- Firmware status bits include already registered, FW ready, MSA ready, memory ready, and FW init done.

Enums:

- `enum wlfw_driver_mode_enum_v01` includes mission, FTM, epping, WAL test, off, CCPM, QVIT, and calibration modes.
- `enum wlfw_cal_temp_id_enum_v01` identifies up to five calibration slots.
- `enum wlfw_pipedir_enum_v01` defines none/in/out/inout CE directions.
- `enum wlfw_mem_type_enum_v01` distinguishes MSA and DDR memory.

Message structures:

- Configuration and mode: `wlfw_wlan_cfg_req_msg_v01`, `wlfw_wlan_mode_req_msg_v01`, and corresponding responses.
- Capability and version: `wlfw_cap_resp_msg_v01` and nested RF chip/board/SoC/version structs.
- Board/calibration: BDF download, calibration report/download/update messages and calibration indications.
- Memory: MSA info, MSA ready, request/respond memory, and memory-ready indications.
- Diagnostics/control: INI firmware log, athdiag read/write, voltage, MAC address, host capability, rejuvenation, dynamic feature mask, M3 info, and XO calibration messages.
- Standard response structs embed `struct qmi_response_type_v01`.

Each message type has a `WLFW_*_MAX_MSG_LEN` macro and an extern `wlfw_*_ei[]` declaration.

## Control Flow and Integration

This header does not execute control flow. It defines the structures that `qmi.c` fills before calling QMI transaction APIs and the response/indication structures populated by the QMI framework. The matching `qmi_elem_info` arrays in `qmi_wlfw_v01.c` use the exact field offsets from these structs to serialize TLVs.

Typical firmware boot flow uses this header in this order: register indications, optionally send host capability, send MSA info, send MSA ready, request capability, fetch board file using returned IDs, download BDF segments, send calibration report, send WLAN config, and switch WLAN mode.

## State and Persistence Behavior

The header defines no storage. Its structures represent transient QMI messages, but values decoded from them persist in `struct ath10k_qmi` and firmware state. The ABI itself is persistent: changing IDs, field types, max lengths, or enum values affects host/firmware interoperability.

## Dependencies and Integration Points

The header depends on Linux integer/endianness types through included users and `struct qmi_response_type_v01`/`struct qmi_elem_info` declarations from the QMI subsystem. It is included by `qmi.h`, `qmi.c`, and `qmi_wlfw_v01.c`.

Firmware and the Linux QMI framework are the main external integration points. ath10k SNOC code indirectly relies on chip/board IDs, firmware build strings, and mode/config message shapes declared here.

## Risks and Edge Cases

- This file is protocol ABI. Any field reorder, type change, max-length change, or message ID change can break firmware communication.
- Several messages have optional-field-valid booleans. Callers must set the valid flag for optional payloads or the QMI encoder will omit them.
- Large payload messages cap data at 6144 bytes; board and calibration downloads must segment larger blobs correctly.
- Some request structs include placeholder fields for zero-length messages; the corresponding max message length remains zero and QMI elem arrays are empty.
- Local ath10k structs in `qmi.h` mirror some of these WLFW shapes but are not identical; conversion code must keep endian and width assumptions clear.
- The host capability quirk has two encoder arrays for one C struct; caller-side selection must match firmware expectation.

## Test Signals

- Compile QMI/SNOC builds to ensure every extern array has an implementation.
- Firmware boot and recovery logs should confirm all expected message IDs succeed.
- Boundary tests should cover maximum BDF/calibration/athdiag payload sizes, maximum CE/service/shadow-register counts, maximum memory segments, and absent optional fields.
- Schema conformance checks should compare this header and `qmi_wlfw_v01.c` against the WLFW IDL used by firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/qmi_wlfw_v01.h -->
