# Group Research: subset-b-005397

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/sdio.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/sdio.c

## Purpose
Implements a Greybus SD/MMC host bridge as a `gbphy_driver` for `GREYBUS_PROTOCOL_SDIO`. It presents a remote Greybus SDIO controller to the Linux MMC core by allocating an `mmc_host`, translating host capability, OCR, IOS, command, response, and data-transfer semantics into Greybus SDIO operations.

## Important APIs, Types, and Functions
`struct gb_sdio_host` owns the Greybus connection, gbphy device, `mmc_host`, current `mmc_request`, locks, workqueue, transfer cancellation state, and card state. `_gb_sdio_set_host_caps()` maps Greybus capability bits to `mmc->caps/caps2`; `_gb_sdio_get_host_ocr()` maps Greybus voltage bits to Linux OCR bits. `gb_sdio_get_caps()` fetches remote limits and programs `mmc` maximum block, segment, request, frequency, and OCR fields. `gb_mmc_request()`, `gb_mmc_set_ios()`, `gb_mmc_get_ro()`, `gb_mmc_get_cd()`, and `gb_mmc_switch_voltage()` implement `mmc_host_ops`. `gb_sdio_command()`, `_gb_sdio_send()`, `_gb_sdio_recv()`, and `gb_sdio_transfer()` encode command and data phases into `GB_SDIO_TYPE_COMMAND` and `GB_SDIO_TYPE_TRANSFER`.

## Control Flow and State
Probe allocates the MMC host, creates/enables the Greybus connection, reads capabilities, initializes locks and a single-lane workqueue, enables RX, registers the MMC host, then processes queued insert/remove events. Requests enter `gb_mmc_request()`, are rejected if removed or media absent, then run asynchronously in `gb_sdio_mrq_work()`: optional SBC, command, data chunks, optional stop, completion via `mmc_request_done()`. Transfer chunks are bounded by Greybus payload size and copied through scatterlists. STOP_TRANSMISSION marks `xfer_stop` so the active chunk loop aborts with `-EINTR`.

## Dependencies and Integration Points
Depends on Greybus core operations and `gbphy` runtime PM, Linux MMC core, scatterlist helpers, workqueues, mutexes, and spinlocks. It integrates with remote unsolicited `GB_SDIO_TYPE_EVENT` messages for card insert/remove/write-protect and calls `mmc_detect_change()`.

## Risks and Test Signals
Key risks are request lifetime races around remove, event queuing while `removed` is true, payload sizing for non-divisible block transfers, and the `single_op()` timeout check for multi-block single commands. Test signals include successful module probe/remove, card-detect changes, read/write scatterlist integrity across multi-payload transfers, STOP cancellation, runtime PM balance, and MMC core error propagation for `-ENOMEDIUM`, `-ESHUTDOWN`, and Greybus operation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/sdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/spi.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/spi.c

## Purpose
Provides the small Greybus PHY wrapper for the SPI protocol. It binds `GREYBUS_PROTOCOL_SPI` devices, creates a Greybus connection, and delegates Linux SPI controller registration to the shared Greybus SPI library in `spilib.c`.

## Important APIs, Types, and Functions
`gb_spi_probe()` creates and enables the CPort connection, calls `gb_spilib_master_init(connection, &gbphy_dev->dev, spilib_ops)`, stores the connection in gbphy driver data, and drops runtime PM autosuspend. `gb_spi_remove()` resumes the gbphy if needed, calls `gb_spilib_master_exit()`, disables the connection, and destroys it. `spi_driver` is a `gbphy_driver` registered by `module_gbphy_driver()`.

## Control Flow, State, and Integration
This file keeps no per-device state beyond the `gb_connection *` stored with `gb_gbphy_set_data()`. All protocol translation, controller config, device enumeration, and transfers live in `spilib.c`. The optional `spilib_ops` pointer is currently NULL, so no board-specific prepare/unprepare hooks are installed.

## Risks and Test Signals
The wrapper is simple, so main risks are cleanup ordering and runtime PM balance when `gb_spilib_master_init()` fails after connection enable. Test by probing a Greybus SPI interface, verifying controller/device creation from `spilib.c`, then removing and ensuring the connection and registered SPI controller disappear cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/spilib.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/spilib.c

## Purpose
Implements the reusable Greybus SPI controller library. It exposes a Linux `spi_controller`, discovers remote controller and chip-select configuration over Greybus, instantiates child SPI devices, and chunks Linux `spi_message` transfers into Greybus `GB_SPI_TYPE_TRANSFER` operations.

## Important APIs, Types, and Functions
`struct gb_spilib` stores the Greybus connection, parent device, optional hardware ops, transfer cursor state, cached controller caps, and timeout state. `gb_spilib_master_init()` allocates a SPI controller, fetches `GB_SPI_TYPE_MASTER_CONFIG`, assigns controller methods, registers the controller, and creates devices with `gb_spi_setup_device()`. `gb_spilib_master_exit()` unregisters the controller. The transfer path centers on `gb_spi_transfer_one_message()`, `gb_spi_operation_create()`, `gb_spi_decode_response()`, and `setup_next_xfer()`. Sizing helpers `tx_header_fit_operation()`, `calc_tx_xfer_size()`, and `calc_rx_xfer_size()` keep request/response payloads within Greybus limits.

## Control Flow and State
For each SPI message, the library starts at the first transfer and repeatedly builds one Greybus operation that can contain one or more SPI transfers or a partial transfer. TX bytes are copied behind the Greybus transfer descriptors; RX bytes are copied back from the response. `msg->state` uses internal sentinel values for idle, running, operation ready/done, message done, and error. Offsets allow a single large SPI transfer to span multiple Greybus operations, and `last_xfer_size` tracks how much of the current transfer was included in the most recent operation.

