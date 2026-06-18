# subset-b-005864 grouped research

This grouped report covers Linux kernel header contracts under `sources/distributed-fs/ceph-client/include/linux` for IIO, input, networking, initialization, integrity, Intel platform, and interconnect interfaces. Each section is source-path aligned for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/events.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/events.h

Purpose: Defines kernel-side helpers for packing Industrial I/O event identity into the u64 event code consumed by `iio_push_event()` and userspace event readers.

Important APIs/types/functions: `_IIO_EVENT_CODE()` is the common bit-packer; `IIO_MOD_EVENT_CODE()`, `IIO_UNMOD_EVENT_CODE()`, and `IIO_DIFF_EVENT_CODE()` specialize modified, unmodified, and differential channels. It depends on UAPI event bit positions and `enum iio_chan_type`.

Control flow: There is no runtime control flow; callers build stable event codes at event-report sites.

State/persistence: No state is owned. The generated code encodes channel type, index, modifier or differential pair, event type, and direction into a persistent ABI value.

Dependencies/integration: Integrates `linux/iio/types.h`, `uapi/linux/iio/events.h`, and IIO event callbacks declared in `iio.h`.

Risks: Incorrect modified/differential flags or channel numbering silently changes userspace-visible event identity.

Test signals: Compile users using all three macros and exercise threshold/event sysfs paths; verify decoded event codes match expected channel, type, and direction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/frequency/ad9523.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/frequency/ad9523.h

Purpose: Supplies board/platform configuration for the Analog Devices AD9523 SPI low-jitter clock generator IIO driver.

Important APIs/types/functions: `enum outp_drv_mode` selects output electrical mode; `enum ref_sel_mode` selects reference behavior; PLL loop-filter enums encode resistor/capacitor choices. `struct ad9523_channel_spec` describes each output divider, phase, polarity, power, alternate source, and name. `struct ad9523_platform_data` carries VCXO, reference input, PLL1/PLL2, loop-filter, output-channel, and optional device-name settings.

Control flow: The header has no functions. Probe-time driver code consumes the platform data to program reference paths, PLL divisors, charge pumps, and output channels.

State/persistence: State is platform supplied and persists as board data, device-tree translated data, or static machine data. Hardware programming derived from it persists until reconfigured or reset.

Dependencies/integration: Integrates SPI device naming (`SPI_NAME_SIZE`) and IIO frequency driver probe code.

Risks: Divider, phase, charge-pump, or loop-filter values are hardware-sensitive; invalid combinations can produce unlocked PLLs or bad clocks.

Test signals: Driver probe should validate channel count/ranges, lock status, output clock rates, and sysfs channel naming on representative board data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/frequency/ad9523.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/frequency/adf4350.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/frequency/adf4350.h

Purpose: Defines register bit builders, limits, and platform data for ADF4350/ADF4351 SPI PLL synthesizer drivers.

Important APIs/types/functions: Register constants `ADF4350_REG0` through `REG5`; field macros for INT/FRAC/MOD/phase, charge pump, reference dividers, muxout, output power, RF divider, feedback, and lock detect; hardware limits such as output/VCO/PFD frequency and modulus; `struct adf4350_platform_data` with name, reference clock, spacing, power-up frequency, reference divider settings, and user register overrides.

Control flow: Probe/tune paths build six register words from these macros and platform inputs; no functions run in the header.

State/persistence: User settings and calculated registers become device configuration over SPI. The header itself stores no state.

Dependencies/integration: Used by the IIO PLL/frequency driver and board data.

Risks: Field macros mostly mask but do not range-check semantic limits; bad reference or spacing inputs can produce illegal PFD/VCO settings.

Test signals: Unit-style register word checks, boundary frequency tuning, lock detect, and sysfs frequency readback are strong coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/frequency/adf4350.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/gyro/itg3200.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/gyro/itg3200.h

Purpose: Provides shared register definitions and helper declarations for the InvenSense ITG3200 three-axis gyroscope IIO driver.

Important APIs/types/functions: Register constants cover sample rate, DLPF/full-scale, IRQ configuration/status, temperature and gyro output registers, and power management. `struct itg3200` stores the owning I2C client, optional trigger, orientation matrix, and mutex. `enum ITG3200_SCAN_INDEX` orders temp and XYZ samples. `itg3200_read_reg_8()` and `itg3200_write_reg_8()` are common accessors. Buffer/trigger functions are real only under `CONFIG_IIO_BUFFER`.

Control flow: Core driver code configures registers, reads data, and optionally wires a data-ready trigger and buffer setup; stubs keep non-buffer builds compiling.

State/persistence: Per-device state includes I2C identity, trigger pointer, mount orientation, and lock. Hardware register configuration persists until reset.

Dependencies/integration: Depends on `linux/iio/iio.h`, I2C, IIO trigger/buffer support, and mount matrix reporting.

Risks: IRQ polarity/latch settings and DLPF sample rates affect data readiness and buffering correctness.

Test signals: Probe without buffer support, buffered capture, orientation sysfs output, register read/write failures, and IRQ data-ready handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/gyro/itg3200.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/hw-consumer.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/hw-consumer.h

Purpose: Declares a small consumer API for enabling and disabling hardware-backed IIO consumers.

Important APIs/types/functions: Opaque `struct iio_hw_consumer`; allocation/free APIs `iio_hw_consumer_alloc()`, `iio_hw_consumer_free()`, and managed `devm_iio_hw_consumer_alloc()`; runtime control APIs `iio_hw_consumer_enable()` and `iio_hw_consumer_disable()`.

Control flow: Consumers allocate a handle for a device, enable the associated hardware route when needed, then disable and release it. Managed allocation ties cleanup to device lifetime.

State/persistence: State is hidden behind the opaque handle; this header owns no fields. Enabled hardware state persists until disabled or devres cleanup.

Dependencies/integration: Integrates with the device model and IIO consumer/provider mapping internals.

Risks: Enable/disable imbalance may leave hardware active or consumers unavailable.

Test signals: Probe/remove with devm cleanup, repeated enable/disable, and error injection for missing provider mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/hw-consumer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/iio-gts-helper.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/iio-gts-helper.h

Purpose: Defines helper data structures and APIs for IIO drivers that expose coupled gain, integration-time, and scale settings.

Important APIs/types/functions: `struct iio_gain_sel_pair` maps gain to hardware selector; `struct iio_itime_sel_mul` maps integration time to selector and multiplier; `struct iio_gts` stores max scale and sorted lookup tables. Macros `GAIN_SCALE_GAIN()` and `GAIN_SCALE_ITIME_US()` build tables. Helpers find gain/time selectors, validate gains/times, convert total gain to scale, choose replacement gains when integration time changes, and expose available times/scales.

Control flow: Drivers initialize `iio_gts` with `devm_iio_init_iio_gts()`, then call lookup/conversion helpers in `read_raw`, `write_raw`, and `read_avail` paths.

State/persistence: Helper state is immutable table metadata after initialization; actual hardware gain/time remains driver-owned.

Dependencies/integration: Uses device-managed lifetime and standard IIO value formats.

Risks: Tables must be sorted/consistent or scale selection can choose wrong hardware settings.

Test signals: Boundary gains/times, unavailable scale lists, nearest-low gain selection, and scale preservation across integration-time changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/iio-gts-helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/iio-opaque.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/iio-opaque.h

Purpose: Defines private IIO core storage that is embedded behind public `struct iio_dev` but not meant for direct driver access.

Important APIs/types/functions: `struct iio_dev_opaque` carries internal ids, character device, indio parent, event interface, buffer list/count, channel attribute group, scan-index mapping, clock id, flags for registration and sysfs enablement, mutexes, event interface, and optional debugfs dentry. `to_iio_dev_opaque()` maps a public IIO device to its private tail storage.

Control flow: IIO core allocation/register/unregister code initializes and consumes the opaque structure; drivers use public helpers instead.

State/persistence: Holds persistent per-device core state for registered IIO devices, including buffer/event/sysfs/debugfs internals.

Dependencies/integration: Integrates with device model, cdev, mutexes, events, buffers, and debugfs.

Risks: Direct use outside core can violate locking/lifetime assumptions; layout must stay synchronized with allocation code.

Test signals: IIO device allocation/free, register/unregister, debugfs builds, multiple buffers, and event interface creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/iio-opaque.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/iio.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/iio.h

Purpose: Main Industrial I/O kernel interface for declaring devices, channels, events, buffers, triggers, value formats, registration, and common helpers.

Important APIs/types/functions: Key types include `struct iio_chan_spec`, `iio_scan_type`, `iio_event_spec`, `iio_info`, `iio_buffer_setup_ops`, and `iio_dev`. Helpers cover enum/ext-info attributes, mount matrices, channel capability checks, timestamps, device registration/devm registration, event push, direct/buffer mode locking, driver data, private data, scan type lookup, active channel iteration, value formatting/parsing, ACPI mount data, and unit conversions.

Control flow: Drivers allocate an `iio_dev`, fill channel/spec/info callbacks, register it, then IIO core dispatches sysfs reads/writes, event config, buffer setup, trigger validation, scan updates, and debugfs access through the declared callbacks.

State/persistence: `struct iio_dev` persists for the device lifetime and stores modes, buffer, scan masks, trigger/poll functions, channels, label/name, callback tables, and private data. Mode guards protect direct reads versus active buffers.

