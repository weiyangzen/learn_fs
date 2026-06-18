# Research: subset-b-005467

Grouped research for virtual terminal Unicode table generators, keyboard input, selection/paste, Unicode helper lookups, `/dev/vcs*` screen access, and the main VT console engine. Each section preserves the original source path for source-tree-aligned reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vt/gen_ucs_recompose_table.py -->
# sources/distributed-fs/ceph-client/drivers/tty/vt/gen_ucs_recompose_table.py

## Purpose
`gen_ucs_recompose_table.py` generates `ucs_recompose_table.h`, a C include file consumed by `ucs.c` to map a base Unicode BMP character plus a combining mark to a precomposed BMP code point. The default mode intentionally emits a small common table for Latin, Greek, and Cyrillic pairs; `--full` emits every canonical two-code-point BMP decomposition discoverable through Python `unicodedata`.

## Important APIs, Types, And Functions
- `COMMON_RECOMPOSITION_PAIRS` is the curated default table, stored as `(base, combining, recomposed)` integer triples.
- `collect_all_recomposition_pairs()` scans code points `0..0xffff`, skips unassigned/control entries, rejects compatibility decompositions containing `<...>`, accepts simple two-part canonical decompositions, and returns sorted triples.
- `validate_common_pairs()` verifies the curated list is a subset of the generated full list with matching results.
- `generate_recomposition_table(use_full_list=False, out_file=DEFAULT_OUT_FILE)` selects the list, calculates min/max base and mark bounds, and writes the static C table plus `UCS_RECOMPOSE_*` boundary macros.
- CLI handling uses `argparse` for `--full` and `-o/--output`.

## Control Flow And State
On execution, arguments are parsed and `generate_recomposition_table()` is called. Both default and full modes first build the full table so the default table can be validated against the active Python Unicode database. The emitted table is sorted by base then mark, matching the binary-search comparator in `ucs.c`. Boundary macros allow `ucs_recompose()` to reject impossible searches before bsearch.

## State And Persistence Behavior
The script has no persistent runtime state beyond the output header. Reproducibility depends on Python's `unicodedata.unidata_version`, which is embedded in the generated header. The default curated table is stable in source; the `--full` table can change when the host Python Unicode database changes.

## Dependencies And Integration Points
It depends on the Python standard library: `unicodedata`, `argparse`, `textwrap`, and `pathlib`. The VT `Makefile` can regenerate `ucs_recompose_table.h` when `GENERATE_UCS_TABLES` is enabled, passing `--full` when `GENERATE_UCS_TABLES := 2`. `ucs.c` includes the generated file after defining `struct ucs_recomposition`.

## Risks And Edge Cases
The full scan is BMP-only because the generated C type uses `u16`; non-BMP recomposition pairs are omitted by design. The script imports `sys` but does not use it. An empty selected table would make `min()`/`max()` fail, though both current modes produce entries. Unicode-version drift can change `--full` output and validation expectations. The generated file is not guarded by include guards because it is intended as a private include inside `ucs.c`.

## Test Signals
Run `python3 gen_ucs_recompose_table.py -o /tmp/ucs_recompose_table.h` and check that it reports common mode, writes sorted triples, and emits min/max macros. Run `python3 gen_ucs_recompose_table.py --full -o /tmp/ucs_recompose_table_full.h` and confirm the full output compiles through `ucs.c`. A useful unit check is verifying that common pairs such as `A + U+0301 -> U+00C1`, Greek tonos pairs, and Cyrillic breve pairs are present and that default validation fails if a curated triple is corrupted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vt/gen_ucs_recompose_table.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vt/gen_ucs_width_table.py -->
# sources/distributed-fs/ceph-client/drivers/tty/vt/gen_ucs_width_table.py

## Purpose
`gen_ucs_width_table.py` generates `ucs_width_table.h`, the interval tables used by `ucs.c` and then `vt.c` to classify Unicode code points as zero-width or double-width for Linux console rendering. It combines Unicode category/East Asian Width data with terminal-oriented overrides for emoji, variation selectors, tag characters, and regional indicators.

