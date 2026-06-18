# Research: subset-b-005588

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_ring.c -->
## sources/distributed-fs/ceph-client/drivers/virtio/virtio_ring.c

Purpose: this is the generic Linux virtio vring implementation used by virtio transports and drivers to create, populate, notify, consume, resize, reset, and destroy virtqueues. It supports split rings, packed rings, and the `VIRTIO_F_IN_ORDER` variants through `enum vq_layout` and four `struct virtqueue_ops` tables.

Important APIs, types, and functions: the main state carrier is `struct vring_virtqueue`, wrapping the public `struct virtqueue` plus layout-specific `split` or `packed` ring state. Split-ring state is in `struct vring_virtqueue_split` with descriptor state/extra arrays, DMA address, flags shadows, and avail index. Packed-ring state is in `struct vring_virtqueue_packed` with descriptor/event areas, wrap counters, next available index, flags shadows, and DMA addresses. Exported APIs include `virtqueue_add_sgs()`, `virtqueue_add_outbuf()`, `virtqueue_add_inbuf()`, `virtqueue_get_buf_ctx()`, `virtqueue_kick_prepare()`, `virtqueue_notify()`, `virtqueue_disable_cb()`, `virtqueue_enable_cb*()`, `vring_interrupt()`, `vring_create_virtqueue*()`, `vring_new_virtqueue()`, `vring_del_virtqueue()`, `virtqueue_resize()`, `virtqueue_reset()`, `vring_transport_features()`, DMA address getters, and `virtqueue_map_*()` helpers.

Control flow: queue creation chooses packed or split based on `VIRTIO_F_RING_PACKED`, allocates coherent ring memory when it owns the ring, allocates descriptor metadata, initializes indices/flags, and links the queue onto `vdev->vqs`. Add paths map scatterlist entries, optionally build indirect descriptors, publish descriptors before making the first descriptor or avail index visible with virtio memory barriers, and track `num_added` until a kick decision. Used-buffer paths poll device-visible indices/flags, validate descriptor IDs, detach descriptor chains, unmap DMA, return the driver token and optional context, and update used-event state. Interrupt flow calls `more_used()`, handles hardened early notifications, records an event hint, and invokes the queue callback. Resize/reset first uses transport hooks to disable/reset the queue, recycles unused buffers, rebuilds or reinitializes ring state, then re-enables the queue.

State and persistence behavior: all state is in memory and is per-virtqueue. Descriptor ownership is represented by `vq.num_free`, `free_head`, descriptor state data pointers, packed wrap counters, split avail/used shadows, and `broken`. DMA mappings are stored in `vring_desc_extra` so detach paths can unmap exactly what was exposed. No persistent storage exists; recovery is through reset, break/unbreak, and transport-level queue lifecycle.

Dependencies and integration points: this file integrates with virtio core feature negotiation, transport `virtio_config_ops`, DMA mapping or custom `vdev->map`, KMSAN DMA annotations, Xen DMA quirk handling, Linux scatterlist APIs, and exported GPL symbols consumed by virtio drivers and transports such as virtio-vdpa.

Risks: correctness depends on memory barriers around descriptor publication and event suppression, precise DMA mapping/unmapping for direct and indirect descriptors, and caller serialization for most queue operations. Premapped buffers rely on callers providing valid DMA addresses and lengths. Packed-ring wrap counter bugs can silently corrupt queue progress. The reset/resize path is only valid for queues owned by this implementation and transports implementing disable/enable hooks.

Test signals: useful checks include split and packed ring I/O, indirect descriptor fallback, in-order feature combinations, event-index interrupt suppression, callback race tests using `enable_cb_prepare()` plus `poll()`, DMA API and custom map paths, queue reset/resize with buffer recycling, hardened notification-before-DRIVER_OK behavior, and transport feature filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_rtc_arm.c -->
## sources/distributed-fs/ceph-client/drivers/virtio/virtio_rtc_arm.c

Purpose: this Arm-specific companion supplies hardware cross-timestamp parameters for virtio RTC PTP support.

Important APIs/types/functions: it implements `viortc_hw_xtstamp_params(u8 *hw_counter, enum clocksource_ids *cs_id)`, returning `VIRTIO_RTC_COUNTER_ARM_VCT` and `CSID_ARM_ARCH_COUNTER`.

