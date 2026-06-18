# subset-b-003879 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/vf610_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/vf610_adc.c

## Purpose
This file implements the Linux IIO platform driver for the Freescale/NXP Vybrid VF610 ADC family and the related i.MX6SX ADC variant. It exposes voltage channels, a temperature channel on VF610-class devices, direct sysfs reads, sampling-frequency control, a conversion-mode enum, debugfs register reads, suspend/resume handling, and triggered-buffer capture for one active scan channel.

## Important APIs, Types, And Functions
The central state is `struct vf610_adc`, which stores the MMIO base, enabled ADC clock, vref regulator, cached reference voltage, selected ADC feature configuration, completion object, lock, latest conversion value, available sample rates, and an aligned one-sample scan buffer. `struct vf610_adc_feature` records clock source, reference source, conversion mode, divider, resolution, hardware averaging index, long-sample-time index, default sample time, calibration state, and overwrite behavior. `struct vf610_chip_info` gates channel count for `fsl,vf610-adc` versus `fsl,imx6sx-adc`.

Key functions are `vf610_adc_calculate_rates()` for deriving clock divider, long sample timing, and `sample_freq_avail`; `vf610_adc_cfg_init()`, `vf610_adc_cfg_post_set()`, `vf610_adc_sample_set()`, `vf610_adc_cfg_set()`, and `vf610_adc_hw_init()` for programming hardware; `vf610_adc_calibration()` for one-time calibration; `vf610_read_sample()`, `vf610_read_raw()`, and `vf610_write_raw()` for IIO direct ABI callbacks; `vf610_adc_isr()` for completion and buffered push handling; and `vf610_adc_probe()` for resource acquisition and IIO registration.

## Control Flow
Probe allocates an IIO device, maps the ADC registers, picks chip data from firmware match data, requests the IRQ, enables the `adc` clock, enables the `vref` regulator with a devm cleanup action, reads optional `fsl,adck-max-frequency` and `min-sample-time` properties, initializes completions and IIO metadata, programs defaults, calibrates hardware, installs a one-hot triggered buffer, initializes the mutex, and registers the device. Direct raw reads claim direct mode, select the requested channel in `HC0` with interrupt enable, wait up to 100 ms for the ISR to complete, then return raw voltage or a processed temperature value. Buffered mode enables continuous conversion, selects the first active scan channel, and the ISR pushes the cached 16-bit sample with a timestamp before notifying the trigger.

## State And Persistence
The driver persists configuration only in memory and hardware registers: conversion mode, hardware averaging index, default sample-time-derived timing, cached vref voltage, and calibration-complete state. It does not persist across reboot. Runtime state is protected by `info->lock` for direct conversion paths and mode updates, while completions synchronize interrupt-driven conversion results. Suspend disables conversion, clock, and vref; resume re-enables them and reinitializes hardware.

## Dependencies And Integration Points
It depends on platform firmware matching, MMIO, IRQs, the common clock framework, regulators, IIO direct mode, IIO sysfs attributes, and IIO triggered buffers. Userspace integration is through IIO channel attributes for raw/processed readings, scale, sampling frequency, `sampling_frequency_available`, and `conversion_mode`. Device-tree integration includes `fsl,vf610-adc`, `fsl,imx6sx-adc`, `vref`, `adc` clock, `fsl,adck-max-frequency`, and `min-sample-time`.

## Risks And Test Signals
Important risks are timeout or failure during calibration and direct conversions, invalid clock-rate/divider assumptions, regulator voltage read failures affecting scale, and a narrow one-channel buffer model enforced by `iio_validate_scan_mask_onehot`. The temperature conversion uses fixed typical constants for the 3.3 V case, so board variance can affect accuracy. Useful tests are probe/remove with both compatibles, raw reads on every exposed channel, temperature read on VF610, sampling-frequency writes using only advertised values, conversion-mode sysfs changes during idle, buffered capture with a single selected channel, suspend/resume followed by reads, IRQ timeout injection, and debugfs register-read boundary checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/vf610_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/viperboard_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/viperboard_adc.c

## Purpose
This file implements the Nano River Technologies Viperboard ADC IIO child driver. It exposes four direct voltage input channels backed by USB control messages through the parent Viperboard MFD device.

## Important APIs, Types, And Functions
`struct vprbrd_adc_msg` is the packed three-byte protocol frame containing command, channel, and returned value. `struct vprbrd_adc` stores a pointer to the parent `struct vprbrd`, which supplies the USB device, shared transfer buffer, timeout, request IDs, and parent mutex. `vprbrd_iio_read_raw()` is the only IIO data path. `vprbrd_adc_probe()` allocates the IIO device and wires the four `IIO_VOLTAGE` raw-only channel specs.

## Control Flow
Probe retrieves the parent MFD state from `pdev->dev.parent`, allocates private IIO state, points it at the parent, sets `INDIO_DIRECT_MODE`, and registers the device. On `IIO_CHAN_INFO_RAW`, the read callback locks the parent Viperboard mutex, fills the shared buffer with `VPRBRD_ADC_CMD_GET` and the requested channel, sends it via a USB vendor control OUT request, receives the response via a control IN request, copies `admsg->val` to `*val`, unlocks, and returns `IIO_VAL_INT` if both transfers returned the exact expected frame size.

## State And Persistence
The ADC child has almost no private state beyond the parent pointer. It uses the parent's shared USB buffer and lock, so ADC transfers are serialized with other parent users. There is no persistent calibration, scale, or sample-rate state.

