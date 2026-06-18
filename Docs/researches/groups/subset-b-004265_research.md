# subset-b-004265 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_context.c -->
# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_context.c

Purpose: implements the host-side VMCI context registry and per-context state used by hosted VMX processes and the host context. A `vmci_ctx` owns a CID, credentials, privilege flags, queued incoming datagrams, registered queue-pair handles, doorbell handles, pending doorbell notifications, context-removal subscriptions, and optional user notify-page mapping.

Important APIs/functions: `vmci_ctx_create()` allocates a context, initializes handle arrays, wait queues, locks, credentials, and inserts into the global RCU list while regenerating colliding CIDs. `vmci_ctx_destroy()` removes the context from the global list, waits for RCU, and drops the final reference. `vmci_ctx_get()/put()/exists()` provide RCU lookup and kref lifetime. `vmci_ctx_enqueue_datagram()` queues copied datagrams with per-context byte limits and wakes poll waiters. `vmci_ctx_dequeue_datagram()` removes the oldest datagram only if the caller's buffer is large enough. Doorbell and queue-pair registration are handled by `vmci_ctx_dbell_*()` and `vmci_ctx_qp_*()`. Checkpoint APIs cover notifier and doorbell state.

Control flow: datagram delivery looks up the destination context, allocates a queue entry, checks queue byte limits, signals the notify flag, and wakes `host_context.wait_queue`. Context teardown fires `VMCI_EVENT_CTX_REMOVED` to subscribers, detaches all brokered queue pairs, drains queued datagrams, destroys arrays and notifier nodes, unmaps notify pages, releases credentials, and frees the object. Doorbell notification validates access rules, appends pending handles, and wakes the context.

State/persistence: all state is kernel-resident and volatile, but checkpoint methods expose notifier and doorbell state for VM suspend/restore. The global context list is protected by `ctx_list.lock` plus RCU readers. Each context's datagram queue and handle arrays are protected by `context->lock`; queue-pair arrays are also touched by queue-pair broker paths per comments.

Dependencies/integration: integrates with `vmci_datagram_dispatch()`, `vmci_event_dispatch()`, `vmci_qp_broker_detach()`, doorbell privilege lookup, handle arrays, host poll/ioctl code, and exported VMCI APIs `vmci_context_get_priv_flags()` and `vmci_is_context_owner()`.

Risks: lock ordering across context, broker, and resource operations needs care. `vmci_ctx_rcv_notifications_release()` assumes a valid context after `vmci_ctx_get()` and would fault if called after context teardown. Checkpoint allocation uses `GFP_ATOMIC` under spinlock and may fail under pressure. `vmci_ctx_exists()` is explicitly race-prone for policy decisions. Datagram queue limits and hypervisor-event exceptions are security-sensitive.

Test signals: exercise context creation with CID collision, restricted/trusted privilege combinations, datagram queue full paths, notify-page setup/unset, poll wakeups, checkpoint get/set with too-small buffers, context destruction with live queue pairs, and doorbell notification replay on failed userspace copy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_context.h -->
# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_context.h

Purpose: declares the internal context model for the VMCI driver. It defines checkpoint state identifiers, host wait-queue state, handle-list nodes, the main `struct vmci_ctx`, ioctl payload structs for context operations, and the non-public context API consumed by host, datagram, doorbell, and queue-pair code.

Important types/APIs: `struct vmci_ctx` contains the global list node, CID, kref, datagram queue counters, spinlock, queue-pair and doorbell handle arrays, notifier list, host wait queue, privilege flags, credential pointer, and notify-page mapping. `vmci_deny_interaction()` is the central inline access-control helper for restricted/trusted isolation. Public-in-module prototypes include context create/destroy, lookup, datagram enqueue/dequeue, notification add/remove, checkpoint get/set, queue-pair registration, doorbell registration/notification, pending notification receive/release, and `vmci_ctx_get_id()`.

Control flow/integration: this header is included by most VMCI submodules, so it is the contract linking `/dev/vmci` ioctl contexts, datagram routing, doorbell delivery, queue-pair broker ownership, and exported privilege/ownership checks.

State/persistence: the struct layout is in-memory state. `struct vmci_ctx_chkpt_buf_info`, `struct vmci_ctx_notify_recv_info`, and `struct dbell_cpt_state` integration make selected context state serializable for checkpoint flows.

