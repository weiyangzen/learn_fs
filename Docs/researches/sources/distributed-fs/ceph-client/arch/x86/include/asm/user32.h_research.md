# sources/distributed-fs/ceph-client/arch/x86/include/asm/user32.h

Purpose: IA32-compatible user register/FPU/core-dump structures for 64-bit kernels handling 32-bit tasks and 32-bit core dumps.

Important APIs/types/functions: `struct user_i387_ia32_struct`, `struct user32_fxsr_struct`, `struct user_regs_struct32`, and IA32 `struct user`.

Control flow: no runtime flow; compat ptrace/core dump code fills or reads these fixed layouts for 32-bit tasks.

State/persistence: serialized task register/FPU/core metadata layout. Fields include general registers, segment selectors, eflags, stack/ip, FP state, sizes, start addresses, signal, `u_ar0`, `u_fpstate`, magic, command, and debug registers.

Dependencies/integration: relies on fixed-width `u32`/`__u32` style types from included architecture context. Integrated with compat ptrace, ELF core dumping, and debugger ABI compatibility.

Risks/test signals: padding and field size mistakes break IA32 debuggers and core files. Test 32-bit process ptrace on x86_64, compat core dumps, FP/FXSR register access, debug register export, and gdb/strace compatibility.
