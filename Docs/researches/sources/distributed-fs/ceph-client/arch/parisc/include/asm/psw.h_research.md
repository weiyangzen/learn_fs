# sources/distributed-fs/ceph-client/arch/parisc/include/asm/psw.h

Purpose: defines PA-RISC Processor Status Word bits, kernel/user PSW masks, real-mode PSW setup, and C bitfield view of PSW state.

Important APIs/types/functions: exports `PSW_*`, `PSW_SM_*`, `KERNEL_PSW`, `REAL_MODE_PSW`, `USER_PSW_MASK`, `USER_PSW`, `struct pa_psw`, and `pa_psw(task)`.

Control flow: boot, trap return, signal, and exec code compose PSW values to enable/disable interrupts, data/address translation, wide mode, and user-visible condition bits.

State and persistence: PSW is live CPU state and saved in task/trap frames. Dependencies and integration: used by `head.S`, `assembly.h`, `processor.h`, `ptrace`, and trap return assembly.

Risks and test signals: wrong user/kernel masks expose privileged state or break wide/narrow execution. Test trap/syscall return, 32-bit/64-bit tasks, signal frames, and ptrace PSW reads/writes.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