Risks: broad inclusion creates circular dependencies with `vmci_datagram.h` and `vmci_queue_pair.h`. Any change to fields used without the context lock, especially `queue_pair_array`, must preserve documented locking assumptions. Checkpoint numeric constants are ABI-like for VMX.

Test signals: compile coverage for all includes, ABI layout checks where userspace structs are copied, and targeted tests for `vmci_deny_interaction()` restricted/trusted combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_datagram.c -->
# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_datagram.c

Purpose: implements VMCI datagram endpoints, endpoint lifetime, routing dispatch, host callback invocation, guest hypercall forwarding, and exported datagram APIs.

Important APIs/functions: `vmci_datagram_create_handle_priv()` and `vmci_datagram_create_handle()` allocate a host datagram endpoint as a VMCI resource with callback, flags, client data, and privilege flags. `vmci_datagram_destroy_handle()` removes the resource and frees the endpoint. `vmci_datagram_send()` dispatches a caller-provided datagram. Internal `vmci_datagram_dispatch()` validates datagram size, calls `vmci_route()`, and selects host or guest dispatch. `vmci_datagram_invoke_guest_handler()` invokes a local guest endpoint for datagrams read from the device.

Control flow: host dispatch rejects hypervisor destinations, checks source ownership, resolves source privileges, then either invokes a host resource callback, queues delayed work, handles hypervisor event datagrams, or copies the datagram to a VM context queue. Guest dispatch validates that the source endpoint exists, then sends through `vmci_send_datagram()`. Delayed callbacks keep a resource reference until work completion and optionally count against `delayed_dg_host_queue_size`.

State/persistence: datagram endpoint state is a `datagram_entry` in the global resource table. Delayed host-to-host callbacks are bounded by `VMCI_MAX_DELAYED_DG_HOST_QUEUE_SIZE`. No persistent state exists beyond in-memory resources and scheduled work.

Dependencies/integration: relies on `vmci_resource` for lookup/lifetime, `vmci_route` for personality selection, `vmci_context` for VM queue delivery and privileges, `vmci_guest` for hypervisor send, and `vmci_event` for event datagrams.

Risks: delayed queue limit uses `atomic_add_return() == max`, allowing max-1 but not clearly guarding values greater than max under unusual races. Callback execution context differs by flags and by host-to-host delivery, so clients must tolerate process/workqueue context. Destroy removes the resource after dropping one lookup reference; delayed work safety depends on resource references.

Test signals: create/destroy endpoint with duplicate handles, invalid flags, ANYCID flags, host-to-host delayed delivery, guest route send failure, no-handle guest callback, VM-to-VM rejection, privilege-denied delivery, and payload-size boundary cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_datagram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_datagram.h -->
# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_datagram.h

Purpose: provides internal datagram queue and ioctl contracts shared by context, host, and datagram implementation files.

Important types/APIs: `VMCI_MAX_DELAYED_DG_HOST_QUEUE_SIZE` bounds delayed host callback backlog. `struct vmci_datagram_queue_entry` wraps an in-kernel queued datagram with list node and cached datagram size for spinlock-protected queue accounting. `struct vmci_datagram_snd_rcv_info` is the userspace send/receive ioctl payload. Internal prototypes are `vmci_datagram_dispatch()` and `vmci_datagram_invoke_guest_handler()`.

Control flow/integration: contexts store `vmci_datagram_queue_entry` nodes on per-context queues. Host ioctl code copies `vmci_datagram_snd_rcv_info` to and from userspace before calling dispatch/dequeue. Guest interrupt code calls the guest handler for datagrams read from the virtual device.

State/persistence: the queue entry is transient in-memory state and owns a pointer to a separately allocated datagram until dequeued or context destruction.

Risks: the header includes `vmci_context.h`, while context includes this header, so changes can aggravate include cycles. The ioctl struct uses raw user virtual addresses and must remain layout-compatible.

Test signals: structure-size compatibility, datagram queue entry lifetime under enqueue/dequeue/destroy, and ioctl send/receive buffer-size handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_datagram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_doorbell.c -->
# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_doorbell.c

