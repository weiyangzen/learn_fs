# sources/distributed-fs/ceph-client/drivers/hid/hid-mcp2221.c

## Purpose

`hid-mcp2221.c` drives the Microchip MCP2221A HID USB bridge and exposes it as a Linux I2C/SMBus adapter, optional four-line GPIO controller, and optional IIO voltage device for ADC/DAC functions. It serializes all HID command/response traffic because MCP2221 responses do not carry enough transaction identity to safely pipeline commands.

## Important APIs, Types, and Functions

- `struct mcp2221` is the central device state: HID device, I2C adapter, mutex, completion, init delayed work, RX/TX buffers, response status, I2C clock divisor, GPIO chip, GPIO index/direction/mode state, and optional IIO channel/ADC/DAC state.
- `mcp_send_report()` and `mcp_send_data_req_status()` are the synchronous HID command primitives.
- I2C path: `mcp_i2c_xfer()`, `mcp_i2c_write()`, `mcp_i2c_smbus_read()`, `mcp_chk_last_cmd_status[_free_bus]()`, `mcp_cancel_last_cmd()`, and `mcp_set_i2c_speed()`.
- SMBus path: `mcp_smbus_xfer()` and `mcp_smbus_write()` implement quick, byte, word, block, I2C-block, process-call, and block-process-call transactions.
- GPIO path, gated by gpiolib: `mcp_gpio_read_sram()`, `mcp2221_check_gpio_pinfunc()`, `mcp_gpio_get/set`, `mcp_gpio_direction_input/output`, and `mcp_gpio_get_direction()`.
- `mcp2221_raw_event()` decodes all supported input reports, translates MCP status bytes to Linux errors, copies received I2C data, updates GPIO/IIO state, and completes waiters.
- IIO path: `mcp_iio_channels()`, `mcp_init_work()`, `mcp2221_read_raw()`, and `mcp2221_write_raw()` expose ADC raw reads, DAC writes, and scale values.
- `mcp2221_probe()` registers HID, I2C, GPIO, and scheduled IIO setup; `mcp2221_remove()` cancels pending IIO work.

## Control Flow

Probe parses and opens HID, installs a managed HID unregister action, starts I/O, clamps the `i2c_clk_freq` module parameter to 50-400 kHz, sends an I2C speed command, then registers an `i2c_adapter`. If gpiolib is reachable, it creates a sleeping GPIO chip and optionally forces non-GPIO alternate pin functions into GPIO input mode when IIO is disabled or `gpio_mode_enforce` is set. If IIO is reachable and GPIO mode is not enforced, delayed work reads SRAM/flash configuration, discovers ADC/DAC channels from GP1-GP3 modes, and registers an IIO device.

I2C and SMBus transfers power the HID device to `PM_HINT_FULLON`, lock the single command mutex, build reports in `txbuf`, and wait on `wait_in_report`. Reads first command the chip to perform the slave read, then repeatedly send `MCP2221_I2C_GET_DATA` until `rxbuf_idx` reaches the requested length. Final bus status is queried and failures issue a cancel to free the bus. Raw events are the only place where response status and payloads are interpreted.

## State and Persistence Behavior

Driver state is per-device and volatile. `cur_i2c_clk_div` persists after probe. `rxbuf`, `rxbuf_idx`, and `rxbuf_size` describe the currently active read and must only be touched under the serialized transaction model. GPIO mode bytes come from SRAM settings and may be changed in chip SRAM by `mcp2221_check_gpio_pinfunc()`. IIO `adc_values`, `adc_scale`, `dac_value`, and `dac_scale` are cached from status/flash/SRAM reports; DAC writes update SRAM settings and the cached value after success.

## Dependencies and Integration Points

The file bridges HID core to I2C core (`i2c_algorithm`, `devm_i2c_add_adapter`), SMBus emulation flags, gpiolib, IIO, power management hints, completions, delayed work, and ACPI companion propagation. It uses `hid-ids.h` for Microchip IDs and `FIELD_GET`, `GENMASK`, and endian helpers for status parsing.

## Risks and Edge Cases

- Response matching depends on strict one-command-at-a-time locking; any future async path would need explicit correlation.
- `mcp_set_i2c_speed()` returns `0` even if setting speed fails after cancel, so probe may continue with an unexpected bus speed.
- GPIO callbacks return status from HID reports directly; `mcp_gpio_get()` returns the line value encoded in `mcp->status`, so negative errors and boolean values share one path.
- `mcp_init_work()` uses a static retry counter shared across all devices, which can make multi-device retry behavior surprising.
- Block SMBus reads depend on `data->block[0]` as a requested length before the read; callers must initialize it correctly.
- The GPIO-vs-IIO mode policy can rewrite SRAM pin modes and surprise users expecting existing alternate functions to remain active.

## Test Signals

Exercise I2C single-message read/write, two-message repeated-start reads, unsupported multi-message rejection, SMBus transaction variants, timeout/cancel behavior, and address NACK translation to `-ENXIO`. GPIO tests should cover alternate-function pins, direction reads, direction set plus value set, and `gpio_mode_enforce`. IIO tests should validate channel discovery, scale derivation from flash, ADC bounds, DAC range checks, delayed retry behavior, and removal while delayed work is pending.
