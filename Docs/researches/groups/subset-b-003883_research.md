# Research: subset-b-003883

This grouped report covers Analog Devices IIO DAC and mixed-signal DAC source files under `sources/distributed-fs/ceph-client/drivers/iio/dac/`. Each section preserves the original source path so the reconciliation lane can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5504.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5504.c

## Purpose
`ad5504.c` is a Linux IIO SPI driver for the Analog Devices AD5504 four-channel and AD5501 single-channel high-voltage DACs. It exposes voltage output channels through direct-mode IIO raw/scale attributes, per-channel powerdown controls, a shared powerdown mode enum, and an optional temperature-threshold event if an interrupt line is wired.

## Important APIs, Types, And Functions
- `struct ad5504_state` stores the SPI device, optional regulator-derived/reference voltage, powerdown shadow state, and DMA-aligned 16-bit transfer buffers.
- `ad5504_spi_write()` formats a 16-bit command with write/read bit, register address, and 12-bit payload.
- `ad5504_spi_read()` performs a 16-bit command/response SPI transfer and masks the returned 12-bit DAC value.
- `ad5504_read_raw()` supports `IIO_CHAN_INFO_RAW` and `IIO_CHAN_INFO_SCALE`.
- `ad5504_write_raw()` writes validated raw DAC codes.
- `ad5504_read_dac_powerdown()` and `ad5504_write_dac_powerdown()` implement the `powerdown` ext_info sysfs attribute.
- `ad5504_event_handler()` pushes a fixed rising temperature threshold event via IIO when `spi->irq` fires.
- `ad5504_probe()` allocates/registers the IIO device, reads `vcc` or platform-data reference voltage, chooses one or four channels by device id, and requests the optional threaded IRQ.

## Control Flow
Probe allocates a devm IIO device, resolves the reference voltage, initializes channel metadata and `INDIO_DIRECT_MODE`, then registers the IIO device. Raw writes validate against the 12-bit channel width and write directly to the channel DAC register. Raw reads issue an SPI read for the channel register. Powerdown writes update the software mask, write the control register with the selected mode, then issue the mandatory NOOP write required after CTRL writes. IRQ handling is independent of DAC data flow and only pushes the temperature event.

## State And Persistence
Persistent runtime state is limited to `vref_mv`, `pwr_down_mask`, `pwr_down_mode`, and the SPI buffer. DAC output registers persist in the chip, but the driver does not cache raw output values. Powerdown state is a software shadow that is synchronized to the control register when the sysfs attribute is written. All state is lost on driver removal or device reset.

## Dependencies And Integration Points
The driver integrates with SPI, regulators, IIO direct-mode DAC sysfs, IIO events, optional platform data from `linux/iio/dac/ad5504.h`, and optional interrupt wiring. Device binding is through SPI IDs `ad5504` and `ad5501`; AD5501 limits `num_channels` to one while reusing the same channel table.

## Risks And Edge Cases
- `ad5504_probe()` dereferences `pdata` when `ret == -ENODEV`; if no regulator and no platform data are provided, `pdata->vref_mv` can fault. A defensive NULL check is a key test target.
- `ad5504_read_dac_powerdown()` returns the inverse of the mask bit, while write clears the mask when `pwr_down` is true. This naming inversion is subtle and should be validated against the ABI expectation and datasheet.
- CTRL writes ignore the return value of the follow-up NOOP, so a NOOP failure is not reported.
- There is no mutex around the shared transfer buffer; concurrent IIO reads/writes could race if the IIO core permits overlapping direct accesses.

## Test Signals
Useful tests include probe with and without regulator/platform reference, AD5501 channel count, raw write bounds, SPI command encoding for read/write/control/NOOP, powerdown mode/mask behavior, IRQ event emission, and failure propagation for SPI read/write paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5504.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5592r-base.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5592r-base.c

## Purpose
`ad5592r-base.c` is the shared IIO and GPIO implementation for the AD5592R SPI and AD5593R I2C configurable eight-channel mixed ADC/DAC/GPIO devices. Bus-specific files provide register and data-path callbacks through `struct ad5592r_rw_ops`, while this base file handles firmware channel modes, IIO channel construction, raw ADC/DAC access, scale/range control, reset, reference handling, and optional GPIO chip registration.

## Important APIs, Types, And Functions
- `ad5592r_probe()` and `ad5592r_remove()` are exported in namespace `IIO_AD5592R` for the SPI and I2C wrappers.
- `ad5592r_set_channel_modes()` converts firmware `adi,mode` and `adi,off-state` values into DAC enable, ADC enable, pulldown, tristate, GPIO input/output, and GPIO value registers.
- `ad5592r_alloc_channels()` reads child fwnodes, builds the dynamic IIO channel list, and always appends the internal temperature channel.
- `ad5592r_read_raw()` reads ADC channels, returns cached DAC writes for output channels, reports scale, and calculates temperature offset.
- `ad5592r_write_raw()` writes DAC values and switches ADC or DAC gain bits in `AD5592R_REG_CTRL`.
- GPIO callbacks `ad5592r_gpio_get()`, `ad5592r_gpio_set()`, `ad5592r_gpio_direction_input()`, `ad5592r_gpio_direction_output()`, and `ad5592r_gpio_request()` expose channels configured as GPIOs.
- `ad5592r_reset()` uses an optional reset GPIO or writes the reset magic value to the reset register.

## Control Flow
Probe allocates the IIO device, initializes the bus callback table and mutex, enables optional `vref`, computes available scales, resets the chip, configures internal/external reference powerdown, allocates channels from firmware, applies channel modes, registers the IIO device, then registers a GPIO chip if any channels are marked GPIO. Runtime raw writes go through the bus `write_dac` callback and update `cached_dac`; raw ADC reads call `read_adc`, verify that the returned channel tag matches, and strip the 12-bit sample. Scale writes read-modify-write the control register cache to set ADC or DAC range bits.

## State And Persistence
`struct ad5592r_state` persists firmware-derived `channel_modes` and `channel_offstate`, GPIO maps and values, `cached_gp_ctrl`, cached DAC values, available scale pairs, regulator pointer, and the bus transfer buffers. The driver treats DAC readback as a software cache for output channels. GPIO state is protected by `gpio_lock`; SPI/I2C register/data sequences are protected by `lock`. Removal unregisters IIO, resets all channel modes to unused/off-state, removes GPIO, and disables the regulator.

## Dependencies And Integration Points
The base depends on IIO, gpiolib, firmware property APIs, regulators, mutex cleanup helpers, and `dt-bindings/iio/adi,ad5592r.h` channel mode constants. It integrates with transport wrappers through `ad5592r_rw_ops` and with gpiolib only for channels explicitly configured as GPIO.

## Risks And Edge Cases
- GPIO chip registration happens after IIO device registration; if GPIO registration fails, IIO is unregistered and channels are reset, but consumers briefly observing the IIO device during probe failure are theoretically possible.
- `ad5592r_write_raw_get_fmt()` returns `IIO_VAL_INT_PLUS_MICRO` for non-scale masks even though raw writes are integer; this ABI detail should be checked against IIO expectations.
- Firmware parsing silently ignores invalid/missing child `reg`; invalid `adi,mode` values are treated as unused when applying channel modes.
- `ad5592r_reset()` does not propagate failure from reset-register write in the non-GPIO path because the scoped guard body return is not captured; the delay still occurs and probe continues. This is worth targeted review.
- Temperature scale and offset formulas depend on fixed-point arithmetic and reference voltage; regression tests should pin expected values.

## Test Signals
Test fwnode configurations for DAC, ADC, DAC_AND_ADC, GPIO, and unused off-states; register write ordering in channel setup; ADC readback channel-tag validation; DAC cache readback; gain scale switching; optional regulator and internal reference behavior; GPIO direction/value paths; reset GPIO and register-reset paths; and cleanup on mid-probe errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5592r-base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5592r-base.h -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5592r-base.h