Control flow: PTP registration or cross-timestamp operations call this symbol when available. It has no branching and simply reports that the Arm virtual counter should be requested from the virtio RTC device and correlated with Linux's Arm architected clocksource.

State and persistence behavior: no state is stored. The function writes through caller-provided pointers only.

Dependencies and integration points: it depends on `linux/clocksource_ids.h`, `uapi/linux/virtio_rtc.h`, and the internal virtio RTC header. It overrides the weak fallback in `virtio_rtc_ptp.c`, which returns `-EOPNOTSUPP` on platforms without a hardware-specific implementation.

Risks: platform correctness depends on the running system actually using the Arm architected counter as the clocksource when cross timestamps are requested. Mismatches are rejected later by `ktime_get_snapshot()` checks in the PTP code.

Test signals: build with Arm virtio RTC PTP support, verify `getcrosststamp` is advertised only when the device supports `VIRTIO_RTC_COUNTER_ARM_VCT`, and verify it returns `-EOPNOTSUPP` if the active clocksource ID differs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_rtc_arm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_rtc_class.c -->
## sources/distributed-fs/ceph-client/drivers/virtio/virtio_rtc_class.c

Purpose: this file exposes one suitable virtio RTC clock as a Linux RTC class device, translating RTC operations into virtio RTC request helpers.

Important APIs/types/functions: `struct viortc_class` stores the backing `viortc_dev`, `rtc_device`, virtio clock ID, and a `stopped` flag protected by `rtc_lock()`. RTC operations are `viortc_class_read_time()`, `viortc_class_read_alarm()`, `viortc_class_set_alarm()`, and `viortc_class_alarm_irq_enable()`. Integration helpers are `viortc_class_init()`, `viortc_class_register()`, `viortc_class_stop()`, and `viortc_class_alarm()`.

Control flow: RTC reads call `viortc_read()` and convert nanoseconds to `rtc_time`. Alarm reads and writes call `viortc_read_alarm()`, `viortc_set_alarm()`, and `viortc_set_alarm_enabled()`, converting between seconds and nanoseconds with overflow checks. Alarm notifications from the core call `viortc_class_alarm()`, which verifies the clock ID and reports `RTC_AF | RTC_IRQF` through `rtc_update_irq()`. Removal calls `viortc_class_stop()` to reject subsequent RTC ops with `-EBUSY`.

State and persistence behavior: state is devm-managed and tied to the virtio device. Alarm state and clock readings live in the virtio device, not in this wrapper. The `stopped` bit is local runtime state used to guard teardown.

Dependencies and integration points: integrates with Linux RTC class APIs, time conversion helpers, overflow helpers, and virtio RTC core request functions declared in `virtio_rtc_internal.h`.

Risks: only whole-second RTC values are exposed, so subsecond precision from virtio RTC is discarded. Alarm setting rejects negative or overflowing times. Stale notifications for a non-registered clock are ignored with a warning.

Test signals: test RTC reads, alarm read/set/enable flows, alarm notification delivery, teardown racing with RTC ops, and configuration without alarm support where `RTC_FEATURE_ALARM` is cleared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_rtc_class.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_rtc_driver.c -->
## sources/distributed-fs/ceph-client/drivers/virtio/virtio_rtc_driver.c

Purpose: this is the virtio RTC core driver. It negotiates virtio clock devices, owns request and alarm virtqueues, implements typed virtio RTC request wrappers, registers RTC/PTP user-facing clocks, and handles suspend/resume and removal.

Important APIs/types/functions: `struct viortc_dev` stores `virtio_device`, optional RTC class wrapper, virtqueues, PTP handles, alarm buffers, and clock count. `struct viortc_msg` represents one request/response transaction with devm buffers, a completion, response length, and a two-reference lifetime model. Public internal helpers include `viortc_read()`, `viortc_read_cross()`, `viortc_cross_cap()`, `viortc_read_alarm()`, `viortc_set_alarm()`, and `viortc_set_alarm_enabled()`. Probe/remove and PM hooks are `viortc_probe()`, `viortc_remove()`, `viortc_freeze()`, and `viortc_restore()`.

