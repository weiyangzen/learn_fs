# Research: subset-b-003885

Grouped research for Industrial I/O DAC, dummy, filter, and frequency driver files under `sources/distributed-fs/ceph-client/drivers/iio`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ti-dac082s085.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ti-dac082s085.c

Purpose: SPI IIO output driver for TI DAC082S085/DAC102S085/DAC122S085 and DAC084S085/DAC104S085/DAC124S085 families. It supports dual and quad voltage-output DACs with 8, 10, or 12 bit resolution selected through `spi_device_id.driver_data`.

Important APIs/types/functions: `struct ti_dac_spec` maps variant to channel count and resolution. `struct ti_dac_chip` stores the SPI message/transfer, Vref regulator, value cache, powerdown state, and mutex. `ti_dac_cmd()` encodes a two-byte SPI frame using command bits such as `WRITE_AND_UPDATE()` and `POWERDOWN()`. IIO callbacks are `ti_dac_read_raw()`, `ti_dac_write_raw()`, `ti_dac_write_raw_get_fmt()`, plus ext-info handlers for `powerdown` and `powerdown_mode`.

Control flow: probe allocates an IIO device, initializes a reusable SPI message backed by the aligned `buf`, resolves the variant spec, enables `vref`, writes all outputs to zero with `WRITE_ALL_UPDATE`, then registers the IIO device. Raw writes validate range and refuse writes while the chip is powered down. Powerdown writes either send a powerdown command or restore channel 0 with its cached value.

State/persistence: state is in RAM only: cached per-channel raw values, shared powerdown boolean, selected powerdown mode, and resolution. Hardware is initialized to zero on probe and regulator is disabled on remove. No nonvolatile state is programmed.

Dependencies/integration: integrates with SPI core, regulator framework, OF/SPI ID tables, and IIO direct mode. Scale derives from `regulator_get_voltage(vref)` and resolution. Sysfs exposes raw output, scale, and shared powerdown controls.

Risks: `powerdown` is shared by type even on multi-channel devices; resume from powerdown writes only channel 0, relying on device behavior rather than replaying all cached channel values. OF compatible entries do not carry `.data`, so SPI ID matching must supply variant data. Test signals include SPI frame encoding per resolution, regulator failure paths, range rejection, powerdown `-EBUSY`, and probe cleanup after initialization failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ti-dac082s085.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ti-dac5571.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ti-dac5571.c

Purpose: I2C IIO output driver for TI single-channel and quad-channel DAC557x/DAC657x/DAC757x plus DAC081C081/DAC121C081 devices. It abstracts command formatting differences between one-channel and four-channel parts.

Important APIs/types/functions: `struct dac5571_spec` identifies channel count and resolution. `struct dac5571_data` stores I2C client, regulator, mutex, per-channel value cache, per-channel powerdown cache/mode, function pointers for data write and powerdown formatting, and a DMA-safe buffer. `dac5571_cmd_single()`, `dac5571_cmd_quad()`, `dac5571_pwrdwn_single()`, and `dac5571_pwrdwn_quad()` are the hardware protocol shims. `dac5571_ext_info` exposes per-channel powerdown state and mode.

Control flow: probe obtains match data from OF/I2C tables, enables `vref`, chooses single or quad command functions, initializes every channel to zero, and registers an IIO direct-mode device. Raw reads return cached values or Vref-derived scale. Raw writes reject out-of-range values and powered-down channels, then send the correct I2C frame and update cache on success. Powerdown toggles the target channel and restores the cached value when leaving powerdown.

State/persistence: all runtime state is volatile. `val[]`, `powerdown[]`, and `powerdown_mode[]` mirror user-visible sysfs state. Hardware channels are zeroed at probe, while remove unregisters the IIO device and disables the regulator.

Dependencies/integration: depends on I2C, regulator consumer API, device property match data, and IIO sysfs/ext-info. Device tables map many compatible strings to common specs.

Risks: probe assumes `i2c_get_match_data()` is non-null; board files without OF/fwnode match data could misbehave despite `i2c_device_id` carrying pointers. I2C helpers treat short writes as `-EIO`. Powerdown-mode available is shared by type while mode itself is separate. Test signals include all variant match entries, one- vs four-channel buffer layout, per-channel powerdown isolation, regulator errors, and cache consistency after failed I2C transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ti-dac5571.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ti-dac7311.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ti-dac7311.c

Purpose: SPI IIO output driver for single-channel TI DAC5311, DAC6311, and DAC7311 devices. It provides raw voltage output, scale from Vref, and shared powerdown controls.

Important APIs/types/functions: `struct ti_dac_spec` stores resolution; `struct ti_dac_chip` holds the SPI device, Vref regulator, cached raw value, powerdown flags, and a mutex-protected two-byte transfer buffer. `ti_dac_get_power()` converts the cached powerdown mode to command bits. `ti_dac_cmd()` packs the DAC value and power bits into the device wire format. IIO callbacks implement raw read/write, integer write format, and ext-info for powerdown.

Control flow: probe forces SPI mode 1 and 16 bits per word, sets up the IIO direct-mode channel, enables Vref, initializes the mutex, and registers the device. Writes validate the raw code against the selected resolution, reject writes while powered down, and send a two-byte SPI command under lock. Powerdown writes always send a command with value zero and update the cached boolean on success.

State/persistence: the only persisted driver state is volatile RAM: one raw output cache, selected powerdown mode, powerdown boolean, and resolution. The driver does not explicitly initialize the DAC output to zero during probe, unlike some neighboring TI DAC drivers.

