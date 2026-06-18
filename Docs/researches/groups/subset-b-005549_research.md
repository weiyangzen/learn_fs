# subset-b-005549 Research

Grouped source research for the vhost core and vhost net, SCSI, test, and vDPA frontends. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/net.c -->
# sources/distributed-fs/ceph-client/drivers/vhost/net.c

## Purpose

`net.c` implements the `/dev/vhost-net` misc device, a kernel vhost backend for virtio-net. It binds guest TX and RX virtqueues to host networking endpoints, primarily TAP/TUN and AF_PACKET raw sockets, and uses the shared vhost core to translate virtqueue descriptors, poll eventfds, log dirty memory, and signal completions. The file contains both the normal copy path and optional experimental TX zerocopy path, plus an XDP batching path for high-throughput TAP/TUN transmission.

## Important APIs, Types, and Functions

The main state is `struct vhost_net`, which embeds `struct vhost_dev`, two `struct vhost_net_virtqueue` instances, backend socket polls, TX zerocopy counters, and a page-frag cache. `struct vhost_net_virtqueue` extends `struct vhost_virtqueue` with virtio-net header lengths, zerocopy state (`upend_idx`, `done_idx`, `ubuf_info`, `ubufs`), an RX `ptr_ring`, a small batched RX queue, and a batched XDP buffer array. `struct vhost_net_ubuf_ref` is the reference-counted completion object used by zerocopy TX.

The device surface is `vhost_net_fops`, especially `vhost_net_open()`, `vhost_net_release()`, `vhost_net_ioctl()`, `vhost_net_chr_read_iter()`, `vhost_net_chr_write_iter()`, and `vhost_net_chr_poll()`. Frontend-specific ioctls are handled by `vhost_net_set_backend()`, `vhost_net_set_features()`, `vhost_net_set_owner()`, and `vhost_net_reset_owner()`. Data-path workers are `handle_tx()`, `handle_tx_copy()`, `handle_tx_zerocopy()`, `handle_rx()`, and the kick/socket-poll trampolines `handle_tx_kick()`, `handle_rx_kick()`, `handle_tx_net()`, and `handle_rx_net()`.

Backend helpers include `get_raw_socket()`, `get_tap_socket()`, `get_tap_ptr_ring()`, and `get_socket()`. Zerocopy helpers include `vhost_net_ubuf_alloc()`, `vhost_zerocopy_complete()`, `vhost_zerocopy_signal_used()`, and `vhost_net_flush()`. RX/TX descriptor helpers include `get_tx_bufs()`, `get_rx_bufs()`, `init_iov_iter()`, `vhost_net_build_xdp()`, `vhost_tx_batch()`, and `vhost_net_signal_used()`.

## Control Flow

Open allocates the device, the vq pointer array, RX batching queue, TX XDP batch buffer, initializes both virtqueues and socket polls, and stores the device in `file->private_data`. Userspace first sets owner through the shared vhost ioctl path, configures memory and vring state, negotiates features, and then uses `VHOST_NET_SET_BACKEND` to attach each virtqueue to a socket fd. Backend setup validates owner and ring access, resolves the fd to a supported socket, disables old polling, installs the new backend, initializes vq access, starts polling, and records the TAP/TUN RX `ptr_ring` when available.

TX starts from a guest kick or socket writable poll. `handle_tx()` locks the TX vq, checks backend and metadata access, disables guest notifications and socket polling, then selects zerocopy only when the socket has `SOCK_ZEROCOPY` and the module parameter enabled it. The copy path repeatedly obtains one descriptor chain with `vhost_get_vq_desc_n()`, rejects input descriptors on TX, skips the virtio header, and sends the payload through `sock->ops->sendmsg()`. If batching is possible, it converts packet data to XDP buffers and flushes them with a `TUN_MSG_PTR` control message through `vhost_tx_batch()`. Otherwise it uses `MSG_MORE` according to total length and ring availability. On transient send pressure it discards the descriptor cursor with `vhost_discard_vq_desc()`, re-enables socket polling, and exits.