## Important APIs, Types, And Functions
- `KNOWN_ZERO_WIDTH`, `EMOJI_ZERO_WIDTH`, `REGIONAL_INDICATORS`, and `EMOJI_RANGES` define policy overrides before and after Unicode-property classification.
- `create_width_tables()` builds `width_map` for all Unicode scalar positions through `0x10ffff`, assigns width 0 to marks and format controls, width 2 to EAW `F`/`W`, width 1 to narrow/neutral/ambiguous classes, then forces emoji ranges to width 2 unless already zero-width.
- The nested `ranges_optimize()` compacts individual code points into sorted inclusive ranges.
- `write_tables()` splits ranges into BMP `struct ucs_interval16` and non-BMP `struct ucs_interval32` arrays and writes C comments from `unicodedata.name()`.
- The CLI accepts `-o/--output`, writes the table, and prints range/count/version summary.

## Control Flow And State
Generation first applies zero-width emoji modifiers and single-width regional indicators, then walks Unicode in `0x1000`-sized blocks and assigns widths to unprocessed code points. Emoji ranges are applied last so many neutral pictographs become double-width while zero-width modifiers remain zero-width. The output order is zero-width BMP, zero-width non-BMP, double-width BMP, and double-width non-BMP, matching the symbols expected by `ucs.c`.

## State And Persistence Behavior
The script writes a generated header and embeds the active Python Unicode database version. It keeps no persistent state. The generated table is deterministic for a fixed script and Python Unicode version, but it can change when `unicodedata` changes or when terminal policy overrides are edited.

## Dependencies And Integration Points
It depends on Python `unicodedata`, `argparse`, and `pathlib`. The VT `Makefile` can use it to generate `ucs_width_table.h` when `GENERATE_UCS_TABLES` is set; otherwise shipped generated headers are used. `ucs.c` includes the generated arrays after defining `struct ucs_interval16` and `struct ucs_interval32`; `vt.c` ultimately consumes the lookups via `ucs_is_zero_width()` and `ucs_is_double_width()`.

## Risks And Edge Cases
The policy deliberately treats ambiguous-width characters as single-width, which is important for Linux console compatibility but differs from some CJK terminal settings. Regional indicators are width 1 individually so flag pairs combine to width 2 conceptually, but the VT renderer does not implement full grapheme clustering. Emoji modifiers such as gender signs are forced zero-width, which may hide standalone characters. The script catches broad exceptions in comment generation, so invalid-name cases degrade to code-point comments. It also imports `sys` but does not use it.

## Test Signals
Generate into a temporary path and compile `ucs.c` against it. Inspect that combining marks and format controls land in zero-width ranges, CJK ideographs and emoji pictographs land in double-width ranges, regional indicators do not become double-width, and variation selectors stay zero-width. Runtime signals include Linux console rendering of combining marks, VS16, emoji, and CJK characters with expected cursor advancement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vt/gen_ucs_width_table.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vt/keyboard.c -->
# sources/distributed-fs/ceph-client/drivers/tty/vt/keyboard.c

## Purpose
`keyboard.c` is the virtual terminal keyboard input engine. It registers the input-layer keyboard handler, translates input key events through console keymaps, emits bytes or UTF-8 to the active VC tty, manages keyboard modes and LEDs, implements dead-key/diacritic composition and Braille chords, exposes keyboard ioctls used by `vt_ioctl.c`, and supports notifier hooks for keyboard events.