Dependencies/integration: integrates with SPI, regulator, IIO, OF match, and SPI modalias tables. Scale reads the live regulator voltage in millivolts with a fractional-log2 denominator based on resolution.

Risks: `ti_dac_set_powerdown_mode()` only updates the cached mode and does not reprogram hardware if already powered down; contrast with related TI drivers that update active powerdown state. `ti_dac_write_powerdown()` sends zero rather than the cached DAC value when enabling powerdown and does not restore cached output on power-up. Test signals should cover SPI setup failure, regulator cleanup, resolution-specific bit shifts, mode changes while powered down, raw write `-EBUSY`, and readback from cache.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ti-dac7311.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ti-dac7612.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ti-dac7612.c

Purpose: SPI IIO direct-mode output driver for the dual 12-bit TI DAC7612. It supports two output channels and optional driver control of the `LOADDACS` GPIO.

Important APIs/types/functions: `struct dac7612` stores the SPI device, optional `ti,loaddacs` GPIO, two cached channel values, mutex, and DMA-aligned two-byte transfer buffer. `dac7612_cmd_single()` formats a start bit, channel address, and 12-bit value, writes it over SPI, then toggles `LOADDACS` if present. `dac7612_read_raw()` and `dac7612_write_raw()` expose raw and scale IIO attributes.

Control flow: probe allocates the IIO device, obtains optional `ti,loaddacs`, initializes channels and mutex, writes zero to both channels, and registers with `devm_iio_device_register()`. Raw writes reject non-raw masks, out-of-range values, nonzero `val2`, and no-op cached values, then call the SPI/GPIO sequence under lock.

State/persistence: per-channel cache is the source for raw readback. Cache is updated inside `dac7612_cmd_single()` before the SPI transaction; a failed SPI write can leave software cache ahead of hardware. There is no regulator handling or nonvolatile state.

Dependencies/integration: depends on SPI, GPIO descriptor API, and IIO direct mode. Scale is hard-coded as integer `1`, so userspace gets a raw-code scale rather than a Vref-derived voltage scale.

Risks: optional GPIO semantics rely on `gpiod_set_value()` with possible NULL descriptor behavior; this should be confirmed against GPIO helper guarantees in the target kernel. Cache-before-write can hide failed hardware updates. The driver lacks a remove callback because resources are managed. Test signals include dual-channel addressing, initial zero writes, optional vs absent `LOADDACS`, raw bounds, cache behavior on SPI error, and OF compatibles `ti,dac7612`, `ti,dac7612u`, and `ti,dac7612ub`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ti-dac7612.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/vf610_dac.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/vf610_dac.c

Purpose: platform IIO output driver for the Freescale/NXP Vybrid VF610 on-chip DAC. It programs memory-mapped registers, exposes one voltage output channel, and supports runtime conversion-mode selection.

Important APIs/types/functions: `struct vf610_dac` contains clock, device pointer, conversion mode, MMIO base, and mutex. `vf610_dac_init()` enables DAC, selects reference, and starts in low-power mode. `vf610_dac_exit()` clears DAC enable. `vf610_set_conversion_mode()` toggles `VF610_DAC_LPEN`; `vf610_read_raw()` and `vf610_write_raw()` expose raw value and scale.

Control flow: probe allocates an IIO device, maps the MMIO resource, gets and enables the `dac` clock, sets direct-mode channel metadata, initializes the mutex, calls `vf610_dac_init()`, and registers the IIO device. Raw writes store `VF610_DAC_DAT0(val)` to the data register under lock. Suspend disables the DAC and clock; resume reenables the clock and reinitializes control bits.

State/persistence: hardware data register is read directly for raw value; conversion mode is cached in RAM and reset to low-power by `vf610_dac_init()`. Suspend/resume does not preserve the previous conversion mode or output value explicitly. Scale is hard-coded to 3300 mV / 2^12 based on datasheet assumptions.

Dependencies/integration: uses platform resources, device tree compatible `fsl,vf610-dac`, clock framework, MMIO helpers, PM ops, and IIO sysfs enum ext-info. It includes regulator headers but does not use a regulator.

Risks: raw writes mask to 12 bits instead of rejecting out-of-range or negative values. Resume may surprise users by resetting low-power mode and possibly output state depending on hardware retention. Test signals include MMIO register writes, PM suspend/resume, conversion-mode sysfs, clock failure paths, and validation of 12-bit raw write semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/vf610_dac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dummy/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/dummy/Kconfig

Purpose: Kconfig menu for IIO dummy/reference drivers. It declares the software dummy device, optional fake event generator, and optional triggered buffer support.

Important symbols: `IIO_DUMMY_EVGEN` is a hidden tristate that selects `IRQ_SIM`. `IIO_SIMPLE_DUMMY` is user-visible and depends on `IIO_SW_DEVICE`. `IIO_SIMPLE_DUMMY_EVENTS` is a bool under `IIO_SIMPLE_DUMMY` that selects `IIO_DUMMY_EVGEN`. `IIO_SIMPLE_DUMMY_BUFFER` is another bool under the dummy device that selects IIO buffer, trigger, kfifo, and triggered-buffer support.

Control flow: menu visibility depends on `IIO`. Enabling the simple dummy driver opens subordinate feature choices; event and buffer objects are compiled into the main dummy module through Makefile conditionals, while the event generator is its own module/object.

State/persistence: Kconfig state determines compile-time inclusion only. Runtime state is in the C files.

Dependencies/integration: integrates with the IIO software-device framework, IRQ simulator, and buffer/trigger subsystems. The event option couples the main dummy driver to the companion event generator.