## Dependencies And Integration Points
The driver depends on the Viperboard MFD core, USB control-message helpers, platform-device child creation, and the IIO core. Its userspace ABI is four raw voltage channels. It registers as `platform:viperboard-adc` and depends on the parent exposing valid `VPRBRD_USB_REQUEST_ADC`, USB type constants, timeout, lock, and buffer.

## Risks And Test Signals
The result is only 8 bits (`u8 val`) and no scale is exposed, so consumers need board knowledge for engineering units. Both USB transfers must return exactly three bytes; short transfers map to `-EREMOTEIO`. The read callback assigns `*val` before checking the receive length, but still returns an error on failure. Tests should cover all four channels, parent lock contention, disconnect or stalled USB control transfers, short IN/OUT transfers, and repeated reads under concurrent MFD child activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/viperboard_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/xilinx-ams.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/xilinx-ams.c

## Purpose
This file implements the Xilinx ZynqMP AMS IIO driver. It monitors PS, PL, and controller voltage/temperature channels, provides labels, direct raw reads, scaling and temperature offsets, threshold-event configuration, IRQ-driven event delivery, and power-management clock control.

## Important APIs, Types, And Functions
`struct ams` stores the shared AMS register base, optional PS and PL SysMon bases, clock, locks, enabled alarm mask, currently masked level-triggered alarms, interrupt mask, and delayed unmask work. Channel construction uses `AMS_*_CHAN_*` macros and three static channel arrays: PS, PL, and controller channels. Firmware parsing uses `ams_parse_firmware()`, `ams_init_module()`, and `ams_get_ext_chan()` to compose the IIO channel list from the main device and child fwnodes.

Important runtime functions include `ams_init_device()` for reset, readiness polling, default sequencer mode, alarm disable, interrupt masking, and pending-interrupt clearing; `ams_enable_channel_sequence()` for programming PS/PL sequencer registers from the exposed channel set; `ams_read_raw()` for direct samples and scale/offset reporting; `ams_read_vcc_reg()` and `ams_enable_single_channel()` for controller VCC channels that require single-channel PS sequencing; `ams_write_event_config()` and `ams_update_alarm()` for alarm enable/disable; `ams_read_event_value()` and `ams_write_event_value()` for threshold registers; `ams_irq()` and `ams_unmask_worker()` for level-sensitive alarm delivery.

## Control Flow
Probe allocates an IIO device, initializes mutex/spinlock state, maps the top-level AMS MMIO region, enables the clock, registers delayed-work autocancel, parses firmware to map PS/PL/controller submodules and build channels, initializes hardware, programs continuous channel sequences, requests the IRQ, stores driver data, and registers the IIO device. Direct raw reads lock `ams->lock`; PS and PL sequence channels read directly from their MMIO bases, while controller channels temporarily switch PS SysMon into single-channel mode, wait for end-of-conversion, read the controller offset, then restore the full channel sequence.

Event enable updates both PS and PL hardware alarm-mask bits and the top-level interrupt mask. The IRQ handler reads `AMS_ISR_0`, filters disabled and temporarily masked alarm bits, clears the active bits, marks them as currently masked, pushes IIO threshold events, schedules delayed unmask work, and returns handled. The delayed work polls active status and only unmasks alarms whose level condition has disappeared.

## State And Persistence
The driver persists configuration in runtime hardware registers and in-memory masks. It initializes thresholds for each alarm-capable parsed channel to min/max defaults during firmware parsing. Alarm state is split across `alarm_mask`, `intr_mask`, and `current_masked_alarm`, with spinlock protection for interrupt state and mutex protection for user configuration and raw reads. Suspend and resume only gate the clock; full hardware register persistence is expected from the platform or remains in hardware.

## Dependencies And Integration Points
It depends on platform firmware with `xlnx,zynqmp-ams` and optional PS/PL child nodes, fwnode MMIO mapping, clocks, IRQs, delayed work, IIO events, and IIO direct mode. Userspace sees labeled channels (`read_label` returns `datasheet_name`), raw values, scale/offset for voltage/temp, and threshold event attributes for alarm-capable channels. It integrates with `readl_poll_timeout()` for PS readiness and conversion completion.

## Risks And Test Signals
Risks include firmware channel parsing exposing no channels or malformed external PL channel `reg` values, missing PS or PL bases for channels that later assume them, interrupt storm hazards from level-sensitive alarms, and no range validation on threshold writes beyond raw register width. `ams_event_to_channel()` assumes a matching channel exists for each delivered alarm; malformed channel lists can make that fragile. Tests should cover PS-only, PL-only, controller-only, and combined nodes; raw reads of controller VCC channels; label output; rising/falling/either threshold attributes; alarm enable/disable and delayed unmask behavior under persistent threshold levels; suspend/resume; and probe failures for missing clock, bad child MMIO, or IRQ request failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/xilinx-ams.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/xilinx-xadc-core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/xilinx-xadc-core.c

## Purpose
This file is the core Xilinx XADC/System Monitor IIO driver. It supports Zynq hard XADC and AXI XADC/System Management Wizard variants, exposing internal temperature, supply voltages, VP/VN, VREF, VAUX channels, sampling-frequency control, threshold events, and buffered acquisition for AXI-backed variants.

## Important APIs, Types, And Functions
The implementation is structured around `struct xadc` from `xilinx-xadc.h` and variant-specific `struct xadc_ops`. `xadc_zynq_ops` communicates through the Zynq command/data FIFOs and level-sensitive interrupt masking. `xadc_7s_axi_ops` and `xadc_us_axi_ops` use direct AXI register windows, optional IRQs, and buffered acquisition. Channel templates are `xadc_7s_channels` and `xadc_us_channels`; firmware parsing duplicates and prunes them based on `xlnx,channels`, `xlnx,external-mux`, optional bipolar flags, and IRQ availability.

