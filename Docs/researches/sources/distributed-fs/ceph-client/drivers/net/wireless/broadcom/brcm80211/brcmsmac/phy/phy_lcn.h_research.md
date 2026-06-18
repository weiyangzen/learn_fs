# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_lcn.h

## Purpose
`phy_lcn.h` defines `struct brcms_phy_lcnphy`, the LCNPHY-specific private state block referenced by `struct brcms_phy`. It stores SPROM-derived calibration inputs, LCN runtime calibration state, transmit-power-control state, RSSI/TSSI parameters, gain/table offsets, PAPD/IQ/LO calibration results, channel and spur state, noise settings, and saved user target values.

The header is data-only. It has no functions and is intended for internal PHY implementation use rather than public MAC-layer consumers.

## Important APIs, Types, and Fields
- `struct brcms_phy_lcnphy`: allocated by `wlc_phy_attach_lcnphy()` and freed by `wlc_phy_detach_lcnphy()`.
- Calibration fields: `lcnphy_full_cal_channel`, `lcnphy_cal_counter`, `lcnphy_cal_temper`, `lcnphy_recal`, and embedded `lcnphy_cal_results`.
- SPROM/power fields: `lcnphy_mcs20_po`, TR isolation fields, `lcnphy_rx_power_offset`, `lcnphy_pa0b0/1/2`, `lcnphy_rawtempsense`, `lcnphy_measPower`, `lcnphy_tempsense_slope`, `lcnphy_freqoffset_corr`, `lcnphy_tempsense_option`, and `lcnphy_tempcorrx`.
- RSSI/TSSI fields: RSSI VF/VC/GS values and low/high-temperature copies, `lcnphy_tssi_val`, `lcnphy_tssi_tx_cnt`, `lcnphy_tssi_idx`, and `lcnphy_tssi_npt`.
- Gain and RX-power fields: gain-index table words, OFDM/DSSS gain table offsets, TR gain values, input-power offset, medium/very-low gain dB values, last sensed temperature, and packet-engine RSSI slope.
- Runtime TX/radio state: target TX frequency, TX power override index, current index, noise sample count, spur mode, bandedge correction, hardware IQ calibration enable, IQ calibration swap disable, PAPD/PSAT/LO state, digital filter type fields, ACI state, and `lcnphy_tx_power_offset[]`.

## Control Flow
Attach zero-allocates this structure. `wlc_phy_txpwr_srom_read_lcnphy()` then copies SPROM values into power, RSSI, PA, temperature, and calibration fields. Init and channel paths update bandedge, spur, filter, AGC, and current TX index fields. Power-control paths update TSSI counters, current index, override index, and temperature compensation state. Calibration paths write TX IQ/LO and RX IQ results into `lcnphy_cal_results`.

Common PHY code accesses it through `pi->u.pi_lcnphy` only for LCN PHY instances.

## State and Persistence Behavior
All fields are runtime cache/state for one attached PHY. Values originate from zeroed allocation, SPROM, static table reads, hardware measurements, and calibration results. They are not persisted across detach, reset, driver reload, or reboot. Some fields mirror hardware registers or table values and must be refreshed after hardware reinitialization.

## Dependencies and Integration Points
- Includes `types.h`.
- Depends on `TXP_NUM_RATES` and `struct lcnphy_cal_results` being visible through include order, normally via `phy_int.h`.
- Populated and consumed mainly by `phy_lcn.c`.
- Referenced by common code in `phy_cmn.c` for LCN packet RSSI correction.
- Tied to SPROM fields, LCN tables, and BCM2064 radio/PHY register programming.

## Risks and Edge Cases
- The header relies on external definitions without including the header that declares them; include-order mistakes can break compilation.
- Narrow signed/unsigned fields hold hardware-derived calibration values, so sign conversion and overflow are easy failure modes.
- Several PAPD/ACI/PSAT fields appear partially implemented or auxiliary, making stale state possible.
- Many fields default to zero after allocation, but zero can also be a valid hardware/calibration value; only some subfields have explicit validity flags.
- `lcnphy_saved_tx_user_target[]` duplicates common TX target state and could diverge from `pi->tx_user_target[]`.

## Test Signals
- Compile tests covering every include path that uses `phy_lcn.h`.
- Attach/SPROM tests confirming expected field population.
- Init tests confirming defaults such as filter type and noise sample setup.
- Calibration tests inspecting `lcnphy_cal_results`.
- Power-control tests tracking current index, override index, TSSI index, and NPT across mode transitions.
- RSSI/noise tests validating RSSI slope/offset and gain-related fields after measurement paths.
