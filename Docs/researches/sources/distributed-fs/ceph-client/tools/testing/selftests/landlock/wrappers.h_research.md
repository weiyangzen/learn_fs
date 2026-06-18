# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/wrappers.h

## Purpose

`wrappers.h` provides direct syscall wrappers for Landlock operations and `gettid`, letting selftests build and run even when libc lacks Landlock wrapper functions.

## Important APIs, Types, and Functions

It conditionally defines inline `landlock_create_ruleset()`, `landlock_add_rule()`, and `landlock_restrict_self()` around `syscall(__NR_landlock_*)`. It also defines `sys_gettid()` as `syscall(__NR_gettid)`.

## Control Flow and State

Each wrapper is a straight pass-through to the kernel syscall with the supplied arguments. It stores no state and performs no errno translation beyond the normal syscall behavior.

## Dependencies and Integration Points

It depends on `<linux/landlock.h>`, syscall numbers, and unistd/syscall headers. It is included by standalone helper programs and can coexist with environments that already provide Landlock symbols because each wrapper is guarded by `#ifndef`.

## Risks and Test Signals

Risks include mismatched syscall numbers on unsupported architectures or accidental signature drift from UAPI. Test signals are successful compilation without libc prototypes and expected syscall return/errno behavior in all helper programs.
