# sources/distributed-fs/ceph-client/samples/vfs/Makefile

## Purpose
This kbuild fragment declares VFS userspace sample programs: `test-fsmount`, `test-statx`, `mountinfo`, and `test-list-all-mounts`.

## APIs, Types, And Functions
It uses `userprogs-always-y` to always build the listed user programs when samples are enabled. `userccflags` adds include paths for `tools/testing/selftests/` and generated UAPI headers under `usr/include`.

## Control Flow
There is no runtime control flow. During kbuild, the samples build system consumes these variables, compiles each `.c` source into a user program, and applies the specified include directories.

## State And Persistence
No state is stored. Build outputs are produced by the surrounding kbuild machinery, not by this file directly.

## Dependencies And Integration Points
The file integrates with kernel sample kbuild rules and the local VFS sample sources. It depends on generated UAPI headers being available for recent syscalls and constants.

## Risks And Test Signals
The main risk is include-path drift when selftest or generated header locations change. Test signals are successful `make samples/vfs/` builds and all four declared binaries appearing in the sample output.
