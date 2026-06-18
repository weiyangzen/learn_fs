<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/module.mk.in -->
# sources/distributed-fs/orangefs/src/apps/user/module.mk.in

## Purpose
Build-system fragment listing OrangeFS user utilities compiled when the user-interface layer is enabled.

## Important APIs, Types, And Functions
The fragment sets `DIR := src/apps/user` and, when `build_usrint` is `yes`, appends `getmattr.c`, `ofs_rm.c`, `ofs_cp.c`, `ofs_graphite_driver.c`, `ofs_setdirhint.c`, `pvfs2-rm.c`, and `setmattr.c` to `USERSRC`.

## Control Flow
The conditional `ifeq ($(build_usrint),yes)` gates all utility sources. No generated target appears when user-interface support is disabled.

## State And Persistence
No runtime state. The only state is make variable composition during build generation.

## Dependencies And Integration Points
Consumed by the top-level OrangeFS automake/make machinery. It ties user-space utilities to the `usrint` build option and shared headers such as `orange.h`.

## Risks And Test Signals
Risks are stale lists, missing `graphite_connect_test.c` if expected as a built utility, and inconsistent gating if a utility no longer requires `usrint`. Test signals are builds with `build_usrint=yes/no` and checking expected binaries in the install tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/module.mk.in -->
