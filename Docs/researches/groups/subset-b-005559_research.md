# subset-b-005559 Research

Grouped source research for Linux fbdev core framebuffer console, rotation, EDID/modeline, sysfs, memory registration, VGA helper, soft cursor, and system-memory drawing helpers. Each section is marker-delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon.c

## Purpose

`fbcon.c` implements the low-level framebuffer-backed Linux virtual console driver. It binds `struct consw fb_con` to VT consoles, maps virtual consoles to registered `struct fb_info` devices, selects bitblit/tile/rotation operations, manages fonts, cursors, boot logo placement, blanking, scrolling, and reacts to framebuffer registration, unregistration, mode changes, suspend/resume, and sysfs controls. The file was read as a complete 3377-line source.

## Important APIs, Types, and Functions

Important exported or cross-file entry points include `fb_console_init`, `fb_console_exit`, `fbcon_fb_registered`, `fbcon_fb_unregistered`, `fbcon_fb_unbind`, `fbcon_remap_all`, `fbcon_update_vcs`, `fbcon_modechange_possible`, `fbcon_mode_deleted`, `fbcon_delete_modelist`, `fbcon_fb_blanked`, `fbcon_new_modelist`, `fbcon_get_requirement`, `fbcon_set_con2fb_map_ioctl`, `fbcon_get_con2fb_map_ioctl`, `fbcon_suspended`, `fbcon_resumed`, and `fbcon_fill_cursor_mask`. The main persistent structures are `fb_display[MAX_NR_CONSOLES]`, `fbcon_registered_fb[FB_MAX]`, `con2fb_map[]`, `con2fb_map_boot[]`, `info_idx`, `primary_device`, logo state, font name, rotation state, margin color, cursor blink state, and the per-device `struct fbcon_par` allocated into `info->fbcon_par`.

## Control Flow

Startup creates `/sys/class/graphics/fbcon`, initializes all console-to-fb mappings to `-1`, and either registers deferred takeover with `dummycon` or waits for framebuffer registration. `fbcon_fb_registered()` records the `fb_info`, selects a primary device when enabled, and either defers takeover or calls `do_fbcon_takeover()`/`set_con2fb_map()` to bind the VT console driver. `fbcon_startup()` opens the chosen fbdev, creates `fbcon_par`, selects a font, computes rows/columns, and starts cursor work. VT callbacks then route text operations through `fbcon_clear`, `fbcon_putcs`, `fbcon_scroll`, `fbcon_switch`, `fbcon_blank`, `fbcon_set_font`, and related methods in `fb_con`.

Scrolling chooses between redraw, copyarea, ypan, and ywrap based on `fb_scrollmode()`, acceleration flags, pan/wrap steps, font height, and virtual resolution. Mode and rotation changes rebuild display state with `var_to_display()`, `display_to_var()`, `set_blitting_type()`, `updatescrollmode()`, palette programming, and screen redraws. Cursor blinking is delayed work that takes `console_trylock()`, checks active/visible text state, and calls the selected bitops cursor method.

## State and Persistence Behavior

State is kernel memory only. Per-console display settings persist in `fb_display[]`; per-framebuffer console state persists in `info->fbcon_par` until release/unregistration; mappings persist in `con2fb_map[]` and boot mapping overrides. Fonts use refcounted `font_data_t`. Cursor mask/source buffers and rotated font buffers are dynamically allocated and freed in `fbcon_release()`. There is no file-backed persistence, but sysfs writes to fbcon rotation and cursor blink immediately mutate runtime console state.

## Dependencies and Integration Points

The file integrates with VT/console core (`do_take_over_console`, `do_unregister_con_driver`, `vc_resize`, `update_screen`), fbdev core (`fb_set_var`, `fb_pan_display`, `fb_blank`, `fb_set_cmap`, `fb_get_color_depth`), fbcon bitops from normal/rotated/tile paths, font helpers, boot logo helpers, sysfs device groups, `vga_switcheroo`, module ownership/open/release callbacks, and userspace ioctl structures for `FBIOPUT_CON2FBMAP`/`FBIOGET_CON2FBMAP`.

## Risks and Edge Cases

The source explicitly documents incomplete locking: fbcon state is console-lock protected, but fbdev locking against userspace access is weak. Mode changes must reject resolutions smaller than active fonts. Rotation and ypan/ywrap calculations are sensitive to swapped dimensions and pan step divisibility. Deferred takeover must not leave stale output notifier state. Cursor work deliberately avoids blocking on console lock, so blinking can be skipped. Mapping/unregistration paths must avoid releasing an fbdev still mapped by another console. User fonts require size checks to prevent out-of-bounds glyph reads.

## Test Signals

Useful signals are fbdev registration/unregistration smoke tests, boot with `fbcon=map:`, `vc:`, `rotate:`, `margin:`, and `nodefer`; console switching across multiple fb devices; sysfs `fbcon/rotate`, `rotate_all`, and `cursor_blink`; `FBIOPUT_CON2FBMAP` remaps; font set/get for 256 and 512 glyph fonts; pan/wrap/scroll behavior with and without acceleration; suspend/resume blanking; mode deletion while a mode is active; and KASAN/lockdep coverage around cursor work and unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon.h

