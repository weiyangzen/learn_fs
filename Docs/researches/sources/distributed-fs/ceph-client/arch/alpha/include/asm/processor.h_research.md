<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/processor.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/processor.h

**Purpose:** Defines Alpha user address-space limits, stack tops, thread structure shell, start-thread entry point, stack inspection helpers, and prefetch primitives.

**Important APIs/types/functions:** `TASK_SIZE`, `STACK_TOP`, `STACK_TOP_MAX`, `TASK_UNMAPPED_BASE`, `struct thread_struct`, `INIT_THREAD`, `start_thread`, `__get_wchan`, `KSTK_EIP`, `KSTK_ESP`, `cpu_relax`, `prefetch`, and `prefetchw`.

**Control flow:** Exec and signal code initialize user register state through `start_thread`; scheduler/debug code reads saved PC/SP from `pt_regs`; prefetch helpers emit Alpha prefetch instructions.

**State and persistence behavior:** Alpha keeps almost no C-level `thread_struct` state here; key task state lives in `thread_info` and PAL PCB fields.

**Dependencies and integration points:** Depends on `ptrace` register layout, task stacks, scheduler code, and Alpha assembler instructions.

**Risks:** Address constants are ABI-sensitive. Wrong `KSTK_ESP` indexing into `pt_regs` breaks proc/debug output and stack unwinding.

**Test signals:** Exec, ptrace, core dump, proc stack reporting, and scheduler tests; compile tests for prefetch intrinsics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/processor.h -->
