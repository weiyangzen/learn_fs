# Grouped Research: subset-b-003884

This grouped report covers the DAC-related source files listed for `subset-b-003884`. Each file section is wrapped for the reconciliation splitter and preserves the original source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/adi-axi-dac.c -->
## sources/distributed-fs/ceph-client/drivers/iio/dac/adi-axi-dac.c

Purpose: Implements the Analog Devices AXI DAC FPGA IP as an IIO backend rather than as a direct DAC frontend. It exposes enable/disable, DMA buffer setup, data source selection, debugfs register access, DDS tone attributes, and a custom register bus path used by the `adi,axi-ad3552r` high-speed child integration.

Important APIs/types/functions: `struct axi_dac_state` stores the MMIO `regmap`, mutex, backend metadata, sampled DAC clock rate, and read-only config. `struct axi_dac_info` selects generic vs AD3552R behavior. Backend operations are split between `axi_dac_generic_ops` and `axi_ad3552r_ops`. Key functions include `axi_dac_enable()`, `axi_dac_disable()`, `axi_dac_request_buffer()`, `axi_dac_extend_chan()`, `axi_dac_data_source_set/get()`, `axi_dac_set_sample_rate()`, `axi_dac_bus_reg_read/write()`, and `axi_dac_create_platform_device()`.

Control flow: probe enables the AXI clock, optionally enables `dac_clk`, maps MMIO, resets the core, checks the IP major version, reads `AXI_DAC_CONFIG_REG`, forces `R1_MODE`, initializes the mutex, and registers an IIO backend. For the AD3552R compatible, child firmware nodes are validated and turned into platform devices with bus callbacks. Runtime backend calls then set reset bits, wait for DRP lock, allocate DMAengine output buffers, select internal tone/DMA/ramp sources, and manage the custom bus stream FSM.

State and persistence: State is volatile FPGA register state plus `st->dac_clk`, which is used to preserve DDS output frequency across sample-rate changes by reading the old tuning word and rewriting it for the new rate. No NVM is written. Mutex locking protects multi-register sequences and shared cached rate data.

Dependencies and integration points: Depends on `linux/adi-axi-common.h`, `regmap_mmio`, clocks, platform firmware properties, IIO backend APIs, and `iio_dmaengine_buffer_setup_ext()`. It imports `IIO_BACKEND` and `IIO_DMAENGINE_BUFFER` namespaces and integrates with `ad3552r-hs.h` through platform data bus callbacks.

Risks and test signals: Validate IP version mismatch handling, DRP-lock timeout, DDS-disabled paths, sample-rate retuning, custom bus busy timeout, child node `reg` validation, and DMA name fallback from `dma-names` to `tx`. Hardware tests should cover generic AXI DAC and AD3552R child operation, including debugfs register reads, stream enable/disable, DDR toggling, and ext-info frequency/phase/scale round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/adi-axi-dac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/cio-dac.c -->
## sources/distributed-fs/ceph-client/drivers/iio/dac/cio-dac.c

Purpose: ISA I/O-port IIO driver for Measurement Computing CIO-DAC16, CIO-DAC08, and PC104-DAC06 boards. It exposes 16 voltage-output DAC channels with 12-bit raw writes.

Important APIs/types/functions: `struct cio_dac_iio` holds the `regmap`. `cio_dac_read_raw()` and `cio_dac_write_raw()` implement `IIO_CHAN_INFO_RAW`. `cio_dac_probe()` claims the configured I/O port region, maps it, initializes an I/O-port regmap, and registers the IIO device. The module parameter `base[]` provides board addresses for `module_isa_driver()`.

Control flow: Each configured ISA base address becomes an ISA device instance. Probe requests 32 bytes, maps them, creates a 16-bit regmap with two-byte stride, and registers a direct-mode IIO device using fixed channels. Reads and writes compute `base + channel * 2` and go through regmap.

State and persistence: The driver has no software cache. All registers are marked precious because on some board jumper settings reading a DAC register can trigger the output transfer. Hardware output persists only while the board remains powered/configured.

Dependencies and integration points: Depends on the ISA bus helper, module hardware parameters, IIO core, and regmap configured for I/O ports. It integrates through sysfs raw DAC attributes and legacy ISA port resource reservation.

Risks and test signals: The main risks are incorrect `base` parameters, failed I/O-port reservation, and side effects from reads on XFER-jumper boards. Tests should validate 0..4095 bounds, one channel stride per output, probe failure on busy ports, and actual board behavior for read-triggered transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/cio-dac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/dpot-dac.c -->
## sources/distributed-fs/ceph-client/drivers/iio/dac/dpot-dac.c

Purpose: Creates a synthetic voltage-output DAC from an IIO digital potentiometer channel wired as a divider from a `vref` regulator. It maps voltage-DAC raw writes to the underlying resistance channel raw value.

