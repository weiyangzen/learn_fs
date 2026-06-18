# File Research: sources/block-storage/kvdo/vdo/reference-operation.c

Implements helpers for constructing `struct reference_operation`.

Functions:
- `vdo_set_up_reference_operation_with_lock()` stores a direct `pbn_lock` pointer in the operation context and uses `return_pbn_lock()` as the getter.
- `vdo_set_up_reference_operation_with_zone()` stores a `physical_zone` pointer and uses `look_up_pbn_lock()` to retrieve the current lock for the PBN later.

Purpose:
- Lets reference-count update code use a uniform operation object while supporting both already-known locks and lazy lookup from a zone.
- Keeps PBN-lock coupling out of `ref-counts.c` callers.
