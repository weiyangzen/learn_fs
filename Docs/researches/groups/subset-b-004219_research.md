# subset-b-004219 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-hdw-internal.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-hdw-internal.h

Purpose: private hardware-core header for the pvrusb2 USB video driver. It defines the internal `struct pvr2_hdw`, internal control metadata, lock helpers, firmware/pathway state constants, control callback types, and low-level prototypes that implementation files use but public V4L/sysfs-facing layers should not include.

Important APIs, types, and functions: `struct pvr2_ctl_info` describes each control's name, type, V4L/internal IDs, defaults, validation, dirty tracking, symbol conversion, and V4L flag callback. `struct pvr2_ctld_info` adds mutable description storage for dynamically generated MPEG controls. `struct pvr2_ctrl` binds a control descriptor to a `struct pvr2_hdw`. `struct pvr2_hdw` is the central state object: USB handles, V4L2 device, device descriptor, work item, video stream, `big_lock`/`ctl_lock`, I2C adapter and per-address function table, IR configuration, control URBs/buffers, pipeline state bits, timers, firmware buffers, tuner/frequency state, crop and standard caches, V4L minor numbers, input masks, stream type, cx2341x MPEG state, scalar control fields, dynamic MPEG control descriptors, and the control array.

Control flow: the header has no executable flow, but its fields drive the hardware worker in `pvrusb2-hdw.c`. State transitions are scheduled through `workpoll`; timers set readiness flags; control commits inspect dirty bits; low-level USB requests use the control URB fields; I2C initialization fills `i2c_func[]`; and public APIs use the opaque `struct pvr2_hdw` handle declared in `pvrusb2-hdw.h`.

State and persistence: all state is in memory and per device. The only long-lived effects are hardware-side register, firmware, GPIO, I2C subdevice, and streaming state created by implementation code. `fw_buffer` can temporarily hold fetched CPU firmware or EEPROM bytes for debug access. No disk persistence is performed.

Dependencies and integration points: depends on Linux USB/V4L2/I2C/workqueue/mutex APIs, cx2341x MPEG control state, IR I2C init data, `pvrusb2-devattr.h` device descriptors, `pvrusb2-io.h` stream handles, and the public hardware/control headers. Integration risk is high because this header is the shared private ABI among hardware, encoder, I2C, and debug code.

Risks: lock state is tracked manually through `LOCK_TAKE`/`LOCK_GIVE`, so new callers must respect `big_lock` versus `ctl_lock` ownership. `struct pvr2_hdw` is broad and cross-cutting, making stale flags or partially initialized fields easy to misuse. Debug fields can be read unlocked and may be inconsistent by design. Any changes to control layout or state flags affect sysfs, V4L2, streaming, and firmware flows.

Test signals: build coverage with sysfs/debug/I2C/V4L enabled; probe and unplug devices while streaming; inspect state reports for coherent flag transitions; exercise all controls through V4L2 and sysfs; run with lockdep to catch lock inversion between hardware, I2C, and USB control paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-hdw-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-hdw.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-hdw.c

Purpose: main hardware implementation for pvrusb2 devices. It creates and initializes the hardware object, loads FX2 and cx23416 firmware, registers V4L2 subdevices over a custom I2C adapter, owns the control table, commits control changes, manages analog/digital pathway switching, controls USB streaming, and evaluates the driver master state.

Important APIs, types, and functions: module parameters include `ctlchg`, `procreload`, per-unit `tuner`, `video_std`, `tolerance`, `tv_freq`, `radio_freq`, and `init_pause_msec`. The large `control_defs[]` table defines scalar, enum, bitmask, standard, signal, input, frequency, crop, and MPEG controls. Public entry points include `pvr2_hdw_create()`, `pvr2_hdw_initialize()`, `pvr2_hdw_destroy()`, `pvr2_hdw_disconnect()`, `pvr2_hdw_commit_ctl()`, `pvr2_hdw_set_streaming()`, `pvr2_hdw_set_stream_type()`, `pvr2_hdw_get_*()` accessors, CPU firmware read helpers, GPIO helpers, and `pvr2_upload_firmware2()`. Internal core functions include `pvr2_hdw_setup_low()`, `pvr2_hdw_commit_setup()`, `pvr2_hdw_commit_execute()`, `pvr2_hdw_state_eval()`, `pvr2_send_request_ex()`, `pvr2_issue_simple_cmd()`, and the state evaluation helpers.

