# Research Report: subset-b-005566

This grouped report covers the OMAP framebuffer and OMAP2 DSS display files assigned to `subset-b-005566`. Each source file has its own marked section so the reconciliation lane can split the report into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/hwa742.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/hwa742.c

## Purpose
`hwa742.c` implements the Epson HWA742 external LCD controller as an `lcd_ctrl` for the legacy OMAP1 fbdev stack. It sits above the internal LCD controller and an external interface (`lcd_ctrl_extif`, normally SoSSI), providing manual-update and auto-update behavior for RGB565/YUV windows, pixel doubling, and tearing synchronization.

## Important APIs, Types, And Functions
- `struct hwa742_request` models queued update/sync work with a handler, completion callback, and either window parameters or a completion pointer.
- The global `hwa742` state stores update mode, timer state, fixed request pool, extif timings, cached format flags, transfer limits, controller pointers, and the `hwa_sys_ck` clock.
- Register helpers `hwa742_read_reg()`, `hwa742_write_reg()`, `set_window_regs()`, and `set_format_regs()` program the external controller over the extif command/data bus.
- Update flow is handled by `create_req_list()`, `submit_req_list()`, `process_pending_requests()`, `send_frame_handler()`, and `request_complete()`.
- Public controller operations are exposed through `hwa742_ctrl`: `init`, `cleanup`, `bind_client`, `get_caps`, update-mode control, plane setup/enabling, `update_window`, `sync`, suspend, and resume.

## Control Flow
Initialization requires an OMAP fbdev device with both an internal controller and extif. `hwa742_init()` initializes the internal controller in external mode, initializes the extif, derives extif timings first from the external clock and then from the HWA742 system clock, validates revision and bootloader PLL state, configures tearing sync, initializes the request pool, and prepares the auto-update timer.

Manual updates call `hwa742_update_window_async()`, validate update mode and format flags, split odd or too-large regions into request-list entries, and submit the list. Each request programs format/window registers, optionally enables TE, asks the internal LCDC to point its plane at the window offset, switches the extif to 16-bit transfers, and starts `extif->transfer_area()`. Completion disables the internal plane and schedules the next pending request. Auto update uses the same path from a timer, with the final request callback rearming the timer.

Update-mode changes first notify manual clients or stop the auto timer for the old mode, enqueue a sync request to drain in-flight work, then notify clients or start auto update for the new mode. Suspend saves the prior mode, disables updates, puts the controller in sleep, and disables the system clock; resume reverses this and waits for PLL stabilization.

## State And Persistence
State is in static memory only: no persistent storage. The request pool is fixed-size, with a semaphore reserving `IRQ_REQ_POOL_SIZE` entries for IRQ/timer contexts. Cached fields (`prev_color_mode`, `prev_flags`, `window_type`) avoid redundant register writes. `stop_auto_update`, timer state, and `update_mode_before_suspend` govern lifecycle transitions.

## Dependencies And Integration Points
This file depends on `omapfb.h` contracts, the legacy internal LCD controller, the SoSSI/extif implementation, OMAP fbdev update window formats, kernel timers, semaphores, spinlocks, completions, and clocks. It integrates with notifier clients through `omapfb_notify_clients()` and with panel timing by reading `fbdev->panel`.

## Risks
The request queue is manually managed and uses `BUG_ON()` for pool exhaustion and invalid formats. Timing math assumes bootloader-initialized PLL state and valid HWA742 register contents. Split-window logic relies on transmit-size limits and can create zero-height requests if max transmit size is smaller than a line. TE decisions use integer timing approximations and may underflow or choose the wrong sync mode on unusual panels. Error recovery is limited; failed extif transfers are not retried.

## Test Signals
Useful signals include successful probe logs with revision/CNF pins, visible manual `OMAPFB_UPDATE_WINDOW` updates, auto-update timer refreshes, notifier READY/DISABLED delivery, suspend/resume with restored mode, and no stale request completion hangs under repeated small-window and TE-enabled updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/hwa742.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcd_ams_delta.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcd_ams_delta.c

## Purpose
`lcd_ams_delta.c` provides the legacy OMAP framebuffer panel description and LCD class hooks for the Amstrad E3/Delta videophone panel.

## Important APIs, Types, And Functions
- `ams_delta_panel` is the `struct lcd_panel` registered with omapfb. It defines a 480x320, 12-bpp, 16-data-line STN-style panel with timing fields and GPIO enable/disable callbacks.
- `ams_delta_lcd_set_power()` and `ams_delta_lcd_set_contrast()` manipulate OMAP PWL registers for LCD power/contrast.
- When `CONFIG_LCD_CLASS_DEVICE` is enabled, `ams_delta_lcd_ops` exposes power and contrast via the LCD class.
- `ams_delta_panel_probe()` acquires `vblen` and `ndisp` GPIOs, optionally registers an LCD class device, initializes contrast and power, then registers the panel.

## Control Flow
The platform driver probe obtains two GPIO descriptors, registers the optional LCD class device, writes default contrast and power-on state to the PWL hardware, and calls `omapfb_register_panel()`. Panel enable asserts NDISP and VBLEN; disable deasserts them in reverse order.

## State And Persistence
Static `ams_delta_lcd` stores current contrast in the low byte and a power flag in bit `AMS_DELTA_LCD_POWER`. GPIO descriptors are global static pointers. No state persists across reboot or module unload.

## Dependencies And Integration Points
The file depends on OMAP1 PWL register access through `omap_writeb()`, gpiod descriptors, the LCD class, and the legacy `omapfb_register_panel()` handshake. The timing fields are consumed by `lcdc.c` during controller setup.

## Risks
Power and contrast state are global and not protected by a lock. `ams_delta_lcd_set_contrast()` silently ignores out-of-range values but still returns success. There is no remove path to unregister the optional LCD class device. Hardware register writes assume OMAP1 Delta-specific PWL semantics.

## Test Signals
Probe should register an `omapfb` LCD class device when configured, expose contrast/power controls, and produce visible panel enable/disable behavior through the VBLEN/NDISP GPIOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcd_ams_delta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcd_dma.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcd_dma.c

## Purpose
`lcd_dma.c` implements OMAP1 LCD DMA setup and control helpers used by the legacy LCDC and external-controller paths. It configures framebuffer source addresses, rotation/mirroring/virtual stride/scaling transforms, and starts/stops the dedicated LCD DMA channel.

## Important APIs, Types, And Functions
- `struct lcd_dma_info lcd_dma` stores reservation state, callback, active flag, framebuffer geometry, transform parameters, external-controller mode, and single-transfer mode.
- Exported setters include `omap_set_lcd_dma_b1()`, `_rotation()`, `_mirror()`, `_vxres()`, `_scale()`, `_ext_controller()`, and `_single_transfer()`.
- `set_b1_regs()` computes top/bottom addresses, element/frame indexes, and register values for OMAP1510 or OMAP1610 LCD DMA.
- `omap_request_lcd_dma()` and `omap_free_lcd_dma()` reserve/release the singleton LCD DMA path.
- `omap_setup_lcd_dma()`, `omap_enable_lcd_dma()`, and `omap_stop_lcd_dma()` program and control the hardware.
- `lcd_dma_irq_handler()` acknowledges OMAP1610 block interrupts and invokes the registered callback.

