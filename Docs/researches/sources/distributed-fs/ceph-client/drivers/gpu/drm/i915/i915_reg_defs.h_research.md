<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_reg_defs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_reg_defs.h

## Purpose
Provides typed wrappers and small aggregate types for i915 MMIO register definitions.

## Important APIs, types, and functions
- `i915_reg_t` and `_MMIO()` represent ordinary MMIO offsets.
- `i915_mcr_reg_t` and `MCR_REG()` represent multicast/replicated register offsets.
- `INVALID_MMIO_REG`, `i915_mmio_reg_offset()`, `i915_mmio_reg_equal()`, and `i915_mmio_reg_valid()` provide generic offset helpers over both typed wrappers.
- `struct i915_irq_regs`/`I915_IRQ_REGS()` and `struct i915_error_regs`/`I915_ERROR_REGS()` bundle common IMR/IER/IIR and EMR/EIR register sets.

## Control flow
The file has no runtime control flow. `_Generic` selection in `i915_mmio_reg_offset()` preserves type convenience while reducing callers to a raw offset when needed.

## State and persistence
No runtime state is stored. The typed wrappers encode register identity in compile-time constants and local aggregate values.

## Dependencies and integration points
Depends on DRM Intel `pick.h` and `reg_bits.h`. It underpins `i915_reg.h`, GT/display register headers, uncore register accessors, interrupt setup, and MCR register handling.

## Risks
Typed register wrappers rely on callers not discarding the MCR/non-MCR distinction prematurely. `INVALID_MMIO_REG` is offset zero, so any real offset-zero register would need special handling. `_Generic` only supports the explicitly listed wrapper types.

## Test signals
Compile-time coverage is the main signal. Misuse tends to show as type errors, invalid register comparisons, or uncore helpers targeting the wrong access path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_reg_defs.h -->
