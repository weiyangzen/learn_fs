# sources/distributed-fs/ceph-client/arch/xtensa/variants/test_mmuhifi_c3/include/variant/tie.h

## Purpose
This generated Xtensa TIE metadata header describes the coprocessor and save-area layout for the `test_mmuhifi_c3` HiFi2 variant.

## Important APIs, types, and macros
The core has one coprocessor, CP1 `AudioEngineLX`, exposed through `XCHAL_CP_NUM`, `XCHAL_CP_MAX`, `XCHAL_CP_MASK`, `XCHAL_CP1_NAME`, `XCHAL_CP1_IDENT`, and `XCHAL_CP_ID_AUDIOENGINELX`. `XCHAL_CP1_SA_SIZE` is 112 bytes with 8-byte alignment. Non-coprocessor optional state is 12 bytes and consists of `br`, `scompare1`, and `threadptr` in `XCHAL_NCP_SA_LIST`. `XCHAL_CP1_SA_LIST` enumerates four AudioEngineLX user registers, eight `aep` registers, and four `aeq` registers. `XCHAL_TOTAL_SA_SIZE` is 128 bytes. `XCHAL_OP0_FORMAT_LENGTHS` describes FLIX instruction lengths.

## Control flow
The file has no execution flow. The main pattern is macro expansion: clients define `XCHAL_SA_REG` and invoke the save-area list macros to emit code, tables, or metadata.

## State and persistence behavior
The state described here is per-thread CPU and coprocessor state that must be preserved by architecture code. The header itself is static metadata and does not allocate memory or perform persistence.

## Dependencies and integration points
It must match `tie-asm.h` exactly. It is consumed by Xtensa HAL, kernel context switch paths, debugger register enumeration, and code that sizes kernel task save areas for optional and TIE state.

## Risks
The most important risk is save-area mismatch with the assembler macro offsets. The header records `ae_ovf_sar` as 7 significant bits and `ae_sd_no` as 28 bits; generic tooling must honor the significant-bit metadata rather than assuming full 32-bit logical values. This variant has no port coprocessor mask.

## Test signals
Compile-time checks that list counts and sizes match generated assembly, context-switch tests under HiFi2 workloads, and debugger register-read validation are useful. A small macro-expansion test can verify that all `XCHAL_CPn_SA_LIST` empty cases remain syntactically valid.
