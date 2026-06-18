# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_color_regs.h

## Purpose
Defines i915 display color-management MMIO registers and bit fields used by `intel_color.c` and plane color code. It covers legacy palettes, precision palettes, pipe CSC, output CSC, pre/post CSC LUTs, Cherryview CGM, Skylake bottom color, and 3D LUT registers.

## Important definitions
Legacy GMCH palette macros include `PALETTE()`, palette RGB masks, 10-bit slope fields, and `PIPEGCMAX()`. ILK+ definitions include `LGC_PALETTE()`, `PREC_PALETTE()`, `GAMMA_MODE()`, CSC coefficient/offset registers, `PIPE_CSC_MODE()`, and ICL output CSC macros. Indexed LUT registers include `PREC_PAL_INDEX/DATA`, multi-segment palette registers, and `PRE_CSC_GAMC_INDEX/DATA`. VLV/CHV color blocks include WGC CSC and `CGM_PIPE_*` degamma/gamma/CSC/mode macros. 3D LUT support is defined by `LUT_3D_CTL`, `LUT_3D_INDEX`, `LUT_3D_DATA`, enable/ready/binding bits, and component masks.

## Control flow and state
The header has no executable control flow. Its macro layout determines which MMIO address and bit encoding each color path writes or reads. Hardware state persists in the addressed registers and is latched according to generation-specific behavior in `intel_color.c`.

## Dependencies, risks, and tests
It depends on `intel_display_reg_defs.h` for `_MMIO`, `_MMIO_PIPE`, `_PIPE`, masks, and field helpers. Risks are incorrect offsets, pipe selection, field widths, or reused enum values that silently corrupt color programming. Test signals include successful color IGTs, hardware state readout, register trace comparison, and build coverage for all generation-specific paths.
