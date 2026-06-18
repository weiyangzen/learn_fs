# Group Research: group_1212_netbsd_src_sources_os_bsd_netbsd_src_lib_libcurses_immedok_c_source_6e50ea0ada9d

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/netbsd-src`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/immedok.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/immedok.c

Implements `immedok(WINDOW *win, bool bf)`, the curses switch that marks a window for immediate refresh after changes.

The function is a small state mutator over `WINDOW.flags`: it sets or clears `__IMMEDOK`, returning `ERR` for `NULL` and `OK` otherwise. The actual refresh-on-change behavior is consumed elsewhere through the private `__IMMEDOK` flag.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/immedok.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/in_wch.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/in_wch.c

Implements wide-character cell extraction APIs: `in_wch`, `mvin_wch`, `mvwin_wch`, and `win_wch`.

The public variants delegate to `stdscr` or move first with `wmove`. `win_wch` reads the current `__LDATA` cell, backs up from a continuation cell using negative `wcols`, and fills a `cchar_t` with the base wide character, attributes, and linked non-spacing characters from `nschar_t`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/in_wch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/in_wchstr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/in_wchstr.c

Implements wide complex-character string extraction: `in_wchstr`, `in_wchnstr`, movement variants, `win_wchstr`, and `win_wchnstr`.

The unsafe unbounded functions carry `__warn_references`. `win_wchnstr` starts at the current cell, normalizes continuation cells to their leading character, copies each complete wide cell into a `cchar_t` array, includes non-spacing character chains, and appends a wide NUL complex character.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/in_wchstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/inch.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/inch.c

Implements narrow `chtype` cell extraction: `inch`, `mvinch`, `mvwinch`, and `winch`.

`winch` returns the current cell character masked with `__CHARTEXT` plus user-visible attributes masked with `__ATTRIBUTES`. When color is active, default-color bits are stripped before returning so callers do not see internal default-color encoding.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/inch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/inchstr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/inchstr.c

Implements `chtype` array extraction from the current line: `inchstr`, `inchnstr`, movement variants, `winchstr`, and `winchnstr`.

Unbounded variants are marked unsafe. `winchnstr` copies from cursor to EOL or up to `n - 1` entries, appends a zero element, and preserves attributes while masking internal wide-character ACS flags under `HAVE_WCHAR`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/inchstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/initscr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/initscr.c

Implements `initscr()`, the traditional default-screen initializer.

It chooses `TERM` unless `My_term` or missing environment forces `Def_term`, calls `newterm`, exits with a diagnostic on failure per POSIX expectations, installs the returned screen with `set_term`, refreshes `curscr`, touches ripoff windows, and returns `stdscr`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/initscr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/ins_wch.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/ins_wch.c

Implements wide complex-character insertion: `ins_wch`, `mvins_wch`, `mvwins_wch`, and `wins_wch`.

`wins_wch` handles control characters (`\b`, `\r`, `\n`, `\t`), rejects cells that will not fit, shifts complete cells right, clears displaced partial wide cells, writes the new base cell plus non-spacing chain, marks continuation cells with negative `wcols`/`CA_CONTINUATION`, touches the changed line, and calls `__sync`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/ins_wch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/ins_wstr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/ins_wstr.c

Implements wide-string insertion APIs: `ins_wstr`, `ins_nwstr`, movement variants, `wins_wstr`, and `wins_nwstr`.

`wins_nwstr` precomputes display width with `wcwidth`, handles backspace, carriage return, newline, tab expansion, and scroll-region constraints, then shifts line cells and inserts each wide character through `_cursesi_addwchar`. It preserves the original cursor position, marks changed regions, clears to EOL across embedded newlines, scrolls when allowed, and syncs parent windows.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/ins_wstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/insch.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/insch.c

Implements narrow character insertion: `insch`, `mvinsch`, `mvwinsch`, and `winsch`.

`winsch` shifts the current line one cell right from the cursor, writes the incoming `chtype` with window background/color merging, copies background non-spacing characters under wide builds, marks the line dirty, and handles the bottom-right scroll case when `__SCROLLOK` is enabled.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/insch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/insdelln.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/insdelln.c

Implements line insertion/deletion: `insdelln` and `winsdelln`.

`winsdelln` inserts for positive `nlines` and deletes for negative `nlines`, respecting the window scrolling region when the cursor lies inside it. Parent windows rotate `__LINE` pointers for efficiency, subwindows copy cell contents, cleared lines are filled with the window background, dirty ranges are touched, subwindows are invalidated through `__id_subwins`, and `__sync` propagates changes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/insdelln.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/insertln.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/insertln.c

Implements insert-line convenience APIs: `insertln` and `winsertln`.

Both are thin wrappers over `winsdelln(..., 1)`, preserving the cursor while inserting one blank line at the current line using the full line insertion engine in `insdelln.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/insertln.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/insstr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/insstr.c

