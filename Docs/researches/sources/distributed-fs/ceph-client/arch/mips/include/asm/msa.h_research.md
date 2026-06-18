# sources/distributed-fs/ceph-client/arch/mips/include/asm/msa.h

Purpose: MIPS SIMD Architecture context and control-register interface.

Important APIs/types/functions: Extern assembly helpers save, restore, initialize upper MSA state, and read/write vector registers in byte/half/word/double formats. Inline `read_msa_wr()` and `write_msa_wr()` dispatch by `enum msa_2b_fmt` and `BUG()` on invalid formats. `enable_msa()`, `disable_msa()`, `is_msa_enabled()`, `thread_msa_context_live()`, `save_msa()`, `restore_msa()`, and `init_msa_upper()` manage feature availability and per-thread state. Toolchain fallback macros encode `cfcmsa` and `ctcmsa`; `__BUILD_MSA_CTL_REG` creates read/write helpers for MSA IR, CSR, ACCESS, SAVE, MODIFY, REQUEST, MAP, and UNMAP. Bitfields define MSAIR and MSACSR rounding, flags, enables, causes, NX, and FS.

Control flow, state, and persistence: Enabling/disabling toggles CP0 Config5 MSAEN with FPU hazards. Thread context live state uses `TIF_MSA_CTX_LIVE`. Persistent state is in task FPU/MSA register storage and MSA control registers.

Dependencies and integration: Depends on `mipsregs.h`, `asm/inst.h`, CPU feature `cpu_has_msa`, task flags, FPU hazards, and assembly save/restore routines. Integrates with context switch, signal handling, ptrace, and exception paths.

Risks and test signals: Invalid format handling, hazard ordering, and constant-folded `cpu_has_msa` paths are key risks. Test MSA context switches, signal save/restore, ptrace register access, disabled-MSA exceptions, and toolchains without native MSA mnemonics.
