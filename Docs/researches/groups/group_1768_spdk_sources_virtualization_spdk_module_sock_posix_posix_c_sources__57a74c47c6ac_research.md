# Group Research: group_1768_spdk_sources_virtualization_spdk_module_sock_posix_posix_c_sources__57a74c47c6ac

Scope checked against `Docs/research_subset_a.md`: these files are within `sources/virtualization/spdk`, which is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/sock/posix/posix.c -->
# File Research: sources/virtualization/spdk/module/sock/posix/posix.c

Implements SPDK’s default POSIX socket network backend plus the SSL socket backend. It registers `posix` as the default `spdk_net_impl` and `ssl` as an additional implementation.

Key responsibilities:
- Socket lifecycle: listen, connect, async connect, accept, close.
- Address helpers: local/peer address lookup, interface-name lookup, NUMA lookup via sysfs.
- Runtime socket operations: `recv`, `readv`, `writev`, async write queueing, flush, connectivity checks, IPv4/IPv6 checks.
- Group polling: epoll on Linux, kqueue on FreeBSD, with a `socks_with_data` queue for level-triggered behavior and fairness rotation.
- Receive buffering: optional `spdk_pipe` receive pipe, including resize, drain, and group integration.
- Zerocopy send support when `SO_ZEROCOPY` and `MSG_ZEROCOPY` are available, including ERRQUEUE completion tracking.
- Placement ID support for grouping sockets by CPU/NIC queue via `spdk_sock_map`.
- TLS/SSL support through OpenSSL, including TLS 1.3 PSK session callbacks, optional kTLS, cipher-suite configuration, and SSL read/write wrappers.

Important structures:
- `struct spdk_posix_sock`: wraps `spdk_sock`, fd, recv pipe, zerocopy state, SSL context/object, placement id, async connect context, and group list node.
- `struct spdk_posix_sock_group_impl`: wraps `spdk_sock_group_impl`, epoll/kqueue fd, interrupt handle, receive-ready list, placement id, and pipe group.
- `struct posix_connect_ctx`: preserves async connect state across address candidates and delayed socket options.

Control flow:
- `_posix_sock_connect()` allocates a socket and creates an async connect context even for synchronous connects; synchronous connect repeatedly calls `posix_connect_poller()`.
- `posix_connect_poller()` handles timeout, connect completion, fallback to the next resolved address, deferred SSL setup, deferred recv/send buffer and low-water settings, and delayed group add.
- `_sock_flush()` prepares queued SPDK socket requests, sends with `sendmsg` or `SSL_write`, advances request offsets, moves complete requests to pending, and completes non-zerocopy requests immediately.
- `_sock_check_zcopy()` consumes socket ERRQUEUE messages and completes pending zerocopy requests by kernel notification index.
- `posix_sock_group_impl_poll()` flushes writes on all group sockets, polls epoll/kqueue, marks sockets with data, returns sockets with callbacks, and rotates the ready list for fairness.

Dependencies and integration points:
- Uses shared sock helpers from `spdk_internal/sock_module.h`.
- Uses `spdk_pipe` and `spdk_pipe_group` for receive buffering.
- Uses Linux `errqueue` and zerocopy APIs conditionally.
- Uses OpenSSL for the `ssl` net implementation.
- Registers `g_posix_net_impl` via `SPDK_NET_IMPL_REGISTER_DEFAULT(posix, ...)`.
- Registers `g_ssl_net_impl` via `SPDK_NET_IMPL_REGISTER(ssl, ...)`.

Notes:
- SSL sockets intentionally disable zerocopy.
- Async connect methods return sockets before readiness; many operations first call `posix_connect_poller()` or report `-EAGAIN`/`-ENOTCONN`.
- Interrupt-mode readiness is based on the group fd, but the implementation also preserves ready sockets in an internal queue for level-triggered behavior.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/sock/posix/posix.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/sock/uring/Makefile -->
# File Research: sources/virtualization/spdk/module/sock/uring/Makefile