Implements narrow string insertion: `insstr`, `insnstr`, movement variants, `winsstr`, and `winsnstr`.

`winsnstr` computes the bounded input length, shifts line cells right when the inserted text fits before EOL, writes each byte as a single-column `__CHARTEXT` cell with current window attributes, clears background/continuation flags, marks the whole affected line dirty, touches it, and syncs. It does not implement multibyte decoding despite comments referring to multi-byte strings.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/insstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/instr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/instr.c

Implements narrow string extraction: `instr`, `innstr`, movement variants, `winstr`, and `winnstr`.

Unbounded functions are marked unsafe. `winnstr` copies `__CHARTEXT` bytes from cursor to EOL or up to `n - 1`, appends NUL, returns `OK` for unbounded calls and the copied count for bounded calls. The file explicitly notes it does not yet support multibyte string extraction.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/instr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/inwstr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/inwstr.c

Implements wide string extraction: `inwstr`, `innwstr`, movement variants, `winwstr`, and `winnwstr`.

`winnwstr` normalizes the cursor from a continuation cell to the leading wide cell, then copies base `wchar_t` values across complete cells until EOL or the bounded limit, appending `L'\0'`. It returns `OK` for unbounded calls and the copied count for bounded calls.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/inwstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/keymap.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/keymap.h

Defines private keymap structures shared by narrow and wide input handling.

It declares `key_entry_t`, keymap entry types (`KEYMAP_MULTI`, `KEYMAP_LEAF`), `MAX_CHAR`, allocation chunk size, circular input-buffer increment macro, input parser states including wide assembly, and `struct tcdata` mapping terminfo capability codes to curses key symbols.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/keymap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/keyname.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/keyname.c

Implements key-code name formatting: `keyname(int key)` and wide `key_name(wchar_t key)`.

`keyname` uses a static buffer to format control, printable, delete, meta, function, and `KEY_*` values in sync with `curses.h`, falling back to `UNKNOWN KEY`. `key_name` delegates to `keyname` and strips the `M-` prefix for wide builds. The static buffer makes returned names transient and non-reentrant.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/keyname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/keypad.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/keypad.c

Implements keypad mode control: `keypad` and `is_keypad`.

`keypad` toggles `__KEYPAD` on the target window and emits the terminal `keypad_xmit` capability the first time any active screen enters keypad transmit mode. It clears only the window flag when disabling. `is_keypad` reports the flag state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/keypad.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/leaveok.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/leaveok.c

Implements cursor-leave policy: `leaveok` and `is_leaveok`.

The file only toggles and reports the `__LEAVEOK` flag. `refresh.c` consumes this flag to decide whether `doupdate` should leave the physical cursor where output ended or move it to the logical window cursor.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/leaveok.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/line.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/line.c

Implements horizontal and vertical line drawing for narrow and wide curses APIs.

The narrow `hline`/`vline` paths delegate to wide `*_set` functions under `HAVE_WCHAR`; otherwise they repeatedly call `mvwaddch` with default ACS line characters when no character is supplied. Wide `whline_set` and `wvline_set` convert defaults to `WACS_HLINE`/`WACS_VLINE`, respect display width, draw with `mvwadd_wch`, restore the original cursor, and sync the window.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/line.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/meta.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/meta.c

Implements terminal meta-mode switching: `meta` and `__restore_meta_state`.

`meta` emits `meta_on` or `meta_off` when present, updates `_cursesi_screen->meta_state`, and flushes output. It validates `win != NULL` even though the window argument is otherwise unused; `__restore_meta_state` calls `meta(NULL, state)`, so restoration depends on this validation behavior and is a point worth checking against callers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/meta.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/mouse.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/mouse.c

Provides minimal mouse API support and coordinate transforms.

`wenclose` tests whether screen-relative coordinates are inside a window, while `mouse_trafo` and `wmouse_trafo` convert between screen and window coordinates. Actual event support is stubbed: `has_mouse` is false, `getmouse`/`ungetmouse` return `ERR`, `mousemask` returns zero, and `mouseinterval` returns the default click interval.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/mouse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/move.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/move.c

Implements cursor movement: `move`, `wmove`, and `wcursyncup`.

`wmove` bounds-checks coordinates, allows `x == maxx` as a past-EOL cursor state, updates `__ISPASTEOL` flags, and records `cury`/`curx`. `wcursyncup` propagates a subwindow cursor position upward through parent windows using screen-relative offsets.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/move.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/mvwin.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/mvwin.c

Implements window relocation: `mvderwin` and `mvwin`.