Risks: `IIO_DUMMY_EVGEN` is selected rather than directly prompted, so it may be built solely because event support is enabled. Because `IIO_SIMPLE_DUMMY_EVENTS` and `IIO_SIMPLE_DUMMY_BUFFER` are bools, they become built-in pieces of `iio_dummy.o` rather than separately loadable add-ons. Test signals include Kconfig dependency resolution for modular and built-in combinations, ensuring event code sees exported evgen symbols, and verifying buffer dependencies are pulled in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dummy/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dummy/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/dummy/Makefile

Purpose: build rules for the IIO dummy driver family.

Important targets: `obj-$(CONFIG_IIO_SIMPLE_DUMMY) += iio_dummy.o` builds the main software dummy module. `iio_dummy-y := iio_simple_dummy.o` makes the core file mandatory. Conditional object additions include `iio_simple_dummy_events.o` and `iio_simple_dummy_buffer.o` when their Kconfig booleans are enabled. `obj-$(CONFIG_IIO_DUMMY_EVGEN) += iio_dummy_evgen.o` builds the companion fake IRQ event generator separately.

Control flow: Kbuild links optional event and buffer code into `iio_dummy.o`; this matches the header stubs in `iio_simple_dummy.h`, where disabled features become no-op inline functions. The event generator is not linked into `iio_dummy.o`, but is selected by Kconfig when events are enabled.

State/persistence: no runtime state. This file controls compile/link composition.

Dependencies/integration: depends on Kconfig symbols from the same directory. It also makes the symbol boundary between dummy core and event generator visible: `iio_dummy_evgen.c` exports IRQ helper symbols used by `iio_simple_dummy_events.c`.

Risks: misconfigured symbol combinations could produce unresolved references if Kconfig selection is changed without updating Makefile linkage. Since event and buffer options are bools, they cannot be loaded independently from the main dummy driver. Test signals include `allyesconfig`/`allmodconfig` style builds and combinations with events disabled and buffer enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dummy/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dummy/iio_dummy_evgen.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dummy/iio_dummy_evgen.c

Purpose: companion module for the IIO simple dummy driver that simulates event IRQs without hardware. It creates an IIO bus device named `iio_evgen` with `poke_ev0` through `poke_ev9` sysfs write attributes.

Important APIs/types/functions: `struct iio_dummy_eventgen` stores ten fake register records, an in-use bitmap, a mutex, and an IRQ simulation domain. `iio_dummy_evgen_get_irq()`, `iio_dummy_evgen_release_irq()`, and `iio_dummy_evgen_get_regs()` are exported for the dummy event code. `iio_evgen_poke()` parses a numeric event code, writes it into the selected fake register, and marks the mapped IRQ pending with `irq_set_irqchip_state()`.

Control flow: module init allocates singleton state, creates an IRQ sim domain, initializes a static device, names it `iio_evgen`, and adds it to `iio_bus_type`. Clients request an unused IRQ; sysfs poke files then raise the corresponding simulated interrupt. Module exit unregisters the device, whose release path removes the IRQ domain and frees state.

State/persistence: singleton RAM state tracks which fake IRQ slots are allocated and the most recent `reg_id`/`reg_data` per slot. State is not persistent and is cleared on module unload.

Dependencies/integration: depends on IIO bus/sysfs helpers, IRQ domains, IRQ simulation, exported GPL symbols, and dummy event consumers. It bridges user-triggered sysfs writes to kernel IRQ delivery.

Risks: `iio_dummy_evgen_release_irq()` assumes a valid singleton and valid IRQ data; misuse by a stale client can dereference invalid data. `iio_evgen_poke()` does not check whether an IRQ mapping exists before setting pending state. Allocation marks `inuse[i]` true without checking `irq_create_mapping()` failure. Test signals include exhaustion of ten slots, concurrent get/release/poke, module unload with active clients, and sysfs writes for all event codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dummy/iio_dummy_evgen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dummy/iio_dummy_evgen.h -->
# sources/distributed-fs/ceph-client/drivers/iio/dummy/iio_dummy_evgen.h

Purpose: private header defining the fake register structure and exported event-generator API used by the IIO simple dummy event implementation.

Important APIs/types/functions: `struct iio_dummy_regs` holds `reg_id` and `reg_data`, the two fields the event handler reads to determine which fake event was triggered. The declarations are `iio_dummy_evgen_get_regs(int irq)`, `iio_dummy_evgen_get_irq(void)`, and `iio_dummy_evgen_release_irq(int irq)`.

Control flow: event-enabled dummy instances call `get_irq()`, call `get_regs()` for that IRQ, and later call `release_irq()` during teardown. The header intentionally exposes only slot allocation and register access, leaving sysfs poke implementation private to `iio_dummy_evgen.c`.

State/persistence: no direct state. The returned `struct iio_dummy_regs *` points into the singleton event generator state and is valid only while the IRQ mapping and module state remain alive.

Dependencies/integration: guarded by `_IIO_DUMMY_EVGEN_H_` and included by both producer and consumer C files. The companion C file exports these symbols with GPL visibility.

