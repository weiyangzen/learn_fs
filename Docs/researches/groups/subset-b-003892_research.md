# subset-b-003892 research

Grouped research for Linux IIO core, buffer, trigger, backend, configfs, software device, software trigger, triggered-event, and GTS helper files under `sources/distributed-fs/ceph-client/drivers/iio`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/industrialio-backend.c -->
# sources/distributed-fs/ceph-client/drivers/iio/industrialio-backend.c

## Purpose
`industrialio-backend.c` implements the IIO backend framework used by aggregate converter devices where a frontend IIO device, such as an ADC or DAC driver, delegates low-level digital-interface, DMA, timing, formatting, or calibration operations to one or more backend devices. Backends register themselves globally, frontends resolve them through firmware-node references, and the framework supplies exported wrappers around `struct iio_backend_ops` with argument validation, lifetime management, debugfs integration, and devm cleanup.

## Important APIs, types, and functions
- `struct iio_backend` is the private framework object. It stores the backend ops, backend device, consumer/frontend device, provider module owner, private driver data, firmware-visible name, cached debugfs register address, capability bits, list node, and frontend-relative index.
- `struct iio_backend_buffer_pair` binds a backend and requested `struct iio_buffer` for devm cleanup.
- `iio_backend_op_call()`, `iio_backend_ptr_op_call()`, and `iio_backend_void_op_call()` are internal dispatch macros that return `-EOPNOTSUPP` when an operation is absent.
- Exported operation wrappers include channel enable/disable, backend enable/disable, data format/source/sample-rate/test-pattern/status, I/O delay, sample trigger, raw reads, interface type, data size, oversampling, filter type, data alignment, lane count, DDR mode, stream enable, data-transfer address, and capability checks.
- `iio_backend_extend_chan_spec()` lets a backend add channel ext_info while enforcing that backend ext_info callbacks use `iio_backend_ext_info_get()` and `iio_backend_ext_info_set()`.
- `devm_iio_backend_request_buffer()` requests a backend-owned buffer and registers a devm action that calls backend `free_buffer`.
- `devm_iio_backend_get()`, `devm_iio_backend_fwnode_get()`, and `__devm_iio_backend_get_from_fwnode_lookup()` resolve registered backends by `io-backends` firmware references or legacy fwnode lookup.
- `devm_iio_backend_register()` allocates the private backend object, records metadata from `struct iio_backend_info`, inserts it into `iio_back_list`, and removes it through a devm action.
- `iio_backend_debugfs_add()` creates per-backend `backendN` debugfs directories under the frontend IIO debugfs node.

## Control flow
Backend providers call `devm_iio_backend_register()` during probe. The backend object is devm-allocated, populated from `iio_backend_info`, and inserted into the global `iio_back_list` under `iio_back_lock`. Consumers call `devm_iio_backend_get()` or a fwnode variant. The resolver finds the requested `io-backends` reference, walks the backend list, obtains a provider module reference with `try_module_get()`, registers a devm release action, creates a supplier/consumer device link, records `frontend_dev`, and returns the backend pointer. If no matching provider exists yet, the fwnode path returns `-EPROBE_DEFER`.

Runtime frontend calls go through small wrappers that validate enumerated inputs and then call the backend operation. Ext-info callbacks are a special case: because sysfs callbacks receive only the frontend `iio_dev`, `iio_backend_ext_info_get()` and `_set()` infer the backend from the frontend parent. That inference deliberately rejects multiple matching backends, requiring such frontends to provide more explicit routing.

Debugfs access is optional. If the frontend IIO debugfs directory exists and the backend supplies either register access or a name, `iio_backend_debugfs_add()` creates `backendN/direct_reg_access` and/or `backendN/name`. The register file stores a cached address on one-value writes and performs writes on two-value input.

## State and persistence behavior
Framework state is in-memory only: the global backend list, provider module references, device links, `frontend_dev` associations, cached debugfs register address, and backend index. Hardware state changes are delegated to backend ops and may persist according to the backend device. `devm_iio_backend_enable()` and `devm_iio_backend_request_buffer()` bind disable/free operations to consumer-device lifetime. Registration cleanup removes the backend from the global list; consumer cleanup drops the provider module reference via `iio_backend_release()`.

## Dependencies and integration points
The file depends on Linux device links, firmware-node property references (`io-backends` and `io-backend-names`), debugfs, module ownership, devm actions, the IIO core, and `include/linux/iio/backend.h`. It integrates with frontend channel sysfs via ext_info callbacks and with backend-provided buffers through the IIO buffer interface.

## Risks
- `iio_backend_ext_info_get()` and `_set()` infer a backend from `indio_dev->dev.parent`; this is intentionally limited and fails for multi-backend frontends unless they route explicitly elsewhere.
- `__devm_iio_backend_get()` records `back->frontend_dev = dev` in the backend object. A backend consumed by multiple frontends or reused unexpectedly would need careful scrutiny.
- Many wrappers rely on backend implementations to serialize hardware access and validate channel numbers; the framework mostly validates enum ranges and null ops.
- Debugfs register access writes to `cached_reg_addr` without a per-backend lock; concurrent debugfs readers/writers can race on the cached address.
- `iio_backend_extend_chan_spec()` rejects overwritten frontend ext_info and backend custom handlers. That protects callback routing but can surprise backend authors expecting to append or customize.

