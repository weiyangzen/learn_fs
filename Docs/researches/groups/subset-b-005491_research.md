# subset-b-005491 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_fs.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_hid.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_hid.c

## Purpose

`f_hid.c` implements the USB HID gadget function for the Linux composite framework. It lets configfs users define HID subclass, protocol, report length, report descriptor, polling interval, and whether HID output reports arrive through an interrupt OUT endpoint or through control `SET_REPORT`. Each function instance creates a `/dev/hidgN` character device that userspace reads and writes as HID reports while the USB host sees a HID interface.

## Important APIs, Types, And Functions

Important data structures:

- `struct f_hidg` is the per-bound function state. It stores descriptor parameters, endpoint pointers, char-device objects, report queues, write request state, GET_REPORT state, wait queues, spinlocks, a workqueue, and the embedded `usb_function`.
- `struct f_hidg_req_list` wraps completed interrupt OUT requests so userspace can drain partial reads from `/dev/hidgN`.
- `struct report_entry` stores cached `struct usb_hidg_report` values used to satisfy host `GET_REPORT` requests immediately or after userspace response.
- `struct f_hid_opts` is defined in `u_hid.h` and holds configfs instance options plus the minor number and refcount.

USB callbacks and file operations:

- `hidg_bind()` allocates the ep0 GET_REPORT request, attaches strings, assigns an interface ID, autoconfigures interrupt IN and optional OUT endpoints, patches HID/endpoint descriptors, allocates a workqueue, and registers the char device.
- `hidg_set_alt()` enables/restarts endpoints, allocates the single IN request, and queues `qlen` OUT requests when interrupt OUT mode is enabled.
- `hidg_disable()` disables endpoints, frees completed OUT requests, resolves pending GET_REPORT state, marks reads disabled, and tears down the write request.
- `hidg_setup()` handles HID class and descriptor control requests.
- `f_hidg_read()`, `f_hidg_write()`, `f_hidg_poll()`, and `f_hidg_ioctl()` implement the `/dev/hidgN` ABI.

Configfs and module setup:

- `F_HID_OPT()` generates show/store handlers for `subclass`, `protocol`, `no_out_endpoint`, and `report_length`.
- Dedicated handlers manage binary `report_desc`, `interval`, and read-only `dev`.
- `hidg_alloc_inst()` allocates options, initializes the global char-device class/major on first use through `ghid_setup()`, and assigns an IDA minor.
- `hidg_alloc()` copies immutable options into a new `f_hidg`, initializes locks/queues/device naming, and installs `usb_function` callbacks.
- `hidg_free_inst()`, `hidg_free()`, `hidg_unbind()`, and `ghid_cleanup()` release minors, descriptors, workqueues, char devices, and class/major registration.

## Control Flow

Configfs creates a function instance through `hidg_alloc_inst()`. The first instance registers class `hidg` and reserves up to `HIDG_MINORS` character-device minors. Attribute writes are permitted only while `opts->refcnt == 0`, which means options become immutable after the function is allocated and linked into a configuration. `hidg_alloc()` copies those options into a `f_hidg`, duplicates the report descriptor, initializes wait queues and spinlocks, and creates a device name like `hidg0`.

Binding in `hidg_bind()` prepares the USB-visible descriptors. It allocates a dedicated ep0 request for asynchronous GET_REPORT replies, attaches the `"HID Interface"` string, obtains a composite interface number, autoconfigures the interrupt IN endpoint, and conditionally autoconfigures interrupt OUT. Descriptor fields are patched from options: subclass/protocol, endpoint count, report descriptor length, max packet/report length, and bInterval. If `interval` was not user-set, the code uses 10 ms for full-speed and 4 microframes/interval units for high/super-speed. The selected descriptor arrays differ between interrupt-OUT mode and setup-SET_REPORT mode.

When the host selects the interface, `hidg_set_alt()` disables/re-enables endpoints by speed, creates the IN report request, and, for interrupt OUT mode, allocates and queues four OUT requests. It marks the function enabled by clearing `disabled`, stores the IN request under `write_spinlock`, clears `write_pending`, and wakes writers.

Userspace writes input reports to the host with `f_hidg_write()`. Only one IN request is outstanding at a time. Blocking writers wait on `write_queue` until `write_pending` clears; nonblocking writers get `-EAGAIN`. The write is clipped to `report_length`, copied into the IN request buffer, and queued to `in_ep`; `f_hidg_req_complete()` clears `write_pending` and wakes writers. Shutdown paths set `hidg->req = NULL`, causing `-ESHUTDOWN`.

Userspace reads output reports through one of two paths. In interrupt OUT mode, `hidg_intout_complete()` wraps completed requests in `f_hidg_req_list` and appends them to `completed_out_req`. `f_hidg_intout_read()` waits for that list, copies from the current offset, and either requeues the request when fully consumed or puts the list node back for later partial reads. In SET_REPORT mode, `hidg_setup()` assigns `hidg_ssreport_complete()` as the ep0 completion; the completion copies the control payload into `set_report_buf`, and `f_hidg_ssreport_read()` hands it once to userspace.

