# Group Research: group_1211_netbsd_src_sources_os_bsd_netbsd_src_lib_libcurses_attributes_c_sou_1c62543acd2b

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/netbsd-src`, which is included in subset A. Every listed source file was read completely and summarized separately below.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/attributes.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/attributes.c

Read completely: 491 lines.

This file implements libcurses attribute and color-pair state operations for `stdscr` and arbitrary `WINDOW` objects. Public wrappers include `attr_get`, `attr_on`, `attr_off`, `attr_set`, `color_set`, `attron`, `attroff`, `attrset`, `wattr_get`, `wattr_on`, `wattr_off`, `wattr_set`, `wcolor_set`, `getattrs`, `wattron`, `wattroff`, `wattrset`, `termattrs`, and, under wide-character support, `term_attrs`.

The implementation centralizes real mutation in `__wattr_on`, `__wattr_off`, and `__wcolor_set`. Those helpers validate `WINDOW *`, inspect the terminal capability table through `win->screen->term`, and only set attributes whose enter/exit terminfo sequences exist. Standout and underscore delegate to `wstandout`/`wunderscore` and `wstandend`/`wunderend`; color bits are carried in `__COLOR` and set only when the terminal reports colors.

Important interactions: this file depends on `curses.h` attribute masks, `curses_private.h` terminal accessors, global terminfo capability macros, and color globals such as `max_colors`. `wattr_set` deliberately replaces any color bits embedded in the requested attributes with `COLOR_PAIR(pair)`, matching ncurses behavior.

Reliability notes: most window-level helpers reject null windows, but `wattr_set` calls `__wattr_off` and `__wattr_on` without checking their return values and always returns `OK` if `opts == NULL`; a null `win` therefore yields `OK` despite failed internal operations. Attribute support is capability-gated, so callers cannot assume every requested bit is retained.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/attributes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/background.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/background.c

Read completely: 352 lines.

This file implements narrow and wide background-character APIs: `bkgdset`, `bkgd`, `wbkgdset`, `wbkgd`, `getbkgd`, and the wide-character `bkgrndset`, `bkgrnd`, `getbkgrnd`, `wbkgrndset`, `wbkgrnd`, `wgetbkgrnd`. Non-wide builds provide stub wide APIs that return `ERR` or do nothing.

For narrow cells, `wbkgdset` updates `win->bch` and `win->battr`, adding `__default_color` when color is active and no color pair is supplied. `wbkgd` applies the new background across all window cells, replacing cells marked `CA_BACKGROUND`, merging attributes, resetting wide column width when enabled, and touching the window.

The wide path maintains `win->bnsp`, the linked list of nonspacing background characters. `wbkgrndset` rejects empty and multi-column base characters, copies the old background into an `__LDATA`, updates background base/nonspacing characters and attributes, compares old/new backgrounds with `_cursesi_celleq`, and rewrites existing background cells with `_cursesi_copy_wchar`.

Important interactions: wide behavior depends heavily on `_cursesi_copy_nsp`, `_cursesi_copy_wchar`, `_cursesi_celleq`, and `__cursesi_free_nsp` from `curses.c`. Color default behavior depends on `__using_color` and `__default_color`.

Reliability notes: `wbkgrndset` is `void` and can return early after allocation failure, potentially after partially changing the background list. Its correctness also depends on `_cursesi_copy_nsp` safely copying into cells that may have no existing nonspacing list.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/background.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/bell.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/bell.c

Read completely: 72 lines.

This file implements `beep()` and `flash()`. `beep` prefers the terminal `bell` capability and falls back to `flash_screen`; `flash` does the reverse. Both emit the selected terminfo string with `tputs(..., __cputchar)` and return `OK` even if neither capability exists.

Important interactions: uses terminfo globals `bell` and `flash_screen`, output helper `__cputchar`, and tracing area `__CTRACE_MISC`.

Reliability notes: no error is reported for terminals without either audible or visible alert capability.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/bell.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/border.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/border.c

Read completely: 625 lines.

This file draws borders for narrow and wide curses windows. It implements `border`, `wborder`, `border_set`, and `wborder_set`. `box.c` delegates to these routines.

In non-wide builds, `wborder` supplies ACS defaults for omitted characters, merges each border character with current window and background attributes, writes left/right sides, top/bottom lines, and corners, then touches the full window. It avoids writing corners for a full-screen scrolling window, matching the historical bottom-right scroll hazard.

In wide builds, `wborder` converts `chtype` values into `cchar_t` values or WACS defaults, then delegates to `wborder_set`. `wborder_set` copies or defaults all eight border glyphs, merges attributes, handles display widths with `wcwidth`, writes continuation cells using negative `wcols`, clears overlapping partial wide characters back to background cells, manages nonspacing lists per cell, and handles corners with separate width calculations.

Important interactions: uses ACS/WACS tables from `curses.h`, `WINDOW` cell layout from `curses_private.h`, `__cursesi_chtype_to_cchar`, `_cursesi_copy_nsp`, `__touchwin`, and background fields `bch`, `battr`, and `bnsp`.

Reliability notes: wide `wborder_set` performs many per-cell allocations for nonspacing characters; allocation failure returns `ERR` after earlier cells may already have been modified. The function repeatedly frees existing nonspacing lists manually, so ownership invariants of `__LDATA.nsp` are critical.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/border.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/box.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/box.c

Read completely: 63 lines.

This is a thin border convenience wrapper. `box(win, vert, hor)` calls `wborder` with the same vertical character for left/right, the same horizontal character for top/bottom, and zero corner arguments so `wborder` supplies defaults. `box_set` is the wide-character equivalent and calls `wborder_set` with null corners.

Non-wide builds return `ERR` from `box_set`.

Important interactions: all drawing behavior and validation are delegated to `border.c`.

Reliability notes: no additional checks beyond those in `wborder` and `wborder_set`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/box.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/cchar.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/cchar.c

Read completely: 139 lines.

This file implements complex-character conversion helpers: `getcchar`, `setcchar`, and internal `__cursesi_chtype_to_cchar`.

`getcchar` reports or copies the wide-character sequence stored in a `cchar_t`, returning the element count when the caller passes `wch == NULL`. When copying, it requires `attrs` and `color_pair`, returns attributes, extracts the color pair when colors are active, copies `vals`, and null-terminates the output string.

`setcchar` builds a `cchar_t` from a wide-character string, attributes, and color pair. It rejects unsupported `opts`, strings longer than `CCHARW_MAX`, and invalid multi-character starts. It truncates at the first later spacing character because only a base character plus nonspacing characters are represented. `__cursesi_chtype_to_cchar` converts ordinary `chtype` values or internal WACS-marked ACS values into `cchar_t`.

Important interactions: uses `__using_color`, `PAIR_NUMBER`, `COLOR_PAIR`, `__ACS_IS_WACS`, `_wacs_char`, and `wcwidth`.

Reliability notes: callers must pass a valid `wcval`/`wch`; there is no null validation for those required inputs. `setcchar` uses `wcslen`, so an unterminated input string is unsafe.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/cchar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/chgat.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/chgat.c

Read completely: 101 lines.

This file implements attribute changes over a run of cells without changing characters: `chgat`, `mvchgat`, `wchgat`, and `mvwchgat`.

`mvwchgat` validates the window and coordinates, combines requested attributes with `COLOR_PAIR(color)`, clamps negative or oversized counts to the rest of the line, marks the affected line dirty, updates `firstchp`/`lastchp`, and overwrites each target cell's attributes. Wide builds preserve only non-wide attribute bits by replacing `WA_ATTRIBUTES`; narrow builds assign the full attribute value.

Important interactions: depends on `WINDOW` line dirty tracking from `curses_private.h`, `wmove` through movement wrappers, and the public color-pair encoding macros.

Reliability notes: `wchgat(win, ...)` computes `win->cury` and `win->curx` before `mvwchgat` can validate `win`; passing a null window to `wchgat` can dereference null.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/chgat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/clear.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/clear.c

Read completely: 73 lines.

This file implements `clear` and `wclear`. `clear` delegates to `_cursesi_screen->stdscr` when macro mode is disabled. `wclear` validates the window, calls `werase`, and sets the `__CLEAROK` flag so the next refresh performs a full clear.

Important interactions: uses `werase` from `erase.c` and the window flag definitions in `curses_private.h`.

Reliability notes: `clear()` assumes `_cursesi_screen` is initialized.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/clear.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/clearok.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/clearok.c

Read completely: 55 lines.

This file implements `clearok(WINDOW *win, bool bf)`. It validates the window and sets or clears the `__CLEAROK` flag, controlling whether refresh should clear the physical screen before repainting.

Important interactions: refresh logic consumes `__CLEAROK`; this file only toggles the state.

Reliability notes: null windows return `ERR`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/clearok.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/clrtobot.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/clrtobot.c

Read completely: 121 lines.

This file implements `clrtobot` and `wclrtobot`, clearing from the current cursor position to the bottom of the window.

`wclrtobot` validates the window, chooses the effective background character and attributes, accounts for `__ISPASTEOL` by starting at the next line, then scans all affected cells. Cells that satisfy `__NEED_ERASE` are reset to the background character, marked `CA_BACKGROUND`, stripped of continuation state, assigned background attributes while preserving `__ALTCHARSET`, and, in wide builds, given copied background nonspacing characters and `wcols = 1`. Dirty ranges are touched per line, then `__sync` propagates synchronization.

Important interactions: uses `__NEED_ERASE`, `_cursesi_copy_nsp`, `__touchline`, and `__sync`. Its behavior differs for `curscr`, where background attributes are forced to zero.

Reliability notes: wide erasure can fail if copying background nonspacing characters fails, returning `ERR` after earlier cells may have been modified.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/clrtobot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/clrtoeol.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/clrtoeol.c

Read completely: 127 lines.

This file implements `clrtoeol` and `wclrtoeol`, clearing from the current cursor position to the end of the current line.

`wclrtoeol` validates the window, handles `__ISPASTEOL` by moving to the next line when possible, then iterates from `curx` to line end. It clears `CA_BACKGROUND` before checking `__NEED_ERASE`, resets changed cells to the background character and attributes, copies background nonspacing data in wide builds, touches the whole line range from the original x coordinate to the right edge, and calls `__sync`.

Important interactions: same erase infrastructure as `clrtobot.c` and `erase.c`.

Reliability notes: the comment notes ncurses compatibility behavior that makes the cleared rest-of-line foreground rather than background. This intentionally affects `CA_BACKGROUND` semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/clrtoeol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/color.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/color.c

Read completely: 711 lines.

This file implements libcurses color support and terminal color output. Public functions include `has_colors`, `can_change_color`, `start_color`, `init_pair`, `pair_content`, `init_color`, `color_content`, `use_default_colors`, `assume_default_colors`, and `no_color_attributes`. Internal functions include `__set_color`, `__unset_color`, `__restore_colors`, and `__change_pair`.

Global state includes `__using_color`, `__do_color_init`, `__default_color`, and `__default_pair`. `start_color` validates terminal capability support, clamps `COLORS` and `COLOR_PAIRS`, resets terminal colors, classifies the terminal color model as ANSI, HP, Tektronix, or other, initializes default RGB values and pair tables, marks color as active, and updates all existing windows with the default color pair.

`init_pair` validates pair and color numbers, maps ANSI color ordering to older `set_foreground`/`set_background` ordering for `COLOR_OTHER`, stores pair values, and calls `__change_pair` when an existing pair changes. `__set_color` emits terminal sequences for the active pair and tracks `_cursesi_screen->curpair`; `__unset_color` emits `orig_pair`; `__change_pair` dirties cells using a changed pair or clears matching color bits on `curscr`.

Important interactions: tightly coupled to terminfo capabilities, `_cursesi_screen`, `curscr`, `__virtscr`, the screen window list, and attribute color-bit encoding from `curses.h`.

Reliability notes: HP and Tektronix paths are placeholders. `pair_content` accepts `pair == _cursesi_screen->COLOR_PAIRS` because it checks `>` rather than `>=`, while `init_pair` rejects that value. Color state is global to the current screen and must be initialized before pair/color content APIs are meaningful.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/color.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/copywin.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/copywin.c

Read completely: 142 lines.

This file implements `copywin`, copying an intersected rectangle from one window to another. It supports destructive overwrite mode and nondestructive overlay mode.

The function normalizes negative source and destination coordinates, clamps the destination maximum row/column to the intersection of both windows, then iterates source cells and writes destination cells through `wmove` plus `__waddch` in narrow builds or `wadd_wch` in wide builds. Overlay mode skips source cells where `isspace(sp->ch)` is true.

Important interactions: used by higher-level `overlay`/`overwrite` style routines. Wide mode converts each `__LDATA` plus its nonspacing list into a temporary `cchar_t`.

Reliability notes: the wide nonspacing copy loop uses `cc.elements <= CURSES_CCHAR_MAX` while appending into `vals`, which can write one past the fixed array if a cell has the maximum number of nonspacing characters. The return values of `wmove`, `__waddch`, and `wadd_wch` are not checked inside the copy loop.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/copywin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/cr_put.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/cr_put.c

Read completely: 517 lines.

This file implements terminal cursor motion and low-level cursor-position optimization. Public `mvcur` delegates to internal `__mvcur`, which initializes desired and current coordinates and calls `fgoto`.

`fgoto` normalizes positions around terminal width/height, accounts for wraparound, scrolls when the destination is below the screen, chooses between direct `cursor_address` addressing and local motion, and updates `outcol`/`outline`. `plod` estimates and optionally emits local motion using home, lower-left, carriage return, cursor up/down/left/right, tabs, backspace, and, during refresh, already-rendered `curscr` cells. `plodput` supports cost estimation by decrementing `plodcnt` instead of outputting. `tabcol` computes tab stops.

Important interactions: depends on global terminal dimensions and capabilities (`COLS`, `LINES`, `cursor_address`, `cursor_home`, `cursor_down`, `cursor_up`, `tab`, etc.), `curscr` contents, `__cputchar`, and wide output helpers `__cputwchar`/`__cursesi_putnsp`.

Reliability notes: this code assumes `curscr` accurately mirrors the physical screen when using refresh-time plodding. Wide builds refuse to plod from a continuation cell. The code has historical comments about imperfect cost accounting, such as carriage-return capability length not being included.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/cr_put.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/ctrace.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/ctrace.c

Read completely: 109 lines.

This file provides debug-only tracing when `DEBUG` is defined. `__CTRACE_init` reads `CURSES_TRACE_MASK` and `CURSES_TRACE_FILE`, supports negative masks as exclusions from `__CTRACE_ALL`, opens the trace file unless set to `<none>`, and records initialization. `__CTRACE` lazily initializes tracing, filters by area mask, optionally prefixes timestamps, writes formatted output, tracks newline state, and flushes after every trace.

Non-debug builds define only a dummy typedef to avoid an empty translation unit; `__CTRACE` becomes a macro in `curses_private.h`.

Important interactions: trace areas are declared in `curses_private.h`. Many files in this group call `__CTRACE` throughout control paths.

Reliability notes: debug tracing opens the configured file with `"w"`, truncating existing content. The trace file is never explicitly closed.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/ctrace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/cur_hash.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/cur_hash.c

Read completely: 87 lines.

This file implements line hashing. `__hash_more` is the PJW hash from the Dragon Book, taking an existing hash seed and a byte span. `__hash_line` hashes an array of `__LDATA` cells.

In wide builds, `__hash_line` hashes each cell's base character, attributes, and every nonspacing character in its `nsp` list. In narrow builds, it hashes the raw `__LDATA` memory for the full line.

Important interactions: used by refresh optimization to detect changed lines. It depends on `__LDATA` having stable representation in narrow builds; `curses_private.h` explicitly warns against padding in `__LDATA`.

Reliability notes: wide hashing omits `cflags` and `wcols`, so visual state represented only by those fields is not part of the hash.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/cur_hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/curs_set.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/curs_set.c

Read completely: 101 lines.

This file implements cursor visibility control. `curs_set(0)`, `curs_set(1)`, and `curs_set(2)` map to `cursor_invisible`, `cursor_normal`, and `cursor_visible` terminfo capabilities respectively. On success it emits the sequence, flushes the screen output file, stores the new mode in `_cursesi_screen->old_mode`, and returns the previous mode. `__restore_cursor_vis` reapplies the stored mode.

Important interactions: depends on `_cursesi_screen`, terminfo cursor-visibility capabilities, `tputs`, and `__cputchar`.

Reliability notes: unsupported visibility requests return `ERR`. The name `old_mode` stores current/last requested visibility after success, not just a historical value.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/curs_set.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/curses.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/curses.c

Read completely: 214 lines.

This file defines core libcurses global variables and wide-cell helper functions. Globals include public `curscr`, `stdscr`, `COLS`, `LINES`, `ESCDELAY`, `TABSIZE`, `COLORS`, `COLOR_PAIRS`, `Def_term`, and private state such as `__echoit`, `__rawmode`, `__pfast`, `__noqch`, `__virtscr`, and `_cursesi_screen`.

`_cursesi_celleq` compares two cells by character and attributes, and under wide support also compares continuation flags and nonspacing-character lists. `_cursesi_copy_wchar` copies a full wide cell. `_cursesi_copy_nsp` copies a source nonspacing list into an existing cell list, allocating or freeing nodes as needed. `__cursesi_free_nsp` frees one nonspacing list, and `__cursesi_win_free_nsp` frees all per-cell nonspacing lists in a window.

Important interactions: background, border, erase, delete, file I/O, and refresh-related code rely on these helpers for complex character ownership and equality.

Reliability notes: `_cursesi_copy_nsp` appears fragile when copying a non-empty source list into a destination cell with `ch->nsp == NULL`: `pnp` starts null, but the allocation branch assigns through `pnp->next`. Callers that copy background nonspacing data into empty cells depend on this path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/curses.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/curses.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/curses.h

Read completely: 1064 lines.

This is the public libcurses API header. It defines `chtype`, `attr_t`, optional wide-character support, `cchar_t`, boolean constants, key constants from `KEY_MIN` through `KEY_MAX`, `KEY_CODE_YES`, attribute masks, ACS and WACS aliases, color constants, `COLOR_PAIR`, `PAIR_NUMBER`, public globals, `ERR`/`OK`, macro-mode pseudo-functions, function prototypes, wide-character APIs, mouse compatibility APIs, and private-but-user-visible output helper prototypes.

The header defaults `HAVE_WCHAR` on unless `DISABLE_WCHAR` is defined, making wide-character structures and APIs the normal build surface. It encodes attributes and color pairs inside `attr_t`/`chtype` bit masks and exposes the core `WINDOW`/`SCREEN` typedefs as opaque struct names.

Important interactions: nearly every file in this group consumes masks such as `__CHARTEXT`, `__ATTRIBUTES`, `__COLOR`, `WA_ATTRIBUTES`, ACS/WACS macros, and public function prototypes from this header. When `_CURSES_USE_MACROS` is defined, many APIs are direct macro wrappers around window-level functions.

Reliability notes: this header fixes ABI-visible bit assignments and type sizes. The comment requires `attr_t` to match `wchar_t` size to avoid padding in `__LDATA`, which affects hashing, serialization, and cell copying.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/curses.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/curses_private.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/curses_private.h

Read completely: 434 lines.

This is the internal libcurses structure and helper declaration header. It defines `nschar_t`, `__LDATA`, `__LINE`, `WINDOW`, screen/window flags, color and pair structures, soft-label structures, ripoff-line structures, `SCREEN`, debug trace masks, common erase logic, internal function prototypes, and private extern globals.

Key internal state: `__LDATA` stores a character, attributes, continuation/background flags, and in wide builds a nonspacing list plus display width. `WINDOW` stores geometry, cursor position, line pointers, ownership pointers, flags, current/background attributes, background nonspacing list, pad refresh coordinates, and formatted I/O buffers. `SCREEN` stores terminal files, standard/current/virtual windows, terminal dimensions, ACS/WACS tables, color tables, termios modes, input keymap, unget buffer, resize state, soft-label state, and wide input conversion buffers.

Important interactions: this header is the integration contract for all source files in the group. It defines `__NEED_ERASE`, `__touchline`, `__sync`, `__mvcur`, key input initializers, color restore functions, nonspacing helpers, and window allocation internals.

Reliability notes: `__LDATA` layout is explicitly padding-sensitive. Many modules directly mutate line dirty markers and linked nonspacing lists, so changes here have broad ABI and memory-ownership impact.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/curses_private.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/delch.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/delch.c

Read completely: 154 lines.

This file implements character deletion at the current cursor position: `delch`, `mvdelch`, `mvwdelch`, and `wdelch`.

In narrow builds, `wdelch` shifts the rest of the line left by `memcpy`, fills the last cell with the background character, marks it as background, sets attributes to background color or zero depending on `curscr`, and touches the affected line. In wide builds, it first normalizes deletion from a continuation cell back to the base cell, deletes the full display-width character, frees the deleted cell's nonspacing list, shifts following cells left, fills trailing cells with background data, copies background nonspacing characters, sets `wcols = 1`, touches the line, and synchronizes.

Important interactions: relies on `wmove`, `__touchline`, `__sync`, `_cursesi_copy_nsp`, and wide-cell `wcols` continuation conventions.

Reliability notes: wide deletion modifies and frees per-cell nonspacing lists manually. Failure while copying background nonspacing data can leave part of the line already shifted.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/delch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/deleteln.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/deleteln.c

Read completely: 65 lines.

This file implements line deletion wrappers. `deleteln()` deletes one line from `stdscr` by calling `winsdelln(stdscr, -1)`, and `wdeleteln(win)` calls `winsdelln(win, -1)`.

Important interactions: real behavior is implemented in the insert/delete-line code outside this group.

Reliability notes: validation is delegated to `winsdelln`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/deleteln.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/delwin.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/delwin.c

Read completely: 118 lines.

This file implements `delwin`, releasing a `WINDOW` and its associated resources. It treats `NULL` as success. Wide builds first free all per-cell nonspacing lists.

For original windows (`orig == NULL`), it frees the window cell storage, recursively deletes subwindows from the circular subwindow list, and removes the window from the screen's window list. For subwindows, it unlinks the subwindow from its original window's circular list without freeing shared cell storage. It then frees line storage, line pointer arrays, formatted output file/buffer state, clears matching `_cursesi_screen` pointers, and frees the window object.

Important interactions: depends on subwindow list invariants maintained by window creation and `__id_subwins`. It updates `_cursesi_screen->curscr`, `stdscr`, and `__virtscr` if the deleted window matches.

Reliability notes: recursively deleting subwindows while walking the circular list depends on capturing `np = wp->nextp` before deletion. External references to deleted subwindows become invalid.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/delwin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/echo_wchar.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/echo_wchar.c

Read completely: 85 lines.

This file implements wide-character echo helpers: `echo_wchar`, `wecho_wchar`, and `pecho_wchar`. They add a `cchar_t` to a window with `wadd_wch` and then refresh either the window (`wrefresh`) or pad (`prefresh` with saved pad coordinates).

Important interactions: pad refresh uses `pad->pbegy`, `pbegx`, `sbegy`, `sbegx`, `smaxy`, and `smaxx`.

Reliability notes: `pecho_wchar` assumes `pad` is valid before reading saved pad coordinates after `wadd_wch` succeeds.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/echo_wchar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/echochar.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/echochar.c

Read completely: 83 lines.

This file implements narrow echo helpers: `echochar`, `wechochar`, and `pechochar`. They add a `chtype` through `waddch` and refresh the target window or pad.

Important interactions: `echochar` may be a macro unless `_CURSES_USE_MACROS` is disabled. `pechochar` uses saved pad refresh coordinates exactly like the wide version.

Reliability notes: pad coordinate dereferences occur after `waddch` succeeds, so callers must pass a valid pad/window.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/echochar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/erase.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/erase.c

Read completely: 109 lines.

This file implements `erase` and `werase`, clearing an entire window and moving the cursor to the origin.

`werase` validates the window, chooses background character/attributes, iterates every cell, and only rewrites cells that satisfy `__NEED_ERASE`. Rewritten cells become background cells, lose continuation state, preserve `__ALTCHARSET`, copy background nonspacing characters in wide builds, and set `wcols = 1`. The whole window is touched to handle overlaps, then `wmove(win, 0, 0)` resets the cursor.

Important interactions: shared erase semantics with `clrtobot` and `clrtoeol`; depends on `_cursesi_copy_nsp`, `__touchwin`, and `wmove`.

Reliability notes: wide erasure can return `ERR` after partially clearing the window if copying nonspacing data fails.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/erase.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/fileio.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/fileio.c

Read completely: 245 lines.

This file implements window serialization and deserialization with `putwin` and `getwin`, excluding `LIBHACK` builds. It includes generated `fileio.h` for `CURSES_LIB_MAJOR` and `CURSES_LIB_MINOR`.

`putwin` rejects null windows and subwindows, writes the library version, writes the raw `WINDOW` structure, writes the background nonspacing list in wide builds, then writes every cell's character and attributes. `getwin` validates the version, reads a temporary `WINDOW`, allocates a new window with `__newwin`, copies selected fields from the serialized structure, restores flags with `__swflags`, reads background nonspacing state, reads every cell's character and attributes, touches each line, and returns the new window.

Important interactions: depends on `genfileioh.awk` output, `__newwin`, `__swflags`, `delwin`, `__touchline`, and nonspacing helpers from `curses.c`.

Reliability notes: the wide helper `__putnsp` never advances `nsp` inside its loop, so any non-null nonspacing list would cause an infinite write loop. Cell serialization also calls `__putnsp(win->bnsp, fp)` when `sp->nsp != NULL`, which appears to serialize the background list rather than the cell's foreground list. `__getnsp` assumes a non-null list head when appending nodes, making serialized nonspacing data fragile.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/fileio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/flushok.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/flushok.c

Read completely: 55 lines.

This file implements `flushok(WINDOW *win, bool bf)`. It validates the window and sets or clears `__FLUSH`, controlling whether refresh should flush output after updating the window.

Important interactions: refresh code consumes the flag; this file only toggles it.

Reliability notes: null windows return `ERR`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/flushok.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/fullname.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/fullname.c

Read completely: 64 lines.

This file implements `fullname(const char *bp, char *def)`, extracting the terminal's full name from a termcap-style alias string. It repeatedly copies alias text up to `|` or `:` into `def`, so the final copied alias before `:` is returned. `def` is initialized to an empty string first.

Important interactions: used with terminal description strings where aliases are pipe-separated and the description begins after `:`.

Reliability notes: there is no destination size parameter, so callers must provide a large enough `def` buffer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/fullname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/genfileioh.awk -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/genfileioh.awk

Read completely: 66 lines.

This AWK script generates `fileio.h` from `shlib_version`. It extracts and normalizes NetBSD RCS version strings for provenance comments, reads `major=` and `minor=` assignments, and emits `CURSES_LIB_MAJOR` and `CURSES_LIB_MINOR` defines.

Important interactions: `Makefile` uses this script to build `fileio.h`, which `fileio.c` uses to version-check serialized windows.

Reliability notes: if `major` or `minor` is absent from input, the generated macro value is empty.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/genfileioh.awk -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/get_wch.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/get_wch.c

Read completely: 612 lines.

This file implements wide-character input: `__init_get_wch`, internal wide `inkey`, `get_wch`, `mvget_wch`, `mvwget_wch`, `wget_wch`, `unget_wch`, and `__fgetwc_resize`.

`__init_get_wch` initializes the screen's circular byte buffer and wide input state. The internal `inkey` is a state machine over `INKEY_NORM`, `INKEY_ASSEMBLING`, `INKEY_BACKOUT`, `INKEY_TIMEOUT`, and `INKEY_WCASSEMBLING`. It combines keypad trie matching with multibyte decoding via `mbrtowc`, inter-character timeouts, disabled key handling, and fallback return of raw characters when sequences fail.

`wget_wch` refreshes touched windows before input, handles resize events, serves pushed-back characters from the shared unget buffer, temporarily switches to cbreak when echoing outside raw mode, applies window delay/keypad modes, echoes regular wide characters through `setcchar`/`wadd_wch`, handles erase-like key symbols during echo, maps carriage return to newline when `nl` is active, and returns either `OK`, `ERR`, or `KEY_CODE_YES`.

Important interactions: shares `_cursesi_state` with `getch.c`, uses the same keymap trie, uses `_cursesi_screen->sp` conversion state and `cbuf`, calls `__timeout`, `__notimeout`, `__delay`, `__save_termios`, `__restore_termios`, `resizeterm`, and `__unget`.

Reliability notes: `__fgetwc_resize` does not set `*resized` on the non-resize error path, but `wget_wch` checks that bool after `WEOF`; this can read an uninitialized local. The state machine exits with `exit(2)` if it sees an invalid internal state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/get_wch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/get_wstr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/get_wstr.c

Read completely: 256 lines.

This file implements wide-string input wrappers and editing behavior: `getn_wstr`, unsafe `get_wstr`, `mvgetn_wstr`, unsafe `mvget_wstr`, `mvwgetn_wstr`, unsafe `mvwget_wstr`, unsafe `wget_wstr`, `wgetn_wstr`, and internal `__wgetn_wstr`.

Bounded APIs reject `n < 1`, and for `n == 1` write an empty string and return `ERR`. The unbounded APIs emit link-time warnings through `__warn_references`. `__wgetn_wstr` reads wide characters with `wget_wch` until newline, carriage return, or error; supports erase, backspace, left, and kill characters; erases display cells using the window background character wrapped in a `cchar_t`; ignores function-key values after removing their echoed display; and always null-terminates the result.

Important interactions: depends on `wget_wch`, `erasewchar`, `killwchar`, `setcchar`, `mvwadd_wch`, `wmove`, and line touch behavior.

Reliability notes: editing assumes the cursor positions created by `wget_wch` echoing match the cleanup coordinates here. Some cleanup paths address `win->curx - 1` or `win->curx - 2`, so correctness depends on the preceding echo behavior and current cursor state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/get_wstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/getch.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/getch.c

Read completely: 1013 lines.

This file implements narrow-character input, keypad sequence mapping, key definition toggles, pushback, escape delay, and resize-aware byte input. Public APIs include `getch`, `mvgetch`, `mvwgetch`, `wgetch`, `keyok`, `define_key`, `ungetch`, `has_key`, and `set_escdelay`; internal APIs include `_cursesi_free_keymap`, `__init_getch`, `__unget`, and `__fgetc_resize`.

The file defines a large terminfo-code to curses-key table, builds a trie-like `keymap_t` from terminal key sequences in `__init_getch`, and parses input through internal `inkey`. The parser handles normal, assembling, timeout, and backout states, inter-character delays based on `ESCDELAY`, disabled key leaves, custom key definitions, and returns either raw bytes or symbolic `KEY_*` values.

`wgetch` refreshes touched windows, moves the physical cursor when echoing and the logical cursor moved, handles pending resize events and unget data, manages cbreak/nodelay/timeout modes, optionally parses keypad sequences, restores termios, echoes ordinary characters, maps carriage return to newline under `nl`, and returns `ERR` for negative input.

Important interactions: shared with `get_wch.c` through `_cursesi_state`, `_cursesi_screen->base_keymap`, and `__unget`. It relies on `keymap.h`, terminfo string arrays, termios helpers, refresh/cursor movement, and resize signal state.

Reliability notes: `add_new_key` and allocation helpers call `exit` on allocation failure, not `ERR`. In `__unget`, the realloc-failure fallback uses pointer and byte counts inconsistently in `memmove`, advancing by `sizeof(wchar_t)` elements and copying only `unget_len - 1` bytes, which is suspicious for a `wchar_t` array.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/getch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/getstr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/getstr.c

Read completely: 262 lines.

This file implements narrow string input: `getnstr`, unsafe `getstr`, `mvgetnstr`, unsafe `mvgetstr`, `mvwgetnstr`, unsafe `mvwgetstr`, unsafe `wgetstr`, `wgetnstr`, and internal `__wgetnstr`.

Bounded APIs reject `n < 1`, and for `n == 1` store an empty string and return `ERR`. Unbounded APIs emit link-time unsafe-use warnings. `__wgetnstr` reads through `wgetch` until newline, carriage return, or `ERR`, supports erase, backspace, left, and kill characters, removes echoed key/control display from the window, ignores function keys after cleaning their display, tracks a remaining character budget, and null-terminates the output.

Important interactions: depends on `wgetch`, terminal erase/kill characters, `mvwaddch`, `wmove`, `__touchline`, and cursor behavior from input echoing.

Reliability notes: unbounded APIs are explicitly unsafe. Editing is byte-oriented and screen cleanup is based on how `wgetch` displays control/key sequences.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/getstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/getyx.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/getyx.c

Read completely: 160 lines.

This file implements coordinate accessor functions backing public macros: `getpary`, `getparx`, `getcury`, `getcurx`, `getbegy`, `getbegx`, `getmaxy`, and `getmaxx`.

Parent-relative accessors return `-1` if the window is null or not a subwindow. Other accessors return `ERR` for null windows and otherwise return the requested field from `WINDOW`.

Important interactions: `curses.h` macros `getyx`, `getbegyx`, `getmaxyx`, and `getparyx` call these functions to fill caller variables.

Reliability notes: because `ERR` is also `-1`, null-window errors and valid parent-query “not a subwindow” results are intentionally indistinguishable for parent accessors.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/getyx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/id_subwins.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/id_subwins.c

Read completely: 60 lines.

This file implements internal `__id_subwins(WINDOW *orig)`, resynchronizing subwindow line pointers after the original window's line storage changes.

It walks the original window's circular subwindow list, computes each subwindow's y offset from the original, and repoints each subwindow line to the corresponding slice of the original line using `win->ch_off`.

Important interactions: used by resize or insert/delete line operations that can move original window line storage. It relies on subwindow circular-list invariants.

Reliability notes: no null checks are performed; callers must pass an original window with a valid circular subwindow list.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/id_subwins.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/idcok.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/idcok.c

Read completely: 61 lines.

This file implements `idcok(WINDOW *win, bool bf)`, toggling the `__IDCHAR` flag for insert/delete-character sequence use.

The comment notes that insert/delete character capabilities are currently not used, so this function primarily preserves compatibility.

Important interactions: any future refresh optimization for character insert/delete would consume `__IDCHAR`.

Reliability notes: null windows return `ERR`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/idcok.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/idlok.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/idlok.c

Read completely: 60 lines.

This file implements `idlok(WINDOW *win, bool bf)`, toggling the `__IDLINE` flag for insert/delete-line sequence use during refresh.

Important interactions: refresh and line-update code can use `__IDLINE` to decide whether terminal insert/delete-line capabilities may be used.

Reliability notes: null windows return `ERR`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/idlok.c -->