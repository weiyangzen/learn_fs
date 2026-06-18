# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_resource.h

Purpose: declares VMCI resource types and the common resource header embedded in datagram, doorbell, and queue-pair objects.

Important types/APIs: `enum vmci_resource_type` distinguishes API, group, datagram, doorbell, guest qpair, host qpair, and wildcard lookups. `struct vmci_resource` stores handle, type, hash node, kref, and completion used for removal synchronization. Prototypes cover add, remove, lookup by handle, get, put, and handle retrieval.

Control flow/integration: embedding objects add their resource on creation, use resource lookup for external handles, and remove it before freeing container memory.

State/persistence: no persistent state in the header, but the struct is the lifetime anchor for global handle resolution.

Risks: embedded object cleanup must respect `vmci_resource_remove()` waiting semantics. Any new resource type must preserve lookup and wildcard behavior.

Test signals: resource lifecycle in each embedding subsystem and type-specific lookup failures.
