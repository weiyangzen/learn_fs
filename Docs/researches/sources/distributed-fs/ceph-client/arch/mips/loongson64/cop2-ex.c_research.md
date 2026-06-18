<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/cop2-ex.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/cop2-ex.c

Purpose: Handles Loongson-3 COP2 exceptions, enabling CU2/FPU state and emulating Loongson overridden unaligned load/store instructions.

Important APIs/types/functions: `loongson_cu2_call()` is registered by `loongson_cu2_setup()` with `cu2_notifier()`. It handles `CU2_EXCEPTION`, `CU2_LWC2_OP`, `CU2_SWC2_OP`, `CU2_LDC2_OP`, and `CU2_SDC2_OP`.

Control flow: CU2 unusable exceptions enable CU1/CU2 and restore/init FPU context if necessary. LWC2/SWC2 emulate paired 64-bit GPR/FPR loads and stores. LDC2/SDC2 decode `opcode1` for halfword/word/dword GPR and word/dword FPR unaligned accesses, validate `access_ok()`, perform `Load*`/`Store*`, and advance EPC.

State and persistence: Mutates current task FPU state, CP0 status bits, GPRs/FPRs, and EPC. On faults it restores return address/EPC before fixup or signal delivery.

Dependencies and integration: Uses MIPS COP2 notifier framework, FPU ownership helpers, unaligned emulation macros, branch EPC helpers, and signal/fixup paths.

Risks: FPU ownership transitions around faulting memory operations are delicate; errors can leave stale FPU state. Kernel unaligned FP access deliberately dies. User faults map to SIGSEGV or SIGBUS depending on access failure.

Test signals: Loongson-specific unaligned gsl/gss instructions should complete in userspace, fault addresses should signal correctly, and CU2 unusable exceptions should not fall through to the default notifier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/cop2-ex.c -->