## Test signals
- Build with `CONFIG_IIO_BACKEND` users and `CONFIG_DEBUG_FS` enabled and disabled.
- Probe tests should cover missing `io-backends`, named backend lookup, `-EPROBE_DEFER`, duplicate or multi-backend frontend cases, and device-link/provider module reference cleanup.
- API tests should verify `-EOPNOTSUPP` for absent ops and `-EINVAL` for invalid enum inputs or zero-only constraints.
- Debugfs tests should validate one-value cached address writes, two-value register writes, readback, and backend index naming for multiple named backends.
- Channel extension tests should confirm backend ext_info must use the framework get/set helpers and cannot replace frontend ext_info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/industrialio-backend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/industrialio-buffer.c -->
# sources/distributed-fs/ceph-client/drivers/iio/industrialio-buffer.c

## Purpose
`industrialio-buffer.c` implements IIO buffered data plumbing. It owns attached buffer lists, scan-mask sysfs, buffer enable/disable transitions, scan-byte calculation, demultiplexing when per-buffer masks differ from the active device mask, legacy character-device read/write/poll operations, newer per-buffer anon-fd access, dma-buf attachment/enqueue support, and helpers for pushing samples into active buffers.

## Important APIs, types, and functions
- `struct iio_dmabuf_priv` tracks an attached dma-buf, mapped sg table, direction, IIO DMA block, fence context, refcount, and list membership.
- `struct iio_dma_fence` wraps `struct dma_fence` with an IIO dma-buf private pointer and deferred cleanup work.
- `iio_buffer_read()`, `iio_buffer_write()`, and `iio_buffer_poll()` implement blocking/nonblocking user I/O against an `iio_dev_buffer_pair`.
- `iio_scan_mask_set()`, `iio_scan_mask_clear()`, `iio_scan_el_store()`, and timestamp scan-element helpers implement `scan_elements/*_en`.
- `iio_compute_scan_bytes()` computes packed scan size using channel storage bits, repeat count, alignment, and optional timestamp.
- `iio_verify_update()`, `__iio_update_buffers()`, `iio_enable_buffers()`, and `iio_disable_buffers()` negotiate buffer modes, scan masks, watermark, trigger attachment, and setup callbacks.
- `iio_buffer_update_demux()` builds `struct iio_demux_table` entries when a buffer wants a subset of the active scan mask.
- `iio_buffer_attach_dmabuf()`, `_detach_dmabuf()`, `_enqueue_dmabuf()`, and `iio_buffer_signal_dmabuf_done()` implement dma-buf import and fence signaling.
- `iio_buffers_alloc_sysfs_and_mask()` creates `bufferN`, legacy `buffer`, and legacy `scan_elements` groups; it also registers the `IIO_BUFFER_GET_FD_IOCTL` handler.
- `iio_push_to_buffers()` and `iio_push_to_buffers_with_ts_unaligned()` are exported producer-side sample push helpers.
- `iio_device_attach_buffer()`, `iio_buffer_init()`, `iio_buffer_get()`, and `iio_buffer_put()` manage buffer lifetime.

## Control flow
Drivers attach one or more initialized buffers to an IIO device. During device registration, `iio_buffers_alloc_sysfs_and_mask()` derives `masklength` from channel scan indexes, validates scan types, allocates scan masks, creates per-buffer sysfs groups, and creates legacy groups for buffer zero. Users configure `length`, `watermark`, channel enable bits, and timestamp enable while the buffer is inactive. Stores take the IIO device `mlock` and reject changes when the buffer is active.

Enabling a buffer calls `__iio_update_buffers()`. The function verifies the combined configuration, requests a buffer update, disables any old active configuration, activates/removes list entries, and enables the new configuration. Mode selection intersects device modes with all active buffer access modes, preferring triggered mode when a trigger is present, otherwise hardware then software. The active scan mask may be a driver-provided available mask or a dynamically allocated compound mask. Enable paths run setup `preenable`, driver `update_scan_mode`, optional hardware FIFO watermark update, each buffer `enable`, trigger pollfunc attachment for triggered mode, and setup `postenable`. Error paths disable and deactivate buffers to leave direct mode.

Reads wait on the buffer poll queue until enough samples are available or a flush succeeds. Writes wait for output-buffer space. The newer `IIO_BUFFER_GET_FD_IOCTL` returns an anon inode tied to one attached buffer and sets `IIO_BUSY_BIT_POS`, causing legacy wrapper access to return `-EBUSY` while the new fd owns the buffer. Dma-buf ioctls attach, detach, and enqueue externally allocated memory; enqueue reserves a dma fence, waits for conflicting reservation-object fences, queues the transfer through buffer access ops, and signals completion asynchronously through `iio_buffer_signal_dmabuf_done()`.

