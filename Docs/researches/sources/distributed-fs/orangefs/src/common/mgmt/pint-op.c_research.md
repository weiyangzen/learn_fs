<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-op.c -->
# sources/distributed-fs/orangefs/src/common/mgmt/pint-op.c

Purpose: implements the small operation helper used by queue search paths. It bridges generic `PINT_queue_entry_t` nodes back to `PINT_operation_t`.

Important function: `PINT_op_queue_find_op_id_callback(PINT_queue_entry_t *entry, void *user_ptr)` compares the operation id stored in a queue entry with the `PINT_op_id` pointed to by `user_ptr`. It uses `PINT_op_from_qentry()` from the header to recover the containing `PINT_operation_t`.

Control flow is minimal: queue functions call this callback during search-and-remove operations, particularly when workers or contexts need to locate a specific operation by id. It returns `1` for match and `0` otherwise. There is no owned state or persistence.

Dependencies are `pvfs2-internal.h`, `pint-op.h`, and the intrusive queue entry layout. Integration points include non-threaded queue workers, threaded queue cancellation, and manager test/cancel paths.

Risks: the callback assumes `entry` belongs to a valid `PINT_operation_t` embedded member. Passing a queue entry from another object type would produce invalid container recovery. Tests should include successful lookup, missing id lookup, and use through `PINT_queue_search_and_remove()` to verify queue link cleanup and operation identity preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-op.c -->
