# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_n.h

## Purpose
`phy_n.h` is the N-PHY hardware contract for the B43 Broadcom wireless driver. It defines the register offsets and bit masks used by `phy_n.c` to initialize, tune, calibrate, and operate 802.11n PHY hardware, and it declares the N-PHY private state carried in `struct b43_phy_n`. It also publishes the N-PHY operation table symbol `b43_phyops_n` for the broader driver PHY dispatch layer.

## Important APIs, Types, And Definitions
- Register map: `B43_NPHY_*` constants cover baseband config, channel selection, band control, RF control sequences, RSSI/TSSI, IQ estimation, TX power control, radar detection, classifier, BPHY compatibility, GPIO, revision-3-plus, and revision-7 RF-control registers. Most constants wrap `B43_PHY_N()` or `B43_PHY_N_BMODE()` from `phy_common.h`.
- Bit fields: many registers include masks and shift constants such as `B43_NPHY_RFCTL_CMD_*`, `B43_NPHY_TXPCTL_CMD_*`, `B43_NPHY_TXPCTL_*`, `B43_NPHY_IQEST_*`, `B43_NPHY_CLASSCTL_*`, and gain/min/max masks for both cores.
- `enum b43_nphy_spur_avoid`: declares disable, automatic, and forced spur-avoidance policies.
- `struct b43_chanspec`: stores a center frequency and `enum nl80211_channel_type` width/sideband type. N-PHY caches use this to determine whether calibration data matches the current channel.
- `struct b43_phy_n_iq_comp`, `struct b43_phy_n_rssical_cache`, and `struct b43_phy_n_cal_cache`: hold cached IQ, RSSI, TX-calibration radio registers, and PHY coefficients for 2.4 GHz and 5 GHz bands.
- `struct b43_phy_n_txpwrindex`: tracks per-core TX power index state plus saved AFE, radio gain, BB multiplier, IQ, LO compensation, and internal index values.
- `struct b43_phy_n_pwr_ctl_info`: records idle TSSI per band.
- `struct b43_phy_n`: the central N-PHY state block embedded under `dev->phy.n`. It persists calibration flags and caches, TX/RX chain state, TX power state, spur workarounds, classifier/clip saved state, IQ/RSSI channel specs, cached PPR limits, and board/radio capability booleans.
- External symbol: `extern const struct b43_phy_operations b43_phyops_n;` integrates the N-PHY implementation into the generic PHY operation dispatcher.

## Control Flow And State
This header has no executable control flow, but it shapes nearly every N-PHY control path. `phy_n.c` reads and writes the register constants during PHY init, channel switching, RSSI/IQ/TX calibration, TX power recalculation, radio setup, and workaround paths. State in `struct b43_phy_n` persists across those calls while the wireless device object is alive.

Calibration persistence is held in `cal_cache`, `rssical_cache`, `iqcal_chanspec_*`, and `rssical_chanspec_*`. TX power persistence is held in `tx_pwr_max_ppr`, `tx_pwr_last_recalc_freq`, `tx_pwr_last_recalc_limit`, `tx_pwr_idx`, `tx_power_offset`, `adj_pwr_tbl`, `txpwrindex[]`, `txcal_bbmult`, and `txiqlocal_*`. PHY/radio chain state is represented by `phyrxchain`, `hw_phyrxchain`, `hw_phytxchain`, `txrx_chain`, saved TX/RX calibration registers, and RF-control save registers. Workaround and mode flags include `hang_avoid`, `mute`, `spur_avoid`, `aband_spurwar_en`, `gband_spurwar_en`, `ipa2g_on`, `ipa5g_on`, `crsminpwr_adjusted`, and `noisevars_adjusted`.

## Dependencies And Integration Points
- Depends on `phy_common.h` for PHY register-address macros and on `ppr.h` for `struct b43_ppr`.
- Depends indirectly on mac80211 channel typing through `enum nl80211_channel_type`.
- Consumed heavily by `phy_n.c`, which uses `B43_NPHY_*` constants for register programming and embeds `struct b43_phy_n` as the N-PHY private data contract.
- Shares radio integration with `radio_2055.h`, `radio_2056.h`, and N-PHY table helpers. The channel/radio register constants in this header must line up with the radio tables and `phy_n.c` sequencing.
- `tx_pwr_max_ppr` connects this header to `ppr.c`/`ppr.h`; `phy_n.c` clears, loads, clamps, and adjusts that per-rate power table during TX power limit recalculation.

## Risks
- Register-map drift is the main risk. A wrong offset, mask, or shift can silently misprogram RF, power, radar, gain, or calibration hardware.
- Revision-specific aliases are easy to misuse. Several register addresses are reused with `REV3` and `REV7` names, so callers must gate them correctly by PHY/core revision.
- `struct b43_phy_n` is large and stateful. Missing reset, stale calibration channel specs, or incorrect save/restore of register snapshots can cause failures that only appear after band changes, suspend/resume, or calibration retries.
- Power-control fields are safety-sensitive because they feed hardware TX power decisions. Incorrect PPR, TSSI, base-index, or offset state can violate regulatory or board limits.
- This header does not enforce locking. Callers must preserve existing driver synchronization around hardware state mutation.

## Test Signals
- Build-time signals: all users should compile with no undefined register/type references after changes; `ppr.c` also has a `BUILD_BUG_ON` that protects the `struct b43_ppr` layout used here.
- Runtime signals: successful N-PHY device probe, channel changes across 2.4 GHz and 5 GHz, calibration completion, stable TX power recalculation, no PHY/RF warnings, and no regressions in mac80211 association/traffic.
- Hardware-focused tests should exercise PHY revisions that use rev3 and rev7 aliases, both chains, 20/40 MHz channel types, spur-avoidance toggles, and suspend/resume or radio reset paths.
