# subset-b-005556 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeon_base.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeon_base.c

## Purpose

`radeon_base.c` is the central fbdev PCI driver for pre-KMS ATI Radeon adapters. It binds supported PCI IDs, maps MMIO and framebuffer apertures, discovers firmware/monitor/PLL state, registers the `fb_info`, implements core fbdev callbacks, and coordinates mode programming, blanking, palette updates, sysfs EDID exposure, acceleration setup, power-management initialization, and teardown. The file is the owner of the `pci_driver` named `radeonfb` and is the integration point that calls into the companion Radeon files for I2C/DDC, monitor probing, acceleration, backlight, and PM.

## Important APIs, Types, And Functions

The PCI ID table uses `CHIP_DEF()` to encode Radeon family and capability flags in `driver_data`; probe decodes these into `rinfo->family`, `has_CRTC2`, `is_mobility`, and `is_IGP`. Global module parameters and boot options include `mode_option`, `monitor_layout`, `noaccel`, `nomodeset`, `ignore_edid`, `mirror`, `default_dynclk`, `nomtrr`, `panel_yres`, `force_dfp`, `force_measure_pll`, `force_sleep`, and `ignore_devlist`.

Register access helpers exported to the driver family include `_radeon_msleep()`, `_OUTREGP()`, `__INPLL()`, `__OUTPLL()`, `__OUTPLLP()`, `_radeon_fifo_wait()`, `radeon_engine_flush()`, and `_radeon_engine_idle()`. These hide MMIO/PLL errata details and provide bounded polling with timeout diagnostics. Firmware helpers include `radeon_map_ROM()`, `radeon_unmap_ROM()`, x86 `radeon_find_mem_vbios()`, OF `radeon_read_xtal_OF()`, `radeon_probe_pll_params()`, and `radeon_get_pllinfo()`.

The fbdev operations are collected in `radeonfb_ops`: `fb_check_var`, `fb_set_par`, `fb_setcolreg`, `fb_setcmap`, `fb_pan_display`, `fb_blank`, `fb_ioctl`, `fb_sync`, accelerated fill/copy/imageblit, default mmap, and default I/O read/write. Mode-state routines are `radeon_save_state()`, `radeon_calc_pll_regs()`, `radeon_write_pll_regs()`, `radeon_write_mode()`, and `radeonfb_set_par()`. Lifecycle routines are `radeonfb_pci_register()`, `radeonfb_pci_unregister()`, `radeonfb_init()`, and `radeonfb_exit()`.

## Control Flow

Module initialization first honors `fb_modesetting_disabled("radeonfb")`, parses boot options when built in, and registers the PCI driver. Probe enables the PCI device, allocates `fb_info` with private `struct radeonfb_info`, initializes locks/timers, decodes chip identity, removes conflicting aperture users, requests BAR 0 and BAR 2, maps MMIO, applies PPC memory-map fixups, identifies VRAM size/type, maps a bounded write-combining framebuffer window, locates BIOS/legacy/OF data, derives PLL information, optionally creates four bit-banged I2C busses, fills `fb_info`, probes monitors, builds the mode database, exposes EDID sysfs files, saves initial registers, initializes PM, registers with fbdev, adds a WC mapping, optionally initializes backlight, and unmaps temporary BIOS ROM.

Mode setting flows through `radeonfb_check_var()` and `radeonfb_set_par()`. `check_var` delegates timing selection to `radeon_match_mode()`, normalizes color depth, computes virtual pitch alignment, validates mapped VRAM capacity, and corrects offsets. `set_par` computes CRTC timings, sync polarity, pitch, PLL values, flat-panel scaler/stretch registers, LVDS/TMDS control, endian surface swappers, and then writes the mode if the adapter is awake. `radeon_write_mode()` blanks unless asked for registers-only restoration, clears common overlay/capture/I2C interrupt registers, writes surface/CRTC/DAC/flat-panel registers, updates PLLs, unblanks, and restores VCLK source.

Blanking uses `radeon_screen_blank()` to disable CRTC sync/display bits and then handle DFP/LCD output-specific sequencing. LCD blank/unblank uses `lvds_timer` for delayed LVDS power transitions and tracks `pending_lvds_gen_cntl`. Panning programs `CRTC_OFFSET`. Palette updates select the primary palette, handle 8/15/16/24/32 bpp mappings, and maintain both hardware palette entries and the first 16-entry pseudo-palette.

