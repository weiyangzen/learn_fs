# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/cursor.c

## Purpose
`cursor.c` provides the NV04 hardware cursor operation callbacks used by `crtc.c`.

## Important APIs, Types, And Functions
`nv04_cursor_show()` and `nv04_cursor_hide()` call `nv_show_cursor()` for a CRTC head. `nv04_cursor_set_pos()` stores the last x/y and writes `NV_PRAMDAC_CU_START_POS`. `nv04_cursor_set_offset()` encodes the cursor BO offset into extended CRTC cursor-address registers, sets double-scan cursor mode when needed, and applies the NV40 cursor fix on Curie hardware. `nv04_cursor_init()` installs these callbacks into `nouveau_crtc->cursor`.

## Control Flow, State, And Integration
`nv04_crtc_create()` allocates/maps the cursor BO and calls `nv04_cursor_init()`. Later `nv04_crtc_cursor_set()` uploads cursor pixels and calls `set_offset()` and `show()`, while `nv04_crtc_cursor_move()` calls `set_pos()`. State is the saved cursor position, cursor offset, mode register CRTC cursor fields, and live RAMDAC/VGA cursor registers.

## Risks And Test Signals
The cursor address is split across three CRTC registers with chipset-specific workarounds, so offset encoding mistakes cause invisible or corrupt cursors. Double-scan mode and NV40 behavior are explicit risk points. Test signals are cursor visibility, movement, hide/show, correct cursor after modeset, double-scan modes, and NV40 hardware cursor validation.
