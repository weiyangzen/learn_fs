# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9806e-core.c

## Purpose

This file provides the shared core for Ilitek ILI9806E panel transports. It owns common panel allocation, supplies, reset GPIO, backlight binding, power sequencing, and exported helper APIs used by DSI and SPI transport drivers.

## Important APIs, Types, And Functions

`struct ili9806e` contains a transport pointer, DRM panel, supply count and array, and reset GPIO. Exported symbols are `ili9806e_get_transport()`, `ili9806e_power_on()`, `ili9806e_power_off()`, `ili9806e_probe()`, and `ili9806e_remove()`.

`ili9806e_probe()` allocates core state, stores the caller-provided transport pointer, chooses supplies (`vdd` plus optional `vccio` for Densitron and Ortustech DSI panels), gets reset GPIO, initializes the DRM panel with transport-supplied funcs and connector type, attaches a DT backlight, optionally sets `prepare_prev_first`, and adds the panel.

## Control Flow

Transport probe allocates its own bus-specific state and calls `ili9806e_probe()`. Later transport panel callbacks call `ili9806e_power_on()` before bus-specific init and `ili9806e_power_off()` during unprepare. Removal calls `ili9806e_remove()` after transport detach if needed.

## State And Persistence

The core keeps only volatile driver data in `dev_set_drvdata()`. The transport pointer is an untyped pointer back to the DSI or SPI wrapper state. There is no persistent storage.

## Dependencies And Integration Points

The core depends on DRM panel, regulators, GPIO descriptors, OF compatible checks, device properties, backlight binding, and exported GPL symbols. It is integrated by `panel-ilitek-ili9806e-dsi.c` and `panel-ilitek-ili9806e-spi.c`.

## Risks

Supply selection is based on hard-coded compatible checks in the core, so adding new transports or compatibles may require core changes. The untyped `void *transport` relies on the transport driver and panel funcs agreeing on the concrete type. `ili9806e_probe()` sets drvdata on the same device used by transport drivers, so ordering with bus-level drvdata must be considered. The core does not unwind panel add through devm, so transports must call `ili9806e_remove()` on later attach failure.

## Test Signals

Validate exported symbol linkage for both transport modules, regulator and reset GPIO acquisition, backlight binding, correct `prepare_prev_first` on compatible panels, clean power on/off sequencing, and panel removal after DSI attach failure or SPI driver removal.