## Control Flow
Clients reserve the LCD DMA channel, set framebuffer geometry and optional transforms, then call `omap_setup_lcd_dma()`. Setup writes reasonable OMAP1610 defaults, calls `set_b1_regs()`, and programs end-prog/autoinit/repeat bits unless single-transfer mode is active. Internal LCDC mode relies on controller enable to trigger transfers; external controller mode explicitly sets enable bits in `omap_enable_lcd_dma()`. The IRQ handler clears the block interrupt, marks DMA inactive, and calls the client callback.

## State And Persistence
All state is static and singleton. The driver records only the latest B1 plane parameters. The `reserved` flag is protected by a spinlock, but most geometry setters write without locking and assume serialized controller use.

## Dependencies And Integration Points
The file depends on OMAP1 CPU-detection helpers, OMAP DMA register definitions, OMAP1 IO accessors, LCDC register definitions, and `INT_DMA_LCD`. It is consumed by `lcdc.c` and external bus drivers such as `sossi.c`.

## Risks
Unsupported operations on OMAP1510 call `BUG()`. Address and stride math is sensitive to element size, rotation, mirror, virtual xres, and scaling; bad parameters can program invalid DMA windows. `omap_request_lcd_dma()` calls `BUG()` when already reserved, which turns a caller bug into a kernel crash. There is no locking around active state or most configuration fields, so callers must serialize setup and enable.

## Test Signals
Exercise RGB565/CLUT modes with no transform, mirror, and 90/180/270 rotation on OMAP1610. Confirm OMAP1510 rejects transforms, external mode receives DMA completion callbacks, and `omap_lcd_dma_running()` matches hardware state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcd_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcd_dma.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcd_dma.h

## Purpose
`lcd_dma.h` defines OMAP1510/OMAP1610 LCD DMA register addresses, LCD DMA block identifiers, and the exported LCD DMA helper API used by the OMAP1 fbdev controller stack.

## Important APIs, Types, And Functions
- Register macros cover OMAP1510 LCD control/top/bottom registers and OMAP1610 LCD CSDP/CCR/CTRL/top/bottom/source-index/lch-control registers.
- The enum identifies the four OMAP1610 LCD DMA block slots: B1 top/bottom and B2 top/bottom.
- Function declarations expose reservation, setup, enable/stop, external-controller and single-transfer mode, B1 geometry, rotation, virtual stride, mirror, and scaling.

## Control Flow
The header has no executable flow. It establishes the contract used by `lcdc.c`, `sossi.c`, and any other legacy OMAP1 LCD DMA client.

## State And Persistence
No state is defined here. State lives in `lcd_dma.c`.

## Dependencies And Integration Points
This header is tightly coupled to OMAP1 physical register layout and to `linux/omap-dma.h` data-type constants used by callers.

## Risks
The hard-coded physical addresses make the API OMAP1-specific. Callers must respect unsupported OMAP1510 transform constraints enforced in the implementation. There is no type-safe geometry object, so callers can mix pixel and DMA-element dimensions incorrectly.

## Test Signals
Compile-time coverage is the main signal: all legacy OMAP LCDC and SoSSI code should build against these declarations without duplicate register definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcd_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcd_mipid.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcd_mipid.c

## Purpose
`lcd_mipid.c` is a SPI-driven panel driver for MIPI DBI-C/DCS-compatible LCDs in the legacy OMAP fbdev stack. It detects supported panels, registers a `struct lcd_panel`, controls sleep/display/backlight state, performs ESD checks for LS041Y3, and supports a framebuffer-to-panel RGB interface test.

## Important APIs, Types, And Functions
- `struct mipid_device` stores SPI device, reset GPIO, embedded `lcd_panel`, fbdev pointer, guard timing, enabled state, saved backlight level, and delayed ESD work.
- `mipid_transfer()` builds 9-bit SPI command/data/read transactions.
- DCS helpers `mipid_cmd()`, `mipid_write()`, and `mipid_read()` wrap panel access.
- Power/display flow uses `set_sleep_mode()`, `set_display_state()`, `mipid_enable()`, and `mipid_disable()`.
- Backlight methods forward to `struct mipid_platform_data` callbacks.
- `mipid_run_test()` writes the first fb pixel through omapfb and reads panel RGB registers.
- `mipid_detect()` reads display ID and selects `lph8923` or `ls041y3`; `mipid_spi_probe()` allocates, requests reset GPIO, detects, and registers the panel.

## Control Flow
Probe allocates `mipid_device`, deasserts reset through the reset GPIO, sets SPI mode, copies default panel timings, detects the panel over DCS, then calls `omapfb_register_panel()`. During omapfb panel initialization, `mipid_init()` records the fbdev, initializes work and mutexes, reads whether the bootloader already enabled the panel, and starts ESD monitoring or saves current brightness. Enable exits sleep, sends init commands and data-line format, turns display on, restores brightness, and starts ESD checks. Disable cancels ESD work, saves brightness, turns backlight/display off, enters sleep, and marks disabled.

## State And Persistence
Runtime state is per SPI device. `hw_guard_end` and `hw_guard_wait` enforce DCS sleep-in/out spacing. `saved_bklight_level` preserves desired brightness while disabled. Delayed work periodically performs ESD validation only while enabled. No persistent storage is used.

## Dependencies And Integration Points
The driver depends on SPI, GPIO descriptors, platform data from `linux/platform_data/lcd-mipid.h`, delayed work, and legacy omapfb panel registration. It calls `omapfb_write_first_pixel()` for diagnostics and uses panel timing fields consumed by `lcdc.c`.

## Risks
`mipid_spi_probe()` leaks the allocated `mipid_device` if reset GPIO acquisition fails because it returns directly. SPI transfer read handling assumes panel-specific 9-bit protocol quirks. Backlight platform callbacks are optional but not consistently checked by all call paths. ESD recovery performs sleep transitions under the mutex and may disturb active updates. `set_data_lines()` has no default error path before writing `par`.

## Test Signals
Expected signals include successful display ID log, correct panel name/revision/data-line reporting, sleep/display/backlight transitions, stable delayed ESD work, and a passing `MIPID_TEST_RGB_LINES` test that writes and reads known first-pixel values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcd_mipid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcd_palmte.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcd_palmte.c

## Purpose
`lcd_palmte.c` registers the legacy omapfb panel description for the Palm Tungsten E.

## Important APIs, Types, And Functions
- `palmte_panel` is a static `struct lcd_panel` with TFT configuration, sync polarity flags, 16 data lines, 8 bpp, 320x320 resolution, 12 MHz pixel clock, and porch/sync timings.
- `palmte_panel_probe()` simply calls `omapfb_register_panel()`.

## Control Flow
The platform driver probe registers the static panel. All actual LCDC configuration, framebuffer allocation, and enable/disable behavior is handled by the common OMAP1 fbdev code.

## State And Persistence
There is no mutable state in this file beyond driver registration.

