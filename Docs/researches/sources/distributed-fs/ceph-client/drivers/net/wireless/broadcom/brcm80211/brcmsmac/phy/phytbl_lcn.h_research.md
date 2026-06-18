<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phytbl_lcn.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phytbl_lcn.h

## Purpose

`phytbl_lcn.h` exposes the LCN-PHY table descriptors and transmit-gain table type/data defined in `phytbl_lcn.c`. It is the internal interface used by LCN PHY implementation code to load static calibration and control tables without depending on private array names.

## Important APIs, Types, And Data

- Extern declarations for default and RX-gain `struct phytbl_info` arrays and their size constants.
- Extern declarations for board-specific switch-control descriptors for BCM4313 variants.
- `struct lcnphy_tx_gain_tbl_entry` with `gm`, `pga`, `pad`, `dac`, and `bb_mult` byte fields, matching the TX gain tables consumed by LCN transmit gain programming.
- Extern declarations for `dot11lcnphy_2GHz_gaintable_rev0`, `dot11lcnphy_2GHz_extPA_gaintable_rev0`, and `dot11lcnphy_5GHz_gaintable_rev0`.

## Control Flow

The header has no runtime control flow. It also has no include guard, so repeated inclusion in the same translation unit would repeat the struct definition and extern declarations.

## State And Persistence

No mutable state is defined. All declared data is `const` storage in `phytbl_lcn.c`; consumers write referenced values into hardware PHY tables where they persist until reset or reprogramming.

## Dependencies And Integration Points

It includes `<types.h>` and `phy_int.h` for fixed-width types and `struct phytbl_info`. `phy_lcn.c` relies on this header during LCN PHY initialization, gain-table selection, switch-control table selection, and TX gain table loading.

## Risks And Edge Cases

- Missing include guard is a concrete maintenance hazard because this header defines `struct lcnphy_tx_gain_tbl_entry`; duplicate inclusion can produce a redefinition error.
- The declaration `dot11lcn_sw_ctrl_tbl_info_4313_epa_combo` has no matching definition in the inspected `phytbl_lcn.c`, making it a stale or incomplete API surface unless defined elsewhere.
- The split-line extern for `dot11lcnphy_2GHz_extPA_gaintable_rev0` is valid C but easy to disturb during mechanical edits.
- Callers must pair the correct size constants with the matching descriptor arrays; the header does not encode array lengths in types.

## Test Signals

Header validation is mostly build/link coverage: include it from LCN code, ensure no duplicate-include path hits the missing guard, and ensure all referenced externs resolve. Functional signals come from `phytbl_lcn.c` table loading on LCN hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phytbl_lcn.h -->