## Purpose
`ad5592r-base.h` defines the common contract shared by the AD5592R SPI wrapper, AD5593R I2C wrapper, and the base mixed-signal driver. It centralizes register IDs, control-bit definitions, transport operations, shared driver state, and exported probe/remove prototypes.

## Important APIs, Types, And Functions
- `enum ad5592r_registers` defines common register addresses, including DAC/ADC enable, GPIO, pull-down, powerdown, LDAC, tristate, and reset registers.
- `AD5592R_REG_PD_EN_REF`, `AD5592R_REG_CTRL_ADC_RANGE`, and `AD5592R_REG_CTRL_DAC_RANGE` define shared control bits.
- `struct ad5592r_rw_ops` is the bus abstraction with callbacks for DAC write, ADC read, generic register read/write, and GPIO read.
- `struct ad5592r_state` is the shared private state used by base and transport code, including IIO/GPIO state, caches, channel modes, and DMA-aligned SPI buffers.
- `ad5592r_probe()` and `ad5592r_remove()` are declared for bus drivers.

## Control Flow
This header does not execute logic. Its main control-flow role is shaping how bus wrappers call into `ad5592r_probe()` with an operations table and how the base driver calls back into SPI/I2C-specific register functions.

## State And Persistence
The declared `ad5592r_state` persists cached DAC values, cached control register, channel modes/off-states, GPIO direction/value maps, regulator pointer, and synchronization primitives. It also contains SPI-specific buffers even though the base is bus-neutral, allowing the SPI wrapper to reuse the common allocation.

## Dependencies And Integration Points
The header depends on Linux types, cache alignment, mutexes, gpiolib, and IIO. It is included by `ad5592r-base.c`, `ad5592r.c`, and `ad5593r.c`, and its exported namespace is declared by the C files rather than in the header.

## Risks And Edge Cases
- The state structure is shared by transport and base logic, so layout changes can break both buses.
- Bus-neutral code contains SPI transfer buffers; future non-SPI expansion should avoid assuming those buffers are meaningful.
- GPIO and IIO caches are byte-sized, which matches the eight-channel hardware but should be revisited if support for variants with different channel counts is added.

## Test Signals
Compile coverage for both SPI and I2C wrappers is important after any signature or state changes. Tests should validate that every callback in `ad5592r_rw_ops` is provided before probe and that channel count assumptions remain eight-wide.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5592r-base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5592r.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5592r.c

## Purpose
`ad5592r.c` is the SPI transport wrapper for the AD5592R configurable eight-channel ADC/DAC/GPIO device. It implements the wire protocol required by the shared AD5592R base driver and registers the SPI, OF, and ACPI device IDs.

## Important APIs, Types, And Functions
- `ad5592r_spi_wnop_r16()` clocks a NOP word and receives a 16-bit response.
- `ad5592r_write_dac()` formats direct DAC writes as `BIT(15) | channel | value`.
- `ad5592r_read_adc()` programs the ADC sequence, discards the first invalid conversion result, then reads the valid conversion with another NOP.
- `ad5592r_reg_write()` and `ad5592r_reg_read()` implement register writes/readback, using LDAC readback enable for register reads.
- `ad5592r_gpio_read()` enables GPIO readback and clocks the returned value.
- `ad5592r_spi_probe()` delegates to `ad5592r_probe()` with `ad5592r_rw_ops`; remove calls `ad5592r_remove()`.

## Control Flow
SPI probe resolves the SPI ID and hands the device to the common base. All runtime IIO and GPIO operations enter through base code and are dispatched to this file’s callbacks. ADC reads require a multi-step sequence: write ADC sequence register, NOP to discard invalid data, NOP to capture valid data. Register reads write an LDAC readback selector and then NOP-read the selected register.

## State And Persistence
The SPI wrapper uses `st->spi_msg` and `st->spi_msg_nop` buffers from shared state. Persistent state remains owned by the base driver; this file only performs transport operations.

## Dependencies And Integration Points
The file depends on SPI core, module device tables, bitops, and the exported `IIO_AD5592R` base namespace. It supports SPI ID `ad5592r`, OF compatible `adi,ad5592r`, and ACPI ID `ADS5592`.

## Risks And Edge Cases
- SPI readback sequences are timing/order sensitive; changing transfer grouping can break ADC validity or register readback.
- `gpio_read()` casts the 16-bit returned word to `u8`; this matches GPIO bit width but can hide unexpected high bits.
- The wrapper assumes `st->dev` is embedded in a `struct spi_device`; this is guaranteed only when called from the SPI probe path.

## Test Signals
Mock SPI transfer tests should cover DAC write encoding, ADC double-NOP sequencing, register readback command encoding, GPIO readback setup, probe/remove delegation, and failure propagation from each `spi_write`/`spi_sync_transfer`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5592r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5593r.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5593r.c

## Purpose
`ad5593r.c` is the I2C transport wrapper for the AD5593R configurable ADC/DAC/GPIO device. It maps the AD5592R base driver’s bus operations onto SMBus/I2C transactions and registers I2C, OF, and ACPI IDs.

## Important APIs, Types, And Functions
- `ad5593r_read_word()` writes a register/mode byte and receives a big-endian 16-bit value with `i2c_master_recv()`.
- `ad5593r_write_dac()` writes DAC data with the AD5593R DAC write mode.
- `ad5593r_read_adc()` configures ADC sequence and then reads back ADC data.
- `ad5593r_reg_write()` and `ad5593r_reg_read()` implement common register access over I2C mode bytes.
- `ad5593r_gpio_read()` reads the GPIO readback mode.
- `ad5593r_i2c_probe()` checks adapter support for SMBus byte plus raw I2C receive and delegates to `ad5592r_probe()`.

## Control Flow
I2C probe validates adapter capabilities and calls the common probe. Runtime operations enter from the base driver callback table. Register writes are SMBus word-swapped operations; reads are two-step operations that select a mode/register byte and read two bytes. ADC read writes the sequence register first, then reads the ADC readback mode.

## State And Persistence
All durable state is in the shared `ad5592r_state`. This file does not add local cache state. Transport buffers are stack-local for I2C reads.

## Dependencies And Integration Points
The file depends on I2C core, SMBus helpers, unaligned big-endian helpers, and the `IIO_AD5592R` namespace. It supports I2C ID `ad5593r`, OF compatible `adi,ad5593r`, and ACPI ID `ADS5593`.

## Risks And Edge Cases
- Probe checks `I2C_FUNC_SMBUS_BYTE | I2C_FUNC_I2C` but uses `i2c_smbus_write_word_swapped()` as well; adapter capability expectations should be verified.
- `ad5593r_read_word()` treats short positive `i2c_master_recv()` returns as success; a short read could leave stale stack bytes. A robust path would require `ret == sizeof(buf)`.
- Endianness depends on mixed SMBus swapped writes and big-endian reads matching the device protocol.

## Test Signals
Test I2C mode-byte selection, write-word-swapped payloads, short-read handling, ADC sequence setup, GPIO readback, capability rejection, and base probe/remove integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5593r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5624r.h -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5624r.h

## Purpose
`ad5624r.h` contains register command/address constants, device IDs, chip metadata, and private state definitions for the AD5624R/AD5644R/AD5664R SPI DAC driver family.

## Important APIs, Types, And Functions
- `AD5624R_*` constants define DAC addresses, command opcodes, LDAC/powerdown modes, and the four-channel count.
- `struct ad5624r_chip_info` binds a channel table to the internal reference voltage for each variant.
- `struct ad5624r_state` stores the SPI device, chip info pointer, reference voltage, and powerdown state.
- `enum ad5624r_supported_device_ids` enumerates 12-, 14-, and 16-bit variants with 1.25 V or 2.5 V internal references.

