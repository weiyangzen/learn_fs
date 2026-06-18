# Research Report: subset-b-005561

This grouped report covers the requested fbdev source files under `sources/distributed-fs/ceph-client/drivers/video/fbdev`. Each source section is bounded by reconciliation markers so it can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/gx1fb_core.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/gx1fb_core.c

Purpose: implements the PCI fbdev core for AMD/Cyrix Geode GX1 systems using the GX1 display controller and CS5530 video device. It owns framebuffer registration, mode validation, memory/register mapping, palette handling, blanking dispatch, module options, and driver bind/unbind.

Important APIs, types, and functions: `gx1_modedb` is the supported mode table up to 1280x1024. `gx1_line_delta()` rounds scanline pitch to 1024, 2048, or 4096 bytes. `gx1fb_check_var()` validates resolution, optional panel bounds, 8/16 bpp formats, and framebuffer capacity. `gx1fb_set_par()` selects pseudo/truecolor visual, programs `fix.line_length`, and calls `par->dc_ops->set_mode()`. `gx1fb_setcolreg()` updates either the software pseudo-palette or the hardware palette through `dc_ops`. `gx1fb_blank()` delegates DPMS behavior to `vid_ops`. `gx1fb_map_video_memory()` enables PCI, maps the CS5530 BAR, maps the GX1 display-controller region, discovers framebuffer size, and maps framebuffer memory. `gx1fb_probe()` wires `gx1_dc_ops` and `cs5530_vid_ops`, selects a mode, clears VRAM, sets hardware state, and registers the framebuffer.

Control flow: module init parses boot/module options and registers a PCI driver unless fb modesetting is disabled. Probe removes conflicting apertures, allocates `fb_info`, fills `geodefb_par`, maps resources, resolves a mode with `fb_find_mode()`, zeroes VRAM, calls check/set, then registers fbdev. Runtime callbacks go from fbdev core to local check/set/palette/blank functions and then into Geode display/video operation tables. Remove unregisters the framebuffer and releases mappings and color map.

State and persistence: persistent driver state lives in `fb_info`, `geodefb_par`, `info->cmap`, and the 16-entry pseudo-palette stored after `geodefb_par` in the framebuffer allocation. Module parameters `mode`, `crt`, and `panel` select initial mode and output policy. No suspend/resume path is implemented here.

Dependencies and integration points: depends on fbdev core, PCI, aperture conflict removal, GX1 helpers from `geodefb.h`/`display_gx1.h`, and CS5530 video operations from `video_cs5530.c`. Hardware dependencies include `gx1_gx_base()`, `gx1_frame_buffer_size()`, `gx1_dc_ops`, and CS5530 display register BAR layout.

Risks: resource cleanup is fragile on partial failures: `gx1fb_map_video_memory()` returns immediately after several request/map failures without undoing prior successful resources, and the error path releases `pci_release_region(pdev, 1)` for `vid_regs` even though `gx1fb_map_video_memory()` requested BAR 0 for video. `gx1fb_check_var()` contains a timing-parameter FIXME, so invalid sync timings may reach hardware. Panel parsing assumes a simple `<x><separator><y>` shape and only reports a warning before falling back to CRT.

Test signals: useful tests are PCI probe/remove under success and forced failure at each mapping step, fb mode setting for every entry in `gx1_modedb`, invalid overlarge modes and bpp values, palette updates in 8 bpp and 16 bpp, DPMS blank modes through `cs5530_vid_ops`, and module/boot option parsing for `mode`, `crt`, and `panel`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/gx1fb_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/gxfb.h -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/gxfb.h

Purpose: declares the Geode GX framebuffer private state, hardware register indexes, bit definitions, MMIO access helpers, and exported operation prototypes shared by `gxfb_core.c`, `video_gx.c`, and `suspend_gx.c`.

Important APIs, types, and functions: `struct gxfb_par` is the central per-device state and includes output policy, MMIO pointers for display/video/graphics processors, `powered_down`, saved MSR state, saved GP/DC/VP/FP registers, and a saved display-controller palette. Prototypes cover framebuffer sizing, pitch calculation, mode programming, hardware palette writes, GX video clock/display/blank operations, and powerdown/powerup. Enums `gp_registers`, `dc_registers`, `vp_registers`, and `fp_registers` name register slots used by inline `read_gp/write_gp`, `read_dc/write_dc`, `read_vp/write_vp`, and `read_fp/write_fp`.

Control flow: this header is not executable by itself. It defines the data contract used when the core driver allocates `fb_info->par`, when the mode code writes display/video registers, and when suspend code snapshots and restores hardware state.

State and persistence: the register count constants define the size of saved state arrays in `struct gxfb_par`. Saved state includes 32-bit register snapshots even for VP/FP areas stored as 64-bit arrays, matching comments that only lower 32 bits are used. MSR persistence covers pad select and dot PLL state.

Dependencies and integration points: includes `<linux/io.h>` and relies on fbdev types through source files that include it. MSR names come from `linux/cs5535.h` and low-level MSR instructions in implementation files. The header ties GX-specific register definitions to the generic fbdev `fb_info` callback flow.

Risks: register offsets and undocumented bits are encoded as constants with sparse comments, so changes require hardware documentation or regression testing. `PREDIV2` is defined with `MSR_GLCP_SYS_RSTPLL_DOTPOSTDIV3`, matching the source but suspicious by name. Inline helpers perform unchecked MMIO arithmetic and assume mappings are valid.

Test signals: compile coverage with all Geode GX files, suspend/resume tests validating saved array sizes against register ranges, and mode/blank tests that exercise every accessor family are the main signals. Static analysis should flag mismatched register-count constants or invalid enum indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/gxfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/gxfb_core.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/gxfb_core.c

Purpose: implements the PCI fbdev core for AMD/National Geode GX video devices with virtual PCI BARs for framebuffer, graphics processor, display controller, and video/flat-panel registers.