## Dependencies and Integration Points
Depends on Greybus operation APIs and Linux SPI core. The Greybus remote side supplies master mode bits, flags, bits-per-word mask, speed range, chip-select count, and per-chip-select device identity. Device config supports generic `spidev`, `spi-nor`, or a remote modalias. Optional `spilib_ops` hooks map to controller prepare/unprepare hardware callbacks.

## Risks and Test Signals
Risks include transfer chunking boundary errors, pointer arithmetic on `void *` buffers, unsupported bufferless transfers, timeout calculations for slow transfers, and maintaining correct `actual_length` across partial operations. `gb_spi_decode_response()` must match the request construction exactly, especially for mixed TX/RX and split transfers. Test signals include controller registration, SPI child enumeration, full-duplex transfer correctness across payload-size boundaries, mode/bits-per-word propagation, invalid remote device type handling, and clean controller unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/spilib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/spilib.h -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/spilib.h

## Purpose
Declares the public interface for the Greybus SPI library used by `spi.c` and potentially other Greybus SPI bridge wrappers.

## Important APIs and Types
`struct spilib_ops` optionally supplies `prepare_transfer_hardware()` and `unprepare_transfer_hardware()` callbacks operating on the parent `struct device`. `gb_spilib_master_init()` registers a Linux SPI controller over a Greybus connection, and `gb_spilib_master_exit()` tears it down.

## State, Dependencies, and Integration
The header forward-declares `struct device` and `struct gb_connection`, avoiding broad include dependencies. Persistent state is private to `spilib.c`; consumers only hold the Greybus connection and call init/exit.

## Risks and Test Signals
The interface risk is lifecycle symmetry: every successful `gb_spilib_master_init()` must be paired with `gb_spilib_master_exit()` before the Greybus connection is destroyed. Compile coverage should ensure users include this header without needing SPI internals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/spilib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/uart.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/uart.c

## Purpose
Implements a Greybus UART protocol driver that exposes remote Greybus UART modules as Linux TTY devices named `ttyGB*`. It bridges unsolicited RX/control/credit messages and synchronous TX/configuration operations into the TTY core.

## Important APIs, Types, and Functions
`struct gb_tty` holds gbphy and Greybus connection state, `tty_port`, minor number, line coding, input/output modem controls, write FIFO, TX work, credit accounting, completion, and locks. The unsolicited operation dispatcher `gb_uart_request_handler()` handles `GB_UART_TYPE_RECEIVE_DATA`, `GB_UART_TYPE_SERIAL_STATE`, and `GB_UART_TYPE_RECEIVE_CREDITS`. TTY operations include install/open/close/cleanup/hangup, write, write_room, chars_in_buffer, break, termios, modem get/set, throttle/unthrottle, serial info, ioctl, and icount. Probe/remove are `gb_uart_probe()` and `gb_uart_remove()`, with module init registering the TTY driver before the gbphy driver.

## Control Flow and State
Probe allocates a Greybus connection, validates max payload, allocates `gb_tty`, initializes a `tty_port`, TX work, FIFO, credits, minor IDR entry, locks, connection data, default control lines, default 9600n81 line coding, and registers the TTY device. Writes enter a FIFO under `write_lock`; `gb_uart_tx_write_work()` drains up to available firmware credits and Greybus payload capacity, sends `GB_UART_TYPE_SEND_DATA`, and returns credits on error. Incoming credit operations add credits, schedule TX, wake the TTY, and complete close waits when all credits are restored. Shutdown cancels TX, resets FIFO, flushes the remote transmitter, waits for credits, then autosuspends.

## Dependencies and Integration Points
Integrates with Greybus gbphy runtime PM, Linux TTY core, IDR minor allocation, KFIFO, workqueues, completions, GPIO-less modem control abstractions, and line coding Greybus requests. Runtime PM is acquired on port activation and dropped on shutdown.

## Risks and Test Signals
Risks include credit accounting races, blocking close if credits never return, missing `iocount` updates despite wait/ioctl support, global minor exhaustion, and handling disconnect while TTY references remain. Test signals include opening/closing multiple minors, RX flag propagation for break/parity/framing/overrun, TX backpressure via write_room/chars_in_buffer, termios-driven baud/parity/flow-control writes, throttle/unthrottle control lines, disconnect hangup, and runtime PM balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/usb.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/usb.c

## Purpose
Implements a skeleton Greybus USB host-controller driver for `GREYBUS_PROTOCOL_USB`. It wires Greybus HCD start/stop and hub-control operations into a Linux `usb_hcd`, but probe intentionally disables the protocol because required USB core changes are not upstream.

## Important APIs, Types, and Functions
`struct gb_usb_device` stores the Greybus connection and gbphy device inside `usb_hcd` private data. `hcd_start()` and `hcd_stop()` send `GB_USB_TYPE_HCD_START` and `GB_USB_TYPE_HCD_STOP`. `hub_control()` forwards root hub control fields through `GB_USB_TYPE_HUB_CONTROL` and copies the response buffer. `urb_enqueue()`, `urb_dequeue()`, `get_frame_number()`, and `hub_status_data()` are stubs. `usb_gb_hc_driver` registers these callbacks with USB core.

## Control Flow and State
Probe creates an HCD, creates/enables a Greybus connection, stores cross-pointers, sets `hcd->has_tt`, then always warns and exits with `-EPROTONOSUPPORT` before `usb_add_hcd()`. Remove assumes an HCD was added and calls `usb_remove_hcd()`, then tears down the connection and HCD.

