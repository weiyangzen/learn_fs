# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-jdi-lpm102a188a.c

## Purpose

This DRM driver supports the JDI LPM102A188A command-mode panel as a dual-link MIPI DSI display. It registers a DRM panel only for the primary DSI link and controls the secondary link through a `link2` phandle.

## Important APIs, Types, And Functions

- `struct jdi_panel` stores panel state, primary/secondary DSI links, regulators, backlight, enable/reset GPIOs, and fixed mode.
- `jdi_wait_frames()` converts frame counts to delays using the fixed mode refresh.
- `jdi_panel_prepare()` disables backlight, powers rails, sequences GPIOs, configures both DSI links, exits sleep, writes DCDC registers, waits, and turns both halves on.
- `jdi_setup_symmetrical_split()` programs both links for a left/right split.
- `jdi_write_dcdc_registers()` unlocks manufacturer commands and changes VGH/VGL divider ratios.
- `jdi_panel_unprepare()` sends display off/sleep to both links and powers down.
- `jdi_panel_dsi_probe()` allocates the panel only when the secondary link is found.

## Control Flow

Both DSI devices match `jdi,lpm102a188a`. The node with `link2` finds the secondary device, registers the DRM panel, then attaches. The secondary interface attaches without panel drvdata. Prepare sends dual-link commands using `mipi_dsi_dual()` helpers and supports only symmetrical left-right split. Enable waits for image data before enabling backlight; disable turns backlight off and waits before shutdown.

## State And Persistence

No persistent state exists. The fixed mode is 2560x1800 at 60 Hz with 211 mm by 148 mm size and 8 bpc. The driver holds a device reference to `link2` until deletion. Panel and DCDC state are volatile.

## Dependencies And Integration Points

The driver integrates with DRM panel, dual-link MIPI DSI helpers, OF phandle lookup, regulators, GPIOs, and `devm_of_find_backlight()`. The DSI host and device tree must correctly represent both links. Only left-right split is supported.

## Risks

Dual-link probe ordering can defer until the secondary DSI device exists. Misconfigured `link2` or host split assumptions can cause half-screen or no-screen output. Failure handling after partial power-up does not lower every GPIO in all branches. DCDC divider changes are hardware-specific and may vary by board.

## Test Signals

Validate both DSI devices attach, primary finds `link2`, only one DRM panel is registered, both links receive commands, full-width image alignment, no left/right swap, TE behavior, backlight sequencing, suspend/resume, and absence of backlight noise.