## State And Persistence

Persistent runtime state is in `struct radeonfb_info` from `radeonfb.h`: mapped resource bases, BIOS pointer, chip family/flags, VRAM sizing, monitor and EDID pointers, panel info, PLL info, current and initial `struct radeon_regs`, palette caches, WC cookie, PM flags, and LVDS timer state. `rinfo->state` represents the last programmed mode for resume; `rinfo->init_state` snapshots the firmware/entry state for restoration-like behavior and LVDS sequencing. The driver also publishes EDID blobs as binary sysfs attributes tied to the PCI device. State is not persisted across boot; all hardware state is rediscovered on probe and reconstructed on resume.

## Dependencies And Integration Points

This file depends on the Linux PCI, fbdev, sysfs, aperture, MMIO, MTRR/write-combining, timer, and module parameter APIs. It uses Radeon register definitions from `<video/radeon.h>`, chip IDs from `ati_ids.h`, EDID helpers from `../edid.h`, and architecture hooks for PPC/SPARC OF and PPC BootX text. It calls `radeon_create_i2c_busses()`, `radeon_probe_screens()`, `radeon_check_modes()`, `radeonfb_pm_init()`, `radeonfb_pm_exit()`, acceleration functions from `radeon_accel.c`, and optional backlight helpers.

## Risks

The file performs extensive raw MMIO and PLL programming with family-specific errata; ordering and delays are hardware-sensitive. `radeon_probe_pll_params()` disables local interrupts while measuring vertical timing and can fail if display state is odd. BIOS parsing assumes legacy offsets and validates only lightly. `radeonfb_check_var()` adjusts offsets with `v.xres_virtual - v.xres - 1`, which requires care when virtual and visible sizes match. The cleanup path after `register_framebuffer()` failure jumps to `err_unmap_fb` but does not call `radeonfb_pm_exit()`, even though PM was initialized just before `pci_set_drvdata()`. EDID sysfs creation failures are non-fatal, so user-space may miss diagnostics. Runtime globals such as `mirror` and module-wide options affect all adapters rather than being per-device.

## Test Signals

Useful validation signals include PCI bind/unbind on supported Radeon IDs, failure-injection across region request, MMIO map, framebuffer map, cmap allocation, I2C creation, and framebuffer registration paths; boot with `noaccel`, `nomodeset`, `ignore_edid`, `monitor_layout`, `mode_option`, `nomtrr`, and dynamic-clock options; `fbset` mode validation and panning; `FBIO_RADEON_GET_MIRROR`/`SET_MIRROR` on mobility chips; sysfs `edid1`/`edid2` reads; suspend/resume preservation of `rinfo->state`; and visual checks for LVDS/DFP blank/unblank timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeon_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeon_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeon_i2c.c

## Purpose

`radeon_i2c.c` provides the optional `CONFIG_FB_RADEON_I2C` DDC transport used by `radeon_monitor.c` to identify connected displays and obtain EDID. The hardware exposes DDC pins through Radeon GPIO-style registers, so this file wraps those registers in four Linux `i2c_adapter`s using `i2c-algo-bit`, then uses fbdev DDC helpers to classify connectors as CRT, LCD, DFP, or absent.

## Important APIs, Types, And Functions

The primary shared type is `struct radeon_i2c_chan`, defined in `radeonfb.h`, containing a back-pointer to `struct radeonfb_info`, the DDC GPIO register offset, an `i2c_adapter`, and an `i2c_algo_bit_data` object. The low-level bit callbacks are `radeon_gpio_setscl()`, `radeon_gpio_setsda()`, `radeon_gpio_getscl()`, and `radeon_gpio_getsda()`. They use `INREG()` and `OUTREG()` on `chan->ddc_reg`, setting output-enable bits low to drive the line low and clearing them to release the line high.

`radeon_setup_i2c_bus()` fills the adapter name, owner, parent device, bit algorithm callbacks, delay/timeout parameters, raises SCL/SDA, and registers with `i2c_bit_add_bus()`. `radeon_create_i2c_busses()` initializes four channels in fixed order: `ddc_monid` on `GPIO_MONID`, `ddc_dvi` on `GPIO_DVI_DDC`, `ddc_vga` on `GPIO_VGA_DDC`, and `ddc_crt2` on `GPIO_CRT2_DDC`. `radeon_delete_i2c_busses()` unregisters any initialized adapters. `radeon_probe_i2c_connector()` calls `fb_ddc_read()` and returns a Radeon monitor type based on the EDID digital-input bit and mobility/LVDS register state.