## Dependencies and Integration Points
Depends on Greybus core, gbphy, and USB HCD core. It models a USB2 host with transaction translator support. The remote protocol owns hub behavior; this host driver only passes root hub control requests through.

## Risks and Test Signals
Because probe is disabled, real runtime coverage is mostly negative: enabling the Greybus USB interface should fail with `-EPROTONOSUPPORT` and release all resources. If re-enabled, stubs for URB enqueue/dequeue make the driver non-functional for normal USB I/O. Additional risks include remove ordering if future changes allow partial registration and `hub_control()` response-length validation for unspecified lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/vibrator.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/vibrator.c

## Purpose
Provides a Greybus vibrator class driver that exposes each remote vibrator bundle as `/sys/class/vibrator/vibratorN/timeout`. Writing a timeout turns the remote vibrator on and schedules automatic turn-off.

## Important APIs, Types, and Functions
`struct gb_vibrator_device` holds the Greybus connection, sysfs device, allocated minor, and delayed work. `turn_on()` runtime-resumes the bundle, cancels a prior delayed off, sends `GB_VIBRATOR_TYPE_ON`, and schedules `gb_vibrator_worker()`. `turn_off()` sends `GB_VIBRATOR_TYPE_OFF` and autosuspends the bundle. `timeout_store()` parses the sysfs value and calls on or off. Probe registers the connection and sysfs device; disconnect cancels work, turns off if needed, unregisters the device, frees the minor, and destroys the connection.

## Control Flow, State, and Persistence
State is in-memory only: minor allocation through `IDA`, delayed off work, and runtime PM usage. There is no persisted timeout or intensity. Probe validates a single vibrator CPort, enables the connection, creates a class device, initializes delayed work, and releases runtime PM autosuspend.

## Dependencies and Integration Points
Depends on Greybus bundle drivers rather than gbphy, device class/sysfs, IDA, delayed work, and runtime PM. It intentionally uses a custom class because no generic vibrator subsystem is used here.

## Risks and Test Signals
Risks include truncating user timeouts to `u16`, runtime PM imbalance if `turn_on()` cancels active work and `turn_off()` fails, and class lifecycle around module unload. Test signals include writing nonzero and zero timeout values, repeated timeout writes, disconnect while delayed work is pending, invalid input parsing, and ensuring the remote off operation runs before resource teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/vibrator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/iio/Kconfig

## Purpose
Defines the top-level staging Industrial I/O menu. The menu is visible only when core `IIO` support is enabled.

## Important Entries and Integration
The file sources subordinate Kconfig files for accelerometers, ADCs, ADDAC devices, DDS frequency devices, and impedance analyzers. It does not define symbols itself beyond the menu wrapper.

## Risks and Test Signals
Risk is mostly build-menu coverage: omitted sources make driver symbols unreachable. Test by running Kconfig menu or `olddefconfig` with `IIO=y/m` and verifying each sourced submenu is reachable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/iio/Makefile

## Purpose
Adds staging IIO subdirectories to the build.

## Important Entries and Integration
`obj-y` descends unconditionally into `accel/`, `adc/`, `addac/`, `frequency/`, and `impedance-analyzer/`. Individual drivers are still controlled by each subdirectory Makefile and Kconfig symbol.

## Risks and Test Signals
Risk is directory omission or stale paths. Build tests should verify selected staging IIO drivers under these subdirectories are discovered and compiled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/accel/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/iio/accel/Kconfig

## Purpose
Defines the staging accelerometer menu and the `ADIS16203` driver option.

## Important Entries and Integration
`config ADIS16203` is tristate, depends on `SPI`, selects `IIO_ADIS_LIB`, and selects `IIO_ADIS_LIB_BUFFER` when `IIO_BUFFER` is enabled. The help text names the module `adis16203`.

## Risks and Test Signals
Dependencies must match the source driver's use of SPI and ADIS library helpers. Kconfig tests should confirm buffer support is selected only when the IIO buffer core is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/accel/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/accel/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/iio/accel/Makefile

## Purpose
Builds the ADIS16203 staging accelerometer/inclinometer driver.

## Important Entries and Integration
`obj-$(CONFIG_ADIS16203) += adis16203.o` ties the C file to the Kconfig symbol.

## Risks and Test Signals
Compile coverage for `CONFIG_ADIS16203=m/y` should produce the expected object/module without building it when the symbol is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/accel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/accel/adis16203.c -->
# sources/distributed-fs/ceph-client/drivers/staging/iio/accel/adis16203.c

## Purpose
Implements an IIO SPI driver for the Analog Devices ADIS16203 programmable 360 degree inclinometer. It exposes supply, auxiliary ADC, X/Y inclination, temperature, calibration bias, and buffered scan support through the ADIS helper library.

## Important APIs, Types, and Functions
Register definitions describe data, calibration, alarm, control, status, and command registers. `adis16203_read_raw()` handles raw conversions, scale, offset, and calibration-bias reads. `adis16203_write_raw()` writes the X inclination null calibration register. `adis16203_channels` uses ADIS channel macros plus a soft timestamp. `adis16203_data` describes ADIS library behavior: read delay, MSC/GLOB/DIAG registers, self-test behavior, timeout values, and status error masks. `adis16203_probe()` allocates an IIO device, initializes ADIS state, sets up buffer/trigger support, performs initial startup, and registers the IIO device.

## Control Flow and State
Runtime state is the ADIS library `struct adis` stored as IIO private data. Probe establishes static channel metadata and direct-mode operation. Raw reads call the ADIS single-conversion path, which also checks the `ADIS16203_ERROR_ACTIVE` bit. Calibration bias uses `adis_read_reg_16()` and sign extension; writes mask to 14 bits.

