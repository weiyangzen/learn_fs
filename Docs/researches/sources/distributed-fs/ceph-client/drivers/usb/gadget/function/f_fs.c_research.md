# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_fs.c

## Purpose

`f_fs.c` implements the FunctionFS USB composite function. It exposes a `functionfs` pseudo filesystem where userspace first writes USB descriptors and string tables to `ep0`, then uses generated endpoint files (`ep1`, `ep2`, or virtual-address names like `ep81`) for bulk/interrupt/isochronous I/O. The same source also implements the configfs USB function instance named `ffs`, the global FunctionFS device registry used by legacy and configfs gadgets, control request forwarding to userspace, event delivery, endpoint autoconfiguration, asynchronous I/O completion, and optional DMA-BUF based zero-copy transfers.

This is not a Ceph/distributed-filesystem client path despite the repository prefix. It is Linux USB gadget code vendored under `sources/distributed-fs/ceph-client`.

## Important APIs, Types, And Functions

Core data structures:

- `struct ffs_function` wraps `struct usb_function` and binds one ready `struct ffs_data` instance into a USB configuration. It tracks endpoint state (`eps`), reverse maps for physical endpoint/interface numbers, and current alternate settings.
- `struct ffs_ep` represents one parsed FunctionFS endpoint, including the selected `struct usb_ep`, one reusable synchronous `usb_request`, and full/high/super speed endpoint descriptor pointers.
- `struct ffs_epfile` backs each generated endpoint file. It holds the current enabled endpoint pointer, direction/type flags, a synchronous partial-read buffer, DMA-BUF attachment state, and a per-endpoint sequence counter for DMA fences.
- `struct ffs_io_data` carries synchronous or asynchronous endpoint transfer state, including user iterators, optional SG table, request, completion, work item, and the owning `ffs_data`.
- `struct ffs_dmabuf_priv` and `struct ffs_dma_fence` connect attached DMA-BUFs to USB requests and expose completion through DMA fences.

Major control-file APIs:

- `ffs_ep0_write()` handles the descriptor/string upload phase and later services IN control requests from userspace.
- `ffs_ep0_read()` reads FunctionFS events or services OUT control request payloads.
- `__ffs_ep0_queue_wait()` queues ep0 data/status stages and waits for completion.
- `__ffs_event_add()` coalesces and queues `FUNCTIONFS_*` events while cancelling stale pending setup state.

Endpoint file APIs:

- `ffs_epfile_io()` is the central read/write engine. It waits for endpoint enablement, validates direction versus halt operation, allocates linear or SG-backed buffers, queues USB requests, and handles synchronous or AIO completion.
- `ffs_epfile_read_iter()` and `ffs_epfile_write_iter()` set up `ffs_io_data` for VFS `read_iter`/`write_iter`.
- `ffs_aio_cancel()` dequeues a queued USB request for async cancellation.
- `ffs_epfile_ioctl()` implements FIFO status/flush, clear halt, endpoint reverse mapping, endpoint descriptor copyout, and DMA-BUF attach/detach/transfer ioctls.

Descriptor and binding APIs:

- `__ffs_data_got_descs()` parses the FunctionFS descriptor blob, validates flags, counts descriptors by speed, validates OS descriptors, records endpoint/interface/string counts, and stores raw descriptor memory.
- `__ffs_data_got_strings()` parses language/string tables and builds `usb_gadget_strings`.
- `ffs_do_descs()`, `ffs_do_single_desc()`, and `__ffs_data_do_entity()` validate descriptor shape and collect entity counts.
- `ffs_func_bind()` and `_ffs_func_bind()` bind parsed userspace descriptors into a composite function, allocate endpoint/interface maps, autoconfigure endpoints, rewrite descriptor numbers, and build OS descriptor tables.
- `ffs_func_set_alt()`, `ffs_func_disable()`, `ffs_func_setup()`, `ffs_func_req_match()`, `ffs_func_suspend()`, and `ffs_func_resume()` are the USB composite callbacks.

Filesystem/configfs/device APIs:

- `ffs_fs_type` registers the `functionfs` filesystem. `ffs_fs_get_tree()` allocates `ffs_data`, acquires a named `ffs_dev`, and builds a superblock with `ep0`.
- `ffs_alloc_inst()`, `ffs_set_inst_name()`, `ffs_free_inst()`, and `ffs_alloc()` implement the configfs function instance.
- `ffs_name_dev()`, `ffs_single_dev()`, `ffs_acquire_dev()`, `ffs_release_dev()`, `ffs_ready()`, and `ffs_closed()` maintain the global `ffs_devices` registry and bridge mount readiness to gadget binding.

## Control Flow

Mount setup starts in `ffs_fs_get_tree()`. The source name becomes `ffs->dev_name`; the code creates a fresh `ffs_data`, acquires a matching `ffs_dev`, then `ffs_sb_fill()` builds a root directory containing only `ep0`. The first opener writes a descriptor blob to `ep0`. `ffs_ep0_write()` requires at least 16 bytes, copies the user buffer with `ffs_prepare_buffer()`, and calls `__ffs_data_got_descs()`. If descriptor parsing succeeds, the state advances from `FFS_READ_DESCRIPTORS` to `FFS_READ_STRINGS`. The next write parses strings, creates endpoint files with `ffs_epfiles_create()`, moves to `FFS_ACTIVE`, and calls `ffs_ready()` so configfs or legacy gadget code can bind the function.

USB binding flows through `ffs_func_bind()`. `ffs_do_functionfs_bind()` verifies that the target `ffs_dev` has ready descriptors, calls `functionfs_bind()` once per FunctionFS instance to allocate ep0 request/string IDs and store the gadget pointer, and sets the function string table. `_ffs_func_bind()` then allocates one combined memory block for endpoint records, descriptor pointer arrays, interface numbers, optional OS descriptor tables, and copied raw descriptors. It parses descriptors in speed order with `__ffs_func_bind_do_descs()` to autoconfigure endpoints, then makes a second pass with `__ffs_func_bind_do_nums()` to rewrite interface, endpoint, and string references to composite-assigned values. On success it emits `FUNCTIONFS_BIND`.

Alternate setting enablement runs through `ffs_func_set_alt()`: resolve the composite interface number back to the FunctionFS interface, disable any previously enabled function endpoints, handle `FFS_DEACTIVATED` by scheduling reset work, check that userspace is still active, set `ffs->func`, enable all endpoints through `ffs_func_eps_enable()`, wake blocked endpoint-file users, and emit `FUNCTIONFS_ENABLE`. Disable/unbind reverse this flow by disabling endpoints, clearing epfile endpoint pointers, freeing read buffers, draining async completions, sending `FUNCTIONFS_DISABLE`/`UNBIND`, and unbinding the underlying `ffs_data` when the last function reference is gone.

Control requests enter `ffs_func_setup()`. Interface and endpoint recipients are reverse-mapped before being exposed to userspace; other recipients are accepted only with `FUNCTIONFS_ALL_CTRL_RECIP`. The request is stored in `ffs->ev.setup`, a `FUNCTIONFS_SETUP` event is queued, and userspace completes the data stage by reading or writing `ep0`. `ffs_setup_state_clear_cancelled()` coordinates races where a new event cancels an old pending setup.

Normal endpoint I/O enters through `read_iter`/`write_iter`, builds `ffs_io_data`, then calls `ffs_epfile_io()`. Reads on OUT endpoints are aligned with `usb_ep_align_maybe()` for UDCs that require maxpacket-sized requests. Large buffers may use scatter-gather if the gadget supports it. Synchronous I/O reuses `ep->req` and waits on a completion. AIO allocates a fresh request and completes in `ffs_epfile_async_io_complete()`, which queues `ffs_user_copy_worker()` to copy read data back in the submitter's mm and call `ki_complete()`. Endpoint I/O also supports endpoint halt by issuing a read/write in the wrong direction on non-isoc endpoints.