## Control Flow

Probe-time flow begins in `radeonfb_pci_register()` after PLL discovery. When I2C support is enabled, it calls `radeon_create_i2c_busses()`, which attempts all four adapter registrations regardless of previous failures. Later, `radeon_probe_screens()` probes specific logical DDC ports by passing enum values such as `ddc_dvi`, `ddc_vga`, or `ddc_crt2` into `radeon_probe_i2c_connector()`. That function converts the enum to the zero-based channel index with `conn - 1`, reads EDID, stores the allocated EDID pointer through `out_edid` if requested, and returns `MT_NONE` on read failure, `MT_LCD` for digital EDID when mobility LVDS is currently on, `MT_DFP` for other digital EDID, or `MT_CRT` for analog EDID.

Teardown flow is symmetric at device removal or failed probe cleanup: `radeon_delete_i2c_busses()` calls `i2c_del_adapter()` on each channel whose `rinfo` pointer remains set and then clears that pointer. EDID memory returned by `fb_ddc_read()` is not freed here; ownership is transferred to `rinfo->mon1_EDID` or `rinfo->mon2_EDID` and freed by the base driver.

## State And Persistence

The file keeps no static mutable state. All channel state lives in `rinfo->i2c[4]`. The Linux I2C core owns registered adapter state after `i2c_bit_add_bus()`, while EDID buffers are dynamically allocated by `fb_ddc_read()` and stored by callers. Electrical line state is maintained in hardware GPIO registers, with explicit readbacks after writes to flush posted MMIO.

## Dependencies And Integration Points

Dependencies are Linux I2C core, `i2c-algo-bit`, fbdev EDID/DDC support, Radeon register definitions, and the `INREG`/`OUTREG` MMIO helpers from `radeonfb.h`. The monitor probing file depends on the port numbering and return semantics here. The base driver depends on this file only under `CONFIG_FB_RADEON_I2C`; without it, monitor probing falls back to OF, BIOS scratch/register state, and DAC load detection.

## Risks

`radeon_create_i2c_busses()` ignores individual setup failures, leaving `rinfo` set even if an adapter was not registered; `radeon_delete_i2c_busses()` may call `i2c_del_adapter()` for a channel whose add failed. `radeon_probe_i2c_connector()` trusts `conn` to be 1 through 4, so incorrect callers would index outside `rinfo->i2c`. EDID classification uses only byte `0x14` and an LVDS-on heuristic, so unusual panels or stale LVDS state can be misclassified. Bit-banged timings are fixed at `udelay = 10` and `timeout = 20`, which may be marginal on some boards.

## Test Signals

Tests should exercise adapter registration/removal with all four ports, simulated `i2c_bit_add_bus()` failure, invalid or absent EDID, analog EDID classification, digital TMDS classification, and the mobility LVDS override. Integration signals include `radeonfb` debug logs for each port, monitor type chosen by `radeon_probe_screens()`, sysfs EDID content from the base driver, and absence of I2C adapter lifetime warnings during probe failure and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeon_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeon_monitor.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeon_monitor.c

## Purpose

`radeon_monitor.c` discovers attached Radeon displays, extracts flat-panel timing information, builds the primary head mode list, selects a default `fb_var_screeninfo`, and implements mode matching for `radeonfb_check_var()`. It bridges platform firmware, BIOS tables, EDID/DDC, manual `monitor_layout`, DAC load detection, and fbdev mode database helpers so `radeon_base.c` can program a valid CRTC/LVDS/TMDS mode.

## Important APIs, Types, And Functions

The file exports `radeon_probe_screens()`, `radeon_check_modes()`, and `radeon_match_mode()`. It maintains a default 640x480x8 `radeonfb_default_var`. Firmware helpers under PPC/SPARC include `radeon_parse_montype_prop()` and `radeon_probe_OF_head()`, which inspect OF `display-type` and EDID properties. BIOS helpers include `radeon_get_panel_info_BIOS()` for LVDS timing and divider tables and `radeon_parse_connector_info()` for debug connector table decoding. Hardware probing includes `radeon_crt_is_connected()`, which temporarily changes DAC/VCLK/CRTC registers to use the DAC comparator for load detection.

