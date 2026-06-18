# Group Research: group_1766_spdk_sources_virtualization_spdk_module_bdev_raid_raid5f_c_sources__429f0ce3fa97

Scope: `Docs/research_subset_a.md`, source tree `sources/virtualization/spdk`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/raid/raid5f.c -->
# File Research: sources/virtualization/spdk/module/bdev/raid/raid5f.c

## Purpose
Implements SPDK RAID level `SPDK_BDEV_RAID_LEVEL_RAID5F`, a full-stripe RAID5 bdev module. It supports full-stripe writes, direct reads from data chunks, degraded reads reconstructed from parity, and process/rebuild requests for missing base devices.

## Main Structures
- `struct chunk`: per-base-device chunk descriptor with chunk index, data iovecs, and metadata buffer.
- `struct stripe_request`: reusable per-channel work object for full-stripe writes or reconstruction reads. Tracks RAID I/O, stripe index, parity/reconstructed chunk, XOR state, buffers, and chunk array.
- `struct raid5f_info`: module-private RAID geometry: stripe blocks, total stripes, buffer alignment, block-length shift.
- `struct raid5f_io_channel`: channel-private pools of write/reconstruct stripe requests plus SPDK accel channel and XOR retry queue.

## Control Flow
`raid5f_start()` normalizes base bdev usable sizes to full strips, computes exported RAID block count, sets optimal/write-unit boundaries, stores module-private geometry, and registers an I/O device.

Writes are accepted only as full-stripe writes aligned to stripe boundaries. `raid5f_submit_write_request()` maps the user iovecs across data chunks, allocates/parses a parity chunk buffer, computes parity using `spdk_accel_submit_xor()`, then submits writes to all chunks. If the parity base device is missing, it skips parity XOR and treats the parity write as successfully omitted.

Reads normally map to a single data chunk. If the target chunk’s base channel is missing, `raid5f_submit_reconstruct_read()` reads the other data chunks plus parity and XORs them to reconstruct the missing data into the caller’s buffer.

`raid5f_submit_process_request()` supports rebuilding a missing target chunk. It reconstructs one strip using the same XOR path, then writes the reconstructed strip to the target base bdev.

## Dependencies
Depends on `bdev_raid.h`, SPDK bdev extension submission helpers, SPDK I/O channels, DMA allocation, iovec iterators, and the SPDK accel framework XOR operation. Metadata parity is handled when non-interleaved metadata is present.

## Invariants And Risks
- This is full-stripe RAID5: writes assert stripe alignment and full stripe length.
- `RAID5F_MAX_STRIPES` limits concurrent write and reconstruct stripe requests per channel to 32 each.
- XOR `-ENOMEM` is queued on a channel-local retry queue; other XOR errors fail the parent I/O.
- Reconstruction assumes at most one base device removed, enforced by module constraints.
- Metadata handling depends on non-interleaved metadata and `blocklen_shift`; interleaved metadata disables the shift path.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/raid/raid5f.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/rbd/Makefile -->
# File Research: sources/virtualization/spdk/module/bdev/rbd/Makefile

Builds the SPDK Ceph RBD bdev module.

Key settings:
- Includes SPDK common and library make rules through `SPDK_ROOT_DIR := $(abspath $(CURDIR)/../../..)`.
- Sets shared object version `SO_VER := 9`, `SO_MINOR := 0`.
- Compiles `bdev_rbd.c` and `bdev_rbd_rpc.c`.
- Produces library `bdev_rbd`.
- Uses the blank SPDK map file.

This Makefile is purely build glue and has no runtime logic.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/rbd/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/rbd/bdev_rbd.c -->
# File Research: sources/virtualization/spdk/module/bdev/rbd/bdev_rbd.c

## Purpose
Implements the SPDK bdev module backed by Ceph RBD images via `librados` and `librbd`.

