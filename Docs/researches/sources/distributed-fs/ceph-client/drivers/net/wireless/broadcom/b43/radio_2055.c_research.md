# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2055.c

## Purpose
`radio_2055.c` provides BCM2055 radio data tables and two helper functions for N-PHY hardware. It contains a band-dependent default radio initialization table and a channel switch table for N-PHY revision-2 style channel programming. The executable logic uploads selected radio defaults and performs channel-to-table-entry lookup; the rest of the file is static hardware calibration/programming data.

## Important APIs, Types, And Data
- `struct b2055_inittab_entry`: internal table row with 5 GHz value, 2.4 GHz value, and flags. Flags are `B2055_INITTAB_ENTRY_OK` and `B2055_INITTAB_UPLOAD`.
- `b2055_inittab[]`: indexed by BCM2055 radio register number. Rows define default per-register values for 5 GHz and 2.4 GHz. Some rows are marked uploadable by default; others are valid but normally skipped unless forced.
- `RADIOREGS(...)` and `PHYREGS(...)`: initializer macros that map compact table values into `struct b43_nphy_channeltab_entry_rev2` fields.
- `b43_nphy_channeltab_rev2[]`: static channel table covering many 5 GHz channel numbers/frequencies plus 2.4 GHz channels 1-14. Each row stores channel number, frequency, an unknown field, radio PLL/VCO/LGEN/core tuning values, and six PHY bandwidth/SFO registers.
- `b2055_upload_inittab(struct b43_wldev *dev, bool ghz5, bool ignore_uploadflag)`: writes selected init-table rows to BCM2055 radio registers using `b43_radio_write16()`.
- `b43_nphy_get_chantabent_rev2(struct b43_wldev *dev, u8 channel)`: linear-searches `b43_nphy_channeltab_rev2[]` and returns a const row pointer or `NULL`.

## Control Flow
`b2055_upload_inittab()` iterates over every index in `b2055_inittab[]`. It skips entries without `B2055_INITTAB_ENTRY_OK`. It writes a row if the row has `B2055_INITTAB_UPLOAD` or the caller passes `ignore_uploadflag`. The chosen value comes from `ghz5` or `ghz2`. Every fourth write it reads `B43_MMIO_MACCTL` to flush posted writes.

`b43_nphy_get_chantabent_rev2()` scans the static channel table in order and compares `e->channel` to the requested `u8 channel`. The returned pointer is used by N-PHY channel-switch code to program radio and PHY registers. Failure returns `NULL`; callers must handle unsupported channels.

## State And Persistence
This file has no mutable software state. Its static const tables persist for the module lifetime. Runtime state changes occur only through hardware writes in `b2055_upload_inittab()` and through callers that apply channel-table entries to radio/PHY registers. The returned channel-table pointers are immutable and should not be stored beyond normal table lifetime assumptions, although static storage makes them stable while the module is loaded.

## Dependencies And Integration Points
- Includes `b43.h` for `struct b43_wldev`, MMIO/radio write helpers, and `B43_MMIO_MACCTL`; `radio_2055.h` for register names and channel-entry type; and `phy_common.h`.
- `phy_n.c` calls `b2055_upload_inittab()` during BCM2055/N-PHY initialization and uses many `B2055_*` register names directly for calibration and channel setup.
- `phy_n.c` calls `b43_nphy_get_chantabent_rev2()` during channel switching for radio revision paths that use BCM2055 rev2 tables, then writes the returned radio fields to `B2055_PLL_REF`, `B2055_RF_PLLMOD*`, `B2055_VCO_*`, `B2055_LGEN_*`, and per-core registers; PHY fields are written through N-PHY table/register helpers.
- `radio_2055.h` declares this file's two exported helpers and defines the register constants that make the table indices meaningful.

## Risks
- Hardware table correctness is critical. A wrong byte in the init table or channel table can break only specific bands/channels, making regressions hard to spot without broad hardware coverage.
- `b2055_upload_inittab()` trusts table indices as radio register addresses. Sparse unnamed entries such as `[0xC7]` are intentional but easy to damage during refactors.
- The `ignore_uploadflag` argument can force writes to rows normally marked `NOUPLOAD`; callers must use it only when full table programming is safe.
- Channel lookup is linear but the table is small enough for driver use. The bigger risk is missing or duplicate channel rows; lookup returns the first match.
- The `unk2` field has no documented semantics in this file, so updates require care and preferably comparison against vendor tables or known-good hardware traces.

## Test Signals
- Build-time coverage must include N-PHY and BCM2055 radio support so table initializers match the struct declaration.
- Runtime tests should include initialization on 2.4 GHz and 5 GHz, channel changes across low/mid/high 5 GHz and channels 1-14, and verification that unsupported channels fail gracefully.
- Hardware logs and register traces should show expected `b43_radio_write16()` sequences and no channel-switch failures in `phy_n.c`.
- Regression tests should specifically cover rows at boundaries: first/last table entries, 2.4 GHz channel 14, and 5 GHz channels with half-step odd channel numbers.
