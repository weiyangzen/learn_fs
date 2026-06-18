<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_qmath.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_qmath.c

## Purpose

`phy_qmath.c` implements the small fixed-point arithmetic helper layer used by Broadcom `brcmsmac` PHY calibration code. It provides saturated 16-bit and 32-bit arithmetic, signed and unsigned fixed-point multiplication, normalization, bidirectional shifts, and a table/interpolation based `log10()` routine that avoids floating point in kernel/driver code. The file has no device state of its own; its purpose is deterministic math support for PHY calculations such as transmit gain estimation in `phy_lcn.c`.

## Important APIs, Types, And Functions

- `qm_mulu16(u16 op1, u16 op2)` multiplies two unsigned 16-bit fixed-point values and returns the high 16 bits of the 32-bit product.
- `qm_muls16(s16 op1, s16 op2)` multiplies signed 16-bit values and returns a Q15-style result, with a special saturation branch for `0x8000 * 0x8000`.
- `qm_add32()`, `qm_add16()`, and `qm_sub16()` perform saturating arithmetic. `qm_add32()` detects signed overflow from the wrapped result; the 16-bit helpers compute in `s32` and clamp to `0x7fff` or `0x8000`.
- `qm_shl32()` and `qm_shl16()` implement saturated left shift by repeated saturated doubling, and arithmetic right shift for negative shifts. `qm_shr16()` is a thin inverse wrapper around `qm_shl16()`.
- `qm_norm32()` counts redundant sign bits in a 32-bit signed value and is used to normalize magnitudes before lookup/interpolation.
- `qm_log10(s32 N, s16 qN, s16 *log10N, s16 *qLog10N)` computes a fixed-point base-10 logarithm using `log_table[]`, interpolation, and multiplication by `LOG10_2`.

## Control Flow

Most helpers are straight-line arithmetic with clamp checks. The shift helpers clamp requested shift ranges to `[-31, 31]` for 32-bit and `[-15, 15]` for 16-bit, then use repeated saturated addition for positive left shifts. `qm_log10()` is the only multi-stage algorithm: it normalizes `N`, adjusts `qN`, derives a five-bit table index from the normalized mantissa, takes a 16-bit interpolation offset, adds the exponent contribution, normalizes the log2 result, converts it to log10 by multiplying with `LOG10_2`, and returns both value and resulting Q format.

## State And Persistence

There is no mutable state, heap allocation, I/O, or persistence. The only private data is the compile-time `log_table[]`. All exported functions are pure for valid pointer arguments, except that `qm_log10()` writes through `log10N` and `qLog10N`.

## Dependencies And Integration Points

The implementation includes only `phy_qmath.h`, which pulls in Broadcom/Linux integer aliases from `<types.h>`. `phy_lcn.c` calls `qm_log10()`, `qm_shr16()`, and `qm_sub16()` while computing gain-related quantities from LCN PHY table entries. These helpers are expected to be link-visible within the brcmsmac PHY object set through prototypes in `phy_qmath.h`.

## Risks And Edge Cases

- `qm_log10()` does not guard `N <= 0`; `N == 0` leads to `qm_norm32(0) == 31`, then left-shifts zero and indexes `log_table[0]`, but a mathematical log of zero is undefined. Negative input normalization/table lookup also relies on signed shifts and is not a meaningful logarithm path.
- `qm_norm32()` left-shifts signed values in its loop. Kernel toolchains generally tolerate this legacy driver pattern, but strictly speaking signed overflow/left-shift behavior can be compiler-sensitive.
- Saturation constants are written as hex literals cast to signed types. The intended values are clear, but changes to type widths or warning policy could expose implementation-defined conversions.
- `qm_shl32()` and `qm_shl16()` use loops rather than one-step shift and saturation, so unusually large repeated calls in hot paths would be slower, though shift counts are bounded.

## Test Signals

Useful checks are focused unit vectors: signed multiply saturation for `0x8000 * 0x8000`, add/sub overflow clamps, positive and negative shift boundaries, `qm_norm32()` examples, and `qm_log10()` comparisons for known fixed-point powers. Integration signals are successful brcmsmac build, LCN PHY initialization without calibration regressions, and stable transmit-gain behavior on hardware paths that call `phy_lcn.c` math.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_qmath.c -->
