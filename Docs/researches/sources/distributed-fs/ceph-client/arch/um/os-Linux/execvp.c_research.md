# sources/distributed-fs/ceph-client/arch/um/os-Linux/execvp.c

## Purpose
Provides an allocation-controlled `execvp` implementation for UML helper processes.

## Important APIs, Types, and Functions
`execvp_noalloc()` searches `PATH` for a command unless the file contains `/`, using a caller-supplied buffer for path construction. It preserves glibc-like error priority for `EACCES` and ignores path-search misses such as `ENOENT`, `ESTALE`, `ENOTDIR`, `ENODEV`, `ETIMEDOUT`, and `ENOEXEC`.

## Control Flow, State, and Persistence
No persistent state. The function attempts `execv()` repeatedly and only returns negative errno on failure. A `TEST` block supplies a standalone test harness.

## Dependencies and Integration Points
Used by `helper.c` to exec host helper commands after clone without allocating in the child. Depends on environment `PATH` and a buffer sized by the caller, normally `PATH_MAX`.

## Risks and Test Signals
Risks are buffer sizing assumptions, PATH corner cases, and differing shell fallback semantics for `ENOEXEC`. Test empty file name, direct paths, empty PATH components, permission-denied binaries, and missing helpers.
