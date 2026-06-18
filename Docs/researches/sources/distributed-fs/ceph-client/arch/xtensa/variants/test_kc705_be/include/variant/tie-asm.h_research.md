# sources/distributed-fs/ceph-client/arch/xtensa/variants/test_kc705_be/include/variant/tie-asm.h

## Purpose
This assembler header saves/restores both non-coprocessor optional state and CP1 AudioEngineLX state for `test_kc705_be`.

## Important APIs, types, and functions
- `xchal_ncp_store/load` handle `THREADPTR`, `ACCLO`, `ACCHI`, `BR`, `SCOMPARE1`, and `M0`-`M3`.
- `xchal_cp_AudioEngineLX_store/load` alias `xchal_cp1_store/load`.
- CP1 macros save user registers `AE_OVF_SAR`, `AE_BITHEAD`, `AE_TS_FTS_BU_BP`, `AE_SD_NO`, `AE_CBEGIN0`, `AE_CEND0`, eight `aep` registers, and four `aeq` registers with audio-engine load/store instructions.
- Empty macros exist for unconfigured CP0 and CP2-CP7.

## Control flow
NCP macros follow the modern select/alloc save-area pattern. CP1 macros align to 8 bytes, save scalar AE user registers, then store packed 24x2 and 56-bit audio register-file state, adjusting the pointer across the 120-byte CP payload. Loads reverse the process.

## State and persistence behavior
The macros persist a 36-byte NCP area plus a 120-byte AudioEngineLX area, matching the 160-byte total save area in `tie.h`. CP7 XTIOP has no state.

## Dependencies and integration points
This file depends on HiFi2/AudioEngine assembler instructions and common Xtensa save-area helpers. It must match `test_kc705_be` `tie.h` and CPENABLE lazy/explicit coprocessor context management.

## Risks and edge cases
Audio state alignment is 8 bytes; incorrect alignment or CP enable handling will fault or corrupt registers. Pointer arithmetic in the macro splits stores across offsets, so metadata and assembler must remain in lockstep. Big-endian builds add coverage risk.

## Test signals
Run assembler builds with AudioEngine instructions enabled, context-switch stress using HiFi2 registers, signal delivery/return with CP state, and lazy coprocessor enable/disable tests.