Host `GET_REPORT` is handled asynchronously. `hidg_setup()` records the requested report ID and length, queues `get_report_workqueue_handler()`, and returns without immediately queueing ep0. The worker first checks `report_list` for a cached report that is not marked `userspace_req`; otherwise it wakes `get_id_queue`, waits up to 2500 ms for userspace to respond with `GADGET_HID_WRITE_GET_REPORT`, then replies with the matching report, the latest cached report, or an empty report. `GADGET_HID_READ_GET_REPORT_ID` lets userspace discover which ID is pending.

## State And Persistence Behavior

The function is memory-only. Configfs options persist only as configfs items; runtime report queues disappear on unbind/free. `opts->refcnt` prevents option mutation while functions exist. `hidg_ida` allocates up to four minors and triggers class/major cleanup when the last minor is released.

Concurrency is managed with three spinlocks: `read_spinlock` for completed OUT or SET_REPORT buffers and `disabled`, `write_spinlock` for the single IN request and `write_pending`, and `get_report_spinlock` for report-cache and GET_REPORT coordination. Wait queues expose state changes to blocking read/write/poll. `hidg_release()` frees `report_desc`, `set_report_buf`, and the `f_hidg` object when the embedded device refcount drops.

## Dependencies And Integration Points

The file integrates with the USB composite framework, HID class constants/descriptors, configfs, Linux cdev/device/class APIs, IDA minor allocation, wait queues/poll, userspace copy helpers, and workqueues. It includes `u_hid.h` for configfs option storage and `uapi/linux/usb/g_hid.h` for ioctl/report structures. Userspace interacts through `/dev/hidgN`, configfs attributes, and HID-specific ioctls.

## Risks And Edge Cases

The main risks are races among host disconnect, endpoint disable, blocking file operations, and pending GET_REPORT work. `hidg_disable()` frees queued OUT requests and the IN request under locks, but writers can be in the retry path after copying from userspace. SET_REPORT mode stores only one `set_report_buf`; a later host report can replace earlier unread data via `krealloc()`. GET_REPORT uses cached report entries without an explicit cleanup loop in the visible free path, so report-list lifetime should be reviewed with UAPI expectations. `f_hidg_poll()` reports `EPOLLPRI` while `GET_REPORT_COND` is true, which corresponds to userspace needing to service a pending GET_REPORT. Descriptor fields are global static objects patched at bind time, so multi-instance behavior relies on composite binding serialization and copied descriptors.

Input validation is mostly range-based. `report_length` may be as large as 65535 and `report_desc` may be up to `PAGE_SIZE`; tests should include memory-pressure and large report scenarios. `no_out_endpoint` changes host-visible topology and read semantics, so userspace must be aligned with the selected receive mode.

## Test Signals

Test configfs creation with valid and invalid values for subclass, protocol, report length, interval, and binary report descriptor. Bind both default interrupt-OUT mode and `no_out_endpoint=1` SET_REPORT mode and inspect descriptors at full/high/super speed. Exercise `/dev/hidgN` blocking and nonblocking reads/writes, partial OUT reads, poll readiness, host disconnect during blocked I/O, and repeated set-alt restarts. HID control tests should cover GET_DESCRIPTOR for HID/report descriptors, GET/SET_PROTOCOL, GET/SET_IDLE, SET_REPORT in both modes, GET_REPORT immediate cached replies, userspace-delayed replies, timeout empty replies, and ioctl error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_hid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_loopback.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_loopback.c

## Purpose

`f_loopback.c` implements the USB gadget loopback function used by Gadget Zero style testing. It exposes one vendor-specific interface with a bulk OUT endpoint and a bulk IN endpoint. Data received from the host on OUT is queued back to the host on IN using the same buffer, making it a compact test vehicle for endpoint autoconfiguration, request queueing, transfer completion, and configfs option plumbing.

## Important APIs, Types, And Functions

The central runtime type is `struct f_loopback`, which embeds `struct usb_function` and stores the selected IN/OUT endpoints plus `qlen` and `buflen` copied from `struct f_lb_opts` in `g_zero.h`.

Descriptor objects include one interface descriptor, full-speed bulk source/sink endpoint descriptors, high-speed descriptors with 512-byte max packet size, super-speed descriptors with 1024-byte max packet size plus companion descriptors, and a single English interface string.

Major functions:

- `loopback_bind()` allocates interface/string IDs, autoconfigures endpoints from the full-speed descriptors, copies endpoint addresses into high/super-speed descriptors, assigns descriptor arrays with `usb_assign_descriptors()`, and logs selected endpoints.
- `loopback_alloc()` creates a function instance, increments the configfs option refcount, copies `bulk_buflen` and `qlen`, installs callbacks, and defaults zero `qlen` to 32.
- `enable_loopback()` enables both endpoints by speed and prequeues transfer pairs.
- `alloc_requests()` allocates `qlen` pairs of requests. Each OUT request owns the data buffer; the paired IN request points at the same buffer. The two requests reference each other through `context`.
- `loopback_complete()` is the ping-pong completion handler that turns an OUT completion into an IN queue and an IN completion back into a fresh OUT queue.
- `loopback_set_alt()` restarts the function for altsetting zero by disabling and enabling endpoints.
- `loopback_disable()` and `disable_loopback()` stop both endpoints.
- Configfs handlers expose writable `qlen` and `bulk_buflen` while no function references exist.

## Control Flow

Configfs instance creation starts with `loopback_alloc_instance()`, which allocates `f_lb_opts`, initializes its mutex and defaults from `GZERO_BULK_BUFLEN` and `GZERO_QLEN`, and registers the configfs attributes. Attribute stores parse unsigned integers and return `-EBUSY` if a function has already been allocated from the instance.

When the function is allocated, `loopback_alloc()` creates `struct f_loopback`, increments `opts->refcnt`, copies option values, sets the function name to `"loopback"`, and installs bind/set_alt/disable/free callbacks. `lb_free_func()` decrements the option refcount, frees descriptors, and releases the function object.

Binding assigns one interface number and one string ID, then autoconfigures a bulk IN endpoint and a bulk OUT endpoint. The full-speed endpoint descriptors are the templates used for autoconfig; assigned addresses are propagated to high-speed and super-speed descriptors. Descriptor arrays are then assigned for full, high, super, and super-plus speeds.

Enablement configures endpoint descriptors for the current gadget speed, enables both endpoints, stores `loop` as `ep->driver_data`, and calls `alloc_requests()`. Each queue slot consists of one IN request and one OUT request. The OUT request is allocated with a data buffer of `buflen`; the IN request reuses that buffer and has its length set later from `out_req->actual`. Initial traffic waits on all OUT requests.

On OUT completion, `loopback_complete()` retrieves the paired IN request, sets `in_req->zero` when the host sent a short packet, sets `in_req->length` to the received byte count, and queues it on the IN endpoint. On IN completion, it retrieves the paired OUT request and requeues it to receive more data. On queue failure or terminal request statuses (`-ECONNABORTED`, `-ECONNRESET`, `-ESHUTDOWN`) it frees both paired requests through the opposite endpoint and the current endpoint helper.

## State And Persistence Behavior

Runtime state is limited to endpoint pointers, copied queue depth, copied buffer length, and queued USB requests. No data persists beyond the life of a transfer; buffers are recycled between OUT and IN until endpoint disable or error. Configfs option state persists in memory while the function instance exists. `f_lb_opts->refcnt` prevents changing `qlen` or `bulk_buflen` after a function has been allocated.

There is intentionally no explicit list of submitted requests. The code relies on the UDC/composite endpoint disable path to complete or purge queued requests; the completion handler frees request pairs on error statuses. This small state model is simple but makes correctness depend on UDC request completion semantics during disconnect and disable.

## Dependencies And Integration Points

The file depends on the USB composite framework, endpoint autoconfiguration, `config_ep_by_speed()`, `usb_ep_enable()`, `usb_ep_queue()`, descriptor assignment/free helpers, configfs attribute macros, and shared Gadget Zero helpers/types from `g_zero.h` and `linux/usb/func_utils.h`. It registers a USB function named `Loopback` with `DECLARE_USB_FUNCTION()` and also exposes `lb_modinit()`/`lb_modexit()` for Gadget Zero module initialization.

## Risks And Edge Cases

The important risks are around request-pair lifetime and option bounds. `qlen` and `bulk_buflen` accept any `u32`; very large values can create memory pressure because enablement allocates `qlen` buffers of `buflen` bytes. `qlen == 0` is normalized to 32 only at function allocation; later stores before allocation can set zero and still get the default. The completion handler assumes `req->context` always points at its paired request and frees both sides on errors, so any future change to allocation or queuing must preserve that invariant. High-speed descriptor order differs from full-speed order (`source` before `sink` in the array), but endpoint addresses are explicitly assigned and should be verified against enumeration behavior.

## Test Signals

Tests should bind the loopback function at full/high/super speed and verify descriptor endpoint addresses, packet sizes, and interface string. Functional tests should send host OUT transfers of zero length, short packets, exact maxpacket multiples, and larger buffers, then verify the same bytes return through IN. Stress tests should vary `qlen` and `bulk_buflen`, disconnect while requests are queued, force endpoint queue failures if possible with a dummy UDC, and confirm configfs stores return `-EBUSY` after allocation and parse errors for invalid input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_loopback.c -->