Purpose: implements VMCI doorbell resources, host callback delivery, guest notification bitmap index management, hypervisor link/unlink messages, and exported doorbell create/destroy APIs.

Important APIs/functions: `vmci_doorbell_create()` validates callback, flags, privileges, and handle ownership, adds a `VMCI_RESOURCE_TYPE_DOORBELL` resource, and for active guest personality assigns a bitmap index and links it with the hypervisor. `vmci_doorbell_destroy()` removes guest bitmap state, unlinks from the hypervisor, removes the resource, and frees the entry. `vmci_dbell_host_context_notify()` invokes or schedules host callbacks. `vmci_dbell_register_notification_bitmap()` sends the bitmap PPN to the hypervisor. `vmci_dbell_scan_notification_entries()` processes raised bitmap bits.

Control flow: doorbell entries are stored in the global VMCI resource table and, for guest endpoints, in a hashed bitmap-index table. Bitmap scan clears bit 0 for each active index and fires all active entries sharing that index. Delayed callbacks take resource references until work completion. Host notifications arrive through context doorbell notification paths and call the host-context notify helper.

State/persistence: `vmci_doorbell_it` tracks index-to-entry mappings with `max_notify_idx`, `notify_idx_count`, round-robin reservation, and a one-entry released-index cache. State is volatile except `dbell_cpt_state`, used by context checkpointing to preserve doorbell handles.

Dependencies/integration: depends on `vmci_resource`, `vmci_datagram`/`vmci_send_datagram()` for hypervisor commands, `vmci_route` indirectly through notification senders, `vmci_context` for privilege checks, and guest interrupt bitmap processing.

Risks: callbacks can run under the index-table spinlock when not delayed, so callback clients must not sleep or call back into lock-conflicting paths. Index sharing and round-robin allocation mean bitmap collisions are intentional; tests must cover multiple entries per index. Destroy frees `entry` after `vmci_resource_remove()` waits for references, but scheduled work and callback ordering are subtle.

Test signals: create with invalid/valid fixed handles, auto-allocated handles, guest active/inactive modes, bitmap registration failure, duplicate index sharing, delayed and immediate callback paths, unlink failure after hibernation-style state loss, and privilege-denied notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_doorbell.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_doorbell.h -->
# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_doorbell.h

Purpose: declares internal doorbell ioctl, checkpoint, privilege, bitmap, and host-notify contracts.

Important types/APIs: `struct vmci_dbell_notify_resource_info` is used by host ioctl paths to create, destroy, or notify a doorbell/queue-pair-like resource. `struct dbell_cpt_state` stores checkpointed doorbell mapping data and is explicitly checkpoint-compatible. Prototypes expose host notification, privilege lookup, notification bitmap registration, and bitmap scanning.

Control flow/integration: host ioctl code passes `vmci_dbell_notify_resource_info` into context doorbell create/destroy/notify helpers. Guest probe registers a notification bitmap, and interrupt processing scans it through this header's API.

State/persistence: `dbell_cpt_state` is persistent checkpoint ABI. Other declarations describe volatile doorbell resources.

Risks: changing `dbell_cpt_state` breaks checkpoint compatibility. `vmci_dbell_get_priv_flags()` is security-sensitive because context doorbell notification relies on it before cross-context delivery.

Test signals: checkpoint binary compatibility, ioctl copy layout, and bitmap scan behavior with mocked bitmap data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_doorbell.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_driver.c -->
# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_driver.c

Purpose: module entry point and personality coordinator for the unified VMCI driver. It initializes event support, guest PCI personality, host misc-device personality, module parameters, and VSOCK transport activation callbacks.

Important APIs/functions: `vmci_get_context_id()` returns the guest VM CID when the guest device is active, otherwise host CID when host personality is active. `vmci_register_vsock_callback()` registers or unregisters the VSOCK transport callback and immediately calls it for already active personalities. `vmci_call_vsock_callback()` ensures host callback is called only once. `vmci_drv_init()` initializes events and enabled personalities. `vmci_drv_exit()` tears them down in reverse order.

Control flow: module load initializes the event subsystem first, then attempts guest and host init unless disabled by `disable_guest` or `disable_host`. If neither personality initializes, it exits with `-ENODEV` and shuts down events. Module unload exits initialized personalities and events. VSOCK callback state is serialized by `vmci_vsock_mutex`.