Important APIs, types, and functions: mode databases `gx_modedb` and OLPC `gx_dcon_modedb` feed `get_modedb()`. `gxfb_check_var()` validates geometry, bpp, memory capacity, and color fields. `gxfb_set_par()` computes visual and pitch, then calls `gx_set_mode()`. `gxfb_setcolreg()` updates the pseudo-palette or calls `gx_set_hw_palette_reg()`. `gxfb_map_video_memory()` maps BAR3 video processor, BAR2 display controller, BAR1 graphics processor, and BAR0 framebuffer, then programs `DC_GLIU0_MEM_OFFSET`. `gxfb_suspend()`/`gxfb_resume()` wrap `gx_powerdown()`/`gx_powerup()` under `console_lock()`. `gxfb_probe()` selects CRT versus flat-panel output by reading `MSR_GX_GLD_MSR_CONFIG`, finds a mode, clears VRAM, sets hardware, configures VT switching, and registers fbdev.

Control flow: init optionally parses `gxfb` boot options, checks `fb_modesetting_disabled()`, and registers a PCI driver. Probe allocates `fb_info`, maps all BARs, derives output type, chooses the normal or DCON mode table, programs a selected mode, then registers the framebuffer. PM callbacks save/restore hardware through `suspend_gx.c`; fbdev callbacks route to mode, palette, and blank helpers in `video_gx.c`.

State and persistence: `struct gxfb_par` stores mappings, output state, and suspend snapshots. The `vram` module parameter can override `gx_frame_buffer_size()`. `vt_switch` is persisted via `pm_set_vt_switch()`. The pseudo-palette is embedded after private data in the framebuffer allocation.

Dependencies and integration points: depends on PCI, fbdev, console suspend coordination, aperture removal, OLPC DCON detection, x86 MSR access, CS5535 definitions, and `gxfb.h` operations. It assumes firmware supplies a virtual PCI header with a fixed BAR layout and a 16 MiB framebuffer unless overridden.

Risks: mapping failure paths in `gxfb_map_video_memory()` do not unwind prior requested BARs before returning to the caller, though the probe error path later handles fields that were stored. `gxfb_resume()` returns after a failed `gx_powerup()` without unlocking `console_lock()`, which is a potential deadlock path in this version. Timing validation is still a FIXME. The code assumes BIOS/firmware virtual PCI setup and may misbehave on nonconforming platforms.

Test signals: probe/remove on emulated BAR failure permutations, suspend/resume while framebuffer is active, OLPC DCON mode selection, mode validation across 8/16/32 bpp, palette writes in pseudo and truecolor, and DPMS blank modes. Locking tests should cover the `gx_powerup()` failure path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/gxfb_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/lxfb.h -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/lxfb.h

Purpose: provides the Geode LX framebuffer private state, output flags, register index maps, bit definitions, MMIO helpers, and operation prototypes shared by the LX core and operations files.

Important APIs, types, and functions: `struct lxfb_par` carries output mask, GP/DC/VP MMIO pointers, `powered_down`, saved MSR values, register snapshots, palettes, filter coefficients, and VP coefficient RAM. `lx_get_pitch()` aligns scanline pitch to 8 bytes. Public prototypes include `lx_set_mode()`, `lx_framebuffer_size()`, `lx_blank_display()`, `lx_set_palette_reg()`, `lx_powerdown()`, and `lx_powerup()`. Enums define GP, DC, VP, and FP register indexes; inline accessors map those indexes to byte offsets in MMIO.

Control flow: like `gxfb.h`, this file is a contract, not a standalone driver. The core initializes `struct lxfb_par`, `lxfb_ops.c` consumes register constants to program clocks and display state, and suspend code uses the arrays and MSR members to save/restore hardware.

State and persistence: compared with GX, LX preserves more state: DC and VP palettes, horizontal and vertical filter coefficients, and video processor coefficient RAM. Output state uses `OUTPUT_CRT` and `OUTPUT_PANEL` bit flags rather than the GX boolean CRT flag.

Dependencies and integration points: depends on fbdev type declarations and LX/CS5535 MSR definitions in implementation files. It integrates MMIO registers, MSR control, flat-panel registers at `VP_FP_START`, and fbdev palette/mode callbacks.

Risks: many MSR bits are documented in comments as undocumented or uncertain, so hardware compatibility depends on legacy knowledge. Inline accessors are unchecked and depend on successful BAR mappings. The state arrays must remain consistent with register counts or suspend/resume will silently omit or overrun intended state.

Test signals: build tests with `lxfb_core.c` and `lxfb_ops.c`, mode-setting smoke tests for CRT, panel, and simultaneous output, suspend/resume state comparison on representative hardware, and static checks for register enum values exceeding count constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/lxfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/lxfb_core.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/lxfb_core.c

Purpose: implements the PCI fbdev core for AMD Geode LX video devices. It owns module parameters, mode database selection, fbdev callbacks, PCI BAR mapping, output selection, registration, and PM entry points.

Important APIs, types, and functions: `geode_modedb` contains a broad fixed mode list up to 1920x1440; `olpc_dcon_modedb` supplies the 1200x900 OLPC panel mode. `lxfb_check_var()` rejects missing pixclock, unsupported geometry, unsupported bpp, and insufficient VRAM, then assigns color bitfields. `lxfb_set_par()` selects visual/pitch and calls `lx_set_mode()`. `lxfb_setcolreg()` handles pseudo-palette or hardware palette updates. `lxfb_map_video_memory()` requests BAR0 framebuffer, BAR1 GP, BAR2 display controller, BAR3 VP, maps them, and programs the GLIU memory offset with DC unlock/lock. `lxfb_suspend()` and `lxfb_resume()` call `lx_powerdown()`/`lx_powerup()` under `console_lock()`.

Control flow: init parses `lxfb` options for `noclear`, `nopanel`, `nocrt`, or a mode string, then registers a PCI driver. Probe removes conflicting apertures, allocates fbdev state, maps resources, computes `par->output`, selects OLPC or generic mode database, sets and optionally clears the framebuffer, configures hardware mode, configures VT switching, and registers fbdev.

State and persistence: private state is `struct lxfb_par`; module parameters persist initial VRAM override, no-clear policy, output disable flags, and VT switch behavior. The framebuffer allocation embeds the pseudo-palette after private data. Suspend state is saved/restored in `lxfb_ops.c`.

Dependencies and integration points: depends on PCI, fbdev, aperture conflict handling, console locking, OLPC DCON detection, and LX operation functions. Hardware expectations include BAR layout matching the Geode LX PCI video function and accessible CS5535/LX MSRs.

