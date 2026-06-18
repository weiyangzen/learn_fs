# subset-b-003977 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ad7877.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/ad7877.c

Purpose: SPI driver for the Analog Devices AD7877 touchscreen controller, auxiliary ADC channels, DAC output, and two GPIO-style control bits. It reports a resistive single-touch input device and exposes board-level sensor/DAC/GPIO controls through device sysfs attributes.

Important APIs/types/functions: `struct ad7877` owns the SPI device, input device, default sequencer message, cached control words, timer, mutex, spinlock, and conversion buffer. SPI helpers `ad7877_read()`, `ad7877_write()`, and `ad7877_read_adc()` perform register and single-ended ADC transactions. Touch handling is centered on `ad7877_setup_ts_def_msg()`, `ad7877_irq()`, `ad7877_process_data()`, `ad7877_timer()`, `ad7877_disable()`, `ad7877_enable()`, `ad7877_suspend()`, and `ad7877_resume()`. Sysfs attributes expose `temp1`, `temp2`, `aux1`, `aux2`, `aux3`, `bat1`, `bat2`, `disable`, `dac`, `gpio3`, and `gpio4`; visibility of `aux3` versus `gpio3` depends on the module parameter `gpio3`.

Control flow: probe requires platform data, an IRQ, and a SPI clock at or below 20 MHz, switches the SPI word size to 16 bits, allocates device/input state, initializes timers and locks, copies platform timing/filter/pressure parameters, verifies the sequencer register by writing and reading `AD7877_MM_SEQUENCE`, optionally configures AUX3 as GPIO3, builds a reusable SPI message for sequence-mode sampling, requests a falling-edge threaded IRQ, and registers the input device. The IRQ synchronously executes the prebuilt message, processes X/Y/Z1/Z2 samples, reports `BTN_TOUCH`, `ABS_X`, `ABS_Y`, and `ABS_PRESSURE`, then arms a pen-up timer. The timer emits pressure zero and touch release if no further interrupt refreshes it.

State and persistence: all state is volatile per-device runtime state. `cmd_crtl1`, `cmd_crtl2`, and `cmd_dummy` back the persistent SPI transfer buffers used by the IRQ path, while `conversion_data[]` is DMA-safe sample storage. `disabled`, `gpio3`, `gpio4`, and `dac` are cached software views of sysfs-controlled chip state. Touch release is represented by timer state; if `timer_delete_sync()` returns true during disable, a release event is emitted. The hardware is left in low-power/default acquisition mode after each request.

Dependencies/integration: depends on SPI core, input core, Linux device attributes, `linux/spi/ad7877.h` platform data, IRQ threading, timers, and PM callbacks. It does not use device-tree property parsing directly; board files or equivalent platform data must supply axis ranges, pressure limits, plate resistance, and timing/filter parameters.

Risks and test signals: probe fails hard without platform data, so DT-only systems will not bind unless another layer supplies it. Sysfs `dac`, `gpio3`, and `gpio4` writes ignore `ad7877_write()` errors, making I/O failures hard to observe. Pressure math uses `(z2 - z1)` with unsigned arithmetic and depends on valid AD7877 sequencing; test noisy release, pressure threshold rejection, and `x == 0`/`z1 == 0` samples. IRQ, timer, and disable paths share touch state through a spinlock and mutex; test suspend/resume, sysfs disable while the IRQ thread is running, and removal with an active touch. Hardware test signals include successful SEQ1 readback, falling IRQ generation, correct pen-up timeout, sensor sysfs reads, and GPIO3 visibility toggling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ad7877.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ad7879-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/ad7879-i2c.c

Purpose: I2C bus glue for the shared AD7879/AD7889 touchscreen core. It creates an I2C regmap with 8-bit register addresses and 16-bit values, verifies adapter capability, and delegates all device behavior to `ad7879_probe()`.

Important APIs/types/functions: `ad7879_i2c_regmap_config` defines `.reg_bits = 8`, `.val_bits = 16`, and `.max_register = 15`. `ad7879_i2c_probe()` checks `I2C_FUNC_SMBUS_WORD_DATA`, initializes `devm_regmap_init_i2c()`, and calls `ad7879_probe(&client->dev, regmap, client->irq, BUS_I2C, AD7879_DEVID)`, where `AD7879_DEVID` is `0x79`. Match tables cover I2C IDs `ad7879` and `ad7889`, plus OF compatible `adi,ad7879-1`.

Control flow: after I2C core matching, probe rejects adapters that cannot perform SMBus word data transfers, creates the regmap, and enters the common core. PM callbacks and sysfs groups are not implemented here; they are imported from `ad7879.h` as `ad7879_pm_ops` and `ad7879_groups` and installed on the `i2c_driver`.

State and persistence: this file owns no runtime state beyond the devm-managed regmap. The common core stores per-device state with `dev_set_drvdata()` after successful registration.

Dependencies/integration: depends on I2C core, regmap-I2C, OF match support, input bus ID constants, and the shared AD7879 core/header. It is a thin transport module and must be built/loaded with `ad7879.c`.

