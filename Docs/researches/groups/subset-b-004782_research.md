# Research: subset-b-004782

Grouped research report for the subset B work item. Each file section is wrapped with reconciliation markers so it can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/main.c

## Purpose
`main.c` is the central Broadcom b43 mac80211 driver implementation. It registers the BCMA, SSB, and SDIO-facing driver entry points, builds the mac80211 `ieee80211_ops` table, manages firmware loading and upload, initializes and resets wireless cores, services interrupts, handles TX/RX queueing, programs shared memory and template RAM, manages hardware keys, and coordinates common PHY operations through the `struct b43_phy_operations` vtable.

## Important APIs, Types, and Functions
- Module parameters control runtime behavior: firmware postfix, hardware power control, hardware crypto/TKIP, QoS, Bluetooth coexistence, verbosity, PIO forcing, and broad hardware support gating.
- Device tables `b43_bcma_tbl` and `b43_ssb_tbl` match 802.11 cores by BCMA/SSB revision.
- Shared-memory and timing helpers include `b43_shm_read16/32`, `b43_shm_write16/32`, `b43_hf_read`, `b43_hf_write`, `b43_tsf_read`, and `b43_tsf_write`.
- Core and MAC lifecycle functions include `b43_wireless_core_reset`, `b43_wireless_core_init`, `b43_wireless_core_start`, `b43_wireless_core_stop`, `b43_wireless_core_exit`, `b43_mac_suspend`, `b43_mac_enable`, and `b43_controller_restart`.
- Firmware paths include `b43_do_request_fw`, `b43_try_request_fw`, `b43_request_firmware`, `b43_upload_microcode`, `b43_write_initvals`, and the release helpers.
- mac80211 entry points are gathered in `b43_hw_ops`: TX, interface add/remove, config, BSS changes, filter configuration, key setup, TSF, start/stop, scan notifications, survey, and rfkill polling.
- Interrupt handling is split between `b43_do_interrupt` top-half collection/ACK and `b43_do_interrupt_thread` threaded work, with an SDIO process-context variant.
- Hardware encryption helpers program key table memory, RCMTA MAC slots, default RX/TX keys, and TKIP phase-1 state.
- Static channel/rate tables publish 2.4 GHz, 5 GHz A-PHY, full N-PHY 5 GHz, and limited channel variants to mac80211.

## Control Flow
Module init initializes debugfs and SDIO support, then registers BCMA and/or SSB bus drivers. Probe allocates a `b43_bus_dev`, creates the mac80211 `ieee80211_hw`, attaches one wireless core, and schedules asynchronous firmware loading. Firmware loading first tries proprietary firmware, then open firmware, maps core revision and PHY type to microcode/initvals filenames, validates firmware headers, registers the mac80211 hardware, registers LEDs, and optionally registers an hwrng.

Attach-time core discovery powers the bus, resets the core enough to read PHY/radio versioning, determines supported bands, allocates the PHY-specific private state, validates chip access, sets band tables, disables analog, and powers down. Runtime start clears per-instance state, initializes the wireless core if needed, requests IRQs, enables MAC/data flow, starts periodic work, then reloads mac80211 configuration. Stop cancels beacon/TX/txpower work, disables IRQs, frees IRQs, drains TX queues, suspends MAC, releases LED state, exits the PHY/chip, disables the core, and lets the bus power down.

Interrupt flow disables device IRQs in the top half after reading and ACKing generic and DMA reason registers. The thread handles fatal DMA fallback to PIO, firmware debug/panic IRQs, TBTT/ATIM/PMQ/beacon/noise interrupts, RX processing through DMA or PIO, TX status completion, and finally restores the current IRQ mask.

## State and Persistence
Persistent driver state lives in `struct b43_wl` and `struct b43_wldev`: current core, status, interface mode, BSSID/MAC, beacon templates, TX queues, filter flags, QoS parameters, firmware metadata, key slots, IRQ masks/reasons, PHY state, noise samples, and statistics. Firmware blobs are cached in `dev->fw` until core detach, not re-requested on every init. Hardware state is persisted into MMIO registers, shared memory, template RAM, key table memory, and RCMTA. The file uses `wl->mutex` for most lifecycle and mac80211 state, `hardirq_lock` for non-SDIO interrupt top halves, and `beacon_lock` around the current beacon skb.

