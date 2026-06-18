# sources/distributed-fs/ceph-client/arch/xtensa/variants/dc233c/include/variant/tie-asm.h

## Purpose
This assembler header implements `dc233c` optional-state save/restore macros.

## Important APIs, types, and functions
It defines the full `XTHAL_SAS_*` mask set including `ANYOT`, `ANYCC`, `ANYABI`, and `XTHAL_SAS3()`. `xchal_ncp_store/load` save and restore `THREADPTR`, `ACCLO`, `ACCHI`, `M0`-`M3`, and `SCOMPARE1`. One temporary register is required.

## Control flow
The macros use common save-area start/alignment helpers, evaluate selected categories, and emit user/special register reads or writes. The `alloc` parameter can reserve space for unselected groups, allowing composition with larger save sequences.

## State and persistence behavior
The 32-byte NCP payload stores thread pointer, MAC16, and conditional-store state. There is no BR/boolean state and no nonempty coprocessor save state.

## Dependencies and integration points
It must match `dc233c` `tie.h` and is used by Xtensa assembly paths that preserve extra architectural state during task switch, exception handling, or user-state save.

## Risks and edge cases
The macro syntax differs from `dc232b` while the register set is similar. Shared assembly should not assume a uniform parameter list. Incorrect `alloc` handling can desynchronize offsets across composed saves.

## Test signals
Compile assembly against this variant, exercise TLS and MAC16 computations across context switches, and run signal-frame tests that validate `SCOMPARE1` and optional state restoration.