State/persistence: module-global booleans track parameter disables and whether each personality was initialized. Callback pointer and host-callback-called state are process-lifetime globals only.

Dependencies/integration: calls `vmci_event_init/exit`, `vmci_guest_init/exit`, `vmci_host_init/exit`, `vmci_guest_code_active()`, `vmci_host_code_active()`, and VSOCK exported callback registration.

Risks: `vmci_get_context_id()` prioritizes guest personality when both host and guest are active, which is intentional but affects clients expecting host CID in unified mode. Failed host/guest init is warning-only unless both fail. Callback registration allows only one callback and returns `-EBUSY` for duplicates.

Test signals: module parameter combinations, guest-only/host-only/both-disabled load behavior, VSOCK callback registration/unregistration, callback replay for already active personalities, and host callback single-call behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_driver.h -->
# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_driver.h

Purpose: internal driver-wide interface for personality state, current context IDs, guest datagram send, host/guest init and exit, VSOCK callback dispatch, and shared file-private object typing.

Important types/APIs: `enum vmci_obj_type` distinguishes file-private VMCI objects such as VMX VM contexts and sockets. `struct vmci_obj` is a generic file-handle payload. It declares global `vmci_pdev`, context ID helpers, datagram send, host and guest lifecycle/activity functions, host-user count, VM context ID, and PPN width selection.

Control flow/integration: included by most submodules to determine whether to route as host or guest and to call the guest hypercall transport.

State/persistence: exposes `vmci_pdev` singleton because the virtual hardware allows only one VMCI device.

Risks: global singleton assumptions must match hardware and PCI probe behavior. `vmci_obj` typing is only as safe as file-operation code maintaining `ct_type` correctly.

Test signals: compile coverage across host-disabled and guest-disabled configurations, singleton device setup/teardown, and file-private object lifecycle in `/dev/vmci`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_event.c -->
# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_event.c

Purpose: implements in-kernel VMCI event subscription and dispatch for hypervisor/context/queue-pair events.

Important APIs/functions: `vmci_event_init()` initializes per-event subscriber lists. `vmci_event_exit()` frees remaining subscribers with warnings. `vmci_event_dispatch()` validates event datagram payload size and event number, then calls `event_deliver()`. `vmci_event_subscribe()` allocates a subscription, generates a nonduplicate ID with limited attempts, and links it under RCU. `vmci_event_unsubscribe()` removes by subscription ID and frees via RCU.

Control flow: event datagrams are delivered from guest interrupt handling or local host-generated event paths. Delivery sanitizes the event index with `array_index_nospec()`, enters an RCU read-side section, iterates the selected subscriber list, and invokes callbacks. Subscription mutation is serialized by `subscriber_mutex`.

State/persistence: static `subscriber_array[VMCI_EVENT_MAX]` stores volatile subscriptions. Subscription IDs come from a static incrementing counter inside subscribe.

Dependencies/integration: used by guest CID update subscription, queue-pair peer attach/detach notifications, context removal events, and datagram dispatch of hypervisor event messages.

Risks: callback functions run inside RCU read-side critical section and must not sleep. `vmci_event_subscribe()` writes `*new_subscription_id = sub->id` even on failure, and currently leaks `sub` when no ID is found because the failure path does not free it. Event ID generation only attempts `VMCI_EVENT_MAX_ATTEMPTS`.

Test signals: invalid event payload sizes, invalid event numbers, subscribe/unsubscribe races with dispatch, callback non-sleeping expectations, duplicate ID exhaustion, and module exit with lingering subscriptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_event.h -->
# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_event.h

Purpose: small internal header for the VMCI event subsystem.

Important APIs: declares `vmci_event_init()`, `vmci_event_exit()`, and `vmci_event_dispatch()`. Public subscription APIs come from the external VMCI API header, while this header exposes module-internal lifecycle and dispatch hooks.

Control flow/integration: module init/exit call lifecycle functions; datagram and guest receive paths call dispatch for event datagrams.

State/persistence: no state is declared here.

Risks: minimal, but all callers must pass a valid `struct vmci_datagram *` whose payload matches VMCI event layout.

Test signals: build coverage and dispatch validation with malformed datagrams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_guest.c -->
# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_guest.c

