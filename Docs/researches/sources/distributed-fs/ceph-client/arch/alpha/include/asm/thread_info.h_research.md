<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/thread_info.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/thread_info.h

**Purpose:** Defines Alpha `thread_info`, task flags, thread status flags, unaligned-access control mapping, and FPU save helper.

**Important APIs/types/functions:** `struct thread_info`, `INIT_THREAD_INFO`, `current_thread_info`, `THREAD_SIZE_ORDER`, `THREAD_SIZE`, `TIF_*`, `_TIF_*`, `_TIF_WORK_MASK`, `TS_UAC_*`, `TS_SAVED_FP`, `TS_RESTORE_FP`, `SET_UNALIGN_CTL`, `GET_UNALIGN_CTL`, `__save_fpu`, and `save_fpu`.

**Control flow:** Entry/exit assembly and scheduler code inspect `_TIF_WORK_MASK` before returning to user mode. Unaligned-control helpers translate user sysinfo bits into thread status bits. `save_fpu` records FP state once per thread until restored.

**State and persistence behavior:** Per-task state includes flags, status, CPU id, PCB, address limit, FP registers, FP control, and syscall number.

**Dependencies and integration points:** Depends on Alpha processor, HWRPB, sysinfo constants, task stack layout, and low-level entry/FPU code.

**Risks:** Bit positions are consumed by assembly and userspace unaligned-control ABI. Thread size must match `ptrace.h` frame placement.

**Test signals:** Syscall return work flags, signal/seccomp/audit tracing, unaligned access policy tests, FPU save/restore tests, and assembly offset checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/thread_info.h -->