The zerocopy path records the descriptor in `vq->heads[upend_idx]`, attaches a `ubuf_info_msgzc` with `vhost_ubuf_ops`, increments the ubuf reference, and sends the packet with `TUN_MSG_UBUF`. Completion arrives in `vhost_zerocopy_complete()`, marks the corresponding head as done or failed, drops the ubuf ref, and queues vhost work periodically or when the count drains. `vhost_zerocopy_signal_used()` advances contiguous completed heads and publishes them to the used ring.

RX starts from a guest kick or socket readable poll. `handle_rx()` locks the RX vq, checks metadata, disables notifications and socket polling, peeks the next packet length either from TAP/TUN `ptr_ring` or socket receive queue, and optionally busy-polls the paired TX queue. It then collects enough guest input descriptors through `get_rx_bufs()`, receives the socket packet into the guest iovecs, supplies or patches the virtio-net header and `num_buffers`, logs dirty writes when requested, batches used-ring entries, and re-enables polling or notifications when no packet or no descriptors are available.

## State and Persistence Behavior

All state is per-open file and lives in memory. There is no disk persistence. Persistent-for-open state includes negotiated feature bits on each vq, derived header lengths (`vhost_hlen` and `sock_hlen`), backend socket references, RX ring pointers, XDP batch buffers, zerocopy completion arrays, and the shared vhost memory/IOTLB state. `vhost_net_stop()` clears backends and stops polling. `vhost_net_flush()` drains vhost workers and zerocopy DMA completions. `vhost_net_release()` stops backends, flushes twice to cover self-requeued work, drops socket refs, drains RCU, frees buffers, and releases the vhost core state.

## Dependencies and Integration Points

The file depends on `vhost.c` and `vhost.h` for virtqueue parsing, eventfd polling, worker execution, IOTLB miss handling, dirty logging, and owner/memory ioctls. It integrates with Linux socket operations, TAP/TUN helpers (`tun_get_socket()`, `tun_get_tx_ring()`, `tun_ptr_free()`), TAP helpers, AF_PACKET raw sockets, XDP buffer APIs, skb queue inspection, page-frag allocation, eventfd, miscdevice registration, and virtio-net feature definitions. Userspace components such as QEMU configure this device through vhost ioctls and pass the TAP/TUN fd as backend.

## Risks and Edge Cases

Descriptor parsing is security-sensitive because guest-provided vring state controls iovec translation and used-ring writes. RX must avoid overrun when one packet spans more than `UIO_MAXIOV` segments and must discard cleanly when userspace races by consuming socket data. TX must correctly rewind descriptor cursors on transient send failures, especially with `VIRTIO_F_IN_ORDER`, XDP batching, and zerocopy outstanding completions. Zerocopy state is subtle because completions can arrive out of order and are coordinated with RCU, a refcount, vq locks, and device flush. In this source snapshot, `vhost_net_ubuf_put()` visibly contains two consecutive `rcu_read_unlock()` calls after one `rcu_read_lock()`, which is a high-risk imbalance if not corrected elsewhere in the source history. Backend replacement must stop polling before dropping socket refs and must flush old work after the swap. Busy polling uses `mutex_trylock()` to avoid lock-order inversion but can miss opportunities under contention.

## Test Signals

Useful signals include building with `CONFIG_VHOST_NET`, boot tests that create `/dev/vhost-net`, QEMU virtio-net traffic over TAP/TUN, migration or dirty-log tests with `VHOST_F_LOG_ALL`, IOTLB tests with `VIRTIO_F_ACCESS_PLATFORM`, stress tests that repeatedly set/unset backends, traffic tests with mergeable RX buffers and `VIRTIO_F_IN_ORDER`, and fault injection around `sendmsg()`, `recvmsg()`, descriptor translation, and zerocopy completions. The optional zerocopy module parameter should be tested separately because it activates paths not used by default.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/scsi.c -->
# sources/distributed-fs/ceph-client/drivers/vhost/scsi.c

## Purpose

`scsi.c` implements the `/dev/vhost-scsi` device and a Linux target-core fabric named `vhost`. It lets a virtio-scsi guest submit SCSI commands through vhost virtqueues and maps those commands into target-core `struct se_cmd` operations against configured LIO target portal groups. It also handles virtio-scsi control requests, task management functions, hotplug events, T10 protection information, configfs target objects, and endpoint binding between userspace vhost instances and target-core TPGs.