Key functions include Zynq FIFO register accessors (`xadc_zynq_read_adc_reg()`, `xadc_zynq_write_adc_reg()`), AXI accessors, interrupt handlers, alarm update functions, `xadc_read_raw()` and `xadc_write_raw()` for IIO data paths, `xadc_read_samplerate()` and `xadc_write_samplerate()` for `CONF2` divisor handling, `xadc_preenable()` and `xadc_postdisable()` for sequencer setup around buffers, `xadc_trigger_handler()` for buffered sample reads, and `xadc_parse_dt()`/`xadc_probe()` for integration.

## Control Flow
Probe selects ops from compatible data, obtains an optional IRQ subject to variant flags, allocates state, initializes locks/completion/delayed work, maps MMIO, parses firmware channels and external mux config, optionally sets up triggered buffers and AXI triggers, enables the clock, clamps buffered sample rate to 150 kSPS, requests the IRQ, runs variant setup, snapshots all threshold registers, writes `CONF0`, programs input bipolar masks, switches to non-buffered continuous sequencer mode with `xadc_postdisable()`, and registers IIO.

Direct reads fail with `-EBUSY` when a buffer is active, read the channel address through the ops layer, shift/sign-extend according to the channel scan type, and return scale/offset/sample-rate metadata. Buffer enable programs scan masks into sequencer registers, chooses continuous versus simultaneous/independent mode based on selected VAUX channels and external mux mode, powers ADC-B as needed, and enables sequencer mode. The trigger handler reads each active channel register and pushes the packed buffer.

## State And Persistence
Runtime state includes threshold cache, temperature hysteresis, enabled alarm mask, buffer data allocation, active trigger pointers, external mux mode, Zynq masked-alarm/intmask fields, completion state, mutex, and spinlock. Register state is restored by setup and postdisable, but not persisted outside runtime. Zynq register access serializes command FIFO operations with spinlocks and completions; generic ADC register access is protected by the XADC mutex.

## Dependencies And Integration Points
The driver depends on platform firmware compatibles `xlnx,zynq-xadc-1.00.a`, `xlnx,axi-xadc-1.00.a`, and `xlnx,system-management-wiz-1.3`, MMIO, clocks, optional IRQs, IIO events, IIO triggered buffers, and `xilinx-xadc-events.c` for event ABI helpers. It integrates with external mux firmware properties and child channel definitions. Userspace sees raw, scale, offset, sampling frequency, threshold event configuration, and optional buffer triggers named for `convst` and `samplerate`.

## Risks And Test Signals
The major operational risk is interrupt load: the driver clamps sampling to 150 kSPS because the hardware lacks a FIFO. Zynq threshold IRQs are level-sensitive and require delayed unmask logic; broken masking can produce interrupt storms. `xadc_parse_dt()` tolerates invalid child channel `reg` by skipping them, so firmware mistakes can silently reduce channel coverage. Tests should cover all three compatibles, with and without IRQ, external mux modes, bipolar child channels, sample-rate clamp and divisor rounding, direct reads blocked by active buffers, buffer scan modes across lower/upper VAUX groups, threshold and hysteresis writes, Zynq FIFO timeout paths, AXI EOS trigger polling, delayed alarm unmask, and UltraScale temperature scale/offset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/xilinx-xadc-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/xilinx-xadc-events.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/xilinx-xadc-events.c

## Purpose
This companion file implements the XADC IIO event ABI used by `xilinx-xadc-core.c`. It maps hardware alarm bits to IIO channels, pushes threshold events, and reads/writes threshold and hysteresis values while keeping `struct xadc` alarm state synchronized with hardware configuration.

## Important APIs, Types, And Functions
The exported callbacks are `xadc_handle_events()`, `xadc_read_event_config()`, `xadc_write_event_config()`, `xadc_read_event_value()`, and `xadc_write_event_value()`. Internal helpers `xadc_event_to_channel()`, `xadc_get_threshold_offset()`, and `xadc_get_alarm_mask()` translate between XADC threshold numbers, alarm mask bits, channel addresses, and IIO event directions.

## Control Flow
Interrupt handlers in the core pass a normalized event bitmask to `xadc_handle_events()`, which iterates the low eight bits and calls `xadc_handle_event()`. Temperature events are pushed as rising threshold events; voltage events are pushed as either-direction threshold events because the hardware status does not identify upper versus lower threshold cause. Event configuration updates `xadc->alarm_mask`, calls the variant `ops->update_alarm()`, then rewrites `XADC_REG_CONF1` alarm-disable bits while holding `xadc->mutex`.

Threshold reads use the cached `xadc->threshold[]` or `temp_hysteresis` value, right-shifted from the hardware's MSB-aligned representation to the channel realbits. Threshold writes left-shift userspace values back into MSB alignment, validate the 16-bit range, update the cache, and write the corresponding `XADC_REG_THRESHOLD()` register. For temperature hysteresis, the driver stores hysteresis as a relative userspace value but programs the hardware lower threshold as an absolute value derived from the cached upper threshold.

## State And Persistence
This file mutates shared `struct xadc` state: `alarm_mask`, `threshold[16]`, and `temp_hysteresis`. The threshold cache is initialized by the core at probe from hardware registers. All hardware register writes are protected by the XADC mutex and use the lock-asserting `_xadc_*` accessors.

