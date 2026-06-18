# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_resource.c

Purpose: implements the global VMCI resource table used to map handles to datagram, doorbell, and queue-pair resources with kref lifetime and RCU lookup.

Important APIs/functions: `vmci_resource_add()` validates uniqueness or allocates a free resource ID, initializes the resource, and inserts into a hash bucket. `vmci_resource_remove()` unlinks under lock, waits for RCU, drops the table reference, and waits for completion after final kref release. `vmci_resource_by_handle()` looks up and kref-gets a resource. `vmci_resource_get()/put()` wrap kref access, and `vmci_resource_handle()` returns the assigned handle.

Control flow: lookup hashes by resource ID and matches type, resource ID, and compatible context ID, allowing wildcard invalid context in either stored or requested handle. ID allocation cycles through nonreserved resource IDs and checks lookup for collisions. Removal waits until no outstanding references remain before callers free the containing object.

State/persistence: static hash table of 128 buckets guarded by spinlock for mutation and RCU for readers. Resource lifetime is volatile and tied to module state.

Dependencies/integration: used by datagram, doorbell, queue-pair guest endpoints, and broker entries. Depends on VMCI handle helpers and kernel kref/completion/RCU.

Risks: hash only uses resource ID, so buckets can be hot if many contexts use same RID patterns. `vmci_resource_add()` calls lookup while holding the table spinlock; lookup uses RCU and assumes this nesting is acceptable. Wildcard context matching is powerful and must be used carefully for ANYCID handles.

Test signals: duplicate add, auto-ID wraparound, wildcard context lookup, remove with outstanding refs, type filtering, and concurrent lookup/remove races.
