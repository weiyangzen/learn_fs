# sources/distributed-fs/ceph-client/drivers/tty/vt/vt.c

## Purpose
`vt.c` is the main Linux virtual terminal engine. It owns VC allocation, tty driver operations, console driver binding, VT102/ANSI escape parsing, screen buffer updates, Unicode side-buffer maintenance, console switching, selection invalidation, blanking/unblanking, palette/font operations, `/dev/tty0` state, printk console output, and notifier events consumed by `/dev/vcs*` and other subsystems.

## Important APIs, Types, And Functions
- Global VC state includes `vc_cons[MAX_NR_CONSOLES]`, `fg_console`, `last_console`, `want_console`, `console_driver`, `conswitchp`, `con_driver_map[]`, and `registered_con_driver[]`.
- Notifier APIs `register_vt_notifier()` and `unregister_vt_notifier()` emit `VT_WRITE`, `VT_UPDATE`, `VT_ALLOCATE`, and `VT_DEALLOCATE`.
- Unicode screen helpers include `vc_uniscr_alloc()`, `vc_uniscr_check()`, `vc_uniscr_copy_line()`, `vc_uniscr_putc()`, insert/delete/clear/scroll/copy helpers, and saved alternate-screen Unicode buffers.
- Rendering helpers include `update_region()`, `invert_screen()`, `complement_pos()`, `redraw_screen()`, `con_scroll()`, `insert_char()`, `delete_char()`, cursor helpers, and `vc_con_write_normal()`.
- Escape parser functions include `do_con_trol()`, `handle_ascii()`, `handle_esc()`, `csi_ECMA()`, `csi_DEC()`, `csi_m()`, `csi_J()`, `csi_K()`, `csi_RSB()`, `csi_hl()`, and `csi_DEC_hl()`.
- Lifecycle and tty entry points include `vc_allocate()`, `vc_deallocate()`, `__vc_resize()`, `vty_init()`, `con_init()`, `con_install()`, `con_write()`, `con_ioctl` through `vt_ioctl`, `con_shutdown()`, and `con_cleanup()`.
- Console-driver APIs include `do_take_over_console()`, `give_up_console()`, `do_unregister_con_driver()`, `con_is_bound()`, and `con_is_visible()`.

## Control Flow And State
Early `con_init()` selects a console switch driver, initializes registered console-driver state, allocates the minimum VCs, initializes palette/default attributes, clears or saves the first screen, and registers the printk console when configured. `vty_init()` registers `/dev/tty0`, initializes `/dev/vcs*`, allocates and registers the tty driver, initializes keyboard and console maps, and optional MDA console support.

TTY output enters through `con_write()`/`do_con_write()`. The writer takes `console_lock`, hides the cursor, translates bytes through UTF-8 or console maps, sends prewrite notifiers, dispatches control characters and escape state transitions, or renders normal glyphs. Rendering handles insert mode, autowrap, glyph lookup, fallback substitution, attribute construction, Unicode side-buffer writes, and batched driver `con_putcs()` flushes. Unicode handling classifies double-width and zero-width characters through `ucs.c`, stores zero-width-space padding for double-width glyphs, handles VS16, and attempts recomposition for combining marks.

Console switching is deferred through `console_callback()` so keyboard interrupt paths can request switches safely. The callback processes `want_console`, blanking pokes, scrollback deltas, blanking timer expiry, and update notifications. Resize allocates new screen and optional Unicode buffers, copies preserved rows, updates tty winsize, posts resize events, and redraws visible consoles.

## State And Persistence Behavior
Each `vc_data` owns screen memory, optional Unicode side-buffer, saved alternate-screen memory, cursor/parser state, palette, font-related state, tab stops, scroll region, keyboard-related mode bits through `keyboard.c`, bracketed paste and mouse modes, blanking and bell settings, and tty port state. Global state tracks current/last/wanted console, registered console drivers, blanking timers, module parameters such as `default_utf8`, default colors, default cursor settings, and printk redirection. All state is kernel runtime state; there is no on-disk persistence.

## Dependencies And Integration Points
`vt.c` integrates with console switch drivers through `struct consw`, the tty core through `tty_operations`, keyboard through mode-bit/LED/reset helpers, selection through highlight clearing and glyph APIs, `/dev/vcs*` through exported screen and Unicode-buffer helpers, consolemap through glyph translation, `ucs.c` through width/recomposition/fallback helpers, vt ioctls through `vt_ioctl`, fbcon/vgacon-like drivers through console binding, sysfs through `tty0` and `vtconsole`, timers/workqueues for blanking and switching, and notifier consumers such as `vc_screen.c`.

## Risks And Edge Cases
`vt.c` is lock-sensitive: most state requires `console_lock`, but printk and keyboard paths impose constraints that force deferred work or narrower spinlocks. UTF-8 parsing must handle overlong sequences, surrogate code points, rescan after malformed input, and display-control modes. Double-width and zero-width behavior is an approximation rather than full grapheme clustering. Alternate-screen restore after resize can drop Unicode side-buffer fidelity on allocation failure. Console-driver unregister defers sysfs removal to avoid lock-order inversions. Screen blanking has special behavior for graphics mode, oops paths, VESA timers, and external hooks. Many exported helpers assume callers already hold the console lock.

## Test Signals
High-value tests include boot console initialization, tty open/write/close for multiple VCs, UTF-8 valid and malformed sequences, combining-mark recomposition, CJK/emoji double-width cursor advancement, zero-width marks and VS16, glyph fallback when fonts lack mappings, ANSI/DEC cursor movement and erase sequences, SGR 16/256/24-bit color reduction, alternate screen enter/leave with resize, selection invalidation on updates, `/dev/vcsu*` reads after Unicode rendering, VT switching through keyboard and ioctl, resize winsize propagation, blank/unblank timers and graphics-mode transitions, font and palette ioctls, console-driver bind/unbind/takeover, poll notifications, and printk redirection.