Dependencies/integration: Integrates device model, cdev, cleanup guards, IIO UAPI types, buffers, triggers, ACPI, sysfs, debugfs, and DMA/timestamp alignment.

Risks: Incorrect scan formats, mask lengths, mode locking, or callback formats create ABI breakage, data corruption, or races between sysfs and buffered capture.

Test signals: Device registration/remove, sysfs raw/scale/available paths, event push/read, direct-mode lock failures while buffers run, buffer timestamp alignment, ext scan type validation, and ACPI orientation parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/iio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/imu/adis.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/imu/adis.h

Purpose: Common library interface for Analog Devices ADIS IMU sensors, wrapping SPI register access, reset/status handling, triggers, buffers, and common channel declarations.

Important APIs/types/functions: `struct adis_timeout`, `adis_data`, `adis_ops`, and `adis` describe variant delays, register map, status masks, burst/FIFO behavior, custom bus ops, SPI buffers, paging, IRQ, and locking. APIs initialize/reset devices, read/write 8/16/32-bit registers, update masked fields, check status, enable IRQs, run single conversions, set up buffer/trigger support, and expose debugfs register access. Channel macros build voltage, supply, aux ADC, temp, accel, gyro, inclination, and rotation channel specs.

Control flow: Driver probe calls `adis_init()`, performs startup/status checks, uses locked public helpers for normal access or `__adis_*` helpers under explicit `state_lock`, then optionally installs managed buffer and trigger support.

State/persistence: `struct adis` owns SPI transfer state, current page, DMA-safe buffers, IRQ flags, burst length, and mutex-protected register state.

Dependencies/integration: Depends on SPI, interrupts, IIO core/types, cleanup guards, optional `CONFIG_IIO_ADIS_LIB_BUFFER`, and debugfs.

Risks: Mixing locked/unlocked helpers incorrectly can corrupt shared SPI message/page state; wrong value width in update macros is compile-time guarded but macro constants can still surprise.

Test signals: Register read/write by width, paged-register access, reset timing, status error masks, IRQ enable, buffered capture, scan mode update, and debugfs register read/write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/imu/adis.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/kfifo_buf.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/kfifo_buf.h

Purpose: Declares IIO kfifo buffer allocation and managed setup helpers for software-visible buffered capture.

Important APIs/types/functions: `iio_kfifo_allocate()`, `iio_kfifo_free()`, `devm_iio_kfifo_buffer_setup_ext()`, and the shorter `devm_iio_kfifo_buffer_setup()` macro.

Control flow: Drivers allocate or devm-attach a kfifo buffer during probe; IIO core then uses setup ops and optional buffer attributes during buffer enable/disable and reads.

State/persistence: The actual FIFO buffer state is opaque and persists for the IIO device lifetime or until freed.

Dependencies/integration: Integrates IIO buffer core, device-managed cleanup, `iio_dev_attr` buffer attributes, and `iio_buffer_setup_ops`.

Risks: Wrong setup ops or scan configuration can mismatch FIFO sample layout.

Test signals: Probe/remove cleanup, buffer enable/disable callbacks, scan data ordering, and optional buffer attribute exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/kfifo_buf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/machine.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/machine.h

Purpose: Defines static machine mapping entries that connect IIO provider channels to named consumer devices/channels.

Important APIs/types/functions: `struct iio_map` stores provider channel name, consumer device name, and consumer channel name. `IIO_MAP()` initializes one mapping entry.

Control flow: Board code or mapping tables declare arrays consumed by the IIO map/consumer infrastructure; no runtime behavior exists in the header.

State/persistence: Mapping entries are static configuration and persist as board data.

Dependencies/integration: Used by IIO consumer APIs to resolve provider channels without firmware descriptions.

Risks: String mismatches make consumers fail at runtime; stale maps can silently bind the wrong channel names.

Test signals: Consumer lookup by device/channel, missing-provider error handling, and board boot with expected IIO channel wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/machine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/sw_device.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/sw_device.h

Purpose: Exposes configfs-backed software IIO device type registration and lifecycle helpers.

Important APIs/types/functions: `module_iio_sw_device_driver()` builds module init/exit for a software device type. `struct iio_sw_device_type` names a type and ops; `struct iio_sw_device` embeds an `iio_dev` pointer and configfs group; `struct iio_sw_device_ops` provides `probe()` and `remove()`. APIs register/unregister types and create/destroy instances.

Control flow: Type modules register ops; configfs creates named instances, invoking probe; destroy invokes remove and cleanup.

State/persistence: Per-instance state lives in `struct iio_sw_device` and configfs items until destroyed.

Dependencies/integration: Depends on module/device/IIO/configfs and conditional configfs group initialization.

Risks: Probe/remove imbalance or configfs naming conflicts can leak IIO devices.

Test signals: Module load/unload, configfs mkdir/rmdir instance lifecycle, failed probe cleanup, and IIO device registration visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/sw_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/sw_trigger.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/sw_trigger.h

Purpose: Exposes configfs-backed software IIO trigger type registration and lifecycle helpers.

Important APIs/types/functions: `module_iio_sw_trigger_driver()` creates module init/exit. `struct iio_sw_trigger_type`, `iio_sw_trigger`, and `iio_sw_trigger_ops` describe trigger type, instance, and `probe()`/`remove()` hooks. APIs register/unregister types and create/destroy named triggers.

Control flow: Type registration makes configfs trigger creation possible; instance creation calls probe to allocate an `iio_trigger`; destruction calls remove.

State/persistence: Instance state includes the trigger pointer and configfs group for the instance lifetime.

Dependencies/integration: Depends on module, device, IIO core, configfs, and IIO trigger internals.

Risks: Missing cleanup leaves configfs items or triggers registered; names must remain unique.

Test signals: Software trigger module lifecycle, configfs instance creation/removal, trigger visibility under IIO, and error unwind coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/sw_trigger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/sysfs.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/sysfs.h

Purpose: Provides IIO-specific sysfs attribute wrappers and declaration macros.

Important APIs/types/functions: `struct iio_dev_attr` extends `device_attribute` with an address/private value; `struct iio_const_attr` exposes constant strings. Macros declare generic IIO attrs, device attrs, named attrs, constant attrs, and common sampling frequency, integration time, and temperature attributes.

Control flow: IIO core and drivers declare attributes statically; sysfs invokes show/store callbacks or constant readers.

State/persistence: Attribute metadata is static. Per-device values are read or written through callbacks; constants persist as literal strings.

Dependencies/integration: Integrates with Linux device attributes, IIO buffers/channels, and common IIO ABI filenames.

Risks: Attribute mode/callback mismatches can create write-only/read-only ABI bugs; incorrect address values can direct callbacks to wrong registers.

Test signals: Sysfs file existence, permissions, const-attr output, read/write callback routing, and ABI filename stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/timer/stm32-lptim-trigger.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/timer/stm32-lptim-trigger.h

Purpose: Defines STM32 low-power timer trigger names and a type-check helper for IIO trigger consumers/providers.

Important APIs/types/functions: String constants cover LPTIM output and channel trigger names. `is_stm32_lptim_trigger()` is declared when `CONFIG_IIO_STM32_LPTIMER_TRIGGER` is reachable and otherwise returns false, with a build-time hint when the provider is enabled but not reachable.

Control flow: Drivers compare a selected `iio_trigger` with this helper before accepting timer-specific routing.

State/persistence: No state is owned; trigger objects live in IIO trigger providers.

Dependencies/integration: Depends on IIO core/trigger headers and Kconfig reachability.

Risks: Reachability matters for modular builds; accepting an incompatible trigger can misroute hardware timer capture.

Test signals: Builds for builtin/module/disabled provider states and validation of accepted/rejected triggers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/timer/stm32-lptim-trigger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/timer/stm32-timer-trigger.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/timer/stm32-timer-trigger.h

Purpose: Defines STM32 general-purpose timer trigger names and a helper for recognizing STM32 timer IIO triggers.

Important APIs/types/functions: String constants cover TRGO/TRGO2 and channel/compare outputs for TIM1-TIM20 variants. `is_stm32_timer_trigger()` is declared when the trigger provider is reachable and returns false otherwise.

Control flow: IIO ADC/timer consumers use the helper to validate selected triggers before configuring hardware capture paths.

State/persistence: Header owns no state; timer trigger instances and hardware configuration live in provider drivers.

Dependencies/integration: Integrates Kconfig reachability, IIO trigger objects, and STM32 timer trigger providers.

Risks: Name constants are ABI-like between provider and consumers; typos or missing timer outputs break firmware/driver matching.

Test signals: Kconfig matrix builds, device-tree trigger lookup, and validation for all supported timer output names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/timer/stm32-timer-trigger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/trigger.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/trigger.h

Purpose: Declares the IIO trigger provider interface and trigger object lifecycle.

Important APIs/types/functions: `struct iio_subirq` tracks per-consumer interrupt state; `struct iio_trigger_ops` supplies owner, state, reenable, validate, and try_reenable hooks; `struct iio_trigger` embeds a device, ops, list, pool_lock, subirq base, pool bitmap, attached device list, use count, immutable flag, and driver data. APIs allocate/free, register/unregister, devm-register, poll, generic data-ready polling, validate own triggers, and set immutable triggers.

Control flow: Providers allocate/register triggers; consumers attach poll functions; provider IRQs call `iio_trigger_poll()` or nested variant; core fans out to subirqs and later receives notify-done.

