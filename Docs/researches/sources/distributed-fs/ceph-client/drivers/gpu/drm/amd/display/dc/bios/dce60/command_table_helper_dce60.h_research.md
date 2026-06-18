# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce60/command_table_helper_dce60.h

## Purpose
This header declares the DCE60/SI command-table helper provider.

## Important APIs, Types, And Functions
- `dal_cmd_tbl_helper_dce60_get_table()` returns a `const struct command_table_helper *`.

## Control Flow
No executable flow is defined.

## State And Persistence
No state is defined; the implementation returns static immutable data.

## Dependencies And Integration Points
It forward-declares `struct command_table_helper` and is included conditionally by the shared helper interface when SI support is configured.

## Risks
Consumers must guard use with `CONFIG_DRM_AMD_DC_SI` availability.

## Test Signals
Build coverage with SI enabled verifies provider linkage.