## Important APIs, Types, And Functions
- Global per-console state lives in `kbd_table[MAX_NR_CONSOLES]`; `kbd` points at the active console's entry while processing.
- Handler dispatch is table-driven through `k_handler[]` for key symbol types and `fn_handler[]` for special VT functions.
- Public registration and lifecycle APIs include `register_keyboard_notifier()`, `unregister_keyboard_notifier()`, and `kbd_init()`.
- Input integration is through `kbd_handler` with `.event = kbd_event`, `.match = kbd_match`, `.connect = kbd_connect`, `.disconnect = kbd_disconnect`, and `.start = kbd_start`.
- Core event flow is `kbd_event()` -> `kbd_keycode()` -> keymap lookup/notifiers -> typed handler such as `k_unicode()`, `k_fn()`, `k_shift()`, `k_pad()`, `k_cur()`, or `k_csi()`.
- Ioctl helpers include `vt_do_diacrit()`, `vt_do_kdskbmode()`, `vt_do_kdskbmeta()`, `vt_do_kbkeycode_ioctl()`, `vt_do_kdsk_ioctl()`, `vt_do_kdgkb_ioctl()`, `vt_do_kdskled()`, `vt_do_kdgkbmode()`, and `vt_do_kdgkbmeta()`.
- VT integration helpers include `vt_reset_unicode()`, `vt_get_shift_state()`, `vt_reset_keyboard()`, `vt_get_kbd_mode_bit()`, `vt_set_kbd_mode_bit()`, `vt_clr_kbd_mode_bit()`, `vt_kbd_con_start()`, and `vt_kbd_con_stop()`.

## Control Flow And State
`kbd_init()` initializes each console with default LED flags, lock state, repeat/meta flags, and `VC_UNICODE` or `VC_XLATE` based on `default_utf8`, then registers the input handler and enables the LED tasklet. For each input event, `kbd_event()` takes `kbd_event_lock`, forwards raw MSC events to `kbd_rawcode()` when appropriate, and forwards key events to `kbd_keycode()`. After processing it schedules LED updates, pokes the blanked console, and schedules the VT console callback.

`kbd_keycode()` selects the foreground VC, handles raw and medium-raw modes, updates the global `key_down` bitmap, suppresses repeats when configured or when tty buffers are backed up, computes the effective shift/lock map, calls keyboard notifiers, and dispatches to Unicode or typed handlers. Cursor and CSI keys include modifier encoding through `csi_modifier_param()`. Dead keys store `diacr`; the next character passes through `handle_diacr()` and the global `accent_table`. Braille keys collect dot patterns and either emit Unicode Braille or act as dead chords.

## State And Persistence Behavior
State is runtime-only kernel state. Per-console `kbd_struct` entries hold mode flags, LED flags, lock/slock state, and keyboard mode. Global transient state includes `key_down`, `shift_down`, `shift_state`, `diacr`, `dead_key_next`, numeric keypad character assembly, repeat flag `rep`, LED state/cache, function-key string table contents, and the global diacritic table. Ioctls can mutate keymaps, function strings, keyboard mode, meta behavior, LEDs, and diacritics until reset or module/kernel lifetime ends.

## Dependencies And Integration Points
This file depends on the input subsystem, tty flip buffers, VT console state from `vt.c`, keymap data from `defkeymap`/`consolemap`, LED triggers or EV_LED injection, timers, tasklets, workqueues, notifiers, and user-copy helpers. It integrates with `vt.c` through mode-bit helpers, console switching, scrollback, blanking, SAK work, and `default_utf8`. It integrates with `vt_ioctl.c` through exported ioctl helpers and with `selection.c` indirectly through shift/mouse reporting.

## Risks And Edge Cases
Locking is split across `kbd_event_lock`, `led_lock`, and `func_buf_lock`; comments still call out locking review needs for LED updates. Raw mode emulation is architecture-specific and may warn for unrepresentable keycodes. Keymap mutation must validate type/value bounds and SAK permissions carefully. Function string replacement uses mixed static/kmalloc ownership tracked by a bitmap. `vt_get_shift_state()` and mode-bit reads are intentionally transient and not fully synchronized. Unicode mode is required for Braille patterns; otherwise input is rejected with a warning.

