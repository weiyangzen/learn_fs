# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/pllgt215.c

## Purpose
Implements GT215-generation PLL coefficient search for integer and optional fractional-N PLL programming.

## Important APIs, types, and functions
Exports `gt215_pll_calc()`, which accepts BIOS PLL limits, target frequency, output N/fN/M/P pointers, and returns the achieved frequency or an error.

## Control flow
The function chooses an initial post divider within BIOS limits, computes legal M range from reference input-frequency limits, and iterates M. For integer mode it rounds N based on the remainder and tracks the lowest error. For fractional mode it computes a 13-bit fractional residue and returns immediately with an exact target-oriented representation.

## State and persistence
No persistent state. The computed coefficients are consumed by clock/devinit programming routines.

## Dependencies and integration points
Depends on BIOS PLL limits and NVKM error logging. Used by GT215, Fermi/Kepler display PLL programming, and newer VPLL devinit paths.

## Risks
Fractional mode returns early rather than exhaustive-searching, so callers must request it only for hardware that supports the representation. Bad BIOS limits can produce no match and `-EINVAL`.

## Test signals
PLL coefficient unit checks against known BIOS tables, display mode pixel-clock programming, and debug logs for no matching values.
