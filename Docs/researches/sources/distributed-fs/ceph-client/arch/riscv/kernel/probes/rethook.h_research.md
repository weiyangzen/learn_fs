# sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/rethook.h

Purpose: Declares the RISC-V rethook trampoline symbol used by kretprobe/rethook setup.

Important APIs/types/functions: Declares `arch_rethook_trampoline`.

Control flow: Header-only; C code writes this symbol address into saved return-address slots so execution enters assembly trampoline on function return.

State and persistence: No state.

Dependencies and integration points: Connects `rethook.c` with `rethook_trampoline.S` and generic rethook infrastructure.

Risks and test signals: Declaration/linkage drift breaks kretprobe builds or return redirection. Test kretprobe build/runtime with modules and ftrace enabled.
