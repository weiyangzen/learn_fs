# sources/distributed-fs/ceph-client/include/linux/vt_kern.h

## Purpose
`vt_kern.h` declares internal kernel interfaces for virtual-terminal allocation, resizing, rendering, palette/font management, keyboard ioctls, Unicode translation maps, VT switching, notifier delivery, and console initialization.

## Important APIs, Types, and Functions
Global console state declarations include `fg_console`, `last_console`, and `want_console`. Console APIs include `vc_allocate()`, `vc_cons_allocated()`, `__vc_resize()`, `vc_deallocate()`, `reset_palette()`, blank/unblank helpers, `poke_blanked_console()`, font and colormap ioctls, scrollback/front, `clear_buffer_attributes()`, `update_region()`, `redraw_screen()`, `vc_resize()`, and `tioclinux()`. Translation-map APIs are real under `CONFIG_CONSOLE_TRANSLATIONS` and stubs otherwise. VT APIs include `vt_event_post()`, `vt_waitactive()`, `change_console()`, `reset_vc()`, `do_unbind_con_driver()`, `vty_init()`, `vt_move_to_console()`, notifier registration, and boot cursor hiding. Keyboard helper declarations cover diacritics, keyboard modes, keycode/keymap/string ioctls, LEDs, Unicode reset, shift state, and console keyboard start/stop. `struct vt_spawn_console` tracks a pid and signal under a spinlock.

## Control Flow
Console allocation creates or obtains `vc_data`, resize changes dimensions, redraw/update paths repaint regions, and switch paths move foreground state. VT events are posted to notifier chains when characters or larger updates occur. User ioctls flow through keyboard and console-map helpers. Translation APIs either manipulate Unicode maps or return stubs depending on config.

## State and Persistence
VT state is in-memory global and per-console state: active console indexes, `vc_data`, translation maps, keyboard modes, palette/font data, notifier lists, and spawn-console pid/signaling state. It persists across runtime console operations but is not durable.

## Dependencies and Integration Points
The header depends on VT/KD uapi, tty, mutex, console structures, memory, console maps, notifier blocks, user access annotations, and keyboard structures. Integration points include console drivers, tty ioctl handling, keyboard driver code, accessibility notification consumers, printk/boot cursor handling, and device driver binding/unbinding.

## Risks
Console switching and resizing need careful locking against tty and rendering paths. Stub translation functions can make ioctls appear partially successful in configs without translation support. User pointers require validation in implementations. Global console indexes must remain consistent during allocation/deallocation. Notifier callbacks must not corrupt VT state or sleep in invalid contexts.

## Test Signals
Signals include VT allocation/deallocation, resize, font and cmap ioctls, Unicode map set/get, keyboard mode/keymap/LED ioctls, console switch races, notifier delivery for writes/updates, blank/unblank behavior, and builds with `CONFIG_CONSOLE_TRANSLATIONS` disabled.
