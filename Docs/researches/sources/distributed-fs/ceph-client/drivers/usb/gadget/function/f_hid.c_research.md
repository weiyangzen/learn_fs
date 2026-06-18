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