## Dependencies And Integration Points
The panel timings and signal flags are consumed by `lcdc.c`. The driver relies on a platform device named `lcd_palmte` and the `omapfb_register_panel()` handshake.

## Risks
There are no power, reset, or backlight hooks, so board-specific sequencing must exist elsewhere or the panel must already be powered. The hard-coded timing fields are not validated until common controller setup.

## Test Signals
Probe should result in omapfb selecting panel `palmte`, programming 320x320 TFT timings, and creating a usable 8-bpp framebuffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcd_palmte.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcdc.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcdc.c

## Purpose
`lcdc.c` implements the OMAP1 internal LCD controller as the `omap1_int_ctrl` backend for the legacy omapfb driver. It programs LCDC timing/control registers, allocates framebuffer and palette DMA memory, configures LCD DMA, handles palette loads, reset-on-error interrupts, update mode, and suspend/resume.

## Important APIs, Types, And Functions
- `struct omap_lcd_controller lcdc` stores update mode, external-mode flag, active plane geometry, color mode, palette memory, IRQ mask/completions, clock, fbdev pointer, DMA callback, and allocated VRAM.
- Register helpers include `set_load_mode()`, `enable_controller()`, `disable_controller_async()`, `disable_controller()`, and `reset_controller()`.
- `setup_lcd_dma()` converts fbdev var/plane state into LCD DMA B1 geometry, data type, stride, rotation, and mirror settings.
- `lcdc_irq_handler()` handles DONE, LOADED_PALETTE, FIFO underflow, and sync-lost status.
- Plane/update APIs include `omap_lcdc_setup_plane()`, `omap_lcdc_enable_plane()`, `omap_lcdc_set_update_mode()`, `omap_lcdc_setcolreg()`, suspend/resume, and DMA callback registration.
- `omap_lcdc_init()` and `omap_lcdc_cleanup()` own clock, IRQ, LCD DMA, palette memory, and framebuffer memory resources.

## Control Flow
Initialization clears LCDC control, obtains `lcd_ck`, derives its rate from `tc_ck` with an AMS Delta adjustment, enables the clock, requests the LCDC IRQ, reserves LCD DMA, configures single-transfer/external mode, optionally allocates palette RAM, and allocates framebuffer DMA memory. Internal mode then uses `omap_lcdc_set_update_mode(OMAPFB_AUTO_UPDATE)` to program panel timings, load palette, set up frame DMA, choose frame load mode, enable DONE IRQs, and enable the LCD controller. External mode skips palette/controller auto-update and uses `setup_lcd_dma()` for single transfer windows driven by an external controller.

Plane setup validates only plane 0/channel 0 at position 0, clamps against rotated panel size, stores offset/width/screen width/color mode, maps color mode to bpp/palette code, and either sets up external DMA immediately or, in auto-update internal mode, disables the controller, stops DMA, reprograms DMA, and reenables the controller. Palette update configures LCD DMA to copy palette RAM and waits for `LOADED_PALETTE`.

## State And Persistence
All state is static singleton state for one OMAP1 LCD controller. `last_frame_complete` and `palette_load_complete` serialize disable/palette operations against IRQs. The controller owns allocated WC DMA memory for both palette and framebuffer until cleanup.

## Dependencies And Integration Points
The file depends on OMAP1 IO accessors, OMAP1 CPU/machine checks, clocks, DMA allocation, LCD DMA helpers, fbdev types, and `struct lcd_panel` timing fields. It is selected by `omapfb_main.c` as the internal controller and is also used in external mode by HWA742/SoSSI.

## Risks
Several invalid input paths call `BUG()`. The reset logic gives up after repeated FIFO underflow/sync-lost events but leaves limited diagnostics. Palette load and disable waits have 500 ms timeouts but continue after logging errors. `free_fbmem()` and `free_palette_ram()` assume allocation succeeded. Register programming uses many panel fields directly and can underflow if timing values are zero where hardware expects `value - 1`.

## Test Signals
Key signals include successful clock/IRQ/DMA allocation, correct mode logs from omapfb, visible auto-update display, CLUT palette writes, DONE and LOADED_PALETTE completions, recoverable FIFO underflow/sync-lost logging, suspend/resume blanking, and external-mode DMA callbacks through SoSSI/HWA742.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcdc.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcdc.h

## Purpose
`lcdc.h` defines OMAP1 LCDC register addresses, status/control/IRQ bit masks, and the small callback API shared between the internal LCD controller and external interfaces.

## Important APIs, Types, And Functions
- Register macros define LCDC base, size, IRQ, and offsets for control, timing, status, subpanel, line interrupt, and display status.
- Status bits include DONE, VSYNC, SYNC_LOST, ABC, LINE_INT, FIFO underflow, and LOADED_PALETTE.
- Control/IRQ masks include LCD enable, TFT mode, IRQ mask fields, and DONE/VSYNC/line/palette interrupt bits.
- `omap_lcdc_set_dma_callback()` and `omap_lcdc_free_dma_callback()` let an external interface receive LCD DMA completion notification.
- `omap1_int_ctrl` is declared as the internal controller object.

## Control Flow
The header has no runtime control flow. It defines hardware constants and cross-file declarations used by `lcdc.c`, `lcd_dma.c`, and `sossi.c`.

## State And Persistence
No state is stored in this header.

## Dependencies And Integration Points
The header expects OMAP1 interrupt naming (`INT_LCD_CTRL`) and the `struct lcd_ctrl` type from `omapfb.h`.

## Risks
Hard-coded addresses and bit positions are OMAP1-specific. Any register definition drift would affect low-level DMA/controller behavior across multiple files.

## Test Signals
Compile coverage plus successful LCDC interrupt handling are the primary signals that these definitions match the target platform.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcdc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/omapfb.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/omapfb.h

## Purpose
`omapfb.h` is the private interface for the legacy OMAP1 framebuffer driver. It defines panel, external interface, controller, memory, plane, notifier, and device structures used across `omapfb_main.c`, `lcdc.c`, HWA742, SoSSI, and panel drivers.

## Important APIs, Types, And Functions
- `struct lcd_panel` describes board/panel timing, format, lifecycle hooks, backlight hooks, capability hooks, and diagnostics.
- `struct lcd_ctrl_extif` abstracts an external bus for register/data transfers, timing conversion, transfer-area DMA, and tear-sync.
- `struct lcd_ctrl` abstracts a display controller backend with init/cleanup, caps, update mode, plane/memory setup, mmap, scale/rotation, update window, sync, PM, test, palette, and color-key methods.
- `struct omapfb_device` ties together panel, controller, extif, IRQs, state, memory descriptor, fb_info array, palette, and a dummy DSS clock device.
- Notifier APIs allow clients to register for READY/DISABLED events.

## Control Flow
The header establishes function-pointer contracts. Runtime flow is provided by implementations that fill `struct lcd_ctrl`, `struct lcd_ctrl_extif`, and `struct lcd_panel`.

## State And Persistence
No concrete state is allocated here, but the structures define all major runtime state boundaries for the OMAP1 fbdev stack. State is process-local kernel memory and not persistent.