Risks: the API has no ownership type or lifetime annotation; callers must pair get/release correctly and not retain the register pointer after release. Test signals include compile coverage with `CONFIG_IIO_SIMPLE_DUMMY_EVENTS=y` and symbol availability when `IIO_DUMMY_EVGEN=m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dummy/iio_dummy_evgen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dummy/iio_simple_dummy.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dummy/iio_simple_dummy.c

Purpose: reference IIO software device showing direct-mode channels, sysfs attributes, optional events, and optional buffers without real hardware. It is both documentation and a userspace test target.

Important APIs/types/functions: `iio_dummy_channels[]` defines single-ended voltage, differential voltage, accel, timestamp, DAC output, steps, and activity channels. `struct iio_dummy_state` is declared in the header and initialized by `iio_dummy_init_device()`. `iio_dummy_read_raw()` and `iio_dummy_write_raw()` implement raw, processed, scale, offset, calibration, sampling-frequency, enable, and height attributes. `iio_dummy_probe()` and `iio_dummy_remove()` implement `iio_sw_device_ops`.

Control flow: software-device probe allocates `iio_sw_device` and `iio_dev`, initializes caches, duplicates the instance name, registers optional events and buffer support, then registers the IIO device. Direct raw/processed reads claim direct mode before reading cached state. Writes mutate cached state with mutex guards for most fields. Remove unregisters IIO, cleans buffer/events, frees name and device structures.

State/persistence: all sensor values are RAM caches with deterministic defaults: DAC 0, ADC 73/33/-34, accel 34, bias -7, default calibration scale, steps 47, running 98, walking 4. No hardware or persistent storage exists.

Dependencies/integration: integrates with `IIO_SW_DEVICE`, IIO core, sysfs, optional event callbacks, optional triggered buffers, and configfs-like software device group naming via `iio_swd_group_init_type_name()`.

Risks: the driver is intentionally permissive and illustrative, not strict hardware emulation. Some writes clamp activity to 0..100, but other fields accept arbitrary values. A few writes lack locking even though neighboring state uses locks. Test signals include software-device create/remove, all channel sysfs names, direct-mode busy behavior while buffers are active, optional event/buffer builds, and memory cleanup across probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dummy/iio_simple_dummy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dummy/iio_simple_dummy.h -->
# sources/distributed-fs/ceph-client/drivers/iio/dummy/iio_simple_dummy.h

Purpose: shared header that joins the simple dummy core, event support, and buffer support.

Important APIs/types/functions: `struct iio_dummy_state` is the central per-device state for cached DAC/ADC/accel/activity/steps values, mutex, fake registers, and optional event fields. Event declarations cover config/value read/write plus register/unregister hooks. Buffer declarations cover configure/unconfigure hooks. `enum iio_simple_dummy_scan_elements` gives stable scan indices for buffered data.

Control flow: compile-time `CONFIG_IIO_SIMPLE_DUMMY_EVENTS` and `CONFIG_IIO_SIMPLE_DUMMY_BUFFER` select real declarations or inline no-op stubs. This lets `iio_simple_dummy.c` call event and buffer hooks unconditionally while Kbuild controls linked objects.

State/persistence: the header describes state layout; actual initialization occurs in the C files. Optional event fields exist only in event-enabled builds, so structure size and available callbacks vary by configuration.

Dependencies/integration: includes kernel headers and forward-declares `struct iio_dev`, `struct iio_dummy_regs`, and calibration structs. It is the local contract between dummy core, event, and buffer modules.

Risks: because optional fields are compile-time gated, code touching event state must remain under the same config. Scan index changes must stay aligned with `iio_dummy_channels[]` and buffer `fakedata[]`. Test signals include builds with neither option, only events, only buffer, and both, plus buffer scan data matching the enum order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dummy/iio_simple_dummy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dummy/iio_simple_dummy_buffer.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dummy/iio_simple_dummy_buffer.c

Purpose: optional triggered-buffer implementation for the IIO simple dummy driver. It demonstrates how to push sampled data plus timestamps into an IIO buffer.

Important APIs/types/functions: `fakedata[]` maps `DUMMY_INDEX_*` scan indices to constant sample values. `struct dummy_scan` contains a fixed `s16` data array and aligned timestamp. `iio_simple_dummy_trigger_h()` is the threaded poll function handler. `iio_simple_dummy_configure_buffer()` wraps `iio_triggered_buffer_setup()`, and `iio_simple_dummy_unconfigure_buffer()` calls cleanup.

Control flow: when an IIO trigger fires, the handler allocates a DMA-safe scan object, copies values for active channels in scan order using `iio_for_each_active_channel()`, pushes the scan with `iio_push_to_buffers_with_ts()`, frees the allocation, and calls `iio_trigger_notify_done()`. Setup registers the handler without a top-half poll function.

State/persistence: no persistent device state is modified. Sample values are static constants, and each trigger allocates/free a temporary scan buffer.

Dependencies/integration: depends on IIO buffer, trigger consumer, and triggered buffer support. It relies on scan indices from `iio_simple_dummy.h` matching the channel definitions in `iio_simple_dummy.c`.

Risks: per-trigger allocation can fail; the handler silently skips pushing data but still notifies trigger completion. `sizeof(*scan)` is pushed even when fewer channels are active, so consumers rely on IIO scan mask interpretation. Test signals include active scan masks, timestamp alignment, memory allocation failure path, trigger completion, and direct-mode reads returning `-EBUSY` while buffered capture is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dummy/iio_simple_dummy_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dummy/iio_simple_dummy_events.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dummy/iio_simple_dummy_events.c

Purpose: optional event support for the IIO simple dummy driver. It demonstrates event configuration/value sysfs callbacks and IRQ-driven event delivery through the companion fake event generator.

Important APIs/types/functions: `iio_simple_dummy_read_event_config()`, `write_event_config()`, `read_event_value()`, and `write_event_value()` expose event enable and threshold state. `iio_simple_dummy_get_timestamp()` captures timestamp in the hard IRQ handler. `iio_simple_dummy_event_handler()` maps fake register data to IIO event codes. Register/unregister functions allocate the fake IRQ, obtain fake regs, request a threaded IRQ, and release resources.

Control flow: event config validates channel type, event type, and direction before toggling `st->event_en`. The threaded handler inspects `st->regs->reg_data`: 0 emits voltage rising threshold, 1 emits running threshold if cached running exceeds threshold, 2 emits walking falling threshold if cached walking is below threshold, and 3 emits steps change. Timestamp is captured before threaded handling.

State/persistence: `event_en`, `event_val`, `event_irq`, `event_timestamp`, and fake register pointer are per-device volatile state. The event generator holds the simulated IRQ backing store.

Dependencies/integration: depends on IIO events, IRQ APIs, and `iio_dummy_evgen` exported helpers. The channel event specs are declared in `iio_simple_dummy.c`.

Risks: `event_en` is a single boolean shared across all event-capable channels, so enabling one event effectively caches one global enable state. Event handler does not check `event_en` before pushing events. Threshold storage is also global, not per event. Test signals include sysfs enable/value round-trips, fake `poke_ev*` delivery, timestamp ordering, event code selection, and unregister cleanup after failed `request_threaded_irq()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dummy/iio_simple_dummy_events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/filter/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/filter/Kconfig