State/persistence: Trigger state includes device lifetime, attached consumers, interrupt pool, use count, and private driver data.

Dependencies/integration: Depends on IRQ, module, atomic, device model, IIO devices, and optional `CONFIG_IIO_TRIGGER`.

Risks: Incorrect reenable/notify discipline can stall triggers; own-trigger validation prevents unsafe self-trigger loops.

Test signals: Trigger registration, consumer attach/detach, poll fanout, nested IRQ contexts, immutable trigger rejection, and disabled-Kconfig builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/trigger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/trigger_consumer.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/trigger_consumer.h

Purpose: Declares the consumer-side poll function abstraction used by triggered IIO buffers and events.

Important APIs/types/functions: `struct iio_poll_func` stores top half, threaded bottom half, timestamp, trigger, IIO device, IRQ, and name. `iio_alloc_pollfunc()` creates a poll function; `iio_dealloc_pollfunc()` frees it; `iio_pollfunc_store_time()` is a common top half; `iio_trigger_notify_done()` completes trigger processing.

Control flow: Buffer/event setup allocates a poll function, trigger poll invokes top half/thread, driver pushes samples/events, then notifies done.

State/persistence: Poll function state persists while attached to an IIO device/trigger and carries the last timestamp.

Dependencies/integration: Depends on interrupts, IIO trigger provider API, and buffer/event setup helpers.

Risks: Forgetting notify-done or using sleepable code in a hard IRQ top half can deadlock or miss samples.

Test signals: Triggered buffer capture, timestamp top-half behavior, detach cleanup, and threaded handler error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/trigger_consumer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/triggered_buffer.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/triggered_buffer.h

Purpose: Declares helpers for IIO devices that use trigger-driven buffered capture.

Important APIs/types/functions: `iio_triggered_buffer_setup_ext()` wires top-half, threaded handler, setup ops, and optional attrs; `iio_triggered_buffer_cleanup()` unwinds it. Shorter macros provide default NULL attrs, and devm variants bind cleanup to a device.

Control flow: Probe calls setup, IIO core enables buffers and attaches poll functions to triggers, threaded handlers push scans, and cleanup runs on remove.

State/persistence: Buffer/poll function state is stored in the `iio_dev` and persists while setup is active.

Dependencies/integration: Depends on IIO buffer core, interrupt handlers, trigger consumer infrastructure, and device-managed resources.

Risks: Handler/sample layout mismatch with channel scan specs corrupts buffered ABI.

Test signals: Probe/remove cleanup, buffer enable with trigger, top/thread handler ordering, scan mask validation, and devm unwind on probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/triggered_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/triggered_event.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/triggered_event.h

Purpose: Declares helpers for IIO devices that produce events through trigger infrastructure rather than normal buffered samples.

Important APIs/types/functions: `iio_triggered_event_setup()` installs top and threaded IRQ handlers for event triggering; `iio_triggered_event_cleanup()` removes them.

Control flow: Probe sets up event triggering; trigger polls invoke handlers that typically evaluate/report events; remove cleans up.

State/persistence: Event poll function state is attached to the IIO device for the setup lifetime.

Dependencies/integration: Depends on interrupts, IIO trigger consumer/provider code, and event pushing in `iio.h`.

Risks: Event-triggered mode is unusual and close to buffered trigger flow; incorrect cleanup or notify-done handling affects all attached consumers.

Test signals: Event enable/disable, trigger firing, event code delivery, and cleanup on probe failure/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/triggered_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/types.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/types.h

Purpose: Defines kernel-side IIO value, event-info, available-value, and channel-info enums layered on top of UAPI channel/event types.

Important APIs/types/functions: `enum iio_event_info` adds event configuration fields such as value, hysteresis, period, high/low pass filters, timeout, enable, reset timeout, and scale. `IIO_VAL_*` macros describe callback return value encoding. `enum iio_available_type` describes list/range availability. `enum iio_chan_info_enum` enumerates raw, processed, scale, offset, sampling frequency, filters, calibration, peak, oversampling, integration time, enable, errors, and label.

Control flow: IIO callbacks return these value-format constants and use enum ids in channel/event masks.

State/persistence: No owned state; values define stable ABI contracts between drivers, core, and userspace formatting.

Dependencies/integration: Includes UAPI IIO types and is used heavily by `iio.h`, drivers, sysfs, and events.

Risks: Masks rely on enum positions; changing order breaks sysfs/event ABI.

Test signals: Compile mask users, sysfs formatting for every `IIO_VAL_*` form, and event attribute generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ima.h -->
# sources/distributed-fs/ceph-client/include/linux/ima.h

Purpose: Declares Integrity Measurement Architecture hooks used by file, inode, kexec, critical-data, appraisal, and boot-policy code.

Important APIs/types/functions: Under `CONFIG_IMA`, exports current hash algorithm, file/inode hash calculation, kexec command-line measurement, critical-data measurement, optional appraisal command-line parsing, kexec buffer hooks, appraisal state, signature appraisal, and architecture policy lookup. Disabled builds provide safe stubs returning `HASH_ALGO__LAST`, `-EOPNOTSUPP`, false, or no-op values. `CONFIG_HAVE_IMA_KEXEC` exposes buffer range helpers.

Control flow: Callers invoke hooks at security-sensitive events; Kconfig selects real enforcement or no-op stubs.

State/persistence: IMA measurement lists, hashes, appraisal policy, and kexec buffers are external; this header only exposes access points.

Dependencies/integration: Depends on filesystem/security/kexec/secure-boot/hash headers and integrity policy implementations.

Risks: Disabled stubs can hide missing enforcement in builds; buffer validation must be exact for kexec handoff.

Test signals: Kconfig matrix, file/inode hash success/failure, appraisal enabled state, kexec buffer validation, and secure/trusted boot policy selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ima.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/imx-media.h -->
# sources/distributed-fs/ceph-client/include/linux/imx-media.h

Purpose: Provides small public definitions for i.MX media pipeline controls and private V4L2 events.

Important APIs/types/functions: `V4L2_EVENT_IMX_CLASS` and `V4L2_EVENT_IMX_FRAME_INTERVAL_ERROR` define a private event class. `enum imx_ctrl_id` reserves i.MX-specific control ids starting at `V4L2_CID_USER_IMX_BASE`, including frame interval controls.

Control flow: i.MX media drivers and userspace-facing V4L2 code use these identifiers when registering controls or emitting events.

State/persistence: No state is owned; ids are ABI-facing constants.

Dependencies/integration: Integrates with V4L2 control and event namespaces.

Risks: Numeric id stability matters for userspace; collisions with other private controls would be ABI bugs.

Test signals: V4L2 control enumeration, frame interval error event delivery, and compile checks for include users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/imx-media.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/in.h -->
# sources/distributed-fs/ceph-client/include/linux/in.h

Purpose: Adds kernel IPv4 helpers around the UAPI IPv4 definitions.

Important APIs/types/functions: `proto_ports_offset()` maps IPPROTO TCP/UDP/DCCP/SCTP/UDPLITE to source/destination port offsets or `-EINVAL`. Address classifiers cover loopback, multicast, local multicast, limited broadcast, all-snoopers, zeronet, RFC1918 private ranges, link-local, 6to4 anycast, and test networks.

Control flow: Networking code calls static inline classifiers on hot paths without function-call overhead.

State/persistence: Stateless bitmask checks over network-order IPv4 addresses.

Dependencies/integration: Includes `uapi/linux/in.h` and errno definitions; used by routing, filtering, socket, and packet parsing code.

Risks: Classifiers assume `__be32` network byte order and exact masks; misuse with host-order values misclassifies addresses.

Test signals: Table-driven address classification, unsupported protocol offset errors, and endian-sensitive compile/runtime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/in.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/in6.h -->
# sources/distributed-fs/ceph-client/include/linux/in6.h

Purpose: Provides kernel IPv6 socket/address helpers and well-known address declarations.

Important APIs/types/functions: `struct sockaddr_inet` overlays IPv4 and IPv6 socket addresses. Externs and initializer macros define any, loopback, link-local all-nodes/all-routers, interface-local all-nodes/all-routers, and site-local all-routers addresses.

Control flow: Networking code uses the union-style sockaddr when handling AF_INET/AF_INET6 generically and references global address constants.

State/persistence: The extern address constants are immutable global data; the header owns no mutable state.

Dependencies/integration: Includes UAPI IPv6 definitions and integrates socket, routing, multicast, and neighbor code.

Risks: Initializer constants must match IPv6 multicast scope semantics; sockaddr overlay users must respect active address family.

Test signals: Compile users, equality checks against well-known IPv6 addresses, and generic sockaddr handling for IPv4/IPv6.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/in6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/indirect_call_wrapper.h -->
# sources/distributed-fs/ceph-client/include/linux/indirect_call_wrapper.h

Purpose: Provides retpoline-aware wrappers that replace indirect calls with likely direct-call comparisons when mitigation is enabled.

Important APIs/types/functions: `INDIRECT_CALL_1` through `_4` compare a function pointer with known target functions under `CONFIG_MITIGATION_RETPOLINE`; otherwise they call directly through the pointer. `INDIRECT_CALLABLE_DECLARE`, `INDIRECT_CALLABLE_SCOPE`, and `EXPORT_INDIRECT_CALLABLE` manage symbol visibility. `INDIRECT_CALL_INET` variants adapt to IPv6/INET Kconfig.

