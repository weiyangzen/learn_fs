# sources/distributed-fs/ceph-client/arch/xtensa/variants/test_kc705_hifi/include/variant/tie-asm.h

## Purpose
This generated Xtensa variant header provides assembler save and restore macros for optional non-coprocessor state and configured TIE coprocessor state on the `test_kc705_hifi` core. It is not meant for direct inclusion; it feeds lower-level Xtensa HAL and kernel context-switch assembly that needs exact save-area layout knowledge.

## Important APIs, types, and macros
The public surface is assembler macros and constants rather than C types. `XTHAL_SAS_*` bitmasks classify save-area entries by option/TIE source, compiler use, and ABI lifetime. `XTHAL_SAS3()` composes those selectors. `xchal_ncp_store` and `xchal_ncp_load` save and restore non-coprocessor optional state: `THREADPTR`, MAC16 `ACCLO`/`ACCHI`, `M0` through `M3`, `BR`, and `SCOMPARE1`. `xchal_cp1_store` and `xchal_cp1_load`, aliased as `xchal_cp_AudioEngineLX_store/load`, handle AudioEngineLX coprocessor state. Empty `xchal_cpN_store/load` macros are emitted for unconfigured coprocessor IDs. `XCHAL_NCP_NUM_ATMPS`, `XCHAL_CP1_NUM_ATMPS`, and `XCHAL_SA_NUM_ATMPS` document scratch-register needs.

## Control flow
Each save/load macro begins with `xchal_sa_start`, aligns the caller-provided save-area pointer via `xchal_sa_align`, conditionally emits stores or loads according to `select`, and optionally advances offsets for allocated-but-not-selected categories via `alloc`. The NCP flow writes compact 4-byte special/user registers. The CP1 flow saves six AudioEngineLX user registers, sixteen `aed` 64-bit registers, and four alignment registers, using pointer bumps after 64-byte groups.

## State and persistence behavior
The file defines volatile CPU execution state layout for context save areas. It does not persist state by itself; persistence is the caller-provided memory block. Layout must match `tie.h` sizes: NCP state is 36 bytes, CP1 state is 184 bytes, and the total aligned state is 240 bytes. The macros intentionally exclude zero-overhead loop registers.

## Dependencies and integration points
The macros depend on Xtensa assembler support for `rur.*`, `wur.*`, `rsr.*`, `wsr.*`, `AE_S64.I`, `AE_L64.I`, `AE_SALIGN64.I`, `AE_LALIGN64.I`, and HAL helper macros such as `xchal_sa_start` and `xchal_sa_align`. They integrate with Xtensa kernel context switch, signal frame, exception, and coprocessor enable paths that include generated variant headers.

## Risks
The highest risk is layout drift between this assembler header and C metadata in `tie.h`; a mismatch corrupts task or interrupt context. The macros clobber the pointer and first scratch register, so callers must satisfy the contract. The CP1 macro updates `.Lxchal_pofs_` and `.Lxchal_ofs_` in a non-obvious way after pointer increments; assembler helper bugs or manual changes can silently break save-area offsets.

## Test signals
Useful signals are Xtensa allmodconfig or defconfig builds for the variant, assembler compilation of context-switch files that expand these macros, runtime context-switch tests while using AudioEngineLX registers, and ABI checks comparing save-area sizes and offsets against `XCHAL_*_SA_LIST` in `tie.h`.