## Dependencies and Integration Points
Depends on SPI, Linux IIO core, and `IIO_ADISLIB`. Device matching supports OF compatible `adi,adis16203` and SPI modalias `adis16203`. Buffer and trigger setup are delegated to `devm_adis_setup_buffer_and_trigger()`.

## Risks and Test Signals
Risks include scale/offset correctness, the comment that Y inclination is not what it appears to be, and write support only being valid for the X null calibration channel. Test signals include probe with a real or emulated SPI device, raw reads for all channels, calibration read/write round trips, ADIS diagnostic status reporting, triggered-buffer operation, and startup/self-test timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/accel/adis16203.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/adc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/iio/adc/Kconfig

## Purpose
Defines the staging ADC menu and the `AD7816` temperature sensor/ADC option.

## Important Entries and Integration
`config AD7816` is tristate, depends on `SPI` and on `GPIOLIB || COMPILE_TEST`, and builds support for AD7816/AD7817/AD7818. The module name is `ad7816`.

## Risks and Test Signals
The GPIO dependency is important because the driver requires rdwr, convert, and sometimes busy GPIOs. Kconfig and compile tests should cover all three supported IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/adc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/adc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/iio/adc/Makefile

## Purpose
Builds the AD7816 family staging ADC driver.

## Important Entries and Integration
`obj-$(CONFIG_AD7816) += ad7816.o` binds the driver object to the Kconfig symbol.

## Risks and Test Signals
Compile with `CONFIG_AD7816=m/y` should produce the module and pull required SPI/GPIO dependencies from Kconfig.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/adc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/adc/ad7816.c -->
# sources/distributed-fs/ceph-client/drivers/staging/iio/adc/ad7816.c

## Purpose
Implements a staging IIO SPI driver for AD7816/AD7817/AD7818 digital temperature sensors and ADCs. It exposes legacy custom sysfs attributes for mode, channel, current value, overtemperature interrupt threshold, and events.

## Important APIs, Types, and Functions
`struct ad7816_chip_info` stores chip ID, SPI device, rdwr/convert/busy GPIOs, cached OTI thresholds, selected channel, and operating mode. `ad7816_spi_read()` performs channel selection, conversion trigger, optional busy polling, and a 16-bit SPI read. `ad7816_spi_write()` writes OTI threshold data. Sysfs handlers expose `mode`, `available_modes`, `channel`, `value`, and event `oti`. `ad7816_event_handler()` pushes a falling threshold event. `ad7816_probe()` allocates an IIO device, initializes default OTI values, requests GPIOs, requests an optional IRQ, and registers the IIO device.

## Control Flow and State
The driver stores selected ADC channel and power mode in memory and writes threshold values to the chip. Reads toggle rdwr and convert GPIOs around SPI transactions. Channel validation differs by model: AD7816 only temperature, AD7818 channel 0 or 1, and AD7817 broader channels. Event support is tied to a low-trigger IRQ if provided.

## Dependencies and Integration Points
Depends on SPI, GPIO descriptors, IRQ support, and IIO event/sysfs APIs. OF matching covers `adi,ad7816`, `adi,ad7817`, and `adi,ad7818`; SPI IDs provide driver data used for model behavior.

## Risks and Test Signals
Risks include busy-waiting on the busy GPIO without timeout, string compare for mode requiring exact input including newline behavior, legacy custom attributes, and model-specific channel validation. Test signals include probe with required GPIOs, valid and invalid channel writes per device, temperature conversion formatting, threshold conversion bounds, IRQ event delivery, and GPIO/SPI error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/adc/ad7816.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/addac/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/iio/addac/Kconfig

## Purpose
Defines staging ADDAC options for the ADT7316/7/8 and ADT7516/7/9 temperature, ADC, and DAC family.

## Important Entries and Integration
`ADT7316` enables the shared core and depends on `GPIOLIB || COMPILE_TEST`. `ADT7316_SPI` depends on `SPI && ADT7316`, defaults to yes, and builds the SPI transport module. `ADT7316_I2C` depends on `I2C && ADT7316` and builds the I2C transport module.

## Risks and Test Signals
The split symbols must keep the shared core available whenever either bus glue is selected. Build matrix tests should cover core-only impossible states, SPI-only, I2C-only, and both transports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/addac/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/addac/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/iio/addac/Makefile

## Purpose
Builds the shared ADT7316 family core and optional SPI/I2C bus glue.

## Important Entries and Integration
`obj-$(CONFIG_ADT7316) += adt7316.o`, `obj-$(CONFIG_ADT7316_SPI) += adt7316-spi.o`, and `obj-$(CONFIG_ADT7316_I2C) += adt7316-i2c.o` mirror the split Kconfig symbols.

## Risks and Test Signals
Compile tests should ensure transport modules resolve the exported `adt7316_probe()` and `adt7316_pm_ops` symbols from the core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/addac/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/addac/adt7316-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/staging/iio/addac/adt7316-i2c.c

## Purpose
Provides I2C transport glue for the ADT7316/7/8 and ADT7516/7/9 shared IIO core.

## Important APIs, Types, and Functions
Implements `adt7316_i2c_read()`, `adt7316_i2c_write()`, `adt7316_i2c_multi_read()`, and `adt7316_i2c_multi_write()` for `struct adt7316_bus`. `adt7316_i2c_probe()` fills the bus abstraction with client pointer, IRQ, and function callbacks, then calls shared `adt7316_probe(&client->dev, &bus, id->name)`.