## Dependencies and Integration Points
- Integrates with mac80211/cfg80211 through `ieee80211_alloc_hw`, `ieee80211_register_hw`, queue control, beacon generation, key callbacks, channel configuration, and survey reporting.
- Depends on b43 subsystems: PHY modules, DMA, PIO, xmit, debugfs, sysfs, LEDs, SDIO, local oscillator, and firmware/initvals definitions.
- Integrates with Linux firmware loading APIs, BCMA/SSB bus control, optional hwrng, rfkill polling, workqueues, SKB queues, and IRQ threading.
- Shares register and SHM contracts with firmware; many helpers write fixed offsets such as host flags, channel cookie, QoS parameter blocks, beacon template metadata, and microcode status registers.

## Risks and Edge Cases
- Firmware filename selection is a large matrix of core revision and PHY type; unsupported or newly added hardware fails with `-EOPNOTSUPP` unless this mapping and versioning logic are updated.
- Hardware key programming differs between old and new key-index APIs; pairwise, default RX, and TKIP phase-1 slots must stay synchronized or decryption can silently fail.
- IRQ stop/start code deliberately unlocks `wl->mutex` around work cancellation and IRQ freeing, so it revalidates `wl->current_dev`; regressions here can race device removal or restart.
- Fatal DMA errors permanently set `dev->use_pio = true` and restart the controller, so repeated DMA faults shift the data path and should be visible in performance and logs.
- Beacon template updates are asynchronous and double-buffered; incorrect valid-bit or IRQ-mask handling can upload partial beacons while firmware is transmitting.
- Power saving is partly stubbed and currently forces awake with hardware power save off, so future power-save work must revisit assumptions in TBTT, PHY locking, and `b43_power_saving_ctl_bits`.
- AC-PHY hardware is accepted by versioning, but the companion AC ops are skeletal; null callbacks used by common init paths are a high-risk integration gap if AC support is enabled.

## Test Signals
- Build coverage should compile BCMA, SSB, SDIO, DMA, PIO, hardware crypto, and each enabled PHY variant.
- Probe/start/stop smoke tests should cover firmware absence, proprietary and open firmware, initvals format errors, IRQ request/free, DMA-to-PIO fallback, and suspend/resume-like stop/start cycles.
- mac80211 tests should exercise add/remove interface, AP/mesh/IBSS beacon updates, channel/band changes, retry limits, QoS parameter updates, hardware key setup/removal, TKIP key refresh, scan start/complete, and rfkill polling.
- Runtime signals include firmware version logs, "Microcode not responding", firmware watchdog/panic, fatal DMA messages, unsupported PHY/radio logs, and survey noise updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/main.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/main.h

## Purpose
`main.h` is the local public interface for the central b43 driver implementation. It exposes logging verbosity state, rate classification helpers, shared-memory/host-flag/TSF accessors, core reset and restart hooks, MAC suspend/enable helpers, power-save flags, firmware request/release helpers, and a padding macro used by b43 structures.

## Important APIs, Types, and Functions
- `enum b43_verbosity` defines error, warning, info, and debug verbosity levels and derives the default from `B43_DEBUG`.
- `b43_modparam_verbose` is exported for other b43 files to honor the module's log level.
- `b43_is_cck_rate()` and `b43_is_ofdm_rate()` classify b43 rate IDs for PLCP, rate table, and template code.
- Declared helpers include `b43_ieee80211_antenna_sanitize`, `b43_tsf_read/write`, SHM read/write, host flag read/write, `b43_dummy_transmission`, wireless core reset, controller restart, power-save control, PLL reset, MAC suspend/enable, MAC/PHY clock control, MAC frequency switching, and firmware request/release functions.
- `B43_PS_*` flags encode requested hardware power-save and awake/asleep state.