## Main State
- `struct bdev_rbd`: bdev wrapper holding RBD image, pool/user/config, cluster reference, IO context, reset state, resize watch handle, and read-only flag.
- `struct bdev_rbd_cluster`: named shared Rados cluster registration with config, key file, optional CPU mask, and refcount.
- `struct bdev_rbd_pool_ctx`: shared pool IO context keyed by cluster pointer and pool name.
- `struct bdev_rbd_io`: per-I/O context storing submit thread, status, RBD completion, and expected read length.

## Lifecycle
`bdev_rbd_create()` validates pool/image/block size, duplicates config strings, initializes a private or named shared Rados cluster, opens the image, reads image stats, registers an SPDK I/O device, and registers the bdev.

Cluster creation and image open are run via `spdk_call_unaffinitized()` to avoid Rados work running on SPDK reactor threads. Named clusters are protected by `g_map_bdev_rbd_cluster_mutex`; pool contexts are app-thread-owned and refcounted.

Destruction is asynchronous. `bdev_rbd_destruct()` sends cleanup to the app thread, unregisters the I/O device, then returns to the original destruct thread before calling `spdk_bdev_destruct_done()`.

## I/O Path
Supported operations:
- read, write, unmap/discard, flush, write zeroes
- reset
- compare-and-write when `LIBRBD_SUPPORTS_COMPARE_AND_WRITE_IOVEC` is available

Reads acquire a bdev buffer first. `bdev_rbd_start_aio()` creates a librbd completion and dispatches `rbd_aio_read/readv`, `write/writev`, `discard`, `flush`, `write_zeroes`, or compare-and-write. Completion status is translated back to SPDK bdev status and marshaled to the original submit thread if librbd completes elsewhere.

Reset is a workaround: librbd cannot cancel outstanding AIO, so reset polls current queue depth until in-flight I/O drains.

## Control Plane
Exports creation, deletion, resize, cluster register/unregister, and cluster info helpers used by the RPC file. `bdev_rbd_resize()` opens the bdev, verifies it is RBD, prevents shrinking, calls `rbd_resize()`, then notifies block-count change.

RBD image update watch calls into SPDK app thread and updates bdev block count on image size changes.

## Dependencies
Uses Ceph `librados`/`librbd`, SPDK bdev module APIs, JSON, thread messaging, pollers, cpuset handling, and bdev queue-depth queries.

## Invariants And Risks
- Shared cluster references must be returned through `bdev_rbd_put_cluster()`.
- Pool context mutations assert app-thread context.
- Reset does not abort librbd I/O; it waits for outstanding I/O to complete.
- `bdev_rbd_delete()` assumes a callback is supplied when unregister by name fails.
- Read-only RBD bdevs disable writes, write zeroes, and compare-and-write.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/rbd/bdev_rbd.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/rbd/bdev_rbd.h -->
# File Research: sources/virtualization/spdk/module/bdev/rbd/bdev_rbd.h

Public/internal header for the RBD bdev module and its RPC front-end.

Defines:
- `struct cluster_register_info`: cluster name, user, config parameters, config/key files, and optional core mask.
- Config helpers `bdev_rbd_free_config()` and `bdev_rbd_dup_config()`.
- Async delete callback type `spdk_delete_rbd_complete`.
- Public module functions for create, delete, resize, register/unregister cluster, and emit cluster info.

This header is the interface boundary between `bdev_rbd.c` and `bdev_rbd_rpc.c`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/rbd/bdev_rbd.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/rbd/bdev_rbd_rpc.c -->
# File Research: sources/virtualization/spdk/module/bdev/rbd/bdev_rbd_rpc.c

## Purpose
Registers JSON-RPC methods for managing RBD bdevs and named Rados clusters.

## RPCs
- `bdev_rbd_create`: decodes name, user, pool, image, block size, config object, cluster name, UUID, and read-only flag. Returns created bdev name.
- `bdev_rbd_delete`: unregisters the named RBD bdev asynchronously.
- `bdev_rbd_resize`: grows an RBD bdev to `new_size` MiB.
- `bdev_rbd_register_cluster`: creates a named shared Rados cluster from config/user/key/core-mask data.
- `bdev_rbd_unregister_cluster`: removes an unused registered cluster.
- `bdev_rbd_get_clusters_info`: emits one or all registered clusters.