## Control Flow
This header has no executable control flow. It supplies constants and structures used by `ad5624r_spi.c` to format 24-bit SPI commands and select channel metadata during probe.

## State And Persistence
The declared state persists the active reference in millivolts, selected chip table, and powerdown mask/mode. It does not contain a DAC data cache.

## Dependencies And Integration Points
The header is local to the AD5624R SPI driver and expects Linux SPI/IIO types to be visible in the including C file.

## Risks And Edge Cases
- The header defines state without its own includes for `struct spi_device` or `struct iio_chan_spec`; it relies on include ordering from the C file.
- Since the state has no data cache, raw readback is unavailable and sysfs raw reads are not implemented by the driver.

## Test Signals
Compile coverage of all enum indices against the chip info table is the main signal. Any addition of variants should test channel bit width, internal reference, and command shift alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5624r.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5624r_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5624r_spi.c

## Purpose
`ad5624r_spi.c` is an IIO SPI DAC driver for four-channel AD5624R, AD5644R, and AD5664R variants. It exposes raw writes, scale reads, per-channel powerdown, and shared powerdown-mode selection.

## Important APIs, Types, And Functions
- `ad5624r_spi_write()` encodes the 24-bit command frame with command, DAC address, and bit-width-dependent data shift.
- `ad5624r_read_raw()` reports scale from `st->vref_mv` and channel realbits.
- `ad5624r_write_raw()` validates raw DAC codes and writes with `WRITE_INPUT_N_UPDATE_N`.
- Powerdown helpers implement `powerdown` and `powerdown_mode` ext_info attributes.
- Channel macros create 12-, 14-, and 16-bit four-channel tables.
- `ad5624r_probe()` resolves external or internal reference, programs internal reference setup, and registers the IIO device.

## Control Flow
Probe allocates the IIO device, attempts external `vref` then legacy `vcc`, chooses the reference source, selects chip info by SPI ID, assigns channels, writes the internal-reference setup command, and registers. Runtime writes issue one 24-bit SPI frame per raw value. Powerdown writes update the mask and issue a powerdown command carrying mode plus channel mask.

## State And Persistence
The driver stores reference voltage, selected chip info, and powerdown mask/mode. DAC output values persist in hardware but are not cached/read back. Regulators are devm-enabled through helper APIs.

## Dependencies And Integration Points
The file integrates with SPI, regulator consumers, IIO direct mode, IIO sysfs ext_info, and the local `ad5624r.h` definitions. SPI IDs distinguish bit depth and internal reference voltage.

## Risks And Edge Cases
- `ad5624r_probe()` computes `st->vref_mv = external_vref ? ... : st->chip_info->int_vref_mv` before assigning `st->chip_info`; the no-external-reference path can dereference an uninitialized pointer. This is a high-value bug signal.
- The internal-reference setup writes `external_vref` as the payload; the polarity must be checked against the datasheet because the command name suggests enabling internal reference.
- There is no lock or DMA-aligned persistent transfer buffer for the 3-byte stack message, though `spi_write()` copies synchronously for common controllers.
- Raw reads are unsupported; users only get scale and write-only DAC behavior.

## Test Signals
Probe tests must cover external vref, legacy vcc, and no-regulator internal-reference paths. Additional tests should cover command packing for 12/14/16-bit variants, raw bounds, powerdown mask/mode writes, and channel table selection by ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5624r_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5686-spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5686-spi.c

## Purpose
`ad5686-spi.c` is the SPI transport implementation for the shared AD5686/AD567x/AD569x DAC family driver. It handles multiple register map encodings and delegates common IIO behavior to `ad5686.c`.

## Important APIs, Types, And Functions
- `ad5686_spi_write()` emits 2-byte or 3-byte SPI frames depending on `AD5310_REGMAP`, `AD5683_REGMAP`, or `AD5686_REGMAP`.
- `ad5686_spi_read()` implements readback enable plus NOP read for register maps that support readback.
- `ad5686_spi_probe()` calls `ad5686_probe()` with the SPI write/read callbacks.
- SPI IDs map part names to `enum ad5686_supported_device_ids`.

## Control Flow
Probe obtains the SPI ID and delegates to common probe. Runtime writes enter through `st->write` and are encoded according to the chip info’s `regmap_type`. Runtime reads program readback and then clock a NOP frame; AD5310 readback returns `-ENOTSUPP`.

## State And Persistence
The SPI wrapper uses `struct ad5686_state` transfer buffers and chip info selected by common probe. It maintains no independent persistent state.

## Dependencies And Integration Points
The file depends on SPI core, the common `ad5686.h` API, and imports namespace `IIO_AD5686`. Supported parts include AD5310R, AD5672R/74R/76/76R/79R, and AD5681R/82R/83/83R/84/84R/85R/86/86R.

## Risks And Edge Cases
- `AD5683_REGMAP` uses `&d8[1]` of a big-endian 32-bit word for a 3-byte frame; tests should pin byte ordering.
- Unsupported readback for AD5310 means common raw reads can return `-ENOTSUPP`; user ABI behavior should be acceptable for those parts.
- The SPI ID includes `"ad5685"` mapped to `ID_AD5685R` with a comment that the part does not exist; this compatibility alias should not be propagated without review.

## Test Signals
Transport tests should validate per-regmap write frames, readback commands, NOP transfer ordering, AD5310 read failure behavior, and correct chip ID mapping from SPI device IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5686-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5686.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5686.c

## Purpose
`ad5686.c` is the common IIO implementation for a broad family of Analog Devices voltage-output DACs accessed over SPI or I2C. It defines chip tables, channel layouts, raw read/write handling, scale reporting, powerdown attributes, and reference setup.

## Important APIs, Types, And Functions
- `ad5686_probe()` is exported in namespace `IIO_AD5686` for SPI/I2C wrappers.
- `ad5686_read_raw()` calls transport readback, applies channel shift/mask, and reports scale.
- `ad5686_write_raw()` validates raw DAC codes and writes `WRITE_INPUT_N_UPDATE_N`.
- `ad5686_read_dac_powerdown()` and `ad5686_write_dac_powerdown()` expose per-channel powerdown.
- `ad5686_get_powerdown_mode()` and `ad5686_set_powerdown_mode()` store two-bit per-channel powerdown modes.
- Channel declaration macros model one-, two-, four-, eight-, and sixteen-channel variants with different bit widths and register addresses.
- `ad5686_chip_info_tbl` binds each supported ID to channels, internal reference voltage, channel count, and register map type.

## Control Flow
Transport wrappers allocate the common state through `ad5686_probe()`. Probe selects chip info, resolves optional `vcc`, initializes default 1 kohm pulldown powerdown mode for every channel, configures IIO metadata, initializes the mutex, chooses the reference-control command based on register map type, writes reference setup, and registers the IIO device. Runtime raw reads/writes lock around transport callbacks. Powerdown writes update software masks, fold in powerdown modes and reference bits, and write the proper powerdown/control register.

## State And Persistence
`struct ad5686_state` stores chip metadata, reference voltage, powerdown mask/mode, transport function pointers, internal-reference flag, mutex, and DMA-aligned transfer buffers. Raw values are not cached; readback depends on transport/device support. Powerdown state is cached and pushed to hardware on writes.

## Dependencies And Integration Points
The common code integrates with IIO direct mode, regulator consumers, mutexes, and bus wrappers in `ad5686-spi.c` and `ad5696-i2c.c`. Device matching and regmap type selection are split across wrappers and the chip table.

