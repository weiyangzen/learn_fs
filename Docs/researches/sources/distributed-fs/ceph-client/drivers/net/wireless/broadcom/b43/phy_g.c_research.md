# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_g.c

## Purpose

`phy_g.c` implements the Broadcom b43 IEEE 802.11g PHY operation backend. It owns G-PHY allocation, reset-time structure preparation, baseband/radio initialization, 2050 radio calibration, channel switching, software RF kill, antenna diversity, adjacent-channel interference mitigation, TSSI to dBm conversion, software TX-power recalculation, and periodic G-PHY maintenance hooks. It is selected through `b43_phyops_g` and is the procedural counterpart to the register/state definitions in `phy_g.h`.

The file is highly hardware-specific. Most behavior is direct programming of PHY, radio, shared-memory, host-flag, and OFDM/G-PHY table registers through b43 core accessors. The source also keeps reverse-engineered workarounds for old 4306/2050 combinations, power-control quirks, PPC machine-check avoidance, and Japan channel 14 handling.

## Important APIs, Types, and Functions

- `const struct b43_phy_operations b43_phyops_g` is the driver-facing operation table. It wires allocation/free, prepare/init/exit, PHY/radio accessors, hardware power-control capability, RF kill, generic analog switching, channel switching, default channel, RX antenna selection, interference mitigation, TX-power recalc/adjust, and 15/60 second periodic work.
- `b43_gphy_op_allocate()` allocates `struct b43_phy_g` plus `struct b43_txpower_lo_control`, initializes the TSSI-to-dBm table, and stores the result in `dev->phy.g`.
- `b43_gphy_op_prepare_structs()` zeroes volatile state while preserving the allocated TSSI table and LO-control pointer. It initializes NRSSI sentinel values, the LO calibration list, OFDM table cache direction, average TSSI, default interference mode, and invalid calibration sentinels.
- `b43_phy_initg()`, `b43_phy_initb5()`, `b43_phy_initb6()`, `b43_phy_inita()`, and `b43_radio_init2050()` form the initialization core. They program revision-specific baseband/radio registers, run loopback/LO/radio calibrations, populate lookup tables, initialize power control, and apply workarounds.
- `b43_gphy_channel_switch()` writes the b/g channel code to `B43_MMIO_CHANNEL`, optionally runs the synthetic power-up workaround, and handles channel 14 host-flag/channel-extension behavior.
- `b43_set_txpower_g()`, `b43_gphy_op_recalc_txpower()`, `b43_gphy_op_adjust_txpower()`, `b43_put_attenuation_into_ranges()`, and `b43_generate_dyn_tssi2dbm_tab()` implement the software TX-power loop around TSSI, attenuation, LO bias/magnification, and SPROM power limits.
- `b43_calc_nrssi_offset()`, `b43_calc_nrssi_slope()`, `b43_calc_nrssi_threshold()`, and `b43_nrssi_mem_update()` maintain NRSSI calibration state and thresholds used for RSSI and interference decisions.
- `b43_radio_interference_mitigation_enable()` and `_disable()` save and restore stacks of PHY/radio/table registers for non-WLAN and manual WLAN interference mitigation modes.
- `b43_gphy_op_software_rfkill()` stores and restores RF override registers when the radio is powered down/up through the software RF kill path.

## Control Flow

Common b43 PHY setup calls `allocate`, then `prepare_structs`, then `prepare_hardware`, and finally `init`. `prepare_hardware` computes default baseband/radio attenuation, default TX control, RF/baseband attenuation lists, commits pending writes, and performs a special revision-1 reset sequence that temporarily disables `gmode`. `init` calls `b43_phy_initg()`, which selects the B5 or B6 baseband path, applies A/G common initialization when required, initializes loopback gain, runs radio 2050 calibration once or restores the cached calibration value, initializes LO state, calculates NRSSI state, initializes power control, and applies chip-specific OFDM restrictions.

Channel switching is intentionally small but side-effectful. The public callback validates channels 1..14, then writes the channel code through `b43_gphy_channel_switch()`. That helper may briefly tune to another channel for the synthetic power-up workaround, then writes `B43_MMIO_CHANNEL`. Channel 14 also toggles `B43_HF_ACPR` depending on SPROM country code and sets an extension-register bit; other channels clear the channel-14 related bits.