Important APIs/types/functions: `struct dpot_dac` stores the `vref` regulator, consumed `dpot` IIO channel, and computed maximum resistance. `dpot_dac_read_raw()`, `dpot_dac_write_raw()`, and `dpot_dac_read_avail()` proxy and scale the backing channel. `dpot_dac_channel_max_ohms()` derives full-scale resistance from raw max and channel scale. Probe validates that the consumed channel type is `IIO_RESISTANCE`.

Control flow: Probe allocates one IIO voltage output channel, gets `vref`, gets an IIO channel named `dpot`, validates type, computes max ohms, enables the regulator, and registers the device. Raw reads/writes are direct IIO consumer calls. Scale is calculated from the dpot resistance scale and regulator voltage, preserving integer, fractional, and log2 fractional representations.

State and persistence: Only `max_ohms` is cached. The current output state lives in the upstream dpot provider. The regulator is explicitly enabled at probe and disabled on remove.

Dependencies and integration points: Depends on IIO consumer APIs, regulator APIs, platform device/OF compatible `dpot-dac`, and the upstream digital potentiometer driver. It is an integration shim for board designs rather than a physical DAC driver.

Risks and test signals: Scale arithmetic is the key risk because it combines regulator voltage and resistance units across IIO return formats. Test with dpot providers returning `IIO_VAL_INT`, `IIO_VAL_FRACTIONAL`, and `IIO_VAL_FRACTIONAL_LOG2`; validate raw available passthrough, regulator cleanup on registration failure, and rejection of non-resistance input channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/dpot-dac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ds4424.c -->
## sources/distributed-fs/ceph-client/drivers/iio/dac/ds4424.c

Purpose: I2C IIO current-output driver for Maxim DS4402/DS4404/DS4422/DS4424 sink/source current DACs. It supports two-channel and four-channel variants, optional per-channel full-scale resistor properties, signed raw current direction, scale reporting, and suspend output zeroing.

Important APIs/types/functions: `struct ds4424_chip_info` captures name, internal reference, scale denominator, result mask, and channel count. `struct ds4424_data` stores regmap, regulator, chip info, optional `maxim,rfs-ohms`, and scale availability. `ds4424_init_regmap()` chooses a two- or four-channel regmap and primes cache from hardware. `ds4424_read_raw()` decodes source/sink sign and optional scale. `ds4424_write_raw()` encodes sign in `DS4424_DAC_SOURCE`.

Control flow: Probe gets chip match data, enables `vcc`, delays 1 ms for bus readiness, sets channel count, creates regmap, reads current hardware values into cache, parses optional `maxim,rfs-ohms`, chooses channel table with or without scale, and registers. Suspend bypasses the cache to write zero to hardware outputs, then switches regmap cache-only and marks it dirty. Resume disables cache-only and syncs cached pre-suspend values back.

State and persistence: Regmap maple cache tracks DAC register state and is deliberately preserved across suspend while hardware outputs are temporarily zeroed. The chip's output registers are volatile across power events; the driver primes cache at probe to reflect bootloader state.

Dependencies and integration points: Uses I2C, regmap with access tables, regulator `vcc`, firmware property `maxim,rfs-ohms`, and IIO current-output ABI. OF compatibles map to chip-specific masks and channel counts.

Risks and test signals: Risks include sign encoding at zero, mismatched `maxim,rfs-ohms` length, cache bypass correctness during suspend, and restoration after resume. Tests should verify signed raw limits for 5-bit and 7-bit devices, scale denominator math, regulator failure cleanup, and regcache sync after PM transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ds4424.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/lpc18xx_dac.c -->
## sources/distributed-fs/ceph-client/drivers/iio/dac/lpc18xx_dac.c

Purpose: Platform IIO voltage-output driver for the NXP LPC18xx DAC. It exposes a single 10-bit DAC channel and explicitly notes that interrupts and DMA are unsupported.

Important APIs/types/functions: `struct lpc18xx_dac` stores `vref`, MMIO base, mutex, and clock. `lpc18xx_dac_read_raw()` reads `LPC18XX_DAC_CR` for raw and reports `vref / 2^10` scale. `lpc18xx_dac_write_raw()` validates 0..1023 and writes `LPC18XX_DAC_CR_BIAS` plus the shifted value, then enables `LPC18XX_DAC_CTRL_DMA_ENA`.

Control flow: Probe maps MMIO, gets clock and `vref`, enables regulator and clock, clears control and conversion registers, and registers one direct-mode IIO channel. Remove unregisters, clears control, disables clock, and disables regulator.

State and persistence: Output value is held in the DAC control register and read back directly; there is no software cache. Power and clock remain enabled while the device is registered.

Dependencies and integration points: Depends on platform resources, a clock, `vref` regulator, MMIO accessors, mutex for write sequences, and OF compatible `nxp,lpc1850-dac`.

Risks and test signals: Verify the raw bit shift/mask, the fixed BIAS behavior, and the unexpected-looking DMA enable bit after direct writes. Tests should cover probe cleanup after regulator or clock failures, raw bounds, scale with changing regulator voltage, and register clear on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/lpc18xx_dac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ltc1660.c -->
## sources/distributed-fs/ceph-client/drivers/iio/dac/ltc1660.c

