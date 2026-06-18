# sources/distributed-fs/moosefs/mfsmaster/restore.h

## Purpose
`restore.h` exposes the changelog replay entry points for live network replay and changelog-file merge replay.

## Important APIs, Types, And Functions
The header includes `<inttypes.h>` and declares `restore_net(uint64_t lv, const char *ptr, uint32_t *rts)` and `restore_file(void *shfilename, uint64_t lv, const char *ptr, uint8_t verblevel)`.

## Control Flow
`restore_net()` is for one strict operation at the current metadata version. `restore_file()` is for ordered or merged changelog streams and accepts a shared-pointer filename object for diagnostics.

## State, Persistence, And Dependencies
The header does not expose state. `restore_file()` requires its filename argument to be compatible with `sharedpointer.c` (`shp_get/inc/dec`) because the implementation retains the most recent filename.

## Integration Points
`merger.c` calls `restore_file()`. Network replication code calls `restore_net()`. Both functions drive metadata replay through the implementation's module-specific dependencies.

## Risks
The `void *shfilename` type hides the shared-pointer requirement. Passing a raw string would compile but fail at runtime when `shp_get()` treats it as a shared-pointer object.

## Test Signals
Compile and integration tests should cover both entry points. `restore_file()` tests should pass real `shp_new()` filename objects and verify reference counts are balanced after filename changes.
