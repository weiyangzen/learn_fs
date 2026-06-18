# sources/distributed-fs/ceph-client/security/landlock/setup.h

## Purpose

`setup.h` declares global Landlock setup state shared by hook modules and accessors.

## Important APIs, Types, and Functions

It declares `landlock_abi_version`, `landlock_initialized`, `landlock_errata`, `landlock_blob_sizes`, and `landlock_lsmid`.

## Control Flow

Other files use these declarations to index LSM blobs, guard cleanup before initialization, register hook lists with the correct LSM ID, and expose ABI/errata state.

## State and Persistence Behavior

The variables are defined in `setup.c` or syscall code and persist for the running kernel. Some are read-only after init.

## Dependencies and Integration Points

The header depends on LSM hook definitions and is included by most Landlock modules.

## Risks and Test Signals

Declaration/definition mismatch or wrong blob sizes can break all Landlock hooks. Build with varied optional configs and run boot smoke tests plus Landlock selftests.