## Control Flow and State
The bus wrapper has no persistent state beyond the `i2c_client`; all chip state is allocated by the shared core. Reads first write the target register address and then read one byte. Multi-read/write loops clamp count to `ADT7316_REG_MAX_ADDR` and repeatedly use the single-byte helpers.

## Dependencies and Integration Points
Depends on I2C SMBus helpers, interrupt field from the client, OF and I2C ID matching, and shared PM ops from `adt7316.c`.

## Risks and Test Signals
The multi-read/write helpers do not increment the register argument in the loop, so they repeatedly access the same register; this is a notable behavior risk for callers expecting sequential access. Test signals include probe for all six compatible names, register read/write error propagation, IRQ pass-through to the core, and suspend/resume through exported PM ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/addac/adt7316-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/addac/adt7316-spi.c -->
# sources/distributed-fs/ceph-client/drivers/staging/iio/addac/adt7316-spi.c

## Purpose
Provides SPI transport glue for the ADT7316/7/8 and ADT7516/7/9 shared IIO core.

## Important APIs, Types, and Functions
Defines SPI command bytes `ADT7316_SPI_CMD_READ` and `ADT7316_SPI_CMD_WRITE`, a 5 MHz maximum clock, multi-read/write helpers, single-byte wrappers, and `adt7316_spi_probe()`. Probe validates `spi_dev->max_speed_hz`, sends three dummy writes to switch the chip from default I2C protocol to SPI protocol, builds a `struct adt7316_bus`, and calls shared `adt7316_probe()`.

## Control Flow and State
The transport keeps no private state. Multi-read first selects the starting register with a write command, then sends a read command and reads `count` bytes. Multi-write builds a command buffer containing write command, register, and data bytes. Count is clamped to `ADT7316_REG_MAX_ADDR`.

## Dependencies and Integration Points
Depends on Linux SPI APIs, OF/SPI ID tables for all six supported chip names, and shared `adt7316_pm_ops`. The shared core receives `spi_dev->irq` and `spi_dev->modalias` as the name used to infer chip family.

## Risks and Test Signals
Risks include rejecting boards configured above 5 MHz, ignoring errors from the three protocol-switch writes, and relying on modalias string positions in the shared core. Test signals include bus transactions with logic analyzer traces, max clock validation, probe for all IDs, PM suspend/resume, and register read/write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/addac/adt7316-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/addac/adt7316.c -->
# sources/distributed-fs/ceph-client/drivers/staging/iio/addac/adt7316.c

## Purpose
Implements the shared IIO core for ADT7316/7/8 and ADT7516/7/9 temperature sensor, ADC, and DAC devices. Bus-specific files provide register access; this file exposes configuration, readings, DAC outputs, interrupts, and PM behavior through legacy IIO sysfs attributes and event attributes.

## Important APIs, Types, and Functions
`struct adt7316_chip_info` caches bus callbacks, optional LDAC GPIO, logical interrupt mask, config registers, DAC config, LDAC config, DAC resolution, and chip ID. `adt7316_probe()` is exported for bus glue and performs chip-family inference from the device name, DAC bit-depth selection, optional LDAC GPIO acquisition, attribute group selection, IRQ setup, initial config writes, and IIO registration. Large groups of show/store handlers update `CONFIG1`, `CONFIG2`, `CONFIG3`, `DAC_CONFIG`, and `LDAC_CONFIG`. `adt7316_show_ad()` formats VDD, internal/external temperature, and AIN values. `adt7316_show_DAC()` and `adt7316_store_DAC()` expose four DAC channels. `adt7316_event_handler()` reads interrupt status registers and pushes IIO threshold events. PM ops call `_adt7316_store_enabled()` on suspend/resume.

## Control Flow and State
The core maintains a software mirror of configuration bytes and updates the mirror only after successful bus writes in most paths. Attribute writes parse strings, validate family-specific limits, write the target register through `chip->bus`, and update cached state. Direct ADC/DAC reads fetch live register values. Event setup requests a threaded IRQ and sets interrupt polarity in cached `config1` before initial config writes. If no LDAC GPIO is present, the core enables DAC updates through DAC/LDAC registers and adjusts ADT75xx AIN selection.

## Dependencies and Integration Points
Depends on IIO core/sysfs/events, GPIO descriptors, IRQ APIs, RTC include transitively unused in this view, and the `struct adt7316_bus` abstraction from `adt7316.h`. It exports `adt7316_probe` and `adt7316_pm_ops` for I2C/SPI modules.

## Risks and Test Signals
Risks include a very large custom sysfs surface, family detection by fixed characters in `name`, inconsistent interrupt-mask caching in `adt7316_set_int_mask()`, no central lock around many config updates, repeated code for attributes, and staging-style attributes rather than modern channel info. Test signals include probing every family member over both buses, validating all sysfs bounds and family-specific `-EPERM` paths, IRQ event mapping for temp/VDD/AIN thresholds, DAC bit-depth conversion for 8/10/12-bit devices, LDAC GPIO and register-update modes, suspend/resume enable state, and bus error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/addac/adt7316.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/addac/adt7316.h -->
# sources/distributed-fs/ceph-client/drivers/staging/iio/addac/adt7316.h

## Purpose
Defines the shared bus abstraction and exported entry points for the ADT7316 family core.

## Important APIs and Types
`ADT7316_REG_MAX_ADDR` caps register operations. `struct adt7316_bus` carries a client pointer, IRQ, and callbacks for single and multi register reads/writes. `adt7316_pm_ops` is exported for transport drivers. `adt7316_probe()` lets I2C/SPI bus glue instantiate the common IIO device.

## State, Dependencies, and Integration
The header includes `linux/types.h` and `linux/pm.h`; all persistent chip state remains private to `adt7316.c`. The abstraction allows the shared core to operate without knowing whether transactions are I2C or SPI.

