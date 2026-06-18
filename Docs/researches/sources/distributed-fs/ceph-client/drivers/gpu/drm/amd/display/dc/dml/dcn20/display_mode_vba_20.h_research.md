# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_mode_vba_20.h

## Purpose

`display_mode_vba_20.h` is the small public header for the DCN 2.0 VBA display mode implementation. It exposes the two functions implemented in `display_mode_vba_20.c` so the surrounding Display Mode Library and AMD Display Core validation code can run DCN 2.0 mode support/configuration and selected-mode recalculation.

## Important APIs, Types, And Functions

- Include guard `_DCN20_DISPLAY_MODE_VBA_H_`: prevents duplicate declarations.
- `void dml20_recalculate(struct display_mode_lib *mode_lib);`: recalculates final selected-mode DCN 2.0 clocks, watermarks, prefetch, bandwidth, and pipe parameters by mutating `mode_lib->vba`.
- `void dml20_ModeSupportAndSystemConfigurationFull(struct display_mode_lib *mode_lib);`: performs full mode support validation across voltage states/MPC options and commits the selected state into `mode_lib->vba`.
- `struct display_mode_lib`: referenced by pointer but not declared in this header. Callers are expected to include the shared DML display mode library header before or alongside this header.

## Control Flow

The header contains declarations only. Runtime control flow is owned by callers that include this header and invoke the functions in the appropriate DML sequence. The intended ordering is that full mode support/configuration chooses a valid voltage and pipe configuration, and recalculation derives final selected-mode programming values from that chosen state.

## State And Persistence Behavior

The header stores no state. Its declared functions operate on caller-owned `struct display_mode_lib` and mutate in-memory VBA fields. There is no persistence, allocation, locking, or hardware access in the header itself.

## Dependencies And Integration Points

This header is integrated by DCN 2.0 DML source files and any generation-selection layer that dispatches to DCN-specific VBA functions. It depends on the shared definition of `struct display_mode_lib` from `display_mode_lib.h`; the implementation file includes that header before including this one.

The declarations are part of the AMDGPU display validation interface for DCN 2.0. They connect the common DML caller flow to the DCN 2.0-specific formula implementation in `display_mode_vba_20.c`.

## Risks And Edge Cases

- The header does not forward declare `struct display_mode_lib`, so standalone inclusion before the shared DML header can produce compile warnings or errors depending on compiler settings and include order.
- Any signature change must be coordinated with the implementation and all generation-dispatch callers.
- The include guard name omits `_20` while the file name includes `20`; that is harmless today but can be confusing near other generation headers.
- The header exposes only coarse entry points. Callers cannot independently test static helpers in the C file without including or instrumenting the implementation.

## Test Signals

- Kernel build coverage should catch include-order problems, declaration/definition mismatches, or missing callers after refactors.
- A focused compile test can include this header after `display_mode_lib.h` from a DML translation unit and call both declarations with a mock or initialized `struct display_mode_lib *`.
- Integration tests should verify the generation dispatch path for DCN 2.0 actually resolves to these functions and that the resulting `mode_lib->vba` fields are populated by the implementation.
