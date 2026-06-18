# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_handle_array.h

Purpose: declares the VMCI handle-array container and accessors.

Important types/APIs: `struct vmci_handle_arr` stores capacity, max capacity, current size, and a counted flexible array of `struct vmci_handle`. `VMCI_HANDLE_ARRAY_DEFAULT_CAPACITY` is chosen so a default array is roughly 64 bytes. Prototypes cover create, destroy, append, remove by entry, remove tail, indexed get, membership test, raw handle pointer access, and `vmci_handle_arr_get_size()`.

Control flow/integration: context code uses this as a set-like container for registered and pending handles; userspace copy helper uses `vmci_handle_arr_get_handles()` to copy pending notifications.

State/persistence: volatile in-memory structure.

Risks: callers must check allocation returns, serialize mutation, and avoid assuming stable order. Raw pointer returned by `get_handles()` is only valid while the array object is stable.

Test signals: counted-by flexible-array builds, null/empty array behavior through callers, and concurrent mutation coverage under context locks.
