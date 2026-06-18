## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/exception-64s.h

Purpose: defines Book3S 64-bit exception save offsets and assembly slots for speculation/security fixups around interrupt entry and return.

Important APIs/types/functions: PACA offsets `EX_R9` through `EX_CTR`, `MAX_MCE_DEPTH`, slot macros `STF_ENTRY_BARRIER_SLOT`, `STF_EXIT_BARRIER_SLOT`, `ENTRY_FLUSH_SLOT`, `SCV_ENTRY_FLUSH_SLOT`, `RFI_FLUSH_SLOT`, return macros `RFI_TO_*`, `HRFI_TO_*`, `RFSCV_TO_USER`, and C prototype `do_uaccess_flush()`.

Control flow: assembler entry/return paths expand to feature-fixup sections plus placeholder nops. Runtime feature fixups can replace those nops with barriers or cache flushes before entry to kernel or return to user/guest. Return macros execute `rfid/hrfid/rfscv` and branch to fallback flush code if patched behavior requires it.

State and persistence: PACA save areas hold interrupted register state. Feature-fixup tables and fallback labels persist in the kernel image and are patched/used based on CPU/firmware mitigations.

Dependencies and integration: depends on `feature-fixups.h`, low-level exception assembly, security mitigation code, membarrier sync-core semantics, uaccess flushing, and machine-check recursion handling.

Risks and test signals: slot sizes must match patch code and return instructions must remain context synchronizing. Mistakes can create security regressions or broken interrupt returns. Test signals include Book3S boot, syscall/SCV paths, Spectre/L1D mitigation toggles, KVM guest returns, machine-check recursion tests, and objdump verification of fixup sections.