Risks and test signals: functionality checking only covers SMBus word data, so unusual I2C controllers must provide that operation even if raw I2C would otherwise work. A wrong compatible or device ID can still reach the common probe but will fail revision/product comparison. Test by binding an AD7879-1/AD7889-1 device, confirming regmap reads of `REVID`, IRQ delivery into the core, sysfs `disable`, and suspend/resume through `ad7879_pm_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ad7879-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ad7879-spi.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/ad7879-spi.c

Purpose: SPI bus glue for the shared AD7879/AD7889 touchscreen core. It configures the AD7879 SPI command framing through regmap and delegates probe, input, GPIO, sysfs, and PM behavior to `ad7879.c`.

Important APIs/types/functions: `ad7879_spi_regmap_config` uses 16-bit register addresses and values, `.max_register = 15`, `.read_flag_mask = AD7879_CMD_MAGIC | AD7879_CMD_READ`, and `.write_flag_mask = AD7879_CMD_MAGIC`. `ad7879_spi_probe()` enforces `MAX_SPI_FREQ_HZ` of 5 MHz, creates `devm_regmap_init_spi()`, and calls `ad7879_probe(&spi->dev, regmap, spi->irq, BUS_SPI, AD7879_DEVID)`, where SPI `AD7879_DEVID` is `0x7A`. The driver exposes OF compatible `adi,ad7879` and alias `spi:ad7879`.

Control flow: SPI core match enters probe, the clock ceiling is validated, regmap is created with AD7879 command bits, and common probe performs reset, revision verification, IRQ request, input registration, and optional GPIO registration. Driver-level PM and sysfs groups are pointers exported by the common core.

State and persistence: the file has no independent per-device structure. The devm regmap is the only bus-layer object, and all persistent runtime state is managed in `struct ad7879` inside `ad7879.c`.

Dependencies/integration: depends on SPI core, regmap-SPI, OF, module SPI registration, and the common AD7879 core/header. It integrates the same logical device as the I2C wrapper but with different on-wire command encoding and expected revision ID.

Risks and test signals: incorrect SPI mode, word framing, or command masks will produce core probe failures when `REVID` is read. The wrapper does not call `spi_setup()` itself, relying on core/regmap behavior and controller defaults. Test with clocks above and below 5 MHz, valid `REVID` value `0x7A`, falling IRQs, common `disable` sysfs, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ad7879-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ad7879.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/ad7879.c

Purpose: shared core for AD7879/AD7889 touchscreen devices behind I2C or SPI. It implements register programming through regmap, resistive touch reporting, pen-up timing, device-tree property parsing, sysfs disable control, optional one-line GPIO controller support, and PM behavior.

Important APIs/types/functions: `struct ad7879` stores the regmap, device/input handles, IRQ, timer, optional `gpio_chip`, control register cache, touch sample cache, delayed-report coordinates, pressure resistance, and parsed properties. External APIs exported to bus wrappers are `ad7879_probe()`, `ad7879_pm_ops`, and `ad7879_groups`. Internal touch paths include `ad7879_read()`, `ad7879_write()`, `ad7879_report()`, `ad7879_irq()`, `__ad7879_enable()`, `__ad7879_disable()`, `ad7879_open()`, `ad7879_close()`, `ad7879_suspend()`, and `ad7879_resume()`. Optional GPIO support is implemented by `ad7879_gpio_direction_input()`, `ad7879_gpio_direction_output()`, `ad7879_gpio_get_value()`, `ad7879_gpio_set_value()`, and `ad7879_gpio_add()`.

Control flow: `ad7879_probe()` requires a positive IRQ and the mandatory `adi,resistance-plate-x` property, allocates input/device state, parses timing/filter and `touchscreen-swapped-x-y`, registers a timer, sets up input axes and pressure through common touchscreen properties, resets the chip, reads `REVID`, and rejects devices whose product byte differs from the bus wrapper's expected ID. It then prepares CTRL1/CTRL2/CTRL3 masks for interrupt-driven sequence sampling of X/Y/Z1/Z2, requests a falling threaded IRQ, disables the chip until userspace opens the input device, optionally registers a GPIO controller if `gpio-controller` is present, and registers the input device. The IRQ bulk-reads four sample registers, computes pressure, reports the previous valid sample only while the timer is already pending, updates cached current sample, and extends the 50 ms pen-up timer.

State and persistence: runtime state is fully volatile. `cmd_crtl1`, `cmd_crtl2`, and `cmd_crtl3` are the cached hardware operating mode and are rewritten on every enable; GPIO operations mutate `cmd_crtl2`. The delayed-report scheme stores `x`, `y`, and `Rt` so the final possibly incomplete sample in a touch sequence is not reported. `disabled` and `suspended` are protected by `input->mutex`; GPIO register access has a separate mutex under `CONFIG_GPIOLIB`.

Dependencies/integration: bus wrappers supply a regmap and expected device ID. The driver depends on input core, threaded IRQs, timers, firmware/device properties, common touchscreen property parsing, regmap, optional gpiolib, and exported attribute/PM hooks. Device-tree properties supply plate resistance, acquisition and filter timing, conversion interval, pressure range, coordinate transforms, and optional GPIO controller declaration.

Risks and test signals: `ad7879_toggle()` appears polarity-sensitive and should be tested carefully: writes to `disable` must actually disable when `1` and enable when `0`. Mandatory pressure max and X-plate properties can cause probe failure if bindings are incomplete. GPIO operations update CTRL2 while touch enable/disable also rewrites CTRL2, so test GPIO state across input close/open and suspend/resume. The delayed sample model intentionally suppresses the first sample; test tap latency, fast taps shorter than the timer cadence, pressure overflow rejection, swapped axes, REVID mismatch, and IRQ behavior after `__ad7879_disable()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ad7879.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ad7879.h -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/ad7879.h