Risks: `lxfb_map_video_memory()` returns after request/map failures without local unwind, so probe cleanup must infer partial state; requested PCI regions with failed mapping may be retained until the error path. `lxfb_resume()` has the same early-return-without-console-unlock risk as `gxfb_resume()` if `lx_powerup()` fails. Timing validation is limited to nonzero pixclock and maximum geometry. No explicit check rejects disabling both panel and CRT.

Test signals: boot/module option parsing, probe/remove with each BAR failure injected, no-clear behavior, output combinations including `nopanel,nocrt`, OLPC DCON mode selection, color depth validation, suspend/resume including forced `lx_powerup()` failure, and DPMS blank tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/lxfb_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/lxfb_ops.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/lxfb_ops.c

Purpose: contains Geode LX hardware operations for dot-clock programming, mode programming, output enable/disable sequencing, palette writes, blanking, and suspend/resume register save/restore.

Important APIs, types, and functions: `pll_table` maps dot-clock frequencies to PLL values. `lx_set_dotpll()` writes `MSR_GLCP_DOTPLL` and waits for lock. `lx_set_clock()` chooses the closest PLL entry from `info->var.pixclock`. `lx_graphics_disable()` shuts down video overlays, VGA/video enable, IRQs, genlock, color key, panel power, DACs, display timing generator, FIFO loader, and waits for GP idle. `lx_graphics_enable()` programs VP display config and panel/CRT output. `lx_framebuffer_size()` obtains VRAM size from GLIU MSR or VSA virtual registers. `lx_set_mode()` programs output MSRs, framebuffer offsets, scaling defaults, DV line size, pitch, watermarks, display timing registers, bpp mode, and re-enables output. `lx_set_palette_reg()` writes DC palette entries. `lx_blank_display()` implements fbdev DPMS. `lx_powerdown()`/`lx_powerup()` call save/disable and restore paths.

Control flow: mode setting unlocks DC registers, disables current graphics, programs clock and output mode, writes frame and timing state, enables graphics, writes main DC config registers, then locks DC. Powerdown waits for idle, snapshots MSRs/registers/palettes/filter coefficient RAM, disables graphics, and marks `powered_down`. Powerup restores PLL, GP/DC/VP/FP state in dependency order and re-enables VP/DC state last.

State and persistence: save/restore persists GP, DC, VP, FP registers, pad/dotpll/display/spare MSRs, DC and VP palettes, horizontal/vertical filter coefficients, and VP coefficient RAM inside `struct lxfb_par`. `powered_down` prevents duplicate transitions. Mode state is otherwise hardware-resident.

Dependencies and integration points: integrated with `lxfb_core.c` callbacks and `lxfb.h` register definitions; uses x86 MSR access, CS5535 VSA helpers, fbdev `fb_info` mode fields, and low-level delays. Output behavior depends on `par->output` flags set by the core.

Risks: busy-wait loops for PLL lock and GP idle can stall if hardware misbehaves; GP idle loops have no timeout in several places. `lx_set_clock()` uses `abs()` on unsigned-derived values and chooses nearest table entry rather than exact validation. Several TODO/FIXME comments mark missing panel scaling, acceleration, interlacing, and compression support. Suspend restore skips selected registers and contains comments questioning some omissions, so obscure hardware state may not round-trip.

Test signals: compare programmed timing registers against expected mode values, verify closest PLL selection for known modes, DPMS blank/unblank on CRT and panel, suspend/resume register round-trip with active palettes and filter state, failure testing for PLL lock/GP busy loops, and visual tests for every supported bpp.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/lxfb_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/suspend_gx.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/suspend_gx.c

Purpose: implements Geode GX suspend and resume helpers used by `gxfb_core.c` PM callbacks.

Important APIs, types, and functions: `gx_save_regs()` waits for BLT idle, saves pad select and dot PLL MSRs, unlocks DC, copies GP/DC/VP/FP register blocks, and saves the DC palette. `gx_set_dotpll()` restores dot PLL with reset/lock sequencing. `gx_restore_gfx_proc()`, `gx_restore_display_ctlr()`, and `gx_restore_video_proc()` restore register groups while deliberately skipping volatile/status or enable-sensitive registers. `gx_disable_graphics()` shuts off VP, flat panel, and DC enables. `gx_enable_graphics()` restores panel power state and re-enables VP/DC in order. `gx_powerdown()` and `gx_powerup()` are the exported idempotent entry points.

Control flow: powerdown returns early if already powered down, saves state, disables graphics, and sets `powered_down`. Powerup returns early if not powered down, restores PLL and registers, enables graphics, and clears `powered_down`. Restore order is PLL, graphics processor, display controller, video processor, flat-panel registers, then final enables.

State and persistence: state is persisted in `struct gxfb_par`: MSRs, GP/DC/VP/FP arrays, palette, and powered-down flag. Framebuffer contents are not saved here; the driver relies on mapped VRAM retention or higher-level redraw.

Dependencies and integration points: uses `gxfb.h` register helpers, x86 MSR access, CS5535 MSR definitions, and delay helpers. Called under console lock by `gxfb_core.c` suspend/resume.

Risks: BLT wait and PLL wait are bounded inconsistently: BLT wait has no timeout, while PLL lock has a short loop. Register save uses `memcpy()` from MMIO pointers rather than explicit `memcpy_fromio()`, which is legacy style and may be architecture-sensitive. Restore intentionally skips multiple registers, so features outside the normal fbdev mode path may not survive suspend.

Test signals: suspend/resume cycles while in CRT and panel mode, palette preservation, BLT-active suspend, PLL lock timeout behavior, and regression tests that compare visible mode after resume with mode before suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/suspend_gx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/video_cs5530.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/video_cs5530.c

Purpose: implements the `geode_vid_ops` backend for the CS5530 video/display block used by the GX1 framebuffer driver.

Important APIs, types, and functions: `struct cs5530_pll_entry` maps fbdev pixclock values to CS5530 PLL register values. `cs5530_set_dclk_frequency()` chooses the closest table entry and writes `CS5530_DOT_CLK_CONFIG` through reset and bypass sequencing. `cs5530_configure_display()` programs display configuration bits for CRT, flat panel, default sync skew, power sequence delay, palette bypass, and sync polarity. `cs5530_blank_display()` maps fbdev blank modes to DAC/panel power, data, and sync bits. `cs5530_vid_ops` exports these three functions.

