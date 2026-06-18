<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/pal.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/pal.h

**Purpose:** Wraps Alpha PALcode operations used by the kernel: halt, instruction barriers, drain, TLB invalidation, context switching, interrupt priority, user stack pointer, FP enable, performance monitor writes, and machine-check status.

**Important APIs/types/functions:** `__halt`, `imb`, `draina`, PAL call wrapper macros, `tbi`, `tbisi`, `tbisd`, `tbis`, `tbiap`, `tbia`, and inline helpers such as `rdmces`, `wrmces`, `wrusp`, `rdusp`, `swpipl`, `rdps`, `wrent`, `wrkgp`, `wrvptptr`, and `wrfen`.

**Control flow:** Inline assembly binds PAL call arguments to Alpha calling registers and invokes `call_pal`. TBI helpers encode specific invalidation modes and optional address operands.

**State and persistence behavior:** PAL calls mutate CPU-local privileged state, TB state, interrupt priority, unique/user pointers, FP enable, and machine-check state. Nothing is file-persistent.

**Dependencies and integration points:** Depends on UAPI PAL number definitions and Alpha compiler/register conventions. Used by MMU context, TLB flush, SMP, thread switching, signal/ptrace, machine-check, and shutdown paths.

**Risks:** Register constraints and clobber lists are architecture-critical. Wrong PAL number or argument placement can corrupt CPU state. Some calls have ordering requirements with `mb`, `imb`, and `draina`.

**Test signals:** Alpha boot smoke tests, PAL-assisted TLB flush tests, machine-check recovery paths, signal/user-stack pointer tests, FP enable paths, and shutdown/halt validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/pal.h -->
