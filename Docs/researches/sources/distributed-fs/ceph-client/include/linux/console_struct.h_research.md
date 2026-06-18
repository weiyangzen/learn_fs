## sources/distributed-fs/ceph-client/include/linux/console_struct.h

Purpose: This header defines virtual console data structures used by the VT layer, excluding implementation details in `vt.c`.

Important APIs, types, and functions: `enum vc_intensity` encodes half-bright, normal, and bold intensity. `struct vc_state` captures cursor position, color, charset selection, intensity, italic, underline, blink, and reverse flags. `struct vc_font` describes glyph width, height, count, and bitmap data; helpers `vc_font_pitch()` and `vc_font_size()` operate on it. `struct vc_data` is the main virtual console state, including tty port, saved/current states, dimensions, screen buffer addresses, scroll region, driver switch pointer, colors, cursor fields, font state, escape-parser fields, VT switching state, wait queues, mode flags, UTF-8 decoding, tab bitmap, palette, translation table, bell timing, foreground display pointer, Unicode mapping, and saved screen copies. `struct vc` wraps `vc_data` plus SAK work. Cursor encoding macros define shape, colors, and mode changes.

Control flow: The VT core mutates `vc_data` as bytes are parsed, screen regions scroll, console drivers render characters, fonts or palettes change, and VT switching saves/restores state. Low-level drivers are expected to populate fields marked by comments and may update origin fields for fast scrolling.

State and persistence: This header is almost entirely state layout. `vc_screenbuf`, Unicode lines, font pointers, palette, cursor state, escape parser state, and saved screen buffers persist for each virtual console until console teardown. `vc_cons[MAX_NR_CONSOLES]` is the global virtual console array.

Dependencies and integration points: It depends on VT UAPI definitions, wait queues, workqueues, tty ports, bitmaps, Unicode page dictionaries, `struct consw`, and console translation code.

Risks and test signals: Risks include corrupt screen-buffer pointer arithmetic, inconsistent character/attribute cell sizing, font pitch miscalculation, UTF-8 parser state corruption, and races in VT switching or SAK work. Test signals include VT switching, font load/ioctl tests, scrollback, Unicode rendering, tab stops, palette changes, and lockdep around console locking.