Builds the SPDK io_uring socket implementation as library `sock_uring`.

Key contents:
- Sets `SPDK_ROOT_DIR` to the SPDK root relative to `module/sock/uring`.
- Includes `mk/spdk.common.mk`.
- Declares shared object version `SO_VER := 7` and minor `SO_MINOR := 0`.
- Builds `C_SRCS = uring.c`.
- Uses the blank export map `mk/spdk_blank.map`.
- Includes `mk/spdk.lib.mk`.

Role:
- This file is purely build metadata for `uring.c`; it does not include feature gates directly. Runtime registration in `uring.c` probes whether io_uring buffered-ring support is available before registering the implementation.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/sock/uring/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/sock/uring/uring.c -->
# File Research: sources/virtualization/spdk/module/sock/uring/uring.c

Implements SPDK’s Linux io_uring socket backend. It registers a `uring` `spdk_net_impl` only if a probe group can be created successfully.

Key responsibilities:
- Socket lifecycle: listen, connect, dummy async connect, accept, close.
- Socket operations: `recv`, `readv`, `writev`, async write queueing, flush, recv-next, low-water/buffer setters, IPv4/IPv6 checks, connectivity checks.
- io_uring group processing: queue initialization, SQE submission, CQE reaping, read/write/ERRQUEUE/cancel task handling.
- Provided-buffer receive path: io_uring buffer ring registration, tracker management, user buffer acquisition/return through `spdk_sock_group_get_buf()` and `spdk_sock_group_provide_buf()`.
- Optional receive-pipe path mirroring the POSIX implementation.
- Optional zerocopy send handling using ERRQUEUE completions.
- Placement ID lookup and socket-group mapping with `spdk_sock_map`.

Important structures:
- `struct spdk_uring_sock`: wraps `spdk_sock`, fd, per-socket tasks (`write_task`, `read_task`, `errqueue_task`, `cancel_task`), recv stream, recv pipe, zerocopy state, connection status, placement id, and callback data.
- `struct spdk_uring_task`: represents one io_uring operation and stores task type, status, msghdr/iovs, final request pointer, and zerocopy flag.
- `struct spdk_uring_sock_group_impl`: wraps `spdk_sock_group_impl`, owns the `io_uring`, inflight/queued/available counters, pending receive list, buffer ring, tracker array, and free tracker list.
- `struct spdk_uring_buf_tracker`: tracks a user-provided buffer posted to the io_uring buffer ring.

Control flow:
- `uring_sock_create()` handles both listen and connect paths using shared POSIX fd helper routines, then allocates an io_uring socket.
- `uring_sock_connect_async()` is intentionally a dummy async wrapper around synchronous connect; it stores the callback and invokes it during flush/poll, avoiding immediate callback-before-return behavior.
- `uring_sock_group_impl_create()` creates a queue with depth `4096`, registers a provided-buffer ring, and inserts CPU placement mapping if configured.
- `uring_sock_group_impl_add_sock()` initializes per-socket tasks, starts a receive SQE immediately, and starts an ERRQUEUE receive SQE for zerocopy sockets.
- `uring_sock_group_impl_poll()` flushes socket writes, repopulates the buffer ring, submits queued SQEs, reaps completions, and returns sockets with pending receive events.
- `sock_uring_group_reap()` is the central CQE dispatcher for read, write, ERRQUEUE, and cancel completions.
- `uring_sock_group_impl_remove_sock()` synchronously cancels active write/read/errqueue tasks, drains cancel completions through polling, removes pending receive state, releases placement mapping, and detaches the socket from the group.

Dependencies and integration points:
- Requires Linux io_uring via `<liburing.h>`.
- Reuses SPDK POSIX socket fd helpers for address resolution, fd creation, and connect setup.
- Uses SPDK socket request helpers for async write queue handling.
- Uses SPDK socket group buffer APIs for provided-buffer receive mode.
- Constructor `net_impl_register_uring()` creates and closes a probe group before registering `g_uring_net_impl`.

