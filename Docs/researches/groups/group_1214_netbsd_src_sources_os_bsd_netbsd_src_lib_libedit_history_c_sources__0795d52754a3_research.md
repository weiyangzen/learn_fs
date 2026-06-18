# Group Research: group_1214_netbsd_src_sources_os_bsd_netbsd_src_lib_libedit_history_c_sources__0795d52754a3

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/netbsd-src` is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/history.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/history.c

## Purpose
Implements libedit's `History` API, with wide-character support by default and a narrow-character variant when included through `historyn.c`. It provides the public varargs dispatcher `history_w()`/`history()` and the default in-memory history backend.

## Main Components
- `struct history`: API-level object holding function pointers for history operations and a backend reference.
- `history_t`: built-in circular doubly linked list backend with a sentinel node, cursor, maximum size, current size, monotonic event IDs, and `H_UNIQUE` flag.
- `hentry_t`: list node containing `HistEvent`, optional user `data`, and links.
- `HistEventPrivate`: internal event layout used for string ownership and event number mutation.

## Key Behavior
- Default backend supports first/last/next/previous/current navigation, set by event number, nth-position set/delete, clear, enter, append, and delete.
- `H_ENTER` inserts new entries at the head and trims from the tail when `cur > max`.
- `H_SETUNIQUE` suppresses adjacent duplicate entries only; it does not deduplicate the whole history list.
- `H_FUNC` replaces the default backend with caller-supplied function pointers; default-only operations such as size/unique are rejected once custom functions are active.
- File persistence uses `_HiStOrY_V2_\n` cookie, `strvis`/`strunvis`, and chartype encode/decode glue.
- `H_SAVE_FP` writes all entries; `H_NSAVE_FP` can save a bounded subset.
- Readline wrapper extensions use `H_NEXT_EVDATA`, `H_DELDATA`, and `H_REPLACE` for GNU-readline-style entry data and replacement.

## Dependencies
Uses `histedit.h`, optional `chartype.h`, `<vis.h>`, file I/O, and allocator macros over libc allocation. It is consumed heavily by `readline.c` and the broader editline history command layer.

## Notes
`H_REPLACE` assigns a duplicated new string but does not free the prior string in the cursor entry, so callers need to understand existing ownership behavior. `history_save()` leaks the raw fd if `fdopen()` fails because the fd is not closed on that path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/history.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/historyn.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/historyn.c

## Purpose
Build shim for the narrow-character history implementation.

## Behavior
Defines `NARROWCHAR` and includes `history.c`, causing the macro layer in `history.c` to generate narrow `char`/`HistEvent`/`History` symbols instead of wide-character variants.

## Dependencies
Includes `config.h` first, then reuses the full implementation in `history.c`.

## Notes
This file intentionally contains no independent logic; all semantics and risks are inherited from `history.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/historyn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/keymacro.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/keymacro.c

## Purpose
Maintains libedit's extended key/macro map: multi-character input sequences that resolve to editor commands or replacement strings.

## Main Components
- `keymacro_node_t`: trie-like node with one wide character, type (`XK_CMD`, `XK_STR`, `XK_NOD`), value, `next` child, and `sibling`.
- Public internal API: `keymacro_init`, `keymacro_end`, `keymacro_reset`, `keymacro_get`, `keymacro_add`, `keymacro_delete`, `keymacro_print`, `keymacro_clear`.
- Recursive helpers: `node_trav`, `node__try`, `node__delete`, `node__put`, `node_lookup`, `node_enum`.

## Key Behavior
- `keymacro_get()` traverses the trie, reading more input with `el_wgetc()` until it finds a command/string leaf or a mismatch.
- `keymacro_add()` rejects empty sequences and binding `ED_SEQUENCE_LEAD_IN` as a command. Adding a sequence that is a prefix of longer sequences discards the longer subtree.
- String macro values are duplicated on insertion and freed when replaced/deleted.
- `keymacro_clear()` removes a macro binding when a single-character key is rebound away from sequence-lead-in status.
- Print helpers render human-readable key bindings with `ct_visual_char`, `ct_encode_string`, and function metadata from `el_map.help`.