Purpose: internal bus-interface header for the AD7879/AD7889 driver family. It declares the shared core's probe function, sysfs attribute group pointer, and PM operations for use by the I2C and SPI wrappers.

Important APIs/types/functions: forward declarations cover `struct attribute_group`, `struct device`, and `struct regmap`. `ad7879_groups[]` exposes the common `disable` sysfs group to bus drivers. `ad7879_pm_ops` provides suspend/resume callbacks. `ad7879_probe(struct device *dev, struct regmap *regmap, int irq, u16 bustype, u8 devid)` is the common entry point and takes bus-specific identity, IRQ, and regmap parameters.

Control flow: the header defines the contract where `ad7879-i2c.c` and `ad7879-spi.c` stop and `ad7879.c` begins. Bus probes create a regmap and call `ad7879_probe()`, then driver registration installs the exported groups and PM hooks.

State and persistence: no state is stored here. The declarations describe how the common core receives transport state and stores runtime data via device-managed allocations and `dev_set_drvdata()`.

Dependencies/integration: depends on PM and integer types plus regmap/device forward declarations. It intentionally avoids exposing `struct ad7879`, keeping bus wrappers transport-only.

Risks and test signals: this is a small but high-blast-radius internal ABI; any signature or exported symbol change must be compiled with both bus wrappers. Test modular builds with I2C-only, SPI-only, and both wrappers enabled, and ensure exported symbols resolve when wrappers are loadable modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ad7879.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ads7846.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/ads7846.c

Purpose: SPI resistive touchscreen and auxiliary sensor driver for ADS7846/TSC2046, ADS7843, ADS7845, and AD7873-compatible devices. It reports touch coordinates and pressure, manages pen-down polling from an IRQ thread, supports board/DT debounce and coordinate properties, optionally exposes temperature/voltage channels through hwmon, and controls a regulator supply.

Important APIs/types/functions: `struct ads7846` owns input, SPI, regulator, pendown/hsync GPIOs, filter callbacks, lock/stopped state, wait queue, and touch properties. `struct ads7846_packet` stores DMA-safe batched TX/RX buffers and per-command layout. Key functions include `ads7846_setup_pendown()`, `ads7846_setup_spi_msg()`, `ads7846_read_state()`, `ads7846_filter()`, `ads7846_report_state()`, `ads7846_hard_irq()`, `ads7846_irq()`, `ads7846_stop()`, `ads7846_restart()`, `ads7846_disable()`, `ads7846_enable()`, `ads7846_read12_ser()`, `ads7845_read12_ser()`, `ads784x_hwmon_register()`, `ads7846_get_props()`, `ads7846_probe()`, and `ads7846_remove()`. Sysfs device attributes expose `pen_down` and `disable`; hwmon attributes expose raw temperatures and scaled auxiliary/battery voltages when available.

Control flow: probe requires an IRQ, limits SPI sample rate, sets portable 8-bit SPI mode 0 transfers, allocates state and packet buffers, loads platform data or firmware properties, configures debounce filtering, obtains the pendown GPIO or callback, parses optional hsync and touchscreen properties, builds the input device, creates the packed SPI message for X/Y/Z1/Z2 or X/Y sampling plus powerdown, enables the regulator, requests a threaded IRQ with a hard handler that filters spurious pen-up interrupts, registers hwmon, takes an initial non-touch sample to leave the chip in low-power/penirq mode, registers input, and sets wakeup capability. The threaded IRQ sleeps briefly, loops while the pen line stays asserted, samples through SPI, filters repeated readings, reports coordinates and pressure, waits five milliseconds, and emits release once pendown deasserts.

State and persistence: runtime state includes `pendown`, `stopped`, `disabled`, and `suspended` under `lock`, plus debounce counters reused across samples. Packet TX/RX buffers are persistent devm allocations so DMA-capable SPI controllers have stable cacheline-separated storage. The regulator is enabled at probe and on resume/enable, and disabled through devm cleanup or explicit suspend/disable. The chip is intentionally left in low-power mode with PENIRQ enabled after each request.

Dependencies/integration: depends on SPI core, input and touchscreen helpers, GPIO descriptors, regulators, optional hwmon, DT/software-node properties, wait queues, threaded IRQs, and legacy `linux/spi/ads7846.h` platform data. It integrates with wakeup handling via `device_init_wakeup()` and `enable_irq_wake()`.