## Risks And Edge Cases
- Raw write validation uses `val > (1 << realbits)` instead of `>=`, allowing a value exactly one past the maximum representable code. This is a likely off-by-one defect.
- Reference setup computes `val = (has_external_vref | ref_bit_msk)` and writes `!!val`, which collapses bitmask detail to 0/1. This may be intentional for command payloads but is easy to break when adding register maps.
- Powerdown mode is stored with `mode + 1`, so unset fields decode as `-1`; initial defaults avoid this for known channels, but any new channel count mismatch can expose invalid enum values.
- AD5674R/AD5679R 16-channel powerdown split uses `address = 0x8` and shifts the value by `address * 2`; test coverage should verify high-channel encoding.

## Test Signals
Tests should cover chip table indices, scale for internal/external references, raw read/write bounds, each register map’s reference setup, powerdown mode and mask encoding for low/high channels, readback unsupported behavior, and namespace integration with SPI/I2C wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5686.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5686.h -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5686.h

## Purpose
`ad5686.h` is the shared interface and register-definition header for the AD5686 family common driver and its SPI/I2C transport wrappers.

## Important APIs, Types, And Functions
- Command/address/data macros define AD5310, AD5683, AD5686, and AD5693 register map layouts.
- `enum ad5686_supported_device_ids` enumerates supported AD531x, AD533x, AD567x, AD568x, and AD569x variants.
- `enum ad5686_regmap_type` selects transport command formatting.
- `ad5686_write_func` and `ad5686_read_func` define transport callback signatures.
- `struct ad5686_chip_info` binds internal reference, channel count, channel table, and register map type.
- `struct ad5686_state` stores common driver state and transfer buffers.
- `ad5686_probe()` is the common probe entry called by bus wrappers.

## Control Flow
The header does not execute logic. It defines the callback contract used when bus drivers call `ad5686_probe()` and when common IIO operations call `st->write` or `st->read`.

## State And Persistence
The declared state persists device metadata, reference voltage, powerdown state, transport callbacks, internal-reference flag, mutex, and DMA-safe transfer buffers for SPI/I2C use.

## Dependencies And Integration Points
It depends on Linux types, cache alignment, mutexes, kernel macros, and IIO channel types. It is included by `ad5686.c`, `ad5686-spi.c`, and `ad5696-i2c.c`.

## Risks And Edge Cases
- Register map constants are shared by both buses; a bus-specific encoding mistake can appear as a common-driver issue.
- The state field comments still mention `spi` although the state stores `struct device *dev`, reflecting the shared transport evolution.
- Callback types return an `int`, so read callbacks encode either negative errno or positive register value; common callers must preserve that convention.

## Test Signals
Compile and probe tests across every enum entry are important after adding variants. Static checks should ensure chip table coverage matches `ad5686_supported_device_ids` and that every transport supports the regmap types it advertises.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5686.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5696-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5696-i2c.c

## Purpose
`ad5696-i2c.c` is the I2C transport implementation for the shared AD5686 family DAC driver, covering I2C-connected AD5311R, AD5337R/38R, AD567x, and AD569x variants.

## Important APIs, Types, And Functions
- `ad5686_i2c_write()` sends a 3-byte command/address/value frame with `i2c_master_send()`.
- `ad5686_i2c_read()` performs a combined write/read `i2c_transfer()` to retrieve two bytes.
- `ad5686_i2c_probe()` calls the common `ad5686_probe()` with I2C callbacks and chip ID.
- I2C and OF ID tables map part names/compatibles to common chip IDs.

## Control Flow
Probe resolves the I2C device ID and delegates common setup to `ad5686_probe()`. Runtime common-driver calls format a 24-bit command word and use the upper three bytes for writes. Reads write a three-byte selector and then read a two-byte response into the shared buffer.

## State And Persistence
The file relies on common `ad5686_state`; it adds no transport-local persistent state. Shared transfer buffers are reused for I2C message payloads.

## Dependencies And Integration Points
The file integrates with I2C core, OF matching, module tables, and the common `IIO_AD5686` namespace.

## Risks And Edge Cases
- `ad5686_i2c_read()` treats any non-negative `i2c_transfer()` return as success; a partial transfer count other than 2 should be considered `-EIO`.
- The read path writes into `st->data[0].d16` through a casted buffer while also using `d8[1]` for the command; byte overlap assumptions should be tested.
- OF match table does not include every I2C ID listed in the ID table, such as `adi,ad5673r` and `adi,ad5677r`.

## Test Signals
Test exact I2C write frame bytes, combined transfer handling including short-transfer returns, chip ID mapping, OF compatible coverage, readback value endianness, and common probe behavior with internal/external references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5696-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5755.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5755.c

## Purpose
`ad5755.c` is an SPI IIO driver for AD5755/AD5755-1/AD5757/AD5735/AD5737 industrial current/voltage output DACs. It supports four channels, firmware-defined output modes, calibration gain/offset registers, DC-DC converter configuration, slew configuration, and per-channel power sequencing.

## Important APIs, Types, And Functions
- `struct ad5755_platform_data` captures firmware/platform configuration for DC-DC, output mode, current sense, overrange, and slew.
- `struct ad5755_state` stores SPI device, chip info, powerdown bitmask, per-channel control shadows, dynamic channel specs, mutex, and transfer buffers.
- `ad5755_write_unlocked()`, `ad5755_write_ctrl_unlocked()`, and locked wrappers perform 24-bit SPI writes.
- `ad5755_read()` performs read-command plus NOOP readback.
- `ad5755_set_channel_pwr_down()` sequences DC-DC/internal/output enable bits with required delay.
- `ad5755_read_raw()` and `ad5755_write_raw()` handle raw, scale, offset, calibration scale, and calibration bias.
- `ad5755_setup_pdata()` programs DC-DC, slew, and DAC control registers.
- `ad5755_parse_fw()` converts device properties and child nodes into platform data.

## Control Flow
Probe allocates state, selects chip info, initializes IIO metadata and mutex, parses firmware or falls back to default current-output platform data, initializes per-channel IIO types, programs platform data into hardware, and registers the IIO device. Raw reads map IIO info to hardware registers, read values, adjust calibration offsets, and return scale/offset derived from the configured mode. Raw writes perform the inverse mapping and range validation. Power-up clears powerdown, enables internal and DC-DC circuitry, waits 200 microseconds, then enables output; powerdown clears those control bits.

## State And Persistence
The driver persists channel control shadow registers in `ctrl[]`, powerdown bits, channel types, and SPI buffers. Firmware-derived platform data is devm-allocated during probe and then reflected into the hardware and `ctrl[]`. Calibration and DAC data persist in hardware registers. Regulators are not used directly by this driver.

## Dependencies And Integration Points
The driver uses SPI, IIO direct mode/sysfs, firmware property APIs, scoped fwnode iteration, delays, and device match data. OF and SPI IDs map to chip info that controls bit width and voltage-output support.

## Risks And Edge Cases
- Firmware property name `adi,ext-dc-dc-compenstation-resistor` appears misspelled; bindings and users must match that spelling.
- `ad5755_set_channel_pwr_down()` ignores return values from `ad5755_update_dac_ctrl()` and always returns 0; hardware write failures during power sequencing can be hidden.
- `ad5755_parse_fw()` returns NULL on allocation failure and malformed child count, causing probe to silently use default platform data in some error cases.
- Child-node ordering, not `reg`, determines `dac[]` index; this can mismatch firmware intent if child order is unexpected.
- Current ranges use small integer milliamp scale while voltage ranges use millivolts; IIO unit consistency should be verified.

## Test Signals
Tests should cover firmware parsing tables, invalid mode rejection for current-only variants, DC-DC/slew register values, raw/calibration register mapping, scale/offset for every output mode, power sequence write ordering and error propagation, default platform fallback, and OF/SPI device matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5755.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5758.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5758.c