## Notable Logic
`bdev_rbd_decode_config()` converts a JSON object into a NULL-terminated flat string array of alternating key/value entries. JSON `null` is accepted as an empty config map.

Autogenerated RPC context cleanup functions are used where available; this file has local TODO cleanup helpers for older/manual contexts.

## Dependencies And Risks
Relies on `spdk_internal/rpc_autogen.h`, SPDK JSON decoders, UUID parsing, and RBD module helpers. Invalid JSON decode mostly maps to JSON-RPC internal errors, while backend failures return backend errno strings.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/rbd/bdev_rbd_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/split/Makefile -->
# File Research: sources/virtualization/spdk/module/bdev/split/Makefile

Builds the split virtual bdev module.

Key settings:
- Includes common SPDK make rules from the module tree root.
- Sets `SO_VER := 8`, `SO_MINOR := 0`.
- Compiles `vbdev_split.c` and `vbdev_split_rpc.c`.
- Produces library `bdev_split`.
- Uses SPDK blank map file.

No runtime behavior is defined here.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/split/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/split/vbdev_split.c -->
# File Research: sources/virtualization/spdk/module/bdev/split/vbdev_split.c

## Purpose
Implements a simple virtual bdev module that slices one base bdev into multiple fixed-size `spdk_bdev_part` child bdevs.

## State
`struct spdk_vbdev_split_config` stores base bdev name, split count, optional split size in MiB, tailq of parts, and part-base pointer. `g_split_config` stores all active or pending split configs.

Per-I/O context stores the channel and bdev I/O for retry through `spdk_bdev_queue_io_wait()`.

## Lifecycle
`create_vbdev_split()` adds config and attempts immediate construction. If the base bdev does not exist, the config remains pending and `vbdev_split_examine()` creates the splits when the base appears.

`vbdev_split_create()` constructs a `spdk_bdev_part_base`, computes split size, clamps split count to the maximum possible, and registers child parts named `<base_bdev>p<index>`. `vbdev_split_destruct()` hot-removes all split parts and deletes the config.

## I/O Path
The module delegates I/O to `spdk_bdev_part_submit_request()`. Reads acquire an aligned buffer first; all other supported part operations pass through directly. `-ENOMEM` submission failures are queued for retry on the base channel.

## JSON
The module-level config writer emits `bdev_split_create` records containing base bdev, split count, and split size.

## Invariants And Risks
- Duplicate split configs for a base bdev are rejected.
- Split count must be nonzero.
- Split size must be aligned to the base bdev block size.
- If construction fails after part-base creation, the code hot-removes/free the part base to unwind.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/split/vbdev_split.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/split/vbdev_split.h -->
# File Research: sources/virtualization/spdk/module/bdev/split/vbdev_split.h

Header exposing split module control functions:
- `create_vbdev_split(base_bdev_name, split_count, split_size_mb)`.
- `vbdev_split_destruct(base_bdev_name)`.
- `vbdev_split_get_part_base(base_bdev)`.

It documents deferred creation behavior: configs can be added before the base bdev exists, and split bdevs are created during examination when the base appears.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/split/vbdev_split.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/split/vbdev_split_rpc.c -->
# File Research: sources/virtualization/spdk/module/bdev/split/vbdev_split_rpc.c

## Purpose
JSON-RPC front-end for split bdev creation and deletion.

## RPCs
- `bdev_split_create`: decodes `base_bdev`, `split_count`, optional `split_size_mb`, calls `create_vbdev_split()`, and returns an array of created split bdev names if the base is present.
- `bdev_split_delete`: decodes `base_bdev`, calls `vbdev_split_destruct()`, and returns boolean success.