Notes:
- Interrupt mode is explicitly unsupported by `uring_net_impl_init()`.
- TLS fields exist in copied implementation options but this backend does not implement SSL.
- The receive path differs significantly depending on whether `enable_recv_pipe` is set: with pipes, reads can use direct `recvmsg`; without pipes and in a group, io_uring buffer-ring completions populate `recv_stream`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/sock/uring/uring.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/vfu_device/Makefile -->
# File Research: sources/virtualization/spdk/module/vfu_device/Makefile

Builds the vfio-user virtio device module as library `vfu_device`.

Key contents:
- Sets `SPDK_ROOT_DIR` to the SPDK root relative to `module/vfu_device`.
- Includes `mk/spdk.common.mk`.
- Declares shared object version `SO_VER := 5` and minor `SO_MINOR := 0`.
- Always builds:
  - `vfu_virtio.c`
  - `vfu_virtio_blk.c`
  - `vfu_virtio_scsi.c`
  - `vfu_virtio_rpc.c`
- Adds `vfu_virtio_fs.c` only when `CONFIG_FSDEV=y`.
- Uses `mk/spdk_blank.map`.
- Includes `mk/spdk.lib.mk`.

Role:
- This Makefile defines the compilation boundary for common virtio-over-vfio-user code, block and SCSI device models, RPC glue, and optional virtio-fs support.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/vfu_device/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/vfu_device/vfu_virtio.c -->
# File Research: sources/virtualization/spdk/module/vfu_device/vfu_virtio.c

Common virtio-over-vfio-user implementation used by the virtio-blk, virtio-scsi, and virtio-fs endpoint models.

Key responsibilities:
- Creates and tears down a vfio-user-backed virtio PCI BAR4 memory region.
- Emulates modern virtio PCI common configuration, ISR access, device-specific config, and notification BAR layout.
- Handles feature negotiation, device status transitions, reset, start, and stop.
- Maps and unmaps guest virtqueue memory using SPDK vfio-user DMA mapping helpers.
- Supports both split and packed virtqueues.
- Parses available descriptors into `vfu_virtio_req` IOV arrays.
- Enqueues used descriptors and triggers IRQs with optional interrupt coalescing.
- Provides attach/detach, memory hot-add/remove handling, PCI reset handling, quiesce support, and vendor capability generation.

Important structures come from `vfu_virtio_internal.h`:
- `vfu_virtio_endpoint`: per endpoint transport state.
- `vfu_virtio_dev`: per attached virtio device state.
- `vfu_virtio_vq`: per virtqueue mapping and ring state.
- `vfu_virtio_req`: per request descriptor and mapped IOV state.

Control flow:
- `vfu_virtio_endpoint_setup()` creates an unlinked file for BAR4, truncates it to the virtio BAR size, mmaps the notification region, stores endpoint ops, and sets default queue count/size.
- `vfu_virtio_attach_device()` allocates the device and request pools for all queues, initializes queue SG storage, gets model-specific supported features, and attaches the device to the endpoint.
- `virtio_vfu_pci_common_cfg()` handles common-config reads/writes, including selected feature pages, queue selection, queue size/vector/enable, queue physical addresses, and device status writes.
- `virtio_dev_enable_vq()` maps descriptor, available, and used rings, initializes ring indices, and sets packed-ring phase state when negotiated.
- `vfu_virtio_dev_process_split_ring()` and `vfu_virtio_dev_process_packed_ring()` pull available descriptors, allocate request objects, map descriptors into IOVs, and dispatch via `virtio_ops.exec_request`.
- `vfu_virtio_finish_req()` decrements outstanding I/O, writes the used-ring entry, and returns the request to its free queue.
- `vfu_virtio_vq_flush_irq()` posts interrupts only when there are used requests, guest notification suppression permits it, and coalescing timing allows it.
- `vfu_virtio_quiesce_cb()` returns busy while outstanding I/O exists and completes quiesce asynchronously through a poller.

