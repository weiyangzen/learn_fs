# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce110/command_table_helper_dce110.h

## Purpose
This header declares the DCE110 command-table helper provider.

## Important APIs, Types, And Functions
- `dal_cmd_tbl_helper_dce110_get_table()` returns a `const struct command_table_helper *`.

## Control Flow
The header has no runtime flow; it exposes the provider used by shared helper selection.

## State And Persistence
No state is defined. The provider returns immutable static data from the C file.

## Dependencies And Integration Points
It forward-declares `struct command_table_helper` and is included by helper selection and helper struct headers.

## Risks
Only the provider is declared; consumers must include the shared helper struct for member semantics. Header guard naming is DCE110-specific and should remain unique.

## Test Signals
Compile/link success verifies the provider is present when DCE110 helper selection is enabled.
