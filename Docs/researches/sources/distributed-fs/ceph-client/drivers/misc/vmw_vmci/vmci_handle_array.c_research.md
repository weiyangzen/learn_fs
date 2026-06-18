# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_handle_array.c

Purpose: implements a small dynamically growable array of VMCI handles used by contexts for queue pairs, doorbells, pending notifications, and subscription snapshots.

Important APIs/functions: `vmci_handle_arr_create()` allocates a flexible-array object with default capacity when requested capacity is zero. `vmci_handle_arr_append_entry()` grows capacity up to `max_capacity` with `krealloc()` and appends. `vmci_handle_arr_remove_entry()` removes by swapping the last element into the removed slot. `vmci_handle_arr_remove_tail()`, `vmci_handle_arr_get_entry()`, `vmci_handle_arr_has_entry()`, and `vmci_handle_arr_get_handles()` provide basic access.

Control flow: callers generally hold their own locks. Append doubles by adding the current capacity, capped by remaining max capacity. Removal does not preserve ordering.

State/persistence: purely in-memory flexible-array state with size, capacity, and max capacity. Entries beyond `size` may be set to `VMCI_INVALID_HANDLE` on removal but are not relied upon.

Dependencies/integration: used heavily by `vmci_context.c` and doorbell checkpoint logic.

Risks: allocation uses `GFP_ATOMIC`, so append can fail under pressure. Removal swaps last entry and changes ordering, which is fine for membership sets but not ordered queues. The inline `vmci_handle_arr_get_size()` in the header assumes non-NULL arrays.

Test signals: growth at capacity, max-capacity exhaustion, remove present/missing entries, duplicate membership policy enforced by callers, and get entry out-of-range.