Mode-selection helpers are `radeon_parse_monitor_layout()`, `radeon_fixup_panel_info()`, `radeon_var_to_panel_info()`, `radeon_videomode_to_var()`, optional pSeries `is_powerblade()`, `radeon_compare_modes()`, and `radeon_match_mode()`.

## Control Flow

`radeon_probe_screens()` first parses connector info for diagnostics. If `monitor_layout` is supplied, it maps strings `CRT`, `TMDS`, and `LVDS` to monitor types and optionally probes EDID without changing the requested layout. If the first monitor is absent, it promotes monitor 2 or assumes CRT. Without a manual layout, the function auto-detects. Single-head cards try OF, then DVI/VGA/CRT2 DDC, then assume CRT. Dual-head cards first inspect BIOS connector data to detect reversed DAC or TMDS wiring, then probe head 1 via OF, DVI DDC, CRT2 DDC, mobility LVDS scratch/register hints, and CRT DAC load. Head 2 is probed via OF, VGA DDC, CRT2 DDC if unused, and the opposite DAC load path. If only head 2 is found, it is promoted to head 1. Reversed TMDS handling swaps monitor state to keep internal TMDS primary. If `ignore_edid` is set, EDID buffers are freed after type detection.

`radeon_check_modes()` initializes `info->var` and `info->modelist`, then for LCD primary displays tries BIOS panel info first. If BIOS dividers are not locked and EDID exists, it parses EDID detailed timing into panel info when it is at least as large as current panel dimensions. PPC may force firmware PLL dividers for mobility LCD panels. With valid panel info, it constructs a default native panel mode. It then converts EDID monspecs to a modelist and stores `rinfo->mon1_modedb`. If panel info is still missing, it guesses panel size from `FP_HORZ_STRETCH` and `FP_VERT_STRETCH`, tries to find a matching mode, or falls back to CRT behavior. User `mode_option`, pSeries hardcoded fallback, and EDID preferred timing are applied before the chosen mode is added to `info->modelist`.

`radeon_match_mode()` copies the requested var, selects EDID modedb or built-in VESA modes, validates direct TEST/NOW requests, and for FIND-style activation chooses the closest mode that is at least as large. Flat-panel scalers allow fallback from native EDID modes to VESA modes and may accept unmatched modes for RMX scaling; CRTs reject unmatched modes.

## State And Persistence

The file mutates monitor and mode fields in `struct radeonfb_info`: `mon1_type`, `mon2_type`, `mon1_EDID`, `mon2_EDID`, `mon1_modedb`, `mon1_dbsize`, `reversed_DAC`, `reversed_TMDS`, and `panel_info`. It also fills `fb_info->var`, `fb_info->monspecs`, and `fb_info->modelist`. EDID buffers are allocated by OF duplication or I2C DDC and later owned by the base driver. Panel info is volatile runtime state reconstructed at probe; no persistent configuration is written.

## Dependencies And Integration Points

The file depends on `radeonfb.h`, fbdev EDID/mode helpers, optional OF APIs, optional Radeon I2C probing, and Radeon register definitions. `radeon_base.c` calls it during PCI probe before saving mode state and registering the framebuffer. `radeonfb_set_par()` later consumes `panel_info`, monitor types, reversed output hints, and mode lists to compute CRTC/flat-panel registers.

## Risks

Detection is heuristic-heavy. OF can label DFP as LCD, BIOS connector tables are parsed mostly for hints, and DDC can be absent or routed through alternate GPIOs. Manual `monitor_layout` parsing uses fixed four-character buffers, truncating longer tokens. DAC load detection temporarily rewrites display and clock registers; missed restoration would affect active output. BIOS panel parsing trusts offsets under `fp_bios_start` and only bounds the power delay. `radeon_match_mode()` intentionally accepts some RMX modes without strict validation, which can permit timings that user space requested but hardware or panel scaling handles poorly. `ignore_edid` frees EDID and loses mode database quality.

## Test Signals