## Important APIs, Types, and Functions

`struct vhost_scsi` is the per-open device containing the shared `vhost_dev`, the vq array, endpoint table `vs_tpg`, event work/list state, and old inflight refs used by flush. `struct vhost_scsi_virtqueue` wraps each `vhost_virtqueue` with command pools, tag bitmap, page pointer scratch space, completion work, and two alternating `struct vhost_scsi_inflight` refs. `struct vhost_scsi_cmd` stores one in-flight I/O command, including the original descriptor head, scatter-gather tables, response iovecs, dirty-log records, target-core `se_cmd`, sense buffer, and inflight reference. `struct vhost_scsi_tmf` is the analogous state for task management. Configfs-facing objects are `struct vhost_scsi_tport`, `struct vhost_scsi_tpg`, and `struct vhost_scsi_nexus`.

The main data-path functions are `vhost_scsi_handle_vq()`, `vhost_scsi_get_desc()`, `vhost_scsi_get_req()`, `vhost_scsi_mapal()`, `vhost_scsi_target_queue_cmd()`, and `vhost_scsi_complete_cmd_work()`. Control and event paths are `vhost_scsi_ctl_handle_vq()`, `vhost_scsi_handle_tmf()`, `vhost_scsi_tmf_resp_work()`, `vhost_scsi_send_evt()`, `vhost_scsi_do_evt_work()`, and `vhost_scsi_complete_events()`. Endpoint and lifecycle functions are `vhost_scsi_set_endpoint()`, `vhost_scsi_clear_endpoint()`, `vhost_scsi_flush()`, `vhost_scsi_open()`, `vhost_scsi_release()`, and `vhost_scsi_ioctl()`. Target-core fabric callbacks are collected in `vhost_scsi_ops`.

## Control Flow

Module init registers the miscdevice and target-core fabric template. Configfs creates vhost target ports and TPGs through `vhost_scsi_make_tport()` and `vhost_scsi_make_tpg()`, then userspace creates an I_T nexus by writing the `nexus` configfs attribute. An open of `/dev/vhost-scsi` allocates control, event, and I/O virtqueues, initializes per-I/O completion work, initializes alternating inflight refs, and delegates shared setup to `vhost_dev_init()`.

Userspace configures ownership, memory, vrings, features, and then calls `VHOST_SCSI_SET_ENDPOINT`. Endpoint setup validates all rings, allocates a target table, walks the global TPG list for matching WWPNs with active nexus sessions, pins configfs items with `target_depend_item()`, allocates command pools for configured I/O queues, sets each vq backend to the target table, initializes vq access, flushes old work, and finally publishes `vs->vs_tpg`.

For I/O queues, `vhost_scsi_handle_vq()` disables notifications and repeatedly reads descriptor chains. It copies the virtio-scsi command header, validates LUN format and target, derives data direction from request and response buffer sizes, handles optional T10 PI bytes, validates CDB length, obtains a command tag from `sbitmap`, stores response iovecs, copies log records if dirty logging is active, maps guest payload iovecs into scatterlists by pinning user pages or falling back to a copy path for problematic misaligned I/O, and submits the command to target-core. Target-core later calls fabric callbacks that free or complete the command. Completion is queued to the vhost worker so response writes and used-ring updates occur in the owner mm.

The control queue first reads a request type, then handles task management or asynchronous notification commands. Only logical-unit reset TMF is submitted to target-core; other TMFs are rejected. AN query/subscribe receives an OK response with no events. The event queue is fed by target-core LUN link/unlink hooks when the guest negotiated hotplug; events are stored on an llist and copied to guest event descriptors by vhost work, with an events-missed bit when queueing fails or descriptors are unavailable.

## State and Persistence Behavior

State is split between per-open vhost device state and configfs/target-core fabric state. Per-open state includes endpoint table, vq backends, command pools, tag bitmaps, inflight refs, event queue, and negotiated features; it is freed on release or endpoint clear. Configfs state for target ports, TPGs, nexus sessions, and fabric attributes persists until removed through target-core configfs. Inflight tracking alternates between two refs per vq: flush switches to a new ref, drops the old initial reference, flushes vhost work, and waits for commands that started before the switch to release the old ref.