## Test Signals
Useful tests include input-handler registration, console typing in `K_XLATE`, `K_UNICODE`, `K_RAW`, `K_MEDIUMRAW`, and `K_OFF`, LED propagation on lock keys and tty stop/start, keymap get/set ioctls including invalid bounds, function-key string get/set, dead-key composition through both legacy and Unicode diacritic ioctls, modifier CSI sequences for cursor/function keys, Alt-numpad decimal/hex input, Braille chord input, VT switching hotkeys, SysRq/SAK behavior, and suspend of repeat under tty backlog.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vt/keyboard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vt/selection.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vt/selection.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vt/ucs.c -->
# sources/distributed-fs/ceph-client/drivers/tty/vt/ucs.c

## Purpose
`ucs.c` provides compact Unicode helper lookups for the virtual terminal. It classifies zero-width and double-width code points using generated interval tables, recomposes a base code point plus combining mark using a generated recomposition table, and returns fallback display substitutions for characters missing from the current console font.

## Important APIs, Types, And Functions
- `struct ucs_interval16` and `struct ucs_interval32` define generated width intervals included from `ucs_width_table.h`.
- `ucs_is_zero_width(u32 cp)` and `ucs_is_double_width(u32 cp)` dispatch BMP and non-BMP lookups through binary search.
- `struct ucs_recomposition` and `ucs_recompose(u32 base, u32 mark)` use `ucs_recompose_table.h` plus generated min/max macros.
- `struct ucs_page_desc`, `struct ucs_page_entry`, and `ucs_get_fallback(u32 cp)` implement a two-level BMP fallback table from `ucs_fallback_table.h`.
- Local comparators support `__inline_bsearch()` for interval, recomposition, page, and page-entry lookup.

## Control Flow And State
Width classification first rejects code points outside the first/last interval in the relevant generated array, then binary-searches for a containing interval. Recomposition rejects base/mark values outside generated boundary macros before bsearching the sorted pair table. Fallback lookup rejects non-BMP, handles fullwidth ASCII `U+FF01..U+FF5E` algorithmically, finds a page descriptor by high byte, and then finds an offset or range marker within that page.

## State And Persistence Behavior
The file has no mutable runtime state. All data is static generated tables compiled into the kernel object. Behavior changes only when the generated headers or Python Unicode-generation inputs change, or when `CONFIG_CONSOLE_TRANSLATIONS` controls whether these helpers are declared as real functions versus stubs in `consolemap.h`.

## Dependencies And Integration Points
It depends on `linux/bsearch.h`, `linux/array_size.h`, `linux/minmax.h`, and `linux/consolemap.h`. `vt.c` uses the width helpers in `vc_process_ucs()` for cursor advancement and zero-width behavior, uses `ucs_recompose()` for combining marks, and uses `ucs_get_fallback()` in `vc_get_glyph()` when font glyph lookup fails. The generated headers are produced by scripts in the same directory and wired by the VT `Makefile`.

## Risks And Edge Cases
`cp_in_range16()` and `cp_in_range32()` index `ranges[0]` and `ranges[size - 1]`, so generated arrays must never be empty. `ucs_recompose()` stores 32-bit inputs into 16-bit search keys after boundary checks; correctness depends on BMP-only generated bounds. Fallbacks are BMP-only and intentionally approximate display, not semantic equivalence. Range-marker entries in the fallback table require a following entry; malformed generated data could make lookup read the wrong fallback.

## Test Signals
Unit-style checks should cover BMP and non-BMP width ranges, boundary values before the first and after the last interval, known combining marks, CJK double-width characters, emoji width overrides, common recompositions, fullwidth ASCII fallback, table range-marker fallback, and no-fallback returns. Integration signals include proper cursor movement and `/dev/vcsu*` Unicode retrieval for double-width, zero-width, and fallback-rendered characters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vt/ucs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vt/vc_screen.c -->
# sources/distributed-fs/ceph-client/drivers/tty/vt/vc_screen.c

