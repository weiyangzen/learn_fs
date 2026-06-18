# sources/distributed-fs/ceph-client/include/linux/selection.h

Purpose: `selection.h` declares the VT console selection, paste, mouse reporting, color table, and screen-buffer helper interfaces shared among console, TTY, virtual terminal, vc_screen, and selection code.

Important APIs/types/functions: Selection APIs include `clear_selection()`, `set_selection_user()`, `set_selection_kernel()`, `paste_selection()`, `sel_loadlut()`, `mouse_reporting()`, `mouse_report()`, and `vc_is_sel()`. Screen helpers include `screen_pos()`, `screen_glyph()`, `screen_glyph_unicode()`, `complement_pos()`, `invert_screen()`, `getconsxy()`, `putconsxy()`, `vcs_scr_readw()`, `vcs_scr_writew()`, `vcs_scr_updated()`, `vc_uniscr_check()`, and `vc_uniscr_copy_line()`. It also exposes `console_blanked` and console color arrays.

Control flow: TTY ioctls or kernel callers set selections, paste them into TTY input, load selection lookup tables, and report mouse events. VT rendering code uses glyph and inversion helpers to highlight selections and update vc_screen consumers.

State and persistence behavior: Selection state, LUTs, console blanking, color tables, and virtual console buffers are owned by implementation files. Selection persists until cleared or replaced and is tied to console/TTY state, not this header.

Dependencies and integration points: It depends on `tiocl` UAPI data, VT buffer representation, TTY structures, and `vc_data`. It integrates with console rendering, mouse selection, paste into line discipline, and `/dev/vcs*`.

Risks: User pointers in `set_selection_user()` and `sel_loadlut()` require careful copy/validation. Screen offsets must match current console geometry. Selection and paste behavior crosses privilege and TTY boundaries, so ownership and active console checks matter.

Test signals: TIOCL selection ioctls, kernel selection setup, paste into TTY, mouse reporting modes, Unicode screen copy, blanked console behavior, color table use, and vc_screen update notifications.
