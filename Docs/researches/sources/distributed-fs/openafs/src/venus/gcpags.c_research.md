# sources/distributed-fs/openafs/src/venus/gcpags.c

## Purpose
`gcpags.c` is a minimal administrative helper that asks the cache manager to run garbage collection for PAGs through the `VIOC_GCPAGS` pioctl. Its visible message says "disable gcpags failed", but the operation is the cache-manager pioctl named for PAG garbage collection.

## Important APIs, Types, And Functions
The only function is `main`. It constructs an empty `struct ViceIoctl` and calls `pioctl(0, VIOC_GCPAGS, &blob, 1)`. It includes `AFS_component_version_number.c` for OpenAFS build/version metadata.

## Control Flow
Startup initializes no command parser and accepts no arguments. It zeroes all input/output pointers and sizes in the ioctl blob, invokes the pioctl, prints a `perror` message on nonzero return, and returns the pioctl result directly.

## State And Persistence
There is no local state beyond the stack `ViceIoctl`. The only effect is inside the running cache manager, which may reclaim or alter PAG-related credential bookkeeping. No files or configuration are read or written by this utility.

## Dependencies And Integration Points
The file depends on OpenAFS pioctl declarations from `sys_prototypes.h` and `vioc.h`. It integrates with the cache manager's `VIOC_GCPAGS` implementation and therefore requires a local AFS client with the expected pioctl support.

## Risks And Test Signals
Risks are mostly operational: no argument validation, no privilege precheck, terse error reporting, and direct propagation of a possibly negative syscall return as process exit status. Test signals are successful execution on a running cache manager, expected failure on hosts without AFS, and verification from cache-manager diagnostics that PAG cleanup behavior occurred.
