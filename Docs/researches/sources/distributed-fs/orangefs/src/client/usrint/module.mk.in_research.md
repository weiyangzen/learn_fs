# sources/distributed-fs/orangefs/src/client/usrint/module.mk.in

## Purpose
`module.mk.in` contributes the OrangeFS usrint source lists and per-file compiler flags to the repository build system. It decides which files are built into the old library (`OLIBSRC`), the usrint library (`ULIBSRC`), and the common library source set (`LIBSRC`) based on `build_olib` and `build_usrint`.

## Important Build Variables
`DIR` is set to `src/client/usrint`. When `build_olib` is `yes`, `OSRC` contains core PVFS-backed helpers such as `pvfs-path.c`, `mmap.c`, `openfile-util.c`, `iocommon.c`, `request.c`, `ucache.c`, `posix-pvfs.c`, and `env-vars.c`, and the list is appended to `OLIBSRC`. When `build_usrint` is `yes`, the same `OSRC` list is appended to `OLIBSRC`, while `USRC` adds interposition/front-end sources such as `posix.c`, `stdio.c`, `selinux.c`, `overunder.c`, `fts.c`, `glob.c`, `error.c`, and `recursive-remove.c`, and appends them to `ULIBSRC`. `SRC` contains `pvfs-qualify-path.c` and is appended to `LIBSRC`.

## Control Flow
The make fragment is declarative. Build configuration chooses the `build_olib` and `build_usrint` branches. Each branch assigns source lists and appends them to aggregate variables consumed elsewhere by the top-level make logic. The final lines add warning suppressions for `posix.c` and `stdio.c`.

## State And Persistence Behavior
There is no runtime state. The file shapes build outputs by selecting which objects are compiled into which library. Changes here persist only as build metadata.

## Dependencies And Integration Points
The fragment depends on the surrounding OrangeFS make system to define `build_olib`, `build_usrint`, `OLIBSRC`, `ULIBSRC`, `LIBSRC`, and `MODCFLAGS_*` conventions. The inclusion of `fts.c` and `glob.c` in `USRC` explains why those bundled compatibility implementations are part of the usrint build. `mmap.c` and `iocommon.c` are included in both old-library and usrint core lists.

## Risks
`OSRC` is assigned separately inside each branch, so future edits must keep duplicate lists synchronized. The same `OSRC` is appended to `OLIBSRC` in both branches when both build flags are enabled, which may be intentional or may risk duplicate source entries depending on upstream aggregation behavior. Commented-out sources (`acl.c`, `socket.c`) indicate stale or deferred build decisions. Warning suppression is narrow, currently only disabling `-Wnonnull-compare` for `posix.c` and `stdio.c`; similar warnings in other usrint files would fail under stricter builds.

## Test Signals
Build tests should run configurations with only `build_olib`, only `build_usrint`, both enabled, and both disabled if supported. Source-list tests should detect duplicate object entries. Compiler tests should verify that `fts.c`, `glob.c`, `mmap.c`, and `iocommon.c` are included in the expected libraries and that `MODCFLAGS` are applied only to intended files.