## Notable Behavior
After creation, it opens the base bdev and walks the part-base tailq to return the actual split bdev names. If the base is not available yet, creation may succeed as pending config but the returned array will be empty.

## Dependencies
Uses SPDK JSON-RPC, generated RPC cleanup contexts, `spdk_bdev_open_ext()`, and split module helpers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/split/vbdev_split_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/uring/Makefile -->
# File Research: sources/virtualization/spdk/module/bdev/uring/Makefile

Builds the Linux `io_uring` bdev module.

Key settings:
- Includes SPDK common/lib makefiles.
- Sets `SO_VER := 7`, `SO_MINOR := 0`.
- Compiles `bdev_uring.c` and `bdev_uring_rpc.c`.
- Produces library `bdev_uring`.
- Uses blank SPDK map file.

No runtime logic is present.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/uring/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/uring/bdev_uring.c -->
# File Research: sources/virtualization/spdk/module/bdev/uring/bdev_uring.c

## Purpose
Implements a file/block-device-backed SPDK bdev using Linux `io_uring`.

## State
- `struct bdev_uring`: SPDK bdev, filename, fd, optional zoned metadata, and hot-remove flag.
- `struct bdev_uring_group_channel`: per-module channel with `io_uring`, pending/in-flight counts, poller, and detached flag.
- `struct bdev_uring_io_channel`: per-bdev channel referencing the group channel.
- `struct bdev_uring_task`: per-I/O context with expected length and channel pointer.

## Lifecycle
`create_uring_bdev()` opens the file/device, detects or validates block size, checks zoned support when enabled, validates size alignment, registers bdev and I/O device, and inserts it into `g_uring_bdev_head`.

Destruction unregisters the bdev, closes fd, unregisters the I/O device, and frees memory. Module init registers a shared module I/O device that creates per-thread `io_uring` queues.

## I/O Path
Read/write requests acquire aligned bdev buffers, enqueue `io_uring_prep_readv/writev` SQEs, and are submitted by `bdev_uring_group_poll()`. The same poller reaps CQEs and completes bdev I/O.

Completion checks `cqe->res` against expected byte count. `-EAGAIN`/`-EWOULDBLOCK` map to `NOMEM`; other short/error completions may trigger detach detection via `spdk_fd_get_size(fd) == 0`.

## Zoned Support
Under `SPDK_CONFIG_URING_ZNS`, the module detects host-aware/host-managed block devices from sysfs, reads zone count/size/open/active limits, implements zone management via `BLKRESETZONE`, `BLKOPENZONE`, `BLKCLOSEZONE`, `BLKFINISHZONE`, and implements zone reports via `BLKREPORTZONE`.

## Control Plane
`bdev_uring_rescan()` reopens the bdev by name, checks fd size, hot-removes zero-sized detached devices, and notifies block-count changes on resize.

## Invariants And Risks
- Queue depth is fixed at 512 and CQE reap is bounded by current in-flight count.
- `io_pending` is converted to `io_inflight` after `io_uring_submit()`.
- Device detach detection is heuristic and depends on fd size becoming zero.
- Zoned support is compile-time conditional.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/uring/bdev_uring.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/uring/bdev_uring.h -->
# File Research: sources/virtualization/spdk/module/bdev/uring/bdev_uring.h

Header for the uring bdev module.

Defines:
- Async delete callback `spdk_delete_uring_complete`.
- `struct bdev_uring_opts` with name, filename, block size, and UUID.
- `create_uring_bdev()`, `delete_uring_bdev()`, and `bdev_uring_rescan()`.

Used by RPC code and module consumers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/uring/bdev_uring.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/uring/bdev_uring_rpc.c -->
# File Research: sources/virtualization/spdk/module/bdev/uring/bdev_uring_rpc.c

## Purpose
Registers JSON-RPC methods for uring-backed bdevs.

