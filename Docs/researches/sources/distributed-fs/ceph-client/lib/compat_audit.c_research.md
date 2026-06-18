# sources/distributed-fs/ceph-client/lib/compat_audit.c

## Purpose

`sources/distributed-fs/ceph-client/lib/compat_audit.c` supplies audit syscall classification tables and classification logic for compat 32-bit syscalls.

## Important APIs, Types, and Functions

The file defines `compat_dir_class`, `compat_read_class`, `compat_write_class`, `compat_chattr_class`, and `compat_signal_class` arrays, each populated from asm-generic audit headers and terminated by `~0U`. It also defines `audit_classify_compat_syscall(int abi, unsigned syscall)`.

## Control Flow

Classification switches on the compat syscall number and returns specialized classes for `open`, `openat`, `socketcall`, `execve`, and `openat2` when those syscall numbers exist; all other syscalls return `AUDITSC_COMPAT`.

## State and Persistence Behavior

The arrays are static kernel data used by audit logic. There is no runtime mutation in this file.

## Dependencies and Integration Points

Dependencies include compat syscall numbers from `asm/unistd32.h`, audit architecture constants, and asm-generic audit class include files. Audit code consumes the arrays and classifier to apply policy to compat tasks.

## Risks and Edge Cases

Syscall-number availability is architecture-dependent, so conditional cases must match the compat table. Missing a newly special-cased syscall can cause less precise audit classification. The `abi` argument is unused here, so ABI-specific distinctions must be handled elsewhere if needed.

## Test Signals

Signals include build coverage on compat architectures with and without optional syscall numbers, audit classification tests for open/openat/openat2/socketcall/execve/default, and table terminator checks for each class array.

## Read Coverage

Source read size: 56 lines, 1002 bytes.