Control flow: Hot networking paths pass a function pointer and likely targets; wrappers dispatch direct calls for matching targets or fall back to the function pointer.

State/persistence: Stateless macro dispatch.

Dependencies/integration: Tied to retpoline mitigation, export symbols, and networking protocol Kconfig.

Risks: Argument order must match target prototypes; missing `INDIRECT_CALLABLE` export can break modules.

Test signals: Builds with/without retpoline, IPv4-only/IPv6 configs, and objdump/perf checks showing direct target branches in hot paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/indirect_call_wrapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/inet.h -->
# sources/distributed-fs/ceph-client/include/linux/inet.h

Purpose: Declares kernel IP text parsing and formatting helpers for IPv4/IPv6 addresses.

Important APIs/types/functions: Constants `INET_ADDRSTRLEN` and `INET6_ADDRSTRLEN`; `in_aton()`, `in4_pton()`, `in6_pton()`, `inet_pton_with_scope()`, and `inet_addr_is_any()`.

Control flow: Callers parse strings into binary addresses, optionally with scope and network namespace context, or test sockaddr storage for wildcard addresses.

State/persistence: Stateless parsing; scope parsing may consult namespace/device context externally.

Dependencies/integration: Depends on kernel types, socket definitions, and net namespaces; used by procfs/sysfs/config parsers and networking subsystems.

Risks: Delimiter/end pointer handling is subtle; scoped IPv6 parsing must validate interfaces correctly.

Test signals: IPv4/IPv6 parse vectors, invalid input, delimiter behavior, scoped link-local addresses, and wildcard sockaddr tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/inet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/inet_diag.h -->
# sources/distributed-fs/ceph-client/include/linux/inet_diag.h

Purpose: Declares inet socket diagnostic handler interfaces for netlink-based socket dumps.

Important APIs/types/functions: `struct inet_diag_handler` binds protocol handlers with dump/destroy helpers and optional get-info logic. `struct inet_diag_dump_data` stores request nlattrs, bytecode, netlink cb data, and cgroup id. APIs fill common socket diagnostic messages/attrs, evaluate bytecode filters, and register/unregister handlers.

Control flow: Netlink diagnostic requests dispatch to registered protocol handlers, filter sockets with bytecode/cgroup data, and fill `inet_diag_msg` plus optional attributes.

State/persistence: Registered handlers persist until unregistered; dump data is per-netlink request.

Dependencies/integration: Depends on netlink, UAPI inet_diag, IPv6 optional attrs, cgroup socket data, and protocol hashinfo.

Risks: Attribute size calculations must match fill logic; handler lifetime must be synchronized with netlink dumps.

Test signals: `ss`/inet_diag dumps for TCP/UDP variants, bytecode filters, cgroup attrs, IPv6 attrs, and handler unregister during module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/inet_diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/inetdevice.h -->
# sources/distributed-fs/ceph-client/include/linux/inetdevice.h

Purpose: Defines IPv4 per-device state, per-interface addresses, devconf helpers, and lookup/notifier APIs.

Important APIs/types/functions: `struct ipv4_devconf` stores sysctl data and explicit state bits. `struct in_device` links a net_device to IPv4 addresses, multicast lists/hash, IGMP timers/state, ARP parameters, devconf, refcount, and RCU head. `struct in_ifaddr` describes IPv4 interface addresses, masks, broadcast, scope, flags, lifetimes, labels, and timestamps. Helpers read/set devconf, combine all/per-device policy, iterate addresses under RTNL/RCU, look up devices/addresses, compute masks, and manage refcounts.

Control flow: Device setup creates `in_device`; address configuration mutates `ifa_list`; routing, ARP, multicast, and ioctls read devconf/address state under RCU or RTNL.

State/persistence: Per-netdevice IPv4 state persists while the network device is alive; address lifetimes and multicast timers update over time.

Dependencies/integration: Depends on netdevice, RCU, timers, sysctl, rtnetlink, neighbor, multicast, and notifier chains.

Risks: Locking context matters for address iteration and `ip_ptr`; missing refcount/RCU discipline can cause use-after-free.

Test signals: IPv4 address add/delete, ioctl gifconf, notifier callbacks, multicast timers, devconf sysctl changes, RCU lookups, and mask validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/inetdevice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/init.h -->
# sources/distributed-fs/ceph-client/include/linux/init.h

Purpose: Core initialization annotation and initcall registration interface for built-in kernel code and modules.

Important APIs/types/functions: Section macros mark init/exit/ref/meminit code and data. `initcall_t`, `exitcall_t`, `initcall_entry_t`, initcall boundary symbols, boot command-line globals, architecture init prototypes, and `THIS_MODULE` are declared. Macros register early, pure, core, postcore, arch, subsys, fs, rootfs, device, late, sync, console, and exit calls. `struct obs_kernel_param`, `__setup()`, `early_param()`, and `early_param_on_off()` register boot parameter parsers.

Control flow: Linker collects initcall and setup entries; boot code parses early/setup params and runs initcall levels in order, freeing init sections later.

State/persistence: Init/exit section data may be discarded; boot command lines and setup tables persist through initialization. Module builds elide built-in setup macros.

Dependencies/integration: Integrates compiler attributes, linker scripts, LTO, PREL32 relocations, module ownership, and init/main.c.

Risks: Section mismatch annotations can hide real lifetime bugs; initcall ordering is link-order sensitive except special LTO handling.

Test signals: Build-time modpost section checks, boot initcall ordering, early parameter parsing, module versus builtin builds, and LTO/PREL32 configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/init_ohci1394_dma.h -->
# sources/distributed-fs/ceph-client/include/linux/init_ohci1394_dma.h

Purpose: Declares optional early OHCI-1394 DMA initialization hooks.

Important APIs/types/functions: When `CONFIG_PROVIDE_OHCI1394_DMA_INIT` is enabled, exposes `init_ohci1394_dma_early` initdata flag and `init_ohci1394_dma_on_all_controllers()`.

Control flow: Early boot code can inspect the flag and initialize DMA on all OHCI-1394 controllers.

State/persistence: The flag is `__initdata`, so it is only meaningful during init. Controller DMA state is external hardware state.

Dependencies/integration: Depends on init annotations and the optional FireWire/OHCI early DMA provider.

Risks: Only available under the Kconfig option; code must not reference symbols otherwise.

Test signals: Kconfig enabled/disabled builds and early boot path coverage on systems with OHCI-1394 controllers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/init_ohci1394_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/init_syscalls.h -->
# sources/distributed-fs/ceph-client/include/linux/init_syscalls.h

Purpose: Declares syscall-like helpers used by kernel init code before userspace exists.

Important APIs/types/functions: Init-only helpers include `init_mount()`, `init_umount()`, `init_chdir()`, `init_chroot()`, `init_chown()`, `init_chmod()`, `init_eaccess()`, `init_stat()`, `init_mknod()`, `init_link()`, `init_symlink()`, `init_unlink()`, `init_mkdir()`, `init_rmdir()`, `init_utimes()`, `init_dup()`, and `init_pivot_root()`.

Control flow: Early init/rootfs code calls these wrappers to build or switch root filesystem state.

State/persistence: Operations mutate VFS namespace, files, directories, modes, ownership, and mounts.

Dependencies/integration: Integrates init, VFS, mount, namespace, and credential behavior.

Risks: These helpers run in privileged init context; errors can prevent boot or corrupt initramfs setup.

Test signals: Initramfs boot, root mount/unmount, namespace setup, file mode/ownership operations, and error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/init_syscalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/init_task.h -->
# sources/distributed-fs/ceph-client/include/linux/init_task.h

Purpose: Provides declarations and small initialization macros used while defining the kernel's initial task.

Important APIs/types/functions: Declares `init_files`, `init_fs`, and `init_nsproxy`; defines `INIT_PREV_CPUTIME(x)` for non-native virtual CPU accounting builds; defines `INIT_TASK_COMM` as `"swapper"`; and marks the initial thread-info storage with `__init_thread_info`.

Control flow: No runtime functions. The macros expand into the compile-time initializer for `init_task` and related structures.

State/persistence: The referenced files/fs/nsproxy objects and swapper task identity are permanent baseline kernel state.

Dependencies/integration: Includes RCU, IRQ flags, UTS, lockdep, ftrace, IPC, PID/user/net namespaces, securebits, seqlock, rbtree, refcount, scheduler, livepatch, mm types, and architecture thread info.

Risks: The initial task identity and thread-info placement are early-boot critical; accounting macro changes must match scheduler fields.

Test signals: Successful boot, virtual CPU accounting config builds, `comm` showing swapper for PID 0, and architecture thread-info alignment checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/init_task.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/initrd.h -->
# sources/distributed-fs/ceph-client/include/linux/initrd.h

Purpose: Declares initrd/initramfs global state and helpers.

Important APIs/types/functions: Externs include `initrd_start`, `initrd_end`, `initrd_below_start_ok`, `initrd_start` resource ranges on some architectures, and `phys_initrd_start`/`phys_initrd_size`. Functions include `initrd_load()`, optional `initrd_memblock_reserve()`, `free_initrd_mem()`, and `early_initrdmem()` depending on configuration.

Control flow: Early boot records and reserves initrd memory; later rootfs/initramfs setup loads it and frees memory when allowed.

State/persistence: Initrd physical/virtual ranges persist during boot and may be freed after unpack/load.