Risks and test signals: pendown state is mandatory unless a platform callback is supplied; missing GPIO properties will block probe. The IRQ thread relies on `stopped` with memory barriers and a wait queue; test disable/suspend/remove while the thread is polling. Busy-wait hsync support can spin until GPIO changes, so validate boards using `ti,hsync`. Pressure is inverted as `pressure_max - Rt`; test calibration, overflow rejection, and ADS7843/ADS7845 paths that do not provide full pressure data. `ads7846_setup_spi_msg()` return is not checked in probe, so allocation failure in setup should be audited. Test hwmon reads while touch polling is active, regulator failure paths, wakeup suspend, falling/rising IRQ workaround, debounce reject/retry behavior, and AD7873 model remapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ads7846.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/apple_z2.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/apple_z2.c

Purpose: SPI driver for Apple Z2 touch devices, notably Touch Bar controllers on Apple Silicon/Asahi-supported machines. It resets the controller, uploads volatile firmware and optional calibration data, reads interrupt packets, and reports high-slot-count multitouch events.

Important APIs/types/functions: `struct apple_z2` stores the SPI device, reset GPIO, input device, boot completion, boot state, interrupt counter parity, touchscreen properties, firmware name, and shared TX/RX buffers. Packet and firmware formats are represented by `struct apple_z2_finger`, `struct apple_z2_hbpp_blob_hdr`, `struct apple_z2_fw_hdr`, and `struct apple_z2_read_interrupt_cmd`. Main functions are `apple_z2_parse_touches()`, `apple_z2_read_packet()`, `apple_z2_irq()`, `apple_z2_build_cal_blob()`, `apple_z2_send_firmware_blob()`, `apple_z2_upload_firmware()`, `apple_z2_boot()`, `apple_z2_probe()`, `apple_z2_shutdown()`, `apple_z2_suspend()`, and `apple_z2_resume()`.

Control flow: probe allocates  command and receive buffers, obtains a reset GPIO asserted high, requests a no-auto-enable threaded IRQ, reads `firmware-name`, configures multitouch axes and 256 direct slots, registers input, waits for reset settling, then boots the controller. Boot enables IRQ, deasserts reset, waits for an initial IRQ completion, validates the firmware header magic/version, iterates firmware load commands, sends init/blob/calibration payloads with the required SPI word size, marks the device booted, and performs an initial packet read. Normal IRQs call `apple_z2_read_packet()`, which sends a read-interrupt command with alternating counter parity, reads the reported packet length, fetches the packet, and parses finger records from the payload.

State and persistence: firmware is requested from userspace storage but controller state is volatile; suspend/shutdown resets the device and resume reuploads firmware. Optional calibration is read from the `apple,z2-cal-blob` property and wrapped in a checksum-protected HBPP blob for upload. `booted` selects whether an interrupt completes boot progress or carries touch data. The receive buffer is fixed at 4000 bytes.

Dependencies/integration: depends on SPI core, firmware loader, GPIO descriptors, completions, input multitouch, touchscreen property parsing, OF compatible matching for `apple,j293-touchbar` and `apple,j493-touchbar`, and SPI IDs carrying user-visible input names. It declares firmware pattern `apple/dfrmtfw-*.bin`.

Risks and test signals: packet length from hardware is not bounded against the 4000-byte RX buffer before `spi_read()`, so malformed or unexpected firmware/controller responses could overflow assumptions. Firmware parsing relies on correctly aligned load commands and only validates local file bounds. IRQs are enabled during boot before `booted` flips; test race-free transition from boot completion to packet processing. Calibration blob length and checksum should be tested for absent, malformed, and odd-sized properties. Test suspend/resume reupload, reset GPIO polarity, invalid firmware header, malformed load command handling, multi-finger slot reuse, and input axis ranges from DT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/apple_z2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ar1021_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/ar1021_i2c.c

Purpose: minimal I2C input driver for Microchip AR1020/AR1021 resistive touchscreen controllers. It enables touch reporting on input open and reports single-touch X/Y plus `BTN_TOUCH` from fixed 5-byte packets.

Important APIs/types/functions: `struct ar1021_i2c` stores the I2C client, input device, and packet buffer. `ar1021_i2c_irq()` reads and decodes packets. `ar1021_i2c_open()` sends command `0x55 0x01 0x12` to enable touch reporting and enables the IRQ. `ar1021_i2c_close()` disables the IRQ. `ar1021_i2c_probe()` allocates/registers the input device and requests a no-auto-enable threaded IRQ. PM hooks simply disable/enable the IRQ.

Control flow: probe requires full I2C functionality, allocates state, configures a direct touchscreen input device with X/Y ranges 0..4095, requests a threaded IRQ with `IRQF_NO_AUTOEN`, and registers input. Userspace opening the input device sends the enable-touch command and enables interrupts. Each IRQ reads five bytes, rejects short reads and packets without the sync bit, extracts button state from byte 0 bit 0 and 12-bit X/Y values from 7-bit packed fields, reports events, and syncs.

State and persistence: no persistent hardware configuration is cached except the packet buffer. IRQ enabled state follows input open/close and PM callbacks. The controller is not explicitly powered down or reset by this driver.

Dependencies/integration: depends on I2C core, input core, IRQ threading, OF compatible `microchip,ar1021-i2c`, and I2C ID `ar1021`.

