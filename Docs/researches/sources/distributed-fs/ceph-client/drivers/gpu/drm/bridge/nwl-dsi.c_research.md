# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/nwl-dsi.c

## Purpose

This file implements the Northwest Logic MIPI DSI host/bridge used on i.MX8. It registers both a `mipi_dsi_host` for panel command transfers and a DRM bridge for video output, configures the DSI host, DPHY, DPI timing generator, resets, clocks, mux input selection, and interrupt-driven packet transfer completion.

## Important APIs, Types, And Functions

`struct nwl_dsi` stores the DRM bridge, DSI host, PHY/config, quirk flags, MMIO regmap, IRQ, four resets, input mux, five clocks, attached DSI lane/format/mode flags, current display mode, sticky register error, and active packet transfer pointer. `struct nwl_dsi_transfer` tracks one MIPI DSI transaction, including packet, completion, status, direction, BTA need, command byte, and RX/TX lengths.

Key functions include `nwl_dsi_config_host()`, `nwl_dsi_config_dpi()`, `nwl_dsi_get_dphy_params()`, `nwl_dsi_mode_set()`, `nwl_dsi_disable()`, `nwl_dsi_host_attach()`, `nwl_dsi_host_transfer()`, `nwl_dsi_begin_transmission()`, `nwl_dsi_read_packet()`, `nwl_dsi_finish_transmission()`, `nwl_dsi_irq_handler()`, bridge mode_set/atomic_check/enable/disable/attach, and DT parsing/input mux selection.

## Control Flow

Probe allocates the bridge, parses PHY, clocks, mux, MMIO regmap, IRQ, and resets, requests IRQ, registers the MIPI DSI host, detects SoC quirks, sets bridge metadata/timings, enables runtime PM, selects LCDIF or DCSS input through the mux based on graph endpoints, and adds the bridge.

When a DSI peripheral attaches, `nwl_dsi_host_attach()` stores lane count, pixel format, and mode flags. Bridge mode_set computes DPHY timings, stores the adjusted mode, resumes runtime PM, enables LCDIF and core clocks, deasserts PCLK reset, initializes PHY/host/DPI/interrupts, then deasserts ESC and BYTE resets so command transfers can run. Atomic enable deasserts DPI reset, starting pixel flow. Atomic disable powers down PHY, disables TX escape clock, asserts DPI/BYTE/ESC/PCLK resets, disables clocks, and drops runtime PM.

DSI host transfer builds a packet, chooses send/receive, enables RX escape clock, writes payload/header, starts transfer, waits up to 500 ms for IRQ completion, and returns bytes transferred or error. The IRQ handler logs FIFO/timeout errors and completes send/RX transactions when status bits arrive.

## State And Persistence

Attached DSI parameters and the current adjusted mode persist in `struct nwl_dsi`. `dsi->error` accumulates regmap read/write failures until cleared by `nwl_dsi_clear_error()`. `dsi->xfer` points to a stack transfer only during synchronous host transfers and is completed by IRQ. Hardware state spans reset lines, clocks, PHY power, mux selection, and DSI/DPI registers.

## Dependencies And Integration Points

The driver depends on platform resources, regmap MMIO, PHY MIPI DPHY helpers, clocks, resets, mux consumer API, runtime PM, IRQs, SoC matching for i.MX8MQ errata, DRM bridge/atomic helpers, MIPI DSI host APIs, OF graph, and `nwl-dsi.h` register definitions. It attaches downstream bridge/panel from output port 1.

## Risks And Edge Cases

The active transfer pointer is not protected by a lock, so transfers assume serialization by the MIPI DSI framework/panel setup. Some error paths in mode_set jump to runtime put without undoing already enabled clocks/resets. The i.MX8MQ E11418 workaround changes HS mode for payload patterns with zero high bytes. Mode validity depends on lane count/format already being attached; before attach, format/lane values may be incomplete. Reset sequencing comments note that panel bridge command setup and DPI deassertion are not ideally ordered.

## Test Signals

Test DSI host attach for 1-4 lanes and RGB565/RGB666/RGB888, command writes and reads with short/long packets, IRQ completion and timeout paths, FIFO overflow/HS timeout logs, LCDIF versus DCSS mux selection, runtime PM and reset sequencing, i.MX8MQ rev 2.0 quirk behavior, mode clock limits, suspend/remove cleanup, and panel init command timing.