Purpose: SPI IIO voltage DAC driver for Linear Technology LTC1660/LTC1665 octal DACs. It supports eight channels with 10-bit or 8-bit resolution depending on device ID.

Important APIs/types/functions: `struct ltc1660_priv` holds SPI, regmap, `vref` regulator, cached channel values, and vref mV. `ltc1660_read_raw()` returns cached raw values and regulator-derived scale. `ltc1660_write_raw()` bounds values by channel resolution, left-shifts to the 12-bit register format, writes via regmap, and updates the cache. PM hooks issue sleep/wake commands.

Control flow: Probe initializes a 4-bit-register/12-bit-value SPI regmap, gets and enables `vref`, stores the SPI device, selects channel specs by ID, and registers the IIO device. Remove unregisters and disables the regulator.

State and persistence: Because the device is write-oriented, raw reads come from a software cache that starts at zero and updates only after successful writes. Sleep/wake commands do not repopulate output values from hardware.

Dependencies and integration points: Uses SPI, regmap SPI formatting, regulator `vref`, IIO direct mode, and OF/SPI IDs for `lltc,ltc1660` and `lltc,ltc1665`.

Risks and test signals: Validate channel-number-as-register mapping, raw cache vs actual power-on state, regulator disable on errors, and suspend/resume sleep/wake behavior. Tests should check bounds for 8- and 10-bit variants and ensure scale uses live regulator voltage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ltc1660.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ltc2632.c -->
## sources/distributed-fs/ceph-client/drivers/iio/dac/ltc2632.c

Purpose: SPI IIO voltage driver for LTC2632/LTC2634/LTC2636/LTC2654 families, covering 2-, 4-, and 8-channel parts with 8-, 10-, 12-, and 16-bit variants and low/high reference options.

Important APIs/types/functions: `struct ltc2632_chip_info` supplies channel tables, channel count, and internal reference mV. `struct ltc2632_state` stores SPI, powerdown cache mask, and active vref. `ltc2632_spi_write()` builds the 24-bit command frame. `ltc2632_write_raw()` sends write-and-update commands. Ext-info `powerdown` uses `ltc2632_read_dac_powerdown()` and `ltc2632_write_dac_powerdown()`.

Control flow: Probe reads optional `vref`; if present it programs external reference and uses measured voltage, otherwise it programs internal reference and uses chip default. It chooses the channel table from SPI ID, sets direct mode, and registers. Raw writes validate resolution and send a 24-bit SPI command.

State and persistence: There is no raw readback or raw value cache. Powerdown state is cached in `powerdown_cache_mask`; however the write path always sends the `POWERDOWN_DAC_N` command regardless of whether the requested state is true or false, so the software cache is the only source for the sysfs value and deserves hardware validation.

Dependencies and integration points: Uses SPI, unaligned big-endian 24-bit packing, optional `vref` regulator, IIO ext-info, and a broad SPI/OF ID table.

Risks and test signals: The powerdown setter is the highest-risk behavior because clearing the cache still sends a powerdown command rather than an update/wake command. Tests should cover each resolution shift, external/internal reference selection, channel count vs channel table length, and physical powerdown recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ltc2632.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ltc2664.c -->
## sources/distributed-fs/ceph-client/drivers/iio/dac/ltc2664.c

Purpose: SPI IIO driver for LTC2664 voltage-output SoftSpan DACs and LTC2672 current-output SoftSpan DACs. It supports channel spans, toggle A/B input registers, powerdown ext-info, current or voltage scale/offset reporting, and debugfs write-only register access.

Important APIs/types/functions: `struct ltc2664_chip_info` abstracts voltage/current differences, scale/offset callbacks, channel count, span tables, internal vref, manual span support, and RFSADJ support. `struct ltc2664_state` stores regmap, per-channel cached raw A/B values, span, toggle/powerdown state, vref, rfsadj, and global toggle. `ltc2664_dac_code_write()`, `ltc2664_reg_bool_set()`, `ltc2664_channel_config()`, and `ltc2664_setup()` are central.

Control flow: Probe gets chip data, initializes regmap, enables `vcc`, `iovcc`, and `v-neg`, reads optional `ref`, builds mutable channel specs, parses global `adi,manual-span-operation-config` and `adi,rfsadj-ohms`, parses child channel `reg`, toggle mode, voltage/current output ranges, writes span registers, disables internal reference when external reference is configured, and registers the IIO device.

State and persistence: The device lacks readback for normal raw paths, so A/B raw values, powerdown, toggle select, global toggle, span, and scale behavior are driver caches or one-time configuration mirrors. There is no nonvolatile persistence in the driver.

Dependencies and integration points: Uses SPI regmap, regulators, optional reset GPIO, firmware child nodes, Analog Devices `adi,*` properties, and IIO voltage/current channel ABI.

