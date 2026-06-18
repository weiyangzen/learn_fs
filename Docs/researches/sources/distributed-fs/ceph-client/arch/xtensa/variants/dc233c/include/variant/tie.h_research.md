# sources/distributed-fs/ceph-client/arch/xtensa/variants/dc233c/include/variant/tie.h

## Purpose
This generated C header describes `dc233c` TIE and optional-state save areas.

## Important APIs, types, and functions
The variant has one CP7 `XTIOP` port coprocessor with zero save size and a 32-byte, 4-byte-aligned NCP area. `XCHAL_NCP_SA_LIST()` lists eight registers: `threadptr`, `acclo`, `acchi`, `m0`-`m3`, and `scompare1`.

## Control flow
Consumers expand macros with their own `XCHAL_SA_REG` definition; this file itself has no runtime behavior.

## State and persistence behavior
The layout persists per-thread TLS, MAC16, and conditional-store state. All CP save lists are empty despite CP7 being present.

## Dependencies and integration points
The file is paired with `dc233c` `tie-asm.h` and `core.h`. It informs kernel save-area sizing and register metadata.

## Risks and edge cases
The order differs from `dc232b` even though the set is the same, with `threadptr` first here. Mixing metadata and assembler macros from different variants would corrupt restored state.

## Test signals
Compile generated save-list users and run context-switch, signal, TLS, and MAC16 tests on `dc233c`.
