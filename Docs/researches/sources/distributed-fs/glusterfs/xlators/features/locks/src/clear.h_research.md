# sources/distributed-fs/glusterfs/xlators/features/locks/src/clear.h

## Purpose
Declares clear-lock argument types and clear helper APIs for the locks translator.

## Important APIs, Types, and Functions
- `clrlk_type` enumerates inode, entry, and POSIX lock clearing.
- `clrlk_kind` selects blocked, granted, or all locks.
- `clrlk_args` carries parsed type, kind, and optional type-specific string.
- Declares parser helpers and clear functions for POSIX, inode, entry, and all-domain lock cleanup.

## Control Flow
This header is consumed by lock xattr handling code and implemented by `clear.c`. Callers parse a command into `clrlk_args`, then dispatch to a type-specific clear function.

## State and Persistence
No state is stored here. The declared functions mutate in-memory lock tables owned by the locks translator.

## Dependencies and Integration Points
Includes GlusterFS errno compatibility and `locks.h`, so it depends on lock structs such as `pl_inode_t`, `pl_dom_list_t`, and GlusterFS lock/fop types.

## Risks and Edge Cases
The declaration `clrlk_get__kind` does not match the implementation name `clrlk_get_kind`, which can cause missing-prototype or linker issues for external callers. The `kind` enum uses bit-like values for blocked and granted, and `CLRLK_ALL` is `3`, so code relies on bitwise checks.

## Test Signals
Build all callers with warnings enabled, especially any direct calls to `clrlk_get_kind`. Runtime tests should dispatch each enum combination to the appropriate clear routine.