Control flow: `pvr2_hdw_create()` allocates state, builds static and dynamic cx2341x controls, initializes timers, allocates control URBs/buffers, registers a `v4l2_device`, reserves a unit number, and stores USB identity. `pvr2_hdw_initialize()` installs a state callback and runs setup under `big_lock`. Setup probes or uploads FX2 firmware, powers up hardware, initializes I2C, loads configured subdevices, sets default controls and frequencies, analyzes EEPROM, derives video standards, commits initial control state, creates the video stream, and schedules state evaluation. Control commits mark the pipeline unconfigured, then the worker waits for the pipeline to become idle before pushing subdevice controls and encoder settings. Streaming requests set `state_pipeline_req` and then wait for the worker to reach `READY` or `RUN`. The state machine repeatedly evaluates pathway, pipeline config, encoder firmware/config/run, decoder run/stabilization, and USB stream bits until stable, then derives `DEAD`, `COLD`, `WARM`, `ERROR`, `READY`, or `RUN`.

State and persistence: runtime state is held in `struct pvr2_hdw`; static `unit_pointers[]` tracks unit allocation. Firmware uploads and GPIO/register writes affect hardware until reset. EEPROM/CPU firmware fetch mode stores data in `fw_buffer` only while enabled. Dirty flags on controls are the persistence boundary between user-visible values and hardware/subdevice state.

Dependencies and integration points: integrates with Linux firmware loading, USB URBs/control and bulk endpoints, V4L2 device/subdev calls, tuner and media I2C modules, cx2341x MPEG helpers, pvrusb2 encoder support, EEPROM analysis, device descriptor tables, pvrusb2 stream buffers, and optional digital hardware schemes. Higher layers call the public hardware API and consume state callbacks and stream handles.

Risks: USB control transfers render the device inoperable on most failures, so transient errors can force `DEAD`. Firmware size, endian swabbing, endpoint assumptions, and cx25840/wm8775 quirks are device-sensitive. The worker relies on timers and many booleans; missed scheduling or stale dirty flags can stall streaming. Pathway changes require the pipeline to be idle. Some failure paths log and continue, so partial subdevice setup can surface later as missing decoder or error state.

Test signals: firmware-present and firmware-missing probe paths; cold-device re-enumeration; analog and digital input switching; start/stop streaming repeatedly; change unsafe controls while streaming and verify pause/reconfigure/resume; exercise V4L2 standard/frequency/crop controls; unplug during control transfer and streaming; read sysfs/debug state reports; watch dmesg for state transitions, firmware upload, subdevice load failures, and stream statistics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-hdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-hdw.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-hdw.h

Purpose: public hardware API for the pvrusb2 driver. It exposes an opaque `struct pvr2_hdw`, control IDs, input constants, stream configuration types, master-state constants, and the operations used by V4L2, sysfs, context, DVB, debug, and lower-level helper modules.

Important APIs, types, and functions: defines internal control IDs such as `PVR2_CID_STDCUR`, `PVR2_CID_INPUT`, `PVR2_CID_FREQUENCY`, crop capability IDs, and `PVR2_CID_STDDETECT`. Defines input values for TV, DTV, composite, S-video, and radio; `enum pvr2_config` for MPEG/VBI/PCM/raw stream configuration; `enum pvr2_v4l_type` for minor-number slots; and master states `PVR2_STATE_DEAD` through `PVR2_STATE_RUN`. Public functions cover creation, initialization, teardown, disconnect, V4L device hookup, unit/USB/serial/bus/identity lookup, control enumeration, control lookup by index/internal ID/V4L ID, control commit, input availability/allowed masks, tuner/crop/status polling, USB speed query, type/description lookup, streaming control, stream-type control, video stream retrieval, CPU firmware/EEPROM debug retrieval, V4L minor storage, control-message/register/GPIO helpers, debug state reports, module status logging, and encoder firmware upload.

