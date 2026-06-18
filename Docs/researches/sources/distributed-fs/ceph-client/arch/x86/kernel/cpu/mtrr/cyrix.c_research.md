# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/cyrix.c

Purpose: implements legacy Cyrix Address Range Register operations for 32-bit CPUs with `X86_FEATURE_CYRIX_ARR`.

Important APIs/types/functions: provides `cyrix_mtrr_ops` with `cyrix_set_arr()`, `cyrix_get_arr()`, `cyrix_get_free_region()`, `generic_validate_add_page()`, and `positive_have_wrcomb()`. Internal helpers `prepare_set()` and `post_set()` manage cache/TLB-safe ARR programming.

Control flow: reads use MAPEN in `CX86_CCR3` to access ARR base bytes and RCR type registers, then decode size and type with special ARR7 semantics. Free-region search prefers ARR7 for ranges over 32MB, otherwise scans ARR0-ARR6 and uses ARR7 only for ranges at least 256K. Writes disable PGE if present, disable caches, flush with `wbinvd()`, enable MAPEN, program ARR base/size/type registers, restore CCR3, reenable caches, and restore CR4.

State and persistence: static globals `cr4` and `ccr3` save transient control-register state while programming. Persistent hardware state is in Cyrix ARR/RCR registers until reset or reprogramming.

Dependencies and integration points: selected by `legacy.c` for Cyrix ARR CPUs. Depends on `processor-cyrix.h` accessors, CR0/CR4 cache controls, generic MTRR validation, and common MTRR APIs.

Risks: ARR7 has different enable/type/size encoding from ARR0-ARR6. Programming requires cache-disabled critical sections; missed restore paths can leave caches or PGE misconfigured. The code manipulates legacy CPU-specific configuration registers that are not safe on other vendors.

Test signals: boot on Cyrix ARR hardware or emulator, add/read/delete ranges below and above 32MB, ARR7 minimum-size behavior, write-combining/write-through/write-back/uncacheable type decoding, and suspend/resume through legacy syscore registration.
