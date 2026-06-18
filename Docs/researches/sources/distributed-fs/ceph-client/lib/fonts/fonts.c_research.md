# sources/distributed-fs/ceph-client/lib/fonts/fonts.c

## Purpose
`fonts.c` implements Linux console soft-font data management and lookup. It imports user-provided console font glyphs into kernel-owned `font_data_t` buffers, reference-counts non-internal font data, exports font buffers back to userspace layout, compares font data, and chooses or finds built-in fonts.

## Important APIs, Types, and Functions
Font-data helpers use metadata words stored immediately before `font_data_t`: `REFCOUNT`, `FNTSIZE`, and `FNTSUM`. `font_data_import()` allocates a `struct font_data`, checks overflow, copies glyph rows from userspace pitch to kernel glyph pitch, optionally calculates a checksum, and starts refcounting at one. `font_data_get()` and `font_data_put()` manage references for dynamic font data while treating internal static font data as unrefcounted. `font_data_size()`, `font_data_is_equal()`, and `font_data_export()` provide size, equality, and userspace conversion. Lookup APIs are `find_font()` by name and `get_default_font()` by screen geometry and supported width/height bitmaps.

## Control Flow, State, and Persistence
Imported font state persists in heap allocations until the last `font_data_put()` frees the enclosing `struct font_data`. Static fonts have zero refcount metadata and live in read-only data. `font_data_export()` walks glyphs and zero-fills per-glyph trailing pitch bytes. `get_default_font()` scores all configured fonts by preference, screen height, effective rows/columns at the display resolution, platform-specific m68k hints, and caller-supported dimensions.

## Dependencies and Integration Points
The file depends on console font types from `<linux/kd.h>`, overflow helpers, slab allocation, string/memory helpers, and local `font.h`. Built-in descriptors are added to a static `fonts[]` table under `CONFIG_FONT_*` options, including `font_ter_16x32` when enabled. Exports are used by fbcon, console font ioctls, and other console/font consumers.

## Risks and Test Signals
Important risks include integer overflow in glyph-size calculations, mismatched `vpitch`/height causing bad copies, non-atomic reference count updates if callers share dynamic font data without external synchronization, equality deliberately rejecting static-vs-dynamic matches, and default selection surprises from scoring. Tests should cover import/export round trips with padded pitches, overflow rejection, dynamic refcount lifetime, internal font no-op put/get behavior, checksum-assisted equality, `find_font()` for configured fonts, and `get_default_font()` with constrained width/height masks.
