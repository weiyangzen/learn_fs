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