Risks and test signals: suspend/resume blindly disables/enables the IRQ without checking whether the input device is open, which can unbalance IRQ state if runtime PM occurs while closed. The open path treats any positive partial `i2c_master_send()` as success; short sends should be tested. No coordinate transform or touchscreen common property parsing is implemented. Test sync-bit rejection, packet decoding at 0 and 4095 boundaries, open/close IRQ balancing, suspend while closed/open, and I2C short read/write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ar1021_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/atmel_mxt_ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/atmel_mxt_ts.c

Purpose: full-featured I2C driver for Atmel/Microchip maXTouch Object Based Protocol controllers. It discovers the controller object table, processes T5/T44 message streams, reports T9/T100 multitouch and T15/T19/T97 key events, manages power and reset, applies configuration firmware, supports bootloader firmware flashing, exposes sysfs diagnostics, and optionally registers a V4L2 touch diagnostic capture device for T37 data.

Important APIs/types/functions: core state is `struct mxt_data`, which caches object table addresses/report IDs, input device, message buffer, firmware/config CRCs, completions, regulators, reset/wake GPIOs, keymaps, suspend mode, wakeup method, and touchscreen properties. Protocol descriptors include `struct mxt_info`, `struct mxt_object`, `struct t7_config`, `struct mxt_cfg`, and debug `struct mxt_dbg`. Main paths include raw I2C helpers `__mxt_read_reg()`/`__mxt_write_reg()`, bootloader helpers `mxt_probe_bootloader()`, `mxt_check_bootloader()`, `mxt_flash_fw()`, command helper `mxt_t6_command()`, object discovery `mxt_read_info_block()`/`mxt_parse_object_table()`, message handlers `mxt_proc_t6_messages()`, `mxt_proc_t9_message()`, `mxt_proc_t15_messages()`, `mxt_proc_t100_message()`, IRQ dispatch `mxt_interrupt()`, config update `mxt_update_cfg()`, input setup `mxt_initialize_input_device()`, and lifecycle `mxt_probe()`, `mxt_remove()`, `mxt_suspend()`, and `mxt_resume()`.

Control flow: probe filters devices lacking firmware properties and ignores ACPI bootloader-mode addresses below `0x40`, allocates state, initializes completions, chooses a DMI-specific suspend mode for some Chromebooks, parses keymap properties, enables `vdda` and `vdd`, handles reset/wake GPIOs, requests a no-auto-enable threaded IRQ, powers the chip, releases reset, reads wakeup method, and calls `mxt_initialize()`. Initialization reads and CRC-validates the info block and object table, recovers from bootloader mode if possible, checks the RETRIGEN workaround, enables IRQ, and asynchronously requests `maxtouch.cfg`; the config callback initializes T7 power, applies config if CRCs require it, registers the input device, and starts optional T37 debug. IRQs either complete bootloader transitions or read message counts from T44/T5, dispatch each report ID to the correct object handler, and sync input once per batch.

State and persistence: the object table, raw info block, message buffer, report-ID ranges, config CRC, T7 active/idle power config, keymaps, and input device persist for the client lifetime. Configuration files may be written into controller memory and backed up to nonvolatile storage via `MXT_COMMAND_BACKUPNV`. Firmware updates switch to bootloader mode, free the active input/object state, write firmware frames with CRC acknowledgement, and then reinitialize application mode. Suspend either disables T9 scanning or sets T7 deep sleep, depending on DMI-selected mode.

Dependencies/integration: depends on I2C, firmware loader, input MT, common touchscreen properties, regulators, GPIO descriptors, completions, IRQ type inspection, DMI/ACPI/OF matching, sysfs attributes, and optional V4L2/videobuf2 support under `CONFIG_TOUCHSCREEN_ATMEL_MXT_T37`. Device properties provide compatible identity, wakeup method, key/button maps, reset/wake GPIOs, supplies, and coordinate transforms.

Risks and test signals: asynchronous config loading means probe can return before input registration; removal racing a pending firmware callback should be tested. `mxt_prepare_cfg_mem()` has an off-by-one-looking check `if (i > mxt_obj_size(object))` that allows `i == size` semantics to be scrutinized when config object sizes differ. Firmware update interruption paths are explicitly TODO for `-ERESTARTSYS`. IRQ handling has two modes, with and without T44; test both, including CHG stuck-low and RETRIGEN workaround. Validate object table CRC mismatch, bootloader recovery, T6 reset/config CRC completions, T9 and T100 orientation/range parsing, keymap lengths, regulator/reset failure unwind, suspend/resume for open and closed inputs, sysfs `object` buffer growth, V4L2 diagnostic capture if enabled, and firmware/config files with mismatched family/variant/info CRC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/atmel_mxt_ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/auo-pixcir-ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/auo-pixcir-ts.c

Purpose: I2C driver for AUO/Pixcir in-cell touchscreens. It supports up to two contact reports, single-touch compatibility events, controller interrupt/power configuration, GPIO reset/interrupt lines, wakeup behavior, and deep-sleep/open-close power management.

Important APIs/types/functions: `struct auo_pixcir_ts` stores the client, input device, interrupt/reset GPIO descriptors, physical name, X/Y dimensions, touch-indicate mode flag, wait queue, and stopped flag. `struct auo_point_t` is the decoded coordinate/area/orientation representation. Key functions include `auo_pixcir_collect_data()`, `auo_pixcir_interrupt()`, `auo_pixcir_power_mode()`, `auo_pixcir_int_config()`, `auo_pixcir_int_toggle()`, `auo_pixcir_start()`, `auo_pixcir_stop()`, input open/close, suspend/resume, reset cleanup, and probe.

