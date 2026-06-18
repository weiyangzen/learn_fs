# sources/distributed-fs/lizardfs/tests/set_lizardfs_constants.sh.in

## Purpose
This template emits shell constants describing the compiled LizardFS block geometry, version, and install library path for bash tests.

## Important APIs, Types, and Functions
Configured variables are `LIZARDFS_BLOCKS_IN_CHUNK`, `LIZARDFS_BLOCK_SIZE`, computed `LIZARDFS_CHUNK_SIZE`, normalized `LIZARDFS_VERSION`, `LIZARDFS_INSTALL_LIBDIR`, and `LIZARDFS_INSTALL_FULL_LIBDIR`.

## Control Flow
CMake substitutes `@...@` placeholders into `set_lizardfs_constants.sh`; shell tests source the generated file to use chunk size and install paths.

## State and Persistence Behavior
The generated script is build/install state. It does not mutate runtime state when sourced, except defining variables in the caller shell.

## Dependencies and Integration Points
It depends on CMake package/block constants and on `LIZARDFS_ROOT` being set by the test harness for full library path expansion.

## Risks and Edge Cases
Version normalization strips suffixes after `-`, which may hide prerelease/build metadata. Missing `LIZARDFS_ROOT` produces a relative or incorrect full libdir.

## Test Signals
Build tests should source the generated file and validate numeric chunk size, version normalization, and expected library path.