Good signals include monitor detection logs for single and dual head cards, reversed DAC/TMDS cases, manual `monitor_layout` combinations, `ignore_edid`, DDC-present and DDC-absent panels, mobility non-DDC LVDS detection, BIOS panel timing extraction, EDID preferred timing selection, pSeries fallback, `fb_find_mode()` with `mode_option`, and `fbset` requests using `FB_ACTIVATE_TEST`, `NOW`, and `FIND`. Regression testing should verify that `info->modelist` is never empty after probe and that EDID allocations are freed on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeon_monitor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeon_pm.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeon_pm.c

## Purpose

`radeon_pm.c` implements Radeon framebuffer power management. It controls dynamic clocking, prepares chips for low-power suspend states, saves/restores hardware registers, handles D2 sleep and selected D3-cold reinitialization paths, wires into the PCI `dev_pm_ops`, and applies machine-specific workarounds for PowerMacs and selected x86 laptops. It is tightly coupled to `radeon_base.c`, which initializes PM after probe and uses the exported PM ops from the PCI driver.

## Important APIs, Types, And Functions

Public entry points are `radeonfb_pm_init()`, `radeonfb_pm_exit()`, and `radeonfb_pci_pm_ops`. x86 workaround data is represented by `struct radeon_device_id` and `radeon_workaround_list`, where subsystem IDs can OR PM capabilities into `rinfo->pm_mode` and replace `rinfo->reinit_func`.

Dynamic-clock control is split between `radeon_pm_disable_dynamic_mode()` and `radeon_pm_enable_dynamic_mode()`, with separate paths for R100/RV100/RV350/R300/mobility/IGP families. PM register preservation uses `radeon_pm_save_regs()` and `radeon_pm_restore_regs()` over the fixed `rinfo->save_regs[100]` array. Low-power preparation helpers include `radeon_pm_disable_iopad()`, `radeon_pm_program_v2clk()`, `radeon_pm_low_current()`, and `radeon_pm_setup_for_suspend()`. Memory-controller and PLL reinit helpers include `INMC()`, `OUTMC()`, DLL enable functions, `radeon_pm_full_reset_sdram()`, `radeon_pm_reset_pad_ctlr_strength()`, `radeon_pm_all_ppls_off()`, `radeon_pm_start_mclk_sclk()`, spread-spectrum helpers, and pixel PLL restoration.

Chip-specific D3-cold reinitializers include `radeon_reinitialize_M10()` for RV350/M10/M11 style chips and PPC-only `radeon_reinitialize_M9P()` for M9+ PowerMac hardware. A large `radeon_reinitialize_QW()` implementation exists under `#if 0` as incomplete reference code.

## Control Flow

`radeonfb_pm_init()` records dynamic-clock policy, immediately enables/disables dynamic clocks when requested, detects PowerMac capabilities from OF node names, marks D2 or D3-cold resume support, registers platform wake capability, applies x86 subsystem workarounds unless suppressed, and honors `force_sleep` by enabling D2. `radeonfb_pm_exit()` tears down the old PPC early-resume hook when applicable.

Suspend enters through `radeonfb_pci_suspend_late()`. Freeze/prethaw do not power down hardware. For real suspend/hibernate, it locks the console, marks fbdev suspended, idles/resets the accelerator, blanks the display, sets `asleep` and `lock_blank`, deletes the LVDS timer, suspends PMAC AGP if needed, and saves a full register context if D3-cold resume is supported. Mobility chips without D2 support receive explicit LVDS shutdown. If D2 is supported, `radeon_set_suspend(..., 1)` disables dynamic mode, saves registers, programs V2CLK, disables pads, selects low-current settings, sets suspend clock/power registers, disables PCI, saves PCI state, repeatedly forces PCI D2 until it sticks, and calls platform power transition.

Resume enters `radeonfb_pci_resume()`. It locks the console, checks for D3-cold power loss by comparing key saved PLL registers against live hardware, invokes `rinfo->reinit_func` when required, or resumes from D2 with `radeon_set_suspend(..., 0)`. After hardware wake, it writes the saved display mode registers-only, reinitializes the accelerator, restores pan offset and cmap, clears fbdev suspend, unblanks, resumes PMAC AGP, reapplies dynamic-clock policy, and marks the PCI device ON.

## State And Persistence

