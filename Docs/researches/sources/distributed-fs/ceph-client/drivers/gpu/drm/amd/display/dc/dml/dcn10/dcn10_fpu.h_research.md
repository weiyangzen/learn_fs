# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn10/dcn10_fpu.h

## Purpose

`dcn10_fpu.h` declares the public DCN1 FPU-protected helper exported by `dcn10_fpu.c`. It is a narrow interface used by resource construction code that needs the DCN1 floating-point bounding-box adjustment logic without exposing the implementation details or global DML tables through this header.

## Important APIs, Types, And Functions

Declared API:

- `void dcn10_resource_construct_fp(struct dc *dc);`

The header does not include `struct dc` definitions itself, so callers must include an appropriate DC core/resource header before or alongside this header. It uses a conventional include guard `__DCN10_FPU_H__`.

## Control Flow

There is no runtime control flow in the header. It only makes the function prototype visible to translation units that perform DCN1 resource construction or related setup.

## State And Persistence Behavior

The header holds no state and performs no persistence. The declared function mutates `struct dc` state in its implementation, but the header itself does not describe or own that state.

## Dependencies And Integration Points

Integration is intentionally minimal:

- Included by `dcn10_fpu.c` for prototype consistency.
- Expected to be included by DCN1 resource construction code that calls `dcn10_resource_construct_fp`.
- The caller is responsible for ensuring FPU access is enabled before calling, as documented in the `.c` file.

## Risks And Edge Cases

- Because the header does not include or forward-declare `struct dc`, include ordering matters. Existing callers likely already include broader DC headers; new callers must do the same.
- The function name suffix `_fp` communicates FPU requirements but does not enforce them at compile time. Misuse is only caught at runtime by `dc_assert_fp_enabled()` in the implementation.
- Adding more prototypes here should preserve the FPU boundary convention: callers enter/exit FPU protection outside this file, and implementation functions assert that protection.

## Test Signals

Useful validation signals include:

- Compile coverage for all DCN1 resource files that include this header.
- Header self-containment checks if project policy changes to require forward declarations.
- Runtime FPU assertion coverage through the implementation.
