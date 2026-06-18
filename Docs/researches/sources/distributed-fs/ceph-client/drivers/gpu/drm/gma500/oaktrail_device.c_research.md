# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail_device.c

## Purpose
This file defines the Oaktrail chipset personality for the shared GMA500 driver. It wires output initialization, backlight control, display save/restore, display-island power gating, register maps, chip setup/teardown, and the `psb_ops` table selected by Oaktrail PCI IDs.

## Important APIs, Types, and Functions
The externally consumed object is `oaktrail_chip_ops`. Important functions include `oaktrail_output_init()`, `oaktrail_backlight_init()`, `oaktrail_set_brightness()`, `oaktrail_save_display_registers()`, `oaktrail_restore_display_registers()`, `oaktrail_power_down()`, `oaktrail_power_up()`, `oaktrail_chip_setup()`, and `oaktrail_teardown()`. `oaktrail_regmap` maps pipe A/B abstract offsets to hardware registers.

## Control Flow
Chip setup enables MSI, installs the Oaktrail register map, runs MID chip setup, falls back to OpRegion/VBT when no GCT exists, initializes GMBUS, and probes HDMI hardware. Output init creates LVDS if fuses say LVDS, logs unsupported DSI otherwise, creates HDMI if present, and initializes SDVO. Suspend save captures watermarks, pipe A, cursor, palette, HDMI state, LVDS/panel/backlight, overlay, and DPST registers, then shuts down LVDS hardware. Restore writes the saved registers back in hardware-safe order.

## State and Persistence Behavior
The file persists saved hardware state in `dev_priv->regs`, HDMI state in `dev_priv->hdmi_priv`, backlight adjustment percentages, and `dev_priv->regmap`. Power gating uses OSPM I/O ports derived by `gma_power_init()`. Backlight state is written to `BLC_PWM_CTL*` and adjusted by `blc_adj1`/`blc_adj2`.

## Dependencies and Integration Points
It depends on MID BIOS discovery, Intel BIOS/OpRegion parsing, GMBUS, HDMI, LVDS, SDVO, power management, and register definitions. `psb_drv.c` selects `oaktrail_chip_ops` for the 0x4100 family and calls these hooks during load, suspend/resume, modeset, and unload.

## Risks
Power-up/down loops poll forever without timeout. Backlight PWM calculations depend on `core_freq`; a missing/zero core clock can break setup. Save/restore order is hardware-sensitive and mixes VDC and HDMI controller state. DSI is explicitly unsupported, so systems fused for MIPI will log an error and have no internal panel.

## Test Signals
Signals include Oaktrail probe selecting this ops table, successful GCT or BIOS fallback, registered LVDS/HDMI/SDVO connectors as expected, backlight init and brightness changes, suspend/resume preserving panel state, and display-island power transitions completing without hangs.
