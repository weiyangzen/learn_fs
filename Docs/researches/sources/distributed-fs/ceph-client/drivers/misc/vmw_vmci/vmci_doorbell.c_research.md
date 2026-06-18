# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_doorbell.c

Purpose: implements VMCI doorbell resources, host callback delivery, guest notification bitmap index management, hypervisor link/unlink messages, and exported doorbell create/destroy APIs.

Important APIs/functions: `vmci_doorbell_create()` validates callback, flags, privileges, and handle ownership, adds a `VMCI_RESOURCE_TYPE_DOORBELL` resource, and for active guest personality assigns a bitmap index and links it with the hypervisor. `vmci_doorbell_destroy()` removes guest bitmap state, unlinks from the hypervisor, removes the resource, and frees the entry. `vmci_dbell_host_context_notify()` invokes or schedules host callbacks. `vmci_dbell_register_notification_bitmap()` sends the bitmap PPN to the hypervisor. `vmci_dbell_scan_notification_entries()` processes raised bitmap bits.

Control flow: doorbell entries are stored in the global VMCI resource table and, for guest endpoints, in a hashed bitmap-index table. Bitmap scan clears bit 0 for each active index and fires all active entries sharing that index. Delayed callbacks take resource references until work completion. Host notifications arrive through context doorbell notification paths and call the host-context notify helper.

State/persistence: `vmci_doorbell_it` tracks index-to-entry mappings with `max_notify_idx`, `notify_idx_count`, round-robin reservation, and a one-entry released-index cache. State is volatile except `dbell_cpt_state`, used by context checkpointing to preserve doorbell handles.

Dependencies/integration: depends on `vmci_resource`, `vmci_datagram`/`vmci_send_datagram()` for hypervisor commands, `vmci_route` indirectly through notification senders, `vmci_context` for privilege checks, and guest interrupt bitmap processing.

Risks: callbacks can run under the index-table spinlock when not delayed, so callback clients must not sleep or call back into lock-conflicting paths. Index sharing and round-robin allocation mean bitmap collisions are intentional; tests must cover multiple entries per index. Destroy frees `entry` after `vmci_resource_remove()` waits for references, but scheduled work and callback ordering are subtle.

Test signals: create with invalid/valid fixed handles, auto-allocated handles, guest active/inactive modes, bitmap registration failure, duplicate index sharing, delayed and immediate callback paths, unlink failure after hibernation-style state loss, and privilege-denied notification.