Purpose: Kconfig menu for IIO filter drivers, currently containing the Analog Devices ADMV8818 tunable high-pass/low-pass filter.

Important symbols: `ADMV8818` is a tristate user option depending on `SPI`, `COMMON_CLK`, and `64BIT`, and selecting `REGMAP_SPI`.

Control flow: enabling the option builds `admv8818.o` through the filter Makefile. The `COMMON_CLK` dependency matches the driver's optional `rf_in` clock and notifier integration; `64BIT` supports 64-bit frequency calculations exposed through IIO.

State/persistence: build-time only. Runtime state is in `admv8818.c`.

Dependencies/integration: integrates with SPI, regmap over SPI, common clock, and IIO. The help text identifies the device as a 2 GHz to 18 GHz digitally tunable high-pass/low-pass filter.

Risks: the help text contains a typo in "module"; not functional. If `COMMON_CLK` is unavailable, even manual non-clock filter mode cannot be built. Test signals include Kconfig dependency resolution and module build of `admv8818`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/filter/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/filter/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/filter/Makefile

Purpose: Kbuild glue for IIO filter drivers.

Important targets: `obj-$(CONFIG_ADMV8818) += admv8818.o` compiles the ADMV8818 driver when selected.

Control flow: one-to-one symbol-to-object mapping. Alphabetical ordering is documented for future additions.

State/persistence: no runtime behavior.

Dependencies/integration: consumes the `ADMV8818` Kconfig symbol and feeds the kernel build system. The object depends on regmap/SPI/common-clock configuration selected in Kconfig.

