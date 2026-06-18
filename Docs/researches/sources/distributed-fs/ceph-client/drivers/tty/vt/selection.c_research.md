# sources/distributed-fs/ceph-client/drivers/tty/vt/selection.c

## Purpose
`selection.c` implements Linux virtual console text selection and paste. It maintains one global selected range, highlights selected cells on the console, copies selected screen contents into a kernel buffer as bytes or UTF-8, allows a user-configurable word-character lookup table, and pastes the buffer into the current tty line discipline with optional bracketed paste wrappers.

## Important APIs, Types, And Functions
- `vc_sel` stores the selected console, buffer, buffer length, start/end cell offsets, and a mutex.
- Public APIs are `clear_selection()`, `vc_is_sel()`, `sel_loadlut()`, `set_selection_user()`, `set_selection_kernel()`, and `paste_selection()`.
- `sel_pos()` reads either Unicode side-buffer data through `screen_glyph_unicode()` or translated glyph data through `screen_glyph()`/`inverse_translate()`.
- `store_utf8()` encodes a Unicode code point for selection buffers.
- `vc_selection_store_chars()` builds the paste buffer and strips trailing spaces per line.
- `vc_do_selection()` expands character, word, line, and pointer selections, updates highlights incrementally, and stores selected text.

## Control Flow And State
User ioctl entry `set_selection_user()` copies `struct tiocl_selection`, enforces `CAP_SYS_ADMIN` for selection-changing modes except clear and pointer, and calls `set_selection_kernel()`. The kernel path takes `vc_sel.lock` and `console_lock`, maps coordinates to byte offsets in the foreground VC, optionally sends mouse reports instead of selecting, clears selection when switching consoles, and delegates to `vc_do_selection()`. Selection ranges are highlighted by calling `invert_screen()` in `vt.c`; mouse pointer position is shown with `complement_pos()`.

`paste_selection()` obtains the tty line discipline, locks the VC tty buffer exclusively, waits when throttled, and feeds bracketed-paste start, selection bytes, and bracketed-paste end through `tty_ldisc_receive_buf()`. It drops and reacquires `vc_sel.lock` while sleeping on throttle.

## State And Persistence Behavior
The selection is global, not per-console. It persists until cleared, replaced, the selected console changes, resize/cursor operations call `clear_selection()`, or allocation failure clears it. The `inwordLut` table is global and mutable through `sel_loadlut()`. The paste buffer is heap memory owned by `vc_sel.buffer`; it is replaced on new selections and freed before replacement.

## Dependencies And Integration Points
This file depends on `vt.c` for screen glyph access, Unicode side-buffer access, highlighting, pointer complement, blank-console poke, mouse reporting, and bracketed paste state. It depends on `keyboard.c` for current keyboard mode via `vt_do_kdgkbmode()`. It integrates with `vt.c` through `tioclinux()` for TIOCLINUX operations and with tty line disciplines for paste injection.

## Risks And Edge Cases
The file explicitly notes selection locking still needs work; `clear_selection()`, `highlight()`, and pointer highlighting can be called from interrupt paths and assume callers hold appropriate console locking. Global selection means a new selection on one console clears another. Unicode selection can allocate up to four bytes per screen cell. Pasting uses ldisc receive methods in a historically unsafe way and must handle throttling, signals, and ldisc hangup. Word selection treats all non-ASCII code points as word characters.

## Test Signals
Test character, word, line, clear, and pointer selection modes; selection across reversed coordinate order; trailing-space stripping and CR insertion; Unicode selection in `K_UNICODE`; non-Unicode selection through inverse translation; custom word LUT loading; mouse-report mode short-circuiting; paste into a throttled tty; signal interruption during paste; bracketed paste escape wrapping; and selection clearing on console switch, resize, cursor changes, and font changes.