## Dependencies
Depends on `el.h`, `fcns.h`, chartype conversion helpers, keymap state from `map.c`, and input from `read.c`.

## Notes
The implementation intentionally does not support both a key and a longer key sharing that key as prefix. Several allocation failure paths return `-1` internally, but `keymacro_add()` itself is `void`, so callers do not receive insertion failure status.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/keymacro.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/keymacro.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/keymacro.h

## Purpose
Declares the internal key macro state and APIs for multi-character key bindings.

## Main Components
- `keymacro_value_t`: union of editor command ID or wide string pointer.
- Opaque `keymacro_node_t`.
- `el_keymacro_t`: print buffer, trie root, and temporary value buffer.
- Binding type constants: `XK_CMD`, `XK_STR`, `XK_NOD`.

## Exposed Functions
Declares initialization, cleanup, reset, lookup, add, clear, delete, print, printable binding output, and string decode helpers.

## Dependencies
Requires `EditLine`, `el_action_t`, and `libedit_private` definitions from surrounding libedit headers.

## Notes
This header exposes only internal libedit interfaces, not the public histedit API.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/keymacro.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/literal.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/literal.c

## Purpose
Stores literal terminal escape/display sequences embedded in prompts so refresh code can account for visible width while outputting the original byte sequence.

## Main Components
- `literal_init()` zeroes `el_literal`.
- `literal_clear()` frees all stored literal strings and resets counters.
- `literal_add()` encodes a literal span and returns a magic `EL_LITERAL | index` character for the virtual display.
- `literal_get()` resolves a magic literal character back to the saved byte string.

## Key Behavior
- Computes visible width from `wcwidth(end[1])`, then encodes the literal bytes from the prompt span plus the visible char.
- Grows the literal buffer array in increments of four.
- Nonprintable or allocation-failure cases return `0`, meaning no literal placeholder is emitted.

## Dependencies
Uses `ct_enc_width`, `ct_encode_char`, libedit allocation wrappers, and `EL_LITERAL` from `literal.h`.

## Notes
`literal_get()` uses assertions for index validity; invalid magic characters are programmer errors rather than runtime-checked failures.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/literal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/literal.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/literal.h

## Purpose
Defines the literal prompt sequence storage type and API.

## Main Components
- `EL_LITERAL`: high-bit marker for virtual-display placeholder characters.
- `el_literal_t`: dynamic array of saved byte strings plus used/allocated counters.
- Function declarations for init, end, clear, add, and get.

## Dependencies
Requires `EditLine`, `wint_t`, and libedit internal visibility macros.

## Notes
The `EL_LITERAL` marker assumes `wint_t` can hold the high-bit sentinel and index bits.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/literal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/makelist -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/makelist

## Purpose
Shell/awk generator used by libedit's build to derive binding headers and function tables from source comments/prototypes.

## Modes
- `-h`: generate a guarded header of `libedit_private el_action_t` prototypes for `vi_*`, `em_*`, and `ed_*` functions found in source comments.
- `-bh`: generate `help.h` with `el_func_help[]`, command names, and descriptions.
- `-fh`: generate `fcns.h` numeric `#define`s for sorted editor functions plus `EL_NUM_FCNS`.
- `-fc`: generate `func.h` with the sorted `el_func[]` function pointer table.

## Dependencies
Uses `/bin/sh`, `sed`, `awk`, `sort`, `tr`, and input file comment conventions such as `function():`.

## Notes
The script relies on fixed source formatting and comment structure. It is build tooling rather than runtime code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/makelist -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/map.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/map.c

## Purpose
Defines editor key maps, initializes emacs/vi binding modes, prints bindings, processes `bind` commands, and registers user-defined editor functions.

## Main Components
- Static maps: `el_map_emacs`, `el_map_vi_insert`, and `el_map_vi_command`, each sized for `N_KEYS`.
- Runtime state allocation in `map_init()`: normal map, alternate map, help table, function table, and wordchars.
- Mode initializers: `map_init_emacs()` and `map_init_vi()`.
- Binding command implementation: `map_bind()`.