## Dependencies And Integration Points
It depends on the channel order and register definitions in `xilinx-xadc.h`, the `xadc_ops->update_alarm()` implementation selected by the core, and IIO event helper macros. It is not a standalone module; it supplies callbacks referenced from `xadc_info` in the core.

## Risks And Test Signals
A notable risk is channel mapping drift: event-to-channel translation assumes the core channel arrays keep internal supplies in the expected order. The first temperature threshold event is ignored because only over-temperature is handled. Voltage event direction is ambiguous by design. Tests should exercise enable/disable of every alarm-capable channel, rising/falling threshold writes, temperature hysteresis recalculation including hysteresis greater than threshold, event delivery mapping for Zynq and AXI normalized masks, and invalid event info handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/xilinx-xadc-events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/xilinx-xadc.h -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/xilinx-xadc.h

## Purpose
This header is the shared internal contract for the Xilinx XADC driver. It declares the event helper APIs, defines `struct xadc` and `struct xadc_ops`, provides mutex-aware register access wrappers, and centralizes hardmacro register, configuration, alarm, and threshold constants.

## Important APIs, Types, And Functions
`struct xadc` is the driver-private state shared across the core and event files. It contains MMIO base, clock, selected ops, threshold cache, temperature hysteresis, alarm mask, buffer data pointer, trigger pointers, external mux mode, Zynq-specific interrupt masking state, delayed work, mutex, spinlock, and completion. `enum xadc_external_mux_mode` represents no/single/dual mux configuration. `enum xadc_type` distinguishes Series 7 and UltraScale scaling/channel behavior. `struct xadc_ops` abstracts register read/write, setup, alarm update, dclk-rate query, interrupt handler, feature flags, type, and temperature conversion constants.

Inline helpers `_xadc_read_adc_reg()` and `_xadc_write_adc_reg()` assert the mutex is held and call the selected ops. Public `xadc_read_adc_reg()` and `xadc_write_adc_reg()` acquire and release the mutex. The macro block defines ADC result registers, max/min history registers, sequencer/input-mode/threshold registers, `CONF0/CONF1/CONF2` bitfields, power-down bits, alarm masks, and threshold indexes.

## Control Flow
The header itself has no runtime control flow, but it shapes the core: all variant register access is routed through `xadc_ops`, and event code uses the threshold/alarm constants to translate userspace ABI operations into hardware registers. The lock-asserting helper split is important because some operations update multiple registers under one mutex and need to avoid nested locking.

## State And Persistence
No state is allocated here, but the state layout controls persistence and synchronization semantics. Threshold and alarm state are runtime memory mirrors of hardware registers. `mutex` protects ADC register transactions and event configuration; `spinlock_t lock` protects IRQ-level register masking paths; `completion` synchronizes Zynq FIFO responses.

## Dependencies And Integration Points
The header depends on Linux interrupt, mutex, and spinlock declarations plus forward declarations for IIO, clock, and platform-device types. It is included by `xilinx-xadc-core.c` and `xilinx-xadc-events.c` and must remain aligned with Xilinx hardmacro documentation and the channel maps in the core.

## Risks And Test Signals
The main risk is that constant or bitfield changes affect both direct reads and event handling. `XADC_CONF1_ALARM_MASK` and threshold offsets must match hardware layout and event code assumptions. Tests are indirect: build coverage for both source files, lockdep coverage for `_xadc_*` helpers, event ABI tests for every alarm mask, and buffered/direct register-access tests across Series 7 and UltraScale variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/xilinx-xadc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/addac/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/addac/Kconfig

## Purpose
This Kconfig file defines the Industrial I/O ADDAC submenu and the build-time options for three mixed analog input/output drivers: AD74115, AD74413R, and STX104.

## Important APIs, Types, And Functions
There are no C APIs, but the configuration symbols are important integration contracts. `CONFIG_AD74115` enables the Analog Devices AD74115H single-channel configurable input/output driver and selects CRC8, IIO buffers, triggered buffers, and REGMAP over SPI. `CONFIG_AD74413R` enables AD74412R/AD74413R quad-channel configurable I/O support, depending on GPIOLIB and SPI, selecting REGMAP_SPI, CRC8, and IIO buffered infrastructure. `CONFIG_STX104` enables the Apex Embedded Systems PC/104 card driver, depending on PC104 and X86, selecting ISA bus API, REGMAP_MMIO, GPIOLIB, GPIO_REGMAP, and I8254.

## Control Flow
Kconfig evaluation gates whether the corresponding objects can be built, either built-in or as modules. The submenu is ordered alphabetically and each entry documents the module name expected by userspace/package maintainers.

## State And Persistence
The file persists only build configuration. It indirectly controls which runtime drivers and module aliases are available in the kernel image or module tree.

## Dependencies And Integration Points
It integrates with the kernel configuration system, the ADDAC Makefile, SPI/regmap/IIO/GPIO/I8254 subsystems, and architecture/platform availability for STX104. The selected symbols ensure dependencies needed by the C files are present without requiring users to select all helpers manually.

## Risks And Test Signals
Risks include missing selects when C files gain new mandatory subsystems, dependency expressions that allow invalid builds, and symbol ordering drift. Test signals are `allyesconfig`/`allmodconfig` build coverage, individual module builds for each symbol, dependency checks on non-X86 builds for STX104, and verification that module names in help text match Makefile outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/addac/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/addac/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/addac/Makefile

## Purpose
This Makefile maps ADDAC Kconfig symbols to object files for the Linux IIO build.