Risks and test signals: Verify span lookup for voltage and current properties, RFSADJ range enforcement, manual-span support only on LTC2664, toggle-mode ABI changes that clear normal raw, cache consistency after failed writes, and lack of debugfs read support. Tests should include both device types and child-node configurations with invalid spans and invalid channel numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ltc2664.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ltc2688.c -->
## sources/distributed-fs/ceph-client/drivers/iio/dac/ltc2688.c

Purpose: SPI IIO driver for the LTC2688 16-channel 16-bit voltage-output SoftSpan DAC. It supports per-channel span, overrange, calibration bias/scale, A/B input registers, toggle mode, dither mode, optional TGP clocks, powerdown, and debugfs register access.

Important APIs/types/functions: `struct ltc2688_chan` caches dither frequencies, overrange, toggle capability, and current mode. `struct ltc2688_state` stores SPI, custom regmap bus, per-channel config, mutable channel specs, mutex, vref, and DMA-aligned transfer buffers. Important functions include `ltc2688_spi_read/write()`, `ltc2688_dac_code_read/write()`, `ltc2688_channel_config()`, `ltc2688_tgp_clk_setup()`, and the dither/toggle ext-info handlers.

Control flow: Probe initializes a custom SPI regmap with read flag and no-op second transfer, enables `vcc` and `iovcc`, optionally reads external `vref`, resets via `clr` GPIO or config reset bit, duplicates the default channel table, parses child nodes for `reg`, `adi,toggle-mode`, `adi,output-range-microvolt`, `adi,toggle-dither-input`, and `adi,overrange`, writes channel settings, sets external-reference mode when needed, and registers 16 channels.

State and persistence: Device registers hold raw/calibration/span data. The driver caches mode and dither frequency availability because dither frequencies derive from child clocks. A mutex protects A/B select plus read/write sequences. No NVM is written.

Dependencies and integration points: Uses SPI, regmap custom bus callbacks, regulators, optional GPIO reset, optional child clocks, firmware child properties, and IIO ext-info/enums. It has richer per-channel sysfs ABI for dither and toggle channels depending on firmware.

Risks and test signals: Key risks are A/B select races, ext-info shape changes based on firmware, dither frequency generation from TGP clocks, raw B value masking for dither amplitude, and scale behavior when no external vref is supplied. Tests should cover invalid child `reg`, invalid output range, overrange scale, dither phase/frequency, toggle with and without TGP clock, and debugfs register reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ltc2688.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/m62332.c -->
## sources/distributed-fs/ceph-client/drivers/iio/dac/m62332.c

Purpose: I2C IIO voltage driver for the Mitsubishi M62332 two-channel 8-bit DAC, including simple power-saving regulator behavior and legacy IIO map registration.

Important APIs/types/functions: `struct m62332_data` stores I2C client, `VCC` regulator, mutex, raw cache, and suspend save cache. `m62332_set_value()` writes two-byte channel/value frames and manages regulator enable/disable around nonzero outputs. `m62332_read_raw()` exposes raw cache, scale, and offset. PM hooks save, zero, and restore both channels.

Control flow: Probe allocates the IIO device, initializes the mutex, gets `VCC`, registers optional platform IIO maps, then registers two output channels. Writes skip hardware if the value is unchanged; nonzero writes enable VCC, zero writes disable it after successful transfer. Remove unregisters, unregisters maps, and writes zero to both channels.

State and persistence: Raw values are software-cached because there is no readback. Suspend stores `raw[]` in `save[]`, writes zeros, and resume restores. Regulator state follows whether outputs are nonzero.

Dependencies and integration points: Uses I2C, regulator `VCC`, IIO map array support, IIO direct mode, and PM sleep hooks.

Risks and test signals: The regulator handling can become unbalanced if one channel remains nonzero and another channel is written to zero, because disabling is per write rather than a global nonzero-count policy. Tests should check two-channel interactions, unchanged-value behavior, suspend/resume restore, raw bounds, and map cleanup on register failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/m62332.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/max22007.c -->
## sources/distributed-fs/ceph-client/drivers/iio/dac/max22007.c

Purpose: SPI IIO driver for the Analog Devices MAX22007 four-channel DAC/addac output block. It supports voltage and current output channel functions, CRC-protected SPI/regmap transfers, per-channel powerdown ext-info, reset handling, and transparent DAC updates.

Important APIs/types/functions: `struct max22007_state` stores SPI, regmap, dynamic channel specs, and DMA-aligned transfer buffers. `max22007_spi_read()` validates CRC on reads; `max22007_spi_write()` appends CRC. `max22007_parse_channel_cfg()` builds channels from firmware child nodes and programs mode/latch bits. `max22007_read_raw/write_raw()` access 12-bit DAC data fields.

Control flow: Probe populates the CRC table, initializes a custom regmap bus, enables `vdd`, `hvdd`, and `hvss`, performs reset through optional reset GPIO or soft reset register, enables device CRC, parses child nodes requiring `reg` and `adi,ch-func`, programs channel mode and transparent latch mode, then registers the IIO device.

State and persistence: Channel configuration is programmed at probe from firmware. Raw values are read from device registers. There is no software raw cache or NVM persistence. CRC state is enabled in the chip after reset and expected by subsequent accesses.

