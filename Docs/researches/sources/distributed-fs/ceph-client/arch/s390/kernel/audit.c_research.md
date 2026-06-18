# sources/distributed-fs/ceph-client/arch/s390/kernel/audit.c

## Purpose
Provides s390 syscall classification tables for Linux audit. It maps selected syscall numbers to audit classes and registers generic audit class arrays for read, write, directory-write, attribute-change, and signal operations.

## Important APIs, Types, And Functions
`audit_classify_arch()` returns 0 for architecture classification. `audit_classify_syscall(int abi, unsigned syscall)` maps `open`, `openat`, `socketcall`, `execve`, and `openat2` to special audit classes and returns `AUDITSC_NATIVE` otherwise. `audit_classes_init()` registers class arrays included from asm-generic headers.

## Control Flow
At initcall time, the class arrays are registered. During audit processing, the generic audit layer calls the classify functions for syscall events and uses the registered bitmaps to decide rule matching.

## State And Persistence
The registered class arrays become audit subsystem state for the lifetime of the kernel. There is no file persistence.

## Dependencies And Integration Points
Depends on Linux audit core, s390 syscall numbers, and asm-generic audit class include files. It integrates syscall entry reporting with architecture-neutral audit filtering.

## Risks And Edge Cases
New s390 syscall numbers may need class updates. `audit_classify_arch()` is trivial, so ABI distinctions must be handled elsewhere if they matter. `socketcall` exists for compatibility paths and must remain correctly classified.

## Test Signals
Signals include audit syscall filter tests for open/openat/openat2/execve/socketcall, build checks after syscall table changes, and audit rule matching on s390 systems.