Dependencies/integration: Integrates bootmem/memblock, rootfs, architecture boot protocols, and init memory freeing.

Risks: Incorrect range reservation can overwrite initrd or leak memory; physical/virtual address confusion is architecture-sensitive.

Test signals: Boot with and without initrd, high/low memory placement, memblock reservation logs, rootfs unpack success, and free-initrd memory accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/initrd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/inotify.h -->
# sources/distributed-fs/ceph-client/include/linux/inotify.h

Purpose: Defines the kernel mask of all valid inotify bits around the UAPI inotify interface.

Important APIs/types/functions: Includes `uapi/linux/inotify.h` and defines `ALL_INOTIFY_BITS`, the OR of access, modify, attrib, close, open, move, create/delete, self-delete/move, unmount, queue-overflow, ignored, and modifier bits such as `IN_ONLYDIR`, `IN_DONT_FOLLOW`, `IN_EXCL_UNLINK`, `IN_MASK_ADD`, `IN_MASK_CREATE`, `IN_ISDIR`, and `IN_ONESHOT`.

Control flow: Inotify setup code uses the aggregate mask to validate requested watch masks before creating fsnotify marks.

State/persistence: Header owns no state; inotify marks and event queues live in fsnotify/inotify implementations.

Dependencies/integration: Integrates with fsnotify, file descriptors, inode watches, and UAPI masks.

Risks: Omitting a valid bit rejects legal userspace requests; including unsupported bits allows invalid watch configuration.

Test signals: inotify add/remove watch, invalid mask errors, ignored event handling, and fsnotify event delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/inotify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input.h -->
# sources/distributed-fs/ceph-client/include/linux/input.h

Purpose: Main in-kernel input subsystem interface for devices, handlers, handles, events, absolute axes, polling, grabs, timestamps, and force feedback.

Important APIs/types/functions: `struct input_value`, `enum input_clock_type`, `struct input_dev`, `input_handler`, `input_handle`, and `ff_device` define device capabilities/state, event routing, open/close, keymaps, polling, multi-touch, autorepeat, locking, and force-feedback effects. APIs allocate/register/unregister devices and handlers, open/close handles, grab/release, inject/report events, configure abs axes, keycodes, softrepeat, timestamps, polling intervals, minors, force feedback, and memless FF.

Control flow: Drivers allocate/register `input_dev`; handlers connect and open handles; drivers call `input_event()` or report helpers; core batches events to handlers until `input_sync()`. Open/close transitions start or stop hardware.

State/persistence: `input_dev` persists across registration and holds capability bitmaps, current key/LED/switch state, abs info, queued values, timestamps, users, locks, and device-model object.

Dependencies/integration: Depends on UAPI input ids/events, device model, fs, timers, lists, mod_devicetable, multitouch, and force feedback.

Risks: Event callbacks run under spinlock and cannot sleep; capability/keymap bitmaps must match UAPI/mod_devicetable limits; unregister/open races require mutex and going-away handling.

Test signals: Device registration, evdev event delivery, grabs, inhibit/uninhibit, keymap ioctls, polling, abs configuration, force-feedback upload/play/erase, and lockdep for callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/ad714x.h -->
# sources/distributed-fs/ceph-client/include/linux/input/ad714x.h

Purpose: Defines board data for Analog Devices AD714x capacitive sensors used as buttons, sliders, scroll wheels, and touchpads.

Important APIs/types/functions: Constants describe 12 stages, 8 stage config registers, and 8 system config registers. Platform structs define slider/wheel stage ranges and max coordinate, touchpad X/Y stage ranges and dimensions, button keycode and threshold masks, and global `ad714x_platform_data` with counts, arrays, register initialization tables, and IRQ flags.

Control flow: Driver probe consumes platform data to program stage/system registers and create input capabilities for each declared control.

State/persistence: Board data is static; programmed sensor register state persists in hardware.

Dependencies/integration: Integrates with input key/abs event reporting and platform/IRQ setup.

Risks: Stage ranges and masks are board-specific; bad tables mis-detect touches or map buttons incorrectly.

Test signals: Probe with each control type, input event generation, coordinate range validation, IRQ polarity, and register programming readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/ad714x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/adxl34x.h -->
# sources/distributed-fs/ceph-client/include/linux/input/adxl34x.h

Purpose: Supplies platform configuration for ADXL34x digital accelerometer input drivers.

Important APIs/types/functions: `struct adxl34x_platform_data` captures axis offsets, tap/double-tap axis and timing thresholds, activity/inactivity AC/DC and axis masks, free-fall threshold/time, data rate, range/full-resolution mode, low-power/power behavior, FIFO mode, watermark, interrupt mapping, event codes, and optional platform callbacks. Macros define bit positions and ranges for tap, activity, full-resolution, g range, FIFO, and interrupt behavior.

Control flow: Probe applies board data to sensor registers and input capabilities; interrupt paths report configured tap/activity/free-fall/motion events.

State/persistence: Configuration persists in hardware registers; platform callback state is external.

Dependencies/integration: Depends on input event codes and board-specific device data.

Risks: Many zero values disable or destabilize detection; data rate versus bus speed can drop samples.

Test signals: Register programming, tap/activity/free-fall event tests, range/resolution reporting, FIFO watermark IRQs, and suspend/resume power callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/adxl34x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/as5011.h -->
# sources/distributed-fs/ceph-client/include/linux/input/as5011.h

Purpose: Defines platform data for AS5011 joystick/axis input devices.

Important APIs/types/functions: `struct as5011_platform_data` provides axis IRQ number, IRQ flags, and positive/negative threshold values for X and Y axes.

Control flow: Driver probe uses thresholds and IRQ config; interrupt or polling paths convert axis movement into input events.

State/persistence: Static platform data persists for device lifetime; threshold programming may persist in hardware.

Dependencies/integration: Integrates platform IRQ setup and input relative/absolute axis reporting.

Risks: Signed threshold chars are board calibration data; wrong values create dead zones or noisy events.

Test signals: Axis IRQ handling, threshold boundary movement, probe without IRQ, and input axis event validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/as5011.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/cma3000.h -->
# sources/distributed-fs/ceph-client/include/linux/input/cma3000.h

Purpose: Defines platform data and mode/range constants for the VTI CMA3000 accelerometer input driver.

Important APIs/types/functions: Mode constants cover default, measurement rates, motion detect, free fall, and power-off. Range constants encode 2g and 8g. `struct cma3000_platform_data` includes fuzz per axis, g range, operating mode, motion/free-fall thresholds/timers, and IRQ flags.

Control flow: Probe configures operating mode, range, thresholds, and input abs fuzz; IRQ or poll paths report acceleration/motion/free-fall.

State/persistence: Platform values are static; programmed mode/range/threshold state persists in the sensor.

Dependencies/integration: Integrates input absolute axes and platform interrupt configuration.

Risks: Mode/range mismatch changes units and event sensitivity; threshold values are hardware-specific bytes.

Test signals: Probe in all modes, 2g/8g scaling, fuzz propagation, IRQ event delivery, and power-off transition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/cma3000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/elan-i2c-ids.h -->
# sources/distributed-fs/ceph-client/include/linux/input/elan-i2c-ids.h

Purpose: Provides the ACPI device-id whitelist shared by Elan I2C/SMBus touchpad drivers.

Important APIs/types/functions: Static `elan_acpi_id[]` lists supported ACPI HID strings from `ELAN0000`, `ELAN0100`, many `ELAN06xx` devices, and `ELAN1000`, terminated by an empty entry. One known-bad `ELAN061B` entry is intentionally commented out.

Control flow: Driver ACPI matching uses the table to bind supported touchpads.

State/persistence: The match table is static const metadata and may be exported through module device tables by users.

Dependencies/integration: Depends on `linux/mod_devicetable.h` and ACPI/I2C input driver matching.

Risks: Adding/removing ids changes hardware binding; known-bad ids should remain excluded unless validated.

Test signals: ACPI modalias matching, affected laptop probe, non-matching device rejection, and module autoload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/elan-i2c-ids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/kxtj9.h -->
# sources/distributed-fs/ceph-client/include/linux/input/kxtj9.h

Purpose: Defines board data for Kionix KXTJ9 accelerometer input drivers.

Important APIs/types/functions: `KXTJ9_I2C_ADDR` gives the default address. `struct kxtj9_platform_data` includes minimum and initial poll interval, axis remapping, per-axis negation, resolution selection, g range, and optional init/exit/power callbacks. Macros define 8/12-bit resolution and 2g/4g/8g ranges.

Control flow: Probe configures orientation, polling, resolution/range, and power; report paths remap/negate raw axes before input events.

State/persistence: Board orientation and callbacks persist for device lifetime; resolution/range/power state is hardware state.

Dependencies/integration: Integrates I2C, input polling, platform power management, and absolute axis reporting.

Risks: Axis maps must be a valid permutation; power callbacks can fail during resume/probe.

Test signals: Orientation matrix equivalents, polling interval limits, g range scaling, suspend/resume callbacks, and input axis direction tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/kxtj9.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/lm8333.h -->
# sources/distributed-fs/ceph-client/include/linux/input/lm8333.h

Purpose: Public interface for LM8333 keypad driver platform data and low-level register access helpers.

