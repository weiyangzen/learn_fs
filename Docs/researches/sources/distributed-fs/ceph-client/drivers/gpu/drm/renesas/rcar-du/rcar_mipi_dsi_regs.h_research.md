# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_mipi_dsi_regs.h

## Purpose

`rcar_mipi_dsi_regs.h` defines register offsets and bitfields for the R-Car V3U/V4H DSI link, command transfer engine, video mode engine, PPI, clocks, PHY setup, PLL, and PHY test interface.

## Important APIs, Types, and Functions

Macro groups cover link status (`LINKSR`), lane count (`TXSETR`), command TX/RX registers (`TXCM*`, `RX*`, `TOS*`), video mode registers (`TXVM*`), PPI lane status/control (`PPI*`), clock controls (`LPCLKSET`, `CFGCLKSET`, `VCLKSET`, `VCLKEN`), `PHYSETUP`, `CLOCKSET*`, and PHY test registers (`PHTW`, `PHTR`, `PHTC`). Bitfield helpers use `FIELD_PREP()` and `GENMASK_U32()`.

## Control Flow

The MIPI DSI driver composes these macros during PHY/PLL initialization, lane setup, timing programming, HS clock transitions, video start/stop, and command-mode transfers.

## State and Persistence Behavior

The header defines hardware state only. Registers retain configuration until shutdown, reset assertion, or subsequent writes.

## Dependencies and Integration Points

It requires Linux bitfield/bit macros through included driver context and is consumed by `rcar_mipi_dsi.c`.

## Risks and Edge Cases

- Register offsets and bit widths are tightly coupled to V3U/V4H hardware manuals.
- RX payload registers are defined as 32-bit spaced (`RXPPD0R`..`RXPPD3R`), so consumers must increment by register spacing rather than byte count.
- Macro inputs are generally not range-checked.

## Test Signals

Register write tracing for DSI startup/shutdown and command transfers, plus compile checks for field macros, provide the main validation signal.
