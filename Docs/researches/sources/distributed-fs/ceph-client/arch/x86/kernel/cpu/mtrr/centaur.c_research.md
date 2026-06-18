# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/centaur.c

Purpose: implements legacy Centaur/VIA WinChip memory control register operations for 32-bit systems that expose `X86_FEATURE_CENTAUR_MCR`.

Important APIs/types/functions: defines `centaur_mcr[8]`, `centaur_mcr_reserved`, `centaur_mcr_type`, and `centaur_mtrr_ops`. Operation callbacks are `centaur_get_free_region()`, `centaur_get_mcr()`, `centaur_set_mcr()`, `centaur_validate_add_page()`, and `positive_have_wrcomb()`.

Control flow: free-region search skips reserved MCR slots and returns empty slots from `mtrr_if->get()`. `centaur_get_mcr()` decodes cached high/low register values into base, negative-mask size, and a type that differs between WinChip and WinChip2. `centaur_set_mcr()` encodes disable or base/size/type values, updates the shadow array, and writes `MSR_IDT_MCR0 + reg`. Validation allows only write-combining on WinChip and write-combining or uncacheable on WinChip2.

State and persistence: maintains a software shadow of eight MCRs in `centaur_mcr[]` and writes hardware MSRs. No disk persistence exists.

Dependencies and integration points: selected by `legacy.c` on Centaur CPUs with MCR support. It implements the `mtrr_ops` contract used by `mtrr.c` and `/proc/mtrr`.

Risks: the file relies on `centaur_mcr_type` and reserved-mask initialization from surrounding CPU setup; if those are wrong, type encoding and allocation are wrong. The shadow array must stay synchronized with MSR writes. Legacy hardware supports fewer memory types than generic MTRRs.

Test signals: boot on WinChip/WinChip2 or emulator with MCR feature, add/read/delete WC and UC entries as appropriate, verify reserved registers are skipped, and confirm `/proc/mtrr` displays expected decoded types.
