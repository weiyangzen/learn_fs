# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn30/display_mode_vba_30.h

## Purpose

`display_mode_vba_30.h` is the public declaration header for the DCN 3.0 VBA implementation. It exposes the small set of functions in `display_mode_vba_30.c` that other DML/DCN code can call: the selected-state recalculation entry, the full mode-support solver, and two reusable helper calculations for writeback DISPCLK and source-format block geometry.

The header deliberately contains no implementation logic and no persistent state. It is a source-tree-aligned contract between the DCN30 DML implementation and its callers.

## Important APIs, Types, And Functions

- `dml30_recalculate(struct display_mode_lib *mode_lib)`: runs the selected-mode DCN30 recalculation path and writes results into `mode_lib->vba`.
- `dml30_ModeSupportAndSystemConfigurationFull(struct display_mode_lib *mode_lib)`: runs full DCN30 mode validation and system-configuration selection across voltage/resource states.
- `dml30_CalculateWriteBackDISPCLK(...)`: computes writeback DISPCLK demand from scaling taps, ratios, timing, destination width, source width, and line-buffer size.
- `dml30_CalculateBytePerPixelAnd256BBlockSizes(...)`: maps source format and swizzle mode to luma/chroma byte counts and 256-byte block dimensions through output pointers.

The declared types come from the DML/DC display headers: `struct display_mode_lib`, `enum source_format_class`, and `enum dm_swizzle_mode`.

## Control Flow

The header only declares entry points. Normal call flow is that an owning DML/DCN module includes the necessary common DML type definitions, includes this header, fills `struct display_mode_lib`, then calls either `dml30_ModeSupportAndSystemConfigurationFull()` for validation/selection or `dml30_recalculate()` for selected-state result recomputation. The helper declarations can be called independently when a caller only needs writeback clock demand or format block-size metadata.

## State And Persistence Behavior

The header itself owns no state. The two main entry points mutate the caller-owned `struct display_mode_lib`, especially `mode_lib->vba`; the helper functions return values through their return value or output pointer parameters. There is no allocation, reference ownership, file IO, or cross-call persistence in the header.

## Dependencies And Integration Points

The include guard is `__DML30_DISPLAY_MODE_VBA_H__`. The header does not include `display_mode_lib.h` or any enum/type headers itself, so it assumes callers include it in a context where `struct display_mode_lib`, `enum source_format_class`, and `enum dm_swizzle_mode` are already known. In `display_mode_vba_30.c`, this is satisfied by including `../display_mode_lib.h` before this header.

Integration is limited but important: generation-specific DML code and AMD Display Core mode-validation code use these prototypes to invoke the DCN30 VBA solver and shared helper calculations.

## Risks And Edge Cases

- The header is not standalone because it relies on prior type declarations/definitions from DML headers. Including it before the common DML type headers can produce compiler errors, especially for enum parameters.
- The helper functions use many output pointers. Callers must pass non-NULL pointers for every output of `dml30_CalculateBytePerPixelAnd256BBlockSizes()`.
- The function names are generation-specific. Accidentally mixing DCN30 declarations with another generation's implementation can silently produce wrong validation behavior even if signatures are similar.
- The main entry points mutate `mode_lib->vba`; callers must not treat them as pure queries.

## Test Signals

- Compile coverage from files that include `display_mode_vba_30.h` verifies include ordering, type visibility, and prototype/definition agreement.
- API-level tests can call `dml30_CalculateBytePerPixelAnd256BBlockSizes()` for representative formats and tilings and verify byte/block outputs.
- Writeback clock tests can compare `dml30_CalculateWriteBackDISPCLK()` against known vectors for horizontal-limited, vertical-limited, and line-buffer-limited cases.
- Integration validation should exercise both declared main entry points through the normal DCN30 DML mode-validation path and confirm expected `mode_lib->vba` results.