Control flow: GX1 mode programming calls `set_dclk` and `configure_display` through the video ops table; blanking calls `blank_display`. The code reads existing display config, masks old mode bits, writes updated output policy, and uses delays during PLL programming.

State and persistence: no private state is allocated here. It consumes `geodefb_par` from `fb_info->par`, especially `vid_regs`, `enable_crt`, and `panel_x`. Hardware display state persists in CS5530 registers.

Dependencies and integration points: depends on `geodefb.h` for `struct geodefb_par` and `struct geode_vid_ops`, `video_cs5530.h` for register bits, and fbdev blank/mode fields. Integrated only by GX1 core in this work item.

Risks: PLL selection is nearest-match only; there is no bounds rejection if the requested pixclock is far from the table. Register writes assume `vid_regs` is valid. Panel blanking powers the panel only when both hsync and vsync are active, which may not match all panels' power sequencing requirements.

Test signals: unit-style table selection for common VESA pixclocks, register trace validation for reset/bypass sequence, CRT-only, panel-only, and combined output configuration, and all five fbdev blank modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/video_cs5530.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/video_cs5530.h -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/video_cs5530.h

Purpose: declares the CS5530 video operation table and register offsets/bit masks used by `video_cs5530.c` and GX1 code.

Important APIs, types, and functions: exports `cs5530_vid_ops`. Defines register offsets for video config, display config, video position/scale/color-key, palette address/data, dot-clock config, and CRC. Defines bit masks for video input formats, line size, filter enable, display enable, sync enable, DAC and flat-panel power/data, sync polarity, power sequence delay, DDC pins, and 16-bit mode.

Control flow: this header is consumed by the CS5530 implementation; it does not execute. Its constants determine which bits are preserved, cleared, or set during display configuration and blanking.

State and persistence: all state represented here is hardware-resident in CS5530 registers. There is no C storage except users of the constants.

Dependencies and integration points: depends on `struct geode_vid_ops` being visible in including source contexts. Integrates CS5530 display control with GX1 fbdev operations.

Risks: incorrect masks here directly affect hardware programming. Several DDC and video overlay definitions are present even though this worker-read implementation uses only display/PLL/blanking bits, so future users need separate validation.

Test signals: compile coverage with `video_cs5530.c`, register-level tests that compare expected display config masks, and hardware smoke tests for palette, PLL, and DPMS behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/video_cs5530.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/video_gx.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/video_gx.c

Purpose: implements Geode GX video processor operations for dot-clock programming, CRT/TFT output configuration, and blanking.

Important APIs, types, and functions: `struct gx_pll_entry` and the 48 MHz/14 MHz PLL tables map pixclock to divider bits and dot PLL values. `gx_set_dclk_frequency()` chooses the correct table by CPU stepping, programs `MSR_GLCP_DOTPLL` and `MSR_GLCP_SYS_RSTPLL`, and waits for lock. `gx_configure_tft()` configures pad select, flat-panel timing, dither control, FP power/data, and panel power. `gx_configure_display()` programs VP display config, sync polarity, DAC power, gamma, CRT enables, and calls TFT setup when CRT is disabled. `gx_blank_display()` maps fbdev blank modes to DAC, sync, CRT enable, and panel power.

Control flow: `gx_set_mode()` from the GX display controller path calls these exported functions to set clock and display output. Blanking is called from fbdev callbacks. CRT mode and flat-panel mode diverge primarily through `par->enable_crt`.

State and persistence: uses `struct gxfb_par` MMIO pointers and `enable_crt`. Persistent hardware state is in MSRs, VP registers, and FP registers; no private heap state is maintained here.

Dependencies and integration points: depends on `gxfb.h`, x86 CPU stepping data, MSR helpers, CS5535 MSR definitions, and fbdev sync/blank fields. It is paired with `gxfb_core.c` and `suspend_gx.c`.

Risks: the `PREDIV2` macro appears to alias the post-divider bit by definition, which may be intentional legacy behavior or a typo carried into PLL setup. PLL lock wait has a timeout counter but no error return if lock is never observed. Comments indicate undocumented TFT bits and hardware-specific magic values. Flat-panel configuration is limited and not EDID-driven.

Test signals: dot-clock programming on stepping-1 and later GX CPUs, register traces for common VESA modes, CRT versus flat-panel output validation, all DPMS blank modes, and suspend/resume interaction with TFT panel power bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/video_gx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/goldfishfb.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/goldfishfb.c

Purpose: implements a platform fbdev driver for the Goldfish virtual framebuffer used by Android/emulator-style virtual platforms.

Important APIs, types, and functions: MMIO offsets cover width/height discovery, interrupt status/enable, framebuffer base update, rotation, blanking, and physical size. `struct goldfish_fb` embeds `struct fb_info`, register base, IRQ, spinlock, wait queue, base-update counter, rotation, and pseudo-palette. `goldfish_fb_interrupt()` handles `FB_INT_BASE_UPDATE_DONE` and wakes waiters. `goldfish_fb_check_var()` restricts modes to the host-reported dimensions, rotation parity, fixed xoffset, bpp, and grayscale. `goldfish_fb_set_par()` updates line length and writes rotation. `goldfish_fb_pan_display()` writes a new base and waits briefly for interrupt completion. `goldfish_fb_probe()` maps MMIO, reads geometry, allocates coherent DMA memory for two screens, requests IRQ, enables base-update interrupts, pans once, and registers fbdev.

Control flow: platform probe initializes state from device registers and coherent DMA memory. Runtime fbdev pan writes `FB_SET_BASE` and waits on `base_update_count`. Interrupts serialize with pan via a spinlock. Remove unregisters fbdev, frees IRQ, frees coherent memory, and releases the container.

State and persistence: persistent state is in the allocated `goldfish_fb` object, including embedded `fb_info`, 16-entry pseudo-palette, current rotation, and completion counter. The framebuffer is coherent DMA memory whose physical address is handed to the device.

Dependencies and integration points: depends on platform device resources, OF compatible `google,goldfish-fb`, ACPI ID `GFSH0004`, DMA coherent allocation, fbdev core, and interrupt delivery from the virtual device.