Risks: minimal. Additions should preserve ordering and ensure Kconfig selects any required bus helpers. Test signals are build coverage when `CONFIG_ADMV8818=m` and `=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/filter/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/filter/admv8818.c -->
# sources/distributed-fs/ceph-client/drivers/iio/filter/admv8818.c

Purpose: SPI/regmap IIO driver for ADMV8818 digitally tunable RF high-pass and low-pass filter. It exposes manual 3 dB cutoff controls and an automatic mode that tracks an input RF clock with configured margins.

Important APIs/types/functions: `struct admv8818_state` stores SPI/regmap, optional `rf_in` clock, clock notifier, mutex, filter mode, cached center frequency, and HPF/LPF margins. `__admv8818_hpf_select()` and `__admv8818_lpf_select()` choose band/state pairs from frequency tables and write WR0 switch/filter registers. `admv8818_rfin_band_select()` computes target HPF/LPF cutoffs around `clk_get_rate()`. IIO raw handlers expose low/high pass filter 3 dB frequency as `IIO_VAL_INT_64`; ext-info exposes `filter_mode`.

Control flow: probe initializes regmap, optional clock/notifier, property margins, performs soft reset and chip ID validation, enables single-instruction mode, and registers IIO. Manual writes directly program cutoff. Auto mode enables the clock and notifier; on `POST_RATE_CHANGE`, the notifier recalculates HPF/LPF. Bypass mode sets both bands/states to zero.

State/persistence: hardware register state is authoritative for readback; driver stores mode and margins in RAM. Auto mode caches center frequency only when recalculating. No nonvolatile programming occurs.

Dependencies/integration: uses SPI, regmap, common clock notifier, device properties `adi,lpf-margin-mhz` and `adi,hpf-margin-mhz`, IIO debugfs register access, and IIO enum ext-info.

Risks: mode cleanup actions check `filter_mode == 0`, relying on enum value for auto. Transition from auto to manual disables the clock before unregistering the notifier. Frequency approximation chooses nearest valid state with explicit handling for an HPF gap. Test signals include chip ID failure, manual cutoff round-trip, bypass, auto notifier recalculation, no-clock mode restrictions, margin underflow/overflow, and regmap error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/filter/admv8818.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/frequency/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/frequency/Kconfig

Purpose: Kconfig menu for IIO frequency devices including DDS/clock distribution and PLL/frequency synthesizer drivers.

Important symbols: `AD9523`, `ADF4350`, `ADF4371`, `ADF4377`, `ADMFM2000`, `ADMV1013`, `ADMV1014`, `ADMV4420`, and `ADRF6780`. Dependencies select SPI, GPIOLIB, COMMON_CLK, REGMAP_SPI, and 64BIT as needed by each implementation.

Control flow: choices are grouped under clock generator/distribution and PLL frequency synthesizers. Each symbol maps to a same-named object in the Makefile.

State/persistence: build-time only. Runtime configuration is through device tree/platform data and IIO sysfs/debugfs.

Dependencies/integration: captures bus and framework needs for the frequency directory. `ADF4377` and converter drivers depend on common clock where they consume or provide clocks; regmap-based SPI drivers select `REGMAP_SPI`.

Risks: dependency changes can break compile-time assumptions, particularly 64-bit arithmetic for ADMV1014 and SPI/regmap availability for ADF437x/ADMV4420. Test signals include allmodconfig-style builds and ensuring `select REGMAP_SPI` matches source use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/frequency/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/frequency/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/frequency/Makefile

Purpose: Kbuild object list for IIO frequency drivers.

Important targets: maps each Kconfig symbol to its object: `ad9523.o`, `adf4350.o`, `adf4371.o`, `adf4377.o`, `admfm2000.o`, `admv1013.o`, `admv1014.o`, `admv4420.o`, and `adrf6780.o`.

Control flow: Kbuild includes objects according to selected config symbols. The file is alphabetically ordered as requested by its comment.

State/persistence: no runtime state.

Dependencies/integration: consumes frequency Kconfig symbols and compiles the corresponding drivers into the kernel or modules.

Risks: missing object additions for new Kconfig entries would silently omit drivers. Test signals are module/built-in build coverage for each symbol and ordering checks during review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/frequency/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/frequency/ad9523.c -->
# sources/distributed-fs/ceph-client/drivers/iio/frequency/ad9523.c

Purpose: SPI IIO driver for the Analog Devices AD9523 low-jitter clock generator/distribution device. It configures PLL1, PLL2, VCO dividers, output channels, status sysfs, EEPROM storage, and divider synchronization from platform data.

Important APIs/types/functions: `struct ad9523_state` stores platform data, GPIOs, cached VCO/output frequencies, channel metadata, mutex, and SPI buffers. `ad9523_read()`/`ad9523_write()` implement variable-width register access by encoding transfer length into register constants. `ad9523_setup()` performs full device programming. `ad9523_read_raw()`/`write_raw()` expose output enable, frequency, and phase per configured channel. Sysfs attrs expose lock/reference status plus `sync_dividers` and `store_eeprom`.

Control flow: probe requires platform data, enables `vcc`, gets optional powerdown/reset/sync GPIOs, assigns channels from platform data, runs setup, and registers IIO. Setup resets serial config, programs PLL dividers/charge pumps/input receivers, calculates VCO outputs, writes per-channel distribution registers, powers down unused channels, sets status monitor, and issues IO update. Writes read-modify-write channel distribution registers and call IO update.

State/persistence: channel metadata and frequency maps are cached in RAM. EEPROM store is explicit and persistent on device when `store_eeprom` sysfs is written true. Register readback uses buffered register mode.

Dependencies/integration: depends on SPI, regulator, GPIO descriptors, platform data header `linux/iio/frequency/ad9523.h`, IIO sysfs/debugfs. It does not parse device tree for configuration.

Risks: no platform data means probe fails. Frequency selection chooses between clock providers using divisibility heuristics. EEPROM writes have polling and verification but a small fixed retry count. Test signals include full platform-data setup, inactive channel powerdown, output frequency/phase writes, sync pulse, EEPROM failure, status bits, and SPI register width encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/frequency/ad9523.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/frequency/adf4350.c -->
# sources/distributed-fs/ceph-client/drivers/iio/frequency/adf4350.c

Purpose: SPI IIO and optional common-clock driver for Analog Devices ADF4350/ADF4351 wideband PLL synthesizers. It programs six hardware registers to synthesize an RF output from a reference clock.

Important APIs/types/functions: `struct adf4350_state` holds SPI, optional lock-detect GPIO, platform/device-tree settings, input/output clocks, computed PLL fields, desired frequency, register cache, and mutex. `adf4350_set_freq()` calculates RF divider, prescaler, reference counter, modulus, integer/fraction, band select divider, and register values. `adf4350_sync_config()` writes changed registers in descending order with double-buffer handling. Ext-info sysfs exposes `frequency`, `frequency_resolution`, `refin_frequency`, and `powerdown`. Clock ops expose the synthesizer as a clock provider.

Control flow: probe parses device tree or platform data, gets input clock/regulator/GPIO, initializes caches, optionally tunes a power-up frequency, optionally registers a clock provider if `#clock-cells` exists, installs a devm powerdown action, and registers IIO only when no clock provider is exported. Writes under lock tune frequency, update reference clock, set channel spacing, or toggle powerdown.

State/persistence: `regs[]` is desired state and `regs_hw[]` is last written hardware state. PLL fields cache the current solution for readback. No nonvolatile writes occur.

Dependencies/integration: SPI, regulator, GPIO, common clock provider, device properties, optional platform data, and IIO debugfs. It consumes many ADI-specific properties for register policy.

Risks: `adf4350_clk_is_enabled()` returns the powerdown bit rather than its inverse, which may be semantically suspicious. Ext-info uses string sysfs because full frequency range exceeds 32-bit IIO frequency. Test signals include fractional/integer tuning, reference clock changes, lock-detect `-EBUSY`, clock-provider registration, powerdown devm cleanup, and register debugfs writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/frequency/adf4350.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/frequency/adf4371.c -->
# sources/distributed-fs/ceph-client/drivers/iio/frequency/adf4371.c

Purpose: SPI/regmap IIO driver for ADF4371/ADF4372 wideband synthesizers with RF8, auxiliary RF8, RF16, and RF32 output channels depending on variant.

Important APIs/types/functions: `struct adf4371_state` stores regmap, clock-derived reference/PFD values, fractional-N fields, divider state, reference mode, and scratch buffer. `adf4371_pll_fract_n_compute()` derives integer, FRAC1, FRAC2, and MOD2. `adf4371_set_freq()` validates channel range, maps requested output to VCO frequency/divider, bulk-writes PLL words, updates R counter, RF divider, charge pump bleed, integer/fractional mode, and INT LSB. Ext-info exposes per-channel `frequency`, `powerdown`, and `name`.