## State and persistence behavior
State is runtime kernel state: attached buffer array, active buffer list, scan masks, timestamp flags, per-buffer demux tables, watermarks, lengths, dma-buf attachment lists, fence sequence numbers, busy bits, and device current mode. There is no persistent on-disk state. Active scan masks allocated dynamically are freed on disable; driver-provided available masks are not. Buffer reference counts protect attached buffers and active list membership. Unregister paths set `indio_dev->info` elsewhere and wake poll queues so blocked readers and writers exit.

## Dependencies and integration points
The file integrates with IIO core opaque state, IIO trigger attach/detach, channel scan types, setup ops, buffer implementation callbacks, sysfs group registration, anon inodes, `poll`, wait queues, dma-buf, dma-resv, dma-fence, scatter-gather mappings, and exported IIO producer APIs. Buffer access implementations supply operations such as `read`, `write`, `store_to`, `set_length`, `request_update`, `attach_dmabuf`, and `enqueue_dmabuf`.

## Risks
- The available scan-mask terminator logic intentionally uses only the first `unsigned long`; comments warn multi-long masks are not fully handled and can hide valid masks.
- Error recovery after failed enable/disable is best effort. `__iio_update_buffers()` deactivates all buffers after low-level failures because hardware state may be uncertain.
- Dma-buf paths involve reservation locks, attachment references, queued fences, and deferred cleanup. Incorrect buffer access implementations can deadlock or leak attachments.
- `iio_buffer_attach_dmabuf()` unlocks the reservation object before duplicate attachment detection and uses custom cleanup for that case; this is subtle lifetime code.
- Legacy and anon-fd access are mutually excluded with busy bits, but tests must cover both device-level and buffer-level busy states.
- Demux code assumes timestamp placement and scan-index ordering; bad channel metadata can produce wrong sample layouts.

## Test signals
- Build with dma-buf enabled and exercise both `CONFIG_DEBUG_FS`-independent buffer paths and compile-time namespace imports.
- Sysfs tests should cover scan type validation, duplicate or invalid scan masks, changing length/watermark/channel bits while active, and legacy group aliases for buffer zero.
- Runtime tests should enable single and multiple buffers in software/triggered modes, hardware single-buffer mode rejection for extra buffers, and trigger attach/detach ordering.
- I/O tests should check blocking read wakeups, nonblocking `-EAGAIN`, hardware FIFO flush behavior, output buffer write/poll, unregister wakeups, and `-ENODEV` after removal.
- Dma-buf tests should cover attach/detach/enqueue, duplicate attach rejection, cyclic only on output buffers, invalid sizes/flags, reservation-object contention, fence error signaling, and close cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/industrialio-buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/industrialio-configfs.c -->
# sources/distributed-fs/ceph-client/drivers/iio/industrialio-configfs.c

## Purpose
`industrialio-configfs.c` provides the root configfs subsystem for Industrial I/O. It creates the top-level `iio` configfs subsystem under which other IIO modules, notably software devices and software triggers, register default groups.

## Important APIs, types, and functions
- `iio_root_group_type` is the minimal config item type for the root group.
- `struct configfs_subsystem iio_configfs_subsys` is exported for other IIO modules to attach subgroups.
- `iio_configfs_init()` initializes the root group and registers the subsystem.
- `iio_configfs_exit()` unregisters the subsystem.

## Control flow
At module init, the root group is initialized with name `iio` and registered with configfs. On module exit, it is unregistered. The file itself does not create device instances or attributes; it only provides the shared root.

## State and persistence behavior
The only state is configfs subsystem registration and the root group object. Configfs directories are runtime kernel/user configuration state and disappear when the module is unloaded or the subsystem is unregistered.

## Dependencies and integration points
The file depends on the configfs core and exports `iio_configfs_subsys` to `industrialio-sw-device.c` and `industrialio-sw-trigger.c`. Those modules register `devices` and `triggers` default groups beneath this root.

## Risks
- Software device and trigger modules depend on this subsystem being initialized before they register their groups.
- The root group has no custom operations, so all behavior comes from child groups; regressions tend to be ordering or module-lifetime issues rather than data-path bugs.

## Test signals
- Build with IIO configfs and verify `/sys/kernel/config/iio` appears after module load.
- Load and unload software device/trigger modules around the root module to check registration ordering.
- Confirm exported symbol users can register default groups and cleanup without dangling configfs entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/industrialio-configfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/industrialio-core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/industrialio-core.c

## Purpose
`industrialio-core.c` is the central IIO bus, device, sysfs, debugfs, character-device, ioctl, timestamp, and registration implementation. It allocates `iio_dev` objects, assigns stable numeric IDs, formats and parses IIO ABI values, builds channel attributes from `iio_chan_spec`, registers event and buffer support, exposes `/dev/iio:deviceN`, and tears devices down safely while file descriptors may still exist.

