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