Dependencies and integration points: Depends on SPI, Linux CRC8 helper, regmap custom bus, regulator bulk APIs, optional reset GPIO, dt binding constants from `adi,ad74413r.h`, and IIO voltage/current output ABI.

Risks and test signals: Validate the SPI CRC framing, read CRC calculation for varying `val_size`, `reg_shift = -1` addressing, channel function conversion to mode bits, and powerdown polarity. Hardware tests should include CRC mismatch injection, invalid child functions, all supplies missing/failing, reset GPIO vs soft reset, and voltage/current scale paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/max22007.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/max517.c -->
## sources/distributed-fs/ceph-client/drivers/iio/dac/max517.c

Purpose: Legacy I2C IIO voltage driver for Maxim MAX517/518/519/520/521 8-bit DACs with 1, 2, 4, or 8 channels.

Important APIs/types/functions: `struct max517_data` stores I2C client and per-channel reference mV. `max517_set_value()` sends command/value bytes. `max517_read_raw()` reports scale only; `max517_write_raw()` writes raw. PM hooks send powerdown and wake commands.

Control flow: Probe chooses channel count from I2C device ID, fills per-channel vref from platform data except MAX518 or missing platform data defaults to 5000 mV, and registers direct-mode IIO channels. Raw write sends the channel command byte and value.

State and persistence: The driver does not cache raw output values and does not read them back. Vref values are static platform/default state. Suspend powers the device down with `COMMAND_PD`; resume sends command zero.

Dependencies and integration points: Depends on I2C, optional `struct max517_platform_data` from `linux/iio/dac/max517.h`, and sleep PM hooks. It has no OF match table in this file.

Risks and test signals: Test per-device channel count, platform-data vref indexing, raw value bounds, partial I2C transfer handling, and powerdown/resume command effects. Lack of raw readback is expected and should be reflected in ABI expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/max517.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/max5522.c -->
## sources/distributed-fs/ceph-client/drivers/iio/dac/max5522.c

Purpose: SPI IIO voltage driver for the Maxim MAX5522 dual 10-bit ultra-low-power DAC.

Important APIs/types/functions: `struct max5522_state` stores regmap, chip info, two-channel DAC cache, and vref mV. `max5522_read_raw()` returns cached raw or scale. `max5522_write_raw()` validates 0..1023, writes the shifted value to the channel data register, and updates the cache. `max5522_spi_probe()` gets `vrefin` and initializes SPI regmap.

Control flow: Probe matches chip data, enables and reads `vrefin`, initializes a 4-bit-register/12-bit-value regmap, and registers two direct-mode output channels. Writes use control addresses `MAX5522_REG_DATA(channel)` to load inputs A/B.

State and persistence: Raw values are software-cached and start at zero. Hardware state is not read at probe. No PM hooks or NVM writes are present.

Dependencies and integration points: Uses SPI regmap, regulator `vrefin`, OF/SPI IDs for `maxim,max5522`, and IIO direct output channels.

Risks and test signals: Tests should validate cache consistency after failed writes, scaling from microvolts to millivolts, 10-bit bounds, channel register mapping, and behavior after device reset where cache may not match hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/max5522.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/max5821.c -->
## sources/distributed-fs/ceph-client/drivers/iio/dac/max5821.c

Purpose: I2C IIO voltage driver for the Maxim MAX5821 dual 10-bit DAC, including per-channel powerdown mode sysfs controls and raw readback.

Important APIs/types/functions: `struct max5821_data` holds I2C client, vref mV, per-channel powerdown state/mode, and a mutex. `max5821_get_value()` performs command then read under lock. `max5821_set_value()` sends the channel-specific load command. `max5821_sync_powerdown_mode()` writes extended command mode for selected channel. PM hooks globally power down/up both DACs.

Control flow: Probe initializes both channels as powered down with 100 kohm-to-ground mode, enables and reads `vref`, and registers two output channels. Raw reads send `READ_DAC_A/B` commands and decode the 10-bit result. Raw writes use channel-specific load commands.

State and persistence: Powerdown state/mode is software-cached and synchronized when sysfs powerdown is written. Raw values are read from hardware. Suspend/resume writes global extended commands but does not update the per-channel software powerdown flags.

Dependencies and integration points: Uses I2C, regulator `vref`, IIO ext-info/enums, mutex serialization for read command/read response, and OF compatible `maxim,max5821`.

Risks and test signals: Verify consistency between PM hooks and cached powerdown flags, partial I2C transfer handling, 10-bit decode, lock coverage for read sequences, and initial assumption that the chip starts powered down in 100 kohm mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/max5821.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/mcp4725.c -->
## sources/distributed-fs/ceph-client/drivers/iio/dac/mcp4725.c

Purpose: I2C IIO voltage driver for Microchip MCP4725/MCP4726 single-channel 12-bit DACs. It supports powerdown modes, optional external reference on MCP4726, EEPROM persistence through `store_eeprom`, and boot-state readback.