Control flow: callers create a hardware handle in USB probe, initialize it with a state callback, attach user-facing interfaces, commit controls after updates, start/stop streaming through the state machine, and disconnect/destroy on USB removal. Lower-level helpers use the same header for register and GPIO commands that are intentionally not part of normal user-facing control flow.

State and persistence: the header hides all state inside `struct pvr2_hdw`. It communicates state through getters, control handles, stream handles, and debug reports. No persistent storage is declared here.

Dependencies and integration points: includes Linux USB/V4L2 declarations, `pvrusb2-io.h` for `struct pvr2_stream`, and `pvrusb2-ctrl.h` for control access. It is the principal contract between hardware core and pvrusb2 context, sysfs, V4L2, DVB, encoder, I2C, and debug code.

Risks: low-level APIs such as `pvr2_send_request()`, `pvr2_write_register()`, GPIO changes, CPU reset, and firmware upload can disrupt hardware state and must be serialized by implementation expectations. Minor-number storage is explicitly a V4L coupling inside hardware state. State values are numeric and used by controls/sysfs, so changing them has user-visible effects.

Test signals: compile all callers after prototype changes; probe/remove devices; verify state names through controls and debug; run V4L2 open/register/minor paths; exercise debug firmware and GPIO functions only on controlled hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-hdw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-i2c-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-i2c-core.c

Purpose: implements the pvrusb2 I2C adapter by translating Linux I2C transfers into FX2 firmware commands and layering device-specific I2C quirks for IR receivers, wm8775, and cx25840 chips.

Important APIs, types, and functions: module parameters `i2c_scan`, per-unit `ir_mode`, and `disable_autoload_ir_video` shape initialization. `pvr2_i2c_write()`, `pvr2_i2c_read()`, and `pvr2_i2c_basic_op()` issue `FX2CMD_I2C_WRITE` and `FX2CMD_I2C_READ` through `pvr2_send_request()`. Special function entries include `i2c_24xxx_ir()`, `i2c_hack_wm8775()`, `i2c_black_hole()`, and `i2c_hack_cx25840()`. `pvr2_i2c_xfer()` is the adapter `master_xfer`, and `pvr2_i2c_functionality()` advertises `I2C_FUNC_SMBUS_EMUL | I2C_FUNC_I2C`. `pvr2_i2c_core_init()` and `pvr2_i2c_core_done()` are the public lifecycle hooks.

Control flow: initialization fills `hdw->i2c_func[]` with the basic operation, overrides specific addresses for disabled IR, emulated 24xxx IR, cx25840 wedge detection, or wm8775 probe success, configures `i2c_adapter`/`i2c_algorithm`, registers the adapter, optionally probes for newer IR hardware at `0x71`, optionally scans all addresses, and binds an IR I2C client. The transfer path chooses the function for the first address, supports one-message reads/writes and two-message write-then-read transactions, chunks reads to fit the shared 64-byte command buffer, rejects unsupported shapes, and logs traffic when enabled.

State and persistence: per-device state lives in `hdw->i2c_func[]`, `i2c_cx25840_hack_state`, `i2c_linked`, `ir_scheme_active`, and `ir_init_data`. I2C subdevice binding persists until `i2c_del_adapter()` in teardown. No disk state is written.

Dependencies and integration points: depends on `pvrusb2-hdw-internal.h`, FX2 command definitions, Linux I2C core, V4L2 subdevice discovery through the hardware core, and `ir-kbd-i2c` client data. `pvrusb2-hdw.c` initializes this before loading V4L2 submodules and calls teardown during disconnect.

Risks: only limited I2C transaction forms are supported; unsupported multi-message or address-changing transfers fail. The shared `cmd_buffer` limits transfer size and requires `ctl_lock` serialization. The cx25840 hack can deliberately disable address `0x44` and render the device useless if a wedged chip is detected. IR emulation fabricates data for legacy modules and can confuse probes if assumptions change.

Test signals: load with and without IR; run optional `i2c_scan`; verify tuner/decoder/audio subdevices attach; exercise IR on 29xxx, 24xxx, 24xxx MCE, and Zilog schemes; test long reads that require chunking; watch for unexpected I2C status logs, cx25840 wedge warnings, and correct adapter deletion on unplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-i2c-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-i2c-core.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-i2c-core.h

