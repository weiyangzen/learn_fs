<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_qmath.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_qmath.h

## Purpose

`phy_qmath.h` is the public declaration header for the brcmsmac PHY fixed-point math helpers implemented in `phy_qmath.c`. It gives the PHY implementation files a compact, floating-point-free arithmetic API for calibration and gain computations.

## Important APIs, Types, And Functions

The header includes `<types.h>` and declares the fixed-width integer based API: `qm_mulu16()`, `qm_muls16()`, `qm_add32()`, `qm_add16()`, `qm_sub16()`, `qm_shl32()`, `qm_shl16()`, `qm_shr16()`, `qm_norm32()`, and `qm_log10()`. The API uses `u16`, `s16`, and `s32`; `qm_log10()` returns two values by pointer, the computed logarithm and its Q-format exponent.

## Control Flow

The header has no runtime control flow. Its compile-time control flow is a normal include guard `_BRCM_QMATH_H_`, followed by type inclusion and prototypes.

## State And Persistence

No state is declared. The header exposes functions only and does not define storage, inline functions, or macros that mutate caller state.

## Dependencies And Integration Points

It depends on Broadcom/Linux `types.h` aliases and is included by `phy_qmath.c` and PHY code that needs fixed-point helpers. `phy_lcn.c` uses this interface for gain-table derived calculations, so this header is part of the internal ABI between the qmath implementation and PHY calibration code.

## Risks And Edge Cases

- The header documents no valid input ranges; callers must know fixed-point Q formats and avoid invalid `qm_log10()` arguments.
- The API has no `const` or nullability annotations for `qm_log10()` output pointers, so misuse is caught only by runtime failure or static analysis outside this header.
- Because these are external declarations, any signature drift from `phy_qmath.c` would be a build/link failure.

## Test Signals

Compile coverage is the main header-level signal: all users should build cleanly with the prototypes. Functional tests belong to `phy_qmath.c`, especially vectors around saturation, normalization, and Q-format return values from `qm_log10()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_qmath.h -->