`mvderwin` changes a derived window’s source offset within its parent and marks the parent source area dirty. `mvwin` moves parent windows and their circular subwindow list together, or validates and rebinds a child window inside its parent through `__set_subwin`; it recalculates flags with `__swflags` and touches the moved window.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/mvwin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/newwin.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/newwin.c

Implements window, pad, subwindow, and derived-window allocation.

Public APIs include `newwin`, `newpad`, `subwin`, `derwin`, `subpad`, `dupwin`, and `is_pad`. Internals allocate line arrays, line metadata, contiguous cell storage for parent windows, screen winlist entries, subwindow line aliases, background defaults, dirty markers for pads, and geometry flags (`__ENDLINE`, `__FULLWIN`, `__SCROLLWIN`). `__set_subwin` maps child lines into parent cell storage, while `__swflags` derives terminal-sensitive refresh flags.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/newwin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/nodelay.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/nodelay.c

Implements `nodelay(WINDOW *win, bool bf)`.

It maps nonblocking input to `win->delay = 0` and blocking input to `win->delay = -1`, returning `ERR` for `NULL`. `getch`-side code consumes this delay value.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/nodelay.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/notimeout.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/notimeout.c

Implements `notimeout(WINDOW *win, bool bf)`.

It toggles the `__NOTIMEOUT` flag, which affects whether input parsing waits indefinitely while assembling function-key escape sequences.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/notimeout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/overlay.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/overlay.c

Implements non-destructive window copy via `overlay`.

It delegates to `copywin` with source offsets derived from window origins and `overlay` mode set true, meaning blank source cells should not overwrite destination content.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/overlay.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/overwrite.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/overwrite.c

Implements destructive window copy via `overwrite`.

It delegates to `copywin` using the destination’s full rectangle and overlay mode false, so source cells overwrite destination cells regardless of blankness.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/overwrite.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/pause.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/pause.c

Implements output delay helpers: `napms` and `delay_output`.

`napms` sleeps using `nanosleep` for the requested milliseconds. `delay_output` uses terminal padding when `_cursesi_screen->padchar` exists by passing a millisecond string to `tputs`; otherwise it falls back to `napms`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/pause.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/printw.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/printw.c

Implements formatted output APIs: `printw`, `wprintw`, movement variants, `vw_printw`, and alias `vwprintw`.

`vw_printw` formats into a per-window `open_memstream` buffer, rewinding it for reuse, flushes the stream, then sends exactly the formatted byte count to `waddnstr`. It returns `OK` on zero-length output and `ERR` on formatting or stream failures.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/printw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/putchar.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/putchar.c

Implements low-level terminal output callbacks.

`__cputchar` and `__cputchar_args` write bytes to the current or supplied output `FILE`, flushing after each character for terminal control sequencing. Under `HAVE_WCHAR`, `__cputwchar` and `__cputwchar_args` provide the same behavior for wide characters using `putwc`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/putchar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/refresh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/refresh.c

Implements the core curses refresh engine: `refresh`, `wnoutrefresh`, `pnoutrefresh`, `wrefresh`, `prefresh`, `doupdate`, and terminal diff helpers.

`_wnoutrefresh` copies dirty regions from windows or pads into `__virtscr`, handles subwindow and derived-window propagation, copies wide-cell continuation metadata, updates virtual cursor/flags, and clears source dirty ranges. `doupdate` compares `__virtscr` with `curscr`, optionally clears the screen, hashes dirty lines, applies scroll optimization through `quickch`, updates changed lines with `makech`, respects typeahead polling, handles `__LEAVEOK`, and flushes output.

The low-level path manages attributes/colors (`putattr`, `putattr_out`, `__unsetattr`), emits characters and non-spacing chains (`putch`, `__cursesi_putnsp`), handles bottom-right/autowrap hazards (`putchbr`), optimizes clear-to-EOL, and uses terminal insert/delete/scroll capabilities in `scrolln`. It is the central consumer of dirty flags, hashes, line contents, terminal capabilities, color state, wide cell widths, and cursor state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/refresh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/resize.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/resize.c

Implements window and terminal resizing: `wresize`, `is_term_resized`, `resizeterm`, and `resize_term`.

`wresize` clamps requested sizes to parent or screen bounds, preserves requested dimensions, resizes `__virtscr` when `curscr` is resized, and delegates storage changes to `__resizewin`. Terminal resizing updates `LINES`/`COLS`, resizes standard/current/virtual screens, recomputes window flags, repositions ripoff windows, marks `curscr` clear, and redraws soft labels. `__resizewin` reallocates line/cell storage, remaps subwindows, clears contents to background, resets hashes/dirty markers, and recursively bounds child windows.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/resize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/ripoffline.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/ripoffline.c

Implements ripoff-line reservation and lifecycle.