Purpose: implements the VMCI PCI guest personality. It probes VMware VMCI PCI hardware, maps register access, allocates datagram DMA or I/O buffers, sends hypervisor datagrams, receives interrupt-driven datagrams/events, manages notification bitmap memory, and exposes active guest context state.

Important APIs/functions: `vmci_guest_init()/exit()` register/unregister the PCI driver. `vmci_guest_probe_device()` performs device enable, BAR mapping, buffer allocation, capability negotiation, global device publication, notification bitmap registration, host capability check, event subscription, IRQ setup, interrupt enabling, and VSOCK callback. `vmci_guest_remove_device()` undoes those resources. `vmci_send_datagram()` serializes outgoing hypercalls under `vmci_dev_spinlock`. `vmci_get_vm_context_id()` lazily sends `VMCI_GET_CONTEXT_ID`. Interrupt handlers call `vmci_dispatch_dgs()`, `vmci_process_bitmap()`, or wake DMA waiters.

Control flow: probe prefers MMIO BAR1 and DMA datagram support, falling back to I/O port access except on ARM64. It negotiates datagram, PPN64, notifications, and DMA datagram capabilities by writing selected caps back to the device. Incoming datagrams are read into a buffer, walked until invalid headers/end markers, then dispatched either as VMCI events or guest datagram callbacks. Shared interrupt mode reads and clears interrupt causes; exclusive MSI-X vectors split datagram, bitmap, and DMA completion work.

State/persistence: singleton globals `vmci_dev_g`, `vmci_pdev`, `vm_context_id`, `ctx_update_sub_id`, `use_ppn64`, and `vmci_num_guest_devices` represent live guest device state. Device buffers and notification bitmap are DMA-coherent where MMIO/DMA is used. No durable state is stored.

Dependencies/integration: integrates with Linux PCI, DMA, IRQ, MMIO/I/O helpers, VMCI event subscriptions, doorbell bitmap registration/scanning, datagram guest handler dispatch, queue-pair guest endpoint cleanup, and VSOCK callback activation.

Risks: `vmci_write_data()` computes `result` but `vmci_send_datagram()` separately reads `VMCI_RESULT_LOW_ADDR`, so result sequencing depends on device semantics. DMA read waits on `buffer_header->busy` and relies on DMA interrupt wakeups. Global singleton publication must be cleared before freeing buffers. Datagram parsing handles partial, oversized, and page-aligned I/O-port cases; off-by-one mistakes here would corrupt dispatch.

Test signals: PCI probe/remove under MMIO and I/O-port modes, capabilities missing/fallback paths, MSI-X/MSI/legacy interrupt setup, DMA datagram send/receive completion, notification bitmap callbacks, context ID update events, invalid/oversized incoming datagrams, and cleanup after mid-probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_guest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_handle_array.c -->
# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_handle_array.c

Purpose: implements a small dynamically growable array of VMCI handles used by contexts for queue pairs, doorbells, pending notifications, and subscription snapshots.

Important APIs/functions: `vmci_handle_arr_create()` allocates a flexible-array object with default capacity when requested capacity is zero. `vmci_handle_arr_append_entry()` grows capacity up to `max_capacity` with `krealloc()` and appends. `vmci_handle_arr_remove_entry()` removes by swapping the last element into the removed slot. `vmci_handle_arr_remove_tail()`, `vmci_handle_arr_get_entry()`, `vmci_handle_arr_has_entry()`, and `vmci_handle_arr_get_handles()` provide basic access.

Control flow: callers generally hold their own locks. Append doubles by adding the current capacity, capped by remaining max capacity. Removal does not preserve ordering.

State/persistence: purely in-memory flexible-array state with size, capacity, and max capacity. Entries beyond `size` may be set to `VMCI_INVALID_HANDLE` on removal but are not relied upon.

Dependencies/integration: used heavily by `vmci_context.c` and doorbell checkpoint logic.

Risks: allocation uses `GFP_ATOMIC`, so append can fail under pressure. Removal swaps last entry and changes ordering, which is fine for membership sets but not ordered queues. The inline `vmci_handle_arr_get_size()` in the header assumes non-NULL arrays.

