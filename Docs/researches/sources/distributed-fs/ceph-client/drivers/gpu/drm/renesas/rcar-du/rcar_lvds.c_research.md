# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_lvds.c

## Purpose

`rcar_lvds.c` implements the R-Car LVDS DRM bridge. It configures LVDS channel routing, bus format, simple and extended PLLs, dual-link companion encoders, runtime PM, resets, and bridge chaining to panels or downstream bridges.

## Important APIs, Types, and Functions

Important types are `rcar_lvds_device_info` for generation/quirks/PLL setup and `rcar_lvds` for bridge, clocks, reset, MMIO, companion, and link type. Exported helpers are `rcar_lvds_pclk_enable()`, `rcar_lvds_pclk_disable()`, `rcar_lvds_dual_link()`, and `rcar_lvds_is_connected()`. Key internals include PLL setup for Gen2/Gen3/D3/E3, `rcar_lvds_enable()`, `rcar_lvds_disable()`, bridge atomic enable/disable, DT companion parsing, clock acquisition, probe/remove, and runtime suspend/resume.

## Control Flow

Probe allocates a DRM bridge, applies SoC match quirks including an R8A7790 ES1 override, parses the downstream panel/bridge and optional companion LVDS encoder, maps MMIO, gets module and optional PLL input clocks, gets reset, enables runtime PM, and registers the bridge. Atomic enable resumes the device, recursively enables the companion for dual-link, programs control-signal routing and channel lane order, configures stripe mode, programs a PLL unless an extended PLL was already enabled explicitly, selects LVDS mode from connector bus format, powers channels/PLL/PHY in hardware-required order, waits for PLL startup, and releases reset. Disable reverses the sequence and handles companion shutdown. D3/E3 extended PLL users call the exported pixel-clock enable/disable path from DU clock code.

## State and Persistence Behavior

`rcar_lvds` persists as devm bridge storage. It stores the downstream bridge/panel, optional companion bridge reference, link type, MMIO, clocks, and reset. Hardware state persists in LVDS registers and PLL until bridge disable or explicit pclk disable. Runtime PM asserts reset and disables the module clock when idle.

## Dependencies and Integration Points

The file depends on DRM bridge/panel/of helpers, media bus format definitions, Linux clk/reset/runtime PM, SoC revision matching, and `rcar_lvds_regs.h`. It is used by R-Car DU encoder routing and by DU clock code for extended PLL platforms.

## Risks and Edge Cases

- PLL calculation for D3/E3 assumes at least one input clock and a valid candidate; callers must avoid using an uninitialized `pll_info`.
- Dual-link setup reaches into the companion bridge's private data, which the source marks as a FIXME.
- Extended PLL disable intentionally defers full LVDS disable to avoid DU vblank timeouts; sequencing changes can reintroduce stalls.
- Unsupported or absent LVDS bus formats fall back to JEIDA with warnings.
- The code is SoC-quirk-heavy; wrong compatible data can invert lanes, miss LVEN/PWD ordering, or disable dual-link.

## Test Signals

Test single-link and dual-link LVDS panels, even/odd and odd/even pixel ordering, JEIDA/VESA/mirror bus formats, D3/E3 extended PLL dot-clock-only use, runtime suspend/resume, probe deferral of companion bridges, and mode clamping between minimum and 148.5 MHz.
