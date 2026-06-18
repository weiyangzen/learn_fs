<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/um/Makefile

## Purpose
`um/Makefile` selects x86 UML objects, subarchitecture library objects, and generated user-offset headers.

## Important APIs, types, and functions
It defines `BITS`, core `obj-y`, 32-bit `syscalls_32.o` and checksum/atomic helpers, 64-bit `mem_64.o`, `syscalls_64.o`, `vdso/`, `USER_OBJS`, `user-offsets.s`, and hardening exclusions for `stub_segv.o`.

## Control flow
Kbuild chooses 32/64-bit object names, compiles user-facing objects with `USER_CFLAGS`, generates `include/generated/user_constants.h` from `user-offsets.s`, and includes UML make rules.

## State and persistence behavior
State is build artifacts and generated constants used by ptrace/sysdep headers.

## Dependencies and integration points
It depends on `arch/um/scripts/Makefile.rules`, x86 library objects, and generated headers.

## Risks and edge cases
Missing generated offsets break register indexing shared with host ptrace/ucontext code. Hardening/profiling flags must not instrument syscall stubs.

## Test signals
Signals are complete UML builds for both bitnesses and correct regenerated `user_constants.h` after host ABI changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/Makefile -->