Risks: `goldfish_fb_pan_display()` waits only `HZ/15` and logs timeout but still returns success. Blank only handles normal and unblank modes. Rotation changes force line length to `xres * 2`, which is tailored to fixed 16 bpp. Probe embeds `fb_info` in a manually allocated object rather than using `framebuffer_alloc()`, so lifetime must remain carefully paired.

Test signals: probe/remove on OF and ACPI devices, DMA allocation failure, IRQ timeout during pan, rotate parity validation, ypan over two virtual screens, blank/unblank register writes, and interrupt handler behavior for zero/nonzero status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/goldfishfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/grvga.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/grvga.c

Purpose: implements an fbdev platform driver for Aeroflex Gaisler GRLIB SVGACTRL framebuffer hardware.

Important APIs, types, and functions: `struct grvga_regs` mirrors controller MMIO registers for status, timing, framebuffer position, clock vectors, and CLUT. `struct grvga_par` stores the mapped registers, pseudo-palette, selected clock, and whether framebuffer memory was driver-allocated. `grvga_check_var()` normalizes bpp to 8/16/24/32, enforces memory limits, validates the requested pixclock against hardware clock vectors, and sets color fields. `grvga_set_par()` writes timing registers and status bits. `grvga_setcolreg()` writes hardware CLUT for pseudocolor or pseudo-palette for truecolor. `grvga_pan_display()` writes aligned base address. `grvga_parse_custom()` parses a ten-field custom timing string. `grvga_probe()` parses boot options, maps registers, allocates cmap, finds/parses mode, maps supplied framebuffer memory or allocates pages, reserves pages for mmap, clears memory, and registers fbdev.

Control flow: platform probe gets `grvga` fb options, configures `fb_info`, maps resources, chooses mode, prepares framebuffer memory, registers fbdev, then writes the framebuffer base and enables the controller. Runtime callbacks validate mode, program timing/status registers, update CLUT/pseudo-palette, and pan by changing `fb_pos`.

State and persistence: `grvga_par` stores register mapping and clock selection. Framebuffer memory may be externally supplied via `addr` or allocated by the driver and DMA-mapped. For allocated memory, pages are marked reserved for mmap and `fb_alloced` controls cleanup.

Dependencies and integration points: depends on platform resources from OF, fbdev, DMA mapping, boot option string `grvga`, and GRLIB/SVGACTRL clock-vector hardware. OF matching uses names `GAISLER_SVGACTRL` and `01_063`.

Risks: `grvga_check_var()` switches on `info->var.bits_per_pixel` instead of the normalized `var->bits_per_pixel`, which can apply stale color-field logic. Allocated framebuffer cleanup uses `kfree()` on memory allocated with `__get_free_pages()`, rather than `free_pages()`, in this source. DMA mapping is not explicitly unmapped in remove. Custom parsing accepts sparse invalid fields until downstream validation.

Test signals: mode selection for each built-in mode and custom mode, pixclock rejection when not in clock vectors, supplied versus allocated framebuffer paths, mmap of reserved pages, y-pan base alignment, CLUT writes in 8 bpp and pseudo-palette writes in truecolor, and remove cleanup leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/grvga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/gxt4500.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/gxt4500.c

Purpose: implements a PCI fbdev driver for IBM GXT4500P/6500P and GXT4000P/6000P display adapters.

Important APIs, types, and functions: register definitions cover control/status, framebuffer definitions, direct framebuffer access, timing generator, PLL/RAMDAC, cursor, window attribute table, and colormap. `struct gxt4500_par` stores MMIO base, write-combining cookie, pixel format, PLL parameters, reference clock, and pseudo-palette. `calc_pll()` searches legal PLL divisors using LFSR tables; `calc_pixclock()` derives actual clock. `gxt4500_var_to_par()` validates geometry/interlace and selects pixel format. `gxt4500_unpack_pixfmt()` fills fb bitfields. `gxt4500_set_par()` programs PLL, resets raster engine, writes timing generator registers, framebuffer stride/tiles, WAT entries, sync polarity, and fix visual/line length. `gxt4500_setcolreg()`, `gxt4500_pan_display()`, and `gxt4500_blank()` implement palette, pan, and DPMS callbacks. `gxt4500_probe()` maps PCI BARs, sets endian config, allocates cmap, finds default/user mode, programs hardware, and registers fbdev.

Control flow: module init optionally parses mode, checks modesetting-disabled state, and registers a PCI driver. Probe claims register and framebuffer BARs, allocates fbdev state, maps registers and write-combined framebuffer, configures endian behavior, allocates cmap, unblanks, finds a mode, programs hardware, and registers. Runtime set_par recalculates hardware parameters from current `var`; pan writes refresh start; blank writes sync/display controls.

State and persistence: private state persists PLL solution, pixel format, MMIO mapping, and write-combining cookie. Hardware mode is fully register-resident. The pseudo-palette supports non-8bpp console color mapping.

Dependencies and integration points: depends on PCI, aperture removal, fbdev, architecture write-combining, and IBM card IDs. It assumes fixed BAR0 registers and BAR1 framebuffer layout.

Risks: probe error paths often collapse to `-ENODEV`, losing the original error cause. PLL search selects only nonnegative timing error and may reject viable clocks outside its search constraints. Some comments mark guessed WAT formats and incomplete framebuffer allocation support. No suspend/resume support is present. Blank default case silently behaves like normal blank instead of rejecting unknown modes.

Test signals: PCI ID matching for all four cards, PLL calculations for boundary pixclocks, set_par for 8/16/24/32 bpp, endian config on big and little endian builds, xpan alignment rejection, DPMS blank modes, colormap and pseudo-palette writes, and forced failures in BAR mapping/cmap/register_framebuffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/gxt4500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/hecubafb.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/hecubafb.c

Purpose: implements a virtual-memory fbdev driver for Hecuba/Apollo e-ink display hardware, delegating physical I/O to a board-specific `hecuba_board` provider.

Important APIs, types, and functions: fixed display dimensions are 600x800 at 1 bpp. `apollo_send_data()` and `apollo_send_command()` use board callbacks to set data/control lines and wait for ACK transitions. `hecubafb_dpy_update()` sends a full image transfer and display command. Deferred I/O callbacks `hecubafb_dpy_deferred_io()`, `hecubafb_defio_damage_range()`, and `hecubafb_defio_damage_area()` update the display. `FB_GEN_DEFAULT_DEFERRED_SYSMEM_OPS()` and `FB_DEFAULT_DEFERRED_OPS()` provide sysmem fb operations. `hecubafb_probe()` obtains board callbacks from platform data, pins the board module, allocates vmalloc framebuffer memory, initializes deferred I/O, registers fbdev, and calls board init.

