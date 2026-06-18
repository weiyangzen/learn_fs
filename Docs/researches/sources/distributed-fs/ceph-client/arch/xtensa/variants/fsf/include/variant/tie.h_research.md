# sources/distributed-fs/ceph-client/arch/xtensa/variants/fsf/include/variant/tie.h

## Purpose
This generated header declares the `fsf` TIE/save-area layout as empty.

## Important APIs, types, and functions
It reports no coprocessors, zero CP masks, `XCHAL_NCP_SA_SIZE` 0, `XCHAL_TOTAL_SA_SIZE` 0, `XCHAL_NCP_SA_NUM` 0, and empty CP save lists. It still defines standard instruction-length tables.

## Control flow
There is no runtime behavior; list macros expand to nothing.

## State and persistence behavior
According to this C metadata, no optional or custom state is allocated in generic save areas. This conflicts with `core.h` and `tie-asm.h` indications of `THREADPTR` support/save code, so thread pointer persistence may be handled elsewhere or the generated files are inconsistent.

## Dependencies and integration points
The header is paired with `fsf` `core.h` and `tie-asm.h` and is consumed by kernel save-area sizing logic.

## Risks and edge cases
The biggest risk is save-area allocation of zero bytes while assembler macros can store `THREADPTR`. Any caller expanding both must avoid memory corruption. The big-endian, old-core nature of `fsf` increases the chance of bitrot in rarely built paths.

## Test signals
Compile all `fsf` low-level state-save paths and run TLS/context-switch/signal tests. Static inspection should confirm no code calls `xchal_ncp_store` into a zero-sized save area.
