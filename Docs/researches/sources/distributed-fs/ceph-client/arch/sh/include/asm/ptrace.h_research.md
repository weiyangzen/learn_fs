<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/ptrace.h

## Purpose
Defines the SH kernel ptrace register view and maps it to the UAPI ptrace layout for tracing and core-dump users.

## Important APIs, Types, And Functions
Includes `linux/stringify.h`, `linux/stddef.h`, `linux/thread_info.h`, `asm/addrspace.h`, `asm/page.h`, `uapi/asm/ptrace.h`. Key macros/constants include `__ASM_SH_PTRACE_H`, `user_mode(regs)`, `kernel_stack_pointer(_regs)`, `arch_has_single_step()`, `REG_OFFSET_NAME(r)`, `REGS_OFFSET_NAME(num)`, `TREGS_OFFSET_NAME(num)`, `REG_OFFSET_END`, `task_pt_regs(task)`. Structures include `pt_regs_offset`, `perf_event`, `perf_sample_data`. Functions or extern declarations include `regs_query_register_offset`, `regs_query_register_name`, `ptrace_triggered`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `linux/stringify.h`, `linux/stddef.h`, `linux/thread_info.h`, `asm/addrspace.h`, `asm/page.h`, `uapi/asm/ptrace.h`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 139 lines, 3834 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/ptrace.h -->