## Purpose

`fbcon.h` is the private interface shared by fbcon core, normal/rotated/tile bitops, and `softcursor.c`. It defines the per-console display cache, per-framebuffer console private state, bitops dispatch table, attribute decoding helpers, scrolling constants, and coordinate helpers. The file was read as a complete 236-line header.

## Important APIs, Types, and Functions

Key types are `struct fbcon_display`, `struct fbcon_bitops`, and `struct fbcon_par`. `fbcon_display` stores font data, scroll state, virtual rows, cursor shape, rotation, cached var fields, color bitfields, and current `fb_videomode`. `fbcon_bitops` is the operation vtable for `bmove`, `clear`, `putcs`, `clear_margins`, `cursor`, `update_start`, and optional `rotate_font`. `fbcon_par` stores copied `fb_var_screeninfo`, delayed cursor work, cursor state, active display pointer, owning `fb_info`, current console, cursor buffers, blank/graphics/rotation state, and rotated-font cache.

## Control Flow

The header has no standalone execution. Runtime dispatch flows from `fbcon.c` into whichever `fbcon_bitops` table was installed by `fbcon_set_bitops_ur`, `fbcon_set_bitops_cw`, `fbcon_set_bitops_ud`, `fbcon_set_bitops_ccw`, or tileblit setup. Inline helpers `real_y()`, `get_attribute()`, `mono_col()`, `fb_scrollmode()`, and `FBCON_SWAP()` are used throughout drawing, scrolling, and rotation paths.

## State and Persistence Behavior

The header defines the shapes of in-memory state but owns no storage. Its structures are long-lived while a console is mapped to a framebuffer. Rotation buffers, cursor image/mask buffers, and font references require coordinated allocation/free by implementation files.

## Dependencies and Integration Points

It depends on Linux font, VT buffer, VT kernel, workqueue, I/O, fbdev, and console data types. It exposes `soft_cursor()` and `fbcon_fill_cursor_mask()` to rotated cursor paths, and exposes scroll constants used by `fbcon_rotate.h` to decide whether to use physical or virtual x/y resolution.

## Risks and Edge Cases

The layout is private but widely shared inside fbcon; mismatched assumptions in one bitops implementation can corrupt cursor or font buffers. `FBCON_SWAP()` relies on comparable operand types. `get_attribute()` only reports underline/reverse/bold for 1-bit color depth, so rotated attribute rendering depends on fb depth classification.

## Test Signals

Build coverage with all relevant configs is important: normal fbcon, `CONFIG_FRAMEBUFFER_CONSOLE_ROTATION`, `CONFIG_FRAMEBUFFER_CONSOLE_LEGACY_ACCELERATION`, and `CONFIG_FB_TILEBLITTING`. Runtime signals include correct scroll mode selection, rotated drawing, 512-glyph font handling, monochrome attribute rendering, and cursor shape changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_ccw.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_ccw.c

## Purpose

`fbcon_ccw.c` implements framebuffer console bitops for 270-degree counter-clockwise software rotation. It lets the common fbcon engine draw logical text cells while mapping them into rotated framebuffer coordinates and rotated glyph data. The file was read as a complete 376-line source.

## Important APIs, Types, and Functions

The public handoff is `fbcon_set_bitops_ccw(struct fbcon_par *par)`, which installs `ccw_fbcon_bitops`. Internal operations are `ccw_bmove`, `ccw_clear`, `ccw_putcs`, `ccw_clear_margins`, `ccw_cursor`, `ccw_update_start`, and `ccw_update_attr`. Text blits use `fb_copyarea`, `fb_fillrect`, `fb_imageblit`, `fb_get_buffer_offset`, `fb_pad_aligned_buffer`, and the rotated glyph cache in `par->rotated.buf`.

## Control Flow

`fbcon.c` selects this table when `par->rotate == FB_ROTATE_CCW`. Logical cell copy/clear operations compute framebuffer rectangles with x based on logical rows and y mirrored from `GETVYRES()`. `ccw_putcs()` reverses the input glyph order, batches cells to fit the pixmap scratch buffer, optionally applies monochrome underline/bold/reverse attributes, pads glyph data to pixmap alignment, and calls `fb_imageblit()`. Cursor drawing builds a `struct fb_cursor` with rotated dimensions and position, rotates the cursor mask with `font_glyph_rotate_270()`, tries hardware `fb_cursor`, and falls back to `soft_cursor()`.

## State and Persistence Behavior

No file-local persistent state exists. The function mutates `par->cursor_state`, `par->cursor_data`, `par->p->cursor_shape`, and `par->var` during cursor and pan updates. Temporary attribute buffers are allocated per draw/cursor update.

## Dependencies and Integration Points

The file depends on `fbcon.h`, `fbcon_rotate.h`, VT cursor/font state, font rotation helpers, and fbdev drawing callbacks. `ccw_update_start()` integrates with core panning by translating logical offsets into rotated `xoffset`/`yoffset` and calling `fb_pan_display()`.

## Risks and Edge Cases

