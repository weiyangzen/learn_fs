<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phytbl_lcn.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phytbl_lcn.c

## Purpose

`phytbl_lcn.c` is the LCN-PHY static table bank. It contains immutable numeric tables for receive gain, auxiliary gain indexes, gain values, noise-floor and noise-scale data, filter/power-save control, switch-control variants, spur suppression, unsupported MCS entries, IQ-local data, PAPD compensation deltas, and 128-entry transmit-gain tables for 2.4 GHz, 2.4 GHz external PA, and 5 GHz operation. It exports `struct phytbl_info` descriptors that tell LCN PHY code which data pointer, length, PHY table ID, offset, and element width to write.

## Important APIs, Types, And Data

- RX gain descriptor arrays: `dot11lcnphytbl_rx_gain_info_rev0`, `dot11lcnphytbl_rx_gain_info_2G_rev2`, `dot11lcnphytbl_rx_gain_info_5G_rev2`, `dot11lcnphytbl_rx_gain_info_extlna_2G_rev2`, and `dot11lcnphytbl_rx_gain_info_extlna_5G_rev2`.
- Size exports: `dot11lcnphytbl_rx_gain_info_sz_rev0`, `dot11lcnphytbl_rx_gain_info_2G_rev2_sz`, and `dot11lcnphytbl_rx_gain_info_5G_rev2_sz`.
- Main default table descriptor array `dot11lcnphytbl_info_rev0`, which writes min-signal-square, noise scale, filter control, power-save control, gain index, auxiliary gain index, switch control, noise-floor, gain value, gain table, spur table, unsupported MCS, IQ-local, and PAPD compensation tables.
- Board/radio switch-control descriptors: `dot11lcn_sw_ctrl_tbl_info_4313`, `dot11lcn_sw_ctrl_tbl_info_4313_bt_ipa`, `dot11lcn_sw_ctrl_tbl_info_4313_epa`, `dot11lcn_sw_ctrl_tbl_info_4313_bt_epa`, and `dot11lcn_sw_ctrl_tbl_info_4313_bt_epa_p250`.
- TX gain arrays of `struct lcnphy_tx_gain_tbl_entry`: `dot11lcnphy_2GHz_extPA_gaintable_rev0`, `dot11lcnphy_2GHz_gaintable_rev0`, and `dot11lcnphy_5GHz_gaintable_rev0`.

## Control Flow

The file contains no executable functions. Its effective control flow is data-driven in `phy_lcn.c`: initialization iterates `dot11lcnphytbl_info_rev0`, selects RX gain arrays based on band and external-LNA configuration, selects a switch-control descriptor based on board flags such as BT coexistence, internal/external PA, and package variant, and writes TX gain entries through LCN table helpers.

## State And Persistence

All arrays are `static const` or exported `const`; there is no mutable state. Persistence is hardware-facing: once `phy_lcn.c` writes these descriptors to PHY tables, the programmed hardware tables persist until reset or later reinitialization. The data is firmware/driver calibration material and is not updated at runtime by this file.

## Dependencies And Integration Points

The file includes `<types.h>`, `phy_int.h` for `struct phytbl_info` and `ARRAY_SIZE`, and `phytbl_lcn.h` for exports. `phy_lcn.c` consumes the descriptors via `wlc_lcnphy_write_table()`/`wlc_lcnphy_read_table()` wrappers around common PHY table access. The TX gain arrays feed LCN transmit gain programming and downstream math that uses `phy_qmath.c` helpers.

## Risks And Edge Cases

- Table descriptor fields must match hardware table ID, offset, element width, and array length. A mismatch can silently corrupt LCN PHY tables.
- RX gain selection depends on band and external-LNA board data; incorrect descriptor selection affects sensitivity and gain control.
- The header declares `dot11lcn_sw_ctrl_tbl_info_4313_epa_combo`, but this source exports no matching definition in the inspected file. If any caller references that symbol, linking would fail; current observed LCN code uses the exported `bt_epa`/`bt_epa_p250`/`epa` variants instead.
- Static numeric tables have little self-documentation; accidental edits are hard to review without hardware reference data.
- The 5 GHz TX gain table uses sentinel-like high byte values (`255`) in gain fields, so consumers must interpret those entries exactly as existing code expects.

## Test Signals

Build/link coverage should confirm all declared/used symbols resolve. Runtime signals include LCN PHY table initialization loops completing, correct RX gain table chosen for 2G/5G and external-LNA boards, TX gain writes succeeding, stable receive sensitivity/noise floor, transmit power within expected range, and no calibration or association regressions on BCM4313/LCN hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phytbl_lcn.c -->