## Purpose
`ad5758.c` is an SPI IIO driver for the AD5758 single-channel industrial voltage/current output DAC. It configures output range, DC-DC mode/current limit, optional slew rate, calibration refresh, powerdown, and debugfs register access.

## Important APIs, Types, And Functions
- `struct ad5758_state` stores SPI device, mutex, optional reset GPIO, output range, DC-DC settings, slew time, powerdown state, and 32-bit transfer buffers.
- `ad5758_spi_reg_read()` and `ad5758_spi_reg_write()` implement 32-bit SPI register protocol and two-stage readback selection.
- `ad5758_spi_write_mask()` provides read-modify-write register updates.
- `ad5758_wait_for_task_complete()` polls busy/calibration bits with timeout.
- `ad5758_calib_mem_refresh()`, `ad5758_soft_reset()`, `ad5758_set_dc_dc_conv_mode()`, `ad5758_set_dc_dc_ilim()`, `ad5758_slew_rate_config()`, and `ad5758_init()` implement startup sequencing.
- `ad5758_parse_dt()` requires DT properties for DC-DC mode and voltage/current output range.
- `ad5758_read_raw()` and `ad5758_write_raw()` expose raw DAC input, scale, and offset.

## Control Flow
Probe allocates state, initializes mutex and IIO metadata, parses required device properties, chooses a voltage or current IIO channel table, runs hardware initialization, and registers the IIO device. Initialization disables CRC, resets hardware, disables CRC again, refreshes calibration memory, clears diagnostics, configures DC-DC current limit and mode, programs output range and optional slew, enables internal buffers, and enables output. Raw writes write `DAC_INPUT`; powerdown toggles output and internal buffer enable bits.

## State And Persistence
The driver persists parsed configuration in `out_range`, `dc_dc_mode`, `dc_dc_ilim`, `slew_time`, and `pwr_down`. Hardware retains calibration, range, and DAC input registers until reset. The mutex protects SPI read/write sequences and read-modify-write updates.

## Dependencies And Integration Points
It depends on SPI, GPIO descriptors, firmware properties, bsearch, IIO direct mode/sysfs, debugfs register access through IIO, and delay/polling helpers. OF compatible is `adi,ad5758`.

## Risks And Edge Cases
- The file explicitly lacks CRC support and disables CRC checks; noisy SPI links lose a hardware integrity feature.
- `ad5758_write_raw()` does not validate raw range before writing a 16-bit register.
- Several initialization steps rely on short polling windows; slow hardware or board-level delays can produce probe failures.
- `ad5758_parse_dt()` requires `adi,dc-dc-mode` and either voltage or current range; missing properties make probe fail.
- `ad5758_find_closest_match()` assumes sorted arrays and returns first value greater/equal; slew approximation should be validated for low/high requested slew times.

## Test Signals
Test DT parsing for all valid ranges and DC-DC modes, CRC disable/reset/calibration sequence, busy timeout behavior, slew index calculation, raw/scale/offset values for current and voltage channels, powerdown toggling, debugfs register access, and failure paths for each SPI operation in init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5758.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5761.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5761.c

## Purpose
`ad5761.c` is an SPI IIO driver for single-channel AD5721/AD5721R/AD5761/AD5761R voltage-output DACs. It supports 12- and 16-bit variants, internal or external reference, configurable output range via platform data, raw read/write, scale, and offset.

## Important APIs, Types, And Functions
- `struct ad5761_state` stores SPI device, mutex, reference selection/value, output range, and DMA-aligned transfer buffers.
- `_ad5761_spi_write()` and `_ad5761_spi_read()` implement 24-bit command frames and readback.
- `ad5761_spi_set_range()` performs full reset and writes the control register with range, ETS, and internal-reference bit.
- `ad5761_read_raw()` returns raw DAC code, scale derived from range multiplier, and offset derived from range constant.
- `ad5761_write_raw()` validates and writes raw DAC data.
- `ad5761_probe()` resolves reference voltage and range, initializes hardware, and registers the IIO device.

## Control Flow
Probe selects chip info by SPI ID, allocates IIO state, reads optional `vref`, falls back to internal reference only for R variants, validates external reference between 2 V and 3 V, reads optional platform-data voltage range, initializes the mutex, resets/configures range, then registers one IIO voltage output channel. Raw read performs a readback transaction from `DAC_READ`; raw write shifts and writes to `DAC_WRITE`.

## State And Persistence
The driver stores `use_intref`, `vref`, and current `range`. Hardware output and control registers persist until reset. The mutex protects shared SPI buffers.

## Dependencies And Integration Points
It integrates with SPI, IIO direct mode, regulator consumer helpers, and legacy `linux/platform_data/ad5761.h` for range selection. Matching is by SPI IDs.

## Risks And Edge Cases
- `_ad5761_spi_read()` assigns `*val` even if `spi_sync_transfer()` failed; callers ignore the value on error, but instrumentation may see stale data.
- Platform data range is not range-checked before indexing `ad5761_range_params`.
- There is no OF property parsing for range in this file; non-platform-data systems default to 0 V to 5 V.
- Raw write bound uses shifted value and can be vulnerable to integer overflow if future realbits change unexpectedly.

## Test Signals
Tests should cover internal-reference fallback, external-reference validation, all supported output ranges, raw read/write frame encoding, scale/offset calculations, invalid raw values, and probe failure when non-R parts lack `vref`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5761.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5764.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5764.c

## Purpose
`ad5764.c` is an SPI IIO driver for quad AD5744/AD5744R/AD5764/AD5764R voltage DACs. It supports 14- and 16-bit channels, internal-reference R variants, external AB/CD reference regulators for non-R variants, raw data, scale/offset, and calibration gain/bias.

## Important APIs, Types, And Functions
- `struct ad5764_state` stores SPI device, chip info, two reference regulators, mutex, and transfer buffers.
- `ad5764_write()` and `ad5764_read()` implement 24-bit register writes/readbacks.
- `ad5764_chan_info_to_reg()` maps IIO raw/calibration info to data, offset, and fine gain registers.
- `ad5764_write_raw()` validates raw/calibration bounds and writes hardware registers.
- `ad5764_read_raw()` reads raw/calibration registers and computes scale/offset.
- `ad5764_probe()` enables external references when needed, registers IIO, and `ad5764_remove()` unregisters and disables regulators.

## Control Flow
Probe selects chip info from SPI ID, configures four channel specs, initializes mutex, enables `vrefAB`/`vrefCD` regulators for non-internal-reference variants, registers the IIO device, and unwinds regulators on registration failure. Runtime raw/calibration accesses lock around SPI operations. Scale uses internal reference or reads the per-pair regulator voltage; offset is fixed to half-scale negative.

## State And Persistence
The driver persists chip info, regulator handles, and SPI buffers. Hardware stores raw DAC and calibration registers. No raw output cache exists. External regulator enables persist until remove or probe failure unwind.

## Dependencies And Integration Points
It depends on SPI, regulator bulk APIs, IIO direct mode, and manual `iio_device_register()`/`iio_device_unregister()` lifecycle rather than devm registration because remove must disable regulators.

## Risks And Edge Cases
- `ad5764_write_raw()` casts signed calibration values to `u16`; this likely matches two's-complement register encoding but should be checked against datasheet.
- Scale formula comment says `vout = 4 * vref + ((dac_code / 65536) - 0.5)`, but the arithmetic returns `4 * vref / 2^bits`; review comment and units for clarity.
- Regulator voltages are read dynamically on scale reads; regulator_get_voltage failures propagate to userspace.
- No reset or default clear sequence is performed at probe.