## RPCs
- `bdev_uring_create`: decodes name, filename, optional block size and UUID, calls `create_uring_bdev()`, returns name.
- `bdev_uring_rescan`: decodes name, calls `bdev_uring_rescan()`, returns boolean success.
- `bdev_uring_delete`: decodes name and deletes asynchronously.

## Dependencies And Risks
Uses SPDK JSON decoders and autogenerated RPC context cleanup. Create failures are reported as generic internal errors, while rescan/delete return backend errno where available.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/uring/bdev_uring_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/virtio/Makefile -->
# File Research: sources/virtualization/spdk/module/bdev/virtio/Makefile

Builds the virtio bdev module.

Key settings:
- Includes SPDK common/lib makefiles.
- Sets `SO_VER := 8`, `SO_MINOR := 0`.
- Compiles `bdev_virtio_blk.c`, `bdev_virtio_scsi.c`, and `bdev_virtio_rpc.c`.
- Produces library `bdev_virtio`.
- Uses blank SPDK map file.

This file only defines build composition.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/virtio/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/virtio/bdev_virtio.h -->
# File Research: sources/virtualization/spdk/module/bdev/virtio/bdev_virtio.h

Public interface for virtio bdev creation/removal.

Defines callbacks:
- `bdev_virtio_create_cb`: async create/scan completion with created bdev array.
- `bdev_virtio_remove_cb`: async removal completion.

Exposes creation/removal for:
- vhost-user virtio-scsi
- vfio-user virtio-scsi
- PCI virtio-scsi
- vhost-user virtio-blk
- vfio-user virtio-blk
- PCI virtio-blk

Also exposes virtio-scsi device listing and virtio-blk PCI hotplug control.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/virtio/bdev_virtio.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/virtio/bdev_virtio_blk.c -->
# File Research: sources/virtualization/spdk/module/bdev/virtio/bdev_virtio_blk.c

## Purpose
Implements virtio-blk as an SPDK bdev for PCI, vhost-user, and vfio-user transports.

## State
- `struct virtio_blk_dev`: embeds `virtio_dev`, SPDK bdev, and feature flags for readonly, unmap, and flush.
- `struct virtio_blk_io_ctx`: per-I/O virtio request header, optional discard/write-zeroes descriptor, response byte, and iov wrappers.
- `struct bdev_virtio_blk_io_channel`: owns one acquired virtqueue and a poller.

## I/O Path
Read, write, unmap, and flush are converted to virtio-blk requests with an out header, optional payload descriptor, and one response descriptor. Reads acquire a bdev buffer before submission. Completion polling uses `virtio_recv_pkts()` and maps `VIRTIO_BLK_S_OK` to success.

Reset completes immediately as success. Write is rejected if the device is readonly; unmap and flush are conditional on negotiated features.

## Device Initialization
`virtio_blk_dev_init()` reads virtio config for block size, capacity, queue count, max segment size/count, and feature flags. It starts the virtio device, fills bdev geometry/capabilities, registers an I/O device, and registers the bdev.

Transport-specific constructors initialize PCI, vhost-user, or vfio-user virtio devices, negotiate supported features, and call common init.

## Hotplug
`bdev_virtio_pci_blk_set_hotplug()` enables a primary-process-only PCI event listener and poller. The monitor removes devices reported by events and enumerates new virtio-blk PCI devices.

## Dependencies And Risks
Depends on SPDK internal virtio/vhost-user APIs and Linux virtio block headers. Each I/O channel requires exclusive virtqueue acquisition. Queue-count validation prevents zero queues and clamps requested queues to host maximum.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/virtio/bdev_virtio_blk.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/virtio/bdev_virtio_rpc.c -->
# File Research: sources/virtualization/spdk/module/bdev/virtio/bdev_virtio_rpc.c

## Purpose
JSON-RPC front-end for virtio block and SCSI controllers.

