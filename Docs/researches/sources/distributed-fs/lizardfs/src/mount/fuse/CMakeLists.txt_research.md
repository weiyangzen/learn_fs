# sources/distributed-fs/lizardfs/src/mount/fuse/CMakeLists.txt

## Purpose
This CMake file builds FUSE-based mount executables for FUSE 2 and FUSE 3 when the corresponding libraries are found.

## Important APIs, Types, And Functions
- `collect_sources(MOUNT_FUSE)` gathers FUSE mount sources.
- `add_executable(mfsmount ...)` builds the FUSE 2 executable with `FUSE_USE_VERSION=26`.
- `add_executable(mfsmount3 ...)` builds the FUSE 3 executable with `FUSE_USE_VERSION=30` and `CFGNAME=mfsmount`.
- Each target links `mount`, `mfscommon`, and the relevant FUSE library and installs to `${BIN_SUBDIR}`.

## Control Flow
The build enters current include scope, collects sources, conditionally creates/install `mfsmount` if `FUSE_FOUND`, and conditionally creates/install `mfsmount3` if `FUSE3_FOUND`.

## State And Persistence
Build artifacts only; no runtime state.

## Dependencies And Integration Points
It depends on parent-provided `${MOUNT_FUSE_MAIN}`, `${MOUNT_FUSE_SOURCES}`, FUSE discovery variables, and install directory variables.

## Risks
- Compile definitions differ between FUSE 2 and 3; shared source must remain compatible with both.
- If both FUSE versions are found, both executables are installed and must not conflict in config handling.

## Test Signals
CI should configure with FUSE 2 only, FUSE 3 only, both, and neither, verifying target creation and compile definitions.