## Dependencies and Integration Points

This file depends on the shared vhost core for virtqueue and worker operations, target-core for `se_cmd`, sessions, TPG registration, configfs integration, LUN link hooks, and TMF submission, virtio-scsi UAPI structures, scatterlist and page pinning APIs, Linux configfs, sbitmap tags, llist completions, and module parameters controlling `inline_sg_cnt` and `max_io_vqs`. It integrates with userspace VMMs through vhost ioctls and with storage backends through the LIO target subsystem.

## Risks and Edge Cases

The highest-risk areas are lifetime and locking between endpoint clear, configfs TPG/nexus removal, target-core command completion, and vhost worker callbacks. The documented lock order is `vs->dev.mutex -> vhost_scsi_mutex -> tpg->tv_tpg_mutex -> vq->mutex`; violating it can deadlock. Scatter-gather mapping pins guest pages and must release exactly the mapped pages on all failure paths. The fallback copy path for misaligned Windows I/O avoids block-layer limits but adds memory pressure and delayed copy-back for reads. Event accounting is protected by the event vq mutex but uses lockless lists for delivery. Dirty logging is per-command copied because completion is asynchronous. `vhost_scsi_clear_endpoint()` must prevent new commands, flush all old inflight work, destroy command pools, drop configfs dependencies, flush again, and only then free the endpoint table.

## Test Signals

Important signals include building with `CONFIG_VHOST_SCSI` and target-core enabled, configfs creation/removal of vhost WWNs and TPGs, QEMU virtio-scsi boot and I/O tests, LUN hotplug/hotunplug event tests, endpoint set/clear stress while I/O is active, TMF logical-unit-reset tests, dirty logging and migration tests, T10 PI I/O tests, page-pinning fault injection, and lockdep/KASAN/KCSAN runs around release and configfs teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/scsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/test.c -->
# sources/distributed-fs/ceph-client/drivers/vhost/test.c

## Purpose

`test.c` implements `/dev/vhost-test`, a minimal vhost backend used as a virtio simulator and core exerciser. It does not emulate a real device protocol; it accepts one virtqueue, drains guest output descriptors, immediately publishes them used with length zero, and exposes small ioctls to start/stop the test backend. The file is useful because it demonstrates the smallest backend built on top of `vhost.c`.

## Important APIs, Types, and Functions

`struct vhost_test` contains a shared `struct vhost_dev` and a single `struct vhost_virtqueue`. The supported features are `VHOST_FEATURES` through `VHOST_TEST_FEATURES`. The data path is `handle_vq()`, scheduled through `handle_vq_kick()`. Lifecycle and control are `vhost_test_open()`, `vhost_test_release()`, `vhost_test_run()`, `vhost_test_set_backend()`, `vhost_test_set_features()`, `vhost_test_reset_owner()`, and `vhost_test_ioctl()`. File operations are exposed through `vhost_test_fops` and a dynamically allocated miscdevice named `vhost-test`.

## Control Flow

Open allocates `struct vhost_test`, allocates the vq pointer array, installs the kick handler, initializes the shared vhost device with one queue, and stores it in the file. Userspace configures the common vhost owner, memory, and vring state. `VHOST_TEST_RUN` validates ownership and ring access, then sets each vq backend pointer to the device itself when enabled or to `NULL` when disabled, initializes vq access, and flushes if a backend was already present. `VHOST_TEST_SET_BACKEND` is a second enable/disable path that stores a static backend token, stops or starts polling on the queue kick file, and initializes access when re-enabled.

When a kick arrives, `handle_vq()` locks the vq, verifies the backend pointer, disables notifications, and loops over `vhost_get_vq_desc()`. It stops on parser errors, no available descriptor, unexpected input descriptors, zero-length output, or weight exhaustion. Each valid output-only descriptor chain is completed with `vhost_add_used_and_signal()` and a used length of zero. If the available ring becomes empty, notifications are re-enabled, with the standard race check that disables again and continues if the guest added a descriptor concurrently.

## State and Persistence Behavior