## RPCs
- `bdev_virtio_blk_set_hotplug`: enables/disables PCI virtio-blk hotplug monitoring.
- `bdev_virtio_detach_controller`: tries virtio-blk removal first, then virtio-scsi removal if no blk device exists.
- `bdev_virtio_scsi_get_devices`: returns all active virtio-scsi devices.
- `bdev_virtio_attach_controller`: creates blk or scsi controllers over PCI, vhost-user, or vfio-user.

## Notable Validation
PCI and vfio-user transports reject `vq_count`/`vq_size`; vhost-user defaults to one queue and queue size 512 when not supplied. PCI transport parses `traddr` as an SPDK PCI address.

Virtio-blk creation is synchronous and the RPC manually invokes the shared completion helper. Virtio-scsi creation is asynchronous and returns through the scan callback.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/virtio/bdev_virtio_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/virtio/bdev_virtio_scsi.c -->
# File Research: sources/virtualization/spdk/module/bdev/virtio/bdev_virtio_scsi.c

## Purpose
Implements virtio-scsi bdevs for PCI, vhost-user, and vfio-user transports. One virtio-scsi controller can expose multiple SPDK bdevs, one per discovered target LUN0.

## State
- `struct virtio_scsi_dev`: virtio device, detected disk list, scan context, management poller, control queue ring, event queue buffers, removal state, callbacks.
- `struct virtio_scsi_disk`: SPDK bdev for one target, scan geometry, notification descriptor, removal state.
- `struct virtio_scsi_scan_base`: active target scan state, scan queue, retry state, command context, payload buffer, and callback.
- `struct bdev_virtio_io_channel`: one acquired request virtqueue and response poller.
- `struct virtio_scsi_io_ctx`: per-I/O command/TMF request and response wrappers.

## Device Initialization
`virtio_scsi_dev_init()` negotiates features, starts the virtio device with fixed control/event queues plus request queues, allocates the control ring, acquires control/event queues, posts event buffers, registers a management poller, registers the SPDK I/O device, and links the device globally.

## I/O Path
Reads/writes build SCSI READ/WRITE 10 or 16 depending on capacity. Reset uses a control-queue TMF logical unit reset. UNMAP builds an SCSI UNMAP parameter list in a bdev buffer and submits it if target scan found thin-provisioning support. Flush is advertised as supported in `io_type_supported()` but `_bdev_virtio_submit_request()` does not implement it and fails default submission.

Request queue completions call `spdk_bdev_io_complete_scsi_status()` with SCSI status and parsed sense key/ASC/ASCQ.

## Scan Flow
Target scan sends:
1. standard INQUIRY
2. TEST UNIT READY, or START STOP UNIT if not ready
3. VPD supported pages
4. block thin provisioning VPD for UNMAP support when available
5. READ CAPACITY 10, falling back to READ CAPACITY 16 for large devices

Full scans walk targets `0..63`. Hotplug/rescan events can enqueue specific target scans. Existing targets are not reconfigured if geometry changes.

## Event And Management Queues
The management poller sends TMF I/O from `ctrlq_ring`, receives TMF completions, and receives eventq messages. Events trigger full rescan on missed events, target rescan on transport reset/rescan, or bdev unregister on removed target.

## Removal And Fini
Device removal marks the controller removed, interrupts pending scans after the next completion, unregisters all child bdevs, and unregisters the I/O device once all LUNs are gone. Module fini is asynchronous and waits for all controllers to remove before `spdk_bdev_module_fini_done()`.

## Invariants And Risks
- Only LUN0 per target is scanned.
- Scan requests have five retries.
- `virtio_scsi_dev_scan_tgt()` sets `full_scan = true` even for a single-target scan path, causing scan-next logic to continue scanning subsequent targets.
- `bdev_virtio_io_type_supported()` advertises FLUSH, but submit does not implement FLUSH.
- Global device list is protected by `g_virtio_scsi_mutex`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/virtio/bdev_virtio_scsi.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/xnvme/Makefile -->
# File Research: sources/virtualization/spdk/module/bdev/xnvme/Makefile

Builds the xNVMe bdev module.

