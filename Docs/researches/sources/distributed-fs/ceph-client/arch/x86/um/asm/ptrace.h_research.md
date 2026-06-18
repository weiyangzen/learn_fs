<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/ptrace.h

## Purpose
`ptrace.h` maps UML `pt_regs` accessors onto the architecture-neutral `uml_pt_regs` saved-register structure.

## Important APIs, types, and functions
It defines regset enum values, `PT_REGS_*` macros, `user_mode()`, syscall-return helpers, thread-area prototypes/stubs, 64-bit high-register accessors, `arch_prctl()`, `user_stack_pointer()`, and `arch_switch_to()`.

## Control flow
Kernel code uses these macros to read/write saved user registers independent of host bitness. 32-bit builds route TLS ptrace operations to `tls_32.c`; 64-bit builds return `-ENOSYS` for thread-area and expose `arch_prctl`.

## State and persistence behavior
State is not stored here; macros access `task->thread.regs.regs` and embedded `uml_pt_regs` fields.

## Dependencies and integration points
It depends on `ptrace-generic.h`, generated frame offsets, bitness-specific sysdep ptrace headers, and task structures.

## Risks and edge cases
Accessor offsets must match `user-offsets.c`; otherwise signal, syscall, and ptrace code modify wrong registers.

## Test signals
Signals are ptrace selftests, signal delivery/return, syscall restart behavior, and core dump register checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/ptrace.h -->