`ripoffline` records pre-initialization top or bottom line reservations and callbacks. `__ripoffscreen` creates windows for recorded reservations during screen setup, calls each callback, and stores them in `SCREEN.ripped`; `__rippedlines` reports reserved line counts. Resize/touch helpers keep ripoff windows positioned and refreshed, while `__unripoffline` lets soft-label initialization cancel a reservation when terminal-native labels are available.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/ripoffline.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/scanw.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/scanw.c

Implements formatted input APIs: `scanw`, `wscanw`, movement variants, `vw_scanw`, and alias `vwscanw`.

`vw_scanw` reads up to 1024 bytes with `wgetnstr`, then parses with `vsscanf`, returning `OK` only if at least one conversion succeeds. The `mvwscanw` implementation calls `move(y, x)` rather than `wmove(win, y, x)`, so its movement target is `stdscr` before scanning the supplied window.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/scanw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/screen.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/screen.c

Implements screen lifecycle and switching: `filter`, `set_term`, `newterm`, `delscreen`, and internal `__delscreen`.

`newterm` allocates and initializes `SCREEN`, termios state, terminal capabilities, `curscr`, `__virtscr`, soft labels, ripoff windows, `stdscr`, getch/ACS/WACS state, and signal handlers, then starts terminal mode. `set_term` saves globals from the old screen, restores globals from the new screen, resets terminal/ACS state, and binds `curscr`, `stdscr`, and `__virtscr`. Destruction frees terminfo, windows, keymaps, soft labels, buffers, and unget storage.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/screen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/scroll.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/scroll.c

Implements logical scrolling and scroll-region APIs.

`wscrl` requires `__SCROLLOK`, preserves cursor position, moves to the top of the scroll region, delegates line movement to `winsdelln`, restores the cursor, and emits a newline when scrolling `curscr`. `wsetscrreg`/`wgetscrreg` manage per-window scroll bounds. `has_ic` and `has_il` report terminal insert/delete character or line capability availability.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/scroll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/scrollok.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/scrollok.c

Implements `scrollok(WINDOW *win, bool bf)`.

It toggles the `__SCROLLOK` flag that allows `scroll`, newline insertion, and bottom-edge writes to scroll the window instead of failing.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/scrollok.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/setterm.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/setterm.c

Implements terminal capability setup: `setterm`, `_cursesi_setterm`, `_cursesi_resetterm`, and `set_tabsize`.

`_cursesi_setterm` loads terminfo, falls back to `dumb`, applies filter mode capability removal, initializes `LINES`, `COLS`, `ESCDELAY`, `TABSIZE`, padding, quick-change eligibility, and attribute/color conflict masks. Helpers detect reset capabilities that imply `ESC[m` or ACS reset behavior after stripping delay specs. `_cursesi_resetterm` copies screen-local terminal settings back to global curses state and calls `set_curterm`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/setterm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/slk.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/slk.c

Implements soft label key support.

`slk_init` validates label layout and reserves a bottom ripoff line. Public APIs delegate to screen-safe internals for attributes, colors, hide/restore, label lookup, refresh, touch, narrow label set, and wide label set. `__slk_init` allocates labels and detects terminal-native SLK support; `__slk_ripoffline` binds the ripoff window; `__slk_resize` computes label widths/positions for 3-2-3 or 4-4 layouts; `__slk_set_finalise` trims and justifies printable text by display width; `__slk_draw` writes either terminal labels or the ripoff window, with special handling to avoid scrolling on the final label; `__slk_free` releases windows and label text.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/slk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/standout.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/standout.c

Implements standout-mode convenience APIs: `standout`, `standend`, `wstandout`, and `wstandend`.

`wstandout` sets `__STANDOUT` in `win->wattr` only if the terminal can enter/exit standout mode or underline characters. `wstandend` resets the window attribute set to `__NORMAL`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/standout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/syncok.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/syncok.c

Implements `syncok(WINDOW *win, bool bf)`.

It toggles the `__SYNCOK` flag, used by synchronization helpers to propagate changes from subwindows or windows to related ancestors/descendants.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/syncok.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/timeout.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/timeout.c

Implements input timeout controls: `timeout` and `wtimeout`.

`wtimeout` maps negative delays to blocking mode (`-1`), zero to nonblocking, and positive millisecond delays to decisecond `VTIME` units, capped at 255. `timeout` applies the same setting to `stdscr`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/timeout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/toucholap.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/toucholap.c

Implements `touchoverlap(WINDOW *win1, WINDOW *win2)`.

It computes the screen-coordinate rectangle where two windows overlap, converts that rectangle into `win2` coordinates, and touches each overlapping line range in `win2` so a later refresh repaints that area.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/toucholap.c -->