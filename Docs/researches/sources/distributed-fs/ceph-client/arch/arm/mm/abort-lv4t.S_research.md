# sources/distributed-fs/ceph-client/arch/arm/mm/abort-lv4t.S

Purpose: implements late data-abort fixup for ARMv4T-class CPUs, where writeback may already have happened before the abort is reported. It decodes faulting ARM or Thumb load/store instructions and repairs base register/SP writeback before invoking common fault handling.

Important APIs/types/functions: exports `v4t_late_abort`. Internal labels handle ARM instruction classes such as `.data_arm_ldmstm`, `.data_arm_lateldrhpost`, `.data_arm_lateldrpreconst`, `.data_arm_lateldrpostreg`, `.data_unknown`, and Thumb classes `.data_thumb_reg`, `.data_thumb_pushpop`, and `.data_thumb_ldmstm`.

Control flow: the entry determines Thumb vs ARM state. With CP15 MMU, it reads FSR/FAR and clears write-related bits; without CP15 MMU it provides zero FSR/FAR. ARM state uses a jump table over instruction bits to classify LDR/STR/LDM/STM/halfword forms, computes offset or register count, and undoes writeback in `pt_regs` when required. Thumb state reads the 16-bit instruction, decodes high opcode bits, repairs SP or base register for push/pop and LDM/STM, and passes unknown instructions to `baddataabort`.

State and persistence: no global state. It mutates the saved register frame in `pt_regs` to undo architectural side effects before `do_DataAbort` sees the fault. Temporary `r9` is saved on the stack in paths needing it.

Dependencies and integration points: selected by `CPU_ABRT_LV4T` for ARM7/ARM720/ARM740-style late-abort CPUs. Integrates with `do_DataAbort`, `baddataabort`, CP15 if available, and the ARM exception vector ABI.

Risks: this is high-risk instruction decoding in exception context. Any unsupported addressing mode falls into bad-data-abort handling. Off-by-one register-count or U/P/W bit errors would corrupt user register state. It assumes specific ARM/Thumb encodings and is not portable to newer instruction sets beyond the selected CPUs.

Test signals: targeted assembly tests for post-index/pre-index LDR/STR, LDRH/STRH, LDM/STM writeback, Thumb push/pop, Thumb LDM/STM, and unknown instruction paths; verify base registers are restored exactly once; test no-MMU and CP15-MMU configurations.
