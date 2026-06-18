# sources/distributed-fs/ceph-client/drivers/spi/spi-dln2.c

## Purpose

`spi-dln2.c` is the SPI host driver for the Diolan DLN-2 USB/MFD adapter. It communicates with adapter firmware through `dln2_transfer()` commands, queries firmware capabilities, configures chip selects, speed, mode and frame size, splits transfers into firmware-sized chunks, and supports runtime/system PM by enabling or disabling the SPI module.

## Important APIs, Types, and Functions

`struct dln2_spi` stores the platform device, SPI host, DLN2 port, reusable command buffer, cached bits-per-word, speed, mode, and selected CS. Firmware command helpers include `dln2_spi_enable()`, `dln2_spi_cs_set()`, `dln2_spi_cs_enable_all()`, `dln2_spi_get_cs_num()`, `dln2_spi_get_speed_range()`, `dln2_spi_set_speed()`, `dln2_spi_set_mode()`, and `dln2_spi_set_bpw()`. Data helpers include endian conversion functions, `dln2_spi_write_one()`, `dln2_spi_read_one()`, `dln2_spi_read_write_one()`, and `dln2_spi_rdwr()`. SPI integration is through `dln2_spi_prepare_message()`, `dln2_spi_transfer_one()`, probe/remove, and PM callbacks.

## Control Flow

Probe allocates the host and a reusable buffer, reads platform port data, disables the firmware module, queries chip-select count, min/max speed, and supported frame sizes, enables all CS lines, sets controller callbacks, enables the module, enables runtime PM, and registers the controller.

Before a message, `prepare_message()` selects the target CS if it changed. Each transfer calls `dln2_spi_transfer_setup()`, which disables the module if bus parameters changed, applies speed/mode/bpw changes, updates caches, and re-enables the module. `dln2_spi_rdwr()` breaks transfer data into 256-byte operations, setting `LEAVE_SS_LOW` for intermediate chunks or continued SPI transfers, and dispatches write, read, or read-write firmware commands with little-endian word ordering.

## State and Persistence Behavior

The driver caches bus setup to avoid unnecessary firmware reconfiguration. Suspend resets cached CS/speed/bpw/mode because USB power may be cut and forces the next transfer to reconfigure the board. Runtime suspend disables the SPI module; runtime resume enables it. No file-backed persistence exists, but firmware module state and CS enables persist while the adapter is powered.

## Dependencies and Integration Points

The file depends on the DLN2 MFD command API, platform data, property headers, runtime PM, unaligned helpers, and the SPI core. It advertises CPOL/CPHA modes and firmware-reported bits-per-word and speed ranges.

## Risks and Edge Cases

`dln2_spi_transfer_setup()` returns immediately after a failed speed/mode/bpw set without re-enabling the module, leaving the adapter disabled until recovery. `dln2_spi_get_supported_frame_sizes()` requires a full fixed-size response rather than accepting `count` plus present entries, which may reject shorter firmware replies. The reusable buffer relies on SPI core serialization. Big-endian conversion paths must avoid unaligned 32-bit access, which is handled on RX but should be regression-tested. Runtime PM and transfer setup both enable/disable the module and can expose ordering bugs if a transfer races with suspend.

## Test Signals

Tests should cover firmware query protocol lengths, min/max speed reporting, frame-size masks, chip-select count and selection, parameter-change and no-change setup, failure during speed/mode/bpw update, transfers of 1, 256, 257, and multi-chunk lengths, TX-only/RX-only/read-write commands, big-endian word conversion, runtime suspend/resume, system suspend/resume cache reset, and remove disabling the module.
