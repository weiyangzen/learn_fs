# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_mipi_dsi.c

## Purpose

`rcar_mipi_dsi.c` implements the R-Car V3U/V4H MIPI DSI host and DRM bridge. It calculates PLL/PHY parameters, initializes the D-PHY, configures video timings, starts/stops HS/video transmission, registers a MIPI DSI host for panel commands, and exposes DU pixel-clock enable/disable hooks.

## Important APIs, Types, and Functions

Key types are `rcar_mipi_dsi_device_info`, `rcar_mipi_dsi`, `dsi_setup_info`, and `dsi_clk_config`. Exported functions are `rcar_mipi_dsi_pclk_enable()` and `rcar_mipi_dsi_pclk_disable()`. Internals include PHTW write helpers, V3U/V4H PHY init tables, PLL calculation, display timing programming, startup/shutdown, HS clock and video start/stop, bridge callbacks, host attach/detach, and command TX/RX transfer handlers.

## Control Flow

Probe allocates the bridge object, parses DT data-lane count, maps MMIO, gets module/PLL/DSI clocks, gets reset, and registers a MIPI DSI host. Host attach validates lanes, records panel format/mode flags, resolves the downstream bridge, and registers the DRM bridge. DU modeset code calls `pclk_enable()`, which enables clocks/reset, calculates DSI PLL and D-PHY settings from adjusted mode clock, initializes PHY test registers, programs lane count and VCLK, writes video timing registers, and starts the HS clock. Bridge atomic enable starts video transmission; atomic disable stops it. Host transfer builds DSI packets, writes register-based payloads up to 16 bytes, polls completion, optionally performs BTA/RX parsing, and delays between commands for panel tolerance.

## State and Persistence Behavior

The `rcar_mipi_dsi` object persists as the host/bridge state and stores clocks, reset, format, mode flags, lane count, and downstream bridge. Startup state persists in DSI registers until shutdown. Command transfers use only stack payload buffers and hardware registers. There is no runtime PM wrapper here; clock/reset state is controlled explicitly by pclk hooks.

## Dependencies and Integration Points

The driver depends on DRM bridge/MIPI DSI helpers, Linux clk/reset/iopoll/io APIs, `rcar_mipi_dsi_regs.h`, and DU encoder code that calls pclk hooks. It integrates with downstream panel/bridge devices via the MIPI DSI host attach flow.

## Risks and Edge Cases

- Register-based command mode supports only 16-byte TX/RX payloads; larger panel commands return `-EOPNOTSUPP`.
- `rcar_mipi_dsi_parameters_calc()` can leave `setup_info` incomplete if no clock config fits; later use must be covered by mode validation and tested.
- RX long-packet loop uses `RXPPD0R + i`, which increments by bytes while registers are 32-bit spaced in the header; this deserves hardware verification.
- Clock enable error unwinding must keep reset/clock state balanced.
- Mode validation only caps pixel clock at 297 MHz, not all lane/bpp/PLL corner cases.

## Test Signals

Build/probe for V3U and V4H compatibles, DSI panels using 1-4 lanes and 16/18/24 bpp, mode validation around clock limits, command-mode short/long read/write up to 16 bytes, HS clock start/stop polling, video start/stop polling, and failure injection for clock/PHY timeouts are important.
