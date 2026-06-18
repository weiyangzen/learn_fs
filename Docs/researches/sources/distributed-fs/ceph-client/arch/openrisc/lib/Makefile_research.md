<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/lib/Makefile -->
# sources/distributed-fs/ceph-client/arch/openrisc/lib/Makefile

## Purpose
Builds OpenRISC architecture library routines.

## Important APIs, Types, And Functions
Adds `delay.o`, `string.o`, `memset.o`, and `memcpy.o` to `obj-y`.

## Control Flow
Kbuild compiles these helpers into the kernel image.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Supports delay loops, usercopy, clear_user, memset, and memcpy declarations/exports.

## Risks
Removing objects breaks low-level architecture APIs and module exports.

## Test Signals
Full kernel link, usercopy tests, delay tests, and string/memory operation smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/lib/Makefile -->