Control flow: probe initializes regmap, selects chip info from match data, gets `clkin` or differential `clkin-diff`, captures clock rate, runs setup, and registers IIO. Setup soft resets, writes default registers, optionally enables mute-till-lock, sets ascending address mode for bulk writes, validates reference input, optionally doubles low reference clocks, computes PFD/reference divider, computes timeouts, and bulk-writes timing registers.

State/persistence: frequency readback uses cached PLL fields plus a lock-status register check. Powerdown state is read from hardware. Driver state is volatile and hardware defaults are rewritten at probe.

Dependencies/integration: SPI, regmap, common clock consumer, IIO ext-info/debugfs, OF/SPI match data. It uses device property `adi,mute-till-lock-en`.

Risks: readback frequency reflects last successful driver computation, not a full hardware decode. Reference doubler TODO notes assumption around D/T terms. Powerdown write reads/modifies channel-specific registers. Test signals include variant channel count, range rejection per output, differential vs single-ended reference max frequency, lock register `-EBUSY`, bulk-write address ordering, and MOD2 reduction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/frequency/adf4371.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/frequency/adf4377.c -->
# sources/distributed-fs/ceph-client/drivers/iio/frequency/adf4377.c

Purpose: SPI/regmap IIO and optional common-clock driver for ADF4377/ADF4378 microwave wideband synthesizers. It supports frequency programming, optional GPIO output enables, reference clock notifier handling, and clock provider registration.

Important APIs/types/functions: `struct adf4377_state` stores chip info, regmap, reference clock, computed PFD/divider/timing values, muxout mode, GPIOs, optional clock provider, and mutex. `adf4377_init()` performs GPIO bring-up, soft reset, reserved-default writes, SDO setup, power-up, muxout setup, PFD calculation, and timing parameter derivation. `adf4377_set_freq()` programs calibration clocks, timeouts, ADC/VCO settings, output divider, R/N counters, waits for FSM idle, disables calibration clocks, and sets output amplitude. Ext-info exposes `frequency` when no clock provider is registered.

Control flow: probe creates regmap, parses `ref_in`, chip-enable/clk-enable GPIOs, and `adi,muxout-select`, registers a clock notifier, initializes hardware, optionally registers a clock provider, and otherwise exposes one IIO output channel. Clock ops route recalc/set/prepare/unprepare to the same register operations.

State/persistence: hardware registers are authoritative for `adf4377_get_freq()`, which reads R and N values and uses current `clk_get_rate()`. Derived setup state is volatile and recomputed on reference clock `POST_RATE_CHANGE`.

Dependencies/integration: SPI, regmap, common clock consumer/provider, GPIO descriptors, property parsing, IIO debugfs/ext-info, OF/SPI variant data.

Risks: `adf4377_freq_change()` locks `st->lock` and calls `adf4377_init()`, which can lead to reinitialization while consumers expect output continuity. `adf4377_set_freq()` computes `n_int = freq / f_pfd` while separately deriving `f_vco`, so output-divider behavior deserves hardware validation. Test signals include soft-reset polling, PFD range limits, reference-rate notifier, clock-provider mode vs IIO mode, GPIO optionality per variant, and FSM timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/frequency/adf4377.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/frequency/admfm2000.c -->
# sources/distributed-fs/ceph-client/drivers/iio/frequency/admfm2000.c

Purpose: platform IIO driver for Analog Devices ADMFM2000 dual microwave downconverter. It controls channel mode routing and digital step attenuator gain through GPIOs.

Important APIs/types/functions: `struct admfm2000_state` stores switch GPIO arrays for two channels, attenuation GPIO arrays for two DSAs, per-channel cached gain, and mutex. `admfm2000_mode()` sets switch GPIO polarity for mixer or direct IF mode. `admfm2000_attenuation()` writes five DSA bits for the selected channel. IIO raw handlers expose `IIO_CHAN_INFO_HARDWAREGAIN`.

Control flow: probe allocates a two-channel IIO direct-mode device, initializes default gain cache, initializes the mutex, and calls `admfm2000_channel_config()`. Channel config iterates firmware child nodes, reads `reg`, chooses mixer/direct mode from `adi,mixer-mode`, obtains switch and attenuation GPIOs by index, and applies mode. Hardware-gain writes convert dB values into a 5-bit inverted attenuation code and update GPIOs under lock.

State/persistence: gain cache is volatile and initialized to `ADMFM2000_DEFAULT_GAIN`; hardware GPIO levels persist only while powered/configured. Mode is applied at probe from firmware and not exposed as runtime IIO state.

Dependencies/integration: platform driver, OF compatible `adi,admfm2000`, firmware child nodes, GPIO descriptor API, and IIO direct mode.

Risks: `mode` is declared bool but assigned enum values; current values are 0/1 so it works. Gain conversion uses bitwise complement and signed arithmetic that deserves tests at boundaries. Channel config does not require both child nodes explicitly. Test signals include firmware children for both channels, missing GPIO errors, mixer/direct switch polarity, gain range -31 dB to 0 dB, and DSA bit ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/frequency/admfm2000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/frequency/admv1013.c -->
# sources/distributed-fs/ceph-client/drivers/iio/frequency/admv1013.c

Purpose: SPI IIO driver for ADMV1013 microwave upconverter. It configures LO quadrature filters, mixer gate bias, detector/input modes, and exposes I/Q calibration controls.