DMA-BUF flow starts with `FUNCTIONFS_DMABUF_ATTACH`, which attaches and maps a DMA-BUF to the gadget parent device and stores importer-private state. `FUNCTIONFS_DMABUF_TRANSFER` validates length, waits on the reservation object for conflicting writers/readers, reserves a fence, allocates a USB request that points directly to the mapped SG list, adds a DMA fence to the reservation object, queues the request, and signals the fence from completion. Detach and file release cancel pending requests and drop attachment refs.

## State And Persistence Behavior

All runtime state is memory-backed; the filesystem is nodev and has no persistent storage. `ffs_data` moves through `FFS_READ_DESCRIPTORS`, `FFS_READ_STRINGS`, `FFS_ACTIVE`, `FFS_DEACTIVATED`, and `FFS_CLOSING`. `ffs->opened` counts open ep0/endpoint files. If the last file closes with `no_disconnect` set, endpoint files are removed and state becomes `FFS_DEACTIVATED`; otherwise the object resets to a fresh descriptor-read state. `ffs_data_reset()` clears descriptors, strings, event count, flags, interface/endpoint counts, and Microsoft OS descriptor counters.

Synchronization is split across `ffs->mutex` for ep0 state, `ffs->eps_lock` for endpoint pointers and active function state, per-epfile mutexes for request/read-buffer state, `ev.waitq.lock` for event/setup queues, and per-DMA-BUF locks/fences. Refcounts guard `ffs_data` lifetime, `ffs_dmabuf_priv` lifetime, and configfs function instances.

## Dependencies And Integration Points

The file depends on USB composite APIs (`usb_function`, `usb_configuration`, descriptor assignment, endpoint autoconfig, ep0 queueing), the VFS/fs_context/simplefs helpers, configfs function registration, eventfd, kthread mm adoption for async copy-back, scatterlist/vmalloc page mapping, DMA-BUF reservation/fence APIs, Microsoft OS descriptor helpers, and local headers `u_fs.h`, `u_os_desc.h`, and `configfs.h`.

Externally visible integration points include the mounted `functionfs` filesystem, the configfs `ffs` function with a read-only `ready` attribute, exported `ffs_lock`, `ffs_name_dev()`, and `ffs_single_dev()`, FunctionFS UAPI ioctls/events, and callbacks stored in `struct ffs_dev` for legacy gadget coordination.

## Risks And Edge Cases

The highest-risk areas are concurrency and userspace-supplied descriptor validation. Descriptor blobs define the interface/endpoint topology and are used later after descriptor rewriting, so malformed length/count/endpoint-order combinations must keep failing cleanly. Endpoint disable races are subtle: epfile endpoint pointers, read-buffer sentinel `READ_BUFFER_DROP`, queued requests, and AIO workers all interact with disconnect/unbind. DMA-BUF transfer has additional ordering risks around reservation locks, fence signalling, request lifetime, and `priv->ep/req` cleanup. Control request state also has races: event coalescing intentionally cancels pending setup requests, so user-visible `-EIDRM`, `-ESRCH`, and stalls are expected in some interleavings.

Other risks include unbounded userspace behavior around blocking reads/writes, AIO read data loss when user buffers are not maxpacket-aligned, `no_disconnect` reactivation paths that defer reset work, assumptions that configfs binding order avoids races on `ffs_opts->refcnt`, and the shared global `ffs_devices` list guarded by `ffs_lock`/`ffs_dev_lock()`.

## Test Signals

Useful tests should mount FunctionFS, write valid and invalid v1/v2 descriptor blobs, verify endpoint file creation and state transitions, bind through configfs, and run host-driven enumeration at full/high/super speed. Exercise ep0 event delivery for bind/enable/setup/suspend/resume/disable/unbind, including cancelled setup requests and `FUNCTIONFS_CONFIG0_SETUP`/`FUNCTIONFS_ALL_CTRL_RECIP` flags. Endpoint tests should cover sync read/write, AIO cancellation, short and unaligned OUT reads, endpoint halt/clear-halt ioctls, descriptor/revmap ioctls, disconnect during blocked I/O, and last-close behavior with and without `no_disconnect`. DMA-BUF tests need attach/detach failures, transfer length validation, nonblocking reservation lock failures, fence signalling on success and queue failure, and release while transfer is pending.
