# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce112/command_table_helper_dce112.h

## Purpose
This header declares the legacy DCE112 command-table helper provider.

## Important APIs, Types, And Functions
- `dal_cmd_tbl_helper_dce112_get_table()` returns a `const struct command_table_helper *`.

## Control Flow
No executable flow is present.

## State And Persistence
No state is defined; the implementation returns a static immutable table.

## Dependencies And Integration Points
It forward-declares `struct command_table_helper` and is included by shared helper headers and selection code.

## Risks
The closing comment references DCE110, which is minor documentation drift. Consumers must know the table is for the legacy helper path, not helper2.

## Test Signals
Compile/link coverage verifies availability for DCE112 legacy parser builds.