## Important APIs, Types, And Functions
It defines `obj-$(CONFIG_AD74115) += ad74115.o`, `obj-$(CONFIG_AD74413R) += ad74413r.o`, and `obj-$(CONFIG_STX104) += stx104.o`. These lines are the build-system contract connecting Kconfig choices to compilation units.

## Control Flow
During kbuild evaluation, each `obj-$()` entry expands to `obj-y`, `obj-m`, or empty depending on the selected configuration. Built-in selections link into the kernel; module selections produce separate `.ko` modules.

## State And Persistence
The file has no runtime state. Its persistent effect is the kernel/module build graph.

## Dependencies And Integration Points
It integrates directly with `drivers/iio/addac/Kconfig` and kbuild. The entries are kept alphabetical, matching the local convention and making future additions easier to review.

## Risks And Test Signals
Risks are stale entries after renames, missing entries for new Kconfig symbols, or ordering churn. Test signals are successful `M=drivers/iio/addac` builds for each config, module artifact names matching Kconfig help, and no orphaned Kconfig symbols without corresponding objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/addac/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/addac/ad74115.c -->
# sources/distributed-fs/ceph-client/drivers/iio/addac/ad74115.c

## Purpose
This file implements the Analog Devices AD74115H single-channel software-configurable ADDAC IIO driver. Depending on firmware properties, the device can expose voltage/current input, voltage/current output, resistance input, digital input comparator threshold output, GPIOs, buffered ADC sampling, and direct register debug access.

## Important APIs, Types, And Functions
`struct ad74115_state` is the central runtime state: SPI/regmap handles, optional trigger and IRQ, mutex, GPIO chips, AVDD voltage, valid GPIO mask, channel-function flags, completions, prebuilt SPI messages for buffered ADC reads, and DMA-aligned register/sample buffers. `enum ad74115_ch_func`, `enum ad74115_adc_range`, conversion sequence enums, slew enums, GPIO mode enums, and channel maps define the firmware-to-IIO ABI. `struct ad74115_fw_prop` and `ad74115_apply_fw_prop()` provide a table-driven firmware-property-to-register mechanism.

Important paths include CRC-framed SPI regmap access (`ad74115_reg_read()`, `ad74115_reg_write()`), GPIO callbacks, comparator GPIO callbacks, `ad74115_update_scan_mode()` for constructing pipelined read-select SPI transfers, `ad74115_get_adc_code()` for one-shot conversions with IRQ or polling fallback, DAC/ADC scale and offset helpers, `ad74115_read_raw()`/`ad74115_write_raw()`, `ad74115_setup()` for firmware application, `ad74115_setup_trigger()`, and `ad74115_probe()`.

## Control Flow
Probe allocates the IIO device, enables AVDD and other regulators, initializes custom regmap over SPI, resets the chip using GPIO or command-key sequence, applies firmware properties, configures channel function and ADC range, registers GPIO chips where requested, sets up optional ADC-ready IRQ/trigger, installs a triggered buffer, and registers IIO. Direct ADC reads claim direct mode, lock the device, enable the requested ADC channel, start single conversion, wait for IRQ completion or poll `LIVE_STATUS`, read the selected data register, return standby, disable the channel, and release direct mode.

Buffered mode uses `update_scan_mode()` to enable selected channels and build a message that writes `READ_SELECT` for the next channel while receiving the previous channel's result. Buffer postenable switches conversion to continuous mode; predisable returns to standby and disables all ADC channels. Firmware setup applies many Analog Devices properties for channel function, DAC slew/HART behavior, digital input range/sink/debounce/comparator settings, RTD mode/excitation, burnout currents, charge pump, and GPIO modes.

## State And Persistence
All state is runtime only and mirrored into device registers. `lock` serializes one-shot conversion and scan-message updates. `adc_data_completion` synchronizes ADC-ready IRQs. GPIO validity and IIO channel layout are computed once at probe from firmware properties. The driver caches AVDD in millivolts for threshold scale calculation and stores flags for bipolar DAC, HART slew, RTD wiring, and threshold mode.

## Dependencies And Integration Points
The driver depends on SPI, CRC8, custom regmap callbacks, regulators (`avdd`, `avcc`, `dvcc`, `dovdd`, `refin`), optional reset GPIO, optional named `adc_rdy` IRQ, IIO buffers/triggers, GPIO subsystem, firmware properties, and `adi,ad74115h` matching. Userspace sees dynamically selected IIO channel sets with raw, processed, scale, offset, and sampling-frequency attributes plus optional GPIO lines and comparator GPIO.

## Risks And Test Signals
Risks include complex firmware-property validation, possible channel ABI changes from firmware, CRC framing failures, conversion timeout at low sample rates, and careful direct/buffer mutual exclusion requirements. The debounce setter computes an index but writes the requested value into the field, which is worth regression coverage against expected hardware encoding. Tests should cover every `adi,ch-func` mode, invalid property values, AVDD-required threshold mode, IRQ and polling ADC completion, raw/processed resistance paths, DAC bipolar offset/scale, DAC slew sample-frequency availability, buffered two-channel reads with CRC-valid frames, GPIO valid-mask behavior, comparator GPIO debounce, reset GPIO and software reset paths, and register debug access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/addac/ad74115.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/addac/ad74413r.c -->
# sources/distributed-fs/ceph-client/drivers/iio/addac/ad74413r.c

## Purpose
This file implements the Analog Devices AD74412R/AD74413R quad-channel software-configurable I/O driver. It supports per-channel voltage/current input and output modes, resistance and digital input modes, optional HART-specific ADC rejection rates on AD74413R, buffered ADC sampling, GPIO output lines, comparator GPIO inputs, and CRC-protected SPI/regmap access.

