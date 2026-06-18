## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/feature-fixups.h

Purpose: defines the PowerPC assembly metadata format and macros for CPU, MMU, firmware, and security-mitigation feature alternatives.

Important APIs/types/functions: `BEGIN_FTR_SECTION*`, `END_FTR_SECTION*`, `FTR_SECTION_ELSE`, `ALT_FTR_SECTION_END*`, MMU/FW variants, `ASM_FTR_IF*`, `ASM_MMU_FTR_IF*`, LWSYNC and barrier fixup section macros, BTB flush section macros, fixup boundary symbols, `apply_feature_fixups()`, `update_mmu_feature_fixups()`, and `setup_feature_keys()`.

Control flow: assembly wraps primary and alternate instruction sequences, emits relative offset table entries into feature-specific sections, and enforces alternate size constraints. Runtime fixup code scans those sections and patches instructions based on CPU/MMU/firmware masks. Security slots emit additional single-offset tables for entry/exit, uaccess, RFI, nospec, and BTB flush patching.

State and persistence: fixup tables persist in the kernel image and may be consumed during boot or runtime MMU feature updates. `static_key_feature_checks_initialized` and fallback symbols coordinate feature checks and mitigations.

Dependencies and integration: depends on assembler semantics, asm constants, Clang/GNU assembler differences, CPU/MMU/firmware feature masks, exception headers, barrier code, and jump-label feature keys.

Risks and test signals: relative offsets assume fixup tables follow code, and alternate code must not be larger than its patch slot. Incorrect table format can patch arbitrary code. Test signals include all PowerPC builds, objdump/fixup table inspection, boot-time alternatives, runtime MMU feature updates, Spectre/L1D mitigation toggles, Clang/GCC assembler coverage, and vDSO32 offset handling.
