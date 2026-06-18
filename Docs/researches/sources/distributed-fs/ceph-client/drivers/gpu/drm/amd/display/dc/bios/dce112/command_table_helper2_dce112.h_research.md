# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce112/command_table_helper2_dce112.h

## Purpose
This header declares the DCE112 helper provider for the firmware-parser helper table.

## Important APIs, Types, And Functions
- `dal_cmd_tbl_helper_dce112_get_table2()` returns a `const struct command_table_helper *`.

## Control Flow
No runtime flow is defined in the header.

## State And Persistence
No state is defined. The implementation returns an immutable static helper table.

## Dependencies And Integration Points
It forward-declares `struct command_table_helper` and is included by `command_table_helper2.h`.

## Risks
The closing comment references DCE110, which is cosmetic but can confuse maintainers. Consumers need the shared helper struct to know which callbacks are valid.

## Test Signals
Build/link coverage ensures the provider is present for firmware parser builds.