## Important APIs, types, and functions
- `iio_bus_type`, `iio_devt`, `iio_ida`, and `iio_debugfs_dentry` are the global bus, char-device number space, ID allocator, and debugfs root.
- Naming tables map channel types, modifiers, info masks, directions, clocks, and event-independent channel ABI pieces to sysfs names.
- `iio_device_alloc()`, `devm_iio_device_alloc()`, `iio_device_free()`, `__iio_device_register()`, `iio_device_unregister()`, and `__devm_iio_device_register()` are the core lifetime APIs.
- `iio_format_value()` and `iio_str_to_fixpoint()` implement common fixed-point sysfs ABI conversion.
- `iio_read_channel_info()`, `iio_write_channel_info()`, `iio_read_channel_info_avail()`, and ext-info helpers dispatch channel sysfs operations to driver `iio_info` callbacks.
- `__iio_add_chan_devattr()` and `iio_device_add_channel_sysfs()` dynamically create channel attributes from info masks, labels, ext_info, shared scopes, modifiers, differential channels, and indexed channels.
- `iio_device_register_sysfs_group()` appends attribute groups to the device group list consumed by `device_add`.
- `iio_chrdev_open()`, `iio_chrdev_release()`, `iio_ioctl()`, and the buffer/event file operation tables multiplex legacy buffer/event ioctls and reads through registered ioctl handlers.
- `iio_device_set_clock()`, `iio_device_get_clock()`, and `iio_get_time_ns()` own timestamp clock selection and timestamp reads.
- `iio_active_scan_mask_index()` helps drivers identify the active scan mask in `available_scan_masks`.

## Control flow
`subsys_initcall(iio_init)` registers the IIO bus, allocates up to 256 char-device minors, and creates the debugfs root. `iio_device_alloc()` allocates the opaque object plus optional driver private storage, assigns an ID, initializes locks and lists, names the device `iio:deviceN`, and initializes the embedded `struct device`.

Device registration first validates that `indio_dev->info` exists, records the owning module, sets the firmware node, reads an optional `label`, checks duplicate scan indexes and `read_label` versus `extend_name`, registers debugfs, creates buffer sysfs and masks, sanity-checks available scan masks, creates channel sysfs, registers event sysfs, registers trigger consumer sysfs when needed, installs noop setup ops for buffered devices that omitted setup ops, chooses buffer or event file operations for the cdev, assigns device groups, and calls `cdev_device_add()`.

Channel sysfs creation walks every `iio_chan_spec`. It builds names based on direction, type, index, differential endpoints, modifier, `extend_name`, and shared scope. Reads dispatch to `read_raw_multi()` or `read_raw()` and format according to the returned `IIO_VAL_*` type. Writes parse according to optional `write_raw_get_fmt()` and call `write_raw()`. Available values use `read_avail()` and list/range formatting. Labels come from `read_label()` or `extend_name`.

Unregistration removes the cdev/device, enters `info_exist_lock`, removes debugfs, disables all buffers, sets `indio_dev->info = NULL`, wakes event and buffer waiters, then frees buffer sysfs and masks. Final object release unregisters trigger consumers and event/sysfs resources, detaches buffers, destroys locks, frees the ID, and frees the opaque allocation.

## State and persistence behavior
All state is runtime kernel state: allocated IDs, sysfs group arrays, channel attribute lists, device locks, current mode, clock ID, char-device busy bits, ioctl handler list, debugfs cached register address, and buffer/event registrations. No state persists across unload or reboot. Timestamp clock changes are rejected while events or buffers are enabled, preventing live ABI clock switches.

## Dependencies and integration points
The core integrates with the Linux device model, bus registration, cdevs, sysfs, debugfs, anon-inode driven buffer/event helpers, firmware-node properties, IIO buffer/event/trigger modules, driver-provided `struct iio_info`, channel metadata, lockdep keys, and devm actions.

## Risks
- Dynamic sysfs name construction is broad; invalid channel metadata can create duplicate names, impossible differential names, or out-of-range table accesses.
- Open character devices can outlive unregister; `info_exist_lock` and `indio_dev->info = NULL` are central to avoiding use-after-unregister.
- `available_scan_masks` handling has known limitations for multi-long masks and warns rather than fully supporting every pattern.
- `iio_write_channel_info()` fixed-point parsing depends on `write_raw_get_fmt()`; wrong format declarations can silently pass wrong integer/fraction pairs to drivers.
- `iio_device_unregister()` frees only part of registration state immediately; final cleanup is split with device release, so ordering with open fds matters.

## Test signals
- Core registration tests should cover devices with no buffers/events, event-only devices, buffered devices, labels, ext_info, available values, shared attributes, differential channels, and duplicate scan-index rejection.
- ABI tests should verify formatting/parsing for all common `IIO_VAL_*` forms, including negative fractional values, dB suffixes, chars, 64-bit values, lists, and ranges.
- Lifetime tests should open `/dev/iio:deviceN`, unregister the device, and verify reads/ioctls return `-ENODEV` without hangs or use-after-free.
- Timestamp tests should cover all accepted clock names and `-EBUSY` while buffers/events are enabled.
- Debugfs tests should check direct register read/write behavior and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/industrialio-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/industrialio-event.c -->
# sources/distributed-fs/ceph-client/drivers/iio/industrialio-event.c

## Purpose
`industrialio-event.c` implements IIO event delivery and event-control sysfs. It lets drivers expose event enable/value/label attributes derived from channel event specs, queue detected events into a small FIFO, and provide userspace an event-only anon fd via `IIO_GET_EVENT_FD_IOCTL`.

