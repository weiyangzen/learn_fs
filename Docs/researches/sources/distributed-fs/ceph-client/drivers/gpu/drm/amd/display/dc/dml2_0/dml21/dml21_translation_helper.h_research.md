# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_translation_helper.h

## Purpose
`dml21_translation_helper.h` declares the translation boundary between DC state and the DML 2.1 model. It keeps most dependencies as forward declarations while exposing the functions needed by the wrapper and utility layers.

## Important APIs, types, and functions
The header declares initialization translation, display-config mapping, clock/watermark extraction, hardware-resource mapping, mcache pipe config generation, p-state type mapping, display-config plane lookup, and minimum-clock initialization.

## Control flow
There is no executable flow. The intended sequence is initialize DML input parameters, map a `dc_state` into `dml2_display_cfg`, run DML core checks/programming, then copy clocks/watermarks/resources back.

## State and persistence behavior
No state is defined here. Implementations operate on `dml2_context`, `dc_state`, `pipe_ctx`, and DML programming objects owned by callers.

## Dependencies and integration points
It forward declares DC and DML types and is included by `dml21_wrapper_fpu.c` and `dml21_utils.c`. It is also part of the local contract for resource-management code that needs plane/display-config mapping.

## Risks and edge cases
The prototypes expose several DML internal types, so include order must provide complete definitions before use in C files. `map_plane_to_dml21_display_cfg()` returns an unsigned value but uses `UINT_MAX` as the invalid sentinel in implementation, requiring callers to compare carefully.

## Test signals
Build coverage of every including translation unit and validation paths that exercise each declared function are the relevant signals.