Purpose: small lifecycle header for the pvrusb2 I2C core. It exposes the adapter setup and teardown functions to the hardware core while keeping transfer implementation private.

Important APIs, types, and functions: forward declares `struct pvr2_hdw`; declares `pvr2_i2c_core_init(struct pvr2_hdw *)` and `pvr2_i2c_core_done(struct pvr2_hdw *)`.

Control flow: `pvrusb2-hdw.c` calls `pvr2_i2c_core_init()` after FX2 firmware/powerup is ready and before V4L2 subdevices are loaded. It calls `pvr2_i2c_core_done()` during disconnect to unregister the adapter and clients.

State and persistence: this header defines no state. The implementation stores adapter, algorithm, callback table, and IR state inside `struct pvr2_hdw`.

Dependencies and integration points: isolates I2C lifecycle from public hardware APIs and lets hardware initialization avoid exposing Linux I2C details to unrelated callers.

Risks: callers must only initialize once per connected hardware object and must call done before USB memory/parent device references disappear. Reordering around subdevice creation/removal risks dangling I2C clients.

Test signals: probe/remove cycle with subdevices loaded; unplug during initialization; build coverage for all files including this header; no I2C adapter leaks after disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-i2c-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-io.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-io.c

Purpose: reusable USB bulk-stream buffer manager for pvrusb2. It owns buffer allocation, idle/queued/ready list transitions, URB submission/completion, error tolerance accounting, callbacks, and stream statistics.

Important APIs, types, and functions: private `struct pvr2_stream` tracks queued, ready, and idle lists plus counts/bytes, buffer array sizing, callback, USB device/endpoint, locks, tolerance counters, and processed byte/error totals. Private `struct pvr2_buffer` wraps an ID, state, client storage pointer, used/max counts, status, stream pointer, list node, and URB. Public functions include `pvr2_stream_create()`, `pvr2_stream_destroy()`, `pvr2_stream_setup()`, `pvr2_stream_set_callback()`, `pvr2_stream_get_stats()`, buffer-count getters/setters, idle/ready/buffer lookup, `pvr2_stream_kill()`, `pvr2_buffer_set_buffer()`, `pvr2_buffer_queue()`, and buffer accessors.

Control flow: stream setup flushes queued work and binds a USB device/endpoint/tolerance. Buffer-count changes allocate or free `struct pvr2_buffer` objects and URBs, keeping newly available buffers on the idle list. `pvr2_buffer_queue()` kills any pending URB for that buffer, moves it to queued, fills a bulk receive URB with caller-owned storage, and submits it. `buffer_complete()` records status and bytes, tolerates a configurable number of nonfatal failures, moves the buffer to ready, and invokes the callback when data arrives. `pvr2_stream_kill()` cancels queued URBs, moves ready buffers back idle, and resizes toward target.

State and persistence: all state is volatile in `struct pvr2_stream` and buffers. Statistics persist until reset through `pvr2_stream_get_stats(..., zero_counts=1)`. Client data storage is supplied by higher layers and only referenced here.

Dependencies and integration points: uses Linux USB bulk URBs, spinlocks for list state in completion context, a mutex for structural changes, and pvrusb2 debug tracing. `pvrusb2-hdw.c` creates and configures the video stream, while `pvrusb2-ioread.c` provides storage and user-read semantics on top.

Risks: `pvr2_buffer_queue()` does not propagate `usb_submit_urb()` failure into `ret`, so failed submissions may only surface later through status/list behavior. List getters are mostly unlocked and rely on caller discipline. Error tolerance can hide intermittent transfer failures. Buffer storage must remain valid while queued. Shrinking the buffer pool only frees trailing idle buffers, so target count may not be reached until active buffers return.

Test signals: repeated set-buffer-count and start/stop streaming; USB disconnect while URBs are queued; forced transfer errors with tolerance set to 0 and nonzero values; stats consistency; lockdep/KASAN on queue/kill/race paths; verify callback wakes readers only when ready data appears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-io.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-io.h