## Purpose
`vc_screen.c` implements the `/dev/vcs`, `/dev/vcsN`, `/dev/vcsaN`, and `/dev/vcsuN` character devices that expose virtual console screen memory to user space. It supports foreground-console proxy minors, glyph and attribute formats, Unicode screen reads, writes to glyph/attribute devices, polling/fasync for VT updates, and sysfs device creation/removal.

## Important APIs, Types, And Functions
- Minor decoding macros split console number, Unicode mode, and attribute mode.
- `struct vcs_poll_data` stores a VT notifier, wait queue, fasync state, event code, and console number.
- `vcs_vc()` resolves an inode to a `vc_data` under `console_lock`.
- `vcs_size()` calculates visible file size for glyph, attribute, and Unicode modes.
- File operations are `vcs_lseek()`, `vcs_read()`, `vcs_write()`, `vcs_poll()`, `vcs_fasync()`, `vcs_open()`, and `vcs_release()`.
- Buffer helpers include `vcs_read_buf_uni()`, `vcs_read_buf_noattr()`, `vcs_read_buf()`, `vcs_write_buf_noattr()`, and `vcs_write_buf()`.
- Device lifecycle APIs are `vcs_make_sysfs()`, `vcs_remove_sysfs()`, and `vcs_init()`.

## Control Flow And State
`vcs_init()` registers major `VCS_MAJOR`, registers class `vc`, creates the foreground proxy devices, and creates devices for initially allocated consoles. Open rejects Unicode-with-attributes minors and nonallocated numbered consoles. Reads allocate one page, take `console_lock`, verify size and alignment, copy screen data into the page while locked, drop the lock for `copy_to_user()`, then reacquire and continue because console state may change while copying. Unicode reads require 4-byte aligned position/count and call `vc_uniscr_check()` before copying lines through `vc_uniscr_copy_line()`.

Writes reject Unicode minors, copy user data into a temporary page outside the console lock, revalidate the VC and size, then update screen memory under the lock. Attribute-mode writes may update the 4-byte header cursor position for background consoles and write native-endian attribute/character words; glyph-only writes preserve attributes. Updated regions are redrawn with `update_region()` and update notifiers are emitted through `vcs_scr_updated()`.

## State And Persistence Behavior
Persistent device state is per-open `file->private_data` for poll/fasync. It is lazily allocated and registered with the VT notifier list, protected from races by `file->f_lock`, and freed on release. Screen contents live in `vc_data`, not in this file. Reads and writes observe live console state and may return partial progress if the VC disappears or size changes.

## Dependencies And Integration Points
The file depends on the VT core (`vc_cons`, `fg_console`, `vc_cons_allocated`, `update_region`, Unicode side-buffer helpers, screen accessors), selection state for clean screen dumping, keyboard/console headers, Linux char-device/file/poll/fasync infrastructure, user-copy APIs, and notifier chains. It receives `VT_UPDATE` and `VT_DEALLOCATE` from `vt.c` to drive `poll()` and `SIGIO`.

## Risks And Edge Cases
The minor space assumes `MAX_NR_CONSOLES <= 63`; the file emits a preprocessor warning otherwise. Unicode attributes are explicitly unsupported. Unicode read alignment is strict. The foreground proxy minor follows `fg_console` dynamically, so reads can observe different consoles across calls. Copying to or from user requires dropping `console_lock`, so every loop revalidates size and allocation. Poll state allocation can race across threads sharing a file descriptor and is carefully collapsed to one survivor.

## Test Signals
Test opening `/dev/vcs`, `/dev/vcs1`, `/dev/vcsa1`, `/dev/vcsu`, and unsupported Unicode+attribute minors. Verify lseek sizes, 4-byte Unicode alignment errors, header row/column/cursor bytes, glyph-only reads preserving attributes, writes updating screen memory and redraws, poll returning `POLLPRI` on updates and `POLLHUP` on deallocate, fasync `SIGIO`, foreground proxy behavior across VT switches, and sysfs device creation/removal as consoles allocate/deallocate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vt/vc_screen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vt/vt.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/vt/vt.c -->