## Control Flow
The header has no runtime control flow. It defines callable contracts used by PHY, DMA/PIO, debug, xmit, and other b43 implementation files to reach central `main.c` services.

## State and Persistence
The header declares accessors for persistent hardware and driver state but owns no state itself. The global `b43_modparam_verbose` mirrors the module parameter in `main.c`, while the declared functions mutate hardware registers, shared memory, firmware references, or `struct b43_wldev` state in their implementations.

## Dependencies and Integration Points
- Includes `b43.h`, so it depends on the main b43 device types and rate constants.
- Bridges non-`main.c` modules to shared memory, host flags, TSF, firmware, MAC lifecycle, and power-save primitives.
- The padding macros are intended for structure layout preservation without naming real fields.

## Risks and Edge Cases
- The verbosity enum and module parameter help text must stay synchronized with `main.c`.
- `b43_is_ofdm_rate()` treats every non-CCK value as OFDM; callers must pass only valid b43 rate IDs.
- Power-save flags can express conflicting states; the implementation warns but currently overrides behavior, so callers should not infer full power-save semantics from the header alone.
- Firmware helpers expose low-level request/release mechanics; callers must respect ownership of `struct b43_firmware_file`.

## Test Signals
- Build tests across b43 submodules catch declaration drift.
- Rate helper users should be covered by PLCP and beacon-template tests that include all CCK and OFDM hardware rate IDs.
- Firmware request helper usage should be exercised by missing, malformed, cached, and released firmware cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_a.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_a.h

## Purpose
`phy_a.h` defines A/OFDM PHY register addresses, bit masks, OFDM table selector encodings, and table access function prototypes for b43. It is a register-contract header used by A/G PHY code that needs OFDM baseband, gain, RSSI, TSSI, DAC, antenna diversity, and threshold tables.

## Important APIs, Types, and Functions
- Register macros wrap raw offsets with `B43_PHY_OFDM()` routing from `phy_common.h`.
- Important registers include A-PHY versioning, baseband config, powerdown, CRS thresholds, LNA/HPF and LPF gain controls, antenna dwell/settle, IQ balance, TX DC bias, OFDM table control/data, hardware power TSSI control, ADC control, idle TSSI, temperature sense, NRSSI threshold, clip thresholds, and diversity gain registers.
- OFDM table helpers include `B43_OFDMTAB(number, offset)` and named table selectors such as AGC, gain, noise scale, rotor, DAC, DC, power dynamic, LNA gain, RSSI, TSSI, and revision-specific tables.
- Prototypes provide 16-bit and 32-bit OFDM table read/write access.

## Control Flow
There is no direct control flow. Consumer code writes `B43_PHY_OTABLECTL` with one of the encoded table selectors and then accesses `B43_PHY_OTABLEI/Q` or uses the declared helper functions.

## State and Persistence
The header owns no driver state. It names hardware registers and tables whose values persist in the PHY until changed by init, calibration, channel switching, or power-control routines.

## Dependencies and Integration Points
- Depends on `phy_common.h` for PHY register routing macros and `struct b43_wldev`.
- Used by G-PHY and OFDM/A-PHY code paths for calibration, gain tables, noise/TSSI handling, and antenna-diversity programming.
- The OFDM table accessors are implemented elsewhere and provide the safer integration point for table operations.

## Risks and Edge Cases
- Many names carry FIXME/TODO markers, indicating incomplete hardware documentation; accidental reuse of poorly named registers can create hard-to-debug RF behavior.
- Table selector encodings combine table number and offset bits; wrong offsets can corrupt unrelated OFDM tables.
- Revision-specific table aliases must be chosen carefully because A/G PHY revisions interpret some table numbers differently.

## Test Signals
- Build coverage should include PHY_G/A-OFDM users that include this header.
- RF regression signals include broken channel calibration, bad RSSI/TSSI, degraded OFDM rates, antenna diversity regressions, and unexpected PHY errors after table changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_ac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_ac.c