## Important APIs, Types, And Functions
`struct ad74413r_state` tracks per-channel configs, GPIO offset maps, GPIO chip objects, ADC-ready completion, sense resistor and reference voltage, mutex, chip info, SPI/regmap handles, IIO trigger, active channel count, prebuilt buffered SPI message, and DMA-aligned buffers. `struct ad74413r_channel_config` stores firmware-chosen channel function, drive strength, comparator GPO flag, and initialization state. `struct ad74413r_chip_info` distinguishes AD74412R from AD74413R HART support.

Key functions include CRC/regmap helpers, GPIO and comparator GPIO callbacks, reset and channel function programming, ADC conversion sequencing, range/rejection/rate/scale/offset helpers, `ad74413r_get_single_adc_result()`, `ad74413r_update_scan_mode()`, buffer enable/disable callbacks, IIO read/write/read-avail callbacks, firmware channel parsing, channel spec setup, GPIO setup, and `ad74413r_probe()`.

## Control Flow
Probe initializes state, regmap, reference voltage, sense resistor, IIO trigger, resets the chip, parses child nodes with `reg` and `adi,ch-func`, rejects duplicate/out-of-range channels and HART modes on AD74412R, builds IIO channels for all four physical channels, programs each channel through high-impedance and zero-DAC transition delays into its requested function, configures GPIO/comparator modes, registers GPIO chips, turns ADC conversion off, requests the SPI IRQ for ADC-ready handling, installs the triggered buffer, and registers IIO.

Direct ADC reads claim direct mode, lock the device with a scoped guard, enable one channel, start a single conversion, wait up to one second for ADC-ready completion, read that channel result, turn conversion off, disable the channel, and return. Buffered scanning disables inactive channels, enables active ones, builds a pipelined `READ_SELECT` SPI message, starts continuous conversion on buffer enable, and uses the IRQ-triggered handler to run the message, CRC-check each returned frame, and push samples with timestamp.

## State And Persistence
State is runtime-only and hardware-register-backed. Per-channel function choices are parsed once at probe; GPIO offset maps compress physical channels into exported logical lines. `lock` serializes one-shot conversion and buffered message reconfiguration. `adc_data_completion` synchronizes direct conversion when buffers are inactive. DAC codes and channel functions live in device registers until reset.

## Dependencies And Integration Points
The driver depends on SPI, CRC8, regmap custom callbacks, regulators for `refin`, optional reset GPIO, SPI IRQ, firmware child nodes, `dt-bindings/iio/addac/adi,ad74413r.h` channel-function constants, GPIO subsystem, IIO triggered buffers, and IIO triggers. It matches `adi,ad74412r` and `adi,ad74413r`, with SPI IDs for both. Userspace sees mode-dependent IIO channels with raw/processed, scale, offset, and sample-frequency attributes plus optional GPIO chips.

## Risks And Test Signals
Risks include intricate SPI read pipelining, CRC validation failures, incorrect channel count if not all four child nodes are initialized, HART mode gating, conversion timeouts, and scale/offset math depending on range and sense resistor. `ad74413r_gpio_set_multiple()` tests `if (*bits & offset)` rather than `BIT(offset)`, which should be covered. Tests should exercise all channel functions, invalid duplicate/missing channel nodes, AD74412R HART rejection, GPO/comparator GPIO registration, debounce/drive-strength properties, direct read while buffered returns busy, buffer scan masks and frame CRC, DAC write range checks, sample-rate availability for HART and non-HART chips, reset GPIO versus software reset, and IRQ failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/addac/ad74413r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/addac/stx104.c -->
# sources/distributed-fs/ceph-client/drivers/iio/addac/stx104.c

## Purpose
This file implements the Apex Embedded Systems STX104 PC/104 IIO driver. It exposes analog inputs, analog outputs, digital I/O through gpio-regmap, and an i8254 timer for an ISA I/O-port board configured by module parameter base addresses.

## Important APIs, Types, And Functions
`struct stx104_iio` stores a mutex plus separate regmaps for analog control and analog data. Static regmap configurations describe 8-bit control, 16-bit data, DIO, and PIT register windows over I/O ports. Channel macros define two voltage output channels plus either 16 single-ended or 8 differential voltage input channels depending on hardware status. Main functions are `stx104_read_raw()`, `stx104_write_raw()`, `stx104_init_hw()`, `bank_select_i8254()`, `stx104_reg_mask_xlate()`, and `stx104_probe()`.

## Control Flow
The ISA driver uses `module_isa_driver()` and the `base[]` module parameter. Probe locks the requested I/O port region, maps it, creates regmaps for analog control/data, DIO, and i8254, reads ADC status to select single-ended or differential channel table, initializes IIO metadata, initializes hardware for software-trigger mode, gain x1, DAC outputs at 0, and i8254 bank selection, registers IIO, then registers a gpio-regmap instance and an i8254 regmap instance.

Raw input reads lock the device, select a single ADC channel, write the software strobe register, poll `STX104_ADC_STATUS` until conversion clears or the long hardware timeout expires, then read 16-bit ADC data. Raw output reads/writes access DAC registers. Hardware gain writes accept only x1/x2/x4/x8. Scale and offset derive from current bipolar/unipolar and gain bits.

## State And Persistence
Runtime state is minimal: mutex and regmap handles. Hardware state includes ADC trigger mode, gain, DAC output codes, bank selection, and any user-programmed gain/output values. No values are persisted across reboot or module unload.