Dependencies and integration points:
- Calls into model-specific `vfu_virtio_ops` for feature bits, request allocation/free, request execution, config get/set, and start/stop hooks.
- Uses `spdk_vfu_map_one()`, `spdk_vfu_unmap_sg()`, libvfio-user `vfu_irq_trigger()`, and SPDK endpoint helper APIs.
- Uses Linux virtio headers for PCI and ring layout definitions.
- Exports endpoint/device utility functions used by blk/scsi/fs modules.

Notes:
- Notification BAR accesses are expected to be sparse mmap accesses; direct MMIO read/write to the notification range asserts.
- Queue mapping is retried on memory add and selectively unmapped before memory remove.
- The file contains misspelled exported helper names `virito_dev_*_get_next_avail_req`; callers use those exact symbols.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/vfu_device/vfu_virtio.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/vfu_device/vfu_virtio_blk.c -->
# File Research: sources/virtualization/spdk/module/vfu_device/vfu_virtio_blk.c

Implements the virtio-blk device model over the common vfio-user virtio transport.

Key responsibilities:
- Registers the `virtio_blk` SPDK vfio-user endpoint model.
- Opens an SPDK bdev and exposes it as a virtio-blk PCI device.
- Builds `virtio_blk_config` from bdev capacity, block size, queue count, topology, discard, write-zeroes, and flush capabilities.
- Polls virtqueues and dispatches block requests to SPDK bdev I/O.
- Handles bdev remove and resize events.
- Provides device feature bits and device-specific configuration reads.

Important structures:
- `struct virtio_blk_endpoint`: embeds `vfu_virtio_endpoint`, bdev descriptor, bdev pointer, I/O channel, virtio block config, init thread, and ring poller.
- `struct virtio_blk_req`: wraps `vfu_virtio_req` and stores the response status byte pointer and endpoint pointer.

Request handling:
- `virtio_blk_process_req()` validates the request header and response status descriptor.
- Supports:
  - `VIRTIO_BLK_T_IN`: `spdk_bdev_readv()`
  - `VIRTIO_BLK_T_OUT`: `spdk_bdev_writev()`
  - `VIRTIO_BLK_T_DISCARD`: `spdk_bdev_unmap()`
  - `VIRTIO_BLK_T_WRITE_ZEROES`: `spdk_bdev_write_zeroes()`
  - `VIRTIO_BLK_T_FLUSH`: `spdk_bdev_flush()`
  - `VIRTIO_BLK_T_GET_ID`: copies the bdev name padded to the virtio block ID field
- Completes requests through `blk_request_complete_cb()` or immediate status completion.
- Sets `req->used_len` according to virtio-blk direction and response semantics.

Lifecycle:
- `vfu_virtio_blk_add_bdev()` finds an existing vfio-user endpoint, sets queue options, opens the bdev, updates config, and records the init thread.
- `virtio_blk_start()` gets the bdev I/O channel and registers the virtqueue poller.
- `virtio_blk_stop()` sends a stop message to the endpoint thread to unregister the poller and release the I/O channel.
- Endpoint destruct closes the bdev descriptor on the init thread, destructs common virtio endpoint state, and frees the endpoint.

Integration:
- Uses common virtio helpers for ring polling and request completion.
- Uses SPDK bdev APIs for all storage I/O.
- Registers endpoint ops in a constructor via `spdk_vfu_register_endpoint_ops(&vfu_virtio_blk_ops)`.
- Fills PCI device ID with `PCI_DEVICE_ID_VIRTIO_BLK_MODERN`.

Notes:
- Payload length must be nonzero and 512-byte aligned for read/write commands.
- Bdev removal zeroes config, stops the device if active, closes the descriptor asynchronously, and causes later requests to fail with I/O error.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/vfu_device/vfu_virtio_blk.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/vfu_device/vfu_virtio_fs.c -->
# File Research: sources/virtualization/spdk/module/vfu_device/vfu_virtio_fs.c

Implements optional virtio-fs over the common vfio-user virtio transport. It is compiled only when FSDEV support is enabled.