TX-power recalculation is two phase. `recalc_txpower` reads CCK and OFDM TSSI values from shared memory, merges them with `gphy->average_tssi`, estimates emitted power using `gphy->tssi2dbm`, clamps the requested power against SPROM maximums, and stores attenuation deltas if a change is needed. `adjust_txpower` later suspends the MAC, folds the deltas into current RF/baseband attenuation, applies radio-revision-specific `tx_control` transitions, locks PHY/radio access, calls `b43_set_txpower_g()`, and re-enables the MAC.

Periodic work also runs through the operations table. The 15-second path suspends the MAC, contains mostly placeholder ACI automation logic, and runs LO maintenance. The 60-second path recalculates NRSSI slope for boards with RSSI calibration data and performs a VCO channel hop on radio 2050 revision 8.

## State and Persistence

All persistent runtime state is in `dev->phy.g` and in the associated LO-control object. It is volatile kernel driver state, not on-disk persistence. The most important fields are current attenuation (`bbatt`, `rfatt`, `tx_control`), pending TX-power deltas, LO-control pointer/list, current/target/average TSSI, dynamic/static TSSI table selection, NRSSI slope/samples/lookup table, loopback gain components, interference mode and saved-register stack, cached OFDM-table address direction, RF kill saved override registers, and cached 2050 radio calibration value.

The code carefully saves and restores raw hardware registers around calibration, interference mitigation, and loopback measurement. Some saves are stored only on the stack within one function; longer-lived state such as `radio_off_context`, `interfstack`, `initval`, `lofcal`, and LO calibration lists persists across callbacks. `prepare_structs()` resets most runtime values but preserves allocation-owned pointers and tables.

Dynamic TSSI tables are allocated from SPROM PA coefficients and freed only when `dyn_tssi_tbl` is true. Static fallback table `b43_tssi2dbm_g_table` is shared and not freed. Allocation cleanup follows explicit error labels to avoid leaking LO or G-PHY state on partial failure.

## Dependencies and Integration Points

`phy_g.c` includes `b43.h`, `phy_g.h`, `phy_common.h`, `lo.h`, `main.h`, `wa.h`, and Linux `bitrev`/`slab`. It depends on core b43 MMIO, PHY, radio, OFDM-table, host-flag, shared-memory, dummy-transmission, MAC suspend/enable, channel-switch, and debug/error helpers. It also depends on SPROM fields such as PA coefficients, board flags, board vendor/type/revision, country code, max power, and idle TSSI.

The operation table is consumed by the b43 PHY dispatcher for G-PHY devices. LO-specific routines in `lo.c`, common A-PHY register definitions in `phy_a.h`, and common PHY operations in `phy_common.c` are tightly coupled to this file. Firmware/shared-memory integration appears in TSSI clearing and reading, RF attenuation shared-memory writes, and host-flag toggles for hardware power control and interference handling.

## Risks and Edge Cases

- The file is full of revision, radio, board, and SPROM conditionals. Regressions are likely if a change is tested on only one 2050 radio revision or only one board flag combination.
- Several paths use `B43_WARN_ON(1)` for unexpected register mode or revision combinations but continue with fallback values, which can mask unsupported hardware states.
- Register save/restore order is critical during NRSSI, loopback, radio calibration, and interference mitigation. Missing a restore can leave the radio deaf, overpowered, or miscalibrated.
- The interference stack is a fixed 26-entry packed array with comments noting it should be a data structure. Adding saved registers without increasing the size risks stack overflow warnings and failed restore.
- TX-power control mixes Q5.2 fixed point, SPROM values, RF/baseband attenuation ranges, and radio-revision-specific `tx_control` transitions. Off-by-one or sign errors can affect regulatory power behavior.
- ACI automation in `pwork_15sec` is largely TODO-gated; the manual and non-WLAN modes exist, but automatic mode is incomplete.
- Channel 14 and country-code handling is special and easy to break because it affects host flags and channel-extension bits in addition to the channel code.

## Test Signals

Useful validation signals include successful probe/init on representative G-PHY revisions, no allocation leaks on forced `kmalloc` failures, correct channel switch return values for channels 1..14 and `-EINVAL` outside that range, stable RF kill off/on cycles with `radio_off_context` restored, no MAC/PHY lock warnings around TX-power adjustment, TSSI shared-memory reads causing expected `B43_TXPWR_RES_*` transitions, and debug logs for TX power showing bounded attenuation changes. Hardware smoke tests should cover radio 2050 rev 8, non-rev8 2050, channel 14 country handling, boards with and without `B43_BFL_RSSI`, and interference mode enable/disable restore behavior.
