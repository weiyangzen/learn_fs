# File Research: sources/block-storage/kvdo/vdo/reference-operation.h

Defines `struct reference_operation`, the common description of a physical-block reference update.

Fields:
- `type`: journal operation, such as data increment/decrement or block-map increment.
- `pbn`: physical block number being updated.
- `state`: block mapping state.
- `lock_getter`: optional callback for retrieving a `pbn_lock`.
- `context`: lock or zone context passed to the getter.

The inline `vdo_get_reference_operation_pbn_lock()` returns `NULL` when no getter is present, otherwise delegates to the callback. This abstraction lets refcount code handle lock-aware and lockless operations consistently.