## Dependencies And Integration Points
It depends on kernel fbdev types, mutexes, and public OMAP fbdev UAPI types in `linux/omapfb.h`. It is the integration contract between board panel drivers, internal/external controller drivers, and `omapfb_main.c`.

## Risks
The single-plane assumption is encoded as `OMAPFB_PLANE_NUM 1`. Several callbacks are optional, so callers must guard null pointers. The function-pointer API predates modern DRM/component conventions and relies heavily on platform data and global registration order.

## Test Signals
Build success across all legacy OMAP fbdev files, correct panel/controller registration, and notifier/client behavior validate this private API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/omapfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/omapfb_main.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/omapfb_main.c

## Purpose
`omapfb_main.c` is the legacy OMAP1 framebuffer driver entrypoint. It binds platform device and panel registration, selects a controller, allocates framebuffer planes, exposes fbdev operations and OMAPFB ioctls, manages sysfs attributes, and handles suspend/resume/cleanup.

## Important APIs, Types, And Functions
- Module parameters/boot options set acceleration, VRAM sizes, virtual resolution, rotation, mirror, and manual-update default.
- `ctrl_init()`, `ctrl_cleanup()`, and `ctrl_change_mode()` mediate controller setup and plane reconfiguration.
- fbdev callbacks include open/release, blank, sync, check_var, set_par, pan_display, setcolreg/setcmap, ioctl, and optional mmap.
- OMAPFB ioctls handle mirror, sync, update mode, update window, plane setup/query, memory setup/query, color key, capabilities, and LCD/controller tests.
- Notifier APIs `omapfb_register_client()`, `omapfb_unregister_client()`, and `omapfb_notify_clients()` are exported.
- Probe flow is split between `omapfb_probe()`, `omapfb_register_panel()`, and `omapfb_do_probe()`.

## Control Flow
The platform driver registers a dummy `omapdss_dss` device for clocks, stores the platform device, and waits until a panel driver calls `omapfb_register_panel()`. Once both sides are present, `omapfb_do_probe()` validates platform data/resources, allocates `omapfb_device`, gets internal/external IRQs, selects the requested controller, initializes the panel, determines default virtual resolution and VRAM, initializes the controller, creates fb_info planes, sets DMA priority if configured, applies the first plane mode, enables the plane, sets auto/manual update mode, enables the panel, registers sysfs attributes, and registers each framebuffer.

`set_fb_var()` normalizes user mode requests against panel size, rotation, memory size, bpp/color mode, offsets, and timing fields. `ctrl_change_mode()` syncs pending controller work, computes the framebuffer offset from x/y offsets, calls controller `setup_plane()`, then applies optional rotate/scale. Manual updates validate/clamp windows and forward them only when the controller is in manual mode. Blank and PM use panel enable/disable plus controller suspend/resume.

## State And Persistence
The driver uses globals for the pending platform device, registered panel, and current fbdev singleton. Per-device state is in `omapfb_device`, with `rqueue_mutex` serializing controller operations and ioctl/fbdev transitions. Module parameters persist only for module lifetime.

## Dependencies And Integration Points
The file depends on Linux fbdev core, platform bus, sysfs, user-copy helpers, OMAP DMA priority APIs, OMAP1 CPU checks, private `omapfb.h`, and controller/panel registration. It is the primary consumer of `lcd_ctrl` and `lcd_panel` callbacks.

## Risks
Singleton global registration means only one panel/platform pairing is supported and `BUG_ON()` is used for duplicates. Some ioctl cases ignore return values, such as `OMAPFB_MIRROR` not assigning the helper result. Cleanup relies on numeric init-state fallthrough and assumes resources match that state. `set_fb_var()` adjusts user input in place and has many geometry/bpp edge cases. Manual update paths depend on controller-specific async completion. Remove has a FIXME for pending events.

## Test Signals
Signals include successful `/dev/fb*` registration, sysfs `caps_*`, `panel/name`, and `ctrl/name`, ioctl coverage for update mode/window/plane/memory, pan/display offset changes, blank/suspend/resume, first-pixel LCD test, and clean resource rollback on injected probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/omapfb_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/sossi.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/sossi.c

## Purpose
`sossi.c` implements the OMAP1 Special OptimiSed Screen Interface as a `lcd_ctrl_extif`. It provides the external command/data bus used by HWA742-style controllers, converts extif timings, performs FIFO command/data reads and writes, coordinates tear-sync, and starts LCD DMA transfers.

## Important APIs, Types, And Functions
- The static `sossi` state stores MMIO base, clocks, bus width/count, TE mode/line, LCDC completion callback, timing cache, fbdev pointer, and pending-vsync count.
- Timing functions `calc_rd_timings()`, `calc_wr_timings()`, `sossi_convert_timings()`, and `sossi_set_timings()` convert generic picosecond extif timings to SoSSI `TW0/TW1/div` register values.
- Transfer helpers include `sossi_write_command()`, `sossi_write_data()`, `sossi_read_data()`, and `sossi_transfer_area()`.
- `sossi_setup_tearsync()` and `sossi_enable_tearsync()` configure pulse widths and deferred TE mode.
- `sossi_dma_callback()` completes transfer-area operations after LCD DMA completion; `sossi_match_irq()` starts DMA on TE match when needed.
- `omap1_ext_if` exposes the extif method table.

## Control Flow
Initialization ioremaps SoSSI, obtains parent and functional clocks, resets/enables the SoSSI module, validates sync pattern reads, registers an LCDC DMA callback, enables DMA mode, and requests the external TE/match IRQ. HWA742 calls timing conversion/set functions, sets 8- or 16-bit cycles, writes commands/register data, and requests `transfer_area()`. A transfer programs write timing, bus width, TE mode, data cycles, and starts the external bus cycle. If TE is active, it increments `vsync_dma_pending` and waits for `sossi_match_irq()` to call `omap_enable_lcd_dma()`; otherwise it starts DMA immediately. LCD DMA completion stops DMA, stops the SoSSI transfer, disables the clock, and calls the HWA742 completion callback.

## State And Persistence
State is singleton static memory. `last_access` caches read/write timing programming, and `vsync_dma_pending` is protected by a spinlock. No persistent storage is used.

## Dependencies And Integration Points
The file depends on OMAP1 IO registers, SoSSI MMIO, clocks, IRQs, LCD DMA helpers, LCDC DMA callback API, and the `lcd_ctrl_extif` contract from `omapfb.h`. It is normally paired with `hwa742.c`.

## Risks
Several resource-error paths in `sossi_init()` return without undoing earlier ioremap/clock resources. `wait_end_of_write()` spins without timeout. Many hardware timing failures return `-1` rather than specific errno. The TE path depends on edge-falling IRQ wiring and manually deferred DMA start; missed IRQs can hang transfers. Pointer arithmetic on `void *` relies on compiler extensions.

## Test Signals
Expected signals include valid SoSSI sync pattern/version logs, successful extif timing conversion for HWA742, working register reads/writes, DMA completion callbacks, TE-triggered transfers without hangs, and clean disable/clock behavior around repeated manual updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/sossi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/Kconfig

