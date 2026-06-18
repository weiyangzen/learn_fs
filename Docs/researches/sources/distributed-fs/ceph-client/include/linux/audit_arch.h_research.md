# sources/distributed-fs/ceph-client/include/linux/audit_arch.h

## Purpose
Architecture-facing audit classification declarations. It names syscall classes used by audit filtering and exposes compat syscall classification data needed when the running task ABI differs from the native kernel ABI.

## Important APIs, Types, And Functions
`enum auditsc_class_t` defines audit syscall classes: native, compat, open, openat, socketcall, execve, openat2, and a count sentinel. The header declares `audit_classify_compat_syscall(int abi, unsigned syscall)` and compat class arrays for write, read, directory, chattr, and signal syscalls.

## Control Flow
This header has no executable flow beyond declarations. Runtime audit classification code uses the enum values and arrays to determine which rule class a syscall belongs to, especially in compatibility ABI paths.

## State And Persistence
The class arrays are extern data owned by architecture/audit implementation files. They are effectively static classification tables, not mutable persistence. The enum values are a compile-time contract between generic audit code and architecture-specific classification code.

## Dependencies And Integration Points
`audit.h` includes this header and uses the classification contract through `audit_classify_syscall()` and related helpers. It integrates with architecture syscall tables, compat syscall support, and audit rule matching for syscall classes such as open/openat/exec/socket operations.

## Risks
Incorrect or stale class tables can cause audit rules to miss compat syscalls or to classify them under the wrong rule bucket. Enum ordering matters because arrays and classifier implementations can treat values as stable indexes. Architecture additions such as new open-like syscalls must be reflected in classification logic.

## Test Signals
Run audit syscall rule tests on native and compat tasks. On 64-bit kernels with 32-bit compat enabled, tests should confirm open, exec, socket, read/write, directory, chattr, and signal rules match the expected compat syscalls.