Control flow: probe reads required `x-size` and `y-size` properties, configures single-touch and legacy multitouch ABS axes, acquires indexed GPIO 0 as INT and indexed GPIO 1 as reset, registers reset cleanup, waits after taking the chip out of reset, reads firmware version, configures touch-indicate interrupts with active-high polarity, requests a threaded IRQ, stops the device into deep sleep, registers input, and stores client data. Opening the input powers active mode, clears `stopped`, enables the host IRQ, and enables device interrupts. The IRQ loops while not stopped; in touch-indicate mode it polls the INT GPIO for release, reads coordinate and area blocks, reports active contact slots through `input_mt_sync()`, mirrors the first contact to `ABS_X`/`ABS_Y`, and waits 10 ms between polls until release.

State and persistence: `stopped` coordinates IRQ thread termination with start/stop and suspend/resume. `touch_ind_mode` records the selected interrupt mode. Controller registers hold power and interrupt state; the driver rewrites them on start/stop. No nonvolatile state is changed.

Dependencies/integration: depends on I2C SMBus block/byte access, input core, GPIO descriptors, wait queues, PM wakeup support, OF compatible `auo,auo_pixcir_ts`, and required dimension properties. It uses old type-B-ish `input_mt_sync()` reporting rather than slot assignment.

Risks and test signals: host IRQ is requested before `auo_pixcir_stop()` disables it, so probe ordering should be tested for spurious IRQs during initialization. Touch-indicate mode loops inside the threaded IRQ and polls GPIO plus wait queue; verify stop/suspend can break the loop promptly. Coordinate properties are vendor-specific `x-size`/`y-size`, not common touchscreen size names. Test invalid coordinate clamping, two-finger reports, release detection from INT GPIO, wakeup-source suspend behavior, start failure unwind when device interrupt enable fails, and deep-sleep resume for open and closed input devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/auo-pixcir-ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/bcm_iproc_tsc.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/bcm_iproc_tsc.c

Purpose: platform driver for Broadcom iProc memory-mapped touchscreen hardware accessed through a syscon regmap. It configures scan/debounce/settling/touch timing, powers the controller on input open, handles pen and FIFO interrupts, and reports single-touch X/Y plus `BTN_TOUCH`.

Important APIs/types/functions: `struct tsc_param` contains controller timing, averaging, FIFO threshold, coordinate max/fuzz, and inversion properties. `struct iproc_ts_priv` stores the platform device, input device, syscon regmap, clock, pen status, and config. Main functions are `iproc_get_tsc_config()`, `iproc_ts_start()`, `iproc_ts_stop()`, `iproc_touchscreen_interrupt()`, `ts_reg_dump()`, and `iproc_ts_probe()`.

Control flow: probe obtains the `ts_syscon` regmap phandle, `tsc_clk`, DT configuration with defaults and range checks, allocates a BUS_HOST input device, sets axis ranges/fuzz and BTN_TOUCH, assigns open/close callbacks, requests a shared IRQ, and registers input. Opening the input enables the clock, unmasks pen/FIFO interrupts, writes FIFO threshold, programs `REGCTL1` timing, clears interrupt status, powers/enables the controller in `REGCTL2`, and dumps registers at debug level. The IRQ masks relevant interrupt status bits, clears write-one-to-clear status, reports pen up/down from `CONTROLLER_STATUS`, drains up to `fifo_threshold` coordinates from `FIFO_DATA`, discards invalid sentinel values, shifts 16-bit hardware values to 12-bit coordinates, applies optional inversion, reports axes, and syncs once.

State and persistence: runtime configuration is parsed once into `cfg_params` and written to hardware on each open. `pen_status` caches current pen state. Clock and touch-controller power are enabled only while the input device is open. The shared interrupt mask register is updated only for touchscreen bits so ADC/flextimer users are not disturbed.

Dependencies/integration: depends on platform/OF, syscon regmap, clock framework, input core, shared IRQs, and Broadcom DT compatible `brcm,iproc-touchscreen`. Configuration uses legacy property names such as `scanning_period`, `debounce_timeout`, `settling_timeout`, `touch_timeout`, `average_data`, and `fifo_threshold`, plus common touchscreen size/fuzz/inversion properties.

Risks and test signals: `clk_disable()` is used after `clk_prepare_enable()`, which should be checked against clock API expectations because many drivers use `clk_disable_unprepare()`. FIFO threshold zero is accepted but would lead to no FIFO reads when interrupts occur. No PM callbacks are present, so system suspend behavior relies on input close or platform clock/reset policy. Test property bounds, shared interrupt IRQ_NONE behavior, invalid coordinate sentinel, inversion math at max ranges, open/close clock balancing, register masks preserving non-touch bits, and FIFO threshold values from 0 to 31.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/bcm_iproc_tsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/bu21013_ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/bu21013_ts.c

Purpose: I2C multitouch driver for the ROHM BU21013 touch controller. It powers and initializes the chip, reads two-finger coordinate blocks in a threaded IRQ loop, applies touchscreen coordinate transforms, and reports type-B multitouch slots.