## Purpose
This Kconfig file gates the OMAP2+ fbdev display stack and includes the nested omapfb Kconfig only when Open Firmware and an OMAP2+/compile-test target are available.

## Important APIs, Types, And Functions
- The top-level conditional is `if OF && (ARCH_OMAP2PLUS || COMPILE_TEST)`.
- It sources `drivers/video/fbdev/omap2/omapfb/Kconfig`.

## Control Flow
Kconfig evaluation enters the nested OMAP2 omapfb menu only under the conditional.

## State And Persistence
No runtime state. It affects build configuration.

## Dependencies And Integration Points
It integrates the OMAP2 fbdev tree into the broader kernel config system and prevents non-DT/non-OMAP builds from seeing irrelevant options except through `COMPILE_TEST`.

## Risks
Disabling `OF` hides all nested options even if source files could compile. Path correctness must match the kernel tree layout.

## Test Signals
`menuconfig` should expose OMAP2 framebuffer options on OF-capable OMAP2+ or compile-test builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/Makefile

## Purpose
This Makefile descends unconditionally into the OMAP2 omapfb subdirectory for fbdev display support.

## Important APIs, Types, And Functions
- `obj-y += omapfb/` adds the subdirectory to the build traversal.

## Control Flow
The kernel build system evaluates the nested Makefile, where actual object inclusion is controlled by configuration symbols.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
It integrates `drivers/video/fbdev/omap2/omapfb` with the parent fbdev build.

## Risks
Because descent is unconditional, nested Makefiles must correctly gate objects by config to avoid unwanted builds.

## Test Signals
Kernel build logs should enter the `omapfb/` subdirectory and include objects only when relevant configs are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/Kconfig

## Purpose
This Kconfig file defines the OMAP2+ framebuffer driver option, VRFB support symbol, debug support, framebuffer count, and includes DSS/display-driver Kconfig files.

## Important APIs, Types, And Functions
- `OMAP2_VRFB` is a helper bool selected on older OMAP2/OMAP3.
- `menuconfig FB_OMAP2` depends on `FB`, `DRM_OMAP = n`, and `GPIOLIB`; it selects `FB_OMAP2_DSS` and `FB_IOMEM_HELPERS`.
- `FB_OMAP2_DEBUG_SUPPORT` enables debug code controlled at runtime by a module parameter.
- `FB_OMAP2_NUM_FBS` chooses 1-10 fbdev framebuffers, defaulting to 3.
- It sources `dss/Kconfig` and `displays/Kconfig`.

## Control Flow
Nested options are visible only inside `if FB_OMAP2`.

## State And Persistence
No runtime state. The selected symbols determine which objects and code paths build into the kernel.

## Dependencies And Integration Points
This file coordinates fbdev OMAP2 with the DSS core, display subdrivers, GPIOLIB, and DRM mutual exclusion.

## Risks
The `DRM_OMAP = n` dependency prevents coexistence with the newer DRM OMAP driver. Display Kconfig symbols may be hidden if `FB_OMAP2` is disabled even for compile-only testing of individual panels.

## Test Signals
Config tests should verify that enabling `FB_OMAP2` selects DSS, exposes display drivers, and respects `FB_OMAP2_NUM_FBS` bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/Makefile

