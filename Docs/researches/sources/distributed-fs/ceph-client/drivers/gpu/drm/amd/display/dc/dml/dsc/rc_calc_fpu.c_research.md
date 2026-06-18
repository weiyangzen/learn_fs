# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dsc/rc_calc_fpu.c

## Purpose
`dsc/rc_calc_fpu.c` computes Display Stream Compression rate-control parameters with floating-point formulas and QP lookup tables.

## Important APIs, Types, And Functions
The public function is `_do_calc_rc_params()`. Private helpers are `median3()`, `dsc_roundf()`, `get_qp_set()`, and `get_ofs_set()`. Macros implement table selection by color mode, bits per component, and min/max selector.

## Control Flow
`_do_calc_rc_params()` asserts FPU enablement, converts DRM bpp from sixteenths, halves bpp for native 422/420, sets quant increment limits, computes grouped bpp, sets fullness and line offsets by color mode, calculates initial transmit delay and padding adjustment, sets flatness fields, loads QP min/max tables, applies DSC 1.1 444 decrements, computes offsets, and writes fixed RC model fields and buffer thresholds.

## State, Persistence, And Dependencies
The only mutable state is caller-provided `struct rc_params`. Dependencies include DRM DSC types, AMD DC FPU guard logic, `qp_tables.h`, `dm_error`, `min`, `swap`, and `memcpy`.

## Integration Points
AMD display DSC code uses this to prepare RC/PPS fields such as quant limits, initial fullness, QP ranges, offsets, model size, target offsets, and thresholds.

## Risks
It must run only in an FPU-safe display context. `get_qp_set()` checks only upper bounds, so bpp below the first row is dangerous. Invalid mode/BPC combinations can leave QP arrays unchanged. Formula changes affect DSC quality and compliance.

## Test Signals
Use known DSC vectors for RGB/444/422/420 at 8/10/12 bpc, native subsampling bpp halving, DSC 1.1 444 QP decrement behavior, slice-width padding cases, table edges, and FPU guard coverage.
