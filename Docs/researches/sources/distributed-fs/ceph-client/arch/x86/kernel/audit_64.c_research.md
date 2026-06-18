# sources/distributed-fs/ceph-client/arch/x86/kernel/audit_64.c

## Purpose
This file provides x86-64 audit syscall classification and audit class registration, including IA32 emulation support when enabled.

## Important APIs, Types, and Functions
It defines native audit class arrays for directory writes, reads, writes, attribute changes, and signals. `audit_classify_arch()` recognizes IA32 audit architecture under `CONFIG_IA32_EMULATION`. `audit_classify_syscall()` maps native syscalls such as `open`, `openat`, `openat2`, `execve`, and `execveat` to audit syscall classes and delegates IA32 classification to `ia32_classify_syscall()`. `audit_classes_init()` registers native and optional 32-bit classes.

## Control Flow
At initcall time, audit class arrays are registered. At audit decision time, syscall classification switches on ABI and syscall number to return audit categories.

## State and Persistence
The static arrays persist for audit class lookup after registration. There is no mutable runtime state in this file beyond audit subsystem registration effects.

## Dependencies and Integration Points
It depends on generic audit syscall class include fragments, x86 syscall numbers, `asm/audit.h`, and IA32 emulation audit tables. The audit subsystem consumes the registered class IDs and classification functions.

## Risks and Test Signals
Incorrect classification can under-audit or over-audit file access, exec, signal, or chmod-like operations. Test signals include audit rule tests for native and IA32 syscalls, registration during boot, and expected class matches for `openat2` and `execveat`.