## Risks and Test Signals
Callback implementations must agree on register semantics, especially multi-read/write behavior. Compile tests should ensure both transports can include the header and link against exported symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/addac/adt7316.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/frequency/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/iio/frequency/Kconfig

## Purpose
Defines staging Direct Digital Synthesis driver options.

## Important Entries and Integration
`AD9832` enables AD9832/AD9835 SPI DDS support. `AD9834` enables AD9833/AD9834/AD9837/AD9838 SPI DDS support. Both are tristate and depend on `SPI`; both expose direct access through sysfs.

## Risks and Test Signals
Dependencies match the SPI-only drivers. Kconfig tests should verify symbols appear under the DDS menu and modules are named `ad9832` and `ad9834`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/frequency/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/frequency/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/iio/frequency/Makefile

## Purpose
Builds staging DDS drivers.

## Important Entries and Integration
`obj-$(CONFIG_AD9832) += ad9832.o` and `obj-$(CONFIG_AD9834) += ad9834.o` map the Kconfig symbols to their driver objects.

## Risks and Test Signals
Build tests should cover each symbol independently and as modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/frequency/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/frequency/ad9832.c -->
# sources/distributed-fs/ceph-client/drivers/staging/iio/frequency/ad9832.c

## Purpose
Implements a staging IIO SPI driver for AD9832/AD9835 DDS devices. It exposes frequency, phase, pin-control, symbol-select, and output-enable controls through DDS sysfs macros.

## Important APIs, Types, and Functions
`struct ad9832_state` stores SPI device, master clock, cached control words, SPI messages/transfers, mutex, and DMA-aligned transfer buffers. `ad9832_calc_freqreg()` converts Hz to a 32-bit tuning word. `ad9832_write_frequency()` writes four 8-bit segments through prepared SPI transfers. `ad9832_write_phase()` writes a 12-bit phase word through two transfers. `ad9832_write()` dispatches sysfs writes for frequency registers, phase registers, pin control, frequency/phase symbol select, and output enable. `ad9832_probe()` enables AVDD/DVDD regulators and mclk, initializes SPI messages, writes reset/sleep/clear defaults, and registers the IIO device.

## Control Flow and State
All mutable device control state is cached in `ctrl_fp`, `ctrl_ss`, and `ctrl_src` under `st->lock`. Sysfs writes validate values, update cached control fields, encode big-endian command words, and call `spi_sync()`. Frequency writes reject output above Nyquist (`mclk / 2`) or zero mclk. The driver is direct-mode only and has no buffered samples.

## Dependencies and Integration Points
Depends on SPI, IIO sysfs, regulators `avdd` and `dvdd`, clock `mclk`, bitfield helpers, and `dds.h` macros. Device matching supports OF compatibles `adi,ad9832` and `adi,ad9835`, plus SPI IDs.

## Risks and Test Signals
Risks include no readback sysfs support, careful byte/register ordering for frequency and phase writes, and output-enable polarity where writing nonzero clears reset/sleep/clear. Test signals include regulator/clock probe failures, frequency boundary validation, SPI command sequences for both frequency banks and all phase banks, mutex protection under concurrent sysfs writes, and correct reset state after probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/frequency/ad9832.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/frequency/ad9834.c -->
# sources/distributed-fs/ceph-client/drivers/staging/iio/frequency/ad9834.c

## Purpose
Implements a staging IIO SPI driver for AD9833/AD9834/AD9837/AD9838 DDS devices. It exposes frequency, phase, pin-control, output-enable, output1 enable, and waveform type controls through sysfs.

## Important APIs, Types, and Functions
`struct ad9834_state` stores SPI device, mclk, cached control word, device ID, prepared SPI messages/transfers, mutex, and DMA-aligned buffers. `ad9834_calc_freqreg()`, `ad9834_write_frequency()`, and `ad9834_write_phase()` encode tuning words. `ad9834_write()` handles generic numeric sysfs controls. `ad9834_store_wavetype()` validates sine/triangle/square combinations depending on device variant and current control bits. Probe enables AVDD, enables mclk, selects the correct attribute group for AD9833/AD9837 versus AD9834/AD9838, initializes default control and default frequency/phase registers, then registers the IIO device.

## Control Flow and State
The cached `control` word is the main persistent state. Sysfs writes hold `st->lock`, update control bits, and issue a command write. Frequency writes use two 14-bit halves with chip select change. Probe initializes reset, B28, DIV2, and AD9834-specific SIGN/PIB, then writes sample default values for two frequencies and two phases.

## Dependencies and Integration Points
Depends on SPI, IIO sysfs, regulator `avdd`, master clock, and `dds.h`. Device selection comes from SPI IDs and OF compatibles for all four variants.

## Risks and Test Signals
Risks include variant-specific waveform constraints, reserved mode rejection, default frequency values exceeding low mclk rates, no readback attributes, and state/control mismatches after failed SPI writes. Test signals include probe for each variant, waveform availability output under different modes, frequency/phase boundary validation, output enable polarity, pin-controlled versus software selection behavior, and SPI trace comparison with datasheet command format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/frequency/ad9834.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/frequency/dds.h -->
# sources/distributed-fs/ceph-client/drivers/staging/iio/frequency/dds.h

## Purpose
Defines IIO sysfs attribute helper macros for DDS output devices.

## Important APIs and Integration
Macros create consistently named `IIO_DEVICE_ATTR` or `IIO_CONST_ATTR` entries for output frequency, frequency scale, frequency symbol, phase, phase scale, phase symbol, pin-control enable, pin-controlled frequency/phase enable, output enable, per-output enable, waveform type, and waveform-type availability.