Important APIs/types/functions: `struct admv1013_state` stores SPI, LO input clock, mutex, notifier, selected input/quad modes, detector enable, and a three-byte SPI buffer. Custom SPI helpers read/write 16-bit register payloads in 24-bit frames. `admv1013_read_raw()`/`write_raw()` expose I/Q mixer offset calibration. Ext-info exposes `i_calibphase` and `q_calibphase`. `admv1013_update_quad_filters()` selects quad filter code from LO frequency; `admv1013_update_mixer_vgate()` derives mixer gate from VCM voltage.

Control flow: probe parses properties, enables ten VCC regulators, reads `vcm` voltage, enables `lo_in`, registers a clock notifier, initializes hardware, installs a powerdown action, and registers IIO. Init soft-resets, validates chip ID, writes default temperature compensation, programs quad SE mode, mixer Vgate, quad filters, detector, and input mode. LO clock changes trigger filter recalculation.

State/persistence: mode selections and detector enable are cached from firmware. Calibration reads/writes go to hardware registers. Powerdown action disables major blocks on device removal. No persistent storage.

Dependencies/integration: SPI, regulator bulk enable, common clock notifier, device properties `adi,detector-enable`, `adi,input-mode`, `adi,quad-se-mode`, IIO raw/ext-info/debugfs.

Risks: `admv1013_read_raw()` switches on `chan->channel` while write path switches on `chan->channel2`, making I/Q offset selection worth testing carefully. Quad filter ranges overlap in the first two branches; ordering means 5.4-7.0 GHz selects code 15. Test signals include VCM range rejection, chip ID validation, LO notifier, property defaults, calibration bitfields, and cleanup powerdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/frequency/admv1013.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/frequency/admv1014.c -->
# sources/distributed-fs/ceph-client/drivers/iio/frequency/admv1014.c

Purpose: SPI IIO driver for ADMV1014 microwave downconverter. It supports IQ or IF input modes, phase/offset/gain/detector controls, LO-dependent quad filtering, and regulator/clock managed power-up.

Important APIs/types/functions: `struct admv1014_state` stores SPI, LO clock, notifier, mutex, nine regulators, input/quad modes, P1dB compensation, detector enable, and SPI buffer. Custom SPI helpers mirror ADMV1013 framing. Raw handlers expose offset, phase, detector scale, and baseband gain controls. Ext-info exposes coarse/fine calibration scale for IF mode. `admv1014_read_avail()` returns detector scale values.

Control flow: probe parses properties and regulators, chooses IQ or IF channel arrays, sets SPI pointer, initializes mutex, and calls init. Init enables regulators and clock, registers cleanup actions and clock notifier, soft-resets, writes temperature compensation, validates chip ID, programs quad SE mode, updates quad filters and VCM settings, then configures P1dB/input/detector bits. LO clock changes recalculate quad filters.

State/persistence: firmware-derived mode flags are cached; register state is hardware-backed. Regulators and clock are devm-cleaned, and powerdown action disables core blocks. No nonvolatile state.

Dependencies/integration: SPI, regulator bulk API, common clock, notifier, IIO channels/ext-info/read_avail/debugfs, and properties `adi,detector-enable`, `adi,p1db-compensation-enable`, `adi,input-mode`, `adi,quad-se-mode`.

Risks: `admv1014_update_vcm_settings()` requires VCM to match exact 1050 mV + 56.25 mV steps, so board regulator tolerances can cause probe failure. IQ mode lacks IF calibration channels by design. Test signals include regulator enable/disable ordering, exact VCM table coverage, LO range branches, detector available list, IF/IQ channel layout, chip ID failure, and cleanup powerdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/frequency/admv1014.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/frequency/admv4420.c -->
# sources/distributed-fs/ceph-client/drivers/iio/frequency/admv4420.c

Purpose: SPI/regmap IIO driver for ADMV4420 K-band downconverter with integrated fractional-N PLL and VCO. It initializes the LO PLL to a configured or default LO frequency and exposes read-only LO frequency through IIO.

Important APIs/types/functions: `struct admv4420_state` stores SPI/regmap, VCO/LO frequencies, reference block settings, N counter values, mux selection, mutex, and transfer buffer. `admv4420_calc_parameters()` searches R divider and N counter values so PFD from reference equals PFD from VCO. `admv4420_set_n_counter()` writes fractional, modulus, and integer fields through bulk writes. `admv4420_setup()` performs reset, scratchpad communication tests, firmware parsing, parameter calculation, reference/N programming, mux selection, and enables PLL/LO/VCO/IF amp/mixer/LNA.

Control flow: probe initializes regmap, state, IIO metadata, runs setup, and registers the device. Setup defaults `lo_freq_hz` to 16.75 GHz, overrides with `adi,lo-freq-khz`, sets reference mode from `adi,ref-ext-single-ended-en`, searches PLL parameters, writes R divider/reference/N counter registers, sets lock-detect mux, and enables blocks.

State/persistence: LO/VCO and PLL parameter state is cached in RAM after setup; read_raw returns cached `lo_freq_hz` rather than decoding hardware. Hardware is initialized at probe and no runtime frequency write path exists.

Dependencies/integration: SPI, regmap, IIO debugfs, device properties, unaligned helpers, and OF compatible `adi,admv4420`.

Risks: PLL parameter search is potentially expensive because it nests R divider up to 1023 with N counter up to 655359. It assumes a fixed 50 MHz reference and does not expose runtime tuning. The mutex is declared but not initialized in probe, though current paths do not lock around public operations except debugfs direct reg access lacks locking. Test signals include scratchpad test failures, property frequency override, no-solution calculation, register endian/bulk writes, and readback units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/frequency/admv4420.c -->