## Test Signals
Test regulator enable/disable lifecycle, scale for internal and external references, raw and calibration bounds, sign extension on calibration read, register addressing for all four channels, and probe/remove error unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5764.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5766.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5766.c

## Purpose
`ad5766.c` is an SPI IIO driver for AD5766 and AD5767 16-channel voltage-output DACs. It exposes direct raw access, scale/offset from a firmware-selected output span, per-channel dither controls, optional reset GPIO, and an IIO triggered output buffer path for synchronized multi-channel updates.

## Important APIs, Types, And Functions
- `struct ad5766_state` stores SPI device, mutex, chip info, reset GPIO, current range, dither state fields, and transfer buffers.
- `__ad5766_spi_read()` and `__ad5766_spi_write()` implement 3-byte command/data transfers.
- `ad5766_reset()` uses reset GPIO or software full reset.
- `ad5766_default_setup()` reads `output-range-microvolts`, resets, powers down dither, initializes dither source/scale/invert registers, and writes span.
- `ad5766_read_raw()` and `ad5766_write_raw()` expose raw, offset, and scale.
- Ext-info handlers expose `dither_enable`, `dither_invert`, `dither_source`, and `dither_scale`.
- `ad5766_trigger_handler()` writes buffer samples into input registers and issues software LDAC.

## Control Flow
Probe allocates the IIO device, initializes mutex and chip info, configures channels, gets optional reset GPIO, performs default hardware setup, installs a triggered output buffer, and registers the device. Direct writes write a DAC register immediately. Buffered writes pop a scan from the output buffer, write active channels to input registers under lock, then issue `SW_LDAC` with the active scan mask.

## State And Persistence
The driver caches dither enable/invert/source/scale values and current span. Hardware stores DAC, dither, and span registers. The mutex protects SPI transactions and shared buffers. Buffered output state is managed by the IIO buffer subsystem.

## Dependencies And Integration Points
It depends on SPI, GPIO descriptors, firmware properties, IIO triggered buffers, output buffer direction support, bitfield helpers, and unaligned big-endian helpers. OF and SPI IDs support `ad5766` and `ad5767`.

## Risks And Edge Cases
- `for_each_set_bit()` in the trigger handler uses `num_channels - 1` as the bit count, which omits the last channel from buffered writes. This is a likely off-by-one bug.
- `ad5766_write_ext()` parses `dither_source` with `kstrtobool()`, limiting source selection to boolean values even though the getter subtracts one and hardware has two sources; ABI semantics should be verified.
- `ad5766_get_output_range()` divides microvolts by 1,000,000, losing sub-volt precision and requiring exact integer volt endpoints.
- Direct dither state updates are not protected by a separate lock before calling locked writes; concurrent sysfs operations could race software shadow fields.

## Test Signals
Tests should cover output range property parsing, reset GPIO/software reset, dither register initialization and sysfs updates, raw bounds for 12/16-bit variants, scale/offset values for every span, triggered-buffer channel coverage including channel 15, and SPI failure handling during default setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5766.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5770r.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5770r.c

## Purpose
`ad5770r.c` is an SPI/regmap IIO driver for the AD5770R six-channel current-output DAC. It configures per-channel current ranges from firmware, reference source, output filter resistors, per-channel powerdown, raw output, scale, offset, and debugfs register access.

## Important APIs, Types, And Functions
- `struct ad5770r_state` stores SPI device, regmap, reset GPIO, per-channel output modes, vref, powerdown flags, reference selection, and transfer buffer.
- `ad5770r_set_output_mode()` writes per-channel output range registers.
- `ad5770r_set_reference()` selects internal/external 1.25 V or 2.5 V reference and external resistor bit.
- `ad5770r_channel_config()` requires six child nodes and reads each channel’s `adi,range-microamp`.
- `ad5770r_read_raw()` and `ad5770r_write_raw()` handle raw current codes, scale/offset, and low-pass 3 dB filter frequency.
- `ad5770r_set_filter_freq()` maps requested frequency to the nearest supported resistor code.
- Powerdown ext_info updates channel shutdown and enable registers.

## Control Flow
Probe initializes SPI regmap, reads optional `vref`, sets internal-reference fallback, prepares IIO metadata, and runs `ad5770r_init()`. Init resets hardware, parses all channel ranges, writes output modes, reads external-resistor property, configures reference, disables all outputs, and marks channels powered down. Runtime raw writes bulk-write two data bytes to the channel DAC register; powerdown toggles channel config and enable bits.

## State And Persistence
The driver persists per-channel output range selections and powerdown flags. Hardware stores DAC values, filters, ranges, and enable bits. Regmap provides the SPI register transport abstraction, but the driver still uses a small aligned buffer for bulk DAC writes.

## Dependencies And Integration Points
It depends on SPI, regmap, regulator helpers, GPIO descriptors, firmware child-node parsing, IIO direct mode/sysfs, debugfs register access, and OF compatible `adi,ad5770r`.

## Risks And Edge Cases
- `ad5770r_channel_config()` requires exactly six child nodes; partial DT descriptions are rejected.
- `ad5770r_write_raw()` does not validate raw range before splitting into two bytes.
- `ad5770r_set_filter_freq()` chooses the first supported frequency greater/equal to the requested value, which may surprise users expecting nearest by absolute difference.
- Powerdown write inverts the parsed boolean into shutdown-B semantics; this is correct-looking but easy to regress.
- If external `vref` is present but not exactly 1250 or 2500 mV, reference config falls back to internal reference selector while `internal_ref` remains false.

## Test Signals
Test six-child firmware parsing, every legal channel range, internal/external reference selection, filter frequency availability and rounding, powerdown register masks for channel 0 sink mode, raw byte order, debugfs reg access, and invalid vref/range behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5770r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5791.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5791.c

## Purpose
`ad5791.c` is an SPI IIO driver for precision single-channel AD5760/AD5780/AD5781/AD5790/AD5791 voltage-output DACs. It supports high-resolution raw access, bipolar scale/offset from positive/negative references, powerdown mode control, optional reset/clear/LDAC GPIOs, and optional SPI offload plus DMAengine output buffering.

## Important APIs, Types, And Functions
- `struct ad5791_state` stores SPI device, GPIOs, chip info, SPI offload objects, reference voltages, control register cache, powerdown state, and transfer buffers.
- `ad5791_spi_write()` and `ad5791_spi_read()` implement 24-bit command frames.
- `ad5791_get_lin_comp()` and `ad5780_get_lin_comp()` choose linearity compensation bits from voltage span.
- `ad5791_read_raw()` returns raw code, scale, offset, and offload sample frequency.
- `ad5791_write_raw()` writes raw code or sample frequency.
- `ad5791_offload_setup()` configures SPI offload trigger, TX DMAengine buffer, streaming transfer, and optimized SPI message.
- Buffer setup callbacks enable/disable the offload trigger.

## Control Flow
Probe obtains optional GPIOs, resolves reference voltages from regulators or platform data, resets hardware, selects chip info, builds the control register with linearity compensation and binary/two's-complement mode, writes powered-down control state, initializes IIO metadata, optionally gets/configures SPI offload and DMA buffer, then registers. Direct raw writes write the DAC register. If offload is available, the channel gains `SAMP_FREQ`, setup ops, and DMA-backed output buffer; preenable rejects streaming while powered down.

## State And Persistence
The driver caches control register bits, powerdown mode/state, vref span and negative reference, offload sample rate, and SPI offload resources. Hardware retains DAC and control registers. No mutex protects direct SPI buffer access, so serialization relies on IIO/SPI call context.

## Dependencies And Integration Points
It integrates with SPI, regulator consumers, GPIO descriptors, IIO, IIO DMAengine buffer namespace, SPI offload consumer APIs, platform data `linux/iio/dac/ad5791.h`, and OF/SPI match data for chip variants.