All state is per-open and in memory. The queue backend pointer acts as the running flag. Feature state is stored in `vq->acked_features`. The static local `backend` in `vhost_test_set_backend()` is only an opaque token used to restore a non-NULL backend pointer after disable. Release clears the backend, flushes workers, stops and cleans up the shared vhost device, and frees allocations. No data is persisted beyond the open file.

## Dependencies and Integration Points

The file depends on `test.h` for private ioctl numbers and on `vhost.c` for owner, memory, vring, worker, descriptor, notification, and reset behavior. It uses standard kernel miscdevice, compat ioctl, eventfd, and file APIs. It is a local simulator backend for testing vhost behavior rather than a production device implementation.

## Risks and Edge Cases

Because this backend discards payload contents and returns zero length, it only validates descriptor mechanics and notification behavior. It rejects any descriptor chain with input descriptors and any zero-length output chain. `VHOST_TEST_SET_BACKEND` uses a static backend token rather than a per-device object; that is acceptable for an opaque test pointer but would be unsafe as a real shared backend. As with other vhost devices, all operations after owner setup must come from the owner mm. Poll start/stop must be paired with vhost flushes to avoid using stale kick file references.

## Test Signals

Useful signals include opening `/dev/vhost-test`, configuring one vring, running `VHOST_TEST_RUN`, submitting output-only descriptors, verifying used-ring advancement and eventfd signaling, testing notification enable races, resetting owner, and running lockdep/KASAN around repeated open/release and backend toggles. Since this is itself a test backend, broader validation comes from userspace tests that drive the vhost UAPI against it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/test.h -->
# sources/distributed-fs/ceph-client/drivers/vhost/test.h

## Purpose

`test.h` is the private UAPI-style header for the vhost test backend. It defines the ioctl commands used by userspace to start/stop the virtio null-device simulation and to enable or disable the test backend for a vq.

## Important APIs, Types, and Functions

The header defines `VHOST_TEST_RUN` as `_IOW(VHOST_VIRTIO, 0x31, int)` and `VHOST_TEST_SET_BACKEND` as `_IOW(VHOST_VIRTIO, 0x32, int)`. The first passes an integer run flag to `vhost_test_run()`. The second passes a `struct vhost_vring_file` payload in practice, because `test.c` copies that structure before calling `vhost_test_set_backend()`, even though the macro's nominal type argument is `int`.

## Control Flow

The header has no executable control flow. It is included by `test.c`, and ioctl dispatch in `vhost_test_ioctl()` switches on these two command values before falling through to common vhost device and vring ioctls.

## State and Persistence Behavior

The header defines command numbers only. It stores no state and has no persistence behavior. The state changes caused by the commands are implemented in `test.c`: `VHOST_TEST_RUN` toggles the queue backend pointer for all queues, while `VHOST_TEST_SET_BACKEND` stops or starts polling for a selected queue.

## Dependencies and Integration Points

The macros depend on the common vhost ioctl namespace `VHOST_VIRTIO`, supplied by Linux vhost headers included before or alongside this file. The command values are consumed by userspace tests and the kernel-side `vhost-test` miscdevice.

## Risks and Edge Cases

The `_IOW` type annotation for `VHOST_TEST_SET_BACKEND` does not describe the actual structure copied by `test.c`; ioctl number construction on Linux generally depends on encoded size, so this mismatch can matter for tooling, tracing, or strict userspace wrappers. Any userspace caller should follow the implementation and pass `struct vhost_vring_file`, not a plain integer. The header is intentionally tiny, so most behavioral risks live in `test.c` and the shared vhost core.

## Test Signals

The basic signal is that userspace can compile against the header and successfully issue `VHOST_TEST_RUN` and `VHOST_TEST_SET_BACKEND` to `/dev/vhost-test`. Compat-ioctl and ioctl-size checks are especially useful because of the `VHOST_TEST_SET_BACKEND` type annotation mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/vdpa.c -->
# sources/distributed-fs/ceph-client/drivers/vhost/vdpa.c

## Purpose

`vdpa.c` implements the vhost character-device frontend for vDPA devices. It registers a `vdpa_driver`, creates one `/dev/vhost-vdpa-*` character device per vDPA device, translates vhost ioctls into `vdpa_config_ops`, manages virtqueue callback wiring, processes userspace IOTLB mappings for device DMA, optionally owns an IOMMU domain, and supports suspend/resume and doorbell mmap for devices that expose notification pages.