## Purpose
This Makefile builds the OMAP2+ fbdev core, VRFB helper, DSS subdirectory, and display subdirectory.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_OMAP2_VRFB) += vrfb.o`
- `obj-y += dss/` and `obj-y += displays/`
- `obj-$(CONFIG_FB_OMAP2) += omap2fb.o`
- `omap2fb-y := omapfb-main.o omapfb-sysfs.o omapfb-ioctl.o`

## Control Flow
The build descends into DSS and displays regardless of `FB_OMAP2`, with each nested object gated by its own config. The main fbdev object links three implementation files when `CONFIG_FB_OMAP2` is set.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
It binds Kconfig symbols to object files and links the fbdev core from multiple compilation units.

## Risks
Unconditional subdirectory descent relies on child Makefiles to avoid building disabled drivers. Adding a new core file requires updating `omap2fb-y`.

## Test Signals
Build tests should confirm `omap2fb.o` contains main/sysfs/ioctl objects and display modules are compiled only under matching config symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/Kconfig

## Purpose
This Kconfig menu defines OMAPFB panel, connector, and encoder driver options for the OMAP2 DSS fbdev stack.

## Important APIs, Types, And Functions
- The menu depends on `FB_OMAP2_DSS`.
- Encoder options include OPA362, TFP410, and TPD12S015.
- Connector options include DVI, HDMI, and analog TV; DVI depends on I2C.
- Panel options include generic DPI, generic DSI command mode, Sony ACX565AKM, LG Philips LB035Q02, Sharp LS037V7DW01, TPO panels, and NEC NL8048HL11.
- Several fbdev panel options depend on equivalent DRM panel drivers being disabled to avoid duplicate binding.

## Control Flow
These symbols control which display modules are compiled by the displays Makefile.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
The file integrates fbdev display subdrivers with DSS, I2C, SPI, backlight class, and DRM-panel mutual-exclusion symbols.

## Risks
Incorrect dependency expressions can either hide valid drivers or allow duplicate fbdev/DRM panel drivers to bind the same hardware.

## Test Signals
Config matrix checks should verify each option appears with its dependencies and maps to the expected object file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/Makefile -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/Makefile

## Purpose
This Makefile maps OMAP2 fbdev display Kconfig symbols to connector, encoder, and panel object files.

## Important APIs, Types, And Functions
- Each `obj-$(CONFIG_FB_OMAP2_...)` line builds one display module.
- It covers the files in this work item plus additional Sony/TPO panel drivers not assigned here.

## Control Flow
The kernel build includes only objects whose config symbols are enabled.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
It couples `displays/Kconfig` to actual source files and module names.

## Risks
Symbol/file mismatch would produce missing driver builds. Adding or renaming a display source requires synchronized Kconfig and Makefile edits.

## Test Signals
Build with each display option as module should produce the corresponding `.ko`/object and module alias metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/connector-analog-tv.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/connector-analog-tv.c

## Purpose
`connector-analog-tv.c` implements a generic OF-only analog TV connector display for the OMAP2 DSS fbdev stack, supporting S-video and composite connector compatibles.

## Important APIs, Types, And Functions
- `struct panel_drv_data` embeds an `omap_dss_device`, stores upstream `in`, device pointer, current timings, and polarity flag.
- `tvc_pal_timings` defines default PAL-like interlaced 720x574 timings.
- `tvc_driver` supplies connect/disconnect, enable/disable, timings, resolution, and WSS operations.
- Probe finds the upstream source via OF endpoint and registers the display as `OMAP_DISPLAY_TYPE_VENC`.

## Control Flow
Probe allocates state, finds the first endpoint source, initializes default timings, fills `dssdev`, and calls `omapdss_register_display()`. Enable requires connection, programs timings, optionally sets composite type and output polarity for non-DT use, enables upstream ATV output, and marks state active. Disable calls upstream disable and marks state disabled. Remove unregisters, disables/disconnects, and drops the source reference.

## State And Persistence
Per-device state stores current timings and connection state in the embedded DSS device. No persistent storage.

## Dependencies And Integration Points
The driver depends on OF graph helpers, OMAP DSS ATV ops, WSS get/set passthrough, and `omapdss_register_display()`.

## Risks
The probe rejects non-OF devices, while enable still has a legacy non-OF branch that is unreachable through this probe. WSS and timing operations assume `in->ops.atv` is valid. Only default PAL timings are provided.

## Test Signals
Device-tree nodes compatible with `omapdss,svideo-connector` or `omapdss,composite-video-connector` should register a VENC display, connect to the upstream source, enable with PAL timings, and pass WSS operations through.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/connector-analog-tv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/connector-dvi.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/connector-dvi.c

## Purpose
`connector-dvi.c` implements a generic OF DVI connector display for OMAP2 DSS fbdev. It forwards DVI connect/timing/enable calls and optionally performs DDC/EDID reads through an I2C adapter.

## Important APIs, Types, And Functions
- `dvic_default_timings` provides 640x480 DVI timings and signal polarity defaults.
- `struct panel_drv_data` stores DSS device, upstream source, current timings, and optional DDC I2C adapter.
- `dvic_ddc_read()` performs a DDC segment read with three retries on `-EAGAIN`.
- `dvic_read_edid()` reads base EDID and one optional extension block.
- `dvic_detect()` uses DDC if available, otherwise reports connected.
- `dvic_driver` exposes DSS display operations.

## Control Flow
Probe requires OF, allocates state, finds the upstream source, optionally resolves `ddc-i2c-bus`, initializes default timings, registers a DVI display, and cleans up references on failure. Enable requires connection, sets timings on upstream DVI ops, enables upstream output, and sets active state. Remove unregisters, disables/disconnects, drops the upstream device, and releases the I2C adapter.

## State And Persistence
Current timings and adapter/source references live in per-device memory. EDID reads are on-demand and not cached.

## Dependencies And Integration Points
The file depends on I2C, DRM EDID constants, OF graph/phandle parsing, and OMAP DSS DVI ops.

## Risks
Only one EDID extension block is read. `detect()` returns true without DDC, which may report a disconnected passive connector as present. Timing mutation is passed through to upstream ops and stored locally. Probe defers if DDC adapter is not ready.

## Test Signals
Expected signals include DVI display registration, optional successful DDC EDID reads from address `DDC_ADDR`, correct `detect()` behavior with/without DDC, and enable/disable propagation to upstream DVI output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/connector-dvi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/connector-hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/connector-hdmi.c

## Purpose
`connector-hdmi.c` implements a generic OF HDMI connector display for OMAP2 DSS fbdev. It passes HDMI operations to an upstream HDMI output and optionally uses an HPD GPIO for detection.

## Important APIs, Types, And Functions
- `hdmic_default_timings` defines default 640x480 HDMI timings.
- `struct panel_drv_data` stores DSS device, upstream source, device pointer, timings, and optional HPD GPIO.
- `hdmic_driver` implements connect/disconnect, enable/disable, timing operations, EDID, detect, HDMI/DVI mode, and AVI infoframe forwarding.

## Control Flow
Probe requires OF, requests optional `hpd` GPIO, names it, finds the upstream source endpoint, initializes timings, registers an HDMI display, and releases the source on failure. Enable requires connection, sets timings, calls upstream enable, and marks state active. Detection reads HPD GPIO if present, else forwards to upstream HDMI detect.

## State And Persistence
The driver stores current timings and optional HPD descriptor per device. No persistent state or EDID cache is kept.

## Dependencies And Integration Points
It depends on GPIO descriptors, OF graph helpers, DRM HDMI infoframe/EDID types, and OMAP DSS HDMI ops.

## Risks
If HPD GPIO polarity is wrong in DT, detection is inverted. EDID and infoframe calls assume upstream ops exist. No hotplug interrupt handling is implemented here; consumers must poll or rely on higher layers.

## Test Signals
A valid `omapdss,hdmi-connector` node should register an HDMI display, report HPD accurately, read EDID through upstream ops, set HDMI mode/infoframes, and enable/disable cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/connector-hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/encoder-opa362.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/encoder-opa362.c

## Purpose
`encoder-opa362.c` models the OPA362 analog video amplifier as an OMAP DSS ATV output. It forwards analog TV operations to an upstream VENC source and controls an optional enable GPIO.

## Important APIs, Types, And Functions
- `struct panel_drv_data` stores the output DSS device, upstream source, optional enable GPIO, and timings.
- `opa362_atv_ops` implements ATV connect/disconnect, enable/disable, timing operations, and type selection.
- `opa362_set_type()` warns unless the requested VENC type is composite.

## Control Flow
Probe requires OF, requests optional `enable` GPIO default-low, finds the upstream source, fills `dssdev` with ATV ops and VENC output type, and registers it as an output. Connect forwards to upstream ATV connect and links `dst->src`/`dssdev->dst`. Enable sets timings, enables upstream ATV, asserts enable GPIO, and marks active. Disable clears GPIO, disables upstream, and marks disabled. Remove unregisters output, warns and tears down if still enabled/connected, and drops the source reference.

## State And Persistence
Connection pointers, state, timing copy, and GPIO value are runtime-only.

## Dependencies And Integration Points
The file depends on OF graph source lookup, GPIO descriptors, and OMAP DSS ATV output registration.

## Risks
The output only supports composite semantics but cannot enforce all downstream type uses beyond a warning. Removal handles enabled/connected states defensively but relies on correct `dst` pointers. Missing optional GPIO means power control is entirely upstream/external.

## Test Signals
Enable should produce upstream VENC output plus asserted OPA362 enable GPIO. Composite connector chains should connect/disconnect without stale `src`/`dst` links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/encoder-opa362.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/encoder-tfp410.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/encoder-tfp410.c

## Purpose
`encoder-tfp410.c` represents a TFP410 DPI-to-DVI encoder as an OMAP DSS DVI output. It forwards DPI operations upstream, fixes DVI timing signal levels/edges, and controls an optional powerdown GPIO.

## Important APIs, Types, And Functions
- `struct panel_drv_data` stores DSS output, upstream DPI source, optional `pd_gpio`, data-line count, and timings.
- `tfp410_fix_timings()` forces data/sync pixel clock edges and DE active-high for the encoder.
- `tfp410_dvi_ops` exposes DVI connect/disconnect, enable/disable, timing operations.

## Control Flow
Probe requires OF, requests optional `powerdown` GPIO default-high, finds the upstream source, fills an output DSS device with DVI ops, output type DVI over DPI, and registers it. Connect links to a downstream connector and forwards to upstream DPI connect. Enable sets fixed timings and data lines upstream, enables DPI, deasserts powerdown, and marks active. Disable asserts powerdown, disables DPI, and marks disabled.

## State And Persistence
The driver stores current timings and connection state in memory only. GPIO state represents runtime hardware power state.

## Dependencies And Integration Points
It depends on GPIO descriptors, OF graph helpers, and OMAP DSS DPI/DVI ops. It is typically chained between a DPI source and a DVI connector.

## Risks
`data_lines` is never parsed in this file, so it remains zero unless populated by future changes. Timing fixups mutate caller-provided timing structures. Optional GPIO absence means no encoder powerdown control.

## Test Signals
Expected signals include successful DVI output registration, powerdown GPIO high at probe/disabled and low when enabled, fixed DVI timing polarities, and clean chaining to a DVI connector.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/encoder-tfp410.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/encoder-tpd12s015.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/encoder-tpd12s015.c

## Purpose
`encoder-tpd12s015.c` models the TPD12S015 HDMI ESD protection and level-shifter chip as an OMAP DSS HDMI output. It forwards HDMI operations upstream and controls GPIOs for charge pump/HPD, level shifter output enable, and HPD detection.

## Important APIs, Types, And Functions
- `struct panel_drv_data` stores DSS output, upstream HDMI source, `ct_cp_hpd_gpio`, `ls_oe_gpio`, `hpd_gpio`, and timings.
- `tpd_hdmi_ops` implements HDMI connect/disconnect, enable/disable, timing operations, EDID read, detect, AVI infoframe, and HDMI mode forwarding.
- `tpd_read_edid()` gates EDID reads on HPD and temporarily enables the level shifter.

## Control Flow
Probe requires OF, finds the upstream source, acquires three indexed GPIOs, fills an HDMI output DSS device, and registers it. Connect forwards upstream HDMI connect, links downstream source pointers, asserts charge-pump/HPD GPIO, and waits 300 us for 5V. Disconnect clears charge-pump GPIO, unlinks pointers, and forwards disconnect. Enable sets timings and enables upstream HDMI. EDID read returns `-ENODEV` without HPD, otherwise asserts `ls_oe_gpio`, reads upstream EDID, and deasserts it.

## State And Persistence
Per-device state is runtime-only. GPIO values carry hardware state for HPD supply/level shifting.

## Dependencies And Integration Points
The file depends on GPIO descriptors, OF graph helpers, OMAP DSS HDMI output ops, and downstream HDMI connector chaining.

## Risks
`tpd_disconnect()` calls `gpiod_set_value_cansleep()` on `ct_cp_hpd_gpio` without a null guard even though the GPIO was requested optional. Connect lacks an already-connected guard unlike other encoders. EDID depends on correct HPD polarity and upstream read behavior. Error paths share labels and release the upstream source for GPIO acquisition failures.

## Test Signals
Test HPD-driven detect, EDID read only when HPD is asserted, level-shifter GPIO toggling around EDID, charge-pump GPIO assertion after connect, and HDMI mode/infoframe forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/encoder-tpd12s015.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-dpi.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-dpi.c

## Purpose
`panel-dpi.c` implements a generic OF-described DPI panel for the OMAP2 DSS fbdev stack. It reads display timings from device tree, forwards DPI operations upstream, and controls an optional enable GPIO.

## Important APIs, Types, And Functions
- `struct panel_drv_data` stores DSS display, upstream DPI source, data-line count, video timings, and optional enable GPIO.
- `panel_dpi_probe_of()` reads the `panel-timing` node via `of_get_display_timing()`, converts it to `omap_video_timings`, requests optional enable GPIO, and finds the upstream source.
- `panel_dpi_ops` supplies display connect/disconnect, enable/disable, timing methods, and resolution.

## Control Flow
Probe requires OF, allocates state, parses panel timing and source endpoint, fills the DSS display, and registers it. Enable requires a connection, sets data lines if nonzero, sets timings, enables upstream DPI, asserts enable GPIO, and marks active. Disable clears GPIO, disables upstream, and marks disabled. Remove unregisters, disables/disconnects, and releases the upstream source.

## State And Persistence
Timings and GPIO/source references are per-device runtime state. No persistent storage.

## Dependencies And Integration Points
The driver depends on OF display timing parsing, GPIO descriptors, OMAP DSS DPI ops, and `omapdss_register_display()`.

## Risks
`data_lines` is not parsed, so data-line configuration remains zero unless extended. Enable GPIO is optional but `gpiod_set_value_cansleep(NULL, ...)` is tolerated by gpiod APIs; behavior depends on kernel semantics. Bad DT timing values are only caught by upstream `check_timings`.

## Test Signals
Valid DT `panel-timing` should create a DPI display with expected resolution/timing, assert enable GPIO on active state, and pass timing checks through upstream DPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-dpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-dsi-cm.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-dsi-cm.c

## Purpose
`panel-dsi-cm.c` implements a generic DSI command-mode panel for OMAP2 DSS fbdev. It manages DSI virtual-channel setup, DCS sleep/display/backlight commands, manual updates, TE synchronization, ULPS idle power state, memory reads, sysfs diagnostics, and reset recovery.

## Important APIs, Types, And Functions
- `struct panel_drv_data` stores DSS display, upstream DSI source, timings, mutex, backlight device, reset/TE GPIOs, pin config, enabled/TE/ULPS state, DSI channel, update atomic, and delayed works.
- DCS helpers `dsicm_dcs_read_1()`, `dsicm_dcs_write_0()`, and `dsicm_dcs_write_1()` wrap upstream DSI ops.
- Power sequencing uses `dsicm_hw_reset()`, `dsicm_sleep_out()`, `dsicm_power_on()`, `dsicm_power_off()`, and `dsicm_panel_reset()`.
- ULPS flow uses `dsicm_enter_ulps()`, `dsicm_exit_ulps()`, `dsicm_wake_up()`, and `dsicm_ulps_work()`.
- Update flow uses `dsicm_update()`, `dsicm_te_isr()`, `dsicm_te_timeout_work_callback()`, and `dsicm_framedone_cb()`.
- Sysfs attributes expose DSI error count, hardware revision, ULPS state, and ULPS timeout.
- `dsicm_ops` registers display operations including manual update, sync, TE control, and memory read.

## Control Flow
Probe requires OF, finds the upstream DSI source, seeds fixed 864x480 timings, registers the DSS display with manual-update and tear-elimination caps, initializes locks/work, requests reset and optional TE GPIO, optionally registers DSI backlight, resets the panel, and creates sysfs files. Connect forwards DSI connect, requests a virtual channel, and maps it to hard-coded target VC ID 0. Enable locks the panel, bus-locks DSI, powers on the panel, and marks active. Power-on configures DSI pins/config, enables DSI, resets hardware, leaves HS off for commands, exits sleep, reads ID, configures brightness/display control/pixel format/display-on/TE, enables video output, then enables HS mode.

Manual update wakes from ULPS, sets the full update window, and either waits for external TE IRQ before starting `in->ops.dsi->update()` or starts immediately. The DSI bus lock is intentionally held until frame-done callback or TE timeout. Disable cancels ULPS work, wakes if needed, powers off, disables DSI, and marks disabled. Memory read sets a DCS read window and loops reading small packets until the requested RGB888 data is collected or interrupted.

## State And Persistence
State is per platform device and protected mostly by `ddata->lock` plus upstream DSI bus locks. `do_update` coordinates TE IRQ update start. `ulps_enabled` and delayed ULPS work implement runtime low-power state. No state persists beyond driver lifetime.

## Dependencies And Integration Points
The driver depends on OMAP DSS DSI ops, MIPI DCS constants, GPIO descriptors, IRQs, workqueues, backlight class, sysfs, and OF graph lookup. It registers as an OMAP DSS DSI display.

## Risks
Several configuration fields (`use_dsi_backlight`, `pin_config`, `ulps_timeout`) are not parsed in the visible probe path, so defaults may disable intended features. TE update flow holds the DSI bus lock across async completion; missed frame-done or TE timeout bugs can stall the bus. Error paths after `omapdss_register_display()` may return without unregistering the display. Reset GPIO polarity comments indicate compatibility with incorrect DTS polarity. Memory reads use very small packet sizes and can be slow.

## Test Signals
Signals include successful display registration, DSI VC allocation, panel ID sysfs read, DSI error sysfs read, enable/disable with DCS sleep/display transitions, manual update completion with and without TE GPIO, TE timeout recovery, ULPS sysfs toggling, backlight writes when enabled, and memory-read correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-dsi-cm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-lgphilips-lb035q02.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-lgphilips-lb035q02.c

## Purpose
`panel-lgphilips-lb035q02.c` implements an SPI-initialized DPI panel driver for the LG.Philips LB035Q02 LCD in the OMAP2 DSS fbdev stack.

## Important APIs, Types, And Functions
- `lb035q02_timings` defines 320x240 timing and signal polarity defaults.
- `struct panel_drv_data` stores DSS display, upstream DPI source, SPI device, data lines, timings, and enable GPIO.
- `lb035q02_write_reg()` sends a two-transfer SPI register index/value sequence.
- `init_lb035q02_panel()` writes the panel initialization sequence.
- `lb035q02_ops` exposes DSS connect/disconnect, enable/disable, timing, and resolution operations.

## Control Flow
SPI probe requires OF, allocates state, stores SPI pointer, requests mandatory enable GPIO, finds upstream source, initializes timings, fills the DSS display, and registers it. Connect forwards to upstream DPI connect and initializes panel registers over SPI. Enable sets data lines if nonzero, programs timings, enables upstream DPI, asserts enable GPIO, and marks active. Disable clears GPIO, disables DPI, and marks disabled.

## State And Persistence
Per-device state stores the SPI pointer, timings, GPIO, and source reference. Panel register state is programmed on connect and otherwise lives in hardware.

## Dependencies And Integration Points
The driver depends on SPI, GPIO descriptors, OF graph helpers, and OMAP DSS DPI display registration.

## Risks
Panel initialization occurs on connect rather than enable, so reconnect behavior matters. The mandatory enable GPIO must be present in DT. SPI transfer buffers are stack-local but synchronous, which is safe. `data_lines` is not parsed and remains zero.

## Test Signals
A compatible SPI node should register a DPI display, emit SPI initialization writes on connect, assert enable GPIO on enable, and display 320x240 output with the declared timings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-lgphilips-lb035q02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-nec-nl8048hl11.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-nec-nl8048hl11.c

## Purpose
`panel-nec-nl8048hl11.c` implements an SPI-initialized NEC NL8048HL11 WVGA DPI panel driver for OMAP2 DSS fbdev, including suspend/resume panel reinitialization.

## Important APIs, Types, And Functions
- `nec_8048_init_seq` contains the panel register initialization sequence.
- `nec_8048_panel_timings` defines 800x480 timing and signal polarity defaults.
- `struct panel_drv_data` stores DSS display, upstream DPI source, timings, data lines, reset GPIO, and SPI device.
- `nec_8048_spi_send()` writes a register/value pair as a 32-bit SPI word.
- `init_nec_8048_wvga_lcd()` sends the init sequence with a delay before the final command.
- `nec_8048_ops` supplies DSS display operations; PM ops send standby/resume commands.

## Control Flow
Probe requires OF, configures SPI mode 0 and 32-bit words, calls `spi_setup()`, initializes the LCD over SPI, allocates state, finds upstream source, requests reset GPIO, initializes timings, and registers the display. Enable programs optional data lines and timings, enables upstream DPI, sets reset GPIO to the compatibility polarity value, and marks active. Disable clears reset GPIO, disables upstream DPI, and marks disabled. Suspend sends register 2 value 1 and delays; resume redoes SPI setup, sends register 2 value 0, and reinitializes the panel sequence.

## State And Persistence
Driver state is per SPI device. Hardware register contents are reinitialized at probe and resume. No persistent software state.

## Dependencies And Integration Points
The file depends on SPI, GPIO descriptors, OF graph helpers, PM sleep ops, and OMAP DSS DPI operations.

## Risks
The panel is initialized before state allocation and before reset GPIO acquisition, which may violate some power/reset expectations. Comments note existing DTS reset polarity is incorrect, so GPIO semantics are compatibility-driven. `nec_8048_spi_send()` logs but init sequence ignores individual failures. `data_lines` is not parsed.

## Test Signals
SPI setup at 32 bits, init-sequence writes, active reset GPIO behavior, successful 800x480 DPI output, and suspend/resume reinitialization are the key validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-nec-nl8048hl11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-sharp-ls037v7dw01.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-sharp-ls037v7dw01.c

## Purpose
`panel-sharp-ls037v7dw01.c` implements the Sharp LS037V7DW01 DPI panel for OMAP2 DSS fbdev, including regulator and multiple control GPIOs.

## Important APIs, Types, And Functions
- `sharp_ls_timings` defines 480x640 timing and signal polarity defaults.
- `struct panel_drv_data` stores DSS display, upstream DPI source, regulator, data lines, timings, and GPIOs for reset, enable, mode, left/right, and up/down scan.
- `sharp_ls_ops` provides DSS display connect/disconnect, enable/disable, timing, and resolution operations.
- `sharp_ls_probe_of()` requests regulator/GPIOs and finds the upstream source.

## Control Flow
Probe requires OF, allocates state, gets `envdd` regulator, requests enable/reset/mode GPIOs, finds upstream source, initializes timings, fills DSS display fields, and registers the display. Enable sets data lines and timings, enables regulator, enables upstream DPI, waits 50 ms, releases reset and asserts panel enable, then marks active. Disable deasserts enable/reset, waits 100 ms, disables upstream DPI, disables regulator, and marks disabled.

## State And Persistence
Runtime state includes current timings, regulator enable state, GPIO values, source reference, and DSS display state. No persistent state.

## Dependencies And Integration Points
The driver depends on regulator consumers, GPIO descriptors, OF graph helpers, and OMAP DSS DPI operations.

## Risks
Mode/LR/UD GPIOs are requested but not explicitly programmed after request defaults, so DT descriptor flags and default-low requests determine scan mode. `regulator_disable(ddata->vcc)` is called in an enable error path even if `vcc` is unexpectedly null, though probe requires it. Power sequencing relies on fixed sleeps rather than VSYNC observation.

## Test Signals
Validate regulator enable/disable, reset/enable GPIO sequence, 50/100 ms power waits, display registration for compatible `omapdss,sharp,ls037v7dw01`, and 480x640 DPI output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-sharp-ls037v7dw01.c -->
