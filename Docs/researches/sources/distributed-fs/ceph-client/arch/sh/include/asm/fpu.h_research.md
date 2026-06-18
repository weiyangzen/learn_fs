<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/fpu.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/fpu.h

## Purpose
Defines SH architecture declarations and macros for `fpu` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `asm/ptrace.h`. Key macros/constants include `__ASM_SH_FPU_H`, `save_fpu(tsk)`, `restore_fpu(tsk)`, `release_fpu(regs)`, `grab_fpu(regs)`, `fpu_state_restore(regs)`, `__fpu_state_restore(regs)`. Structures include `task_struct`, `user_regset`. Functions or extern declarations include `float_raise`, `float_rounding_mode`, `save_fpu`, `restore_fpu`, `fpu_state_restore`, `__fpu_state_restore`, `do_fpu_inst`, `init_fpu`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `asm/ptrace.h`. Kconfig-sensitive paths mention `CONFIG_SH_FPU`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 72 lines, 1707 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/fpu.h -->
