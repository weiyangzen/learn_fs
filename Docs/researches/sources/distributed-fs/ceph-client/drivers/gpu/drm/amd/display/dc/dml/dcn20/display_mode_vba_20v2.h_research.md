# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_mode_vba_20v2.h

## Purpose

`display_mode_vba_20v2.h` is the small public interface for the DCN 2.0v2 VBA implementation. It declares the two generation-specific entry points implemented in `display_mode_vba_20v2.c` so other DML/DC files can run the DCN20v2 recalculation and full mode-support/system-configuration pass.

The header contains only license text, an include guard, and function declarations. It intentionally does not expose the many static helper formulas used by the implementation file.

## Important APIs, Types, And Functions

- `dml20v2_recalculate(struct display_mode_lib *mode_lib)`: recomputes selected-mode clocks, pipe configuration, prefetch, watermarks, and performance values after the common mode support and setup steps.
- `dml20v2_ModeSupportAndSystemConfigurationFull(struct display_mode_lib *mode_lib)`: runs the full DCN20v2 validation/selection pass and updates `mode_lib->vba` with support flags, selected voltage state, DPP/ODM/DSC decisions, clocks, and output bpp.
- `struct display_mode_lib`: used as an incomplete type in the prototypes. The defining declaration is supplied by including `display_mode_lib.h` before or alongside this header in translation units that call the functions.

## Control Flow

The header itself has no executable control flow. Its integration role is compile-time linkage: callers include it, pass a configured `struct display_mode_lib *`, and rely on the `.c` file to mutate `mode_lib->vba`. The include guard `_DCN20V2_DISPLAY_MODE_VBA_H_` prevents duplicate declarations during nested includes.

The two declared functions represent different stages. `dml20v2_ModeSupportAndSystemConfigurationFull` is the broader validation and configuration selector. `dml20v2_recalculate` is the recalculation path used after mode inputs and selected configuration are established.

## State And Persistence Behavior

The header stores no state and has no persistence behavior. All stateful behavior belongs to the implementation functions and the caller-owned `struct display_mode_lib`. Since the header only forward-references `struct display_mode_lib` in parameter lists, it does not force a layout dependency by itself.

## Dependencies And Integration Points

The file depends on the C compiler seeing a compatible declaration for `struct display_mode_lib` in any translation unit using the prototypes. The implementation includes this header from `display_mode_vba_20v2.c`; generation dispatch code elsewhere in the Display Mode Library can include it to call the DCN20v2 formulas.

The naming convention ties it to `drivers/gpu/drm/amd/display/dc/dml/dcn20/` and to sibling DCN20 DML files such as request/deadline calculation and display-mode accessors. It is not a standalone API for external kernel subsystems.

## Risks And Edge Cases

- If a caller includes this header without a prior visible declaration of `struct display_mode_lib`, C permits an incomplete struct type in the prototype, but mismatched declarations elsewhere would be a compile-time or ABI risk.
- The header does not include `display_mode_lib.h`, so include-order assumptions must stay consistent across callers.
- Any signature change in the `.c` file must be reflected here or callers will fail to compile or link.
- The broad mutating behavior of both functions is not documented in the header, so callers must know from DML conventions that `mode_lib->vba` is updated in place.

## Test Signals

- Kernel build and sparse/compiler checks catch missing prototypes, signature drift, duplicate include issues, and missing `struct display_mode_lib` visibility.
- Link tests catch cases where generation dispatch references either declared function but the implementation object is not compiled.
- Functional testing is indirect: any DML mode-validation test that calls the declared functions exercises the header contract.