Key responsibilities:
- Registers the `virtio_fs` SPDK vfio-user endpoint model.
- Creates and owns an SPDK FUSE dispatcher for a configured fsdev.
- Exposes virtio-fs configuration, including tag and request queue count.
- Polls virtqueues and forwards FUSE requests to the dispatcher.
- Handles fsdev removal and asynchronous dispatcher deletion.
- Provides endpoint add function used by the RPC layer.

Important structures:
- `struct virtio_fs_endpoint`: embeds `vfu_virtio_endpoint`, FUSE dispatcher, init thread, I/O channel, virtio-fs config, destruction state, and ring poller.
- `struct virtio_fs_req`: wraps `vfu_virtio_req` and stores endpoint and status pointer fields.

Request handling:
- `virtio_fs_process_req()` validates that the first descriptor contains a `fuse_in_header`.
- It splits the request IOV array into input IOVs and output IOVs by summing input lengths until `fuse_in_header.len` is reached.
- Submits the request to `spdk_fuse_dispatcher_submit_request()`.
- Completion callback `virtio_fs_fuse_req_done()` finishes the virtio request with the negated FUSE error status.

Lifecycle:
- `vfu_virtio_fs_add_fsdev()` validates endpoint, fsdev name, and tag, sets queue options, fills `virtio_fs_config`, allocates async context, and creates the FUSE dispatcher.
- `virtio_fs_start()` gets the dispatcher I/O channel and registers the ring poller.
- `virtio_fs_stop()` sends a stop message to the endpoint thread to unregister the poller and release the channel.
- Destruction is asynchronous if a dispatcher still exists: it initiates dispatcher deletion and returns `-EAGAIN` until deletion completes.

Integration:
- Uses common virtio helpers for ring handling and PCI/vfio-user endpoint behavior.
- Uses `spdk_internal/fuse_dispatcher.h` and Linux FUSE/virtio-fs headers.
- Registers endpoint ops via constructor.
- Fills PCI device ID with `PCI_DEVICE_ID_VIRTIO_FS`.

Notes:
- `VIRTIO_FS_SUPPORTED_FEATURES` is currently zero beyond common host virtio features.
- The RPC layer marks virtio-fs vfio-user support as deprecated for removal in `v26.09`.
- The code includes a duplicated `spdk/stdinc.h` include, but it is harmless.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/vfu_device/vfu_virtio_fs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/vfu_device/vfu_virtio_internal.h -->
# File Research: sources/virtualization/spdk/module/vfu_device/vfu_virtio_internal.h

Internal shared header for vfio-user virtio device implementations.

Key contents:
- Defines host-supported common virtio features:
  - `VIRTIO_F_VERSION_1`
  - `VIRTIO_RING_F_INDIRECT_DESC`
  - `VIRTIO_F_RING_PACKED`
- Defines the virtio PCI BAR4 layout:
  - common config
  - ISR access
  - device-specific config
  - notifications
- Defines queue and request limits:
  - `VIRTIO_DEV_MAX_IOVS`
  - `VIRTIO_DEV_VRING_MAX_REQS`
  - `VIRTIO_DEV_MAX_VQS`
  - default/max queue sizes.

Important data structures:
- `struct virtio_pci_cfg`: tracks selected feature pages, negotiated guest features, MSI-X config vector, status, config generation, queue selection, and ISR byte.
- `enum vfu_vq_state`: created, active, inactive.
- `struct q_mapping`: stores guest queue DMA mapping, SG entry, physical address, local IOV, virtual address union, and length.
- `struct vfu_virtio_vq`: stores queue identity, size, enable/vector state, ring addresses, mapped queue regions, split/packed ring indices and phases, used request count, and interrupt coalescing timestamp.
- `struct vfu_virtio_dev`: stores device name, queue count, host features, PCI config state, queue array, backpointer to endpoint, and SG storage.
- `struct vfu_virtio_ops`: model-specific callbacks for features, request allocation/free, request execution, config get/set, and device start/stop.
- `struct vfu_virtio_endpoint`: per endpoint common state, including BAR fd, notification mapping, queue defaults, packed-ring flag, coalescing delay, SPDK endpoint/thread, operation table, outstanding I/O, and quiesce poller state.
- `struct vfu_virtio_req`: common request object containing queue/device pointers, used length, split/packed descriptor identifiers, mapped IOVs, writeability flags, indirect descriptor mapping, and SG storage.