PM state lives in `rinfo->dynclk`, `rinfo->pm_mode`, `rinfo->reinit_func`, `rinfo->save_regs[100]`, `rinfo->asleep`, `rinfo->lock_blank`, and `rinfo->no_schedule`. The saved register array is an implicit ABI inside this file; many indices have family-specific meanings. PM also relies on `rinfo->state` from `radeon_base.c` to restore the programmed mode after resume. PCI power state is tracked through `pdev->dev.power.power_state` and `pdev->current_state`; no state persists across driver unload.

## Dependencies And Integration Points

The file depends on Radeon MMIO/PLL helpers from `radeonfb.h`, PCI PM APIs, fbdev suspend APIs, console locking, AGP backend headers, optional PPC PMAC features, OF node naming, and subsystem IDs from `ati_ids.h`. It calls accelerator reset/init functions indirectly through base resume flow and expects `radeon_screen_blank()` and `radeon_write_mode()` from `radeon_base.c` to be available. PowerMac integration uses `pmac_suspend_agp_for_card()`, `pmac_resume_agp_for_card()`, and `pmac_call_feature()`.

## Risks

The most important risk is ordering: clock, PLL, memory-controller, LVDS, and PCI power transitions are register-sequence sensitive and family-specific. `save_regs` uses numeric slots rather than named structure fields, so duplicate slot use or family-dependent interpretation can cause subtle resume breakage; slot 96 is assigned both an R300 MC value and later `HDP_DEBUG` depending on path. Several sequences include magic constants copied from firmware traces. D2 entry loops until the PCI PM state bit matches the target and sleeps 500 ms each iteration, so bad hardware could hang suspend. `radeonfb_pci_resume()` can return early without completing if `no_schedule` is set and `console_trylock()` fails. D3-cold resume without a reinit function returns `-EIO` and leaves display recovery to soft reboot. Dynamic clocking changes can interact with DRI or active rendering if not fully quiesced.

## Test Signals

Testing should cover boot/probe with `default_dynclk=-2,-1,0,1`, `ignore_devlist`, and `force_sleep`; suspend/resume, hibernate/restore, and freeze/thaw; D2-capable mobility chips; D3-cold reinit paths for M10/M11 and M9+ where hardware is available; resume after simulated power loss; console-lock early resume behavior; LVDS panel blank and unblank after resume; framebuffer content and cmap restoration; accelerator reset/init after resume; and logs for dynamic clock enable/disable and workaround detection. Static validation should verify every `save_regs` index is intentionally assigned and read for the target family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeon_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeonfb.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeonfb.h

## Purpose

`radeonfb.h` is the private interface for the Radeon fbdev driver family. It defines chip families, feature and errata flags, monitor/DDC/connector enums, PLL/panel/mode register state structures, the central `struct radeonfb_info`, MMIO/PLL/BIOS access macros, inline utility functions, engine helper macros, and cross-file function prototypes. It is the contract shared by `radeon_base.c`, `radeon_monitor.c`, `radeon_i2c.c`, `radeon_pm.c`, acceleration code, and optional backlight code.

## Important APIs, Types, And Functions

`enum radeon_family` identifies supported Radeon generations from original Radeon through RV/R/R/RS families up to R420/RS480. `IS_RV100_VARIANT()` and `IS_R300_VARIANT()` group family behavior. `enum radeon_chip_flags` defines driver-data bits for mobility, IGP, CRTC2, and family masking. `enum radeon_errata` describes PLL dummy read, PLL delay, and R300 clock-gating quirks. `enum radeon_montype`, `enum ddc_type`, and `enum conn_type` define monitor, DDC port, and connector vocabulary.

`struct pll_info` stores clock bounds and reference/system/memory clocks. `struct radeon_regs` is the large register snapshot and programmed-mode record, covering common registers, surface registers, CRTC1/CRTC2, flat-panel/LVDS/TMDS, PLLs, computed PLL values, and palette validity. `struct panel_info` stores native flat-panel timing, sync polarity, power delay, and BIOS PLL dividers. Optional `struct radeon_i2c_chan` wraps a bit-banged I2C adapter. `enum radeon_pm_mode` declares no PM, D2, and D3-cold/off resume capability. `struct radeonfb_info` ties all runtime state together.

The macros `INREG*`, `OUTREG*`, `OUTREGP`, `INPLL`, `OUTPLL`, `OUTPLLP`, and `BIOS_IN*` are central to all implementation files. Inline helpers include `round_div()`, `var_to_depth()`, and `radeon_get_dstbpp()`. The header declares exported functions for I2C, PM, monitor probing, acceleration, blanking/mode writing, and backlight.