## Risks And Edge Cases
- `ad5791_write_raw()` masks raw values instead of rejecting out-of-range or negative inputs; invalid userspace values wrap into valid codes.
- Reference voltage can remain zero if neither regulators nor platform data provide values; scale/offset and linearity compensation then become suspect.
- Direct SPI access lacks an explicit mutex around shared `data[]`.
- Optional offload changes channel metadata; tests must cover both offload and non-offload ABI.
- The GPIO clear and LDAC descriptors are requested but not actively used after probe in this file.

## Test Signals
Test regulator and platform-data reference paths, reset GPIO/software reset, control register bits for spans and rbuf gain setting, raw write bounds/wrapping, scale/offset math, powerdown mode behavior, offload availability/error paths, sample frequency validation, buffer preenable rejection when powered down, and device match data for all variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5791.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad7293.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad7293.c

## Purpose
`ad7293.c` is an SPI IIO driver for the AD7293 mixed-signal device. It exposes four voltage ADC inputs, four current-sense ADC inputs, three temperature channels, and eight voltage DAC outputs, with offset/scale controls, ADC conversion sequencing, DAC enable/write support, page-aware register access, chip ID validation, and debugfs register access.

## Important APIs, Types, And Functions
- `struct ad7293_state` stores SPI device, page/data mutex, reset GPIO, VREFIN presence, current page, and transfer buffer.
- `ad7293_page_select()` caches and writes page selection before register accesses.
- `__ad7293_spi_read()`, `__ad7293_spi_write()`, and update-bit helpers implement variable one-/two-byte register protocol.
- `ad7293_adc_get_scale()`/`ad7293_adc_set_scale()` manage VIN range bits split across two registers.
- `ad7293_get_offset()`/`ad7293_set_offset()` map logical channel groups to page-E offset registers.
- `ad7293_ch_read_raw()` sequences ADC conversions and reads ADC/DAC raw data.
- `ad7293_dac_write_raw()` enables a DAC channel and writes its raw code.
- `ad7293_init()` enables regulators, resets, validates chip ID, and selects internal ADC reference if needed.

## Control Flow
Probe allocates state and static channel table, initializes mutex and page cache, runs hardware init, then registers IIO. Reads dispatch by channel type: voltage inputs program VIN sequence, current/temperature program shared sequence plus bias/reference enables and delays, DAC outputs read their VOUT register. Writes are limited to DAC raw outputs plus offset/scale controls where supported. All SPI accesses are serialized because page selection and data bytes share state.

## State And Persistence
The driver persists page-select cache, VREFIN presence, and GPIO/regulator resources. Hardware stores offsets, ranges, DAC enables, and raw DAC values. There is no DAC software cache; DAC raw reads query hardware.

## Dependencies And Integration Points
It depends on SPI, GPIO descriptors, regulator consumers (`avdd`, `vdrive`, optional `vrefin`), IIO direct mode, unaligned helpers, bitfield helpers, and OF/SPI matching. It uses IIO `read_avail` for offset/scale lists and debugfs register access for raw register operations.

## Risks And Edge Cases
- `ad7293_reg_access()` accepts encoded register constants with page and transfer length bits, not plain addresses; debugfs users must know the driver’s encoding.
- `ad7293_ch_read_raw()` always applies `AD7293_REG_DATA_RAW_MSK`; if a register layout differs from ADC/DAC data fields, raw extraction would be wrong.
- DAC raw writes do not validate the 12-bit raw range before field prep.
- Temperature/current conversion delays are fixed sleeps; slow boards may require different timing.
- `MODULE_AUTHOR` string is missing a closing `>`, a cosmetic metadata issue.

## Test Signals
Tests should cover page switching and cached page behavior, one- versus two-byte register transfers, chip ID rejection, regulator/reference paths, ADC sequence commands for each channel type, scale/offset get/set mappings, DAC enable plus raw write, read_avail lists, debugfs register access encoding, and concurrent access serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad7293.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad7303.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad7303.c

## Purpose
`ad7303.c` is an SPI IIO driver for the dual-channel 8-bit AD7303 voltage DAC. It supports raw writes/readback via software cache, scale from VDD or optional REF regulator, and per-channel powerdown.

## Important APIs, Types, And Functions
- `struct ad7303_state` stores SPI device, config shadow, two-entry DAC cache, VDD/REF regulators, mutex, and 16-bit transfer word.
- `ad7303_write()` formats update commands with channel, config bits, and raw value.
- `ad7303_read_raw()` returns cached raw value and scale.
- `ad7303_write_raw()` validates 8-bit raw values, writes hardware, and updates cache on success.
- Powerdown ext_info updates config bits and rewrites the selected DAC channel because there is no NOOP-only config update.
- `ad7303_probe()` enables required VDD and optional REF regulators using devm cleanup actions.

## Control Flow
Probe allocates state, enables VDD, optionally enables REF and sets external-reference config, initializes IIO metadata, and registers. Raw writes lock, issue a SPI write, and update cache. Raw reads lock only for cache reads. Powerdown writes lock, mutate config, and write the current cached DAC value for that channel to push config.

## State And Persistence
The driver persists config bits and cached raw values because the chip has no readback. Regulator enables are tied to devm cleanup. Hardware retains DAC/config until reset/power loss.

## Dependencies And Integration Points
It integrates with SPI, regulator consumers (`Vdd`, optional `REF`), IIO direct mode/sysfs, mutexes, OF compatible `adi,ad7303`, and SPI ID `ad7303`.

## Risks And Edge Cases
- `ad7303_write_dac_powerdown()` ignores the return value from `ad7303_write()` and always returns `len`, hiding SPI failures.
- Cache defaults to zero after probe and may not reflect hardware power-on state until first write.
- Regulator supply names are uppercase (`Vdd`, `REF`), so bindings must match exactly.

## Test Signals
Test regulator enable/cleanup, external versus VDD/2 reference scale, raw bounds and cache updates, powerdown config bit encoding, SPI failure behavior in powerdown, and no-readback cache semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad7303.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad8460.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad8460.c

## Purpose
`ad8460.c` is an SPI/regmap IIO driver for the AD8460 waveform-generator DAC. It exposes a 14-bit high-voltage voltage output, a quiescent-current control channel, optional temperature monitoring through an external IIO ADC channel, threshold fault events, 16 pattern/DAC words, APG toggle mode, powerdown control, sample frequency from a sync clock, and an output DMAengine buffer.

## Important APIs, Types, And Functions
- `struct ad8460_state` stores SPI device, regmap, optional temperature ADC IIO channel, sync clock, mutex, `refio_1p2v` value, external resistor value, and an aligned little-endian 16-bit data buffer.
- `ad8460_reset()` uses an optional reset GPIO or writes the software reset register; `ad8460_hv_reset()` toggles the high-voltage reset bit after shutdown faults.
- `ad8460_enable_apg_mode()` switches both APG enable and waveform-generator mode bits.
- `ad8460_get_hvdac_word()` and `ad8460_set_hvdac_word()` bulk-read/write the 16 high-voltage DAC data words.
- Ext-info handlers expose `raw0` through `raw15`, `toggle_en`, `symbol`, `powerdown`, and fixed `powerdown_mode`.
- `ad8460_read_raw()`/`ad8460_write_raw()` support voltage raw/scale/sample-frequency, current raw, and optional temperature raw.
- Event handlers map voltage/current/temp threshold events to overvoltage, overcurrent, and overtemperature fault registers.
- Buffer setup callbacks switch APG mode off before DMA output and restore APG mode after buffer disable.
- `ad8460_probe()` validates clocks, supplies, `refio_1p2v`, external resistor, optional fault ranges, optional temp channel, reset/default DAC enable, DMA buffer, and IIO registration.

