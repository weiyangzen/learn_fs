# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_ht.c

## Purpose

`phy_ht.c` implements the b43 HT-PHY backend for Broadcom 802.11n-era devices. It focuses on BCMA bus devices with 2059 radio hardware. The file handles HT PHY allocation, table upload, radio 2059 initialization, RF sequencing, channel setup through HT channel tables, CCA reset, per-core AFE/RSSI/sample control, TSSI measurement, and per-core TX power-control register setup.

The exported `b43_phyops_ht` table integrates this backend with the common b43 PHY layer. Several callbacks are placeholders or minimal implementations, reflecting that this HT support is incomplete compared with the older G-PHY path.

## Important APIs, Types, and Functions

- `const struct b43_phy_operations b43_phyops_ht` wires allocation/free, prepare/init, PHY maskset, radio read/write, software RF kill, analog switching, channel switching, default channel, and TX-power callbacks.
- `b43_phy_ht_op_allocate()`, `_prepare_structs()`, and `_free()` manage `struct b43_phy_ht`, initialize TX power control as enabled, mark per-core TX power index as invalid, and initialize saved baseband multipliers to `-1`.
- `b43_phy_ht_op_init()` is the main initialization sequence. It verifies BCMA, uploads HT tables, clears and programs many PHY/HT table registers, initializes AFE, performs RF sequences, optionally initializes B-PHY compatibility registers for 2 GHz, and configures TX power control.
- `b43_radio_2059_init()`, `_init_pre()`, `_rcal()`, `_rccal()`, and `b43_radio_2059_channel_setup()` program and calibrate the 2059 radio using data from `radio_2059.h` and `tables_phy_ht.h`.
- `b43_phy_ht_set_channel()`, `_channel_setup()`, and `_spur_avoid()` select channel-table entries, program bandwidth registers, toggle 2/5 GHz band control, reset B-PHY as needed, update classifier bits, and update BCMA PLL spur avoidance.
- `b43_phy_ht_force_rf_sequence()` triggers RF state-machine sequences and polls for completion.
- `b43_phy_ht_tx_power_ctl_idle_tssi()`, `_setup()`, `_ctl()`, `_tssi_setup()`, and `_tx_power_fix()` configure per-core TSSI and target-power state based on SPROM core power information.
- `b43_phy_ht_load_samples()`, `_run_samples()`, `_stop_playback()`, and `_tx_tone()` support sample playback used for idle TSSI measurement.
- `b43_phy_ht_rssi_select()` and `_poll_rssi()` configure per-core RSSI/TSSI selection and collect signed 6-bit RSSI samples.

## Control Flow

The driver enters through `b43_phyops_ht`. Allocation installs `dev->phy.ht`; preparation resets it and seeds default TX power-control state. Initialization rejects non-BCMA devices, loads PHY tables, programs baseband/AFE/classifier registers, copies selected HT table values, resets CCA, enables the MAC/PHY clock, forces RX2TX and reset-to-RX RF sequences around PA override state, initializes B-PHY compatibility logic for 2 GHz, writes late HT table data, then temporarily disables TX power control while it measures idle TSSI and programs per-core power-control tables.

RF kill is asymmetric. Blocking clears the radio power-up bit in `B43_PHY_HT_RF_CTL_CMD`; unblocking reinitializes radio 2059 when present and switches back to the current channel. The function expects the MAC to be suspended and logs an error if it is not.

Channel switching is routed through the current mac80211 channel definition, not directly through the `new_channel` value except for validation. Only 2 GHz validation is implemented in `b43_phy_ht_op_switch_channel`; 5 GHz currently returns `-EINVAL` there even though lower-level setup code has 5 GHz register paths. `b43_phy_ht_set_channel()` supports only radio version `0x2059` and returns `-ESRCH` if no channel-table entry exists.

TX power control is mostly an initialization-time hardware setup. Recalculation returns `B43_TXPWR_RES_DONE` and adjustment is empty. The setup path computes target powers and PA polynomial coefficients from SPROM `core_pwr_info` for 2 GHz and 5 GHz low/mid/high bands, writes target and idle TSSI registers, and bulk-writes 64-entry per-core power tables.

## State and Persistence

`struct b43_phy_ht` persists under `dev->phy.ht` until free. It stores:

- `rf_ctl_int_save[3]` for PA override save/restore around forced RF sequences.
- `tx_pwr_ctl` as the desired software view of hardware TX power-control enablement.
- `tx_pwr_idx[3]` as saved per-core power-control indices when disabling/enabling hardware control.
- `bb_mult_save[3]` as saved baseband multipliers restored after sample playback.
- `idle_tssi[3]` as per-core idle TSSI values measured by sample playback and later programmed into power-control registers.

Most other state is transient in hardware registers and tables. The file frequently saves local register arrays around RSSI polling and idle TSSI measurement, then restores them before returning. The channel tables are static data supplied by `tables_phy_ht`/`radio_2059`.

## Dependencies and Integration Points

The file includes `b43.h`, `phy_ht.h`, `tables_phy_ht.h`, `radio_2059.h`, and `main.h`. It depends on Linux allocation, BCMA chipcommon/PMU/PLL helpers, mac80211 channel/band state, SPROM per-core power data, b43 PHY/radio/table helpers, MAC/PHY clock helpers, and common RF/channel dispatch.

`b43_phy_ht_get_channeltab_e_r2059()`, `b43_phy_ht_tables_init()`, `b43_httab_*()` helpers, and `r2059_upload_inittabs()` are key external table/radio dependencies. `b43_phyops_ht` is consumed by the common PHY dispatcher for HT PHY hardware.

## Risks and Edge Cases

- HT-PHY is explicitly limited to BCMA in init. Non-BCMA devices fail with `-EOPNOTSUPP`.
- Many TODO/FIXME markers remain: unconditional radio calibration, uncertain 5 GHz PA override value, unverified AFE masks, sample command mask uncertainty, incomplete RSSI selection types, questionable table index `40`, and uncertain spur avoidance scope.
- RF sequence waits sleep or poll with fixed limits and only log on timeout. A timeout may leave hardware in an unexpected state.
- `b43_phy_ht_op_switch_channel()` rejects 5 GHz at the operation boundary despite lower-level band-control support.
- Recalc/adjust TX-power callbacks are stubs, so runtime power correction depends on the hardware setup rather than a software feedback loop.
- RSSI selection for core off and most RSSI types is unimplemented and logs errors.
- Channel switching ignores `new_channel` except validation and uses the current chandef pointer, so caller ordering matters.

## Test Signals

Validation should include BCMA HT hardware with 2059 radio, successful table upload, radio init without `rcal`/`rccal` timeout logs, RF sequence completion without timeout, channel table lookup success for supported channels, CCA reset after spur avoidance, and idle TSSI values populated for all three cores. Compile tests should cover `CONFIG_B43_PHY_HT`. Runtime tests should verify RF kill requires MAC suspension, 2 GHz channel switches work through mac80211 chandef state, 5 GHz behavior is either intentionally rejected or fixed, and no HT sample playback leaves stale `bb_mult_save` state.