## Purpose
`phy_ac.c` provides the AC-PHY `struct b43_phy_operations` instance for IEEE 802.11ac Broadcom PHYs. In this snapshot it is a minimal skeleton: it allocates/free AC private state, implements AC-specific PHY mask/set and radio read/write accessors, returns a default channel by band, and stubs TX power recalculation/adjustment.

## Important APIs, Types, and Functions
- `b43_phy_ac_op_allocate()` allocates `struct b43_phy_ac` and stores it in `dev->phy.ac`.
- `b43_phy_ac_op_free()` releases that private state and clears the pointer.
- `b43_phy_ac_op_maskset()` accesses AC PHY registers through `B43_MMIO_PHY_CONTROL` and `B43_MMIO_PHY_DATA`.
- `b43_phy_ac_op_radio_read()` and `b43_phy_ac_op_radio_write()` access radio registers through the newer `B43_MMIO_RADIO24_CONTROL/DATA` path.
- `b43_phy_ac_op_get_default_chan()` chooses channel 11 for 2.4 GHz and channel 36 for 5 GHz.
- `b43_phy_ac_op_recalc_txpower()` returns `B43_TXPWR_RES_DONE`; `b43_phy_ac_op_adjust_txpower()` is empty.
- `b43_phyops_ac` publishes these callbacks to `phy_common.c`.

## Control Flow
`b43_phy_allocate()` selects `b43_phyops_ac` when `dev->phy.type` is `B43_PHYTYPE_AC` and `CONFIG_B43_PHY_AC` is enabled. Common PHY code then calls the vtable during allocation, register access, channel setup, and TX power checks. The implemented AC callbacks are direct MMIO wrappers with no calibration sequence.

## State and Persistence
The only software state owned here is the allocated `struct b43_phy_ac`, currently empty. Hardware state changes occur through the register access callbacks. TX power functions intentionally do not persist calculated state or write hardware values.

## Dependencies and Integration Points
- Includes `b43.h` and `phy_ac.h`.
- Integrated through `struct b43_phy_operations` declared in `phy_common.h`.
- Register constants are supplied by `phy_ac.h`; common lifecycle is driven by `phy_common.c` and `main.c`.

## Risks and Edge Cases
- The operations table lacks several callbacks documented as mandatory in `phy_common.h`, including `prepare_structs`, `init`, `software_rfkill`, `switch_analog`, and `switch_channel`. Common b43 paths call these unconditionally in several places, so AC-PHY enablement can crash or fail without additional implementation.
- TX power control is effectively a no-op, which may be acceptable only for unsupported/skeletal hardware bring-up.
- There is no channel-switch or RF-kill implementation despite AC devices being accepted by versioning and firmware selection in `main.c`.

## Test Signals
- A build with `CONFIG_B43_PHY_AC` should catch type/prototype drift, but runtime probe/start on AC hardware is the critical signal because missing callbacks are not compile-time errors.
- Any AC-PHY start attempt should be watched for null-function-pointer faults, failed PHY init, absent channel switching, and missing rfkill behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_ac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_ac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_ac.h

## Purpose
`phy_ac.h` defines register constants and the private-state shell for b43 AC-PHY support. It also declares the AC-PHY operations table consumed by common PHY allocation.

## Important APIs, Types, and Data
- AC register macros cover baseband config, band control, table ID/offset/data registers, classifier control, bandwidth registers, RF control command, and per-core clip-disable registers.
- Bit masks include reset CCA, 5 GHz band select, CCK/OFDM/waited classifier enables, and clip disable bits for cores 1-3.
- `struct b43_phy_ac` is currently empty.
- `extern const struct b43_phy_operations b43_phyops_ac` exposes the implementation in `phy_ac.c`.

## Control Flow
The header has no executable flow. It provides constants and declarations used when common code dispatches into the AC-PHY vtable.

## State and Persistence
No state is owned in the header. The empty AC private struct creates a typed storage slot under `struct b43_phy`, and the register definitions name persistent AC PHY hardware state.

