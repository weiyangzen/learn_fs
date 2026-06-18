<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/machine_check.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/machine_check.c

Purpose: decodes and logs PPC4xx/440A/47x machine-check causes before returning to generic exception handling.

Important APIs/types/functions: `machine_check_4xx()` distinguishes instruction versus data machine checks using ESR; `machine_check_440A()` decodes MCSR bits for PLB read/write, TLB parity, cache parity, and imprecise checks; `machine_check_47x()` adds 47x GPR/FPR parity and imprecise fields.

Control flow: architecture exception code calls the appropriate function based on CPU family. Instruction synchronous checks clear `ESR_IMCP`. Data checks read MCSR, print set cause bits, flush instruction cache for I-cache parity, clear MCSR by writing it back, and return 0.

State and persistence: hardware ESR/MCSR state is cleared for handled bits; instruction cache may be flushed on parity errors. No software state is stored.

Dependencies and integration: depends on `pt_regs->esr`, special registers `SPRN_ESR`/`SPRN_MCSR`, MCSR bit definitions, cache flush helpers, and CPU-family exception dispatch.

Risks and test signals: functions return 0 after severe errors, leaving policy to higher-level code; logging only in kernel mode may miss user-context nuance; exact MCSR bit meanings differ by CPU. Test injected instruction/data machine checks, cache parity paths, 47x parity bits, and that ESR/MCSR clearing prevents repeated exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/machine_check.c -->