## Important APIs, Types, and Functions

`struct vhost_vdpa` is the per-device state: shared `vhost_dev`, optional `iommu_domain`, vq array, `vdpa_device`, per-ASID IOTLB hash buckets, char device, opened flag, config eventfd, batch state, IOVA range, and suspended flag. `struct vhost_vdpa_as` binds an ASID to a `struct vhost_iotlb`.

Device registration and file lifecycle are handled by `vhost_vdpa_probe()`, `vhost_vdpa_remove()`, `vhost_vdpa_open()`, `vhost_vdpa_release()`, `vhost_vdpa_cleanup()`, and `vhost_vdpa_release_dev()`. Ioctl handling is split between `vhost_vdpa_unlocked_ioctl()` and `vhost_vdpa_vring_ioctl()`. Config and feature helpers include `vhost_vdpa_get_device_id()`, `vhost_vdpa_get_status()`, `vhost_vdpa_set_status()`, `vhost_vdpa_get_config()`, `vhost_vdpa_set_config()`, `vhost_vdpa_get_features()`, `vhost_vdpa_set_features()`, `vhost_vdpa_get_backend_features()`, `vhost_vdpa_suspend()`, and `vhost_vdpa_resume()`. IOTLB mapping is handled by `vhost_vdpa_process_iotlb_msg()`, `vhost_vdpa_process_iotlb_update()`, `vhost_vdpa_pa_map()`, `vhost_vdpa_va_map()`, `vhost_vdpa_map()`, and `vhost_vdpa_unmap()`.

## Control Flow

Module init allocates a char-device major and registers the vDPA driver. Probe rejects unsupported multi-group/multi-AS platform-IOMMU cases, allocates a `vhost_vdpa`, assigns a minor, initializes the device and cdev, stores the vDPA device pointer, allocates vq state, and initializes ASID hash buckets. Open is exclusive via `atomic_cmpxchg()`: it resets the vDPA device, allocates the vhost vq pointer array, installs kick handlers, initializes the shared vhost device with no worker thread and a custom IOTLB message handler, allocates an IOMMU domain if the backend does not provide map callbacks, computes the IOVA range, and stores private data.

The main ioctl path handles backend feature negotiation outside the device mutex, then serializes most device operations under `vhost_dev.mutex`. It forwards generic vhost ioctls to the shared core and vq ioctls to `vhost_vdpa_vring_ioctl()`. Status writes enforce monotonic status bits except reset-to-zero, call vDPA reset for zero status, and set up or tear down irq-bypass producers when `DRIVER_OK` changes. Vring ioctls validate queue index, handle vDPA-specific queue enable/group/ASID/size operations, call the shared vring ioctl for common fields, and then push ring address, ring base, callback, and queue size changes into `vdpa_config_ops`.

IOTLB writes arrive through `vhost_vdpa_chr_write_iter()` and the shared vhost write parser, then enter `vhost_vdpa_process_iotlb_msg()`. UPDATE and BATCH_BEGIN allocate or find an ASID table. UPDATE validates the requested range and overlap, then maps either virtual addresses (`vdpa->use_va`) by walking shared file-backed VMAs or physical pages by pinning user pages under `RLIMIT_MEMLOCK`. Mapping records are added to vhost IOTLB first and then applied through backend `dma_map`, backend `set_map`, or the local IOMMU domain. INVALIDATE unmaps ranges, unpins pages or drops file references, and updates backend maps outside a batch. Release resets the device, stops vhost state, unbinds mm, drops config eventfd, unmaps all ASIDs, frees the domain, and marks the device reopenable.

## State and Persistence Behavior

State persists for the lifetime of the probed vDPA device and, separately, for the lifetime of an open file. Device lifetime state includes minor number, cdev/device registration, vq array allocation, vDPA pointer, and ASID hash heads. Open lifetime state includes vhost ownership, mm binding, IOTLB maps, IOMMU domain attachment, config eventfd, irq bypass registrations, backend features, and suspended flag. IOTLB mappings pin pages or hold file references until invalidated, reset, release, or device removal. There is no filesystem persistence.

## Dependencies and Integration Points

