# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_utils.h

## Purpose
Declares the core utility functions implemented in `dml2_core_utils.c`, giving core calculators access to shared arithmetic, enum classification, logging, clock lookup, implicit SubVP expansion, encoder/link helpers, and frame-time helpers.

## Important APIs, types, and functions
The header exports utility families for source-format classification, mode-support logging, output-bpp calculation, pipe/plane mapping, phantom/linear/rotation/swizzle classification, QoS/UCLK table indexing, implicit SubVP expansion, stream encoder and DP link-rate classification, ODM split detection, and frame time calculation.

## Control flow and integration
Core calculation code includes this header whenever it needs shared helper logic. `dml2_core_utils_expand_implict_subvp()` is the most integration-heavy declaration because it links `display_configuation_with_meta`, an expanded `dml2_display_cfg`, and `dml2_core_scratch`.

## State and persistence behavior
No state is stored in the header. Declared functions operate on caller-owned structs and arrays; many output arrays are indexed by plane or stream.

## Dependencies
Includes `dml2_internal_shared_types.h`, `dml2_debug.h`, and `lib_float_math.h`. The declarations reference internal support info, display config, plane/stream parameters, SoC state tables, QoS parameter tables, and display metadata.

## Risks and edge cases
Because this header is broadly included, any signature change can force widespread updates. Function names and semantics must stay aligned with utility implementation and with public core-calcs wrappers that expose similar enum-to-string helpers.

## Test signals
Compile coverage across core calculators is the first signal. Runtime tests should target the implementation behavior described in the `.c` research, especially enum coverage and implicit SubVP expansion.
