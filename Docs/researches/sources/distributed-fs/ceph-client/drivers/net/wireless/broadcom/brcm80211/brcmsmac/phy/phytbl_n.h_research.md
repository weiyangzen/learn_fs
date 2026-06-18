<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phytbl_n.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phytbl_n.h

## Purpose

`phytbl_n.h` declares the N-PHY table descriptor arrays, descriptor counts, and exported noise-variance tables defined by `phytbl_n.c`. It is the internal interface between the static N-PHY table bank and the N-PHY initialization/calibration code.

## Important APIs, Types, And Data

- `ANT_SWCTRL_TBL_REV3_IDX` identifies the antenna-switch-control entry in the rev3 volatile descriptor sequence.
- Extern descriptor arrays and size constants for rev0, rev3, rev7, and rev16 N-PHY table initialization.
- Extern volatile descriptor arrays for rev0 and four rev3 antenna-switch variants.
- Extern `noise_var_tbl_rev3[]` and `noise_var_tbl_rev7[]`, which are used both as table payloads and direct calibration lookup data.

## Control Flow

There is no runtime control flow. The header has no include guard; it provides macros and extern declarations consumed by `phy_n.c`.

## State And Persistence

No state is defined in this header. It exposes `const` arrays owned by `phytbl_n.c`; callers persist their contents into hardware PHY tables during initialization and may read exported noise arrays for calculations.

## Dependencies And Integration Points

It includes `<types.h>` and `phy_int.h` for fixed-width types and `struct phytbl_info`. `phy_n.c` uses the declarations to select table banks by PHY revision, write volatile antenna-switch tables, and inspect noise-variance values during calibration.

## Risks And Edge Cases

- No include guard is a maintenance risk, though the current content is macro/extern-only and less fragile than a header with struct definitions.
- `ANT_SWCTRL_TBL_REV3_IDX` must stay aligned with the order of `mimophytbl_info_rev3_volatile`; if the array order changes, `phy_n.c` can patch/select the wrong descriptor.
- Size constants must match the corresponding arrays. The header cannot enforce pairing, so caller loops depend on correct definitions in `phytbl_n.c`.
- Direct noise table exports expose array layout assumptions to code outside the table bank.

## Test Signals

Compile/link all N-PHY users and exercise revision-specific initialization. Specific signals include correct descriptor loop counts, rev3 antenna switch variant writes, stable noise calibration reads from `noise_var_tbl_rev3`/`rev7`, and successful PHY attach/channel operation on hardware revisions covered by the arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phytbl_n.h -->