The file depends on the vDPA bus and `vdpa_config_ops`, the shared vhost core for UAPI parsing and virtqueue metadata, eventfd callbacks, irq-bypass producer registration, IOMMU APIs, mm and page pinning APIs, VMA/file mapping APIs for VA mode, char-device registration, IDA minor allocation, and optional MMU mmap operations. Userspace VMMs configure vDPA devices through `/dev/vhost-vdpa-*`.

## Risks and Edge Cases

The most sensitive logic is IOTLB mapping and unmapping: PA mode must account pinned pages in `mm->pinned_vm`, obey memlock limits, coalesce contiguous PFNs correctly, dirty writable pages on unmap, and unwind partially mapped chunks. VA mode only maps shared file-backed VMAs that are not IO/PFNMAP and must balance every `get_file()` with `fput()`. Batch mapping must not mix ASIDs and must call `set_map()` at batch end. Queue address and base changes are rejected after `DRIVER_OK` unless suspended, so migration code must use suspend where supported. IRQ bypass setup depends on both callback eventfd and backend IRQ availability. Probe intentionally rejects some multi-AS/group configurations when only a platform IOMMU path exists.

## Test Signals

Useful signals include vDPA simulator tests, QEMU boot with `/dev/vhost-vdpa-*`, backend feature negotiation tests for ASID, batching, persistent IOTLB, suspend, resume, and descriptor ASID, IOTLB map/unmap fault injection, memlock-limit tests, VA-mode shared-file mapping tests, migration tests around suspend/resume and ring-base restore, irq-bypass registration checks, mmap doorbell tests, and repeated open/release/remove races under lockdep and KASAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/vdpa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/vhost.c -->
# sources/distributed-fs/ceph-client/drivers/vhost/vhost.c

## Purpose

`vhost.c` is the shared kernel vhost core used by vhost-net, vhost-scsi, vhost-test, vhost-vdpa, and related backends. It implements owner/mm binding, worker execution, eventfd polling, virtqueue setup ioctls, descriptor translation, IOTLB miss/update handling, dirty logging, used-ring publication, notification suppression, and common character-device read/write/poll helpers for IOTLB messages.

## Important APIs, Types, and Functions

Initialization and lifecycle APIs include `vhost_dev_init()`, `vhost_dev_set_owner()`, `vhost_dev_reset_owner_prepare()`, `vhost_dev_reset_owner()`, `vhost_dev_stop()`, `vhost_dev_cleanup()`, `vhost_dev_flush()`, `vhost_dev_check_owner()`, and `vhost_dev_has_owner()`. Worker APIs include `vhost_work_init()`, `vhost_poll_init()`, `vhost_poll_start()`, `vhost_poll_stop()`, `vhost_poll_queue()`, `vhost_vq_work_queue()`, `vhost_worker_ioctl()`, and internal worker creation/attachment helpers.

Virtqueue and ioctl APIs include `vhost_dev_ioctl()`, `vhost_vring_ioctl()`, `vhost_init_device_iotlb()`, `vhost_vq_access_ok()`, `vq_meta_prefetch()`, `vhost_vq_init_access()`, `vhost_get_vq_desc_n()`, `vhost_get_vq_desc()`, `vhost_discard_vq_desc()`, `vhost_add_used()`, `vhost_add_used_n()`, `vhost_add_used_and_signal()`, `vhost_add_used_and_signal_n()`, `vhost_signal()`, `vhost_enable_notify()`, `vhost_disable_notify()`, and `vhost_vq_avail_empty()`. IOTLB and message APIs include `vhost_chr_write_iter()`, `vhost_chr_read_iter()`, `vhost_chr_poll()`, `vhost_new_msg()`, `vhost_enqueue_msg()`, `vhost_dequeue_msg()`, and `vhost_set_backend_features()`.

## Control Flow

Backends allocate their own containing device, create an array of `struct vhost_virtqueue *`, install kick handlers, and call `vhost_dev_init()`. Userspace becomes owner with `VHOST_SET_OWNER`; the core attaches the current mm, allocates per-vq iovec/log/head arrays, creates a default worker when the backend uses workers, and attaches every vq to it. Common ioctls then configure memory tables, logging, vring size/address/base, kick/call/error eventfds, busyloop timeouts, optional endian mode, and optional IOTLB mode.