## Control Flow

This header has no runtime control flow by itself, but it shapes every code path. `radeon_base.c` allocates `struct radeonfb_info` as fbdev private data and progressively fills fields during PCI probe. Monitor probing writes monitor and panel fields; mode setting writes `state`, pitch, bpp, depth, palette, and timer fields; PM reads and writes `save_regs`, `dynclk`, `pm_mode`, `reinit_func`, `asleep`, and `lock_blank`; I2C code fills `i2c[4]` when configured. The access macros assume each function has a local variable named `rinfo`, so callers are constrained to that naming convention.

## State And Persistence

The header defines all important in-memory persistence for the driver. `struct radeonfb_info` retains hardware mappings, PCI device pointer, optional OF node, BIOS mapping pointer, framebuffer aperture layout, chip identity, VRAM characteristics, current and initial register snapshots, monitor/EDID state, panel timing, PLL information, write-combining cookie, PM mode, and delayed LVDS timer state. None of this is persistent across module unload; it is reconstructed on probe. `struct radeon_regs` is the main persistence unit used across mode switches and resume.

## Dependencies And Integration Points

Dependencies include Linux module/kernel/scheduler/delay/PCI/fb headers, optional I2C headers, architecture I/O, SPARC prom when enabled, and `<video/radeon.h>`. All companion files include this header. External consumers are limited because the header is local to the driver directory, but its function prototypes bind the Radeon fbdev submodules together and allow `radeon_base.c` to assemble `fb_ops` from acceleration and PM helpers.

## Risks

The register and PLL macros are convenience-oriented and depend on a local `rinfo` symbol, which makes misuse easy during refactoring. PLL access comments explicitly state that locking was intentionally removed and relies on fbdev/console serialization rather than internal locking; any new caller from IRQ or concurrent context would be dangerous. `BIOS_IN*` macros assume `rinfo->bios_seg` is valid and do not bounds-check offsets. `struct radeon_regs` includes fields not always saved or programmed by every path, so additions require careful synchronization with save/restore and PM code. `save_regs[100]` is opaque and should ideally be replaced with named fields before broad changes.

## Test Signals

Header-level validation is mostly compile and integration coverage: build with and without `CONFIG_FB_RADEON_I2C`, `CONFIG_FB_RADEON_PM`, `CONFIG_FB_RADEON_BACKLIGHT`, PPC, SPARC, and big-endian options; ensure every prototype has exactly one matching implementation under the relevant config; run sparse or Coccinelle checks for invalid `__iomem` access; and verify all MMIO/PLL macro users have a local `rinfo`. Runtime signals include successful mode set, blank, I2C, PM, and acceleration paths because they all depend on this shared contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeonfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/au1100fb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/au1100fb.c

## Purpose

`au1100fb.c` is a platform fbdev driver for the Au1100 LCD controller. It supports a fixed table of known LCD/CRT-style panels, allocates coherent framebuffer memory, programs memory-mapped LCD controller registers, exposes fbdev operations for blanking, palette updates, panning, and mmap, and handles platform probe/remove plus optional suspend/resume. Unlike the Radeon files, this is a self-contained SoC display controller driver rather than a PCI graphics adapter driver.

## Important APIs, Types, And Functions

`struct au1100fb_panel` describes a supported panel: name, base LCD control bits, base clock control, horizontal/vertical timing registers, native resolution, and maximum bpp. `struct au1100fb_regs` models the LCD controller register block, including control, interrupt, timing, clock, DMA address, word count, PWM, and 256 palette entries. `struct au1100fb_device` embeds `struct fb_info`, selected panel pointer, mapped register pointer, optional PM register snapshot, coherent framebuffer memory, panel index, clock pointer, and device pointer.

The static `known_lcd_panels[]` table contains panel definitions such as `CRT_800x600_16`, `WWPC LCD`, `Sharp_LQ038Q5DR01`, `Hitachi_SP14Qxxx`, `TFT_640x480_16`, and `PrimeView_640x480_16`. Helper macros decode panel type flags. The fbdev operations are `au1100fb_fb_blank()`, `au1100fb_fb_setcolreg()`, `au1100fb_fb_pan_display()`, and `au1100fb_fb_mmap()`. Hardware setup is centralized in `au1100fb_setmode()`. Driver lifecycle is `au1100fb_setup()`, `au1100fb_drv_probe()`, `au1100fb_drv_remove()`, optional `au1100fb_drv_suspend()`, optional `au1100fb_drv_resume()`, and `module_platform_driver(au1100fb_driver)`.