Important APIs/types/functions: `struct bu21013_ts` stores the I2C client, input device, touchscreen properties, regulator, chip-select/reset GPIO, optional INT GPIO, max coordinates, legacy flip flags, and `touch_stopped`. Core functions are `bu21013_read_block_data()`, `bu21013_do_touch_report()`, `bu21013_gpio_irq()`, `bu21013_init_chip()`, `bu21013_power_off()`, `bu21013_disable_chip()`, `bu21013_probe()`, `bu21013_remove()`, `bu21013_suspend()`, and `bu21013_resume()`.

Control flow: probe checks SMBus byte-data support and IRQ presence, reads legacy flip properties and max coordinates, allocates an input device, sets MT axes, parses common touchscreen properties, adjusts legacy flip ranges, initializes two direct tracking slots, enables the `avdd` regulator, asserts the chip select/reset GPIO, obtains optional INT GPIO, writes the controller register initialization sequence, requests a threaded IRQ, registers input, and stores client data. The IRQ repeatedly reads an 11-byte block from sensor/button registers, validates X/Y sensor activity, decodes up to two coordinates, filters contacts that are too close on either axis, assigns slots with `input_mt_assign_slots()`, reports active slots, syncs the frame, and continues polling while the INT GPIO remains asserted.

State and persistence: controller configuration is written during probe and after resume when not wake-capable. `touch_stopped` is a volatile flag used by remove/suspend to make the IRQ loop exit quickly. Power state is controlled by the `avdd` regulator and chip-select/reset GPIO through devm cleanup actions and PM callbacks.

Dependencies/integration: depends on I2C SMBus block/byte access, input MT, touchscreen helpers, GPIO descriptors, regulator framework, IRQ threading, and legacy ROHM properties `rohm,touch-max-x`, `rohm,touch-max-y`, `rohm,flip-x`, and `rohm,flip-y`. The driver registers I2C ID `bu21013_tp`.

Risks and test signals: probe only checks `I2C_FUNC_SMBUS_BYTE_DATA` even though reporting uses SMBus block reads; adapters should be tested for block support. `has_x_sensors` and `has_y_sensors` are declared bool but assigned hweight counts, losing count detail but preserving zero/nonzero intent. Suspend disables the regulator when not wake-capable and resume reinitializes the whole chip; test wake-capable and non-wake suspend. Test IRQ loop exit on remove/suspend, optional INT GPIO absent, two-finger close-contact rejection, legacy flip with common transform properties, regulator failures, reset GPIO polarity, and I2C retry exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/bu21013_ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/bu21029_ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/bu21029_ts.c

Purpose: I2C driver for the ROHM BU21029 resistive touchscreen controller. It powers the chip on input open, verifies hardware ID, programs filter/timing/LDO/autoscan registers, reports single-touch X/Y/pressure, and uses a timer to synthesize pen-up.

Important APIs/types/functions: `struct bu21029_ts_data` stores the I2C client, input device, pen-up timer, `vdd` regulator, optional reset GPIO, X-plate resistance, and touchscreen properties. Main functions are `bu21029_touch_report()`, `bu21029_touch_release()`, `bu21029_touch_soft_irq()`, `bu21029_put_chip_in_reset()`, `bu21029_start_chip()`, `bu21029_stop_chip()`, `bu21029_probe()`, `bu21029_suspend()`, and `bu21029_resume()`.

Control flow: probe validates needed SMBus operations, requires `rohm,x-plate-ohms`, obtains `vdd` and optional reset GPIO, allocates input with X/Y/pressure axes and common touchscreen transforms, initializes a timer, requests a no-auto-enable threaded IRQ, registers input, and stores client data. Opening the input enables the regulator, releases reset, reads and validates HW ID `0x0229`, writes CFR0/CFR1/CFR2/CFR3/LDO configuration bytes, starts autoscan, and enables IRQ. Each IRQ reads an eight-byte autoscan result, decodes 12-bit X/Y/Z1/Z2, computes pressure resistance, reports position and inverted pressure if within range, and rearms a 50 ms timer. The timer emits pressure zero and `BTN_TOUCH` release.

State and persistence: hardware is powered only while the input device is open unless wakeup policy prevents PM shutdown. The timer stores pen-up timing state, and the reset GPIO holds the chip in reset during stop. No nonvolatile controller state is modified.

Dependencies/integration: depends on I2C SMBus byte/block operations, regulators, optional GPIO reset, input core, common touchscreen properties, timers, IRQ threading, OF compatible `rohm,bu21029`, and I2C ID `bu21029`.

Risks and test signals: PM suspend/resume does nothing when `device_may_wakeup()` is true, but the driver does not enable IRQ wake in this file; wake behavior should be validated. `bu21029_touch_soft_irq()` rearms pen-up even if the block read fails after `error < 0` jumps to `out` without a release update. Pressure math assumes `z2 >= z1`; noisy samples can underflow unsigned `rz`. Test open failure cleanup, HW ID mismatch, timer deletion on close, resume while input open, pressure bounds, reset GPIO absent/present, autoscan interrupt cadence, and touchscreen transform parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/bu21029_ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/chipone_icn8318.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/chipone_icn8318.c