Test signals: growth at capacity, max-capacity exhaustion, remove present/missing entries, duplicate membership policy enforced by callers, and get entry out-of-range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_handle_array.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_handle_array.h -->
# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_handle_array.h

Purpose: declares the VMCI handle-array container and accessors.

Important types/APIs: `struct vmci_handle_arr` stores capacity, max capacity, current size, and a counted flexible array of `struct vmci_handle`. `VMCI_HANDLE_ARRAY_DEFAULT_CAPACITY` is chosen so a default array is roughly 64 bytes. Prototypes cover create, destroy, append, remove by entry, remove tail, indexed get, membership test, raw handle pointer access, and `vmci_handle_arr_get_size()`.

Control flow/integration: context code uses this as a set-like container for registered and pending handles; userspace copy helper uses `vmci_handle_arr_get_handles()` to copy pending notifications.

State/persistence: volatile in-memory structure.

Risks: callers must check allocation returns, serialize mutation, and avoid assuming stable order. Raw pointer returned by `get_handles()` is only valid while the array object is stable.

Test signals: counted-by flexible-array builds, null/empty array behavior through callers, and concurrent mutation coverage under context locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_handle_array.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_host.c -->
# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_host.c

Purpose: implements the host personality exposed as `/dev/vmci`. It lets VMX processes create contexts, send/receive datagrams, allocate/map/detach queue pairs, manage context notifications, checkpoint selected state, configure notify flags, and receive doorbell notifications.

Important APIs/functions: `vmci_host_init()` creates the host context and registers the misc device. `vmci_host_exit()` deregisters it and exits the queue-pair broker. File ops include open/close/poll/ioctl. Ioctl handlers cover context init, datagram send/receive, queue-pair allocation/set VA/set page file/detach, context add/remove notification, checkpoint get/set, context ID query, notify-page setup, notify-resource operations, and pending notification receive.

Control flow: open allocates per-file `vmci_host_dev`; init-context ioctl creates a `vmci_ctx` with current credentials and increments active users. Poll waits on the context wait queue and reports readable if datagrams or doorbells are pending. Send ioctl copies a userspace datagram, validates size, dispatches with the file context CID, and returns VMCI status. Receive ioctl dequeues from the context queue and copies the datagram back. Close destroys the context and decrements active users.

State/persistence: global `host_context`, `vmci_host_device_initialized`, and `vmci_host_active_users` model host personality activity. Per-open state stores context pointer, user VMCI version, object type, and mutex. Notify setup pins and maps a userspace page until unset or context teardown. Checkpoint ioctls serialize notifier and doorbell state for VMX.

Dependencies/integration: integrates Linux miscdevice/file/ioctl/poll/usercopy APIs with VMCI context, datagram, queue-pair broker, doorbell notification, event, and resource subsystems.

Risks: all ioctl structures are ABI-facing and copy raw user virtual addresses. Version-dependent queue-pair paths are complex, especially old VMX page-file compatibility. The SetPageFile handler pre-writes success before doing the operation to avoid unwind complexity, which is intentional but unusual. Notify-page mapping uses pinned user memory and must always be released.

Test signals: ioctl ABI compatibility across VMCI versions, context init/close lifecycle, poll wakeups, datagram size mismatch, queue-pair old/new version flows, notification receive with partial user buffers, notify page setup/unset, and failure unwinds for copy_to_user/copy_from_user.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_queue_pair.c -->
# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_queue_pair.c

Purpose: implements VMCI queue pairs for stream-style bidirectional communication. It includes guest endpoint allocation with DMA-backed pages and hypervisor registration, host broker state for guest-backed memory, local queue pairs, map/unmap during quiesce, peer attach/detach events, and exported qpair read/write/index APIs.

Important APIs/functions: `vmci_qpair_alloc()` allocates a client `struct vmci_qp`, routes to guest or host endpoint creation, and registers wakeup callbacks for host-side waits. `vmci_qpair_detach()` detaches and frees the client object. `vmci_qp_broker_alloc()`, `vmci_qp_broker_set_page_store()`, `vmci_qp_broker_detach()`, `vmci_qp_broker_map()`, and `vmci_qp_broker_unmap()` are host broker entry points used by `/dev/vmci`. `vmci_qp_guest_endpoints_exit()` drains guest endpoints. Data APIs include index getters, free-space/ready checks, `vmci_qpair_enquev()`, `vmci_qpair_dequev()`, and `vmci_qpair_peekv()`.

