# sources/distributed-fs/ceph-client/tools/bootconfig/Makefile

## Purpose
Builds, tests, installs, and cleans the `bootconfig` user-space command.

## APIs, Types, and Functions
Targets include `all`, `$(OUTPUT)bootconfig`, `test`, `install`, and `clean`. Variables include `bindir`, inferred `srctree`, `LIBSRC`, `CFLAGS`, `ALL_TARGETS`, and `ALL_PROGRAMS`.

## Control Flow, State, and Persistence
The Makefile includes `../scripts/Makefile.include`, derives `srctree` from `CURDIR` when not provided, builds `main.c` with `lib/bootconfig.c` and the wrapper header, runs `test-bootconfig.sh` after build, installs to `$(DESTDIR)$(bindir)`, and removes output artifacts on clean.

## Dependencies and Integration
Depends on the shared kernel bootconfig library source and `tools/bootconfig/include/linux/bootconfig.h` wrapper. Integrated with the Linux tools build system and optional `OUTPUT` directory support.

## Risks and Test Signals
Risks include incorrect `srctree` inference in unusual out-of-tree layouts, tests running unconditionally as part of `all`, and missing `OUTPUT` directory creation from included infrastructure. Test signals are in-tree and out-of-tree builds, `make test`, `make install DESTDIR=...`, and clean rebuilds.