## Important APIs, types, and functions
- `struct iio_event_interface` stores the event waitqueue, 16-entry `kfifo` of `struct iio_event_data`, dynamic sysfs attribute list, busy flag, sysfs group, read lock, and ioctl handler.
- `iio_push_event()` queues an event and wakes pollers when the event fd is open.
- `iio_event_getfd()` returns an anon inode for event reads, enforces a single open event fd, and resets the FIFO output side on successful open.
- `iio_event_chrdev_read()` performs blocking or nonblocking reads from the event FIFO.
- `iio_ev_state_show/store()` call driver `read_event_config` and `write_event_config`.
- `iio_ev_value_show/store()` call driver `read_event_value` and `write_event_value` with fixed-point formatting/parsing.
- `iio_device_add_event()` and `iio_device_add_event_sysfs()` build event attributes from `iio_event_spec` masks and shared scopes.
- `iio_device_register_eventset()`, `iio_device_wakeup_eventset()`, and `iio_device_unregister_eventset()` manage event subsystem lifetime for an IIO device.

## Control flow
During IIO device registration, the core calls `iio_device_register_eventset()`. If static `event_attrs` exist or any channel has event specs, the function allocates an event interface, initializes the FIFO/waitqueue/read lock, builds dynamic event sysfs attributes for every channel event spec, creates the `events` sysfs group, and registers an ioctl handler. Userspace first opens the normal IIO cdev and issues `IIO_GET_EVENT_FD_IOCTL`; the handler calls `iio_event_getfd()`, which takes `mlock`, sets the busy bit, takes an IIO device reference, creates an anon read-only fd, and resets FIFO output.

Drivers call `iio_push_event()` with an event code and timestamp. Events are silently ignored before registration or when no event fd is open. Reads block until the FIFO contains data or the device is unregistered; poll reports readable when the FIFO is non-empty. Release clears the busy bit and drops the device reference.

Event sysfs names are generated from event type, direction, and info kind, for example threshold rising enable/value names. Enable attributes use config callbacks; all other event info attributes use event value callbacks. Optional event labels use `read_event_label`.

## State and persistence behavior
The event interface is runtime-only. It contains queued event data, the single-open busy bit, dynamic attribute memory, and read serialization. Event enable/value state lives in the hardware or driver state behind the `iio_info` callbacks. Unregister wakes blocked readers so they return `-ENODEV`.

## Dependencies and integration points
This file integrates with the IIO core ioctl handler list, channel event specs, `iio_format_value()`, `iio_str_to_fixpoint()`, anon inodes, `kfifo`, wait queues, sysfs group creation, and driver event callbacks. It depends on core lifetime conventions around `indio_dev->info`.

## Risks
- The FIFO holds only 16 events; `iio_push_event()` drops events silently when full because it only checks whether `kfifo_put()` copied.
- The comment requires callers to avoid concurrent `iio_push_event()` for the same device; drivers must serialize event producers.
- A single event fd is allowed. Userspace expecting multiple independent readers gets `-EBUSY`.
- Event value writes always parse with micro precision; drivers needing different precision must account for that ABI behavior.
- Dynamic event attribute creation relies on valid event type/direction/info enum values and channel metadata.

## Test signals
- Sysfs tests should cover dynamic event attribute names for separate and shared masks, optional labels, enable config callbacks, value callbacks, and invalid callback absence.
- Event fd tests should cover ioctl fd creation, second-open `-EBUSY`, nonblocking empty reads, blocking wakeup, poll, FIFO reset on open, FIFO overflow behavior, and unregister wakeup.
- Driver integration tests should push events before registration, without an event fd, and with an event fd to verify discard versus delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/industrialio-event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/industrialio-gts-helper.c -->
# sources/distributed-fs/ceph-client/drivers/iio/industrialio-gts-helper.c

## Purpose
`industrialio-gts-helper.c` provides gain-time-scale conversion helpers, mainly for IIO light sensors whose scale is a function of hardware gain and integration time. It initializes a descriptor from gain/time selector tables, precomputes available scale/time lists for `read_avail`, converts between total gain and scale, finds selectors for requested scales, and computes gain compensation when integration time changes.

## Important APIs, types, and functions
- `struct iio_gts` is populated with max linear scale, hardware gain table, integration-time table, generated per-time scale tables, all-scale table, and available-time table.
- `devm_iio_init_iio_gts()` initializes the descriptor, validates inputs, builds availability tables, and registers devm cleanup.
- `iio_gts_total_gain_to_scale()`, `iio_gts_get_total_gain()`, and `iio_gts_get_scale()` convert between gain/time combinations and IIO scale values.
- `iio_gts_all_avail_scales()`, `iio_gts_avail_scales_for_time()`, and `iio_gts_avail_times()` return `read_avail`-compatible arrays and types.
- `iio_gts_find_sel_by_gain()`, `iio_gts_find_gain_by_sel()`, `iio_gts_get_min_gain()`, and `iio_find_closest_gain_low()` query gain tables.
- `iio_gts_find_gain_sel_for_scale_using_time()` and `iio_gts_find_gain_time_sel_for_scale()` resolve requested scale values to selectors.
- `iio_gts_find_new_gain_sel_by_old_gain_time()`, `iio_gts_find_new_gain_by_old_gain_time()`, and `iio_gts_find_new_gain_by_gain_time_min()` compute gain changes to preserve or approximate scale across integration-time changes.

