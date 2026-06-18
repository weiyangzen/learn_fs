# sources/distributed-fs/ceph-client/arch/parisc/include/asm/rt_sigframe.h

Purpose: defines the PA-RISC realtime signal-frame layout and sizing constants.

Important APIs/types/functions: provides `struct rt_sigframe`, `SIGFRAME`, `FUNCTIONCALLFRAME`, and `PARISC_RT_SIGFRAME_SIZE`.

Control flow: signal delivery builds this frame on the user stack; `rt_sigreturn` validates and consumes it to restore context.

State and persistence: signal frames persist on user stacks while handlers run. Dependencies and integration: used by signal setup/return, ucontext/sigcontext ABI, and compat signal code.

Risks and test signals: frame size/alignment mistakes break signal handlers and unwinding. Test realtime signals, alternate stacks, nested handlers, and sigreturn fault paths.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
