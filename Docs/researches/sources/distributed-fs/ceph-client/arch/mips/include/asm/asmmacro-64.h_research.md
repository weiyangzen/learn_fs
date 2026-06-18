<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asmmacro-64.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/asmmacro-64.h

**Purpose:** Defines 64-bit MIPS assembly macros for saving and restoring nonscratch CPU registers.

**Important APIs/types/functions:** `cpu_save_nonscratch` and `cpu_restore_nonscratch` operate on thread register save slots.

**Control flow:** Macro expansion stores/restores s0-s7, sp, fp, and restore also loads ra.

**State, dependencies, integration:** Used by low-level context switch paths and depends on generated thread offsets.

**Risks and test signals:** Register-save ABI mistakes cause rare task corruption. Test 64-bit context switching, preemption, and exception return under stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asmmacro-64.h -->