Purpose: public interface for pvrusb2 USB stream and buffer management. It hides stream internals while exposing buffer states, statistics, callbacks, lifecycle, queueing, and ready/idle buffer access.

Important APIs, types, and functions: declares `pvr2_stream_callback`, `enum pvr2_buffer_state`, opaque `struct pvr2_stream` and `struct pvr2_buffer`, and `struct pvr2_stream_stats`. Stream APIs create/destroy/setup streams, set callbacks, get/reset stats, configure buffer counts, get idle/ready/specific buffers, count ready buffers, and kill queued/ready data. Buffer APIs set external storage, read ready byte count/status/ID, and queue a buffer for USB filling.

Control flow: users create a stream, bind it to a USB endpoint, allocate a chosen number of buffers, attach storage to idle buffers, queue buffers, consume ready buffers, then requeue or kill them during stop/teardown. The callback signals transitions to ready data but does not itself transfer data.

State and persistence: the header exposes only counters and state enum values. Stream and buffer internals remain private to `pvrusb2-io.c`.

Dependencies and integration points: includes Linux USB and list declarations. Used by `pvrusb2-hdw.h` for stream handles and by `pvrusb2-ioread.h/.c` to build a user-readable streaming path.

Risks: callers must not manipulate buffers outside expected idle/queued/ready transitions. Storage passed to `pvr2_buffer_set_buffer()` must outlive queued URBs. `pvr2_stream_get_ready_buffer()` and `pvr2_stream_get_idle_buffer()` return raw pointers whose state can change in completion context if caller locking is not aligned with the implementation.

Test signals: compile all stream users; validate queue/read/requeue loops; inspect stats through hardware reports; disconnect and destroy without leaked URBs or buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-ioread.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-ioread.c

Purpose: read-side adapter that turns a `pvr2_stream` of USB buffers into a user-copy pull interface with fixed buffer storage, optional stream synchronization-key filtering, availability checks, and start/stop control.

Important APIs, types, and functions: `struct pvr2_ioread` stores the stream, 32 page-aligned 16 KiB buffers, optional sync key, sync state/offset/skip count, enabled/spigot/running flags, current buffer and offsets, and a mutex. Public functions include `pvr2_ioread_create()`, `pvr2_ioread_destroy()`, `pvr2_ioread_setup()`, `pvr2_ioread_get_stream()`, `pvr2_ioread_set_sync_key()`, `pvr2_ioread_set_enabled()`, `pvr2_ioread_avail()`, and `pvr2_ioread_read()`. Internal helpers include `pvr2_ioread_start()`, `pvr2_ioread_stop()`, `pvr2_ioread_get_buffer()`, and `pvr2_ioread_filter()`.

Control flow: creation allocates fixed buffer storage. Setup tears down any previous stream, kills it, sets the stream buffer count to 32, assigns each stream buffer one storage block, and records the stream. Enabling queues every idle buffer and optionally enters sync-search state. Availability rejects disabled streams, searches for the sync key if required, then requires either any ready buffer once running or at least half the buffers ready before first read. Reading calls availability, marks the stream running, copies from the current ready buffer or repeated sync key to userspace, advances offsets, and requeues exhausted buffers.

State and persistence: all state is volatile per reader. Sync state transitions from searching (`1`) to replaying matched key (`2`) to normal (`0`). Stream buffers are recycled continuously until stop. No persistent storage is used.

Dependencies and integration points: depends on `pvrusb2-io` for buffer queueing/status, kernel `copy_to_user()`, page-aligned allocation, and pvrusb2 debug tracing. V4L2/read-style interfaces can use this layer to expose streaming data without knowing URB details.

Risks: sync filtering has subtle boundary accounting; `cp->c_data_offs += idx` adds an absolute index rather than consumed delta, which is worth scrutinizing for nonzero offsets. A bad userspace pointer returns `-EFAULT` after data may already be consumed. `pvr2_ioread_get_buffer()` stops streaming on queue or buffer status errors and reports no buffer, causing read-side `-EIO` or `-EAGAIN`. Availability threshold delays initial delivery until half the buffers fill, trading latency for smoothness.

