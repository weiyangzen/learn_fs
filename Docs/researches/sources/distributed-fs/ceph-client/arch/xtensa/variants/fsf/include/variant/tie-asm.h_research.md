# sources/distributed-fs/ceph-client/arch/xtensa/variants/fsf/include/variant/tie-asm.h

## Purpose
This assembler header provides minimal `fsf` non-coprocessor save/restore macros.

## Important APIs, types, and functions
`xchal_ncp_store` saves `THREADPTR`, and `xchal_ncp_load` restores it. The header declares one temporary register and has the older no-`alloc` macro form.

## Control flow
The macros use `xchal_sa_start`, optionally include the thread-global group based on `select`, align the save pointer, then issue `rur`/`wur` for `THREADPTR` and memory load/store.

## State and persistence behavior
The macro body persists a thread pointer value, but the paired `tie.h` reports `XCHAL_NCP_SA_SIZE` and `XCHAL_TOTAL_SA_SIZE` as zero. That mismatch is a notable integration hazard and may reflect historical/generated-header inconsistency.

## Dependencies and integration points
It depends on the common Xtensa assembler save-area helpers and `THREADPTR` register support from `core.h`. Consumers must reconcile it with `fsf` `tie.h`.

## Risks and edge cases
The zero-size C metadata versus nonempty assembler macro can desynchronize save-area allocation. Shared code should verify whether this header is actually used for task state or whether higher-level code treats threadptr separately.

## Test signals
Build the `fsf` variant and inspect generated save-area sizes. Runtime TLS preservation across context switches and signal delivery is the key behavioral test.