Important APIs/types/functions: `struct mcp4725_chip_info` distinguishes channel spec, readback length, and external reference support. `struct mcp4725_data` stores client, reference mode, buffering, DAC value, powerdown state/mode, and regulators. `mcp4725_store_eeprom()`, `mcp4725_set_value()`, `mcp4726_set_cfg()`, `mcp4725_read_raw()`, and PM hooks are central.

Control flow: Probe parses platform/firmware reference settings, rejects unsupported MCP4725 external reference and invalid buffering, enables `vdd` and optional `vref`, reads current DAC/config bytes, initializes cached powerdown/value/reference, rewrites MCP4726 config if EEPROM reference differs from desired runtime reference, and registers. Raw writes update volatile DAC output. EEPROM store sends the EEPROM write command and polls readiness.

State and persistence: `dac_value`, powerdown, and reference mode are cached in software after initial hardware read. `store_eeprom` persists current cached value/config to device EEPROM. Suspend powers down using selected mode; resume restores cached DAC value.

Dependencies and integration points: Uses I2C, regulators `vdd` and optional `vref`, platform data or firmware properties, IIO ext-info/enums, and sleep PM.

Risks and test signals: Validate EEPROM polling timeout, MCP4725 vs MCP4726 reference constraints, powerdown mode defaults from readback, resume restoring cached not hardware-read value, and regulator cleanup. Tests should cover boot EEPROM mismatches, external reference buffered/unbuffered modes, raw bounds, and store_eeprom false/true writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/mcp4725.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/mcp4728.c -->
## sources/distributed-fs/ceph-client/drivers/iio/dac/mcp4728.c

Purpose: I2C IIO voltage driver for the Microchip MCP4728 quad 12-bit DAC. It supports per-channel raw, selectable scale via VDD/internal reference/gain, global powerdown state with per-channel modes, EEPROM store, and boot configuration readback.

Important APIs/types/functions: `struct mcp4728_channel_data` stores vref mode, powerdown mode, gain, and raw value. `struct mcp4728_data` stores client, global powerdown, available scales, and channel cache. Important functions are `mcp4728_init_channels_data()`, `mcp4728_program_channel_cfg()`, `mcp4728_set_scale()`, `mcp4728_store_eeprom()`, and suspend/resume.

Control flow: Probe enables/reads `vdd`, reads the 24-byte device response to initialize all channel caches, computes available scales, and registers four channels. Raw writes update cache then send a multiwrite command for that channel. Scale writes find an exact listed scale and update vref/gain fields before programming. EEPROM store writes all channel cached settings and polls RDY.

State and persistence: Channel configuration is cached from device readback at probe and is the source for raw/scale reads. `store_eeprom` persists cached configuration to internal EEPROM. Suspend/resume toggle the global `powerdown` cache and reprogram every channel.

Dependencies and integration points: Uses I2C direct transfers, regulator `vdd`, IIO ext-info/enums and read_avail, and sleep PM. OF compatible is `microchip,mcp4728`.

Risks and test signals: Risks include global powerdown flag shared by all channels, exact scale matching, EEPROM response polling, and boot readback field decoding. Tests should validate read response length, all scale choices, per-channel powerdown mode encoding, raw bounds, suspend/resume partial failure behavior, and EEPROM writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/mcp4728.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/mcp47feb02.c -->
## sources/distributed-fs/ceph-client/drivers/iio/dac/mcp47feb02.c

Purpose: I2C regmap IIO driver for the Microchip MCP47FEBxx and MCP47FVBxx multi-channel DAC families. It covers 1/2/4/8-channel devices, 8/10/12-bit resolutions, EEPROM and non-EEPROM variants, VDD/internal/external VREF selections, per-channel labels, scale lists, powerdown modes, and PM restore.

Important APIs/types/functions: `struct mcp47feb02_features` describes device family/resolution/channel count/vref1/eeprom. `struct mcp47feb02_data` stores channel data, locks, scale tables, active channel mask, labels, regmap, and reference-buffer flags. Important functions include `mcp47feb02_parse_fw()`, `mcp47feb02_init_ctrl_regs()`, `mcp47feb02_init_scales_avail()`, `mcp47feb02_set_scale()`, `mcp47feb02_write_to_eeprom()`, `store_eeprom_store()`, and suspend/resume.

Control flow: Probe selects EEPROM-capable or volatile-only regmap config, parses child nodes as the active channel set with required labels, initializes a mutex, enables `vdd` and optional `vref`/`vref1`, reads control registers to populate channel reference/gain/powerdown cache, builds scale lists from supplies or internal bandgap, and registers. Raw and scale writes update hardware and cache under lock. EEPROM devices expose `store_eeprom`; FVB devices omit it.

State and persistence: Volatile channel state is mirrored in `chdata`. EEPROM-capable devices can persist DAC, VREF, powerdown, gain, and I2C address bits after wiperlock checks and EEWA polling. Suspend writes selected powerdown modes and cached DAC data; resume rewrites DAC data, VREF/gain, and normal operation.

