# sources/distributed-fs/ceph-client/arch/x86/kernel/ptrace.c

## Purpose
Implements x86 ptrace register access, debug register emulation via perf hardware breakpoints, compat/x32 ptrace ABI handling, user regset views, xstate sizing, and SIGTRAP reporting helpers.

## APIs, Types, And Functions
Defines 32-bit and 64-bit regset enums, `struct pt_regs_offset`, register offset/name query APIs, general register get/set functions, debug register helpers, I/O permission regset access, `ptrace_disable()`, `arch_ptrace()`, `compat_arch_ptrace()`, `update_regset_xstate_info()`, `task_user_regset_view()`, `send_sigtrap()`, and `user_single_step_report()`. Regset tables include general, FP, XFP, XSTATE, TLS, IOPERM, and shadow-stack SSP where configured.

## Control Flow
Native `arch_ptrace()` handles USER-area peek/poke, full general/FP register transfers, 32-bit TLS area requests, and 64-bit `PTRACE_ARCH_PRCTL`; unknown requests fall back to generic ptrace. Register writes validate segment selectors, mask user-writable EFLAGS, and keep FS/GS base semantics aligned with architecture mode. Debug register writes create or modify perf hardware breakpoints, emulate DR6/DR7, and roll back DR7 changes on failure. Compat code translates IA32 and x32 layouts to native `pt_regs` and thread fields. Regset view selection uses current task code segment mode.

## State And Persistence
Ptrace-visible state lives in stopped tasks' `pt_regs`, `thread_struct` segment/base fields, `virtual_dr6`, `ptrace_dr7`, `ptrace_bps[]`, TLS descriptors, I/O bitmap, and FPU/xstate buffers. `xstate_fx_sw_bytes` and regset XSTATE sizes are initialized once after xstate enumeration.

## Dependencies And Integration
Depends on generic ptrace, perf hardware breakpoints, FPU regset code, LDT/TLS code, syscall ABI helpers, security/seccomp/audit layers, task stacks, nospec array indexing, shadow-stack regset support, and `process_64.c` FS/GS arch-prctl helpers.

## Risks And Test Signals
This is a user ABI boundary. Risks include accepting invalid selectors, exposing wrong ABI register layouts, debug breakpoint leaks, incompatible xstate sizes, or incorrect compat sign/zero extension. Test signals include ptrace selftests, GDB on 32/64/x32 tasks, hardware breakpoint tests, core dump regset validation, xstate/AMX changes, IOPERM dump tests, and single-step/SIGTRAP behavior.
