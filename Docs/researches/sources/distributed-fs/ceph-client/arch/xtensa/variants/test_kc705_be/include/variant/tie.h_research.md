# sources/distributed-fs/ceph-client/arch/xtensa/variants/test_kc705_be/include/variant/tie.h

## Purpose
This generated C header describes the `test_kc705_be` optional and coprocessor save-area layout.

## Important APIs, types, and functions
It declares two coprocessors: CP1 `AudioEngineLX` with a 120-byte, 8-byte-aligned save area and CP7 `XTIOP` with zero save size. CP masks are `0x82`, with port mask `0x80`. NCP state is 36 bytes; total optional/CP state is 160 bytes aligned to 8. CP1 has 18 saved registers covering AE user registers and `aep`/`aeq` register files.

## Control flow
No runtime code is present. Consumers expand `XCHAL_NCP_SA_LIST()` and `XCHAL_CP1_SA_LIST()` via `XCHAL_SA_REG`.

## State and persistence behavior
NCP state covers threadptr, MAC16, boolean, and conditional-store registers. CP1 state covers AudioEngineLX scalar/user and register-file state. CP7 persists no state.

## Dependencies and integration points
The header must match `test_kc705_be` `core.h` HiFi2/CP flags and `tie-asm.h` CP1 store/load macros. Kernel coprocessor context code uses these sizes and masks to allocate and switch state.

## Risks and edge cases
The AudioEngineLX save area dominates the ABI. Missing the CP1 list or using only NCP state will pass simple integer tests but fail audio workloads after preemption or signal delivery. Instruction length tables include 8-byte entries for FLIX/audio encodings.

## Test signals
Compile save-list expansion, run AudioEngine register preservation across task switches, signals, fork/exec, and CP enable transitions, plus NCP MAC16/boolean/TLS tests.
