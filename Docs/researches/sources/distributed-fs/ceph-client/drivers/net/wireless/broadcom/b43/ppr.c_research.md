# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/ppr.c

## Purpose
`ppr.c` implements Power Per Rate helper operations for the B43 driver. It manages `struct b43_ppr`, a compact table of qdbm power limits for CCK, OFDM, and 802.11n MCS rate groups, and populates those limits from SPROM board data. N-PHY TX power code uses this table to enforce per-rate maximums and adjust them for hardware gain.

## Important APIs And Functions
- `b43_ppr_clear(struct b43_wldev *dev, struct b43_ppr *ppr)`: zeroes the full table and asserts at build time that the union has no padding beyond the rate bytes.
- `b43_ppr_add(struct b43_wldev *dev, struct b43_ppr *ppr, int diff)`: adds a signed delta to every rate and clamps each result to `[0, 127]`.
- `b43_ppr_apply_max(struct b43_wldev *dev, struct b43_ppr *ppr, u8 max)`: caps all rate powers at a maximum.
- `b43_ppr_apply_min(struct b43_wldev *dev, struct b43_ppr *ppr, u8 min)`: raises all rate powers below a minimum.
- `b43_ppr_get_max(struct b43_wldev *dev, struct b43_ppr *ppr)`: returns the maximum power value among all stored rates.
- `b43_ppr_load_max_from_sprom(struct b43_wldev *dev, struct b43_ppr *ppr, enum b43_band band)`: selects band-specific SPROM maximum power and offsets, fills CCK/OFDM/MCS entries, and applies extra CDD/STBC offsets for N-PHY rev >= 3.

## Control Flow
Most helper operations iterate over every byte in `ppr->__all_rates` using the local `ppr_for_each_entry()` macro. That intentionally treats the structured view and flat view as the same storage.

`b43_ppr_load_max_from_sprom()` first selects source data by `enum b43_band`. For 2.4 GHz it uses the minimum of the two cores' `maxpwr_2g`, `ofdm2gpo`, `mcs2gpo`, and the low nibbles of `cddpo`/`stbcpo`; for low, middle, and high 5 GHz it selects the matching max power and OFDM/MCS offset arrays and corresponding extra-offset nibbles. Invalid bands warn once and return false.

After band selection, CCK entries are filled only for 2.4 GHz from `cck2gpo`. OFDM entries are filled from the selected 32-bit OFDM power-offset word. MCS 20 SISO entries are derived from OFDM entries. MCS 20 CDD and STBC entries are filled from the first two MCS offset words and optionally reduced by extra CDD/STBC offsets for N-PHY rev >= 3. OFDM 20 CDD entries mirror selected MCS CDD entries. MCS 20 SDM entries come from the third and fourth MCS offset words.

## State And Persistence
`ppr.c` mutates only caller-owned `struct b43_ppr` memory. It has no static mutable state. In this subset the main persistent owner is `struct b43_phy_n::tx_pwr_max_ppr`; `phy_n.c` clears it, loads SPROM limits, clamps it to regulatory/current limits, subtracts hardware gain, applies a floor, and reads the maximum for hardware programming and debug output.

All stored values are `u8` qdbm values. Offsets from SPROM are 4-bit nibbles multiplied by two, then subtracted from the selected maximum power. Helper add/clamp routines keep values in the range accepted by the table representation.

## Dependencies And Integration Points
- Includes `ppr.h` for structure layout and exported prototypes and `b43.h` for `struct b43_wldev`, `struct b43_phy`, band constants, warning macros, and SPROM access.
- Reads `dev->dev->bus_sprom`, especially `core_pwr_info[]`, CCK/OFDM/MCS power-offset fields, and CDD/STBC offsets.
- Reads `dev->phy.type` and `dev->phy.rev` to apply N-PHY-revision-specific CDD/STBC reductions.
- Used by `phy_n.c` during TX power limit recalculation through `b43_ppr_clear()`, `b43_ppr_load_max_from_sprom()`, `b43_ppr_apply_max()`, `b43_ppr_get_max()`, `b43_ppr_add()`, and `b43_ppr_apply_min()`.

## Risks
- Subtracting offsets from `u8 maxpwr` can underflow before assignment if SPROM data is malformed or max power is smaller than offset. The current code relies on sane SPROM data and later clamping helpers, but load itself does not clamp.
- The function assumes both `core_pwr_info[0]` and `[1]` are valid and uses the lower max power. Single-chain or incomplete SPROM cases need upstream guarantees.
- Extra CDD/STBC offsets are subtracted after max-minus-offset and are not clamped in the load function.
- Only 20 MHz MCS groups represented in `struct b43_ppr` are filled here. If future code expects 40 MHz or newer rate groups, the layout and loader need extension.
- The `dev` argument is unused by simple helpers except for type consistency. That is harmless but can hide future assumptions if helper behavior becomes device-specific.

## Test Signals
- Build-time `BUILD_BUG_ON(sizeof(struct b43_ppr) != B43_PPR_RATES_NUM * sizeof(u8))` catches padding/layout regressions.
- Unit-style tests can validate clear/add/min/max/get-max on synthetic tables, including negative deltas and clamp boundaries 0 and 127.
- SPROM fixture tests should cover 2.4 GHz, all three 5 GHz bands, N-PHY rev < 3 and >= 3, and invalid band handling.
- Runtime signals are correct N-PHY TX power debug output, sane per-rate limits after channel changes, and absence of regulatory/power anomalies.
