# sources/distributed-fs/ceph-client/fs/dlm/lvb_table.h

## Purpose
`lvb_table.h` declares the lock value block operation matrix used by DLM AST and lock conversion code to decide when LVB data should be copied, invalidated, or propagated across mode transitions.

## Important APIs, Types, And Functions
It exports `extern const int dlm_lvb_operations[8][8]`. The table is defined in `lock.c` and referenced by `ast.c` and lock paths.

## Control Flow
This header has no control flow. It provides a shared declaration so user-facing callback code and core lock state transitions agree on LVB handling semantics.

## State And Persistence
The declared matrix is static read-only kernel data. It affects in-memory lock result/LVB decisions but has no persistence beyond module lifetime.

## Dependencies And Integration Points
Integrated directly with `user.c` through `dlm_user_add_ast()` and callback output handling, and with `lock.c` where the table is defined and lock mode transitions are evaluated.

## Risks
Any mismatch between table dimensions and DLM lock-mode numeric ranges can cause out-of-bounds access. Semantic changes to the matrix can alter user-visible LVB validity and callback contents.

## Test Signals
Mode conversion tests with VALBLK locks should verify expected LVB propagation for all relevant grant/request mode pairs, especially recovery and conversion cases.