Important APIs/types/functions: `struct lm8333_platform_data` references a matrix keymap and supplies active timeout and debounce time in microseconds. Extern helpers `lm8333_read8()`, `lm8333_write8()`, and `lm8333_read_block()` allow command-based I/O through an opaque `struct lm8333`.

Control flow: Probe consumes matrix data and timing; driver/keypad code uses helpers for register reads, writes, and block scans.

State/persistence: Platform timing/keymap persists for device lifetime; register state lives in hardware.

Dependencies/integration: Integrates matrix keypad keymaps and input key reporting.

Risks: Debounce/active timings affect missed or repeated keys; helper users must handle negative I/O errors.

Test signals: Matrix keymap parsing, debounce behavior, HALT/active transitions, block read scan data, and I2C error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/lm8333.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/matrix_keypad.h -->
# sources/distributed-fs/ceph-client/include/linux/input/matrix_keypad.h

Purpose: Provides generic helpers and encoding for matrix keypad keymaps.

Important APIs/types/functions: `MATRIX_MAX_ROWS/COLS`, `KEY(row,col,val)`, `KEY_ROW()`, `KEY_COL()`, `KEY_VAL()`, and `MATRIX_SCAN_CODE()` encode/decode matrix positions. `struct matrix_keymap_data` stores an encoded keymap array. `matrix_keypad_build_keymap()` builds an input keymap and capabilities; `matrix_keypad_parse_properties()` reads rows/cols from firmware/device properties.

Control flow: Keypad drivers parse firmware or platform keymap during probe, then convert row/col scan results to keycodes.

State/persistence: The built keymap persists in the input device; source map may be static platform data.

Dependencies/integration: Depends on input devices, firmware properties, and key code UAPI.

Risks: Row/column limits are 32 each; row_shift must match scanner encoding or keys map incorrectly.

Test signals: Keymap build from platform and firmware, boundary rows/cols, duplicate/invalid entries, and scan-to-key event tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/matrix_keypad.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/mt.h -->
# sources/distributed-fs/ceph-client/include/linux/input/mt.h

Purpose: Defines the input multitouch slot tracking library.

Important APIs/types/functions: Flags describe pointer/direct devices, unused contact dropping, in-kernel tracking, semi-MT, and total force. `struct input_mt_slot` stores ABS_MT values, frame, and key. `struct input_mt` stores next tracking id, slot count/current slot, flags, frame, reduced cost matrix, and flexible slot array. Helpers set/get slot values, test active/used slots, initialize/destroy slots, allocate tracking ids, report slot state/finger count/pointer emulation, drop unused slots, sync frames, assign slots from positions, and look up slots by key.

Control flow: Touch drivers initialize slots, report per-contact slot state and ABS_MT values each frame, call sync helpers, and optionally use assignment/tracking helpers.

State/persistence: Slot state persists across frames to maintain tracking ids and contact continuity.

Dependencies/integration: Depends on core input event reporting and ABS_MT UAPI ranges.

Risks: Failing to sync/drop unused slots leaves stale touches; incorrect slot assignment causes pointer jumps.

Test signals: Multi-finger tracking, contact add/remove/reorder, pointer emulation, semi-MT devices, and tracking-id wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/mt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/samsung-keypad.h -->
# sources/distributed-fs/ceph-client/include/linux/input/samsung-keypad.h

Purpose: Defines platform data for Samsung matrix keypad controllers.

Important APIs/types/functions: `SAMSUNG_MAX_ROWS` and `SAMSUNG_MAX_COLS` set 8x8 limits. `struct samsung_keypad_platdata` carries matrix keymap data, row/column counts, autorepeat disable flag, wakeup capability, and optional GPIO configuration callback.

Control flow: Probe configures GPIOs, builds keymap, sets input repeat/wakeup behavior, and scans rows/cols.

State/persistence: Platform data persists for the controller lifetime; wakeup and GPIO settings persist across power states.

Dependencies/integration: Depends on generic matrix keypad helpers and input key reporting.

Risks: GPIO callback must match row/col counts; wakeup settings affect suspend behavior.

Test signals: 8x8 boundary keymaps, no-autorepeat behavior, wake-from-suspend, and GPIO setup invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/samsung-keypad.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/sh_keysc.h -->
# sources/distributed-fs/ceph-client/include/linux/input/sh_keysc.h

Purpose: Defines platform information for SuperH key scan controller drivers.

Important APIs/types/functions: `SH_KEYSC_MAXKEYS` sets a 64-key map. `struct sh_keysc_info` includes one of six scan modes, scan timing, delay values, KYCR2 delay, and keycodes for the KEYIN x KEYOUT matrix.

Control flow: Driver probe programs scan mode/timing and uses keycodes to translate scan results into input events.

State/persistence: Platform scan/keymap settings persist for the controller lifetime.

Dependencies/integration: Integrates SH platform code and input key events.

Risks: Mode and timing values must match board wiring; bad delay settings can cause missed/ghost keys.

Test signals: Each scan mode, max key map, key press/release matrix events, and timing variation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/sh_keysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/sparse-keymap.h -->
# sources/distributed-fs/ceph-client/include/linux/input/sparse-keymap.h

Purpose: Provides sparse keymap support for devices whose scancodes are not dense matrix/table indices.

Important APIs/types/functions: Entry types include key, fixed switch, variable switch, ignored entry, and terminator. `struct key_entry` maps device-specific code to keycode or switch code/value. APIs find entries by scancode or keycode, set up a sparse keymap with optional per-entry setup, report a specific entry, and report by scancode with optional autorelease.

Control flow: Drivers install a sparse keymap at probe, then report events by hardware code; helpers translate and emit input events.

State/persistence: Keymap entries are attached to the input device keycode storage for its lifetime.

Dependencies/integration: Depends on input key/switch UAPI and input device keycode mechanisms.

Risks: Ignored and variable switch entries need deliberate handling to avoid false events.

Test signals: Lookup by scancode/keycode, autorelease keys, fixed and variable switches, ignored entries, and setup callback failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/sparse-keymap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/touch-overlay.h -->
# sources/distributed-fs/ceph-client/include/linux/input/touch-overlay.h

Purpose: Declares helper APIs for mapping touchscreen contacts through overlay regions.

Important APIs/types/functions: `touch_overlay_map()` associates overlay data with an input device. `touch_overlay_get_touchscreen_abs()` retrieves adjusted absolute ranges. `touch_overlay_mapped_touchscreen()` reports whether overlays exist. `touch_overlay_process_contact()` transforms or filters per-slot `input_mt_pos` contacts. `touch_overlay_sync_frame()` completes frame processing.

Control flow: Touchscreen drivers parse/map overlays, process each contact before reporting, then sync overlay state each frame.

State/persistence: Overlay definitions live in the passed list; per-frame/contact state is managed by implementation code.

Dependencies/integration: Depends on input devices, multitouch positions, list heads, and touchscreen firmware/property parsing.

Risks: Coordinate transforms must match input abs ranges; slot-specific filtering can drop contacts if sync is mishandled.

Test signals: Overlay mapped/unmapped devices, transformed coordinates, filtered contacts, multitouch slot behavior, and frame sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/touch-overlay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/touchscreen.h -->
# sources/distributed-fs/ceph-client/include/linux/input/touchscreen.h

Purpose: Provides common touchscreen property parsing and coordinate transformation helpers.

Important APIs/types/functions: `struct touchscreen_properties` stores max X/Y, invert flags, and axis swap flag. `touchscreen_parse_properties()` reads standard properties into the struct. `touchscreen_set_mt_pos()` transforms raw X/Y into an `input_mt_pos`. `touchscreen_report_pos()` reports transformed single-touch or multitouch positions.

Control flow: Drivers parse properties at probe and apply transformations to every contact report.

State/persistence: Parsed properties persist in driver state; no state is owned by the header.

Dependencies/integration: Integrates input abs axes, multitouch helpers, firmware properties, and touchscreen drivers.

Risks: Transform order and max values must match hardware orientation; wrong multitouch flag changes reported event type.

Test signals: Invert X/Y, swap axes, max-boundary coordinates, single-touch versus multitouch reporting, and property absence defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/touchscreen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/tps6507x-ts.h -->
# sources/distributed-fs/ceph-client/include/linux/input/tps6507x-ts.h

Purpose: Defines board initialization data for TPS65070/TPS6507x touchscreen support.

Important APIs/types/functions: `struct touchscreen_init_data` supplies polling period in milliseconds, minimum pressure threshold, and input id vendor/product/version.

Control flow: Driver probe uses the struct to configure polling cadence, touch qualification, and input device identity.

State/persistence: Board data persists for device lifetime; polling and pressure thresholds guide runtime event reporting.

Dependencies/integration: Integrates TPS6507x MFD/I2C touchscreen code and input device registration.

Risks: Too-low pressure thresholds create false touches; too-slow polling harms responsiveness.

Test signals: Poll interval behavior, min-pressure boundary, input id values, and no-touch versus touch transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/tps6507x-ts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/vivaldi-fmap.h -->
# sources/distributed-fs/ceph-client/include/linux/input/vivaldi-fmap.h

Purpose: Defines ChromeOS Vivaldi keyboard function-row physical map data and sysfs formatting.

Important APIs/types/functions: `VIVALDI_MAX_FUNCTION_ROW_KEYS` caps maps at 24 entries. `struct vivaldi_data` stores function-row physical scancodes/HID usages in left-to-right order and a count. `vivaldi_function_row_physmap_show()` formats the map into a buffer.

