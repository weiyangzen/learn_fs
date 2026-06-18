# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/amd.c

Purpose: implements the legacy AMD K6-style MTRR operations for 32-bit systems using the `MSR_K6_UWCCR` register pair rather than generic Intel-style MTRRs.

Important APIs/types/functions: provides `amd_mtrr_ops` with `var_regs = 2`, `amd_set_mtrr()`, `amd_get_mtrr()`, `generic_get_free_region()`, `amd_validate_add_page()`, and `positive_have_wrcomb()`.

Control flow: `amd_get_mtrr()` reads `MSR_K6_UWCCR`, selects lower or upper dword for register 0 or 1, decodes base, type bits, and inverted 128K-granularity size mask. `amd_set_mtrr()` reads both dwords, clears the selected slot for size zero or encodes base/type/negative size mask, flushes cache with `wbinvd()`, then writes the combined MSR. Validation rejects unsupported types, blocks below 128K, non-power-of-two sizes, and misaligned bases.

State and persistence: hardware state lives in `MSR_K6_UWCCR`; no separate heap state is owned. Changes persist only until CPU reset or later MTRR reprogramming.

Dependencies and integration points: selected by `legacy.c` when the boot CPU reports `X86_FEATURE_K6_MTRR`. It plugs into common MTRR APIs through `struct mtrr_ops` and uses generic free-region allocation.

Risks: only two regions exist and size encoding is unusual, so off-by-one mask mistakes can create wrong cacheability over physical memory. The code assumes legacy 32-bit address behavior. Cache flush ordering around MSR writes is required for safe memory type changes.

Test signals: 32-bit AMD K6 feature detection, add/delete WC and UC regions, reject invalid alignment/sizes/types, read back encoded ranges through `/proc/mtrr`, and suspend/resume if legacy syscore support is active.
