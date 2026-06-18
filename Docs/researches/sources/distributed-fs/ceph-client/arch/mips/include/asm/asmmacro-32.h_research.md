<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asmmacro-32.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/asmmacro-32.h

**Purpose:** Defines 32-bit MIPS assembly macros for FPU state save/restore and nonscratch CPU register context operations.

**Important APIs/types/functions:** `fpu_save_single`, `fpu_restore_single`, `cpu_save_nonscratch`, and `cpu_restore_nonscratch`.

**Control flow:** Assembly macro expansion stores/restores FPR even registers and FCR31, and saves/restores callee-saved GPRs plus stack/frame/return registers.

**State, dependencies, integration:** Depends on generated thread offsets and register definitions. Used by context switch and FPU handling code.

**Risks and test signals:** Offset or register omissions corrupt task context. Test context switching with FPU users, signal delivery, and 32-bit ABI preemption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asmmacro-32.h -->