Control flow: probe allocates device state, finds request and optional alarm queues, marks the device ready, requests configuration, enumerates each clock, and registers RTC/PTP representations where supported. Request helpers allocate a message, populate little-endian fields through macros, add request/response scatterlists to the request queue, kick the device, wait for completion with optional timeout, validate response status and size, extract fields, and drop the caller reference. Alarm queue callbacks validate notification headers, dispatch valid alarm notifications to the RTC class wrapper, requeue the buffer, and notify the device if needed.

State and persistence behavior: all allocations are device-managed. Request messages survive timeout by retaining the callback reference until a late response or device cleanup. Clock exposure state is kept in `viortc_class` and `clocks_to_unregister`; removal unregisters PTP clocks and stops RTC ops before resetting the virtio device.

Dependencies and integration points: depends on virtio core, virtqueue APIs, `uapi/linux/virtio_rtc.h`, RTC class support, PTP support, and optional alarm feature negotiation through `VIRTIO_RTC_F_ALARM`.

Risks: request timeouts leave messages for late callback release, so refcount correctness is critical. `viortc_restore()` assumes alarm queue indexes only when alarms are supported and must be exercised in non-alarm configurations. Response validation rejects any short or over/under-sized response, making spec conformance important.

Test signals: probe devices with zero, one, and multiple clocks; UTC-like RTC registration; PTP registration; alarm feature negotiation and notifications; request timeout/interrupt handling; suspend/resume with wake alarms; malformed response sizes/statuses; and remove during pending request.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_rtc_driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_rtc_internal.h -->
## sources/distributed-fs/ceph-client/drivers/virtio/virtio_rtc_internal.h

Purpose: this header defines the private interfaces shared by the virtio RTC core, RTC class wrapper, PTP wrapper, and architecture-specific cross-timestamp helpers.

Important APIs/types/functions: it forward-declares `struct viortc_dev`, `struct viortc_class`, and `struct viortc_ptp_clock`. It declares core request wrappers for reading clocks, cross timestamps, cross capabilities, and alarm operations. It declares RTC class functions and PTP register/unregister functions behind `IS_ENABLED()` guards, plus `viortc_hw_xtstamp_params()` for hardware-specific cross timestamp wiring.

Control flow: compilation selects real RTC/PTP helpers when `CONFIG_VIRTIO_RTC_CLASS` or `CONFIG_VIRTIO_RTC_PTP` are enabled, otherwise inline stubs return `-ENODEV`, `ERR_PTR(-ENODEV)`, or no-op behavior. This lets the core code call helpers conditionally while preserving build coverage across configurations.

State and persistence behavior: the header stores no state. It defines ownership contracts: the core owns `viortc_dev`; RTC/PTP wrappers receive it and parent devices, then return handles used during removal.

Dependencies and integration points: includes Linux device, error, PTP clock, and type headers. It is the internal join point between `virtio_rtc_driver.c`, `virtio_rtc_class.c`, `virtio_rtc_ptp.c`, and `virtio_rtc_arm.c`.

Risks: stub return values must match caller expectations. The PTP disabled `viortc_ptp_register()` returns `NULL`, not an error pointer, and the core treats this as "not registered." RTC disabled initialization returns `ERR_PTR(-ENODEV)`.

Test signals: build matrix coverage with RTC class enabled/disabled, PTP enabled/disabled, and architecture helper present/absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_rtc_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_rtc_ptp.c -->
## sources/distributed-fs/ceph-client/drivers/virtio/virtio_rtc_ptp.c

Purpose: this file exposes virtio RTC clocks as Linux PTP hardware clocks, including optional cross timestamp support when both platform and device support a compatible hardware counter.

Important APIs/types/functions: `struct viortc_ptp_clock` owns the registered `ptp_clock`, backing `viortc_dev`, `ptp_clock_info`, clock ID, and `have_cross`. `struct viortc_ptp_cross_ctx` carries a pre-fetched device time and system counter value into `get_device_system_crosststamp()`. Key functions are `viortc_ptp_register()`, `viortc_ptp_unregister()`, `viortc_ptp_gettimex64()`, `viortc_ptp_getcrosststamp()`, `viortc_ptp_do_xtstamp()`, and `viortc_ptp_get_cross_cap()`.