Polling starts when a backend attaches a file or kick fd. `vhost_poll_start()` registers a waitqueue callback through `vfs_poll()`. On wakeup, the callback either runs work directly for no-worker devices such as vDPA or queues work to the vq's worker. Worker threads drain lockless work lists, clear queued bits, run callbacks under the owner mm for kthread workers, and integrate with KCOV. Flush enqueues a completion work item to every worker and waits for it, providing a barrier for backend teardown and endpoint changes.

Descriptor consumption starts with `vhost_get_avail_idx()`, which reads and validates the guest available index. `vhost_get_vq_desc_n()` then selects the head, walks direct or indirect descriptors, translates guest addresses through either the memory table or device IOTLB, enforces output-before-input ordering, records writable log ranges, advances `last_avail_idx` and `next_avail_head`, and returns the head. Backends can roll this back with `vhost_discard_vq_desc()` after transient backend failures. Completion writes used elements, updates the used index with ordering barriers, logs dirty used-ring writes when enabled, and signals the call eventfd only when notification rules require it.

IOTLB mode is enabled by `vhost_init_device_iotlb()`. When translation misses, the core queues `VHOST_IOTLB_MISS` messages to `read_list` and wakes userspace. Userspace reads the miss through `vhost_chr_read_iter()`, which moves miss nodes to `pending_list`, then writes UPDATE/INVALIDATE messages through `vhost_chr_write_iter()`. The default handler updates the shared IOTLB, clears metadata caches, validates userspace memory access, and requeues pending vqs whose misses are satisfied. vDPA supplies its own message handler for DMA map/unmap side effects.

## State and Persistence Behavior

The core maintains per-device state in `struct vhost_dev`: owner mm, memory table `umem`, device IOTLB, vq list, worker xarray, logging eventfd, read and pending IOTLB message lists, weight limits, backend feature flags, and the fork-owner mode. Each vq stores ring pointers, descriptor counters, feature bits, backend private data, eventfd/file references, IOTLB pointers, metadata-cache entries, logging fields, worker pointer, and scratch arrays. State is in-memory and scoped to the opened backend device. Cleanup drops eventfd and file refs, resets every vq, frees iovecs, frees IOTLBs and queued messages, destroys workers, wakes readers, and detaches the owner mm.

## Dependencies and Integration Points

`vhost.c` depends on Linux eventfd, poll, waitqueue, kthread and vhost_task workers, mm ownership, cgroups, xarray, IOTLB interval trees, virtio ring definitions, user-copy helpers, dirty page logging, module parameters, and optional cross-endian legacy support. Backend drivers call the exported symbols to implement protocol-specific devices. Userspace VMMs interact with this core through the common vhost ioctls and IOTLB read/write protocol.

## Risks and Edge Cases

This file is a high-trust boundary between guest-controlled descriptors and kernel memory access. Address translation must reject overflow, invalid permissions, descriptor loops, nested indirect descriptors, out-after-in ordering, and unavailable IOTLB mappings. Used-ring publication depends on memory barriers paired with guest notification logic. Worker reassignment uses RCU plus flushes; missing a flush can leave callbacks running on old backend state. Owner/mm lifetime differs between worker and no-worker devices. Dirty logging must mark the correct guest pages for both direct memory tables and IOTLB-translated used rings. `vhost_add_used_n_in_order()` and descriptor discard need exact descriptor counts for `VIRTIO_F_IN_ORDER`. IOTLB miss messages are retained on `pending_list` after userspace reads them, so cleanup and successful updates must free or requeue them correctly.

## Test Signals

Core signals include vhost-net, vhost-scsi, vhost-test, vhost-vsock, and vhost-vdPA integration tests; syzkaller coverage for vhost ioctls and descriptor parsing; lockdep/KCSAN for worker reassignment and teardown; KASAN/KMSAN for user-copy paths; migration dirty-log tests; IOTLB miss/update/invalidate tests; packed and split ring tests; `VIRTIO_F_IN_ORDER` tests; worker creation/free/attach ioctls; and fault injection for eventfd, memory table, and IOTLB allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vhost/vhost.c -->
