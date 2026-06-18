<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asmmacro.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/asmmacro.h

**Purpose:** Provides high-level assembler macros for IRQ enable/disable, FPU save/restore, MIPS MT raw encodings, MSA access/save/restore, and MSA upper-lane initialization.

**Important APIs/types/functions:** Includes 32/64-specific macros, defines `local_irq_enable/disable`, `fpu_save_16even/16odd/double`, `fpu_restore_*`, `_EXT`, `DMT/EMT/DVPE/EVPE/MFTR/MTTR`, MSA load/store/control helpers, `msa_save_all`, `msa_restore_all`, and `msa_init_all_upper`.

**Control flow:** Macro expansion adapts to CPU_HAS_DIEI, preemption, MIPS ISA revision, microMIPS, toolchain MSA support, and 32/64-bit builds.

**State, dependencies, integration:** Uses thread offsets, hazard macros, MSA definitions, and toolchain feature symbols. It underpins exception, context switch, FPU/MSA, and MIPS MT assembly.

**Risks and test signals:** Raw instruction encodings must match ISA and microMIPS modes; MSA save paths use `$1` and `noat`. Test with and without toolchain MSA mnemonics, MSA user tasks, preemptible IRQ disable paths, and microMIPS builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asmmacro.h -->