## Control Flow
Probe allocates state, initializes regmap and mutex, enables the sync clock, optionally attaches the `ad8460-tmp` IIO channel, enables six named supplies, reads optional `refio_1p2v`, reads or defaults `adi,external-resistor-ohms`, programs optional current/voltage/temperature fault threshold registers from firmware, resets the device, clears HVDAC sleep to enable the DAC by default, sets direct mode and buffer setup ops, attaches a TX DMAengine output buffer, and registers the IIO device. Direct voltage writes claim direct mode, enable APG mode, write sample word 0, and set pattern depth to zero. Buffered output disables APG mode in preenable and re-enables it after disable. Powerdown writes HVDAC sleep, optionally clears a shutdown flag via HV reset, then updates HV sleep.

## State And Persistence
The driver persists reference/resistor scaling inputs and the shared transfer buffer. Most user-visible state lives in hardware registers: HVDAC words, APG/toggle mode, pattern depth, HVDAC/HV sleep bits, quiescent current, and fault thresholds. The mutex protects shared data-word bulk transfers and power/sample update sequences. DMA buffer state is managed by IIO DMAengine.

## Dependencies And Integration Points
The driver integrates with SPI regmap, clock framework, GPIO reset, bulk regulators (`avdd_3p3v`, `dvdd_3p3v`, `vcc_5v`, `hvcc`, `hvee`, `vref_5v`), optional `refio_1p2v`, optional IIO consumer channel `ad8460-tmp`, IIO event APIs, IIO DMAengine output buffering, and OF/SPI compatible `adi,ad8460`. It imports namespace `IIO_DMAENGINE_BUFFER`.

## Risks And Edge Cases
- `ad8460_dac_input_write()` and `ad8460_write_symbol()` return the raw register-write return value on success instead of `len`, so sysfs writes can report 0 bytes written.
- Raw voltage/current writes do not validate 14-bit DAC code or 8-bit quiescent-current range before field prep/register write.
- Probe programs optional fault thresholds with `regmap_write()` but does not check those return values, so threshold setup failures can be hidden.
- `ad8460_write_powerdown()` naming is subtle: clearing user powerdown can trigger HV reset if shutdown flag is set, then writes the inverse into `HV_SLEEP`.
- `ad8460_buffer_postdisable()` always re-enables APG mode, even if APG/toggle mode was disabled before buffer use.
- `MODULE_AUTHOR` is missing a closing `>`, a cosmetic metadata issue.

## Test Signals
Test supply and clock acquisition, optional temp-channel probe defer/fallback, reference/resistor boundary validation, reset GPIO/software reset, scale formula, raw0..raw15 little-endian word access, sysfs write return values, direct-mode claim failures, APG mode transitions during direct and buffered output, powerdown/HV reset sequencing, fault event value/enable mapping, DMA buffer setup failure, and unchecked firmware-threshold write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad8460.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad8801.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad8801.c

## Purpose
`ad8801.c` is a compact SPI IIO driver for AD8801 and AD8803 eight-channel 8-bit voltage DACs. It exposes write-only hardware through raw writes and software-cache raw reads, with scale/offset derived from high and optional low reference regulators.

## Important APIs, Types, And Functions
- `struct ad8801_state` stores SPI device, eight-channel DAC cache, high/low reference millivolts, and 16-bit transfer word.
- `ad8801_spi_write()` formats channel and 8-bit value.
- `ad8801_write_raw()` validates 0..255 values, writes SPI, and updates cache.
- `ad8801_read_raw()` returns cached raw values, scale as `vrefh - vrefl`, and offset as `vrefl`.
- `ad8801_probe()` enables `vrefh` and, for AD8803, `vrefl`, then registers the IIO device.

## Control Flow
Probe allocates state, resolves the SPI ID, enables required references, sets channel metadata, and registers. Runtime raw writes are one SPI frame per channel. Raw reads do not touch hardware and return the cache.

## State And Persistence
The driver persists cached DAC values and reference voltages. The hardware has no readback path here, so cache reflects only values written after driver probe. Reference regulators are devm-enabled and automatically disabled on detach.

## Dependencies And Integration Points
It depends on SPI, IIO direct mode, regulator helper APIs, and SPI ID matching for `ad8801` and `ad8803`.

## Risks And Edge Cases
- There is no mutex around the shared transfer buffer or DAC cache; concurrent sysfs writes could race.
- Cache starts at zero and may not match hardware after bootloader configuration or reset.
- AD8801 offset is zero because `vrefl_mv` defaults to zero; AD8803 requires `vrefl` regulator.

## Test Signals
Test regulator requirements by device ID, scale/offset calculations, raw bounds, SPI frame encoding, cache update only on successful write, and concurrent access if direct-mode serialization is not guaranteed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad8801.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad9739a.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad9739a.c

## Purpose
`ad9739a.c` is an SPI/regmap IIO driver for the high-speed AD9739A DAC with an IIO backend data interface. It configures device clocks, receiver/Mu controller lock, full-scale current, operating mode, backend sampling frequency, and buffer data source switching.

## Important APIs, Types, And Functions
- `struct ad9739a_state` stores the IIO backend, regmap, and sample rate from the input clock.
- `ad9739a_oper_mode_get()` and `ad9739a_oper_mode_set()` expose normal versus mixed-mode operation as an IIO enum.
- `ad9739a_read_raw()` reports `IIO_CHAN_INFO_SAMP_FREQ`.
- Buffer setup callbacks switch backend data source between external buffer data and internal continuous wave.
- `ad9739a_reg_accessible()` blocks reserved register access in regmap.
- `ad9739a_reset()` uses optional reset GPIO or register reset.
- `ad9739a_init()` writes recommended clock/Mu controller registers, polls Mu and receiver lock, and programs optional full-scale current.
- `ad9739a_probe()` validates clock range, checks chip ID, initializes hardware, obtains/enables backend, extends backend channel spec, and registers IIO.

## Control Flow
Probe gets and validates the DAC clock, initializes regmap, reads chip ID, resets hardware, runs lock/full-scale initialization, obtains the IIO backend, requests the backend buffer, extends the backend-provided alternate-voltage channel, sets backend sampling frequency, enables the backend, and registers two channels: an internal continuous-wave `IIO_ALTVOLTAGE` source and an external-data `IIO_VOLTAGE` output. Buffer preenable switches the backend source to external; postdisable returns it to internal continuous wave.

## State And Persistence
The driver persists sample rate and backend/regmap handles. Hardware state includes mode, full-scale current, receiver/Mu controller settings, and lock state. Backend state persists data source selection while buffers are enabled.

## Dependencies And Integration Points
It depends on SPI, regmap, clock framework, optional reset GPIO, firmware property `adi,full-scale-microamp`, IIO backend APIs, IIO buffer setup, and namespace `IIO_BACKEND`. OF/SPI matching supports `adi,ad9739a`.

## Risks And Edge Cases
- Chip ID mismatch only warns, so unsupported compatible devices may continue probing.
- Lock polling retries only three times with short timeouts; marginal boards can fail probe.
- Clock must be in 1.6 GHz to 2.5 GHz range; sample-rate units and backend expectations should stay aligned.
- Full-scale current conversion uses fixed integer math from the datasheet formula; boundary and rounding tests are important.
- Operating mode maps hardware value 2 to IIO enum value 1; adding modes requires careful ABI mapping.

## Test Signals
Test valid/invalid clock ranges, register accessibility, reset GPIO/register paths, chip ID warning path, Mu and receiver lock timeout handling, full-scale current boundaries and register values, operating-mode enum mapping, backend setup/order, buffer data-source switching, and sample frequency reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad9739a.c -->