## State and Dependencies
The header stores no state and depends on IIO sysfs macro definitions supplied by including C files. It standardizes older custom sysfs naming used by AD9832 and AD9834 staging drivers.

## Risks and Test Signals
Risks are name-generation compatibility and macro misuse causing mismatched attribute names. Compile tests for both DDS drivers and sysfs inspection after probe are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/frequency/dds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/impedance-analyzer/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/iio/impedance-analyzer/Kconfig

## Purpose
Defines the staging impedance converter/network analyzer menu and AD5933/AD5934 driver option.

## Important Entries and Integration
`config AD5933` is tristate, depends on `I2C`, and selects `IIO_BUFFER` plus `IIO_KFIFO_BUF`. The help text names the module `ad5933`.

## Risks and Test Signals
The selected buffer dependencies match the driver's kfifo buffered sweep implementation. Kconfig tests should verify buffer support is selected automatically.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/impedance-analyzer/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/impedance-analyzer/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/iio/impedance-analyzer/Makefile

## Purpose
Builds the AD5933/AD5934 staging impedance analyzer driver.

## Important Entries and Integration
`obj-$(CONFIG_AD5933) += ad5933.o` maps the Kconfig symbol to the driver object.

## Risks and Test Signals
Compile tests should cover module and built-in forms and ensure selected IIO buffer dependencies are available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/impedance-analyzer/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/impedance-analyzer/ad5933.c -->
# sources/distributed-fs/ceph-client/drivers/staging/iio/impedance-analyzer/ad5933.c

## Purpose
Implements an IIO I2C driver for AD5933/AD5934 impedance converter/network analyzer devices. It exposes temperature as a direct channel and real/imaginary voltage samples through an IIO kfifo buffer during frequency sweeps.

## Important APIs, Types, and Functions
`struct ad5933_state` stores the I2C client, optional mclk, delayed work, mutex, clock rate, control bytes, output ranges, supply reference, settling cycles, frequency points/start/increment, sweep state, and polling interval. Low-level helpers `ad5933_i2c_read/write()`, `ad5933_cmd()`, `ad5933_reset()`, and `ad5933_wait_busy()` handle register access and status polling. `ad5933_set_freq()` encodes 24-bit frequency registers. `ad5933_setup()` programs defaults. Sysfs handlers expose frequency start/increment, output range, settling cycles, PGA gain, and frequency points. `ad5933_read_raw()` performs direct temperature measurement. Buffer callbacks and `ad5933_work()` run sweeps and push real/imaginary samples.

## Control Flow and State
Probe enables `vdd`, determines internal versus external clock, computes output range availability from measured vref, initializes delayed work and kfifo buffer, writes default setup, and registers the IIO device. Direct writes claim direct mode to avoid races with buffered sweeps. Buffer preenable resets and initializes start frequency; postenable schedules excitation delay; worker starts sweep, polls status, reads selected real/imag channels, pushes samples, increments frequency, and powers down at sweep completion.

## Dependencies and Integration Points
Depends on I2C SMBus byte operations, optional clock `mclk`, regulator `vdd`, IIO core, IIO buffer, and kfifo buffer setup. OF/I2C IDs support `ad5933` and `ad5934`.

## Risks and Test Signals
Risks include polling with delayed work, direct-mode arbitration, endian and channel-order handling in `ad5933_work()`, output range scaling from regulator voltage, and no explicit remove cancellation beyond devm lifetime paths. Test signals include default setup register writes, temperature read validity polling, sysfs bounds for max 100 kHz output and 511 points, buffer enable/disable sequencing, active scan masks for one or two channels, sweep completion power-down, and I2C error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/iio/impedance-analyzer/ad5933.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/media/Kconfig

## Purpose
Defines top-level staging media driver configuration. `STAGING_MEDIA` gates non-production media drivers, and `STAGING_MEDIA_DEPRECATED` separately gates deprecated staging media drivers.

## Important Entries and Integration
The file depends on `MEDIA_SUPPORT` before sourcing child Kconfigs. It currently sources atomisp, av7110, imx, ipu3, ipu7, max96712, meson/vdec, sunxi, and tegra-video in alphabetical order, plus deprecated atmel under `STAGING_MEDIA_DEPRECATED`.

## Risks and Test Signals
The help text warns APIs may not match normal V4L/DVB/RC expectations. Test signals are Kconfig visibility with `MEDIA_SUPPORT`, correct gating of deprecated drivers, and build menu reachability for atomisp.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/media/Makefile

## Purpose
Routes selected staging media Kconfig symbols to their subdirectories.

## Important Entries and Integration
It descends into deprecated atmel, atomisp, imx, max96712, meson/vdec, sunxi, tegra-video, ipu3, ipu7, and av7110 based on their config symbols. For this work item, `CONFIG_INTEL_ATOMISP` builds `atomisp/`.

## Risks and Test Signals
Risks are stale symbol/path mappings and deprecated directory gating. Build tests with selected media symbols should ensure only intended subdirectories are visited.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/Kconfig

## Purpose
Defines Kconfig for Intel Atom ISP staging support and its sensor subdrivers.

## Important Entries and Integration
`INTEL_ATOMISP` is a bool depending on X86, EFI, PCI, ACPI, and COMMON_CLK, and selects IOSF_MBI and MEDIA_CONTROLLER. `VIDEO_ATOMISP` is tristate and depends on the AtomISP platform plus VIDEO_DEV, INT3472, IPU bridge, media PCI support, PMIC opregion, and I2C; it selects V4L2 fwnode, IOSF_MBI, videobuf2 vmalloc, and V4L2 subdev API. When `VIDEO_ATOMISP` is enabled, the i2c sensor Kconfig is sourced.

