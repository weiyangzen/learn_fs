# sources/distributed-fs/ceph-client/arch/parisc/include/asm/processor.h

Purpose: defines PA-RISC CPU and thread state, task address-space limits, mmap layout hooks, unaligned-access policy, and user-thread startup ABI.

Important APIs/types/functions: key definitions are `TASK_SIZE`, `DEFAULT_TASK_SIZE*`, `system_cpuinfo_parisc`, `cpuinfo_parisc`, `thread_struct`, `task_pt_regs`, unaligned-control flags, `INIT_THREAD`, `start_thread`, `release_thread`, and CPU identification globals.

Control flow: boot fills CPU info, scheduler stores task register state in `thread_struct`, exec uses `start_thread` to initialize PA-RISC user registers/space IDs/stack ABI, and prctl paths update unaligned-access behavior.

State and persistence: CPU info is global/per-CPU state; each task persists register and layout state in `thread_struct`. Dependencies and integration: ties together PDC, ptrace, ELF, MM, scheduler, and syscall return paths.

Risks and test signals: PA-RISC has unusual stack and argument ABI; errors break every exec. Test native/compat exec, mmap layout, unaligned access prctl, context switching, and ptrace register views.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
