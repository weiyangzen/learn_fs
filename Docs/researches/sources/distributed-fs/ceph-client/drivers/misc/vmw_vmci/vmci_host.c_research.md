# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_host.c

Purpose: implements the host personality exposed as `/dev/vmci`. It lets VMX processes create contexts, send/receive datagrams, allocate/map/detach queue pairs, manage context notifications, checkpoint selected state, configure notify flags, and receive doorbell notifications.

Important APIs/functions: `vmci_host_init()` creates the host context and registers the misc device. `vmci_host_exit()` deregisters it and exits the queue-pair broker. File ops include open/close/poll/ioctl. Ioctl handlers cover context init, datagram send/receive, queue-pair allocation/set VA/set page file/detach, context add/remove notification, checkpoint get/set, context ID query, notify-page setup, notify-resource operations, and pending notification receive.

Control flow: open allocates per-file `vmci_host_dev`; init-context ioctl creates a `vmci_ctx` with current credentials and increments active users. Poll waits on the context wait queue and reports readable if datagrams or doorbells are pending. Send ioctl copies a userspace datagram, validates size, dispatches with the file context CID, and returns VMCI status. Receive ioctl dequeues from the context queue and copies the datagram back. Close destroys the context and decrements active users.

State/persistence: global `host_context`, `vmci_host_device_initialized`, and `vmci_host_active_users` model host personality activity. Per-open state stores context pointer, user VMCI version, object type, and mutex. Notify setup pins and maps a userspace page until unset or context teardown. Checkpoint ioctls serialize notifier and doorbell state for VMX.

Dependencies/integration: integrates Linux miscdevice/file/ioctl/poll/usercopy APIs with VMCI context, datagram, queue-pair broker, doorbell notification, event, and resource subsystems.

Risks: all ioctl structures are ABI-facing and copy raw user virtual addresses. Version-dependent queue-pair paths are complex, especially old VMX page-file compatibility. The SetPageFile handler pre-writes success before doing the operation to avoid unwind complexity, which is intentional but unusual. Notify-page mapping uses pinned user memory and must always be released.

Test signals: ioctl ABI compatibility across VMCI versions, context init/close lifecycle, poll wakeups, datagram size mismatch, queue-pair old/new version flows, notification receive with partial user buffers, notify page setup/unset, and failure unwinds for copy_to_user/copy_from_user.