Control flow: platform probe requires board platform data, allocates the backing buffer and `fb_info`, wires board callbacks into `hecubafb_par`, enables deferred I/O, registers the framebuffer, then initializes the hardware. Any fb damage or deferred work sends the entire framebuffer to the Apollo controller. Remove cleans deferred I/O, unregisters fbdev, frees memory, calls optional board remove, and drops the board module reference.

State and persistence: framebuffer state is a vmalloc `screen_buffer`; hardware has no partial dirty tracking in this driver. `struct hecubafb_par` stores `fb_info`, board operations, and send helpers. The display is updated from the buffer on deferred/damage events.

Dependencies and integration points: depends on platform data from a board-specific companion driver, `<video/hecubafb.h>` for command constants and board API, fbdev deferred I/O, vmalloc memory, and module reference ownership.

Risks: every damage callback sends a full 600x800/8 byte image, which is expensive for small updates. If `board->init()` fails after `register_framebuffer()`, the error path releases `fb_info` without unregistering or deferred-I/O cleanup in this source. Physical I/O ordering and ACK behavior are entirely trusted to board callbacks.

Test signals: board-data missing path, board module reference failure, vmalloc/framebuffer allocation failure, deferred I/O update sequencing, damage range/area callbacks, command/data ACK ordering with a fake board, `board->init()` failure after registration, and remove with optional board remove callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/hecubafb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/hgafb.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/hgafb.c

Purpose: implements a platform fbdev driver for Hercules Graphics Adapter compatible hardware at legacy memory and I/O ports.

Important APIs, types, and functions: global state tracks `hga_vram`, `hga_vram_len`, current `hga_mode`, detected card type/name, and I/O release flags. Low-level helpers program HGA registers via `outb_p`, test register writability, clear VRAM, switch text/graphics modes, pan by CRTC start address, and blank video. `hga_card_detect()` reserves 0xb0000 VRAM, maps it, optionally claims I/O ports, tests memory/registers, detects vsync toggling, and classifies card type. Fbdev callbacks include open/release mode switching, `hgafb_pan_display()`, `hgafb_blank()`, and custom monochrome fill/copy/imageblit operations using HGA row addressing. `hgafb_probe()` detects hardware, allocates/registers fbdev; init registers both platform driver and a simple platform device.

Control flow: module init registers a synthetic platform device. Probe performs legacy hardware detection, fills fixed 720x348 1bpp fbdev state, and registers. Opening the framebuffer switches to graphics and clears; release switches back to text and clears. Remove restores text mode, clears, unregisters, unmaps, and releases I/O regions.

State and persistence: most hardware state is global rather than per-device because the driver supports one fixed legacy device. The framebuffer maps fixed physical memory. `nologo` is a module parameter. Current mode is tracked under `hga_reg_lock`.

Dependencies and integration points: depends on legacy VGA/HGA I/O ports, platform-device scaffolding, fbdev IOMEM helpers, and spinlock serialization around register programming.

Risks: port claims are best-effort; if `request_region()` fails, the driver can continue and later may not own the ports it touches. Detection writes to legacy video memory and CRTC registers. Accel callbacks assume byte-aligned widths and HGA memory layout. `hga_fix.smem_start` is assigned the mapped virtual address rather than the physical base, matching legacy style but risky for mmap/userspace expectations.

Test signals: detection with no card, MDA-only, Hercules/HerculesPlus/HerculesColor signatures, open/release mode transitions, pan validation with y offsets multiple of 8, blank/unblank, fill/copy/imageblit alignment behavior, and cleanup after partial port reservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/hgafb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/hitfb.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/hitfb.c

Purpose: implements a platform fbdev driver for the Hitachi HD64461 LCD controller on SuperH systems, including basic hardware blit acceleration and PM.

Important APIs, types, and functions: `hitfb_readw()`/`hitfb_writew()` access HD64461 register offsets. Acceleration helpers wait for `ACCSTATUS`, start the engine, set destination, and program bitblt direction/masks. `hitfb_fillrect()` uses hardware fill for `ROP_COPY`, otherwise falls back to `cfb_fillrect()`. `hitfb_copyarea()` uses hardware bitblt. `hitfb_pan_display()` writes LCD base address. `hitfb_blank()` toggles LCD/display stop bits. `hitfb_setcolreg()` updates hardware palette for 8 bpp or pseudo-palette for 16 bpp. `hitfb_check_var()` clamps mode to fixed x/y, supported bpp, and available memory. `hitfb_set_par()` programs line length and bpp in LCD registers. Probe derives initial geometry from controller registers, allocates fbdev, and registers; suspend/resume blank and toggle clock/standby bits.

Control flow: module init registers a platform driver and synthetic platform device. Probe reads hardware current mode, fills fbdev structures, allocates cmap, and registers. Runtime draw callbacks wait for hardware accelerator completion before programming operations. Suspend blanks display and enters LCD clock stop; resume clears stop bits, waits, and unblanks.

State and persistence: `hitfb_var` and `hitfb_fix` are static templates populated from hardware at probe. Pseudo-palette storage is allocated as `info->par`. Hardware state is in fixed HD64461 registers and framebuffer memory at a fixed offset.

Dependencies and integration points: depends on SuperH machvec, HD64461 register definitions, CPU DAC header, fbdev cfb helpers, and platform scaffolding. It maps screen memory by casting the fixed physical offset rather than using a normal ioremap in this source.

Risks: acceleration wait loops have no timeout. Suspend/resume ignore the `struct device *` and operate global hardware. Probe uses fixed 512 KiB memory and fixed register offsets. `hitfb_resume()` reads/clears `SLCKE_OST` in a local variable, sleeps, then rereads and clears `SLCKE_IST`; only the latter is written, which may be intentional but is subtle.

Test signals: probe against 8 bpp and 16 bpp initial register states, check_var clamping of virtual height, palette programming, pan step for both bpp values, fill/copy accelerator operations and sync wait, blank/unblank bit transitions, and suspend/resume display recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/hitfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/hpfb.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/hpfb.c