Control flow: registration allocates a PTP wrapper, copies a template `ptp_clock_info`, sets the name, queries platform cross-timestamp parameters, asks the virtio device whether that clock/counter pair supports cross timestamps, disables `.getcrosststamp` if unsupported, then registers the PTP clock. `gettimex64` brackets `viortc_read()` with `ptp_read_system_prets/postts`. `getcrosststamp` verifies the active clocksource ID, fetches the device/counter pair first because virtio access may be slow, then passes the captured values into `get_device_system_crosststamp()`.

State and persistence behavior: PTP state is devm allocated but explicitly freed only after successful `ptp_clock_unregister()`. Device time is read on demand; no time state is persisted.

Dependencies and integration points: integrates with Linux PTP clock APIs, clocksource snapshots, virtio RTC read/cross-cap requests, and optional arch helpers like `virtio_rtc_arm.c`.

Risks: cross timestamp accuracy depends on device-provided counter cycles matching the active Linux clocksource. Large nanosecond values above `KTIME_MAX`/`S64_MAX` are rejected. Time adjustment and set operations deliberately return `-EOPNOTSUPP`, so consumers must treat these as read-only PHCs.

Test signals: PTP registration, name truncation failure path, `gettimex64`, cross timestamp enabled/disabled paths, clocksource mismatch, unsupported platform helper, unregister on remove, and read values near overflow limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_rtc_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_vdpa.c -->
## sources/distributed-fs/ceph-client/drivers/virtio/virtio_vdpa.c

Purpose: this file is the bridge that registers vDPA devices as virtio devices and implements virtio config operations on top of `vdpa_config_ops`.

Important APIs/types/functions: `struct virtio_vdpa_device` embeds `struct virtio_device` and points to the backing `vdpa_device`. Config operations include config get/set, generation, status, reset, feature retrieval/finalization, queue creation/deletion, bus name, and queue affinity. Queue setup is centered on `virtio_vdpa_setup_vq()`, with notification through `kick_vq` or `kick_vq_with_data`.

Control flow: probe allocates a virtio-vdPA wrapper, selects the parent DMA device or vDPA device, fills `virtio_config_ops`, reads device/vendor IDs, registers the virtio device, and stores driver data. `find_vqs` builds optional affinity masks, creates each named virtqueue with `vring_create_virtqueue_map()`, installs callbacks into the vDPA device, programs queue size, descriptor/driver/device addresses, initial state, and ready bit, then installs the config callback. Removal unregisters the virtio device; queue deletion clears ready and deletes vrings.

State and persistence behavior: state is kernel-memory only and tied to virtio/vDPA device lifetime. Queue readiness and addresses are stored in the vDPA device via config ops; virtqueue memory/state is owned by virtio ring code.

Dependencies and integration points: depends on vDPA bus APIs, virtio core, virtio ring exported APIs, CPU affinity helpers, and optional custom DMA maps from the vDPA device.

Risks: feature negotiation must clear `VIRTIO_F_NOTIFICATION_DATA` when no data-kick op exists. Queue index accounting skips unnamed queues but still uses sequential vDPA queue indexes. Error unwind must leave queues not ready. Affinity mask generation can fail under memory pressure.