Control flow: Keyboard drivers populate `vivaldi_data` and expose/show the function row map for userspace policy.

State/persistence: The map persists as keyboard metadata for the device lifetime.

Dependencies/integration: Depends on input keyboard drivers and ChromeOS top-row key semantics.

Risks: Incorrect order or count breaks userspace key labeling and remapping.

Test signals: Sysfs/show output, max-key boundary, HID/scancode mapping order, and devices without custom function rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/vivaldi-fmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/instruction_pointer.h -->
# sources/distributed-fs/ceph-client/include/linux/instruction_pointer.h

Purpose: Provides generic instruction-pointer capture macros for tracing and diagnostics.

Important APIs/types/functions: `_RET_IP_` expands to `__builtin_return_address(0)` as an unsigned long. `_THIS_IP_` uses a local label address to identify the current code location unless an architecture has already supplied it.

Control flow: Call sites expand the macros inline to capture return or current instruction addresses without a function call.

State/persistence: Stateless macro expansion over compiler-provided code addresses.

Dependencies/integration: Includes `asm/linkage.h` and is used by tracing, logging, warning, and profiling code that records call sites.

Risks: Return-address availability depends on compiler and frame layout; `_THIS_IP_` relies on local label address support.

Test signals: Architecture builds, WARN/trace call-site reporting, ftrace/perf samples, and compiler configurations with frame-pointer variations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/instruction_pointer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/instrumentation.h -->
# sources/distributed-fs/ceph-client/include/linux/instrumentation.h

Purpose: Defines annotation macros that mark code regions where compiler or runtime instrumentation is allowed or forbidden.

Important APIs/types/functions: Macros such as `instrumentation_begin()` and `instrumentation_end()` create annotation boundaries; validation helpers interact with objtool/KCSAN/KASAN-style instrumentation constraints depending on configuration.

Control flow: Low-level entry/exit, noinstr, and sensitive code bracket instrumentable sections so tooling can validate that unsafe instrumentation is absent.

State/persistence: No runtime state in normal builds; annotations become metadata or compiler barriers/tool hints.

Dependencies/integration: Integrates compiler attributes, objtool validation, tracing, sanitizers, and architecture entry code.

Risks: Missing or misplaced annotations can introduce recursion, tracing in noinstr paths, or false validation failures.

Test signals: Objtool noinstr validation, sanitizer-enabled builds, ftrace/perf entry tests, and architecture entry smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/instrumentation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/instrumented.h -->
# sources/distributed-fs/ceph-client/include/linux/instrumented.h

Purpose: Supplies wrappers around memory and MMIO accesses that notify kernel instrumentation frameworks such as KASAN, KCSAN, and KMSAN.

Important APIs/types/functions: Inline helpers cover reads/writes, reads-before-writes, atomic reads/writes, bit operations, memset/memcpy-style effects, and MMIO variants, usually calling sanitizer hooks before or after real access depending on configuration.

Control flow: Low-level primitives include these wrappers so dynamic analyzers observe memory access semantics while production builds compile away inactive hooks.

State/persistence: No direct state; sanitizer runtimes maintain shadow state externally.

Dependencies/integration: Depends on compiler instrumentation, sanitizer headers, atomic/bitop implementations, and MMIO access code.

Risks: Missing instrumentation hides data races or invalid memory use; instrumenting truly noinstr paths can be unsafe.

Test signals: KASAN/KCSAN/KMSAN builds, race/use-after-free test modules, atomic bitop instrumentation, and MMIO access smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/instrumented.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/int_log.h -->
# sources/distributed-fs/ceph-client/include/linux/int_log.h

Purpose: Declares integer logarithm helpers for base-2 and base-10 style computations.

Important APIs/types/functions: Typically exposes `intlog2()`, `intlog10()`, or related fixed-point integer log helpers used by kernel subsystems needing approximate logarithms without floating point.

Control flow: Callers pass integer values and receive scaled integer logarithm results; no persistent control flow exists in the header.

State/persistence: Stateless math helpers.

Dependencies/integration: Used by drivers and core code that cannot use floating point in kernel context.

Risks: Scaling and zero-input behavior must be understood by callers; approximate integer math can overflow if inputs exceed expected range.

Test signals: Known-value log2/log10 vectors, zero/one boundaries, max integer inputs, and no-floating-point compile checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/int_log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/integrity.h -->
# sources/distributed-fs/ceph-client/include/linux/integrity.h

Purpose: Declares common integrity subsystem interfaces for xattr-based file metadata and inode attribute change detection.

Important APIs/types/functions: Functions include integrity inode get/set xattr helpers, removal hooks, and `integrity_inode_attrs_changed()` for detecting changes in integrity-relevant inode attributes. `struct integrity_inode_attributes` carries tracked inode metadata fields.

Control flow: Integrity and LSM paths call helpers when reading/writing security xattrs or deciding whether cached appraisal data remains valid.

State/persistence: Integrity metadata persists in filesystem xattrs and cached inode security blobs; this header owns no storage.

Dependencies/integration: Integrates VFS inodes, xattrs, IMA/EVM integrity appraisal, and security hooks.

Risks: Attribute-change detection must match appraisal policy or stale measurements may be trusted.

Test signals: Security xattr get/set/remove, chmod/chown metadata changes, IMA/EVM appraisal invalidation, and filesystems without xattr support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/integrity.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel-ish-client-if.h -->
# sources/distributed-fs/ceph-client/include/linux/intel-ish-client-if.h

Purpose: Defines the client-driver interface for Intel Integrated Sensor Hub Transport Protocol devices.

Important APIs/types/functions: `enum cl_state` models client connection state. `struct ishtp_cl_driver` is the bus driver object with probe/remove/reset callbacks and id table. `struct ishtp_msg_data` and `ishtp_cl_rb` model messages and receive buffers. APIs register drivers, register event callbacks, allocate/link/connect/disconnect/destroy clients, send data, flush/recycle queues, get RX buffers, set client data, access ISHTP/PCI/workqueue devices, change ring sizes/state/FW client id, and reset hardware.

Control flow: Client drivers bind to firmware clients, allocate/link a client, establish connection, receive callbacks/RBs, send messages, and disconnect/unlink on remove/reset.

State/persistence: Connection state, rings, client data, receive buffers, and firmware-client ids persist per client connection.

Dependencies/integration: Depends on device model, mod_devicetable, GUID firmware clients, PCI parent devices, and workqueues.

Risks: Duplicate `ishtp_register_event_cb()` declarations hint at ABI sensitivity; queue ownership and recycle discipline are critical.

Test signals: Driver bind/unbind, connect/disconnect, send/receive loopback, reset recovery, ring size changes, and RB recycle leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel-ish-client-if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_dg_nvm_aux.h -->
# sources/distributed-fs/ceph-client/include/linux/intel_dg_nvm_aux.h

Purpose: Defines auxiliary-bus data for Intel discrete graphics NVM devices.

Important APIs/types/functions: `INTEL_DG_NVM_REGIONS` sets a 13-region limit. `struct intel_dg_nvm_region` stores an MMIO/resource area and identifier. `struct intel_dg_nvm_dev` embeds an auxiliary device, region array/count, and writeable flag. `auxiliary_dev_to_intel_dg_nvm_dev()` maps from aux device to container.

Control flow: Parent graphics drivers populate regions and create an auxiliary device; NVM auxiliary drivers retrieve the container and access regions.

State/persistence: Region descriptors and writeability persist for the aux device lifetime.

Dependencies/integration: Depends on auxiliary bus, resources, container_of, and Intel graphics NVM drivers.

Risks: Region count must not exceed fixed array; incorrect writeable flag exposes unsafe writes.

Test signals: Aux device probe/remove, region enumeration, read-only versus writeable operations, and bounds checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_dg_nvm_aux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_pmt_features.h -->
# sources/distributed-fs/ceph-client/include/linux/intel_pmt_features.h

Purpose: Defines Intel Platform Monitoring Technology feature ids, capability bits, layouts, and exported capability tables.

Important APIs/types/functions: `PMT_CAP_*` bits describe telemetry, watcher, crashlog, streaming, threshold, security, TPMI, trace, energy, and feature-specific capabilities. `enum pmt_feature_id` and `enum feature_layout` identify feature groups and data layouts. `struct pmt_cap` maps capability bit to name. Extern arrays provide names and capability sets for common, PCPT, PCET, RMID, accel, uncore, crashlog, PETE, TPMI, S3M, tracing, and energy. `pmt_feature_id_is_valid()` bounds-checks ids.

Control flow: PMT discovery and sysfs/debug code select feature layout/capability tables by id.

State/persistence: Tables are const exported data; device-specific capabilities live elsewhere.

Dependencies/integration: Depends on bit helpers and Intel VSEC/PMT telemetry drivers.

Risks: Capability bit reuse is feature-specific; interpreting a bit with the wrong table mislabels hardware.

Test signals: Feature id validation, sysfs capability names, discovery of each feature class, and table bounds tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_pmt_features.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_rapl.h -->
# sources/distributed-fs/ceph-client/include/linux/intel_rapl.h

Purpose: Defines common data structures and interfaces for Intel RAPL power/energy limiting across MSR, MMIO, and TPMI backends.