## Control flow
Initialization linearizes the maximum scale into a nanounit-based integer, records gain and integration-time tables, checks that gains/selectors/time multipliers are nonnegative and nonzero where required, and validates that gain multiplied by integration-time multiplier does not overflow `int`. It then allocates per-time scale tables, computes total gains for every time/gain combination, sorts gain-derived scales, creates one combined unique sorted all-scale table, and builds a sorted integration-time table formatted as `IIO_VAL_INT_PLUS_MICRO`.

Lookup helpers linearize requested scale values, derive total gain as `max_scale / scale`, divide by known time multiplier or gain, require exact divisibility for exact-match helpers, and validate the resulting gain against the hardware table. Compensation helpers compute the old scale from old gain/time and then solve for a new gain under the new time. The `_min` variant falls back to closest lower supported gain and then minimum gain to avoid saturation.

## State and persistence behavior
The helper stores only generated lookup tables in memory. `devm_iio_init_iio_gts()` binds those allocations to the caller device lifetime through `devm_add_action_or_reset()`. It does not touch hardware; drivers use returned selectors to update their own device registers.

## Dependencies and integration points
The file depends on Linux integer overflow helpers, sorting, slab allocation, unit constants, IIO value types, and the public `iio-gts-helper.h` API. It is exported in namespace `IIO_GTS_HELPER`, so users must import that namespace.

## Risks
- Exact-match helpers require total gain to divide cleanly by known gain/time. Users expecting nearest-match behavior must call the explicit closest/lower helper path.
- Scale linearization divides nanoseconds by the selected scaler; unsupported scaler values return errors and fractional precision can be lost.
- `iio_gts_get_min_gain()` uses a local variable named `min`; it relies on macro expansion context and should be watched when refactoring.
- Availability table generation assumes sorted/preferred integration-time semantics for search order but also sorts displayed values; driver documentation should make policy clear.
- Large gain/time tables can fail allocation or overflow computed table sizes.

## Test signals
- Unit-style tests should cover initialization rejection for empty tables, negative selectors, zero gain/time multiplier, and multiplication overflow.
- Conversion tests should cover gain-to-scale, scale-to-gain selector, exact and non-exact scale requests, duplicate integration times, duplicate scales across time/gain pairs, and all exported availability helpers.
- Compensation tests should verify exact preservation, in-range lower fallback, out-of-range minimum fallback, and selector-versus-time variants.
- Build tests should verify namespace imports for module users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/industrialio-gts-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/industrialio-sw-device.c -->
# sources/distributed-fs/ceph-client/drivers/iio/industrialio-sw-device.c

## Purpose
`industrialio-sw-device.c` implements configfs support for software-created IIO devices. It lets software device type providers register a named type under `iio/devices`, and lets userspace instantiate or remove devices by creating or deleting configfs groups under that type.

## Important APIs, types, and functions
- `iio_devices_group` is the configfs default group registered under the exported IIO configfs subsystem.
- `iio_device_types_list` and `iio_device_types_lock` track registered `struct iio_sw_device_type` providers.
- `iio_register_sw_device_type()` inserts a unique provider type and creates its default configfs group.
- `iio_unregister_sw_device_type()` removes the provider from the list and unregisters its configfs group.
- `iio_sw_device_create()` resolves a type, obtains its owner module, calls provider `ops->probe(name)`, and records the device type on success.
- `iio_sw_device_destroy()` calls provider `ops->remove()` and drops the module reference.
- `device_make_group()` and `device_drop_group()` are configfs group operations for instance creation/destruction.

## Control flow
At module init, the file registers an `iio/devices` default group. Provider modules call `iio_register_sw_device_type()` with a name, owner, and probe/remove ops. Registration rejects duplicate names under lock, appends the type to the global list, then creates a child group named after the type. Userspace creates a group below that type; configfs calls `device_make_group()`, which probes a new software device and names the returned config group. Removing the configfs item calls `device_drop_group()`, which destroys the software device and drops the config item reference.

## State and persistence behavior
State is runtime-only: registered type list, provider configfs groups, instantiated software device config groups, and provider module references while instances exist. Device-specific state is owned by provider probe/remove implementations. Configfs hierarchy contents are not persistent across reboot unless userspace recreates them.

## Dependencies and integration points
The file depends on configfs, the exported `iio_configfs_subsys`, module reference counting, and provider implementations of `struct iio_sw_device_type`. It is the generic bridge between userspace configfs operations and software IIO device providers.

## Risks
- If `configfs_register_default_group()` fails in `iio_register_sw_device_type()`, this file returns the error but does not remove the just-added device type from the list. That can leave a registered type without a configfs group.
- `__iio_find_sw_device_type()` accepts a `len` argument but ignores it, so callers rely entirely on null-terminated names.
- Provider `probe()` must initialize `d->group` correctly before returning; configfs instance creation assumes it can name and return that group.
- Provider remove paths run from configfs item teardown and must tolerate userspace-driven lifetime ordering.

