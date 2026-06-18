# sources/distributed-fs/orangefs/src/apps/fuse/module.mk.in

## Purpose
This makefile fragment conditionally adds the OrangeFS FUSE application to the build when `BUILD_FUSE` is enabled. It describes the FUSE app source list, target path, and configure-derived compiler/linker flags.

## Important APIs, Types, and Functions
There are no C APIs in this file. The important build variables are `DIR := src/apps/fuse`, `FUSESRC += $(DIR)/pvfs2fuse.c`, `FUSE := $(DIR)/pvfs2fuse`, `MODCFLAGS_$(DIR) := @FUSE_CFLAGS@`, and `MODLDFLAGS_$(DIR) := @FUSE_LDFLAGS@`.

## Control Flow
The whole fragment is guarded by `ifdef BUILD_FUSE`. If the configure/build system does not define that variable, no FUSE sources, target, or module flags are emitted. If enabled, the top-level build receives one source file and the FUSE-specific flags substituted by configure.

## State and Persistence
The file does not manage runtime state. Its persistent effect is on generated build metadata and the final `src/apps/fuse/pvfs2fuse` binary when the build runs.

## Dependencies and Integration Points
It depends on configure checks that populate `@FUSE_CFLAGS@` and `@FUSE_LDFLAGS@`, and on the larger OrangeFS make system honoring `FUSESRC`, `FUSE`, `MODCFLAGS_*`, and `MODLDFLAGS_*`.

## Risks and Edge Cases
If configure enables `BUILD_FUSE` without valid FUSE flags, compilation or linking will fail at `pvfs2fuse.c`. The fragment supports only one FUSE source; additional FUSE files would need to be added here or through a shared variable. Because flags are directory-scoped, accidental `DIR` reuse in included make fragments would be risky.

## Test Signals
Build with `BUILD_FUSE` enabled and disabled. Enabled builds should compile `src/apps/fuse/pvfs2fuse.c` with FUSE include flags and link the `pvfs2fuse` binary. Disabled builds should not reference FUSE headers or libraries.