Inline helpers:
- Feature check helper.
- Queue desc/avail/used region size calculators for split and packed rings.
- Event suppression check for split and packed queues.
- Device started check.
- Descriptor flag helpers for indirect and writeable descriptors.
- Packed-ring available/used phase tests.
- Request writeability check.
- Alloc/free wrappers around model-specific callbacks.

Exports:
- Common ring enqueue, ring processing, request completion, IRQ flushing, config notification, endpoint setup/destruct, attach/detach, memory add/remove, reset, quiesce, vendor capability, and model-specific public entry points for blk/scsi/fs.

Notes:
- This header is the contract between common virtio transport code and the individual device models.
- It depends on Linux virtio headers and `spdk/vfu_target.h`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/vfu_device/vfu_virtio_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/vfu_device/vfu_virtio_rpc.c -->
# File Research: sources/virtualization/spdk/module/vfu_device/vfu_virtio_rpc.c

Defines JSON-RPC methods for managing vfio-user virtio endpoints and their backing devices/targets.

RPCs:
- `vfu_virtio_delete_endpoint`
  - Decodes `name`.
  - Calls `spdk_vfu_delete_endpoint()`.
  - Returns boolean success or invalid-params error.

- `vfu_virtio_create_blk_endpoint`
  - Decodes `name`, `bdev_name`, optional `cpumask`, optional `num_queues`, optional `qsize`, optional `packed_ring`.
  - Creates a `virtio_blk` vfio-user endpoint.
  - Calls `vfu_virtio_blk_add_bdev()`.
  - Deletes the endpoint on add failure.

- `vfu_virtio_scsi_add_target`
  - Decodes `name`, `scsi_target_num`, `bdev_name`.
  - Calls `vfu_virtio_scsi_add_target()`.

- `vfu_virtio_scsi_remove_target`
  - Decodes `name`, `scsi_target_num`.
  - Calls `vfu_virtio_scsi_remove_target()`.

- `vfu_virtio_create_scsi_endpoint`
  - Decodes `name`, optional `cpumask`, optional `num_io_queues`, optional `qsize`, optional `packed_ring`.
  - Creates a `virtio_scsi` vfio-user endpoint.
  - Applies options through `vfu_virtio_scsi_set_options()`.
  - Deletes the endpoint on option failure.

- `vfu_virtio_create_fs_endpoint`
  - Compiled only under `SPDK_CONFIG_FSDEV`.
  - Decodes `name`, `fsdev_name`, `tag`, optional `cpumask`, optional `num_queues`, optional `qsize`, optional `packed_ring`.
  - Emits a deprecation log for virtio-fs vfio-user support removal in `v26.09`.
  - Creates a `virtio_fs` endpoint and calls async `vfu_virtio_fs_add_fsdev()`.
  - Sends JSON-RPC success response from completion callback.

Dependencies and integration:
- Uses autogen RPC context structs and free helpers from `spdk_internal/rpc_autogen.h`.
- Uses SPDK JSON decoders and JSON-RPC response helpers.
- Calls public entry points declared in `vfu_virtio_internal.h`.

Notes:
- Most errors are reported as `SPDK_JSONRPC_ERROR_INVALID_PARAMS` with `spdk_strerror(-rc)`.
- The fs endpoint RPC completion ignores the `status` argument and always sends success; setup-time synchronous errors still go through the invalid path.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/vfu_device/vfu_virtio_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/vfu_device/vfu_virtio_scsi.c -->
# File Research: sources/virtualization/spdk/module/vfu_device/vfu_virtio_scsi.c

