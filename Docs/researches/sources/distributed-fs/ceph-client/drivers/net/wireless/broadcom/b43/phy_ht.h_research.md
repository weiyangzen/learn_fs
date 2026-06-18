# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_ht.h

## Purpose

`phy_ht.h` defines the register map, small data structures, and exported operation table declaration for b43 HT-PHY support. It is the shared hardware contract used by `phy_ht.c` and HT table/channel code.

The file names baseband, band-control, table-access, classifier, sample-playback, TSSI, bandwidth, TX power-control, RSSI, RF sequence, RF control, AFE, and B-PHY compatibility registers. It also defines the per-channel PHY register tuple used by radio 2059 channel tables and the per-device HT state block.

## Important APIs, Types, and Register Groups

- `B43_PHY_HT_BBCFG` plus `RSTCCA` and `RSTRX` bits control HT baseband reset behavior.
- `B43_PHY_HT_BANDCTL` and `B43_PHY_HT_BANDCTL_5GHZ` select 2 GHz versus 5 GHz operation.
- `B43_PHY_HT_TABLE_ADDR`, `B43_PHY_HT_TABLE_DATALO`, and `B43_PHY_HT_TABLE_DATAHI` provide HT table access.
- `B43_PHY_HT_CLASS_CTL` and its CCK/OFDM/waited bits gate the PHY classifier.
- `B43_PHY_HT_SAMP_*` and `B43_PHY_HT_IQLOCAL_CMDGCTL` control sample playback and IQ-local command behavior.
- `B43_PHY_HT_TSSIMODE`, `B43_PHY_HT_TXPCTL_*`, and `B43_PHY_HT_TX_PCTL_STATUS_*` define per-core TSSI/TX power-control registers and bit fields.
- `B43_PHY_HT_RSSI_C1`, `_C2`, and `_C3` expose per-core RSSI sample registers.
- `B43_PHY_HT_BW1` through `B43_PHY_HT_BW6` are the channel-dependent PHY bandwidth values.
- `B43_PHY_HT_RF_SEQ_*` registers and bits control the RF state machine.
- `B43_PHY_HT_AFE_*` and `B43_PHY_HT_RF_CTL_INT_*` name per-core analog/RF control override registers.
- `B43_PHY_B_BBCFG` and `B43_PHY_HT_TEST` cover B-PHY compatibility behavior used when HT operates in 2 GHz.
- `struct b43_phy_ht_channeltab_e_phy` groups six bandwidth register values supplied by HT channel tables.
- `struct b43_phy_ht` stores per-device HT runtime state.
- `extern const struct b43_phy_operations b43_phyops_ht` exports the HT operation table.

## Control Flow and Integration

The header is included by `phy_ht.c`, which consumes nearly every register definition during init, RF sequencing, channel switching, sample playback, RSSI polling, and TX power setup. `radio_2059.h` channel entries embed `struct b43_phy_ht_channeltab_e_phy`, allowing a radio-channel table lookup to return both radio synthesizer values and the PHY bandwidth tuple required by `b43_phy_ht_channel_setup()`.

Common b43 PHY dispatch uses `b43_phyops_ht` for HT PHY devices when the build enables HT support. The state structure is hung from `dev->phy.ht` and initialized by the HT operation callbacks.

## State and Persistence

`struct b43_phy_ht` is volatile per-device state. It contains:

- `rf_ctl_int_save[3]`, used to preserve per-core RF control interrupt/PA override registers while forcing RF sequences.
- `tx_pwr_ctl`, the software-desired enable state for hardware TX power control.
- `tx_pwr_idx[3]`, saved/restored per-core TX power-control index values.
- `bb_mult_save[3]`, saved baseband multipliers used by sample playback and restored by `b43_phy_ht_stop_playback()`.
- `idle_tssi[3]`, measured per-core idle TSSI values used by power-control setup.

This state is reset in `prepare_structs()`, not persisted across device teardown, and must remain consistent with the register layouts in the same header.

## Dependencies

The header includes `phy_common.h` for b43 PHY declarations and register encoding helpers. It relies on kernel integer types and b43's `B43_PHY_OFDM()`, `B43_PHY_EXTG()`, and `B43_PHY_N_BMODE()` macros. It is coupled to `tables_phy_ht.h` and `radio_2059.h` because channel-table entries carry `struct b43_phy_ht_channeltab_e_phy` values.

## Risks and Edge Cases

- Register constants are raw hardware ABI. Incorrect masks in the header can cause broad hardware misconfiguration.
- TX power-control bit definitions are shared by three cores but some masks are named with C1 even when reused for C2/C3. Callers must be clear about which registers have identical bit layouts.
- `bb_mult_save` uses signed sentinel behavior in `phy_ht.c`; it is declared `s32`, so changing type would break the `-1` invalid marker.
- The header exposes 5 GHz band-control and target-power fields, but current operation-level channel switching in `phy_ht.c` rejects 5 GHz. Tests should catch any mismatch between declared capability and callback behavior.

## Test Signals

Compile tests should verify HT support with `phy_ht.c`, `tables_phy_ht.c`, and `radio_2059.h`. Runtime signals include clean writes to HT table data ports, correct B-PHY reset behavior when switching bands, per-core idle TSSI capture, RF sequence completion, and TX power-control register writes matching the bit masks defined here.
