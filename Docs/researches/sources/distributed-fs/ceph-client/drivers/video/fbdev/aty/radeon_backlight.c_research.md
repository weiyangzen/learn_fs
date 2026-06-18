# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeon_backlight.c

## Purpose

`radeon_backlight.c` connects Radeon laptop LVDS backlight control to the Linux backlight subsystem. It registers a raw backlight device for LCD panels, maps fbdev brightness curves to Radeon LVDS modulation levels, powers the panel/backlight on and off through LVDS registers, and unregisters the device on teardown.

## Important APIs, Types, and Functions

The public functions are `radeonfb_bl_init()` and `radeonfb_bl_exit()`. `struct radeon_bl_privdata` stores the owning `struct radeonfb_info` and whether brightness polarity is inverted. `radeon_bl_get_level_brightness()` maps a fbdev backlight level through `info->bl_curve` into the hardware range `0x00..0xff`, with optional inversion. `radeon_bl_update_status()` is the backlight core callback and is installed through `radeon_bl_data`.

## Control Flow

Initialization exits unless the primary monitor is LCD. On PowerMac builds it also checks for compatible ATI/MNCA backlight types. It allocates private data, registers a `BACKLIGHT_RAW` device named `radeonblN`, chooses negative brightness polarity based on chip family and selected PowerBook models, stores the device in `rinfo->info->bl_dev`, initializes the default brightness curve, sets brightness to max and power on, and calls `backlight_update_status()`.

`radeon_bl_update_status()` ignores non-LCD outputs. For positive brightness it deletes any pending LVDS timer, idles the engine, clears display-disable, ensures digital/LVDS/backlight enable bits are set in the correct sequence, programs `LVDS_BL_MOD_LEVEL`, optionally delays final `LVDS_ON` state through `rinfo->lvds_timer`, and mirrors state bits into `rinfo->init_state.lvds_gen_cntl`. For zero brightness it clears LVDS always-on pixel clock on mobility/IGP chips, disables modulation/backlight/display, clears LVDS enable and digital-on in stages with required delays, schedules delayed panel power state, then restores pixel-clock control.

Teardown unregisters the backlight device, frees private data, clears `bl_dev`, and logs unload.

## State and Persistence Behavior

Persistent runtime state lives in the backlight device properties, `rinfo->info->bl_curve`, `struct radeon_bl_privdata`, `rinfo->pending_lvds_gen_cntl`, and `rinfo->init_state.lvds_gen_cntl`. Hardware LVDS state persists in `LVDS_GEN_CNTL` and `PIXCLKS_CNTL`. The code intentionally updates `init_state.lvds_gen_cntl` so later mode/power restore logic tracks the latest panel state rather than stale boot values.

## Dependencies and Integration Points

The file depends on the Linux backlight core, `radeonfb.h`, Radeon MMIO/PLL macros, the Radeon LVDS timer managed elsewhere in the driver, fbdev backlight curve helpers, and optional PowerMac backlight/platform checks. It assumes `rinfo->panel_info.pwr_delay`, `rinfo->lvds_timer`, monitor type, family, mobility/IGP flags, and initial LVDS state are initialized by the main Radeon driver.

## Risks and Edge Cases

Panel power sequencing is timing-sensitive; wrong ordering can blank, flicker, or fail to wake a panel. Brightness polarity is determined by family/model heuristics and may be wrong for unknown panels. `timer_delete_sync()` and later `mod_timer()` must coordinate with the LVDS timer callback elsewhere. The update path idles the graphics engine and touches PLL bits, so it should not race with suspend/resume or mode-setting. Allocation failure after private data creation is handled by a shared error path that frees `pdata`.

## Test Signals

Test registration only on LCD outputs, PowerMac gating, brightness min/max/mid values, inverted and non-inverted polarity families, zero-brightness powerdown, nonzero powerup from off, repeated rapid brightness changes, suspend/resume interaction, LVDS timer behavior with `panel_info.pwr_delay`, mobility/IGP pixel-clock workaround, and clean unregister with no stale `bl_dev`.