## Test signals
- Configfs tests should verify `iio/devices` appears, type registration creates a child group, duplicate registration returns `-EBUSY`, and unregister removes the group.
- Instance tests should create and delete configfs groups, verify provider probe/remove calls, and check module references around active instances.
- Failure injection should cover provider probe failure and default-group registration failure to detect stale list entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/industrialio-sw-device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/industrialio-sw-trigger.c -->
# sources/distributed-fs/ceph-client/drivers/iio/industrialio-sw-trigger.c

## Purpose
`industrialio-sw-trigger.c` implements configfs support for software-created IIO triggers. Trigger type providers register named types under `iio/triggers`, and userspace creates trigger instances by creating configfs groups below a type.

## Important APIs, types, and functions
- `iio_triggers_group` is the configfs default group registered under `iio`.
- `iio_trigger_types_list` and `iio_trigger_types_lock` track registered `struct iio_sw_trigger_type` providers.
- `iio_register_sw_trigger_type()` adds a unique type and creates the corresponding configfs default group, rolling back the list insertion on configfs failure.
- `iio_unregister_sw_trigger_type()` removes the type from the list and unregisters its group.
- `iio_sw_trigger_create()` obtains the provider module, calls `ops->probe(name)`, and stores the type on the returned trigger.
- `iio_sw_trigger_destroy()` calls provider `ops->remove()` and drops the module reference.
- `trigger_make_group()` and `trigger_drop_group()` connect configfs mkdir/rmdir to trigger create/destroy.

## Control flow
At module init, `iio_sw_trigger_init()` registers an `iio/triggers` default group under the shared IIO configfs subsystem. Providers register trigger types; each type appears as a child directory. When userspace creates an instance group below a type, configfs calls `trigger_make_group()`, which creates a trigger via the provider and returns its config group. Removing the configfs item calls `trigger_drop_group()`, which destroys the trigger and releases the item.

## State and persistence behavior
Runtime state consists of the registered trigger type list, configfs type groups, active trigger instance groups, and provider module references while instances exist. Actual trigger device state is provider-owned. Configfs-created instances disappear on removal/unload and are not persisted by this file.

## Dependencies and integration points
The file depends on configfs, `iio_configfs_subsys`, software trigger provider APIs, module reference counting, and provider implementations that usually register actual `struct iio_trigger` objects with the trigger core.

## Risks
- Provider probe/remove must correctly initialize and tear down both configfs group state and trigger-core state; this wrapper does not validate those details.
- The find helper ignores its `len` argument, matching by full string compare.
- Userspace controls instance names through configfs; providers must validate names if they map to hardware-meaningful resources.
- Type unregister while instances exist depends on configfs/provider lifetime correctness.

## Test signals
- Configfs tests should verify `iio/triggers`, type registration/unregistration, duplicate type rejection, and rollback when default-group creation fails.
- Instance tests should create/delete software triggers, verify provider probe/remove and module references, and check that trigger core registration is cleaned up.
- Negative tests should try invalid type names and provider probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/industrialio-sw-trigger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/industrialio-trigger.c -->
# sources/distributed-fs/ceph-client/drivers/iio/industrialio-trigger.c

## Purpose
`industrialio-trigger.c` implements IIO trigger devices and trigger consumers. It registers triggers on the IIO bus, exposes trigger names and per-device `trigger/current_trigger`, allocates per-trigger synthetic IRQs for poll functions, dispatches trigger polls to consumers, handles trigger attachment/detachment, provides pollfunc allocation helpers, and supports immutable/own-device trigger validation.

## Important APIs, types, and functions
- `iio_trigger_ida`, `iio_trigger_list`, and `iio_trigger_list_lock` maintain registered trigger IDs and global name lookup.
- `iio_trigger_register()` and `iio_trigger_unregister()` add/remove trigger devices and global list entries.
- `iio_trigger_set_immutable()` assigns a read-only trigger to an IIO device.
- `iio_trigger_poll()` and `iio_trigger_poll_nested()` dispatch hard-IRQ or nested-thread trigger events to enabled synthetic sub-IRQs.
- `iio_trigger_notify_done()` and the atomic variant decrement `use_count` and reenable the trigger when all consumers finish.
- `iio_trigger_attach_poll_func()` allocates a sub-IRQ, requests a threaded IRQ for an `iio_poll_func`, enables the hardware trigger on first user, and records own-device attachment.
- `iio_trigger_detach_poll_func()` disables the trigger on last user, frees IRQ state, and drops the consumer module reference.
- `iio_alloc_pollfunc()`, `iio_dealloc_pollfunc()`, and `iio_pollfunc_store_time()` support triggered buffer/event handlers.
- `current_trigger_show/store()` implements trigger selection by name.
- `__iio_trigger_alloc()`, `__devm_iio_trigger_alloc()`, `iio_trigger_free()`, and `devm_iio_trigger_register()` manage trigger object lifetime.
- `iio_device_suspend_triggering()` and `_resume_triggering()` disable/enable an attached pollfunc IRQ.