## Dependencies and Integration Points
- Includes `phy_common.h` for the vtable type and device declarations.
- Used by `phy_ac.c` and by common PHY selection when `CONFIG_B43_PHY_AC` is enabled.
- Register definitions are potential integration points for future AC init, channel, classifier, bandwidth, and RF-control code.

## Risks and Edge Cases
- The empty private state signals incomplete AC support; future code must add fields without assuming old instances carry calibration or channel state.
- Register macros are low-level and do not enforce valid sequencing; table access and RF-control changes should be wrapped by dedicated helpers before broader use.
- The operations declaration can make AC appear supported even while critical callbacks remain absent in the implementation.

## Test Signals
- Build tests with AC-PHY enabled catch declaration drift.
- Runtime AC hardware tests should verify classifier enablement, band switching, table access, RF control, and clipping behavior once implementation grows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_ac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_common.c

## Purpose
`phy_common.c` implements shared PHY/radio lifecycle and register helpers for b43. It selects the PHY-specific operations table, manages PHY init/exit, serializes PHY and radio access against firmware, wraps common read/write/mask operations, handles PHY reset and channel switching, performs software rfkill, schedules TX power adjustment, reads TSSI samples, and provides generic analog/clock helpers.

## Important APIs, Types, and Functions
- `b43_phy_allocate()` maps `dev->phy.type` to the configured `b43_phyops_*` table and invokes the PHY-specific allocate callback.
- `b43_phy_init()` enables analog/radio, invokes the PHY init callback, marks full init complete, then switches to the current channel.
- `b43_phy_exit()` soft-blocks RF, marks full init required, and invokes optional PHY exit.
- `b43_radio_lock/unlock()` and `b43_phy_lock/unlock()` coordinate register access with firmware and power-save state.
- `b43_radio_read/write/mask/set/maskset()` and `b43_phy_read/write/copy/mask/set/maskset()` provide common register access with debug checks and PCI write flushes after `B43_MAX_WRITES_IN_ROW`.
- `b43_phy_put_into_reset()` and `b43_phy_take_out_of_reset()` implement BCMA/SSB-specific reset sequencing.
- `b43_switch_channel()` writes the firmware channel cookie, invokes PHY-specific channel switching, waits for stabilization, and restores the old cookie on failure.
- `b43_software_rfkill()`, `b43_phy_txpower_check()`, `b43_phy_txpower_adjust_work()`, `b43_phy_shm_tssi_read()`, `b43_phyop_switch_analog_generic()`, `b43_is_40mhz()`, and `b43_phy_force_clock()` implement shared radio/power helpers.

## Control Flow
The common lifecycle is allocate, prepare/init through callbacks, channel switch, normal register operations, exit, and free. Most functions dispatch through `dev->phy.ops`, falling back to generic MMIO access for PHY reads/writes when a specific callback is absent. Channel switching first updates the shared-memory channel value visible to firmware, then asks the PHY implementation to tune hardware; if tuning fails, the SHM value is rolled back.

## State and Persistence
State is held in `dev->phy`: selected vtable, per-PHY private pointer, band support, current channel definition, radio state, TX power scheduling, write counter, and debug lock flags. Hardware state is persisted through MMIO, BCMA/SSB core control registers, PHY/radio registers, shared-memory channel/TSSI values, and MAC power-save bits. TX power adjustment is deferred through `wl->txpower_adjust_work` and throttled by `next_txpwr_check_time`.

## Dependencies and Integration Points
- Includes all PHY headers and selects ops conditionally by `CONFIG_B43_PHY_*`.
- Depends on `main.h` for MAC suspend/enable, shared memory, power-saving, and workqueue helpers.
- Integrates with BCMA and SSB bus reset/clock controls and mac80211 workqueue scheduling.
- Provides shared helpers used by G, N, LP, HT, LCN, and AC PHY implementations.