Purpose: implements fbdev support for HP300 Topcat and Catseye framebuffers on internal HP300 and DIO/DIO-II buses.

Important APIs, types, and functions: global `fb_info`, `fb_regs`, and `fb_bitmask` represent the single device. `hpfb_setcolreg()` programs the color map through HP registers. `hpfb_blank()` controls `TC_NBLANK`. `topcat_blit()` programs the block mover; `hpfb_copyarea()`, `hpfb_fillrect()`, and `hpfb_sync()` use it for acceleration and synchronization. `hpfb_init_one()` reads framebuffer geometry from registers, initializes Catseye-specific magic registers, maps framebuffer memory, detects bit planes, enables planes, clears the screen, allocates cmap, and registers fbdev. `hpfb_dio_probe()` handles DIO devices; `hpfb_init()` also checks the internal framebuffer address.

Control flow: module init requires HP300 architecture and no disabled options, registers the DIO driver, then probes the internal Topcat address. DIO probe reserves device memory, maps DIO-II resources if needed, and calls common initialization. Remove unregisters, unmaps resources, releases memory, and frees the colormap.

State and persistence: one global framebuffer state is used. Hardware geometry and color depth are read from device registers at init. `fb_bitmask` captures the writable planes and is used for blanking and blitter enable masks.

Dependencies and integration points: depends on m68k HP300/DIO bus APIs, big-endian register accessors, fbdev, and Topcat/Catseye register conventions. It integrates with DIO device IDs and a special internal framebuffer physical/virtual address.

Risks: global state limits multiple-device handling. Internal framebuffer resource handling in `hpfb_init()` can return errors after registering the DIO driver without unregistering it. Busy waits on colormap and blitter registers have no timeout. Catseye initialization uses hardware magic from the HP X server. The cleanup module only unregisters the DIO driver; internal device cleanup relies on global fb state but is not fully symmetrical here.

Test signals: HP300-only init rejection on other architectures, DIO probe/remove for each supported secondary ID, internal Topcat detection, color map writes under busy conditions, blitter fill/copy/sync behavior, blank/unblank, and failure injection after DIO driver registration and internal resource request.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/hpfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i740_reg.h -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/i740_reg.h

Purpose: defines Intel740 VGA, extended VGA, multimedia, FIFO, interrupt, and BitBLT register offsets and bit masks used by `i740fb.c`.

Important APIs, types, and functions: there are no functions or types. Constants cover DAC ports, CRTC extension registers, misc output, system configuration extension registers such as `ADDRESS_MAPPING`, DRAM detection/control, DPMS, pixel-pipe configuration, cursor registers, VCLK2 PLL registers, multimedia overlay controls, FIFO status, interrupt masks, FIFO watermark/burst control, and BitBLT command registers/fields.

Control flow: this header shapes the implementation's control flow by naming the registers that `i740fb_decode_var()`, `i740fb_set_par()`, DDC bit-banging, blanking, memory detection, and optional BLT setup write.

State and persistence: all definitions refer to hardware state. The persistent software copy of these fields lives in `struct i740fb_par` in `i740fb.c`.

Dependencies and integration points: included by `i740fb.c`; many definitions are paired with VGA port helpers from `<video/vga.h>`. The BitBLT and FIFO definitions are present even though this driver marks acceleration as none and mainly uses mode programming/DPMS/DDC paths.

Risks: incorrect constants can corrupt VGA register programming. Many registers are legacy VGA indexed ports, where write order and protection bits matter. Some fields such as 32 bpp dynamic depth are explicitly noted as unimplemented on i740.

Test signals: compile coverage through `i740fb.c`, register trace comparison during set_par/blank/DDC, and static checks that fields used in masks match intended register widths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i740_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i740fb.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/i740fb.c

Purpose: implements a PCI fbdev driver for Intel740 PCI/AGP graphics adapters, including DDC probing, mode calculation/programming, palette handling, panning, blanking, write-combining, and minimal PM.

Important APIs, types, and functions: `struct i740fb_par` stores MMIO, memory type, DDC adapter, pseudo-palette, open refcount, VGA register shadows, Intel740 extended register shadows, and FIFO watermark. DDC callbacks bit-bang SCL/SDA through XRX registers; `i740fb_setup_ddc_bus()` registers the adapter. `i740fb_open()`/`release()` maintain `ref_count`. `i740_calc_fifo()` selects memory FIFO watermarks by bpp, clock, and SGRAM/SDRAM. `i740_calc_vclk()` computes PLL register values. `i740fb_decode_var()` validates and normalizes mode geometry/bpp, checks memory, fills VGA and extended register shadows, computes start address, VCLK, and FIFO watermark. `i740fb_check_var()` sets color fields and validates EDID monitor limits. `i740fb_set_par()` clears VRAM, protects VGA, writes clocks, sequencer, CRTC, graphics, attribute, extended i740 registers, FIFO watermarks, palette ramp, waits, and unprotects. Palette, pan, blank, probe, remove, suspend, and resume complete the driver.

Control flow: probe removes aperture conflicts, allocates fbdev state, enables PCI, requests regions, maps framebuffer and MMIO BARs, detects VRAM size and memory type, registers DDC if possible, reads EDID and selects best display mode or default/user mode, maximizes virtual y resolution, allocates cmap, registers fbdev, and enables write-combining if requested. Runtime set_par reprograms the chip from `info->var`. Suspend only marks fbdev suspended if users have it open; resume reprograms mode if active.

State and persistence: state is in `i740fb_par`, including register shadows and DDC registration. Open refcount gates suspend/resume reprogramming. `mode_option` and `mtrr` module parameters affect initial mode and write-combining. Hardware register state is not fully saved; resume regenerates it from current `info->var`.

Dependencies and integration points: depends on PCI, aperture removal, fbdev, I2C bit algorithm, DDC/EDID helpers, VGA MMIO helpers, console lock, and write-combining APIs. Uses IDs `0x00d1` and `0x7800`.

Risks: set_par clears the entire framebuffer on every mode set. Many hardware waits are fixed `mdelay()` values rather than status-driven. Suspend/resume do nothing when `ref_count == 0`, so hardware may not be restored for inactive but registered fbdev users until reopened or mode set. `pci_disable_device()` is commented out on teardown. DDC failure is nonfatal, but invalid EDID/mode fallback must be correct. Mode calculations contain many alignment and legacy VGA overflow fields that are easy to regress.