## Control flow
Trigger allocation reserves `CONFIG_IIO_CONSUMERS_PER_TRIGGER` IRQ descriptors, initializes a simple irq_chip whose mask/unmask callbacks toggle per-subirq `enabled`, formats a trigger name, initializes the embedded device, and returns the trigger. Registration assigns an ID, names the device `triggerN`, adds it to the device model, rejects duplicate trigger names under the global list lock, and appends it to the available-trigger list.

Consumers get a `trigger/current_trigger` sysfs group when registered with triggered modes. A store refuses changes while the device is in triggered buffer mode or the trigger is immutable, resolves the trigger by name, validates it through both consumer and trigger callbacks, swaps `indio_dev->trig`, detaches event pollfuncs from the old trigger when needed, and attaches event pollfuncs to the new trigger when needed.

When a trigger fires, `iio_trigger_poll()` or `_nested()` sets `use_count` to the configured maximum and dispatches each enabled synthetic IRQ. Disabled sub-IRQs immediately notify done. Poll functions call `iio_trigger_notify_done()` when finished; when the count reaches zero, the trigger reenable callback runs directly or through work depending on context.

## State and persistence behavior
State is in-memory: trigger ID, device object, global list membership, trigger name, sub-IRQ descriptors, sub-IRQ enabled flags, IRQ pool bitmap, use count, attached own-device flag, consumer `indio_dev->trig` reference, and optional readonly flag in the consumer opaque state. There is no persistent configuration except userspace can reselect triggers at runtime through sysfs.

## Dependencies and integration points
The file integrates with the IIO core bus, Linux IRQ subsystem, device model, module reference counting, sysfs, IIO buffer enable paths, triggered event setup, and driver-provided trigger ops such as `set_trigger_state`, `reenable`, and `validate_device`.

## Risks
- `iio_trigger_poll()` sets `use_count` to `CONFIG_IIO_CONSUMERS_PER_TRIGGER`, not the actual number of active consumers; every disabled sub-IRQ must notify done to avoid stuck triggers.
- Reenable can race with removal or disabled hardware state; comments rely on drivers not blindly reenabling after state is off.
- `current_trigger_store()` checks current mode under `mlock` but performs lookup and assignment after the scoped lock block; concurrent mode changes need scrutiny.
- Attach/detach module references protect the consumer driver while attached, but errors in request/free IRQ paths can leak if ordering changes.
- Duplicate trigger names are detected after `device_add()`, requiring correct cleanup of both device and ID.

## Test signals
- Trigger registration tests should cover duplicate names, ID allocation/free, device release freeing IRQ descriptors, and devm register/unregister.
- Consumer tests should cover trigger selection, readonly triggers, validation callback failures, own-device validation, event pollfunc attach/detach, and busy rejection while triggered buffer mode is active.
- Polling tests should simulate enabled and disabled sub-IRQs, hard IRQ and nested paths, notify-done reenable behavior, and removal races.
- Suspend/resume tests should verify IRQ disable/enable only when a pollfunc IRQ is attached.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/industrialio-trigger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/industrialio-triggered-event.c -->
# sources/distributed-fs/ceph-client/drivers/iio/industrialio-triggered-event.c

## Purpose
`industrialio-triggered-event.c` is a small helper for drivers that generate IIO events from a trigger-driven poll function. It allocates `indio_dev->pollfunc_event` and marks the IIO device as supporting triggered events.

## Important APIs, types, and functions
- `iio_triggered_event_setup()` allocates a pollfunc using `iio_alloc_pollfunc()` with `IRQF_ONESHOT`, names it from the IIO device name and ID, stores it in `indio_dev->pollfunc_event`, and sets `INDIO_EVENT_TRIGGERED`.
- `iio_triggered_event_cleanup()` clears `INDIO_EVENT_TRIGGERED` and frees the pollfunc with `iio_dealloc_pollfunc()`.

## Control flow
Drivers call setup after fully initializing `indio_dev` but before registration. During later trigger selection in `industrialio-trigger.c`, devices with `INDIO_EVENT_TRIGGERED` attach `pollfunc_event` to the selected trigger. On driver cleanup, the driver calls `iio_triggered_event_cleanup()` to free the allocated pollfunc and clear the mode bit.

## State and persistence behavior
The helper mutates only `indio_dev->pollfunc_event` and `indio_dev->modes`. It has no hardware or persistent state. The allocated pollfunc owns a formatted name string and callback pointers until cleanup.

## Dependencies and integration points
The file depends on IIO trigger consumer helpers, trigger-core pollfunc allocation, and drivers that push events from their pollfunc thread or top half. It integrates with trigger selection through `INDIO_EVENT_TRIGGERED`.

## Risks
- Cleanup assumes setup succeeded and `pollfunc_event` is valid; drivers should pair calls carefully.
- Calling setup before `indio_dev->name` or ID is meaningful would produce poor pollfunc names, though the function expects a completely initialized unregistered device.
- The helper does not attach to a trigger itself; drivers still need normal IIO registration and trigger selection.

## Test signals
- Driver probe/remove tests should verify setup failure on allocation, mode bit set/cleared, and no pollfunc leak.
- Integration tests should select a trigger on a triggered-event device and confirm event pollfunc attach/detach through the trigger core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/industrialio-triggered-event.c -->