Purpose: I2C multitouch driver for ChipOne ICN8318 controllers. It controls a wake GPIO, hibernates the chip when closed, reads up to five touch records on interrupts, and reports direct multitouch positions through the input subsystem.

Important APIs/types/functions: `struct icn8318_data` stores the I2C client, input device, wake GPIO, and touchscreen properties. Wire records are `struct icn8318_touch` and `struct icn8318_touch_data`. Key functions are `icn8318_read_touch_data()`, `icn8318_touch_active()`, `icn8318_irq()`, `icn8318_start()`, `icn8318_stop()`, `icn8318_suspend()`, `icn8318_resume()`, and `icn8318_probe()`.

Control flow: probe requires an IRQ and a `wake` GPIO, allocates input, sets MT position capabilities, parses common touchscreen properties and requires nonzero X/Y maxima, initializes five direct drop-unused slots, requests a threaded IRQ, immediately stops/hibernates the device until open, registers input, and stores client data. Open enables IRQ and asserts wake. Close disables IRQ, writes hibernate to the power register, and deasserts wake. IRQ reads the touch data block through a two-message I2C transfer, ignores softbutton events, clamps excessive touch counts, reports active slots for update events 2/3, marks end events inactive, syncs the MT frame, and syncs input.

State and persistence: there is no persistent configuration beyond wake GPIO and input properties. Device power mode is controlled by writes to `ICN8318_REG_POWER` and by wake GPIO state. Input open/close and PM callbacks share the input mutex.

Dependencies/integration: depends on I2C core, GPIO descriptors, input MT, common touchscreen property parsing, IRQ threading, OF compatible `chipone,icn8318`, and an empty I2C ID table required by the I2C subsystem.

Risks and test signals: `icn8318_read_touch_data()` returns the raw `i2c_transfer()` count; the IRQ only treats negative values as errors, so a short positive transfer would be processed as if successful. Stop writes hibernate after disabling IRQ and does not check the write result. Softbutton reports are ignored entirely. Test missing size properties, wake GPIO polarity, open/close IRQ balancing, suspend/resume while open, short I2C transfers, touch_count clamping, release event handling, and hibernate exit timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/chipone_icn8318.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/chipone_icn8505.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/chipone_icn8505.c

Purpose: ACPI/I2C multitouch driver for ChipOne ICN8505 controllers. It loads/cache-requests platform-specific firmware, can upload firmware into controller SRAM through a programming I2C address, reads controller resolution, reports up to ten contacts, maps a softbutton to `KEY_LEFTMETA`, and hibernates/reuploads firmware across suspend/resume.

Important APIs/types/functions: `struct icn8505_data` stores the I2C client, input device, touchscreen properties, and ACPI-derived firmware name. Wire records are `struct icn8505_touch` and `struct icn8505_touch_data`. Generic transfer helpers `icn8505_read_xfer()` and `icn8505_write_xfer()` support 16-bit normal registers and 24-bit programming registers. Firmware paths include `icn8505_try_fw_upload()`, `icn8505_upload_fw()`, and `icn8505_probe_acpi()`. Touch paths include `icn8505_read_data()`, `icn8505_write_reg()`, `icn8505_touch_active()`, `icn8505_irq()`, probe, suspend, and resume.

Control flow: probe requires an IRQ, allocates input with MT position axes and `KEY_LEFTMETA`, builds firmware name `chipone/icn8505-<subsystem>.fw` from ACPI subsystem ID, uploads firmware unless the controller already identifies as running, reads resolution from config data, sets axis ranges, parses common touchscreen transforms, initializes ten direct drop-unused slots, requests a threaded IRQ, registers input, and stores client data. Firmware upload enters programming mode through magic register writes at I2C address `0x30`, writes firmware in 32-byte chunks, validates reported length and CRC32, and boots from SRAM with up to three tries. IRQ reads touch data from `0x1000`, clamps touch count, reports active slots for update events, syncs MT frame, reports `KEY_LEFTMETA` for softbutton value 1, and syncs input. Resume uploads firmware again before enabling IRQ.

State and persistence: firmware is requested from platform firmware storage and cached by the firmware class for resume, but the controller boots from SRAM and may need reupload after hibernation. Runtime state is limited to input properties and firmware name. Suspend disables IRQ and writes hibernate to the power register.

Dependencies/integration: depends on ACPI matching `CHPN0001`, ACPI subsystem IDs, firmware loader, CRC32, I2C raw transfers, input MT, common touchscreen property parsing, threaded IRQs, and unaligned endian helpers. It has no OF table in this source.

Risks and test signals: `icn8505_upload_fw()` returns `error` after the success label; if the controller was already running via the early `goto success`, `error` is the prior value from firmware request, normally zero, but this control path deserves regression coverage. Firmware upload uses undocumented magic registers and 32-byte write limits; test each failure/retry path. Normal read/write helpers validate transfer counts, unlike ICN8318. Test ACPI subsystem missing (`unknown` firmware), firmware absent, length/CRC mismatch, controller already running, suspend/resume firmware reload, resolution zero/missing property handling, softbutton reporting, excessive touch count, and IRQ disabled during firmware upload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/chipone_icn8505.c -->
