<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon.c

## Purpose

`fbcon.c` implements the low-level framebuffer-backed Linux virtual console driver. It binds `struct consw fb_con` to VT consoles, maps virtual consoles to registered `struct fb_info` devices, selects bitblit/tile/rotation operations, manages fonts, cursors, boot logo placement, blanking, scrolling, and reacts to framebuffer registration, unregistration, mode changes, suspend/resume, and sysfs controls. The file was read as a complete 3377-line source.

## Important APIs, Types, and Functions

Important exported or cross-file entry points include `fb_console_init`, `fb_console_exit`, `fbcon_fb_registered`, `fbcon_fb_unregistered`, `fbcon_fb_unbind`, `fbcon_remap_all`, `fbcon_update_vcs`, `fbcon_modechange_possible`, `fbcon_mode_deleted`, `fbcon_delete_modelist`, `fbcon_fb_blanked`, `fbcon_new_modelist`, `fbcon_get_requirement`, `fbcon_set_con2fb_map_ioctl`, `fbcon_get_con2fb_map_ioctl`, `fbcon_suspended`, `fbcon_resumed`, and `fbcon_fill_cursor_mask`. Main state includes `fb_display[]`, `fbcon_registered_fb[]`, `con2fb_map[]`, `con2fb_map_boot[]`, `info_idx`, `primary_device`, logo/font/rotation settings, scrollback counters, and per-device `info->fbcon_par`.

## Control Flow

Startup creates `/sys/class/graphics/fbcon`, initializes mappings, and either registers deferred takeover with `dummycon` or waits for framebuffer registration. `fbcon_fb_registered()` records the fbdev, selects primary hardware when enabled, and calls takeover/remap paths when takeover is not deferred. VT callbacks route text operations through `fbcon_clear`, `fbcon_putcs`, `fbcon_scroll`, `fbcon_switch`, `fbcon_blank`, and font/palette helpers. Scrolling chooses redraw, copyarea, ypan, or ywrap based on acceleration flags, pan/wrap steps, virtual size, and font geometry. Cursor blinking runs as delayed work and draws through the active bitops cursor function.

## State and Persistence Behavior

State is kernel memory only. Per-console display settings live in `fb_display[]`; per-framebuffer console state lives in `fbcon_par`; mappings live in `con2fb_map[]`. Fonts are refcounted, while cursor buffers and rotated font buffers are dynamically allocated and freed by `fbcon_release()`. Sysfs writes mutate runtime rotation and cursor blink state but do not persist to disk.

## Dependencies and Integration Points

The file integrates with VT/console core, fbdev core (`fb_set_var`, `fb_pan_display`, `fb_blank`, `fb_set_cmap`), fbcon bitops, font helpers, boot logo helpers, sysfs device groups, `vga_switcheroo`, module ownership/open/release callbacks, and userspace con2fb ioctls.

## Risks and Edge Cases

The source documents incomplete fbdev/userspace locking. Mode changes must reject resolutions smaller than active fonts. Rotation, ypan, and ywrap calculations are sensitive to swapped dimensions and step divisibility. Deferred takeover must not leave stale notifier state. Mapping/unregistration must not release an fbdev still mapped by another console. User fonts require size checks to prevent glyph overreads.

## Test Signals

Useful signals include fbdev register/unregister smoke tests, boot with `fbcon=map:`, `vc:`, `rotate:`, `margin:`, and `nodefer`, console switching across multiple fb devices, sysfs `fbcon/rotate`, `rotate_all`, and `cursor_blink`, con2fb ioctls, 256/512-glyph font changes, pan/wrap/scroll behavior, suspend/resume blanking, mode deletion while active, and KASAN/lockdep around cursor work and unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcon.c -->