## Key Behavior
- `map_init()` copies generated function/help tables into mutable runtime arrays, selects default editor mode, and initializes wordchars.
- `map_init_meta()` converts high-bit meta bindings into ESC-prefixed key macros where needed.
- `map_init_nls()` binds printable high-byte characters to insertion.
- Emacs mode adds `^X^X` exchange-mark binding; both modes bind terminal arrow keys.
- `map_bind()` handles switches for alternate map, string binding, terminal key binding, removal, vi/emacs mode selection, and listing.
- `map_addfunc()` appends a user-supplied function and matching help entry.

## Dependencies
Uses generated `fcns.h`, `func.h`, `help.h`, editor function headers, `parse.c`, `keymacro.c`, terminal binding helpers, and tty binding helpers.

## Notes
`map_addfunc()` can leave `func` reallocated if the subsequent `help` reallocation fails. Binding operations use `unsigned char` indexes for single-character keys.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/map.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/map.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/map.h

## Purpose
Declares keymap state, binding metadata, and editor map management APIs.

## Main Components
- `el_func_t`: editor command function pointer.
- `el_bindings_t`: command number, command name, and description.
- `el_map_t`: normal/alternate/current maps, default map pointers, mode type, help/function arrays, function count, and wordchars.
- Constants `MAP_EMACS`, `MAP_VI`, and `N_KEYS`.

## Exposed Functions
Binding command, map init/end, emacs/vi mode initialization, editor get/set, wordchars get/set, and dynamic function registration.

## Notes
This is internal libedit state that backs public `el_set`/`el_get` behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/map.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/parse.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/parse.c

## Purpose
Parses and dispatches editline configuration/extended commands, and decodes key-binding escape syntax.

## Main Components
- Command table for `bind`, `echotc`, `edit`, `history`, `telltc`, `settc`, and `setty`.
- `parse_line()` tokenizes a wide string with `TokenizerW` and dispatches through `el_wparse()`.
- `el_wparse()` handles optional program-prefix filtering of the form `prog:command`.
- `parse__escape()` decodes caret notation, C-style escapes, octal escapes, and `\U+xxxx`/`\U+xxxxx`.
- `parse__string()` converts escaped binding text to raw wide characters.
- `parse_cmd()` maps command names to function numbers.

## Dependencies
Uses tokenizer APIs from histedit, `el_match()` from search, and command handlers from map/history/terminal/tty modules.

## Notes
Unicode escape parsing only accepts uppercase hex digits because the hex table is `0123456789ABCDEF`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/parse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/parse.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/parse.h

## Purpose
Declares parser and escape decoding functions for editline command processing.

## Exposed Functions
`parse_line`, `parse__escape`, `parse__string`, and `parse_cmd`.

## Dependencies
Requires `EditLine`, wide-character types, and libedit private visibility.

## Notes
The header intentionally exposes the lower-level escape parser because key binding code calls it directly.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/parse.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/prompt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/prompt.c

## Purpose
Manages left and right prompts and renders them into the refresh virtual display.

## Main Components
- Default prompt functions: left prompt `"? "`, right prompt empty string.
- `prompt_print()` chooses left/right prompt, obtains wide or narrow prompt text, emits display characters, and tracks prompt cursor position.
- `prompt_set()` installs prompt function, ignored-literal delimiter, and wide/narrow mode.
- `prompt_get()` returns the current prompt callback and ignore delimiter.
- Init/end functions set defaults.

## Key Behavior
- Prompt literal spans are delimited by `p_ignore`; their bytes are sent through `re_putliteral()` so non-display escape sequences do not corrupt column accounting.
- Narrow prompt callbacks are decoded through `ct_decode_string()`.
- If a literal span is unterminated or ends at prompt end, rendering stops and the last literal is lost by design/comment.

## Dependencies
Uses refresh functions `re_putc` and `re_putliteral`, chartype decoding, and `el_prompt_t` from `prompt.h`.