## Risks and Test Signals
This staging driver has many platform dependencies, so build coverage must use an x86 ACPI PCI configuration. Test signals include Kconfig dependency resolution and sensor submenu visibility only when `VIDEO_ATOMISP` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/Makefile

## Purpose
Defines the large AtomISP staging build. It builds the I2C sensor directory, the main `atomisp.o` object, platform glue, a long list of CSS/ISP runtime/kernel objects, include paths, and host-side defines.

## Important Entries and Integration
`obj-$(CONFIG_INTEL_ATOMISP) += i2c/` builds sensor modules under the AtomISP platform symbol. `obj-$(CONFIG_VIDEO_ATOMISP) += atomisp.o` and `pci/atomisp_gmin_platform.o` build the ISP driver and ACPI/GMIN platform glue. `atomisp-objs` aggregates V4L2, HMM, MMU, CSS host, runtime, ISP kernel, and system-local objects. `INCLUDES` points throughout the staging atomisp tree, and `ccflags-y` adds includes and defines such as `HRT_HW`, `HRT_ISP_CSS_CUSTOM_HOST`, `HRT_USE_VIR_ADDRS`, and `__HOST__`.

## Control Flow and State
This Makefile does not contain runtime state but heavily shapes compile-time integration. Debug is enabled while in staging, and a duplicate object/include entries are present in the list.

## Risks and Test Signals
Risks include brittle include-path sprawl, duplicate object entries, platform-specific defines, and high build fragility under compiler flag changes. Test signals are successful `CONFIG_VIDEO_ATOMISP` builds, no duplicate-symbol issues from repeated object entries, and sensor subdirectory compilation with `CONFIG_INTEL_ATOMISP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/i2c/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/i2c/Kconfig

## Purpose
Defines AtomISP sensor-level I2C drivers.

## Important Entries and Integration
`VIDEO_ATOMISP_OV2722` enables an OVT OV2722 raw camera sensor and depends on ACPI plus I2C/VIDEO_DEV. `VIDEO_ATOMISP_GC2235` enables GalaxyCore GC2235 raw camera support with the same dependencies. Both help texts state they currently only work with atomisp.

## Risks and Test Signals
The GC2235 help text calls it OVT despite being GalaxyCore, indicating stale copy. Kconfig tests should ensure these symbols are visible only under AtomISP and compile only on ACPI/I2C camera configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/i2c/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/i2c/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/i2c/Makefile

## Purpose
Builds AtomISP I2C sensor drivers.

## Important Entries and Integration
`obj-$(CONFIG_VIDEO_ATOMISP_GC2235) += atomisp-gc2235.o` and `obj-$(CONFIG_VIDEO_ATOMISP_OV2722) += atomisp-ov2722.o` map sensor symbols to modules.

## Risks and Test Signals
Compile tests should cover each sensor symbol independently and confirm the modules link against AtomISP platform helper interfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/i2c/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/i2c/atomisp-gc2235.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/i2c/atomisp-gc2235.c

## Purpose
Implements a V4L2 subdevice driver for the GalaxyCore GC2235 2MP raw camera sensor used with Intel AtomISP. It handles I2C register programming, power sequencing through AtomISP platform callbacks, exposure control, format/resolution selection, streaming, and sensor registration.

## Important APIs, Types, and Functions
Low-level I2C helpers include `gc2235_read_reg()`, `gc2235_i2c_write()`, `gc2235_write_reg()`, and buffered register-array helpers that coalesce consecutive writes and honor delay tokens. Exposure paths are `__gc2235_set_exposure()`, `gc2235_set_exposure()`, `gc2235_s_exposure()`, and `gc2235_q_exposure()`. Power helpers `power_ctrl()`, `gpio_ctrl()`, `power_up()`, and `power_down()` call platform callbacks. V4L2 operations include `gc2235_s_power()`, `gc2235_set_fmt()`, `gc2235_get_fmt()`, `gc2235_s_stream()`, frame size/code enumeration, frame interval, skip frames, volatile exposure control, and AtomISP private ioctl handling. Probe allocates `struct gc2235_device`, fetches GMIN platform data, configures/detects the sensor, initializes controls and media entity pads, then registers with AtomISP.

## Control Flow and State
Device state includes the selected resolution, media pad/format, control handler, platform data, and `input_lock`. A file-scope `is_init` flag controls whether startup power-cycles and reinitializes before resolution changes. `gc2235_s_config()` powers down, powers up, enables CSI, detects the sensor ID, then powers down after probe. `gc2235_set_fmt()` chooses the nearest preview resolution, stores it, and for active formats writes init/resolution registers. Streaming writes static stream-on/off register arrays.

## Dependencies and Integration Points
Depends on I2C, V4L2 subdev/media entity/control APIs, ACPI match `INT33F8`, AtomISP GMIN platform data, sensor-specific `gc2235.h` register tables, and AtomISP private exposure ioctl `ATOMISP_IOC_S_EXPOSURE`.

## Risks and Test Signals
Risks include global `is_init` across devices, inconsistent media bus code between set/get and enum paths, register write return values overwritten in exposure programming, platform callback failure handling, and tight coupling to AtomISP private APIs. Test signals include ACPI probe, power sequencing timing, sensor ID detection, register-array coalescing with delay tokens, exposure/gain boundary behavior, format negotiation for try and active states, stream on/off register writes, CSI cleanup on remove, volatile exposure readback, and skip-frame values per selected resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/i2c/atomisp-gc2235.c -->
