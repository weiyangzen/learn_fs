# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn401/dcn401_dpp_cm.c

## Purpose
`dcn401_dpp_cm.c` implements DCN401-specific cursor color-management helpers. It programs cursor attributes, cursor enable state, optional cursor FP bias/scale, and a cursor CSC matrix block, though the public cursor matrix entry currently forces bypass.

## Important APIs, types, and functions
- `dpp401_set_cursor_attributes()` programs cursor mode, expansion, ROM degamma enable, monochrome colors, and mirrors state into `dpp_base->att`.
- `dpp401_set_cursor_position()` only toggles cursor enable state for DPP-side cursor control and mirrors it into `pos`/`att` snapshots.
- `dpp401_set_optional_cursor_attributes()` programs G/Y and RB/CRCB cursor FP scale/bias register pairs and records them in software state.
- `dpp401_set_cursor_matrix()` is the public function-table callback for cursor matrix setup; it currently ignores caller inputs and forces bypass through `COLOR_SPACE_UNKNOWN`.
- Local `dpp401_program_cursor_csc()` can program cursor matrix set A or B from color-space tables or caller entries and switch `CUR0_MATRIX_MODE`.

## Control flow
Cursor attribute programming determines whether cursor ROM degamma is required from the cursor color format and attribute flags, writes `CURSOR0_CONTROL` unless cursor offload is active, writes monochrome cursor colors when needed, and updates software attribute shadow fields. Position programming reduces to enable/disable: if the desired enable bit differs from the cached state, it writes `CUR0_ENABLE` unless offloaded, then updates cached position/attribute bits.

Optional attributes program two register pairs so G/Y and RB/CRCB channels share the provided bias and scale. The local cursor CSC helper bypasses non-YCbCr color spaces, otherwise selects a built-in matrix or supplied table, alternates matrix set A/B based on `CUR0_MATRIX_MODE_CURRENT`, writes matrix registers with `cm_helper_program_color_matrices()`, and selects the new set. The public `dpp401_set_cursor_matrix()` currently bypasses this logic unconditionally.

## State and persistence behavior
State is mirrored in `dpp_base->att` and `dpp_base->pos` for cursor controls and in hardware cursor/CM registers. Cursor offload suppresses direct register writes but still updates software shadows. There is no persistence outside runtime kernel memory and registers.

## Dependencies and integration points
The file depends on `dcn401_dpp.h`, register helpers, DC color/cursor types, `dcn10_cm_common.h` matrix tables, and conversion helpers. Its callbacks are wired by `dcn401_dpp.c` and reused by DCN42.

## Risks and edge cases
`dpp401_set_cursor_matrix()` currently discards caller color space and matrix inputs, so cursor CSC is always bypassed despite local support for matrix programming. That may be intentional pending cursor matrix information, but it is a functional limitation. Cursor offload paths rely on software shadow updates remaining consistent with offloaded hardware state. Matrix programming assumes register set A/B fields and shifts are compatible with `color_matrices_reg` using only C11/C12 shift metadata.

## Test signals
Cursor tests should cover all cursor formats, ROM degamma flag behavior, mono cursor colors, cursor enable transitions with and without offload, optional FP scale/bias, YCbCr cursor CSC expectations, and regression tests documenting that `dpp401_set_cursor_matrix()` currently forces bypass.
