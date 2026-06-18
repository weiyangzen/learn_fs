# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_freq.c

## Purpose
`i915_freq.c` decodes legacy chipset strap registers into front-side-bus and memory frequencies for pre-modern Intel graphics platforms.

## Important APIs, Types, and Functions
Exported functions are `i9xx_fsb_freq()`, `ilk_fsb_freq()`, and `ilk_mem_freq()`. They read `CLKCFG`, `CSIPLL0`, and `DDRMPLL1` respectively and map register values to kHz-like integer frequencies.

## Control Flow
`i9xx_fsb_freq()` masks `CLKCFG_FSB_MASK` and uses different switch tables for Pineview/mobile versus desktop straps, returning defaults with `MISSING_CASE()` for unknown values. `ilk_fsb_freq()` decodes Ironlake CPU-side PLL values and returns `0` on unknown values after debug logging. `ilk_mem_freq()` decodes DDR PLL values for 800/1066/1333/1600 MHz memory and returns `0` for unknown values.

## State and Persistence Behavior
The file stores no state. It reads current strap/PLL registers each time. Comments note that some BIOSes can configure straps independently from actual FSB frequency, so returned values are capability/strap interpretations rather than guaranteed live clocks.

## Dependencies and Integration Points
It depends on uncore register access, platform predicates, `intel_mchbar_regs.h`, and DRM debug logging. Callers use these helpers for legacy bandwidth, watermark, or platform information calculations.

## Risks
The mapping is based on legacy documentation and straps, not live measurement. Unknown values fall back to a desktop default in `i9xx_fsb_freq()` but to zero in Ironlake helpers, so callers must handle both. Register access requires MCHBAR/uncore availability.

## Test Signals
Boot legacy i9xx/Pineview/Ironlake systems and compare decoded frequencies with platform expectations; exercise unknown strap debug logs via simulation/selftests where possible; verify callers tolerate zero returns.