## Dependencies And Integration Points
The driver depends on X86 PC/104 ISA support, I/O port resource reservation/mapping, regmap MMIO with `io_port = true`, IIO direct mode, GPIO_REGMAP, and I8254 namespace APIs. Userspace must provide base addresses via the `base` module parameter. It registers DIO names `DIN0`..`DOUT3` and imports the `I8254` namespace.

## Risks And Test Signals
Risks include wrong module base addresses causing probe failure or hardware conflicts, long conversion polling timeout, gain writes overwriting bipolar/range bits because they write the configuration register directly with gain, and ordering dependencies for i8254 bank selection. Tests should cover invalid/busy I/O regions, single-ended versus differential detection, raw reads for every channel, conversion timeout, DAC bounds, gain values and scale/offset changes, gpio-regmap input/output behavior, i8254 registration, and removal/reprobe with multiple base addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/addac/stx104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/afe/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/afe/Kconfig

## Purpose
This Kconfig file defines the IIO Analog Front Ends submenu and the `CONFIG_IIO_RESCALE` option for the rescale virtual front-end driver.

## Important APIs, Types, And Functions
The single symbol, `IIO_RESCALE`, is a tristate option named "IIO rescale". It enables support for IIO rescaling helpers that model voltage dividers, current sense shunts, current sense amplifiers, RTD temperature sensing, and temperature transducers. The help text documents that the module is named `iio-rescale`.

## Control Flow
Kconfig decides whether `iio-rescale.o` is omitted, built in, or built as a module. There are no explicit dependencies in this file, so the C file's included framework dependencies must be available through the IIO subsystem and selected kernel configuration.

## State And Persistence
The file persists build-time selection only. It has no runtime state.

## Dependencies And Integration Points
It integrates with `drivers/iio/afe/Makefile`, the IIO subsystem, and devicetree compatible strings handled by `iio-rescale.c`.

## Risks And Test Signals
Risks are missing dependency declarations if the implementation gains hard dependencies or help text drifting from module naming. Test signals are `CONFIG_IIO_RESCALE=y/m` builds, DT compatible probe tests for all variants, and module artifact checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/afe/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/afe/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/afe/Makefile

## Purpose
This Makefile maps the IIO AFE rescale Kconfig symbol to its object file.

## Important APIs, Types, And Functions
The only build rule is `obj-$(CONFIG_IIO_RESCALE) += iio-rescale.o`.

## Control Flow
Kbuild expands the rule to built-in, module, or empty based on the `IIO_RESCALE` tristate value.

## State And Persistence
There is no runtime state. The file contributes to the persistent build graph.

## Dependencies And Integration Points
It integrates with `drivers/iio/afe/Kconfig` and kbuild. The comment asks maintainers to keep entries alphabetical, which is trivial while only one object exists.

## Risks And Test Signals
Risks are stale object names after file renames or missing rules when new AFE drivers are added. Test signals are successful `M=drivers/iio/afe` builds with `CONFIG_IIO_RESCALE=m` and no orphaned Kconfig symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/afe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/afe/iio-rescale.c -->
# sources/distributed-fs/ceph-client/drivers/iio/afe/iio-rescale.c

## Purpose
This file implements a virtual IIO Analog Front End that wraps a source IIO channel and exposes a rescaled channel. It models common passive/active analog transformations such as current sense amplifiers, shunts, voltage dividers, RTDs, and temperature transducers.

## Important APIs, Types, And Functions
The driver uses `struct rescale` and `struct rescale_cfg` from `<linux/iio/afe/rescale.h>`. `rescale_process_scale()` and `rescale_process_offset()` are exported in the `IIO_RESCALE` namespace for reuse by other kernel users. Variant property parsers compute `numerator`, `denominator`, and optional `offset`: `rescale_current_sense_amplifier_props()`, `rescale_current_sense_shunt_props()`, `rescale_voltage_divider_props()`, `rescale_temp_sense_rtd_props()`, and `rescale_temp_transducer_props()`. `rescale_read_raw()`, `rescale_read_avail()`, ext-info proxy callbacks, `rescale_configure_channel()`, and `rescale_probe()` form the IIO device implementation.

## Control Flow
Probe obtains the unnamed source IIO channel, sizes private memory to include copied source ext-info callbacks, allocates an IIO device, selects variant config from firmware compatible data, computes scaling properties, validates nonzero numerator/denominator, sets a single channel with the target IIO type, proxies compatible ext-info entries, configures channel masks based on whether the source supports raw+scale/offset or processed data, and registers the device.

Raw reads either read raw source values or processed values if only processed data is available. Scale reads obtain source scale or use 1:1 for processed sources, then multiply by the rescaler ratio while preserving fractional representation where possible. Offset reads derive the equivalent userspace offset by combining source offset and rescaler offset divided by source scale. Available raw values are proxied only for raw sources.

## State And Persistence
Runtime state consists of the source channel pointer, computed ratio and offset, chosen variant config, copied channel spec, optional copied ext-info array, and a `chan_processed` flag. It does not maintain samples or persistent calibration. All behavior is recomputed from the source channel and static firmware properties at probe and read time.

## Dependencies And Integration Points
The driver depends on IIO consumer APIs, platform firmware matching, property APIs, gcd/overflow helpers, and the IIO core. It matches compatible strings `current-sense-amplifier`, `current-sense-shunt`, `voltage-divider`, `temperature-sense-rtd`, and `temperature-transducer`. It integrates with upstream producers by consuming their raw/processed/scale/offset/ext-info ABI and re-exposing a transformed channel.

