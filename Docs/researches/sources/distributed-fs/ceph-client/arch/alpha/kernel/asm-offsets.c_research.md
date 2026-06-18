<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/asm-offsets.c -->
## sources/distributed-fs/ceph-client/arch/alpha/kernel/asm-offsets.c

**Purpose:** Generates Alpha assembly offsets for `thread_info`, `pt_regs`, `switch_stack`, and machine-vector fields.

**Important APIs/types/functions:** `DEFINE(TI_FLAGS)`, `TI_FP`, `TI_STATUS`, `SP_OFF`, `SIZEOF_PT_REGS`, `SWITCH_STACK_SIZE`, `HAE_CACHE`, and `HAE_REG`.

**Control flow:** Kbuild compiles this file specially and post-processes emitted `DEFINE` statements into an offsets header consumed by assembly files.

**State and persistence behavior:** No runtime state; generated constants must match C structure layout.

**Dependencies and integration points:** Depends on Linux kbuild offset macros, scheduler/ptrace headers, and `asm/machvec.h`.

**Risks:** Stale offsets break entry, trap, and context-switch assembly in ways that are hard to diagnose.

**Test signals:** Full Alpha build, inspect generated asm-offsets, and boot syscall/trap/context-switch paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/asm-offsets.c -->