## Notes
Right prompt is only useful when refresh determines it fits on the first display line.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/prompt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/prompt.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/prompt.h

## Purpose
Defines prompt callback/state structures and prompt management APIs.

## Main Components
- `el_pfunc_t`: prompt callback returning a wide string pointer.
- `el_prompt_t`: prompt callback, last rendered position, ignored-literal delimiter, and wide/narrow flag.

## Exposed Functions
Prompt print, set, get, init, and end.

## Notes
The same structure is used for both primary and right prompt state in `EditLine`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/prompt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/read.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/read.c

## Purpose
Implements libedit's terminal input path: character reading, macro pushback, command lookup, editor-function execution, and line-return logic.

## Main Components
- `struct macros`: stack-like macro buffer with fixed maximum nesting `EL_MAXMACRO`.
- `struct el_read_t`: macro state, current read callback, and saved read errno.
- `read_char()`: built-in byte reader converting multibyte input to `wchar_t`.
- `read_getcmd()`: reads a character, handles meta mode, key maps, and key macros.
- `el_wgets()`: main wide-character line editing loop.
- `read_prepare()`/`read_finish()`: signal, tty, resize, and refresh setup/teardown.

## Key Behavior
- `el_wpush()` pushes macro strings onto the input stream; macro exhaustion pops and frees strings.
- `read_char()` recovers from `EINTR`, `EAGAIN`/`EWOULDBLOCK` and nonblocking settings where possible, handles `SIGCONT` and `SIGWINCH`, and decodes multibyte input with `mbrtowc`.
- `el_wgets()` supports no-tty and edit-disabled paths through `noedit_wgets()`.
- The edit loop invokes mapped editor functions and interprets return codes such as `CC_REFRESH`, `CC_CURSOR`, `CC_NEWLINE`, `CC_EOF`, and `CC_FATAL`.

## Dependencies
Uses tty, terminal, keymacro, map, refresh, signal, and character editing modules.

## Notes
Macro nesting is capped at 10. The multibyte decoder comment notes it assumes UTF-8 stateless behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/read.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/read.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/read.h

## Purpose
Declares internal read subsystem lifecycle and callback management APIs.

## Exposed Functions
`read_init`, `read_end`, `read_prepare`, `read_finish`, `el_read_setfn`, and `el_read_getfn`.

## Dependencies
Requires `EditLine`, `struct el_read_t`, and `el_rfunc_t` declarations from surrounding libedit headers.

## Notes
The public character-reading functions themselves are declared elsewhere; this header covers subsystem plumbing.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/read.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/readline.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/readline.c

## Purpose
Provides a GNU Readline compatibility layer over libedit, including global readline variables, `readline()`, history functions, completion adapters, callback mode, and many compatibility stubs.

## Main Components
- Singleton state: static `EditLine *e`, `History *h`, key function map, and `jmp_buf topbuf`.
- Readline globals: streams, prompt, line buffer, point/end, completion globals, history counters, signal flags, and compatibility keymaps.
- Initialization: `rl_initialize()` creates/reset `EditLine` and `History`, configures prompt, signals, emacs mode, terminal name, readline completion function, suspend binding, search binding, Home/End/Delete/word-motion bindings, and `.editrc` source.
- Main line reader: `readline()` sets prompt/hooks, uses `el_gets()`, strips trailing newline, and updates history length.

## History Support
Implements `using_history`, `add_history`, `clear_history`, `stifle_history`, `unstifle_history`, `history_get`, `remove_history`, `replace_history_entry`, `history_list`, current/previous/next history, search functions, read/write/append history, truncate history file, csh-style `history_expand`, tokenization, event selection, and argument extraction.

## Completion Support
Wraps file and username completion through `filecomplete` helpers. `rl_complete()` maps readline globals into `fn_complete2()`. `rl_completion_matches()` builds readline-style match arrays and common prefix.