## Risks And Test Signals
The most important risks are numeric overflow/rounding, sign handling for `IIO_VAL_INT_PLUS_MICRO/NANO`, invalid zero scaling factors, unsupported source channels, and misleading available values if source scale changes dynamically. Tests should cover all scale return types, negative numerator/denominator and source scales, offset composition with and without source offset, each compatible's property parsing and gcd reduction, processed-only sources, ext-info read/write proxying, raw available proxying, invalid missing properties, and exported helper use by another module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/afe/iio-rescale.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/amplifiers/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/amplifiers/Kconfig

## Purpose
This Kconfig file defines the IIO amplifier submenu and build symbols for SPI and GPIO-controlled amplifier/attenuator drivers.

## Important APIs, Types, And Functions
`CONFIG_AD8366` enables the AD8366-and-similar SPI gain amplifier/attenuator driver, depends on SPI and GPIOLIB, and selects BITREVERSE. `CONFIG_ADA4250` enables an Analog Devices SPI instrumentation amplifier and selects REGMAP_SPI. `CONFIG_ADL8113` enables a GPIO-controlled low-noise amplifier. `CONFIG_HMC425` enables GPIO-controlled gain amplifier/attenuator support. The AD8366 help text enumerates the supported devices and states module name `ad8366`.

## Control Flow
Kconfig gates which amplifier object rules in the Makefile become active. Dependency evaluation prevents selecting drivers without required buses or GPIO support.

## State And Persistence
The file controls only build-time configuration. Runtime state belongs to the selected C drivers.

## Dependencies And Integration Points
It integrates with kbuild, the amplifier Makefile, SPI, GPIOLIB, BITREVERSE, and REGMAP_SPI. Help text is part of the user-facing configuration documentation.

## Risks And Test Signals
Risks include missing dependency/select lines when drivers change, inaccurate supported-device lists, and symbol/object mismatches. Test signals are `allmodconfig` and per-symbol builds, especially `AD8366=m` with BITREVERSE availability, plus config visibility checks on kernels without SPI or GPIOLIB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/amplifiers/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/amplifiers/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/amplifiers/Makefile

## Purpose
This Makefile maps IIO amplifier Kconfig symbols to the corresponding object files.

## Important APIs, Types, And Functions
The object rules are `ad8366.o` for `CONFIG_AD8366`, `ada4250.o` for `CONFIG_ADA4250`, `adl8113.o` for `CONFIG_ADL8113`, and `hmc425a.o` for `CONFIG_HMC425`.

## Control Flow
Kbuild expands each `obj-$()` expression according to the selected tristate symbol and either links the object into the kernel, builds it as a module, or omits it.

## State And Persistence
The file has no runtime state; it persists the build graph for amplifier drivers.

## Dependencies And Integration Points
It integrates with `drivers/iio/amplifiers/Kconfig` and kbuild. The alphabetical-order comment provides a local maintenance convention.

## Risks And Test Signals
Risks are stale object names, missing objects for Kconfig symbols, or accidental ordering churn. Test signals are module builds for each symbol and checking that module names match help text and driver aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/amplifiers/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/amplifiers/ad8366.c -->
# sources/distributed-fs/ceph-client/drivers/iio/amplifiers/ad8366.c

## Purpose
This file implements an IIO SPI driver for AD8366 and a family of similar Analog Devices/Hittite digital gain amplifiers and attenuators. It exposes output voltage channels with writable/readable hardware gain in dB.

## Important APIs, Types, And Functions
`struct ad8366_info` is per-chip static metadata: name, min/max gain in milli-dB, gain step, number of channels, and optional code-packing callback. `struct ad8366_state` stores SPI device, mutex, current per-channel codes, chip info, and an aligned SPI transmit buffer. Packing functions handle chip-specific bit ordering and frame width: `ad8366_pack_code()`, `adrf5731_pack_code()`, and `hmc271_pack_code()`. `ad8366_write_code()` serializes the cached code array to SPI. IIO callbacks are `ad8366_read_raw()`, `ad8366_write_raw()`, and `ad8366_write_raw_get_fmt()`.

## Control Flow
Probe allocates an IIO device, initializes the mutex, enables the `vcc` regulator, gets chip match data, optionally asserts an enable GPIO high, obtains and deasserts an optional reset controller, configures IIO metadata and channel count, writes the initial zeroed gain code to hardware, and registers the IIO device. Writes convert userspace dB (`IIO_VAL_INT_PLUS_MICRO_DB`) to milli-dB, validate it against chip min/max, convert to a hardware code relative to min or max depending on gain-step sign, lock, cache the code, and write the packed SPI frame. Reads reverse the cached code into dB units.

## State And Persistence
The driver caches only the last written code per channel; it does not read back hardware. Initial probe writes zero codes. The mutex protects cached code and SPI writes. Gain settings are not persisted across reset or module reload except as hardware remains powered.

## Dependencies And Integration Points
The driver depends on SPI, IIO direct mode, regulators, optional enable GPIO, optional reset controller, bit reversal helpers, and firmware/SPI ID match tables for supported parts. Userspace sees one or two output voltage channels depending on chip metadata and the `hardwaregain` attribute with micro-dB format.

## Risks And Test Signals
Risks include devices with negative gain steps, chip-specific bit-order packing, lack of hardware readback, possible stale cached gain if SPI write fails after cache update, and validating only configured channel count while the static channel array has two entries. Tests should cover all match IDs, min/max/out-of-range writes, negative and positive dB formatting, read-after-write cache behavior, SPI frame bytes for each packer, regulator/enable/reset error paths, one-channel versus two-channel devices, and initial write failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/amplifiers/ad8366.c -->