Test signals: probe with valid/zero device ID, split and packed queues, notification-data feature with and without `kick_vq_with_data`, queue ready failure unwind, queue state programming, affinity callback behavior, and virtio feature finalization with `vring_transport_features()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/virtio/virtio_vdpa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/w1/Kconfig

Purpose: this Kconfig file gates the Dallas/Maxim 1-Wire subsystem and its userspace connector option.

Important APIs/types/functions: it defines `menuconfig W1` as a tristate depending on `HAS_IOMEM`, and `config W1_CON` as an optional connector-backed userspace communication path depending on `CONNECTOR` and defaulting to enabled.

Control flow: enabling `W1` opens the menu and sources `drivers/w1/masters/Kconfig` and `drivers/w1/slaves/Kconfig`, so bus master and slave family drivers are only visible when core 1-Wire support is selected.

State and persistence behavior: no runtime state. Build-time selections determine whether `wire.o`, master drivers, slave drivers, and connector support are compiled.

Dependencies and integration points: integrates with kernel Kconfig and the w1 core Makefile. `W1_CON` aligns with `w1_netlink.c` and connector documentation.

Risks: `HAS_IOMEM` excludes systems without MMIO support even though some masters are USB/I2C; this is a broad subsystem-level dependency. Connector defaults to yes when possible, increasing default surface area.

Test signals: Kconfig matrix with `W1=y/m/n`, `CONNECTOR=y/n`, and representative master/slave selections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/Makefile -->
## sources/distributed-fs/ceph-client/drivers/w1/Makefile

Purpose: this Makefile builds the 1-Wire core and descends into master and slave driver directories.

Important APIs/types/functions: `obj-$(CONFIG_W1) += wire.o` builds the core module/object, and `wire-objs` is composed from `w1.o`, `w1_int.o`, `w1_family.o`, `w1_netlink.o`, and `w1_io.o`. `obj-y += masters/ slaves/` always visits subdirectories so their own config symbols decide what to build.

Control flow: Kbuild links the core pieces into `wire.o` when `CONFIG_W1` is enabled, while child Makefiles contribute selected bus master and slave drivers.

State and persistence behavior: no runtime state. It controls build graph composition only.

Dependencies and integration points: integrates Kbuild with Kconfig symbols from `drivers/w1/Kconfig`, master Kconfig, and slave Kconfig.

Risks: `w1_netlink.o` is part of `wire-objs` regardless of `W1_CON`, so correctness depends on source-level conditional compilation for connector-specific behavior.

Test signals: allmodconfig and minimal `W1=m` builds, plus configurations with no master/slave modules selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/masters/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/w1/masters/Kconfig

Purpose: this Kconfig menu defines selectable 1-Wire bus master drivers across platform, PCI, USB, I2C, GPIO, OMAP HDQ, SGI ASIC, and UART transports.

Important APIs/types/functions: symbols include `W1_MASTER_AMD_AXI`, `W1_MASTER_MATROX`, `W1_MASTER_DS2490`, `W1_MASTER_DS2482`, `W1_MASTER_MXC`, `W1_MASTER_GPIO`, `HDQ_MASTER_OMAP`, `W1_MASTER_SGI`, and `W1_MASTER_UART`.

Control flow: each symbol controls one object in the masters Makefile. Dependencies constrain selection to relevant subsystems, for example PCI for Matrox, USB for DS2490, I2C for DS2482, GPIOLIB for GPIO, SERIAL_DEV_BUS for UART, and architecture or `COMPILE_TEST` coverage for MXC/OMAP.

State and persistence behavior: no runtime state. Build-time choices determine which hardware adapters can register `struct w1_bus_master` instances.

Dependencies and integration points: integrates with platform drivers, subsystem buses, and the top-level w1 menu.

Risks: some help text contains legacy hardware names and limited detail about required device tree or board data. Build exposure through `COMPILE_TEST` helps compile coverage but cannot validate timing-sensitive 1-Wire bus behavior.

Test signals: Kconfig dependency checks for each transport and compile-test coverage for platform drivers on non-native architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/masters/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/masters/Makefile -->
## sources/distributed-fs/ceph-client/drivers/w1/masters/Makefile

Purpose: this Makefile maps 1-Wire master Kconfig symbols to their implementation objects.

Important APIs/types/functions: it builds `amd_axi_w1.o`, `matrox_w1.o`, `ds2490.o`, `ds2482.o`, `mxc_w1.o`, `w1-gpio.o`, `omap_hdq.o`, `sgi_w1.o`, and `w1-uart.o` according to their config symbols.

Control flow: Kbuild evaluates each `obj-$(CONFIG_...)` line and includes selected objects as built-in or modules matching the symbol's `y`/`m` value.

State and persistence behavior: no runtime state. Module names follow object names.

Dependencies and integration points: this file is reached from the parent w1 Makefile, with symbol definitions from `masters/Kconfig`.

Risks: object naming must remain synchronized with Kconfig help text and driver module declarations. Missing an object here would make a visible Kconfig option build nothing.

Test signals: build each master as module and built-in; verify expected module filenames match Kconfig help where documented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/masters/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/masters/amd_axi_w1.c -->
## sources/distributed-fs/ceph-client/drivers/w1/masters/amd_axi_w1.c

Purpose: this platform driver exposes the AMD AXI 1-Wire programmable logic IP core as a Linux 1-Wire bus master.

Important APIs/types/functions: `struct amd_axi_w1_local` stores MMIO base, IRQ, wait queue, atomic IRQ flag, and `struct w1_bus_master`. Bus callbacks are `amd_axi_w1_touch_bit()`, `amd_axi_w1_read_byte()`, `amd_axi_w1_write_byte()`, and `amd_axi_w1_reset_bus()`. Probe/remove are `amd_axi_w1_probe()` and `amd_axi_w1_remove()`, with interrupt handler `amd_axi_w1_irq()`.

Control flow: probe maps registers, obtains IRQ and clock, verifies the IP ID and major version, sets bus callbacks, resets the IP, and registers the w1 master. Each bus operation waits for READY, writes an instruction, asserts GO, waits for DONE via interrupt-enabled waits with timeout, reads data/status as needed, then clears GO. Reset also issues controller reset and checks the presence flag.

State and persistence behavior: runtime state is device-managed except the w1 master registration. The atomic flag records a pending IRQ and is cleared after waiters consume it. Hardware registers hold transient controller state.

Dependencies and integration points: depends on platform device resources, device tree compatible `amd,axi-1wire-host`, clock framework, MMIO, IRQs, and w1 core.

Risks: w1 callbacks cannot report rich errors, so timeout/interruption often returns inactive bus values. Busy loops rely on IRQ wakeups and 100 ms timeout. Version gating only accepts major version 1.

Test signals: probe with correct/incorrect IP ID and version, IRQ timeout paths, byte and bit transactions, reset/presence detection, clock enable failure, and w1 master unregister on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/masters/amd_axi_w1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/masters/ds2482.c -->
## sources/distributed-fs/ceph-client/drivers/w1/masters/ds2482.c

Purpose: this I2C driver exposes Maxim/Dallas DS2482/DS2484 I2C-to-1-Wire bridges as one or eight Linux w1 bus masters.

Important APIs/types/functions: `struct ds2482_data` holds the I2C client, access mutex, channel count, per-channel wrappers, cached channel/read pointer, and config byte. `struct ds2482_w1_chan` binds one DS2482 channel to a `w1_bus_master`. Key helpers include command send/read-pointer functions, `ds2482_wait_1wire_idle()`, `ds2482_set_channel()`, bus callbacks for touch bit, triplet, read/write byte, reset, and strong pullup.

Control flow: probe checks SMBus functionality, enables `vcc`, resets the chip, validates reset status, detects 8-channel devices by selecting channel 7, writes configuration, and registers one w1 master per channel. Each bus callback locks `access_lock`, waits for the bridge to become idle, selects the channel when needed, sends the relevant command, waits for completion, reads status or data, and unlocks.

State and persistence behavior: cached read pointer and channel reduce I2C commands but must stay synchronized with successful commands. Module parameters `active_pullup` and `extra_config` affect configuration globally. Strong pullup is enabled by writing config for a delayed operation; hardware deactivates it automatically.

Dependencies and integration points: depends on I2C SMBus byte operations, regulator framework, module parameters, and w1 core callbacks including triplet and set_pullup.

Risks: many helpers return `-1`, while w1 callbacks often collapse errors into default bus values. Idle wait has a fixed retry count without sleep, so slow or wedged devices can create noisy failures. Shared global config parameters affect all chips.

Test signals: DS2482-100 and DS2482-800 detection, regulator failures, reset status validation, multi-channel locking, triplet ROM search, strong pullup for parasitic-power devices, and unplug/remove cleanup after partial channel registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/masters/ds2482.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/masters/ds2490.c -->
## sources/distributed-fs/ceph-client/drivers/w1/masters/ds2490.c

Purpose: this USB driver supports DS2490/DS9490 USB-to-1-Wire adapters and registers them as w1 bus masters with byte, block, pullup, reset, touch-bit, and accelerated search operations.

Important APIs/types/functions: `struct ds_device` stores USB device/interface, endpoint addresses, strong-pullup timing state, status/data buffers, and `w1_bus_master`. USB helpers include `ds_send_control_cmd()`, `ds_send_control_mode()`, `ds_send_control()`, `ds_recv_status()`, `ds_recv_data()`, and `ds_send_data()`. Protocol helpers include `ds_wait_status()`, `ds_reset()`, `ds_set_pullup()`, byte/block I/O helpers, and `ds9490r_search()`.

Control flow: USB probe resets configuration, selects alternate setting 3, records interrupt and bulk endpoints, resets the DS2490, configures strong pullup support, initializes w1 callbacks, registers the master, and links the device globally. I/O uses vendor control messages to enqueue DS2490 commands, waits for idle status through interrupt endpoint polling, and transfers data over bulk endpoints. Search sends the current search ID, issues a hardware search command, polls status, reads returned ROM IDs in bulk chunks, queues callbacks outside the bus mutex, and preserves continuation state when `max_slave_count` is hit.

State and persistence behavior: state is runtime-only. `spu_sleep` and `spu_bit` cache strong pullup configuration. `master->search_id` persists continuation across scans. A global list tracks attached adapters under `ds_mutex`.

Dependencies and integration points: depends on USB core, endpoint altsettings, w1 core, w1 search flags, and kernel sleep/timeouts.

Risks: USB failures can stall bulk endpoints; `ds_recv_data()` clears halt and dumps status. Error returns are often reduced to w1 default values. Search holds the bus mutex while scanning but queues callbacks to avoid adding devices while locked. Several disabled code paths warn about DMAable buffers if revived.

Test signals: DS9490 enumeration, alternate-setting failure, endpoint layout validation, reset after endpoint overflow, byte/block transfers up to FIFO chunking limits, strong pullup timing, search continuation with `max_slave_count`, disconnect during search, and bulk endpoint halt recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/masters/ds2490.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/masters/matrox_w1.c -->
## sources/distributed-fs/ceph-client/drivers/w1/masters/matrox_w1.c

Purpose: this PCI driver bit-bangs a 1-Wire bus through Matrox G400 VGA DDC GPIO-like registers.

Important APIs/types/functions: `struct matrox_device` holds MMIO base/register pointers, data mask, mapped BAR address, and allocated `w1_bus_master`. Helpers read/write indexed DDC registers, initialize hardware, and implement `read_bit`/`write_bit` callbacks.

Control flow: probe validates Matrox G400 PCI IDs, allocates device and bus master together, maps resource 1, computes DDC register addresses, initializes DDC state, assigns w1 bit callbacks, registers the master, and stores driver data. Write-bit uses tristate behavior by driving low for zero and releasing for one; read-bit returns the DDC data register value. Remove unregisters the master, unmaps MMIO, and frees memory.

State and persistence behavior: no persistent state beyond mapped register pointers and bus master registration. Hardware DDC state is directly manipulated per bit.

Dependencies and integration points: depends on PCI, MMIO, Matrox PCI IDs, and w1 core low-level bit callbacks.

Risks: the read callback returns the whole data register, not just a normalized bit, relying on w1 core interpretation. Error path after `w1_add_master_device()` failure unmaps only if mapping exists. Timing is delegated to w1 core bit operations and may vary on legacy hardware.

Test signals: probe/remove on G400, resource mapping failure, DDC line read/write with real hardware, and w1 device discovery over the DDC pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/masters/matrox_w1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/masters/mxc_w1.c -->
## sources/distributed-fs/ceph-client/drivers/w1/masters/mxc_w1.c

Purpose: this platform driver exposes the Freescale/NXP MXC 1-Wire controller as a w1 bus master.

Important APIs/types/functions: `struct mxc_w1_device` stores MMIO registers, clock, and `w1_bus_master`. Bus callbacks are `mxc_w1_ds2_reset_bus()` and `mxc_w1_ds2_touch_bit()`. Probe/remove manage clocking, reset, timing divider setup, and w1 registration.

Control flow: probe allocates state, enables the input clock, warns about low or inaccurate timing base, maps registers, resets the controller, writes a divider to create about a 1 MHz time base, assigns callbacks, and registers the master. Reset writes RPP and waits for the controller to clear it, then returns presence status. Touch-bit writes a WR slot command, delays for the nominal slot, polls for completion, and returns read-state bit.

State and persistence behavior: runtime state is devm-managed; the enabled clock is explicitly disabled on failure/remove. Hardware registers hold transient transaction state.

Dependencies and integration points: depends on platform resources, `fsl,imx21-owire` device tree compatible, clock framework, MMIO, ktime polling, and w1 core.

Risks: timing correctness depends on clock rate and divider accuracy; warnings do not prevent registration. Polling timeouts return no-presence or zero values without detailed w1 errors.

Test signals: clock enable/rate edge cases, divider programming, reset presence detection, touch-bit read/write slots, device tree probe, and cleanup after failed registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/masters/mxc_w1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/masters/omap_hdq.c -->
## sources/distributed-fs/ceph-client/drivers/w1/masters/omap_hdq.c

Purpose: this platform driver supports TI OMAP HDQ/1-Wire hardware and exposes it through the w1 core, either in HDQ-style single-device mode or 1-Wire mode.

Important APIs/types/functions: `struct hdq_data` stores device, MMIO base, transaction mutex, IRQ status with spinlock, and mode. Low-level helpers handle register I/O, flag waits, IRQ status reset, byte write/read, break pulse, and ISR. W1 callbacks include `omap_w1_search_bus()`, `omap_w1_triplet()`, `omap_w1_reset_bus()`, `omap_w1_read_byte()`, and `omap_w1_write_byte()`.

Control flow: probe maps registers, reads `ti,mode`, configures either synthetic HDQ search or true 1-Wire triplet, enables runtime PM/autosuspend, reads hardware revision, requests IRQ, issues a break pulse, registers a global `omap_w1_master`, and releases runtime PM. Transactions take runtime PM references, serialize on `hdq_mutex`, program control/status bits, wait for IRQ status through a wait queue, clear consumed IRQ bits under spinlock, and drop PM references. Runtime suspend stores mode and clears interrupt status; resume enables clock and interrupt mask.

State and persistence behavior: `hdq_irqstatus` accumulates interrupt bits until consumed. `mode` persists selected HDQ/1W mode. The module parameter `w1_id` controls the synthetic ROM ID in HDQ mode. The w1 master object is static and populated at probe time.

Dependencies and integration points: depends on platform resources, device tree compatibles `ti,omap3-1w` and `ti,am4372-hdq`, runtime PM, IRQs, w1 core, and w1 CRC helper.

Risks: global static `omap_w1_master` limits multi-instance safety. Some callbacks return negative errors through `u8`, collapsing to `0xff`. Break/reset ignores `omap_hdq_break()` failure and returns success. Timing and IRQ completion are hardware-sensitive.

Test signals: HDQ and 1-Wire modes, runtime suspend/resume around transactions, IRQ timeout and status clearing, triplet ROM search, SKIP ROM break behavior, module `w1_id`, remove while runtime suspended, and multiple-controller probe attempts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/masters/omap_hdq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/masters/sgi_w1.c -->
## sources/distributed-fs/ceph-client/drivers/w1/masters/sgi_w1.c

Purpose: this platform driver exposes SGI ASIC 1-Wire hardware as a Linux w1 master.

Important APIs/types/functions: `struct sgi_w1_device` stores the memory-mapped control register, `w1_bus_master`, and optional platform `dev_id`. Bus callbacks are `sgi_w1_reset_bus()` and `sgi_w1_touch_bit()`, with polling helper `sgi_w1_wait()`.

Control flow: probe allocates state, maps one MMIO resource, assigns reset/touch callbacks, copies optional platform data `dev_id`, and registers the w1 master. Reset writes a packed pulse/sample command for reset timing, waits for DONE, delays recovery, and returns read data. Touch-bit writes timing values for read/write-one or write-zero, waits for DONE, and delays recovery after read/write-one slots.

State and persistence behavior: no persisted state. The MCR register reflects the active transaction; `dev_id` is copied into driver memory for w1 core identity.

Dependencies and integration points: depends on platform MMIO resources, optional `linux/platform_data/sgi-w1.h`, delay helpers, and w1 core.

Risks: `sgi_w1_wait()` spins without timeout until `MCR_DONE`, so wedged hardware can hang a caller. There is no runtime PM or clock handling despite including clock headers. Timing constants are hardcoded.

Test signals: probe with and without platform data, reset/touch-bit on real ASIC, missing/invalid MMIO resource, remove cleanup, and fault-injection for a never-completing MCR operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/masters/sgi_w1.c -->