## Terminal/Callback Support
Includes `rl_callback_handler_install`, `rl_callback_read_char`, `rl_callback_handler_remove`, prompt save/restore, redisplay, prep/deprep terminal, parse/bind config, screen size get/set, message display, and text insert/replace/delete/copy operations.

## Compatibility Stubs
Several APIs are declared/exported but minimally implemented or no-op: readline keymap creation/get/set/bind operations, cleanup/free line state, keyboard timeout, abort, keymap naming, free history entry, erase entire line, and `rl_kill_text`.

## Dependencies
Depends on `readline/readline.h`, `el.h`, `emacs.h`, generated function IDs, file completion, history implementation, tokenizer APIs, terminal/refresh functions, and passwd/file APIs.

## Notes
This layer is heavily global and singleton-based, matching readline's API style rather than libedit's reentrant `EditLine` style. Some compatibility globals are explicitly documented as not implemented.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/readline.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/readline/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/readline/Makefile

## Purpose
Installs the readline compatibility header subtree for NetBSD builds.

## Behavior
- Marks directory `NOOBJ`.
- Sets `.PATH` to `${NETBSDSRCDIR}/lib/libedit`.
- Installs `readline.h` to `/usr/include/readline`.
- Creates `history.h` as a symlink to `readline.h`.

## Dependencies
Uses NetBSD make includes `bsd.own.mk` and `bsd.prog.mk`.

## Notes
No build objects are produced; this is an install/include makefile.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/readline/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/readline/readline.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/readline/readline.h

## Purpose
Public GNU Readline compatibility header for libedit.

## Main Components
- Readline callback typedefs and command/completion function types.
- Minimal `HISTORY_STATE`, `HIST_ENTRY`, `KEYMAP_ENTRY`, and `Keymap` definitions.
- Control-character macros and readline version/state constants.
- Extern declarations for readline and history global variables.
- Function prototypes for supported readline/history/completion/terminal APIs.
- Separate block for declared but not implemented compatibility functions.

## Dependencies
Includes `<sys/types.h>` and `<stdio.h>`, and conditionally tty defaults for `CTRL`.

## Notes
The header doubles as `history.h` via install symlink. It intentionally exposes some nonimplemented symbols for source/binary compatibility with applications expecting GNU readline.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/readline/readline.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/refresh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/refresh.c

## Purpose
Maintains and updates libedit's terminal display, including virtual screen construction, prompt rendering, right prompt placement, cursor movement, and minimal line diffs.

## Main Components
- Virtual drawing helpers: `re_putc`, `re_putliteral`, `re_addc`, `re_nextline`.
- Full refresh: `re_refresh()`.
- Incremental line update: `re_update_line()`.
- Cursor-only refresh: `re_refresh_cursor()`.
- Fast append path: `re_fastaddc()` and `re_fastputc()`.
- Clear helpers: `re_clear_display`, `re_clear_lines`, `re_goto_bottom`.

## Key Behavior
- `re_refresh()` clears literal state, redraws prompt/input into `el_vdisplay`, computes cursor coordinates, optionally places right prompt if it fits, diffs virtual rows against real rows, then moves the terminal cursor to logical edit position.
- Wide chars, tabs, newlines, control chars, nonprintables, and prompt literals are converted to display cells with width accounting.
- When input exceeds screen height, display/virtual row pointers are shuffled to emulate scrolling.
- `re_update_line()` finds first/last differences and chooses overwrites, insertions, or deletions based on terminal capabilities.
- `re_fastaddc()` avoids full refresh for simple end-of-line character insertion.

## Dependencies
Uses prompt, literal, terminal capability functions, chartype display helpers, and `el_refresh_t`.

## Notes
Refresh correctness depends on terminal width/height and multicolumn character accounting. The diff algorithm deliberately falls back to simpler overwrites when terminal insert/delete capabilities are unavailable or not worthwhile.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/refresh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/refresh.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/refresh.h

## Purpose
Declares refresh state and display update APIs.

## Main Components
- `el_refresh_t`: refresh cursor and old/new vertical row counts.
- Functions for putting characters/literals, clearing display/lines, full refresh, cursor refresh, fast add, and moving to bottom.