Test signals: read streaming with and without sync keys; sync key split across buffers; nonblocking/poll paths expecting `-EAGAIN`; user fault injection; repeated enable/disable/setup; disconnect during read; verify every consumed buffer is requeued and no ready-buffer starvation occurs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-ioread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-ioread.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-ioread.h

Purpose: public header for the pvrusb2 read adapter layered over `pvr2_stream`. It exposes a compact API for setup, synchronization, enablement, availability, and userspace reads.

Important APIs, types, and functions: declares opaque `struct pvr2_ioread`; lifecycle functions `pvr2_ioread_create()` and `pvr2_ioread_destroy()`; `pvr2_ioread_setup()` to bind a stream; `pvr2_ioread_get_stream()` to retrieve it; `pvr2_ioread_set_sync_key()` for MPEG or stream alignment; `pvr2_ioread_set_enabled()` to start/stop queueing; `pvr2_ioread_read()` for `copy_to_user()` reads; and `pvr2_ioread_avail()` for readiness checks.

Control flow: clients create a reader, bind it to a stream from hardware, optionally set a sync key, enable it when capture starts, call avail/read from file operations, and disable/destroy it during close or teardown.

State and persistence: the header hides all state. Runtime storage and current buffer offsets are owned by `pvrusb2-ioread.c`.

Dependencies and integration points: includes `pvrusb2-io.h` so callers can work with the underlying stream handle. It is intended for V4L2 read interfaces or similar code paths that need byte-stream access.

Risks: callers must coordinate hardware streaming state with reader enablement. Reads return kernel error codes (`-EIO`, `-EAGAIN`, `-EFAULT`) that user-facing file operations must propagate correctly. The `void __user *` contract requires use only from user-copy contexts.

Test signals: compile users; bind/unbind against a live `pvr2_stream`; check read readiness behavior in blocking and nonblocking modes; validate cleanup when stream setup fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-ioread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-main.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-main.c

Purpose: module and USB-driver entry point for pvrusb2. It registers the USB driver, creates/destroys global context/sysfs state, and wires each probed USB interface into the pvrusb2 context plus V4L2/DVB/sysfs attachment layers.

Important APIs, types, and functions: defines driver metadata, default debug mask, global `pvrusb2_debug`, and module parameter `debug`. `pvr_setup_attach()` creates V4L2, optional DVB, and sysfs interfaces for a context. `pvr_probe()` calls `pvr2_context_create()`, stores the context with `usb_set_intfdata()`, and returns probe status. `pvr_disconnect()` clears interface data and calls `pvr2_context_disconnect()`. `pvr_driver` provides USB name, ID table, probe, and disconnect callbacks. `pvr_init()` and `pvr_exit()` handle module load/unload.

Control flow: module init initializes global context state, registers the sysfs class, registers the USB driver, and logs version/debug state. USB core invokes probe for IDs in `pvr2_device_table`; probe creates context, which in turn creates hardware and eventually calls the attach callback to expose interfaces. Disconnect tears down the context. Module exit deregisters USB, releases global context state, and unregisters sysfs class.

State and persistence: global `pvrusb2_debug` controls trace output until module unload or parameter change. Per-device state is stored in `struct pvr2_context` via USB interface driver data. No persistent storage is used.

Dependencies and integration points: depends on USB core, pvrusb2 device attributes, context manager, hardware API, V4L2 layer, optional DVB layer, sysfs support, and debug tracing. It is the top-level integration point for kernel module lifecycle.

Risks: if `usb_register()` fails after `pvr2_sysfs_class_create()`, `pvr_init()` returns without destroying the class in this file, so init-failure cleanup depends on broader kernel/module behavior. Probe failure returns `-ENOMEM` for any context creation failure, even non-allocation errors hidden inside context creation. Attach ordering determines whether V4L2/DVB/sysfs see fully initialized hardware.

Test signals: module load/unload; USB probe/disconnect; sysfs class present only while loaded; V4L2/DVB nodes appear for supported devices; debug parameter changes trace output; failure injection around context creation and USB registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-std.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-std.c

Purpose: converts between pvrusb2 textual video-standard names and V4L2 `v4l2_std_id` bitmasks. It provides compact symbol support for controls and sysfs/debug display.