Control flow: guest allocation creates queues, gathers PPNs, sends `VMCI_QUEUEPAIR_ALLOC`, and stores endpoints in `qp_guest_endpoints`. Host allocation enters the broker list, either creating or attaching a `qp_broker_entry`. Broker state moves through NEW, CREATED_NO_MEM/MEM, ATTACHED_NO_MEM/MEM, SHUTDOWN_NO_MEM/MEM, and gone. Guest memory can be registered immediately via page store or later through old-VMX SetPageStore. Map/unmap pins/unpins user pages, maps queue headers, saves headers across quiesce, and wakes blocked host users when memory returns.

State/persistence: volatile global lists `qp_broker_list` and `qp_guest_endpoints` are mutex protected. Broker entries store creator/attacher IDs, flags, refcount, privilege constraints, memory availability state, queue pointers, saved headers, and wakeup callback data. Guest endpoints store produce/consume queue memory and PPN sets. Queue headers persist in shared memory while mapped and may be snapshotted into saved header fields.

Dependencies/integration: uses Linux DMA, page pinning, vmap, mutex/waitqueue, iov_iter, VMCI resource table, context ownership arrays, datagram/event dispatch, guest hypercalls, and queue-header helpers from public VMCI definitions.

Risks: this is the highest-complexity file. Broker transitions are security-sensitive for VM-to-VM rejection, restricted/trusted attach, host queue-pair version compatibility, and create/attach sizing. Page pinning/unpinning and header mapping must not race with enqueue/dequeue. `vmci_qp_broker_exit()` frees broker entries directly without full resource cleanup, so it assumes module teardown context. Several function names use `detatch`, matching existing API spelling.

Test signals: guest endpoint create/detach, local queue pairs, host-created and guest-created broker flows, old VMX SetPageStore, map/unmap quiesce and saved headers, attach/detach events, privilege denial, size overflow/limit checks, queue wraparound enqueue/dequeue/peek, not-ready waits and wakeups, and failure cleanup after partial page pinning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_queue_pair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_queue_pair.h -->
# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_queue_pair.h

Purpose: declares internal queue-pair structures, ioctl payloads, page-store formats, and broker/client APIs.

Important types/APIs: `struct ppn_set` stores guest PPN lists. `struct vmci_qp_alloc_info`, `vmci_qp_set_va_info`, `vmci_qp_page_file_info`, and `vmci_qp_dtch_info` are ioctl payloads. `struct vmci_qp_page_store` describes guest backing memory. `struct vmci_queue` pairs queue header, saved header, and OS-specific kernel interface. Prototypes expose broker lifecycle, allocation, page-store setup, detach, guest endpoint cleanup, generic `vmci_qp_alloc()`, and broker map/unmap.

Control flow/integration: host ioctl code uses the ioctl structs and broker APIs. Exported public qpair APIs in the C file use `vmci_qp_alloc()` to choose host/guest implementation. Guest queue allocation passes PPN sets to hypervisor commands.

State/persistence: ioctl structs are ABI-facing. `vmci_qp_page_file_info` includes comments documenting compatibility with old VMX struct versions. Queue headers can be saved during memory unmap.

Risks: struct layout changes can break VMX compatibility. `VMCI_QP_PAGESTORE_IS_WELLFORMED()` only checks length >= 2; callers must validate sizes and addresses elsewhere. Include dependency on `vmci_context.h` makes this part of the internal subsystem cycle.

Test signals: ioctl struct size/version compatibility, old/new VMX page-file paths, page-store validation, and qpair allocation behavior across host/guest personalities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_queue_pair.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_resource.c -->
# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_resource.c

Purpose: implements the global VMCI resource table used to map handles to datagram, doorbell, and queue-pair resources with kref lifetime and RCU lookup.

Important APIs/functions: `vmci_resource_add()` validates uniqueness or allocates a free resource ID, initializes the resource, and inserts into a hash bucket. `vmci_resource_remove()` unlinks under lock, waits for RCU, drops the table reference, and waits for completion after final kref release. `vmci_resource_by_handle()` looks up and kref-gets a resource. `vmci_resource_get()/put()` wrap kref access, and `vmci_resource_handle()` returns the assigned handle.

