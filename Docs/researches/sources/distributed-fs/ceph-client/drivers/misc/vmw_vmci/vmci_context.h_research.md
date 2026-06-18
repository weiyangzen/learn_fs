# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_context.h

Purpose: declares the internal context model for the VMCI driver. It defines checkpoint state identifiers, host wait-queue state, handle-list nodes, the main `struct vmci_ctx`, ioctl payload structs for context operations, and the non-public context API consumed by host, datagram, doorbell, and queue-pair code.

Important types/APIs: `struct vmci_ctx` contains the global list node, CID, kref, datagram queue counters, spinlock, queue-pair and doorbell handle arrays, notifier list, host wait queue, privilege flags, credential pointer, and notify-page mapping. `vmci_deny_interaction()` is the central inline access-control helper for restricted/trusted isolation. Public-in-module prototypes include context create/destroy, lookup, datagram enqueue/dequeue, notification add/remove, checkpoint get/set, queue-pair registration, doorbell registration/notification, pending notification receive/release, and `vmci_ctx_get_id()`.

Control flow/integration: this header is included by most VMCI submodules, so it is the contract linking `/dev/vmci` ioctl contexts, datagram routing, doorbell delivery, queue-pair broker ownership, and exported privilege/ownership checks.

State/persistence: the struct layout is in-memory state. `struct vmci_ctx_chkpt_buf_info`, `struct vmci_ctx_notify_recv_info`, and `struct dbell_cpt_state` integration make selected context state serializable for checkpoint flows.

Risks: broad inclusion creates circular dependencies with `vmci_datagram.h` and `vmci_queue_pair.h`. Any change to fields used without the context lock, especially `queue_pair_array`, must preserve documented locking assumptions. Checkpoint numeric constants are ABI-like for VMX.

Test signals: compile coverage for all includes, ABI layout checks where userspace structs are copied, and targeted tests for `vmci_deny_interaction()` restricted/trusted combinations.
