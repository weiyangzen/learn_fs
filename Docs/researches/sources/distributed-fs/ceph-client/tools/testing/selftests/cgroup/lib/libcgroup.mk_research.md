# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/lib/libcgroup.mk

## Purpose

`libcgroup.mk` is the make fragment that builds the shared cgroup utility object for kselftest cgroup programs. The complete 19-line file was read.

## Important APIs, Types, and Functions

It defines `CGROUP_DIR`, `LIBCGROUP_C`, `LIBCGROUP_O`, `LIBCGROUP_O_DIRS`, appends `-I$(CGROUP_DIR)/lib/include` to `CFLAGS`, declares `EXTRA_HDRS` for `clone3_selftests.h`, adds a directory creation rule, compiles `lib/cgroup_util.c` into `$(OUTPUT)/lib/cgroup_util.o`, and appends that object to `EXTRA_CLEAN`.

## Control Flow

Make evaluates the object path, creates output subdirectories, then compiles `cgroup_util.c` with the common selftest compiler variables. Test Makefiles include this fragment to link `$(LIBCGROUP_O)` into generated programs.

## State and Persistence Behavior

It persists build artifacts under `$(OUTPUT)` and records cleanup metadata through `EXTRA_CLEAN`; it does not affect runtime test state.

## Dependencies and Integration Points

It depends on selftest `lib.mk` conventions (`selfdir`, `OUTPUT`, `CC`, `CFLAGS`, `CPPFLAGS`, `TARGET_ARCH`, `EXTRA_CLEAN`) and the clone3 helper header used by the utility library.

## Risks and Edge Cases

Incorrect `selfdir` or `OUTPUT` values break include and object paths. The `dirname | uniq` computation assumes a simple object list. Any change to `cgroup_util.c` dependencies must update `EXTRA_HDRS` or rely on broader make dependency behavior.

## Test Signals

Successful cgroup selftest builds and cleanup of `$(OUTPUT)/lib/cgroup_util.o` validate this fragment.
