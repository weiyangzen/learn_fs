# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/ppr.h

## Purpose
`ppr.h` defines the B43 Power Per Rate data layout and helper API. It gives PHY code a compact, byte-addressable qdbm table for per-rate power limits and a structured view grouped by CCK, OFDM, and N-PHY MCS rate families.

## Important APIs, Types, And Definitions
- Rate counts: `B43_PPR_CCK_RATES_NUM` is 4, `B43_PPR_OFDM_RATES_NUM` is 8, `B43_PPR_MCS_RATES_NUM` is 8, and `B43_PPR_RATES_NUM` totals CCK plus two OFDM groups plus four MCS groups.
- `struct b43_ppr_rates`: named arrays for `cck`, `ofdm`, `ofdm_20_cdd`, `mcs_20` (SISO), `mcs_20_cdd`, `mcs_20_stbc`, and `mcs_20_sdm`.
- `struct b43_ppr`: a union exposing the same bytes as `__all_rates[]` for generic iteration and `rates` for semantic access. Values are qdbm Q5.2.
- Forward declarations: `struct b43_wldev` and `enum b43_band` avoid pulling in the full driver header.
- Public helpers: clear, add signed delta, apply max cap, apply min floor, get maximum, and load maximums from SPROM for a selected band.

## Control Flow And State
This header defines storage only. State is caller-owned and normally embedded in PHY state, especially `struct b43_phy_n::tx_pwr_max_ppr`. The union makes it possible for implementation code to iterate over all rate bytes while callers can address specific rate groups by name. There is no allocation or persistence policy in the header itself.

## Dependencies And Integration Points
- Includes only `<linux/types.h>`, keeping it lightweight for inclusion by `phy_n.h` and `ppr.c`.
- `ppr.c` implements the declared helpers and depends on the exact no-padding layout.
- N-PHY code consumes `struct b43_ppr` to carry SPROM-derived and regulatory-clamped TX power limits.
- SPROM band loading uses `enum b43_band`, so any band enum changes in `b43.h` must remain compatible with the loader.

## Risks
- The union layout depends on `struct b43_ppr_rates` being exactly the same size as `__all_rates[]`. `ppr.c` has a build assertion, but any new fields require updating `B43_PPR_RATES_NUM`.
- The layout represents only the current groups. Adding 40 MHz, VHT, or other rate families requires a deliberate ABI/layout update across all iterators.
- All values are `u8` qdbm; callers must handle signed arithmetic and underflow/overflow through the helper functions or explicit clamps.

## Test Signals
- Compile with `ppr.c` to preserve the size assertion.
- Exercise helper functions through N-PHY TX power recalculation and confirm named groups match flat iteration order.
- Static review should verify any new rate group is added to both the structured layout and `B43_PPR_RATES_NUM`.