Dependencies and integration points: Uses I2C regmap with access tables/cache, regulators, firmware child nodes/properties, IIO labels/ext-info, and PM sleep ops. It integrates many compatible IDs through shared feature tables.

Risks and test signals: High-risk areas include firmware requiring labels and active child nodes, odd-channel use of VREF1 on 4/8-channel devices, reference mismatch handling that logs but does not rewrite until scale write, EEPROM lock/EEWA polling, and resume register sequencing. Tests should cover EEPROM vs FVB configs, all resolutions, sparse active channels, scale availability for VREF/VREF1 absent/present, powerdown mode encoding, and store_eeprom failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/mcp47feb02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/mcp4821.c -->
## sources/distributed-fs/ceph-client/drivers/iio/dac/mcp4821.c

Purpose: SPI IIO voltage driver for Microchip MCP4801/4802/4811/4812/4821/4822 DACs using the internal 4.096 V 2x-gain reference.

Important APIs/types/functions: `struct mcp4821_chip_info` maps name, channel count, and channel specs for 8/10/12-bit single or dual devices. `struct mcp4821_state` stores SPI and raw cache. `mcp4821_write_raw()` builds a 16-bit command with active bit, optional second-channel bit, and shifted raw value. `mcp4821_read_raw()` returns cached raw and fixed scale.

Control flow: Probe gets match data, assigns fixed channel specs, and registers direct-mode IIO. Raw writes validate bounds and send a big-endian 16-bit SPI frame, then update the cache.

State and persistence: Raw values are cached in software and start at zero; the hardware is not read back. The driver has no regulator control and no PM hooks. TODO comments note configurable gain and regulator control as missing.

Dependencies and integration points: Uses SPI, OF/SPI ID tables, unaligned/big-endian helpers, and IIO direct output ABI.

Risks and test signals: Validate command bit packing, channel 1 selection, cache consistency, fixed scale for all resolutions, and lack of regulator handling on boards where power sequencing matters. Tests should cover every compatible variant and raw bounds per resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/mcp4821.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/mcp4922.c -->
## sources/distributed-fs/ceph-client/drivers/iio/dac/mcp4922.c

Purpose: SPI IIO voltage driver for Microchip MCP4902, MCP4912, MCP4921, and MCP4922 DACs with external `vref`.

Important APIs/types/functions: `struct mcp4922_state` stores SPI, cached channel values, vref mV, and DMA-aligned two-byte MOSI buffer. `mcp4922_spi_write()` builds the command/address/config bytes. `mcp4922_read_raw()` returns cache and scale. `mcp4922_write_raw()` validates by resolution, shifts to 12-bit format, writes SPI, and updates cache.

Control flow: Probe enables and reads `vref`, selects channel specs by SPI ID, sets one channel for MCP4921 and two for the others, then registers direct-mode IIO. Raw writes are two-byte SPI transfers with output active and gain/buffer config bits hardcoded in the command.

State and persistence: Raw values are software-cached. Note that `write_raw()` caches the shifted register value rather than the original user raw value, so subsequent raw reads may report shifted data for sub-12-bit devices.

Dependencies and integration points: Uses SPI, regulator `vref`, IIO direct mode, and SPI IDs. This file has no OF match table.

Risks and test signals: The shifted-value cache is a notable ABI risk for 8- and 10-bit variants. Tests should verify raw read-after-write for all variants, vref failure handling, single-channel MCP4921 selection, and command bytes on the wire.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/mcp4922.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/rohm-bd79703.c -->
## sources/distributed-fs/ceph-client/drivers/iio/dac/rohm-bd79703.c

Purpose: SPI IIO voltage driver for ROHM BD79700/BD79701/BD79702/BD79703 DAC variants. It abstracts 12-bit command transfers as 8-bit regmap addresses plus 8-bit DAC values.

Important APIs/types/functions: `struct bd7970x_chip_data` supplies name, channel table, count, and whether a separate VFS supply exists. `struct bd79703_data` stores regmap and full-scale voltage. `bd79703_write_raw()` writes the 8-bit value to the channel address; `bd79703_read_raw()` reports scale only.

Control flow: Probe gets chip data, initializes an SPI regmap with 8-bit registers and values, enables `vcc` and optionally reads/enables `vfs`, assigns channel table, writes zero to all outputs, and registers. BD79702 uses non-linear channel addresses for physical channels 0,1,4,5.

State and persistence: No raw cache and no readback are exposed. Regmap has a maple cache, but raw reads do not use it. Outputs are initialized to zero on probe.

Dependencies and integration points: Uses SPI regmap, regulators `vcc` and optional `vfs`, OF/SPI IDs, and IIO scale/raw ABI.

Risks and test signals: Check the 12-bit command abstraction with actual SPI controller word size, BD79702 address mapping, separate VFS vs VCC scale calculation, and all-output zero register behavior. Tests should verify raw bounds, scale for each variant, and probe failure cleanup when VFS is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/rohm-bd79703.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/stm32-dac-core.c -->
## sources/distributed-fs/ceph-client/drivers/iio/dac/stm32-dac-core.c