Implements the virtio-scsi device model over the common vfio-user virtio transport.

Key responsibilities:
- Registers the `virtio_scsi` SPDK vfio-user endpoint model.
- Exposes a virtio-scsi controller with task-management queue, event queue, and I/O queues.
- Maps SCSI targets to SPDK SCSI devices backed by bdevs.
- Polls virtqueues and dispatches SCSI commands/task management to SPDK SCSI.
- Supports hotplug, hotremove, and resize/change notifications through the virtio-scsi event queue.
- Provides device-specific config get/set and queue option setup.

Important structures:
- `struct virtio_scsi_endpoint`: embeds common `vfu_virtio_endpoint`, holds virtio-scsi config, up to 8 target slots, and ring poller.
- `struct virtio_scsi_target`: stores an SPDK SCSI device pointer.
- `struct virtio_scsi_req`: wraps `vfu_virtio_req`, embeds an `spdk_scsi_task`, and stores virtio-scsi command/TMF request and response pointers.

Queue model:
- Queue 0 is used for task management.
- Queue 1 is the event queue.
- Other queues are I/O queues.
- The polling path skips queue 1 because events are enqueued by explicit event helpers.

Request handling:
- `virtio_scsi_process_req()` routes queue 0 requests to `virtio_scsi_tmf_cmd_req()` and all other processed queues to `virtio_scsi_cmd_req()`.
- `virtio_scsi_cmd_data_setup()` validates command request/response descriptors, determines data direction from descriptor writeability, sets SPDK SCSI task IOVs, CDB pointer, transfer length, and response default.
- `virtio_scsi_cmd_lun_setup()` validates virtio LUN format, finds the target, locates port 0 and LUN, and attaches them to the SCSI task.
- `virtio_scsi_cmd_req()` queues regular SCSI tasks with `spdk_scsi_dev_queue_task()`.
- `virtio_scsi_tmf_cmd_req()` supports logical unit reset via `spdk_scsi_dev_queue_mgmt_task()` and rejects unsupported task-management subtypes.
- Completion callbacks populate virtio-scsi response status, sense data, residual length, then finish the virtio request and release the SCSI task.

Target and event handling:
- `vfu_virtio_scsi_add_target()` constructs an SPDK SCSI device with one LUN backed by a bdev, adds port 0, updates config, and sends a hotplug event if the virtio device is already attached.
- `vfu_virtio_scsi_remove_target()` either schedules hotremove on the virtio thread or destructs the SCSI device immediately when unattached.
- Resize and hotremove callbacks find the target number by LUN and send messages to the virtio thread.
- `vfu_virtio_scsi_eventq_enqueue()` consumes one descriptor from the event queue, writes a `virtio_scsi_event`, completes it, and flushes the event queue IRQ.

Lifecycle:
- `virtio_scsi_start()` allocates I/O channels for present SCSI devices and registers the ring poller.
- `virtio_scsi_stop()` unregisters the poller and frees SCSI I/O channels.
- Endpoint destruct destructs all remaining SCSI devices, destructs common endpoint state, and frees the endpoint.
- Endpoint init sets up common virtio endpoint state and initializes virtio-scsi config.

Integration:
- Uses common virtio vfio-user helpers for PCI/device/queue handling.
- Uses SPDK SCSI APIs for command execution and bdev-backed SCSI device construction.
- Registers endpoint ops in a constructor via `spdk_vfu_register_endpoint_ops(&vfu_virtio_scsi_ops)`.
- Fills PCI device ID with `PCI_DEVICE_ID_VIRTIO_SCSI_MODERN`.

Notes:
- Maximum target count is fixed at 8.
- Unsupported changes to `sense_size` or `cdb_size` are rejected.
- Event queue notification depends on negotiated `VIRTIO_SCSI_F_HOTPLUG` and `VIRTIO_SCSI_F_CHANGE`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/vfu_device/vfu_virtio_scsi.c -->