## Risks and Edge Cases
- Several vtable callbacks are called unconditionally despite being documented as mandatory only in comments; incomplete PHY implementations can crash at runtime.
- Debug-only `assert_mac_suspended()` reports but does not prevent register access with the MAC enabled; production builds rely on caller discipline.
- The channel cookie is written before hardware tuning, so failures must restore it correctly to avoid firmware/hardware channel mismatch.
- TSSI reads reject zero and `B43_TSSI_MAX` sentinel values and clear consumed samples; callers must handle `-ENOENT` without treating it as a fatal RF error.
- `b43_software_rfkill()` suspends/enables MAC around the PHY callback, so nested MAC suspend counters and callback behavior must remain balanced.

## Test Signals
- PHY allocation/init tests should cover each enabled PHY type and unsupported/missing config combinations.
- Register access tests should exercise generic and PHY-specific read/write/maskset paths, especially write-flush behavior on PCI.
- Runtime signals include PHY init failure logs, failed channel switches, rfkill toggles, TX power adjustment scheduling, and TSSI sample availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_common.h

## Purpose
`phy_common.h` defines the shared PHY abstraction for b43. It provides register routing macros, version masks, antenna and interference enums, TX power result/flag enums, the `struct b43_phy_operations` vtable, the central `struct b43_phy` state container, and prototypes for common PHY/radio lifecycle and register helpers.

## Important APIs, Types, and Data
- Register routing macros (`B43_PHY_CCK`, `B43_PHY_N`, `B43_PHY_N_BMODE`, `B43_PHY_OFDM`, `B43_PHY_EXTG`) encode PHY register spaces.
- Version masks decode analog type, PHY type, and PHY revision from the version register.
- `enum b43_interference_mitigation` and antenna identifiers define cross-PHY control values.
- `enum b43_txpwr_result` and `enum b43_phy_txpower_check_flags` describe TX power recalculation and scheduling.
- `struct b43_phy_operations` is the PHY vtable for allocation, preparation, init/exit, PHY/radio access, hardware power control, rfkill, analog switching, channel switching, antenna selection, interference mitigation, TX power, and periodic work.
- `struct b43_phy` stores the chosen vtable, per-PHY private pointer union, band support, gmode, full-init state, versioning, radio state, desired TX power, current channel definition, TX error counter, and optional debug locks.
- Function prototypes expose allocation/free/init/exit, PHY/radio register helpers, firmware-lock helpers, reset sequencing, channel switching, software rfkill, TX power work, TSSI reads, generic analog switching, 40 MHz check, and forced PHY clock.

## Control Flow
The header declares the vtable-driven PHY flow implemented in `phy_common.c` and PHY-specific files: select ops, allocate private state, optionally prepare structures/hardware, initialize, switch channels, perform periodic maintenance, adjust TX power, then exit and free. Register helpers centralize callers through common wrappers even when a PHY supplies custom low-level access.

## State and Persistence
`struct b43_phy` is persistent per wireless device and is reset/reinitialized across core lifecycle transitions. Its fields bridge software scheduling state, RF/hardware identity, current channel configuration, and debug access tracking. The header also defines constants for persistent hardware registers and shared behaviors but stores no data itself.

## Dependencies and Integration Points
- Includes Linux basic types and cfg80211/nl80211 channel definitions.
- Forward-declares `struct b43_wldev` and per-PHY private structs to avoid heavy include coupling.
- Used by every PHY implementation and by `main.c` for lifecycle, band support, rfkill, channel switching, and TX power management.

## Risks and Edge Cases
- Documentation says several vtable callbacks must not be NULL, but the type system does not enforce this; common code assumes many callbacks exist.
- The per-PHY private pointer is a union outside debug builds, so using the wrong member can alias silently.
- `struct cfg80211_chan_def *chandef` points into mac80211 configuration; callers must keep it valid across channel changes and initialization.
- Antenna constants are sparse (`B43_ANTENNA3 = 8`), so code must not treat them as dense array indices.
- Deprecated aliases `b43_radio_read16/write16` preserve old call sites but can obscure modernization work.

## Test Signals
- Compile all configured PHY variants to catch vtable and struct changes.
- Runtime coverage should include PHY allocation/free, init/exit, rfkill, channel switch, TX power check/adjust scheduling, TSSI reads, 40 MHz detection, and debug lock assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_common.h -->
