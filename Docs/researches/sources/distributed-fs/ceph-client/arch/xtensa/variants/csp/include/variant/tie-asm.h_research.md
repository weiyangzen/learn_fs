# sources/distributed-fs/ceph-client/arch/xtensa/variants/csp/include/variant/tie-asm.h

## Purpose
This assembler HAL header defines save/restore macros for `csp` non-coprocessor optional state and save-area selection masks.

## Important APIs, types, and functions
- `XTHAL_SAS_*` masks classify optional/TIE state by extension origin, compiler use, and ABI lifetime.
- `xchal_ncp_store` saves `THREADPTR`, `ACCLO`, `ACCHI`, `BR`, `SCOMPARE1`, and `M0`-`M3`.
- `xchal_ncp_load` restores the same registers.
- `XCHAL_NCP_NUM_ATMPS` and `XCHAL_SA_NUM_ATMPS` declare one required temporary register.

## Control flow
The macros are expanded by low-level context-switch, signal, or exception code. They call common `xchal_sa_start`/`xchal_sa_align` helpers, conditionally include register groups based on `select` and `alloc`, then issue `rur`, `rsr`, `wur`, `wsr`, and `s32i/l32i` instructions.

## State and persistence behavior
The macros serialize optional architectural state into the save area described by `tie.h`: thread-global `THREADPTR`, compiler-used MAC16 accumulators, and caller-saved boolean/conditional-store/MAC16 registers. They do not manage CPENABLE because CP7 has no save area.

## Dependencies and integration points
The file depends on assembler save-area support macros and this variant's register names. It must match `XCHAL_NCP_SA_LIST()` ordering and sizes in `tie.h`; otherwise thread switches and signal frames restore incorrect state.

## Risks and edge cases
Incorrect `select`/`alloc` use can skip stores while still reserving space, so callers must use the same policy for load and store. The save area must be 4-byte aligned. Register availability must match `core.h` booleans, MAC16, threadptr, and S32C1I options.

## Test signals
Build assembly users, run context-switch stress with TLS/thread pointer use, MAC16-heavy code, boolean-register use, conditional-store paths, and signal delivery/return tests that cross task switches.