Control flow: lookup hashes by resource ID and matches type, resource ID, and compatible context ID, allowing wildcard invalid context in either stored or requested handle. ID allocation cycles through nonreserved resource IDs and checks lookup for collisions. Removal waits until no outstanding references remain before callers free the containing object.

State/persistence: static hash table of 128 buckets guarded by spinlock for mutation and RCU for readers. Resource lifetime is volatile and tied to module state.

Dependencies/integration: used by datagram, doorbell, queue-pair guest endpoints, and broker entries. Depends on VMCI handle helpers and kernel kref/completion/RCU.

Risks: hash only uses resource ID, so buckets can be hot if many contexts use same RID patterns. `vmci_resource_add()` calls lookup while holding the table spinlock; lookup uses RCU and assumes this nesting is acceptable. Wildcard context matching is powerful and must be used carefully for ANYCID handles.

Test signals: duplicate add, auto-ID wraparound, wildcard context lookup, remove with outstanding refs, type filtering, and concurrent lookup/remove races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_resource.h -->
# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_resource.h

Purpose: declares VMCI resource types and the common resource header embedded in datagram, doorbell, and queue-pair objects.

Important types/APIs: `enum vmci_resource_type` distinguishes API, group, datagram, doorbell, guest qpair, host qpair, and wildcard lookups. `struct vmci_resource` stores handle, type, hash node, kref, and completion used for removal synchronization. Prototypes cover add, remove, lookup by handle, get, put, and handle retrieval.

Control flow/integration: embedding objects add their resource on creation, use resource lookup for external handles, and remove it before freeing container memory.

State/persistence: no persistent state in the header, but the struct is the lifetime anchor for global handle resolution.

Risks: embedded object cleanup must respect `vmci_resource_remove()` waiting semantics. Any new resource type must preserve lookup and wildcard behavior.

Test signals: resource lifecycle in each embedding subsystem and type-specific lookup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_route.c -->
# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_route.c

Purpose: central routing decision logic for VMCI datagrams and queue-pair route selection. It determines whether an operation should be handled locally as host, sent through the guest device to the hypervisor/host, or rejected.

Important API: `vmci_route(struct vmci_handle *src, const struct vmci_handle *dst, bool from_guest, enum vmci_route *route)` validates destination, samples host/guest activity, may fill an invalid source context with current context ID, and returns a route enum plus VMCI status.

Control flow: hypervisor destinations require active guest device and cannot be forwarded from guest-origin ioctls. Host destinations may route as guest when a local client in a guest must send down to the host, or as host for local host/hypervisor delivery. Non-host destinations first try active host contexts; VM-to-VM via host is rejected. If no host context path applies, active guest device routes down to the host for older VM-to-VM-capable environments.

State/persistence: no owned state; decisions are based on current host/guest personality activity and context existence.

Dependencies/integration: used by datagram dispatch and qpair allocation to select host versus guest implementation. Relies on `vmci_host_code_active()`, `vmci_guest_code_active()`, `vmci_get_context_id()`, and `vmci_ctx_exists()`.

Risks: host/guest active state can change after routing, so send paths must revalidate device availability. The function mutates `src->context`, which callers must expect. Unified host+guest mode intentionally removes ambiguous local host-to-host routing in some cases by preferring guest route for local clients.

Test signals: invalid destination, hypervisor route from guest rejection, no-device errors, host local delivery, guest-to-host route, host-to-guest context delivery, VM-to-VM rejection, and invalid source context fill-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_route.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_route.h -->
# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_route.h

Purpose: declares the VMCI route enum and route-selection helper.

Important APIs/types: `enum vmci_route` has `VMCI_ROUTE_NONE`, `VMCI_ROUTE_AS_HOST`, and `VMCI_ROUTE_AS_GUEST`. `vmci_route()` decides the route for source/destination handles and may normalize an invalid source context.

Control flow/integration: datagram and queue-pair code include this header to avoid duplicating personality-selection logic.

State/persistence: no state.

Risks: route enum additions would require updates to all dispatch switch/if logic. Callers must pass mutable source handles because the function can fill the context.

Test signals: compile coverage for every route consumer and unit-style matrix tests for host/guest/personality combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_route.h -->