Important APIs, types, and functions: `struct std_name` maps a string to a standard mask. Macros define PAL, NTSC, ATSC, SECAM color-system masks and modulation masks such as B, D, G, I, M, N, 60, 8VSB, and 16VSB. `std_groups[]` maps color-system names to broad masks. `std_items[]` maps modulation tokens to possible standards. `find_std_name()` searches a token table. Public APIs are `pvr2_std_str_to_id()`, `pvr2_std_id_to_str()`, and `pvr2_std_get_usable()`.

Control flow: parsing alternates between color-system mode and modulation-token mode. A group token must be followed by `-`; modulation tokens are separated by `/` and groups by `;`. Each modulation token is intersected with the active color-system mask; illegal names or impossible combinations fail. Formatting iterates groups and items in table order, emits `GROUP-item/item;GROUP-item`, and includes only standards present in the input mask. `pvr2_std_get_usable()` returns the aggregate mask of all table-supported color systems.

State and persistence: stateless conversion code with static const mapping tables. No runtime or persistent state.

Dependencies and integration points: used by `pvrusb2-hdw.c` control conversion and standard setup to expose and parse video standard masks. Depends on V4L2 standard bit definitions and `scnprintf()`.

Risks: parser is case-sensitive and requires exact syntax. Formatting order is table-driven and may not match user input order. Unknown or newly added V4L2 standard bits outside `CSTD_ALL` are omitted and not considered usable. `scnprintf()` return values are accumulated even as the buffer shrinks, so return length can exceed output capacity by design-like snprintf semantics.

Test signals: round-trip parse/format for PAL, NTSC, SECAM, ATSC combinations; invalid token rejection; buffer truncation behavior; standards controls in sysfs and V4L2 accepting strings generated by this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-std.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-std.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-std.h

Purpose: public declaration header for pvrusb2 video-standard string conversion helpers.

Important APIs, types, and functions: declares `pvr2_std_str_to_id()` to parse strings like `PAL-B/G;NTSC-M` into V4L2 standard masks, `pvr2_std_id_to_str()` to format a mask into parseable text, and `pvr2_std_get_usable()` to return standards supported by the conversion tables.

Control flow: callers use the parser for control writes and the formatter for control reads/logging. The header itself contains no executable logic.

State and persistence: no state is declared. Conversion tables live in `pvrusb2-std.c`.

Dependencies and integration points: includes `linux/videodev2.h` for `v4l2_std_id`. Used by hardware controls and any user-facing interface that wants symbolic standard masks.

Risks: callers must pass explicit buffer sizes because parser input is not necessarily NUL-terminated. Formatter return values should be treated as byte counts, not necessarily NUL-terminated string length.

Test signals: build callers; unit-style round trips through controls; sysfs writes using generated standard strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-std.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-sysfs.c

Purpose: optional sysfs interface for pvrusb2 devices. It creates a `pvrusb2` class device per hardware instance, exposes hardware identity/minor-number attributes, creates per-control sysfs groups, and optionally exposes debug command/status files.

Important APIs, types, and functions: `struct pvr2_sysfs` stores a channel, class device, optional debug interface, linked control items, top-level device attributes, and creation flags. `struct pvr2_sysfs_ctl_item` stores attributes for one control (`name`, `type`, `min_val`, `max_val`, `def_val`, `enum_val`, `bit_val`, `cur_val`, `custom_val`) plus its attribute group. Show/store helpers use `pvr2_ctrl_*` APIs and `pvr2_hdw_commit_ctl()`. `pvr2_sysfs_add_control()`, `pvr2_sysfs_add_controls()`, and teardown functions manage control groups. `class_dev_create()` creates the class device and top-level files. Public functions are `pvr2_sysfs_create()`, `pvr2_sysfs_class_create()`, and `pvr2_sysfs_class_destroy()`.