Coordinate transforms depend on virtual y resolution and scroll mode. Mask generation uses atomic allocation in cursor paths and can silently skip updates on allocation failure. Attribute rendering is meaningful mainly for monochrome. `par->rotated.buf` must have been prepared by `fbcon_rotate_font()`; otherwise drawing returns without output.

## Test Signals

Use `fbcon=rotate:3` or sysfs rotation to verify text, scrolling, margins, cursor position, pan/wrap update, 256/512 glyph fonts, and hardware-cursor fallback. KASAN is useful for reversed glyph iteration and cursor mask sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_ccw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_cw.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_cw.c

## Purpose

`fbcon_cw.c` implements framebuffer console bitops for 90-degree clockwise software rotation. It maps logical console rows and columns into rotated framebuffer rectangles and renders from a cached rotated font buffer. The file was read as a complete 359-line source.

## Important APIs, Types, and Functions

The exported internal setup API is `fbcon_set_bitops_cw(struct fbcon_par *par)`, which installs `cw_fbcon_bitops`. Core helpers are `cw_bmove`, `cw_clear`, `cw_putcs`, `cw_clear_margins`, `cw_cursor`, `cw_update_start`, and `cw_update_attr`. These operate through `struct fb_copyarea`, `struct fb_fillrect`, `struct fb_image`, `struct fb_cursor`, and `par->rotated`.

## Control Flow

After fbcon selects clockwise rotation, copy and clear calls translate logical y into mirrored framebuffer x using `GETVXRES()`, and logical x into framebuffer y. `cw_putcs()` computes one-cell rotated glyph size from font height, batches glyphs by pixmap capacity, applies attributes into a temporary cell buffer when needed, pads each rotated glyph into the scratch pixmap, then issues one `fb_imageblit()` per batch. `cw_cursor()` mirrors the same geometry for cursor image, uses `font_glyph_rotate_90()` for the mask, then tries driver cursor support before `soft_cursor()`.

## State and Persistence Behavior

State lives in caller-owned `fbcon_par`: cursor image/cmap/position cache, cursor data, cursor mask, display cursor shape, rotated font cache, and current panning var. There is no persistent storage outside kernel memory.

## Dependencies and Integration Points

This file integrates with `fbcon_rotate_font()` through the vtable's `rotate_font` pointer, fbdev hardware callbacks (`fb_copyarea`, `fb_fillrect`, `fb_imageblit`, `fb_cursor`), and core `fb_pan_display()`. It relies on `fbcon_fill_cursor_mask()` and font helpers from the console/font subsystem.

## Risks and Edge Cases

Clockwise geometry must account for virtual x resolution only when panning can use it. Allocation failure for attribute or mask buffers drops a draw/cursor update. Incorrect pixmap alignment or `maxcnt` calculation would corrupt glyph batches. The file returns early if rotated font data is not available.

## Test Signals