Key settings:
- Includes SPDK common/lib makefiles.
- Sets `SO_VER := 5`, `SO_MINOR := 0`.
- Compiles `bdev_xnvme.c` and `bdev_xnvme_rpc.c`.
- Produces library `bdev_xnvme`.
- Adds include path `-I$(SPDK_ROOT_DIR)/xnvme/include`.
- Uses blank SPDK map file.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/xnvme/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/xnvme/bdev_xnvme.c -->
# File Research: sources/virtualization/spdk/module/bdev/xnvme/bdev_xnvme.c

## Purpose
Implements an SPDK bdev backed by libxnvme.

## State
- `struct bdev_xnvme`: SPDK bdev, filename, selected async I/O mechanism, xNVMe device, namespace ID, conserve-CPU flag.
- `struct bdev_xnvme_io_channel`: one xNVMe queue plus SPDK poller.
- `struct bdev_xnvme_task`: per-I/O context linking completion back to channel.

## Lifecycle
`create_xnvme_bdev()` configures xNVMe options, opens the device, gets namespace geometry, validates block size and total size, fills bdev geometry, configures unmap/write-zeroes limits for NVM command set, registers I/O device and bdev, then links it globally for config JSON.

`delete_xnvme_bdev()` unregisters by name. Destruct unregisters the I/O device, removes the bdev from the global list, closes the xNVMe device, and frees strings/state.

## I/O Path
Supports read and write for all mechanisms. Supports write zeroes and unmap only when `io_mechanism == "io_uring_cmd"` and the device command-set identifier is NVM.

Read/write/unmap acquire aligned bdev buffers; write zeroes submits directly. `_xnvme_submit_request()` fills NVMe command fields and calls `xnvme_cmd_passv()`. Queue-full/resource errors map to SPDK `NOMEM`; other submission errors fail the I/O.

Completions are polled with `xnvme_queue_poke()`. `bdev_xnvme_cmd_cb()` checks xNVMe completion status, completes the SPDK bdev I/O, and returns the command context to the queue.

## Dependencies And Risks
Depends on libxnvme command and queue APIs plus SPDK bdev/thread/poller support. Queue depth is fixed at 512. `bdev_xnvme_get_buf_cb()` contains an unusual failure path that obtains and immediately returns a command context even though no submission occurred.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/xnvme/bdev_xnvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/xnvme/bdev_xnvme.h -->
# File Research: sources/virtualization/spdk/module/bdev/xnvme/bdev_xnvme.h

Header for xNVMe bdev control.

Declares:
- `create_xnvme_bdev(name, filename, io_mechanism, conserve_cpu)`.
- `delete_xnvme_bdev(name, cb_fn, cb_arg)`.

Used by the xNVMe RPC implementation.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/xnvme/bdev_xnvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/xnvme/bdev_xnvme_rpc.c -->
# File Research: sources/virtualization/spdk/module/bdev/xnvme/bdev_xnvme_rpc.c

## Purpose
Registers JSON-RPC methods for xNVMe-backed bdevs.

## RPCs
- `bdev_xnvme_create`: decodes name, filename, I/O mechanism, optional conserve-CPU flag, calls `create_xnvme_bdev()`, returns name.
- `bdev_xnvme_delete`: decodes name and unregisters asynchronously.

Create failures are returned as generic internal errors. Delete callback returns boolean success or backend errno.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/xnvme/bdev_xnvme_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/zone_block/Makefile -->
# File Research: sources/virtualization/spdk/module/bdev/zone_block/Makefile

Builds the zone block virtual bdev module.

Key settings:
- Includes SPDK common/lib makefiles.
- Sets `SO_VER := 8`, `SO_MINOR := 0`.
- Compiles `vbdev_zone_block.c` and `vbdev_zone_block_rpc.c`.
- Produces library `bdev_zone_block`.
- Uses blank SPDK map file.

Only build composition is covered by this file; runtime zone-block behavior is in source files outside this work item.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/zone_block/Makefile -->