Control flow: module init registers the class. Per-device create allocates a `pvr2_sysfs`, initializes a pvrusb2 channel with a disconnect check callback, creates the class device named from the hardware identifier, adds top-level files, adds one group per hardware control, and optionally adds debug files. Attribute reads fetch current values, descriptions, types, enumerations, bit names, or hardware identity. Attribute writes parse normal or custom symbols, set control masks/values, and commit hardware controls. On context disconnect, `pvr2_sysfs_internal_check()` tears down debug files, control groups, top-level files, drops the parent device reference, unregisters the class device, finalizes the channel, and frees state.

State and persistence: sysfs object state is in memory. Control writes change driver and hardware state through the hardware commit path but are not persisted across unload or unplug. Creation flags prevent removing files that were never successfully added.

Dependencies and integration points: depends on `pvrusb2-context` channel lifecycle, hardware/control APIs, Linux device/sysfs class APIs, optional `pvrusb2-debugifc`, and V4L minor-number storage in hardware state. The header compiles to no-ops when sysfs support is disabled.

Risks: many files are created individually, so partial creation must be unwound carefully. `pvr2_sysfs_add_control()` leaves a `ctl_item` linked even if `sysfs_create_group()` fails, relying on `created_ok` to skip removal. Control stores commit hardware synchronously and can trigger disruptive pipeline reconfiguration. Device parent references must be balanced; teardown handles this through `get_device()`/`put_device()`.

Test signals: sysfs class registration with `CONFIG_VIDEO_PVRUSB2_SYSFS`; per-device class entries named by serial/unit; enumerate all `ctl_*` groups; read/write integer, enum, bitmask, and custom controls; unplug while sysfs files are open; enable debug interface and run `debugcmd`/`debuginfo`; verify no sysfs warnings or leaked devices on unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-sysfs.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-sysfs.h

Purpose: conditional public header for pvrusb2 sysfs support. It exposes sysfs class and per-context creation hooks, or inline no-ops when the feature is disabled.

Important APIs, types, and functions: declares `pvr2_sysfs_class_create()`, `pvr2_sysfs_class_destroy()`, and `pvr2_sysfs_create(struct pvr2_context *mp)` under `CONFIG_VIDEO_PVRUSB2_SYSFS`; otherwise defines empty inline versions.

Control flow: module init calls class create, module exit calls class destroy, and per-device attach calls create. With sysfs disabled, the same call sites compile away.

State and persistence: no state in the header. Implementation state lives in `pvrusb2-sysfs.c` and in pvrusb2 context/channel objects.

Dependencies and integration points: includes Linux list/sysfs declarations and `pvrusb2-context.h`. It lets `pvrusb2-main.c` and attach code avoid preprocessor-heavy call sites.

Risks: callers should not assume sysfs exists unless the config is enabled. The no-op path means tests must cover both enabled and disabled builds.

Test signals: build with `CONFIG_VIDEO_PVRUSB2_SYSFS=y/m` and disabled; verify call sites need no extra ifdefs; class/device entries appear only in enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-util.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-util.h

Purpose: small endian packing helper header for pvrusb2 command buffers. It provides macros to decompose and compose 32-bit values in little-endian or big-endian byte order.

Important APIs, types, and functions: `PVR2_DECOMPOSE_LE(t,i,d)` writes `d` into four bytes starting at `t[i]` least-significant byte first. `PVR2_DECOMPOSE_BE(t,i,d)` writes most-significant byte first. `PVR2_COMPOSE_LE(t,i)` reads four bytes as a little-endian `u32`. `PVR2_COMPOSE_BE(t,i)` reads four bytes as a big-endian `u32`.

Control flow: macros expand inline at call sites. In this subset, `pvrusb2-hdw.c` uses the little-endian helpers for FX2 register read/write command buffers.

State and persistence: stateless macros. They mutate only the caller-provided byte array for decomposition.

Dependencies and integration points: depends on `u32` being visible at the inclusion site. Used by low-level hardware command paths that communicate with the encoder/FX2 firmware.

Risks: arguments are evaluated multiple times in some macro expressions, so callers should avoid side-effecting arguments for `t`, `i`, or `d`. No bounds checking is performed; callers must ensure at least four bytes are valid. Endianness is explicit and independent of host CPU order.

Test signals: compile low-level command users; verify register write/read byte order against USB traces; static analysis for side-effecting macro arguments and buffer bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-util.h -->