Test signals: PCI probe/remove with both device IDs, SGRAM/SDRAM memory detection, DDC success/failure and firmware EDID fallback, EDID best-mode selection and `mode_option` override, bpp-specific DAC speed rejection, virtual height memory clamping, set_par register trace for 8/16/24/32 bpp, pan address computation, DPMS modes, open/release refcount errors, suspend/resume with active and inactive refs, and write-combining enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i740fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/Makefile -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/Makefile

Purpose: defines how the Intel 810/815 framebuffer driver objects are built based on Kconfig options.

Important APIs, types, and functions: `obj-$(CONFIG_FB_I810) += i810fb.o` selects the composite object. `i810fb-objs` always includes `i810_main.o` and `i810_accel.o`. It conditionally adds `i810_gtf.o` when `CONFIG_FB_I810_GTF` is enabled, otherwise `i810_dvt.o`. It conditionally adds `i810-i2c.o` when `CONFIG_FB_I810_I2C` is enabled.

Control flow: build-time control decides whether runtime mode timing comes from GTF or DVT code and whether DDC/I2C support is compiled into the i810fb object.

State and persistence: no runtime state. The file persists build composition and therefore the available code paths in the module/built-in driver.

Dependencies and integration points: integrates with Linux kbuild and Kconfig symbols for `CONFIG_FB_I810`, `CONFIG_FB_I810_GTF`, and `CONFIG_FB_I810_I2C`. The `i810-i2c.c` file in this work item is included only through the I2C conditional.

Risks: misconfigured Kconfig combinations change available EDID and timing behavior. The file assumes object names remain stable; renames in source files must be reflected here.

Test signals: build matrix with `CONFIG_FB_I810` off/on, GTF on/off, and I2C on/off; verify `i810fb.o` links with the expected object list in each configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810-i2c.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810-i2c.c

Purpose: provides bit-banged I2C/DDC support for the Intel 810/815 framebuffer driver.

Important APIs, types, and functions: SCL/SDA direction/value masks define GPIO register protocol. `i810i2c_setscl()` and `i810i2c_setsda()` drive lines through the selected GPIO register and flush posted writes. `i810i2c_getscl()` and `i810i2c_getsda()` release lines and read input bits. `i810_setup_i2c_bus()` initializes an `i2c_adapter` and `i2c_algo_bit_data`, raises both lines, and registers the bus. `i810_create_i2c_busses()` sets up three channels on `GPIOA`, `GPIOB`, and `GPIOC`. `i810_delete_i2c_busses()` removes registered adapters. `i810_probe_i2c_connector()` reads EDID from a selected DDC channel or falls back to firmware EDID when `conn >= par->ddc_num`.

Control flow: the main i810 driver calls create during setup, then probes connectors for EDID. Each I2C transaction calls the bit-algo callbacks to manipulate GPIO registers. Delete is called during teardown to unregister adapters whose `par` remained set.

State and persistence: three `struct i810fb_i2c_chan` entries live in `struct i810fb_par`; each stores the adapter, bit-algo data, MMIO GPIO base, and back-pointer. Failed bus registration clears `chan->par`, which also acts as the registered/unregistered flag.

Dependencies and integration points: depends on `i810.h`, `i810_regs.h`, `i810_main.h`, fbdev EDID helpers, Linux I2C bit-banging, and MMIO helpers `i810_writel/readl`. Build is conditional on `CONFIG_FB_I810_I2C`.

Risks: `strcpy()` into `adapter.name` assumes fixed short names. `DEBUG` is always defined in this source, enabling verbose EDID printk paths when compiled. GPIO write protocol is hardware-specific and uses two writes for reads; missing flushes or register layout changes would break DDC. Firmware EDID fallback allocates with `kmemdup()` and transfers ownership to caller via `out_edid`.

Test signals: create/delete bus lifecycle, I2C read transactions on all three GPIO bases, failed `i2c_bit_add_bus()` handling, EDID read success/failure, firmware EDID fallback path, and teardown after partial bus registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810.h -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810.h

Purpose: central definition header for the Intel 810/815 framebuffer driver, covering raster ops, parser/blit command bits, version/device constants, memory sizes, masks, timing limits, cursor constants, resource flags, private structures, and MMIO helper macros.

Important APIs, types, and functions: constants define 2D engine commands, ROPs, pixel formats, parser/blit opcodes, PCI IDs, page/ring/cursor sizes, register masks, DPMS values, ring buffer masks, timing limits, cursor modes, AGP memory types, resource flags, and driver flags. Types include `struct gtt_data`, `struct mode_registers`, `struct heap_data`, `struct state_registers`, `struct i810fb_i2c_chan`, and `struct i810fb_par`. `struct i810fb_par` aggregates mode state, saved hardware state, AGP/GTT memory, fbops, PCI device, aperture/fb/ring/cursor heaps, VGA state, I2C channels, open locking, pseudo-palette, MMIO addresses, EDID pointer, pitch, pixel config, watermark, resource flags, and cursor/blit state. Macros `i810_read*`/`i810_write*` wrap MMIO access.

Control flow: implementation files use these definitions to allocate and populate `i810fb_par`, program modes and acceleration, save/restore state, manage AGP/GTT memory, drive I2C channels, and access MMIO registers.

State and persistence: this header defines the persistent in-memory state of the i810fb driver. It separates current mode registers from saved hardware registers, and tracks resource allocation flags so teardown can release partially acquired resources.

Dependencies and integration points: includes AGP backend, fbdev, I2C, bit I2C, VGA helpers, and list support. It is the common contract among `i810_main.o`, `i810_accel.o`, optional timing object, and optional `i810-i2c.o`.

Risks: macro argument order for `i810_readl(where, mmio)`/`i810_writel(where, mmio, val)` can be confusing; local callers sometimes pass variables named `mmio` first via wrappers in source. Many constants encode hardware contracts and timing assumptions. The private state is broad and cross-module, increasing coupling between acceleration, mode, PM, and I2C code.

Test signals: full i810 build with acceleration, timing, and I2C variants; static analysis for MMIO macro argument ordering; resource flag transitions in probe/remove; save/restore state coverage; and I2C channel integration tests when `CONFIG_FB_I810_I2C` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810.h -->