Test `rotate:1` on framebuffer devices with and without xpan support, wide and narrow fonts, monochrome attributes, cursor shape changes, scrolling, and sysfs rotation changes. Hardware cursor failure should still display via `soft_cursor()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_cw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_rotate.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_rotate.c

## Purpose

`fbcon_rotate.c` owns the common rotated-font cache builder used by the clockwise, upside-down, and counter-clockwise fbcon bitops. The file was read as a complete 52-line source.

## Important APIs, Types, and Functions

Its sole function is `fbcon_rotate_font(struct fb_info *info, struct vc_data *vc)`. It checks `par->p->fontdata` and `par->rotate` against `par->rotated.fontdata` and `par->rotated.buf_rotate`, synchronizes the framebuffer if the driver provides `fb_sync`, then calls `font_data_rotate()` to create or reuse `par->rotated.buf`.

## Control Flow

Rotated bitops expose this function in their vtable. During console init or switch, `fbcon.c` calls `par->bitops->rotate_font(info, vc)` when present. If the cache already matches the current font and rotation, it returns immediately. On successful rotation it stores the returned buffer and size; on failure it frees and clears the old rotated buffer and returns the error.

## State and Persistence Behavior

The function mutates only the `par->rotated` cache. That cache persists for the life of `info->fbcon_par` and is released in `fbcon_release()`. There is no external persistence.

## Dependencies and Integration Points

It depends on fbdev, console font metadata, `font_data_rotate()`, optional driver `fb_sync`, and the private `fbcon_par` fields from `fbcon.h`.

## Risks and Edge Cases

If rotation allocation fails, the code clears the buffer to avoid stale rotated output; fbcon may then fall back to unrotated bitops. Reusing buffers requires exact fontdata and rotation matches; font lifetime is protected by the surrounding fbcon font reference model.

## Test Signals

Exercise rotation changes after font changes, switching between rotated consoles, allocation-failure paths, and drivers with asynchronous blits requiring `fb_sync`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_rotate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_rotate.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_rotate.h

## Purpose

`fbcon_rotate.h` declares the shared rotation helpers and resolution-selection macros used by rotated fbcon bitops. The file was read as a complete 37-line header.

## Important APIs, Types, and Functions

The header declares `fbcon_rotate_font()` and, when `CONFIG_FRAMEBUFFER_CONSOLE_ROTATION` is enabled, `fbcon_set_bitops_cw`, `fbcon_set_bitops_ud`, and `fbcon_set_bitops_ccw`. Otherwise those setters compile to empty inline stubs. `GETVYRES()` and `GETVXRES()` choose physical or virtual resolution depending on scroll mode and xpan support.

## Control Flow

There is no standalone flow. Rotated bitops call the macros while translating logical console coordinates to framebuffer coordinates. `fbcon.c` calls the bitops setters through `fbcon_set_bitops()` based on requested rotation.

## State and Persistence Behavior

No state is stored here. The macros inspect `fbcon_display`, `fb_info->var`, and `fb_info->fix`.

## Dependencies and Integration Points

It depends on scroll-mode constants from `fbcon.h` and fbdev resolution fields. It is the compile-time bridge between optional rotation support and the common fbcon core.

## Risks and Edge Cases

Wrong physical-versus-virtual resolution selection causes rotated text, cursor, and margins to be offset when panning or wrapping is active. Empty stubs mean callers must only expect actual rotation when the config option is enabled.

## Test Signals

Build both with and without `CONFIG_FRAMEBUFFER_CONSOLE_ROTATION`, and test rotated panning on hardware with `xpanstep`, `ypanstep`, and redraw-only modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_rotate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_ud.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_ud.c

## Purpose

`fbcon_ud.c` implements framebuffer console bitops for 180-degree upside-down software rotation. It mirrors logical console output across both framebuffer axes while preserving the common fbcon rendering API. The file was read as a complete 410-line source.

## Important APIs, Types, and Functions

`fbcon_set_bitops_ud(struct fbcon_par *par)` installs `ud_fbcon_bitops`. Internal helpers include `ud_bmove`, `ud_clear`, `ud_putcs`, `ud_putcs_aligned`, `ud_putcs_unaligned`, `ud_clear_margins`, `ud_cursor`, `ud_update_start`, and `ud_update_attr`. The code uses `fb_copyarea`, `fb_fillrect`, `fb_imageblit`, `fb_pan_display`, `fb_get_buffer_offset`, aligned and unaligned glyph padding, and `font_glyph_rotate_180()`.

## Control Flow

Logical copy/clear operations mirror both x and y using `GETVXRES()` and `GETVYRES()`. `ud_putcs()` starts from the last character in the requested run because upside-down rendering reverses order, builds a framebuffer image batch, and chooses aligned or unaligned padding based on font width modulo 8. `ud_cursor()` mirrors the active glyph and cursor mask, sets cursor image/cmap/size/position only when changed or reset, and falls back to `soft_cursor()` if hardware cursor handling fails. `ud_update_start()` translates logical pan offsets into mirrored x/y offsets.

## State and Persistence Behavior

All persistent state is in `fbcon_par`: rotated font buffer, cursor cache, cursor data/mask, cursor shape, and copied `var`. Temporary attribute buffers are allocated per operation. No external persistence exists.

## Dependencies and Integration Points

The file integrates with the rotated font cache from `fbcon_rotate.c`, common cursor mask generation in `fbcon.c`, fbdev drawing and panning callbacks, and VT font/cursor metadata.

## Risks and Edge Cases

The unaligned glyph path is sensitive to shift and destination stride math. Mirrored pan offsets can go negative and require wrap correction. Allocation failure in cursor path skips updates. As in other rotated files, no glyph output happens if `par->rotated.buf` is absent.

## Test Signals

Use `rotate:2` with odd-width fonts, 512-character fonts, accelerated and non-accelerated devices, cursor shape changes, bottom/right margin clears, and pan/scroll operations under KASAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon_ud.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcvt.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcvt.c

## Purpose

`fbcvt.c` computes VESA Coordinated Video Timings for fbdev modes requested through the `M`/`R` modeline syntax. It turns resolution, refresh, margins, reduced blanking, and interlace flags into a `struct fb_videomode`. The file was read as a complete 368-line source.

## Important APIs, Types, and Functions

The public API is `fb_find_mode_cvt(struct fb_videomode *mode, int margins, int rb)`. Internal state is `struct fb_cvt_data`, which holds active resolution, refresh, pixel clock, horizontal/vertical totals, blanking, margins, sync widths, aspect ratio, flags, and status. Helpers calculate horizontal period, ideal duty cycle, horizontal blanking, hsync, vertical blanking lines, total lines, pixel clock, aspect ratio, printable CVT name, and conversion into `fb_videomode`.

## Control Flow

The caller pre-fills `mode->xres`, `mode->yres`, `mode->refresh`, and `mode->vmode`. `fb_find_mode_cvt()` validates nonzero input, marks non-standard refresh/aspect cases, rounds x resolution to 8-pixel cells, doubles field refresh for interlace, computes optional margins, derives aspect-specific vsync, calculates totals/blanking/porches/clock, logs the CVT name, and writes the timing fields back to `mode`.

## State and Persistence Behavior

All computation is stack-local. The only side effect outside the output mode is informational kernel logging for invalid/non-standard/advisory cases and the generated CVT name.

## Dependencies and Integration Points

`modedb.c` calls this from `fb_find_mode()` when parsing mode strings with CVT syntax. It uses fbdev macros such as `KHZ2PICOS` and mode flags like `FB_VMODE_INTERLACED`, `FB_SYNC_HOR_HIGH_ACT`, and `FB_SYNC_VERT_HIGH_ACT`.

## Risks and Edge Cases

The code does integer arithmetic throughout; overflow and truncation risks grow with very large resolutions or refresh rates, partially mitigated by `f_refresh > INT_MAX`. Reduced blanking is advisory for 60 Hz but not forbidden. Non-standard aspect ratios still compute timings but mark status.

## Test Signals

Test `fb_find_mode()` strings such as `1024x768M`, `1920x1080MR-32@60`, interlaced modes, margins, invalid zero dimensions, high refresh values, and compare generated timings with known CVT references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcvt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbmem.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbmem.c

## Purpose

`fbmem.c` is the fbdev core registration and setup layer for framebuffer devices. It owns the graphics class, the global registered framebuffer table, registration lifetime, mode setting, panning validation, blanking, pixmap scratch-buffer helpers, suspend notifications, and modelist validation. The file was read as a complete 754-line source.

## Important APIs, Types, and Functions

Global state includes `struct class *fb_class`, `registered_fb[FB_MAX]`, `num_registered_fb`, and `registration_lock`. Exported APIs include `get_fb_info`, `put_fb_info`, `fb_get_color_depth`, `fb_pad_aligned_buffer`, `fb_pad_unaligned_buffer`, `fb_get_buffer_offset`, `fb_pan_display`, `fb_set_var`, `fb_blank`, `register_framebuffer`, `unregister_framebuffer`, `devm_register_framebuffer`, `fb_set_suspend`, `fb_new_modelist`, and `fb_modesetting_disabled`.

## Control Flow

`fbmem_init()` creates the graphics class, procfs, character device, and fbcon device. `register_framebuffer()` takes `registration_lock`, validates endian/math support, picks a free node, initializes modelist/refcount/locks, creates `/sys/class/graphics/fbN`, allocates a default pixmap buffer if needed, fills blit capability bitmaps, registers PM VT-switch requirements, stores the device in `registered_fb[]`, and notifies fbcon through `fbcon_fb_registered()`. Unregistration destroys sysfs, unbinds fbcon, frees default pixmap/modelist state, removes the table entry, notifies fbcon, and drops the final reference.

`fb_set_var()` validates FOURCC bitfields, minimum size, multiplication overflow, driver `fb_check_var`, virtual resolution, console blit capabilities, driver `fb_set_par`, panning, colormap, modelist insertion, and LCD mode notifications. `fb_pan_display()` checks pan/wrap steps and virtual bounds before calling the driver.

## State and Persistence Behavior

All state is in kernel memory. `registered_fb[]` and `num_registered_fb` persist until unregister; `fb_info->node`, locks, refcount, pixmap, modelist, blank state, and device object are initialized on registration. `fb_info->var`, `blank`, `state`, and modelist mutate during runtime sysfs/ioctl/driver operations.

## Dependencies and Integration Points

It integrates with fbcon (`fbcon_*` callbacks), sysfs (`fb_device_create/destroy`), procfs/chrdev helpers, LCD/backlight LED notification, PM VT-switch requirements, modelist helpers from `modedb.c`, notifier chains for special configs, and `video_firmware_drivers_only()` for `nomodeset`.

## Risks and Edge Cases

Locking is split between `registration_lock`, `fb_info->lock`, and console lock; fbcon comments note historical lock hazards. Registration must not exceed `FB_MAX` or leak modelist nodes on partial failure. `fb_set_var()` temporarily mutates `info->var` and must restore on driver or modelist failure. Panning rejects unsupported step alignment. Foreign-endian framebuffers require matching kernel config.

## Test Signals

Register/unregister drivers repeatedly, exercise devm cleanup, sysfs mode changes, pan bounds, FOURCC validation, tiny/overflow resolutions, modelist replacement, suspend/resume calls under console lock, `nomodeset`, and KASAN/lockdep during concurrent userspace fb access and console activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbmon.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbmon.c

## Purpose

`fbmon.c` parses monitor EDID data, builds fbdev mode databases from EDID descriptors, computes VESA Generalized Timing Formula modes, converts generic `videomode` objects to fbdev modes, validates modes against monitor specs, and exposes firmware EDID for primary adapters. The file was read as a complete 1525-line source.

## Important APIs, Types, and Functions

Exported APIs are `fb_parse_edid`, `fb_edid_to_monspecs`, `fb_get_mode`, `fb_validate_mode`, `fb_destroy_modedb`, `fb_firmware_edid`, and, when enabled, `fb_videomode_from_videomode` and `of_get_fb_videomode`. Internal helpers classify EDID descriptor blocks, repair known-bad EDIDs via `brokendb`, check header/checksum, parse vendor/display/chroma/DPMS data, derive established/standard/detailed timings, create a `struct fb_videomode` array, estimate monitor limits, and compute GTF timing values using `struct __fb_timings`.

## Control Flow

EDID paths first apply known fixups and validate checksum/header. `fb_parse_edid()` returns the first detailed timing in `fb_var_screeninfo`. `fb_edid_to_monspecs()` clears and fills `struct fb_monspecs`, parses vendor strings and descriptors, derives limits, populates display capabilities, creates `specs->modedb`, and clears the preferred-detailed flag if no detailed mode exists. `fb_create_modedb()` collects detailed timings, established timings, standard timings, and descriptor standard timing blocks into a compact allocated array. `fb_get_mode()` calculates GTF timings from vertical refresh, horizontal frequency, pixel clock, or maximum monitor limits, then writes margins/sync/pixclock to `var`.

## State and Persistence Behavior

The file owns only static EDID fixup tables. Mode databases are dynamically allocated and owned by the caller until `fb_destroy_modedb()`. `fb_edid_to_monspecs()` stores parsed fields and allocated `modedb` inside caller-provided `struct fb_monspecs`.

## Dependencies and Integration Points

It integrates with `modedb.c` tables (`vesa_modes`, `dmt_modes`), fbdev monitor structures, firmware/sysfb EDID, PCI ROM resource flags, devicetree videomode helpers, and display timing flags from the video subsystem. It is usually consumed by fbdev drivers during probe/mode validation.

## Risks and Edge Cases

EDID parsing is byte-offset heavy and depends on macros from `edid.h`; malformed EDID can produce no modes or require fixups. `fb_create_modedb()` initially allocates room for 50 modes, so unexpected descriptor expansion would be risky if source assumptions change. GTF integer math can reject modes outside monitor limits and uses safe 640x480 defaults when specs are invalid. Firmware EDID is only returned for shadow-ROM primary devices.

## Test Signals

Use valid EDIDs, all-null/bad-checksum headers, known broken DEC/ViewSonic/Sharp entries, EDIDs with no detailed timings, high pixel-clock modes, standard timing descriptors, devicetree display timings, GTF mode generation under each flag, and validation against min/max hfreq/vfreq/dclk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbsysfs.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbsysfs.c

## Purpose

`fbsysfs.c` creates and implements the `/sys/class/graphics/fbN` attribute group for each registered fbdev. It lets userspace inspect and request mode, mode list, bpp, virtual size, stride, blanking, panning, rotation, suspend state, and optional backlight curve changes. The file was read as a complete 481-line source.

## Important APIs, Types, and Functions

Public functions are `fb_device_create(struct fb_info *fb_info)` and `fb_device_destroy(struct fb_info *fb_info)`. Attribute handlers include `store_mode/show_mode`, `store_modes/show_modes`, `store_bpp/show_bpp`, `store_rotate/show_rotate`, `store_virtual/show_virtual`, `store_blank/show_blank`, `store_pan/show_pan`, `show_name`, `show_stride`, `store_fbstate/show_fbstate`, and optional `store_bl_curve/show_bl_curve`. `activate()` is the shared mode-changing helper.

## Control Flow

`fb_device_create()` is called during framebuffer registration and creates `fb%d` under `fb_class` with `fb_device_groups`. Mode-changing stores copy `fb_info->var`, mutate requested fields, and call `activate()`, which forces activation under `console_lock` and `lock_fb_info`, calls `fb_set_var()`, then updates fbcon VCs. `store_modes()` replaces the modelist from a binary array of `struct fb_videomode`, validates it through `fb_new_modelist()`, and restores the old list on failure. Blanking and panning call `fb_blank()`/`fb_pan_display()` under console lock.

## State and Persistence Behavior

Sysfs attributes mutate runtime `fb_info` state: `var`, `mode`, `modelist`, `blank`, `state`, and optional `bl_curve`. Attribute files persist only while the device exists. `fb_info->dev` is set on creation and cleared on destroy.

## Dependencies and Integration Points

This layer integrates with fbdev core (`fb_set_var`, `fb_new_modelist`, `fb_pan_display`, `fb_blank`, `fb_set_suspend`), fbcon update/blank callbacks, class device infrastructure, VT console locking, and optional backlight state.

## Risks and Edge Cases

Parsing uses simple comma/number formats for virtual size and pan, and binary struct input for `modes`; invalid sizes return `-EINVAL`. Some attributes (`console`, `cursor`) are stubs returning zero. `store_blank()` calls `fbcon_fb_blanked()` after `fb_blank()` and comments that blanking may recurse. `store_modes()` must preserve the old modelist if the new one is unusable.

## Test Signals

Read/write each attribute, test invalid mode strings and binary mode sizes, verify fbcon updates after `bits_per_pixel`, `mode`, `modes`, `rotate`, and `virtual_size`, check pan bounds, blank/unblank notification, suspend state writes, and backlight curve validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbsysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/modedb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/modedb.c

## Purpose

`modedb.c` provides the fbdev standard video mode database and helpers for parsing mode strings, selecting valid modes, converting between `fb_var_screeninfo` and `fb_videomode`, maintaining per-framebuffer modelists, and choosing preferred display modes. The file was read as a complete 1209-line source.

## Important APIs, Types, and Functions

It defines the static `modedb[]`, exported `vesa_modes[]`, and exported `dmt_modes[]`. Public APIs include `fb_find_mode`, `fb_var_to_videomode`, `fb_videomode_to_var`, `fb_mode_is_equal`, `fb_find_best_mode`, `fb_find_nearest_mode`, `fb_match_mode`, `fb_add_videomode`, `fb_delete_videomode`, `fb_destroy_modelist`, `fb_videomode_to_modelist`, `fb_find_best_display`, and the exported `fb_find_mode_cvt` hook from `fbcvt.c`.

## Control Flow

`fb_find_mode()` uses the caller-provided database or built-in `modedb`, then parses mode option syntax by scanning backward for refresh, bpp, resolution, CVT/reduced-blanking, interlace/progressive, and margin flags. CVT requests call `fb_find_mode_cvt()` and validate with `fb_try_mode()`. Named or resolution requests search for exact refresh/interlace matches, then nearest refresh, then best-fit resolution. If parsing fails or no request succeeds, it tries the default mode and finally all database modes. List helpers compare exact timings, add only non-duplicates, delete all matching entries, and free list nodes.

## State and Persistence Behavior

Built-in mode arrays are static read-only. Dynamic modelists are caller-owned lists of `struct fb_modelist` nodes allocated by `fb_add_videomode()` and freed by `fb_destroy_modelist()` or `fb_delete_videomode()`. Conversion helpers mutate only caller-provided structs.

## Dependencies and Integration Points

It integrates with fbdev driver `fb_check_var`, EDID parsing (`fbmon.c` consumes VESA/DMT tables), CVT generation (`fbcvt.c`), sysfs modelist replacement, framebuffer registration, and fbcon resize/mode matching.

## Risks and Edge Cases

Mode string parsing is permissive but order-sensitive; malformed suffixes fall through to fallback modes. `fb_try_mode()` only calls a driver check if present. Exact mode equality compares timings, sync, and vmode but not names/flags. `fb_find_best_display()` depends on EDID physical dimensions and preferred-detail flags, falling back to first detailed or first mode.

## Test Signals

Test mode strings by name and resolution, with `-bpp`, `@refresh`, `M`, `R`, `i`, `p`, and `m`; driver `fb_check_var` rejection; duplicate list insertion; modelist delete/destroy; nearest/best mode choices; EDID preferred mode selection; and conversion round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/modedb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/softcursor.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/softcursor.c

## Purpose

`softcursor.c` implements a generic software cursor fallback for framebuffer console when a driver does not provide or accept hardware cursor updates. The file was read as a complete 76-line source.

## Important APIs, Types, and Functions

The single API is `soft_cursor(struct fb_info *info, struct fb_cursor *cursor)`. It uses `info->pixmap` as a scratch destination, `par->cursor_src` and `par->cursor_size` for a cached combined `struct fb_image` plus cursor bitmap, and the driver `fb_imageblit` callback for final drawing.

## Control Flow

If the framebuffer is not running, it returns without drawing. It computes source pitch and data size from cursor image dimensions. If the cached buffer is the wrong size, it reallocates it with `GFP_ATOMIC`. For enabled cursors it combines image data and mask using `ROP_XOR` or `ROP_COPY`; for disabled cursors it copies the image data unchanged. It pads the temporary image into the framebuffer pixmap scratch buffer and calls `fb_imageblit()`.

## State and Persistence Behavior

Persistent state is stored in `info->fbcon_par`: `cursor_src` and `cursor_size` survive across cursor updates and are freed by `fbcon_release()`. No file or userspace state is stored.

## Dependencies and Integration Points

It depends on `fbcon_par` from `fbcon.h`, fbdev pixmap helpers (`fb_get_buffer_offset`, `fb_pad_aligned_buffer`), and the framebuffer driver's imageblit operation. Rotated and normal fbcon cursor paths call it when hardware cursor setup returns an error.

## Risks and Edge Cases

Allocation is atomic and can fail under pressure. The code assumes `cursor->image.data` and `cursor->mask` cover the computed bitmap size. Drivers without `fb_imageblit` cannot use this fallback safely. The shared pixmap buffer may require `fb_sync` through `fb_get_buffer_offset()`.

## Test Signals

Force hardware cursor failure, test XOR and COPY cursor rops, enable/disable transitions, varying cursor sizes and masks, suspended framebuffer state, and KASAN coverage for image/mask sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/softcursor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/svgalib.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/svgalib.c

## Purpose

`svgalib.c` provides common utility routines for VGA/SVGA fbdev drivers: register bitfield writes, default VGA register programming, text tile operations, cursor setup in text mode, blit capability reporting, PLL search, CRT timing validation/programming, and pixel format matching. The file was read as a complete 664-line source.

## Important APIs, Types, and Functions

Exported APIs include `svga_wcrt_multi`, `svga_wseq_multi`, `svga_set_default_gfx_regs`, `svga_set_default_atc_regs`, `svga_set_default_seq_regs`, `svga_set_default_crt_regs`, `svga_set_textmode_vga_regs`, `svga_settile`, `svga_tilecopy`, `svga_tilefill`, `svga_tileblit`, `svga_tilecursor`, `svga_get_tilemax`, `svga_get_caps`, `svga_compute_pll`, `svga_check_timings`, `svga_set_timings`, and `svga_match_format`. Internal helper `svga_regset_size()` calculates encodable range for split register fields.

## Control Flow

Register helpers iterate `struct vga_regset` entries and write sequential bits from an integer value into CRT or sequencer registers. Default setup writes standard VGA graphics, attribute, sequencer, CRTC, and text-mode registers. Tile functions operate directly on `info->screen_base` using text-mode strides derived from `fix.type_aux`. PLL computation chooses a divider range, checks VCO bounds, then searches `m/n` pairs for the closest frequency. Timing validation rounds horizontal values to 8 pixels and checks every derived total/start/end against register capacity; programming writes those fields and sync polarity to VGA registers.

## State and Persistence Behavior

The file owns no persistent state. It writes hardware MMIO/PIO-visible VGA registers and framebuffer text memory through caller-provided bases, so persistence is device hardware state until changed by a driver or mode switch.

## Dependencies and Integration Points

It depends on `<linux/svga.h>`, VGA register accessors, fbdev tile/caps/timing/format structures, and is used by SVGA-style framebuffer drivers to avoid duplicating common VGA programming logic.

## Risks and Edge Cases

Incorrect register-set descriptors can misprogram hardware. `svga_settile()` only supports 8x16x1 fonts with 256 entries. Tile copy must handle overlapping source/destination order. PLL arithmetic checks one overflow case but relies on valid bounds. Timing validation must be called before programming to avoid out-of-range register writes.

## Test Signals

Driver tests should cover default register init, text tile rendering/copy/fill/blit/cursor, PLL boundary frequencies, invalid timing totals, sync polarity, format fallback, 4-bpp capability constraints, and hardware readback where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/svgalib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/syscopyarea.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/syscopyarea.c

## Purpose

`syscopyarea.c` is the system-memory wrapper for packed-pixel framebuffer area copy. It exposes a standard fbdev helper that warns if used on a framebuffer not marked as virtual-address accessible, then delegates to the generic copy implementation. The file was read as a complete 30-line source.

## Important APIs, Types, and Functions

The single exported API is `sys_copyarea(struct fb_info *p, const struct fb_copyarea *area)`. It includes `sysmem.h` and `fb_copyarea.h`, with optional `FB_REV_PIXELS_IN_BYTE` enabled by `CONFIG_FB_SYS_REV_PIXELS_IN_BYTE`.

## Control Flow

On each call, the function checks `p->flags & FBINFO_VIRTFB`. If absent, it emits a one-time framebuffer warning. It then calls `fb_copyarea(p, area)` to perform the actual memory copy.

## State and Persistence Behavior

No local state is owned. The one-time warning state is managed by the fb warning helper. The operation mutates framebuffer memory described by `fb_info`.

## Dependencies and Integration Points

Framebuffer drivers use this helper as their `fbops->fb_copyarea` implementation when screen memory is CPU-addressable system memory. It integrates with generic packed-pixel copy macros and optional bit-reversal configuration.

## Risks and Edge Cases

Using this on MMIO-only or otherwise non-virtual framebuffer memory is unsafe, hence the warning. Correct clipping/overlap behavior depends on `fb_copyarea()` and valid `area` fields supplied by callers.

## Test Signals

Test with `FBINFO_VIRTFB` set and unset, overlapping copies, reversed pixels in byte config, different bpp modes, and fbcon scroll paths that call copyarea.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/syscopyarea.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/sysfillrect.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/sysfillrect.c

## Purpose

`sysfillrect.c` is the system-memory wrapper for packed-pixel framebuffer rectangle fills. It validates that the framebuffer is expected to be virtually addressable and then delegates to the generic fill implementation. The file was read as a complete 30-line source.

## Important APIs, Types, and Functions

The single exported API is `sys_fillrect(struct fb_info *p, const struct fb_fillrect *rect)`. It includes `sysmem.h` and `fb_fillrect.h`, with optional byte pixel reversal via `CONFIG_FB_SYS_REV_PIXELS_IN_BYTE`.

## Control Flow

`sys_fillrect()` checks for `FBINFO_VIRTFB`; missing support produces a one-time warning. It then calls `fb_fillrect(p, rect)` to perform the fill.

## State and Persistence Behavior

No file-local state exists. The operation mutates framebuffer memory according to `rect`; warning suppression state belongs to the common warning helper.

## Dependencies and Integration Points

Framebuffer drivers use this as `fbops->fb_fillrect` for CPU-addressable packed-pixel framebuffers. Fbcon clear and margin paths commonly reach this helper through driver fbops.

## Risks and Edge Cases

The helper should not be used for non-virtual framebuffers. Correct raster operation, color interpretation, clipping, and bpp handling are delegated to `fb_fillrect()`.

## Test Signals

Test fill rectangles across bpp modes, ROP_COPY and other supported rops, reversed-pixel config, warning behavior without `FBINFO_VIRTFB`, and fbcon clear/margin workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/sysfillrect.c -->
