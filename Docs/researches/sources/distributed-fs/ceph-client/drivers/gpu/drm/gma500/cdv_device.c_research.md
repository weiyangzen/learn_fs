<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_device.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_device.c

## Purpose

This file provides Cedarview-specific chip operations for the GMA500 DRM driver. It initializes Cedarview outputs, disables legacy VGA, implements Cedarview backlight control, PM/power gating, hotplug handling, HDMI/DP connector properties, display-register save/restore, watermarks integration, errata, and the `cdv_chip_ops` dispatch table.

## Important APIs, Types, And Functions

Important functions include `cdv_disable_vga()`, `cdv_output_init()`, `cdv_get_max_backlight()`, `cdv_get_brightness()`, `cdv_set_brightness()`, `cdv_backlight_init()`, `CDV_MSG_READ32()`, `CDV_MSG_WRITE32()`, `cdv_init_pm()`, `cdv_errata()`, `cdv_save_display_registers()`, `cdv_restore_display_registers()`, `cdv_power_down()`, `cdv_power_up()`, `cdv_hotplug_event()`, `cdv_hotplug_enable()`, property attach helpers, `cdv_chip_setup()`, and global `cdv_chip_ops`.

## Control Flow

Chip setup initializes hotplug work, enables MSI use, installs the Cedarview register map, reads core frequency, initializes opregion/VBT, and clears hotplug enables. Output init creates scaling property, disables VGA, initializes CRT and LVDS, then detects SDVOB/SDVOC as HDMI and optionally DisplayPort. PM init discovers APM/OSPM bases through PUNIT sideband config cycles and powers the GPU on. Save/restore capture display, panel, backlight, VGA, and interrupt registers, DPMS connectors off/on, reinitialize DPIO/DPLL sync lock, reapply errata, reset mode config, and force mode restoration. Hotplug IRQ schedules work that emits a DRM HPD event.

## State And Persistence

State persists in `drm_psb_private`: APM/OSPM bases, core frequency, register save area, `hotplug_work`, properties, VBT-derived fields, and `regmap`. Hardware state includes VGA sequencer bits, APM command/status ports, PUNIT message registers, display/clock/watermark registers, backlight PWM, panel power registers, hotplug enable/status, and interrupt mask/enable.

## Dependencies And Integration Points

The file integrates PCI config access, x86 I/O ports, DRM connector iteration, helper DPMS, opregion/VBT parsing, Cedarview CRT/LVDS/HDMI/DP init files, shared CRTC save/restore, watermarks in `cdv_intel_display.c`, and the core `psb_ops` abstraction.

## Risks And Test Signals

Risks include unguarded root PCI device assumptions in sideband helpers, short power-transition retry loops that return success even on timeout in power up/down, fragile save/restore ordering, hotplug status clearing races, and output probing based on register-detected bits. Test signals are Cedarview boot, VGA-disabled display handoff, CRT/LVDS/HDMI/DP enumeration, hotplug IRQs, backlight percentage conversion including legacy combination mode, suspend/resume register restoration, and dual-pipe watermark behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_device.c -->