## Dependencies
Requires `coord_t`, `EditLine`, and wide character types.

## Notes
This header is central to prompt, read, readline, search, and signal display recovery paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/refresh.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/search.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/search.c

## Purpose
Implements history and line searching for emacs and vi editing modes, including regex-backed matching and vi character searches.

## Main Components
- `search_init()`/`search_end()` manage pattern buffer state.
- `el_match()` performs substring match first, then regex/regexp/re_comp matching depending on build configuration.
- `c_setpat()` captures the current input prefix as a history search pattern.
- `ce_inc_search()` implements Emacs incremental forward/backward history search.
- `cv_search()` implements vi `/` and `?` history search.
- `ce_search_line()` searches inside the current edit buffer.
- `cv_repeat_srch()` repeats vi history search.
- `cv_csearch()` implements vi `f/F/t/T` character search behavior.

## Key Behavior
- Search state tracks pattern buffer/length/direction plus last vi character-search target/direction/type.
- Emacs incremental search temporarily appends a search prompt to the edit buffer, reads keys, updates pattern, searches current line/history, and restores state on abort/failure.
- Vi search prompts with `\n/` or `\n?`, supports repeating the prior pattern, and can submit immediately on ESC.
- Character search supports operator-pending motion completion through `cv_delfini()`.

## Dependencies
Uses regex APIs when configured, `common.h`, generated command IDs, history helpers, refresh, input, and character movement helpers.

## Notes
The optional `ANCHOR` mode rewrites patterns with `.*` anchoring behavior. Pattern storage is bounded by `EL_BUFSIZ`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/search.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/search.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/search.h

## Purpose
Defines search subsystem state and declares search APIs.

## Main Components
- `el_search_t`: pattern buffer, length, last pattern direction, vi character-search direction, target character, and `t`/`f` flag.
- Declarations for search lifecycle, matching, pattern capture, emacs incremental search, vi search, line search, repeat search, and character search.

## Dependencies
Requires `EditLine`, `el_action_t`, and wide character types.

## Notes
Search state is embedded in `EditLine` and shared across emacs and vi command implementations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/search.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/sig.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/sig.c

## Purpose
Installs temporary signal handlers while libedit is reading, restores terminal state, forwards signals to the application's original handlers, and handles resize/continue recovery.

## Main Components
- Static `sel`: current `EditLine` used by the process-global signal handler.
- `sighdl[]`: signal list generated from `ALLSIGS`.
- `sig_handler()`: common handler for all managed signals.
- `sig_init()`/`sig_end()` allocate/free signal state.
- `sig_set()` installs handlers and saves previous actions.
- `sig_clr()` restores saved actions.

## Key Behavior
- Handles `SIGINT`, `SIGTSTP`, `SIGQUIT`, `SIGHUP`, `SIGTERM`, `SIGCONT`, and `SIGWINCH`.
- On `SIGCONT`, restores raw mode, redisplays, and flushes terminal output.
- On `SIGWINCH`, resizes libedit terminal state.
- On other handled signals, restores cooked mode before forwarding.
- After local handling, restores original action for that signal, unblocks it, and re-raises the signal.

## Dependencies
Uses tty, refresh, terminal, edit command, resize, and POSIX signal APIs.

## Notes
Signal handling is process-global through `sel`, so concurrent independent `EditLine` readers would conflict. This matches traditional terminal line editor assumptions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/sig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/sig.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/sig.h

## Purpose
Defines libedit's handled signal set and signal subsystem state.

## Main Components
- `ALLSIGS`: macro list of handled signals.
- `ALLSIGSNO`: count of handled signals.
- `el_signal_t`: saved `sigaction` array, signal mask, and last signal number.
- Declarations for `sig_init`, `sig_end`, `sig_set`, and `sig_clr`.

## Dependencies
Includes `<signal.h>` and requires `EditLine` plus libedit private visibility.

## Notes
The macro-based signal list is used in both header and source to keep the handler table and mask construction synchronized.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/sig.h -->