Important APIs/types/functions: Enums model interface type, domain type, domain registers, primitives, and units. `struct rapl_domain_data`, `rapl_power_limit`, `rapl_domain`, `reg_action`, `rapl_defaults`, `rapl_primitive_info`, `rapl_if_priv`, optional `rapl_package_pmu_data`, and `rapl_package` represent domains, registers, constraints, units, primitive metadata, package topology, CPU hotplug, and PMU state. APIs find/add/remove packages, check units, set floor frequency, compute time windows, and add/remove PMUs under `CONFIG_PERF_EVENTS`.

Control flow: Backend drivers register interface callbacks and packages; common RAPL code reads/writes primitives, exposes powercap zones, handles hotplug, and optionally registers PMU energy counters.

State/persistence: Package/domain state persists while CPUs/packages are online; energy counters and power limits reflect hardware registers and powercap constraints.

Dependencies/integration: Integrates powercap, CPU hotplug, perf events, hrtimers, cpumasks, MSR/MMIO/TPMI backends.

Risks: Unit conversion and time-window encoding are platform-specific; package hotplug locking variants must be used in the right context.

Test signals: Powercap zone creation, limit read/write, energy counter updates, CPU hotplug add/remove, perf PMU events, and MSR/MMIO/TPMI backend parity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_rapl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_tcc.h -->
# sources/distributed-fs/ceph-client/include/linux/intel_tcc.h

Purpose: Declares Intel Thermal Control Circuit helpers for CPU temperature and TjMax offset handling.

Important APIs/types/functions: `intel_tcc_get_tjmax()`, `intel_tcc_get_offset()`, `intel_tcc_set_offset()`, `intel_tcc_get_temp()`, and `intel_tcc_get_offset_mask()`.

Control flow: Thermal and platform drivers query TjMax/offset, optionally set offset, and read package or core temperatures.

State/persistence: TCC offset is hardware/MSR state; temperature readings are transient.

Dependencies/integration: Integrates CPU thermal drivers, MSR/platform code, and thermal zones.

Risks: Offset writes affect thermal throttling behavior; CPU/package selection must be correct.

Test signals: Per-CPU TjMax reads, offset mask enforcement, set/get offset roundtrip where permitted, core/package temperature reads, and unsupported CPU errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_tcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_th.h -->
# sources/distributed-fs/ceph-client/include/linux/intel_th.h

Purpose: Defines Intel Trace Hub MSU buffer provider interface.

Important APIs/types/functions: Buffer capability enum values identify buffer direction/features. `struct msu_buffer` describes name, owner, ops/callbacks, allocation/free/activate/deactivate behavior, window locking, and scatterlist backing. APIs register/unregister MSU buffer providers and unlock MSC windows. `module_intel_th_msu_buffer()` creates module init/exit for a provider.

Control flow: Buffer modules register an `msu_buffer`; Trace Hub core calls provider callbacks to allocate and manage trace capture windows.

State/persistence: Buffer provider registration persists until module exit; allocated scatter-gather windows persist while trace capture is active.

Dependencies/integration: Depends on scatterlist, device model, module lifecycle, and Intel TH/MSC code.

Risks: Window lock/unlock and SG ownership must match DMA/capture lifetime or traces corrupt.

Test signals: Module register/unregister, trace capture allocation/free, window unlock, and active capture teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_th.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_tpmi.h -->
# sources/distributed-fs/ceph-client/include/linux/intel_tpmi.h

Purpose: Declares Intel TPMI version/id helpers, notifications, and auxiliary-device resource accessors.

Important APIs/types/functions: Version macros extract major/minor fields; `enum intel_tpmi_id` identifies TPMI services. Constants `TPMI_CORE_INIT` and `TPMI_CORE_EXIT` label notifier events. APIs register/unregister notifiers, get platform data, resource by index/count, feature status including read/write blocks, and debugfs directory.

Control flow: TPMI core notifies clients about init/exit; auxiliary drivers query resources and feature status before accessing hardware.

State/persistence: Platform data/resources are attached to auxiliary devices; notifier registrations persist until removed.

Dependencies/integration: Depends on bitfield helpers, auxiliary devices, debugfs, Intel VSEC/OOBMSM platform data.

Risks: Feature read/write block flags must be obeyed to avoid illegal MMIO access.

Test signals: Notifier order, resource count/index bounds, version extraction, feature blocked status, and debugfs directory presence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_tpmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_vsec.h -->
# sources/distributed-fs/ceph-client/include/linux/intel_vsec.h

Purpose: Defines Intel VSEC/DVSEC discovery, auxiliary-device, PMT telemetry, and OOBMSM platform interfaces.

Important APIs/types/functions: Capability bits cover telemetry, watcher, crashlog, SDSI, TPMI, and discovery. DVSEC macros extract table BAR/offset. Enums identify discovery source and VSEC ids. `struct intel_vsec_header`, quirks, `pmt_callbacks`, feature dependencies, `intel_vsec_platform_info`, `intel_vsec_device`, `oobmsm_plat_info`, `telemetry_region`, and `pmt_feature_group` model discovery metadata, resources, aux devices, dependencies, callbacks, and grouped telemetry regions. APIs add aux devices, register VSEC platform info, set/get mappings, and acquire/release PMT feature groups with Kconfig stubs.

Control flow: Parent PCI/ACPI drivers discover VSEC headers, register platform info, create auxiliary devices, then PMT clients query telemetry regions by feature.

State/persistence: Aux devices, resources, ida ids, mappings, telemetry regions, and kref-counted feature groups persist while registered.

Dependencies/integration: Depends on auxiliary bus, PCI resources, PMT feature tables, krefs, debugfs, and Kconfig.

Risks: Discovery quirks and source-specific tables must be interpreted correctly; feature group references require balanced put.

Test signals: PCI and ACPI discovery, aux device creation/removal, quirk paths, mapping lookup, PMT telemetry get/put, and disabled-config stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_vsec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/interconnect-clk.h -->
# sources/distributed-fs/ceph-client/include/linux/interconnect-clk.h

Purpose: Declares helpers for registering clocks as interconnect providers.

Important APIs/types/functions: `struct icc_clk_data` maps interconnect ids/names to clocks and bandwidth behavior. APIs `icc_clk_register()`, `devm_icc_clk_register()`, and `icc_clk_unregister()` create and destroy an interconnect provider backed by clock controls.

Control flow: Clock/interconnect glue drivers register provider data at probe; consumers request ICC bandwidth and provider code translates it into clock rates.

State/persistence: Provider state persists until unregister or devm cleanup.

Dependencies/integration: Integrates clock framework, interconnect provider framework, and device-managed resources.

Risks: Bandwidth-to-clock mapping must be conservative enough for consumers; unregister while paths are active can break constraints.

Test signals: Provider registration, consumer `icc_set_bw()` changing clock rates, devm cleanup, and disabled provider paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/interconnect-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/interconnect-provider.h -->
# sources/distributed-fs/ceph-client/include/linux/interconnect-provider.h

Purpose: Defines provider-side interconnect topology objects, aggregation callbacks, registration APIs, and disabled-config stubs.

Important APIs/types/functions: `icc_units_to_bps()` converts ICC units to Bps. `struct icc_node_data`, `icc_onecell_data`, `icc_provider`, and `icc_node` model phandle translation, one-cell data, provider callbacks, users, inter-provider behavior, topology links, traversal state, request lists, and aggregated/init bandwidth. APIs create/destroy/link/add/delete nodes, remove provider nodes, initialize/register/deregister providers, aggregate standard bandwidth, translate OF phandles, and sync state.

Control flow: Provider drivers create nodes, link topology, register provider callbacks, then consumer requests are aggregated and passed to provider `set()` callbacks.

State/persistence: Provider and node lists persist while registered; node request lists and aggregated bandwidth change with active consumers.

Dependencies/integration: Depends on interconnect consumer API, device tree phandles, device model, lists, hlist, and `CONFIG_INTERCONNECT`.

Risks: Disabled stubs return mixed `-ENOTSUPP`/`-EOPNOTSUPP`; topology cycles or bad links can break path search.

Test signals: Provider registration, OF translation, path requests across linked nodes, aggregation math, sync_state, deregistration cleanup, and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/interconnect-provider.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/interconnect.h -->
# sources/distributed-fs/ceph-client/include/linux/interconnect.h

Purpose: Defines consumer-side Linux interconnect APIs for acquiring paths and setting bandwidth constraints.

Important APIs/types/functions: Unit conversion macros convert Bps/kBps/MBps/GBps and bit rates into ICC units. `ICC_ALLOC_DYN_ID` requests dynamic node ids. `struct icc_bulk_data` stores path, firmware name, average bandwidth, and peak bandwidth. APIs get/put paths by name or index, devm/bulk get paths, enable/disable paths, set bandwidth and tags, get names, and bulk set/enable/disable/put. Disabled builds return NULL or success no-ops.

Control flow: Consumer drivers acquire paths at probe, set avg/peak bandwidth around runtime needs, enable/disable paths with device activity, and release paths on remove.

State/persistence: `icc_path` state is opaque and persists from get to put; bulk data stores desired bandwidths.

Dependencies/integration: Integrates device tree interconnect properties, runtime PM, provider aggregation, and Kconfig stubs.

Risks: Disabled-config no-ops can hide missing bandwidth votes; unit conversions intentionally use kBps-like ICC units and need caller care.

Test signals: Named/indexed path lookup, bandwidth vote aggregation, bulk APIs, enable/disable ordering, provider-disabled no-op behavior, and DT property errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/interconnect.h -->