## Control Flow

Probe allocates `struct au1100fb_device` with devm, parses the boot option `au1100fb=panel:<name>` through `fb_get_options()`, stores platform drvdata, retrieves the memory resource, initializes fixed fb metadata, requests the MMIO region, maps registers through `KSEG1ADDR()`, optionally enables the `lcd_intclk` clock at 48 MHz, allocates coherent framebuffer memory sized as panel xres * yres * bytes per pixel * four buffers, fills `fix.smem_*`, initializes `var` from the selected panel, assigns screen base, fbops, and pseudo-palette, allocates a 256-entry cmap, calls `au1100fb_setmode()` to program hardware, then registers the framebuffer.

`au1100fb_setmode()` derives color bitfields and visual type from the panel and bpp, updates line length and screen size, computes rotation from scan-mode bits, writes control/timing/clock/interrupt/DMA registers, sets a second DMA address for dual panels when virtual height allows split display, computes the LCD word count, clears PWM, enables `LCD_CONTROL_GO`, delays, and unblanks. Blanking just toggles `LCD_CONTROL_GO`. Palette updates support truecolor pseudo-palette, active TFT RGB565 palette entries, color STN packed 4-bit components, and monochrome intensity. Panning rejects x panning and adjusts the DMA base by the y delta. Mmap uses `dma_mmap_coherent()` and tweaks page protection for the MIPS streaming CCA path.

Remove blanks conditionally, clears `LCD_CONTROL_GO`, unregisters fbdev, frees cmap, and disables/releases the clock. Suspend blanks, disables the clock, and copies live registers into `pm_regs`. Resume copies `pm_regs` back, enables the clock, and unblanks.

## State And Persistence

The active panel selection, framebuffer memory, register pointer, clock, and fbdev state live in `struct au1100fb_device` stored as platform driver data. The register block is hardware state; in PM builds it is snapshotted into `pm_regs` across suspend. Framebuffer memory is coherent DMA memory and remains owned by devm/dmam until device removal. User-selected panel identity comes from boot options and is not persisted elsewhere.

## Dependencies And Integration Points

The driver depends on platform-device resources, fbdev core, Linux clock APIs, DMA coherent allocation/mmap, MIPS address-space behavior through `KSEG1ADDR()`, and LCD register constants from platform headers such as `AU1100_LCD_BASE`. It registers as a platform driver named `au1100-lcd`, while boot options are looked up under `DRIVER_NAME` (`au1100fb`). User space interacts through the standard framebuffer device, mmap, panning, blanking, and color-map ioctls.

## Risks

`au1100fb_setup()` returns `-ENODEV` when no options are supplied, so probe requires an explicit panel option instead of defaulting safely. If probe fails after `fb_alloc_cmap()` or after clock enable in some intermediate returns, cleanup is inconsistent because several early `return` paths bypass the common `failed` label. Register access via `KSEG1ADDR()` bypasses `ioremap()` and is architecture-specific; compile-test stubbing does not prove runtime mapping correctness. `au1100fb_fb_pan_display()` appears to write the adjusted dual-panel second DMA address back to `lcd_dmaaddr0` rather than `lcd_dmaaddr1`, which is suspicious for dual-panel panning. Suspend calls `clk_disable(fbdev->lcdclk)` without checking whether `lcdclk` is non-NULL, while probe treats the clock as optional. The register snapshot copies the full modeled register block including palette, which may be large but straightforward.

## Test Signals

Useful tests include platform probe with each supported `panel:` option, no-option probe behavior, unsupported panel rejection, clock-present and clock-absent cases, cmap allocation failure, register resource failure, coherent DMA allocation failure, framebuffer registration failure cleanup, palette programming in truecolor/pseudocolor/STN/mono modes, y panning and x-panning rejection, dual-panel DMA programming, mmap from user space, blank/unblank toggling of `LCD_CONTROL_GO`, and suspend/resume with register and framebuffer contents preserved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/au1100fb.c -->
