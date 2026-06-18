# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce80/command_table_helper_dce80.h

## Purpose
This header declares the DCE80 command-table helper provider.

## Important APIs, Types, And Functions
- `dal_cmd_tbl_helper_dce80_get_table()` returns a `const struct command_table_helper *`.

## Control Flow
No runtime flow is defined.

## State And Persistence
No state is defined; the provider returns immutable static helper data.

## Dependencies And Integration Points
It forward-declares `struct command_table_helper` and is included by shared helper interfaces and selection code.

## Risks
The header is small; risk is mainly provider linkage or accidental mismatch with the shared helper struct.

## Test Signals
Build/link coverage and DCE8 helper selection at runtime validate this declaration.
