# sources/distributed-fs/ceph-client/arch/um/scripts/Makefile.rules

## Purpose
Defines shared Kbuild rules for compiling UML user-side objects with the correct flags and instrumentation filtering.

## Important APIs, Types, and Functions
Computes `USER_SINGLE_OBJS`, expands `USER_OBJS` into object paths, customizes `c_flags` for user objects to include `USER_CFLAGS`, `kern_levels.h`, and `user.h`, defines `UNPROFILE_OBJS` with profiling/gcov stripped, removes kernel `NOSTDINC_FLAGS` from `CHECKFLAGS`, and defines the `unprofile` make function.

## Control Flow, State, and Persistence
No runtime behavior. Build-time state determines how host-side UML code and stubs are compiled.

## Dependencies and Integration Points
Included by `os-Linux/Makefile`, `os-Linux/skas/Makefile`, and `kernel/skas/Makefile`. It enforces the boundary between kernel-style and host-user-style compilation.

## Risks and Test Signals
Risks are incorrect flag filtering, missing generated dependency flags, or profiling instrumentation entering stub code. Test with KCOV, gcov, `-pg`, sparse/CHECKFLAGS, and clang/gcc builds.