Purpose: Parent platform driver for STM32 DAC blocks. It owns shared MMIO regmap, peripheral clock, vref regulator, reset, runtime PM, H7 high-frequency selection, and child device population.

Important APIs/types/functions: `struct stm32_dac_priv` wraps `pclk`, `vref`, and shared `struct stm32_dac_common`. `struct stm32_dac_cfg` marks H7 HFSEL support. `stm32_dac_core_hw_start/stop()` enable/disable regulator and clock. `stm32_dac_probe()` initializes resources and populates children. PM callbacks handle runtime and system suspend/resume.

Control flow: Probe allocates common state, maps MMIO, creates an MMIO regmap clocked by `pclk`, gets clock and vref, enables runtime PM, starts hardware, reads vref mV into common state, optionally toggles reset, sets H7 HFSEL if pclk exceeds 80 MHz, populates child OF nodes, and autosuspends. Remove depopulates children and stops hardware.

State and persistence: Shared `regmap`, `vref_mv`, and `hfsel` persist in `stm32_dac_common` for child channel drivers. Runtime PM may shut down clock/regulator; system resume restores HFSEL if it may have been lost.

Dependencies and integration points: Uses platform resources, `devm_regmap_init_mmio_clk`, regulator, clock, reset controller, OF child population, runtime PM, and the local `stm32-dac-core.h` contract consumed by `stm32-dac.c`.

Risks and test signals: Validate PM reference balancing, child populate/depopulate ordering, HFSEL restore after low-power states, reset handling, and vref capture before children use scale. Tests should cover F4 and H7 compatibles, pclk below/above 80 MHz, runtime suspend/resume, and child probe with parent autosuspended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/stm32-dac-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/stm32-dac-core.h -->
## sources/distributed-fs/ceph-client/drivers/iio/dac/stm32-dac-core.h

Purpose: Shared header for the STM32 DAC parent and child drivers. It defines common register offsets, enable/HFSEL bits, and the shared data structure passed from the core to channel instances.

Important APIs/types/functions: Defines `STM32_DAC_CR`, `STM32_DAC_DHR12R1`, `STM32_DAC_DHR12R2`, `STM32_DAC_DOR1`, `STM32_DAC_DOR2`, `STM32_DAC_CR_EN1`, `STM32H7_DAC_CR_HFSEL`, and `STM32_DAC_CR_EN2`. `struct stm32_dac_common` contains shared `regmap`, `vref_mv`, and `hfsel`.

Control flow: No executable control flow. It is included by `stm32-dac-core.c` to fill common data and by `stm32-dac.c` to access registers and parent-provided scale/HFSEL state.

State and persistence: The header defines the shape of the parent-owned common state. Lifetime is managed by the platform parent; child drivers hold a pointer obtained from parent drvdata.

Dependencies and integration points: Depends only on `linux/regmap.h`. It is the coupling point between the MFD-like STM32 DAC core and per-channel IIO devices.

Risks and test signals: Register offsets and bit definitions are ABI-critical for all STM32 DAC children. Tests are indirect: raw reads/writes must hit the right DHR/DOR registers, powerdown must manipulate EN1/EN2, and H7 HFSEL restore must use the correct bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/stm32-dac-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/stm32-dac.c -->
## sources/distributed-fs/ceph-client/drivers/iio/dac/stm32-dac.c

Purpose: Child platform IIO driver for individual STM32 DAC channels. It exposes one IIO voltage-output device per child node, with raw/scale, debugfs register access, and powerdown controls backed by the parent core regmap and runtime PM.

Important APIs/types/functions: `struct stm32_dac` stores parent `stm32_dac_common` and a lock. `stm32_dac_is_enabled()` reads EN1/EN2. `stm32_dac_set_enable_state()` coordinates enable bits with runtime PM and HFSEL delay. `stm32_dac_get_value/set_value()` use DOR/DHR registers. `stm32_dac_chan_of_init()` maps child `reg` values 1 or 2 to a single channel spec.

Control flow: Probe requires an OF node, gets parent common data, initializes one IIO device for the child channel, enables runtime PM with autosuspend, registers, and autosuspends. Powerdown sysfs enables/disables the channel while taking/putting runtime PM references. System suspend refuses to proceed if the channel is still enabled, returning `-EBUSY`.

State and persistence: Output value is held in hardware registers. The child stores no raw cache. Parent runtime PM may disable the clock/regulator when all users autosuspend. The lock protects enable-state checks and writes against PM races.

Dependencies and integration points: Uses the parent `stm32-dac-core.h` common state, regmap, runtime PM, OF child `reg`, IIO ext-info/enums, and debugfs register access. It relies on `of_platform_populate()` from the core driver to instantiate it.

Risks and test signals: Validate channel `reg` parsing, enable/disable PM balancing, suspend rejecting enabled DACs, HFSEL post-enable delay, and raw writes while powered down. Tests should cover both channels as separate IIO devices, debugfs access, scale from parent vref, autosuspend timing, and error rollback if IIO registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/stm32-dac.c -->
