# Group Research: group_1621_plan9_sources_os_plan9_plan9_sys_src_cmd_unix_drawterm_gui_osx_keyc_1ef8fae701a9

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/keycodes.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/keycodes.h

Macintosh keyboard scan-code and local key-symbol constants for the Carbon/OS X drawterm GUI backend.

Key contents:
- Defines `QZ_*` constants for classic Macintosh physical key codes from Inside Macintosh, including function keys, arrows, keypad keys, modifiers, and iBook-specific keys.
- Defines SDL-like `KEY_*` symbolic ranges for control, cursor, multimedia, keypad, and internal pseudo-keys.
- Provides aliases such as `KEY_BS`, `KEY_DEL`, `KEY_PGUP`, and `KEY_PGDWN`.

Role in this group:
- `gui-osx/screen.c` uses the `QZ_*` constants in `convert_key()` to translate Carbon raw key codes into Plan 9 runes and private keyboard constants from `keyboard.h`.

Notable risks:
- Right-side modifier definitions are disabled because they collide with left-side codes in the old Mac key-code model.
- The table is layout/keyboard-generation sensitive; unusual modern macOS keyboards may not match these historical codes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/keycodes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/load.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/load.c

Tiny OS X GUI wrapper exposing the public `loadmemimage()` name while delegating directly to libmemdraw’s underscored `_loadmemimage()`.

Key responsibilities:
- Includes Plan 9 compatibility headers and draw/memdraw interfaces.
- Implements `loadmemimage(Memimage *i, Rectangle r, uchar *data, int ndata)` as a pass-through.

Role in this group:
- Keeps the OS X backend ABI consistent with other drawterm GUI backends while allowing platform files to interpose selected memdraw routines.

Notable risks:
- No validation or synchronization is performed here; callers rely entirely on `_loadmemimage()` and surrounding draw locks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/load.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/screen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/screen.c

Carbon/QuickDraw/Quartz OS X screen, input, cursor, and clipboard backend for drawterm.

Key responsibilities:
- Initializes drawterm as a foreground Carbon application, allocates a full-display-sized 32-bit `Memimage`, wraps it in a `CGImage`, and starts an `osxscreen` kernel process.
- Creates the main window, menu bar, Full Screen command, pasteboard handle, Carbon event handlers, and terminal initialization.
- Translates Carbon keyboard events through `convert_key()` into Plan 9 keyboard runes/constants and sends them to `kbdq`.
- Tracks mouse motion/buttons/wheel events, including Option/Command modifier synthesis for Plan 9 button 2/button 3 behavior.
- Implements full-screen enter/leave via QuickTime `BeginFullScreen`/`EndFullScreen`.
- Implements drawterm screen hooks: `attachscreen`, `flushmemscreen`, `screenload`, `getcolor`, `setcolor`, `mouseset`, `setcursor`, and `cursorarrow`.
- Implements clipboard read/write using the Carbon Pasteboard API with UTF-16 plain text and Plan 9 rune/UTF conversion.

Important behavior:
- `screeninit()` hardcodes 32-bit `XBGR32` screen storage and allocates the backing image at full physical display size, while the window initially occupies 75% of the display.
- `screenload()` creates a subimage from the full backing `CGImage` and draws it into the current window context, flipping the Y coordinate for Quartz drawing.
- Control+Option modifier changes leave full-screen mode.
- Option and Command can synthesize Plan 9 mouse buttons while a button is down, matching X11 drawterm conventions.
- Clipboard read normalizes carriage returns to newlines.

Dependencies:
- Depends on Carbon, QuickTime full-screen APIs, CoreGraphics, Pasteboard, Plan 9 `memdraw`, draw locks, mouse queue state, and keyboard queues.
- Includes `keycodes.h` for Mac raw scan-code mapping.

Notable risks:
- Uses deprecated Carbon, QuickDraw, QuickTime, `SetCursor`, and `InitCursor` APIs.
- `setcolor()` asserts, and palette handling is intentionally absent.
- The backing image size is fixed at initialization; window resizing redraws only within current bounds rather than reallocating the backing store.
- Pasteboard sizing compares UTF-16 byte length against `sizeof rsnarf`; truncation is coarse but bounded.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/screen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/wstrtoutf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/wstrtoutf.c

Wide-rune to UTF-8 conversion helper shared with the Win32 GUI backend.

Key responsibilities:
- `wstrutflen()` computes the UTF-8 byte length of a NUL-terminated `Rune` string.
- `wstrtoutf()` converts a NUL-terminated `Rune` string into a UTF-8 byte buffer, returning required or written size depending on available space.

Role in this group:
- Used by platform clipboard paths that receive UTF-16/`Rune` text and need Plan 9 UTF strings.

Notable risks:
- In the buffer-too-small branch, `i` can be read before assignment if the first rune does not fit, so the reported required length can be undefined in that edge case.
- Assumes `Rune` storage is compatible with the platform data being passed in.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/wstrtoutf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/Makefile

Win32 GUI backend archive build recipe.

Key responsibilities:
- Includes `../Make.config`.
- Builds `libgui.a` from `alloc`, `cload`, `draw`, `load`, and `screen` objects.
- Archives with `$(AR)` and indexes with `$(RANLIB)`.

Role in this group:
- Selects the Win32-specific wrappers and `screen.c` implementation used by drawterm’s portable build.

Notable risks:
- The object list excludes `wstrtoutf.$O` even though `screen.c` uses `wstrutflen()`/`wstrtoutf()`, so this function must be supplied elsewhere or the makefile can produce an unresolved symbol depending on the full build.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/alloc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/alloc.c

Win32 GUI wrapper for memory-image allocation helpers.

Key responsibilities:
- Exposes `allocmemimage`, `freememimage`, and `memfillcolor`.
- Delegates directly to `_allocmemimage`, `_freememimage`, and `_memfillcolor`.

Role in this group:
- Provides public memdraw names for the Win32 GUI backend without the X11 pixmap interposition layer.

Notable risks:
- No Windows-specific acceleration or GDI synchronization occurs here; screen updates depend on explicit `screenload()` calls in `screen.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/cload.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/cload.c

Win32 GUI wrapper for compressed memory-image loading.

Key responsibilities:
- Implements `cloadmemimage()` as a direct call to `_cloadmemimage()`.

Role in this group:
- Complements `load.c` for compressed image data used by drawterm/libdraw paths.

Notable risks:
- No platform-specific update hook is triggered here; callers must flush dirty screen regions separately.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/cload.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/draw.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/draw.c

Win32 GUI wrapper for selected libmemdraw drawing routines.

Key responsibilities:
- Implements `memimagedraw()` by calling `_memimagedrawsetup()` then `_memimagedraw()`.
- Exposes `pixelbits()` through `_pixelbits()`.
- Exposes `memimageinit()` through `_memimageinit()`.

Role in this group:
- Provides unaccelerated in-memory draw operations for the Win32 backend.

Notable risks:
- Assumes `_memimagedrawsetup()` succeeds; unlike some wrappers, it does not check for nil before passing into `_memimagedraw()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/draw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/load.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/load.c

Win32 GUI wrapper exposing `loadmemimage()` as a direct delegation to `_loadmemimage()`.

Role in this group:
- Mirrors the OS X wrapper and keeps public memdraw naming available in the backend.

Notable risks:
- Does not mark or flush a screen region; display refresh depends on callers invoking `flushmemscreen()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/load.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/screen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/screen.c

Win32 GDI screen, input, cursor, and clipboard backend for drawterm.

Key responsibilities:
- Detects desktop bit depth, chooses a compatible Plan 9 image channel, allocates a full-desktop `Memimage`, and starts a `winscreen` kernel process.
- Registers a Win32 window class and creates the drawterm screen window.
- Implements `screenload()` using `StretchDIBits()` from the backing `Memimage` into the window DC.
- Handles mouse, wheel, paint, keyboard, palette, close, and cursor messages in `WindowProc`.
- Maps selected virtual keys to Plan 9 private keyboard constants and sends `WM_CHAR` text to `kbdq`.
- Builds a Plan 9-compatible 8-bit palette and BITMAPINFO table.
- Implements Win32 cursor creation from Plan 9 cursor bitmaps.
- Implements clipboard read/write for `CF_UNICODETEXT` and `CF_TEXT`.
- Provides `atlocalconsole()` returning true.

Important behavior:
- Uses desktop dimensions for the backing screen rectangle, even though the window starts with default Win32 sizing.
- Clips flush rectangles both to the backing image and current window rectangle.
- Right mouse with Shift is mapped as button 2; otherwise right mouse maps as button 3.
- Mouse wheel emits Plan 9 buttons 8 or 16.
- Unicode clipboard writes also publish a plain `CF_TEXT` copy.

Dependencies:
- Depends on Win32 windowing/GDI/clipboard APIs plus drawterm kernel mouse/keyboard queues.
- Uses `wstrutflen()` and `wstrtoutf()` for Unicode clipboard reads.

Notable risks:
- `WM_MOUSEWHEEL` sets `b` before `b` is initialized and then falls through into code that resets `b`, so wheel-button behavior appears suspect.
- `WM_CHAR` maps `'\n'` to `'\r'` and `'\r'` to `'\n'`, which is intentional but host-message dependent.
- `setcolor()` is a no-op, so palette mutation requests are ignored.
- The backing image is not resized with the window.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/screen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/wstrtoutf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/wstrtoutf.c

Same wide-rune to UTF-8 helper as the OS X backend.

Key responsibilities:
- Computes UTF-8 length for a NUL-terminated `Rune` string.
- Converts `Rune` text to UTF-8 into a bounded buffer.

Role in this group:
- Supports Win32 Unicode clipboard conversion in `screen.c`.

Notable risks:
- Contains the same uninitialized `i` edge case when the output buffer is too small before converting any rune.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/wstrtoutf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-x11/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-x11/Makefile

X11 GUI backend archive build recipe.

Key responsibilities:
- Includes `../Make.config`.
- Builds `libgui.a` from `x11.$O` and `keysym2ucs-x11.$O`.
- Archives and indexes the result.

Role in this group:
- Selects the X11 backend plus Unicode keysym conversion table.

Notable risks:
- Build relies on X11 headers/libraries being supplied by the surrounding configuration rather than this makefile.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-x11/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-x11/keysym2ucs-x11.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-x11/keysym2ucs-x11.c

Public-domain generated X11 keysym-to-Unicode conversion table from Markus Kuhn’s xterm-era mapping.

Key responsibilities:
- Defines sorted `keysymtab[]` pairs mapping non-Latin-1 X11 keysyms to UCS values.
- Covers many scripts and symbol ranges, including Latin extended, Kana, Arabic, Cyrillic, Greek, technical symbols, box drawing, publishing symbols, Hebrew, Thai, Hangul, and Euro/OE additions.
- Implements `keysym2ucs(KeySym)` with Latin-1 direct mapping, direct UCS keysyms in `0x01000000..0x01ffffff`, and binary search over the table.

Role in this group:
- Used by `gui-x11/x11.c` to translate non-ASCII/non-ISO-1 keysyms into Plan 9 rune values.

Notable risks:
- The file is generated and old; newer X11 keysyms or Unicode assignments may be absent.
- The table must remain sorted for binary search correctness.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-x11/keysym2ucs-x11.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-x11/keysym2ucs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-x11/keysym2ucs.h

Small declaration header for X11 keysym-to-UCS conversion.

Key contents:
- Includes `<X11/X.h>` for `KeySym`.
- Declares `long keysym2ucs(KeySym keysym)`.

Role in this group:
- Shared between `x11.c` and the generated conversion implementation.

Notable risks:
- No include guard; repeated inclusion is only safe because contents are simple declarations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-x11/keysym2ucs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-x11/x11.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-x11/x11.c

X11 screen, accelerated pixmap-backed memdraw, input, cursor, colormap, local-console detection, and selection/clipboard backend for drawterm.

Key responsibilities:
- Opens X displays for drawing, keyboard/mouse events, and selection handling.
- Chooses a visual and Plan 9 channel for 8/16/24/32-bit X displays, with colormap setup and byte-order heuristics.
- Creates the drawterm window, Glenda icon pixmap, WM properties, backing X pixmap, GCs, and the screen `Memimage`.
- Wraps `Memimage` allocation with optional X pixmap/XImage state for screen-compatible channels.
- Keeps X pixmap and in-memory image data synchronized through `getXdata()`, `putXdata()`, and dirty tracking.
- Accelerates simple memdraw cases with `XFillRectangle`, `XCopyArea`, and 1-bit stippled masks.
- Implements screen hooks: `screeninit`, `attachscreen`, `flushmemscreen`, `mouseset`, cursor setting, color access, and `atlocalconsole`.
- Runs an X event loop for keyboard, mouse, expose, mapping, selection, and window destroy events.
- Converts X keysyms to Plan 9 keyboard constants and runes, using `keysym2ucs()` for non-Latin keysyms.
- Converts X button/motion state into Plan 9 mouse queue events, including wheel buttons 8 and 16.
- Implements X selections for primary and clipboard copy/paste, answering common text targets.

Important behavior:
- `screeninit()` calls `_memmkcmap()`, initializes the X screen, starts the event kproc, initializes memdraw/terminal state, and flushes the whole screen.
- `xallocmemimage()` creates an X pixmap for `GREY1` and screen-channel images, while other channels remain plain memory images.
- `memimagedraw()` always does the software draw first, then optionally mirrors the operation to X; if no accelerated path matches, it uploads the destination rectangle.
- `atlocalconsole()` trusts `DRAWTERM_ATLOCALCONSOLE=1` or checks `DISPLAY` host against empty/local hostname.
- Clipboard read polls a temporary X property rather than waiting indefinitely for `SelectionNotify`.

Dependencies:
- Depends on Xlib, X atoms/WM properties, Plan 9 `memdraw`, draw locks, mouse/keyboard queues, and `keysym2ucs.h`.

Notable risks:
- Comments indicate some X acceleration paths were historically disabled or unreliable on certain platforms.
- Clipboard retrieval requests `XA_STRING`, with only partial UTF-8 handling despite advertising UTF-8 on selection responses.
- `atlocalconsole()` temporarily writes NUL into the `DISPLAY` environment string while parsing.
- Visual/channel byte-order detection is heuristic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-x11/x11.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/9windows.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/9windows.h

Windows host compatibility header for drawterm’s Plan 9 portability layer.

Key contents:
- Includes standard C, Win32-ish POSIX compatibility, process, time, assert, and varargs headers.
- Disables selected MSVC warnings.
- Defines `p9_vlong`, `p9_uvlong`, and `uintptr` for Windows builds.

Role in this group:
- Included by `u.h` when `WINDOWS` is defined to supply host types and headers before Plan 9 type remapping.

Notable risks:
- Uses MSVC-specific `__int64` and assumes the older Windows build environment expected by drawterm.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/9windows.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/auth.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/auth.h

Drawterm copy of Plan 9 libauth caller-facing interface.

Key contents:
- Defines `AuthRpc`, `AuthInfo`, `Chalstate`, CHAP/MSCHAP replies, `UserPasswd`, and auth RPC result codes.
- Defines attribute list parsing/matching structures and helper declarations.
- Declares namespace/login/authentication helper APIs, factotum proxy functions, challenge/response functions, user/password retrieval, WEP helper, and RPC lifecycle functions.

Role in this group:
- Provides authentication API contracts used by drawterm’s CPU/authentication paths while building outside Plan 9.

Notable risks:
- This is a header-only contract; security behavior depends on matching implementations elsewhere in drawterm.
- Includes legacy protocol surfaces such as CHAP/MSCHAP and WEP.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/auth.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/authsrv.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/authsrv.h

Drawterm copy of Plan 9 libauthsrv wire-format and authentication-server interface.

Key contents:
- Defines authentication protocol constants, legacy name/key lengths, DES key lengths, challenge sizes, and auth message type numbers.
- Defines wire structures for ticket requests, tickets, authenticators, password requests, old CHAP/MSCHAP replies, and NVRAM safe storage.
- Declares conversion routines between structs and wire buffers, DES password-key conversion helpers, NVRAM read helpers, auth server dialing, ticket exchange, and SSL negotiation helpers.

Role in this group:
- Supplies the old Plan 9 authentication protocol ABI used by drawterm authentication code.

Notable risks:
- The protocol definitions are DES-centered and include legacy compatibility formats.
- Fixed-width name fields such as `ANAMELEN` reflect old protocol constraints.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/authsrv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/cursor.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/cursor.h

Minimal Plan 9 cursor bitmap structure.

Key contents:
- Defines `struct Cursor` with hotspot offset plus 16x16 `clr` and `set` bitplanes.

Role in this group:
- Used by GUI backends to translate Plan 9 cursor state into platform-native cursors.

Notable risks:
- Fixed 16x16 cursor representation; host cursor systems with different native sizes need adaptation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/cursor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/draw.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/draw.h

Drawterm copy of Plan 9 libdraw’s public drawing API and data model.

Key contents:
- Defines drawing colors, refresh modes, line endings, Porter-Duff draw operations, image channel descriptors, common channel constants, `Point`, `Rectangle`, `Display`, `Image`, `Screen`, fonts, subfonts, glyph cache records, and RGB values.
- Declares image allocation/loading, display management, window/screen APIs, geometry helpers, colormap helpers, drawing primitives, string/font functions, subfont management, and compressed image helpers.
- Declares global draw state such as `display`, `font`, `_screen`, and debug flags.

Role in this group:
- Provides the central graphics contract consumed by GUI backends and drawterm terminal/display code.

Notable risks:
- This header intentionally mirrors Plan 9 APIs and relies on many implementations elsewhere.
- Several globals and compatibility macros make namespace collisions likely without the surrounding `u.h` remapping.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/draw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/dtos.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/dtos.h

Host-selection wrapper for drawterm OS compatibility headers.

Key contents:
- Includes `unix.h` for Unix-like systems and `9windows.h` for Windows.
- On Apple builds, aliases `panic` to `dt_panic`.
- Defines `main` as `mymain` on Windows.
- Errors out if no supported OS macro is defined.

Role in this group:
- Bridges drawterm’s Plan 9 compatibility layer to host OS headers.

Notable risks:
- Platform selection is preprocessor-macro dependent and reflects older OS naming conventions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/dtos.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/fcall.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/fcall.h

9P2000 message and stat wire-format interface.

Key contents:
- Defines `Fcall` for all 9P message variants, including version, auth, attach, walk, open/create, read/write, stat/wstat, flush, and error fields.
- Provides little-endian `GBIT*`/`PBIT*` access macros, fixed-size constants, Qid/stat size constants, `NOTAG`, `NOFID`, and `IOHDRSZ`.
- Enumerates 9P message type numbers from `Tversion` through `Rwstat`.
- Declares message/stat conversion routines, formatting helpers, and `read9pmsg()`.

Role in this group:
- Supplies the file protocol representation used by drawterm’s mount/device code and kernel facade.

Notable risks:
- The bit macros are statement-like macros without `do { } while(0)` wrapping, so callers must use them carefully.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/fcall.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/ip.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/ip.h

Plan 9 IP address helper declarations.

Key contents:
- Defines IPv6-sized address length, IPv4 length, and IPv4-in-IPv6 offset constants.
- Declares IP parsing, mask, formatting, host/network byte-order, IPv4/IPv6 conversion, and predefined address globals.
- Defines `ipcmp` and `ipmove` as 16-byte memory operations.

Role in this group:
- Shared by drawterm networking and device code needing Plan 9-format IP addresses.

Notable risks:
- Uses `vlong` return values for parse helpers in the Plan 9 style; callers need implementation-specific error interpretation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/ip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/keyboard.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/keyboard.h

Plan 9 keyboard control and private key constant header.

Key contents:
- Defines `Keyboardctl` with channel and console/ctl file state.
- Declares keyboard initialization/control/close functions.
- Defines Plan 9 private Unicode-space constants for function keys, navigation keys, insert/end, and modifier pseudo-keys.

Role in this group:
- GUI backends translate platform keyboard events into these runes before writing to `kbdq`.

Notable risks:
- `Kdown` and `Kview` share `Spec|0x00`, matching Plan 9 convention but easy to misread as a collision.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/keyboard.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/lib.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/lib.h

Core Plan 9 compatibility header for drawterm.

Key contents:
- Renames conflicting libc/system symbols, defines Plan 9 scalar aliases, `Rune`, `nil`, `nelem`, `USED`, UTF constants, and syscall constants.
- Defines `Lock`, `QLock`, `Qid`, `Dir`, `Waitmsg`, and Plan 9 mount/open/qid/mode constants.
- Declares rune/UTF routines, Plan 9-style formatting and print APIs, allocation helpers, string/path helpers, base encoders, floating-point helpers, locks, randomness, syscalls, network dial/listen APIs, kernel-process helpers, error-string APIs, and encryption wrappers.

Role in this group:
- This is the main portability ABI used by almost every file in the drawterm Unix tree.

Notable risks:
- Aggressive macros such as redefining `long`, `open`, `read`, `write`, `sleep`, and many libc names require strict include ordering.
- Type widths are fixed to drawterm expectations and may differ from host ABI defaults.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/lib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/libc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/libc.h

Minimal compatibility header.

Key contents:
- Includes `lib.h`.

Role in this group:
- Lets source files written for Plan 9 `<libc.h>` include the drawterm portability definitions.

Notable risks:
- No include guard; repeated inclusion relies on the idempotence of included declarations/macros.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/libc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/libsec.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/libsec.h

Drawterm copy of Plan 9 libsec cryptography and TLS interface declarations.

Key contents:
- Defines state structs and APIs for AES-CBC, Blowfish CBC/ECB, DES, 3DES, MD4, MD5, SHA1, HMAC-MD5, HMAC-SHA1, random generation, RC4, prime generation, RSA, ElGamal, DSA, X.509 parsing/generation/verification, PEM decoding, TLS client/server handshakes, thumbprints, and certificate reading.
- Integrates with `mpint` multiprecision integers from `mp.h`.

Role in this group:
- Supplies cryptographic APIs used by authentication, TLS, and secure channel code in drawterm.

Notable risks:
- Exposes legacy/insecure primitives including DES, RC4, MD4, and SHA1-era X.509 thumbprints.
- Header has no include guard beyond relying on `_MPINT` for forward declaration behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/libsec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/memdraw.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/memdraw.h

Drawterm copy of Plan 9 libmemdraw’s in-memory image API.

Key contents:
- Defines `Memdata`, `Memimage`, `Memcmap`, `Memsubfont`, draw flags, and `Memdrawparam`.
- Declares memory image allocation, load/unload, address calculation, clipping, fill, channel setup, pixel conversion, drawing primitives, string/subfont functions, colormap initialization, and predefined memory images.
- Includes an `X` pointer in `Memimage` used by the X11 backend for platform-specific pixmap state.

Role in this group:
- Core in-memory drawing substrate used by all GUI backends and drawterm screen rendering.

Notable risks:
- The `X` backend hook is a portability escape hatch and requires platform wrappers to keep memory and device state coherent.
- `Memdata` comments reference compaction/back-pointer behavior from Plan 9 that may not fully apply in drawterm.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/memdraw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/memlayer.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/memlayer.h

Plan 9 memory layer/window stacking API.

Key contents:
- Defines `Memscreen` and `Memlayer` for front/rear layer lists, screen rectangles, save areas, clear state, and refresh callbacks.
- Declares layer load/unload, allocation, deletion/free, front/back ordering, refresh setup, hide/expose, clear recomputation, origin movement, and no-refresh callback.

Role in this group:
- Supports Plan 9-style window/layer behavior on top of `Memimage`.

Notable risks:
- Functions distinguish local coordinates from screen coordinates; misuse can corrupt layer positioning.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/memlayer.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/mp.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/mp.h

Multiprecision integer interface used by libsec.

Key contents:
- Defines `mpint`, digit sizing constants, static flag, allocation/normalization/copy APIs, random/conversion APIs, arithmetic, modular arithmetic, comparisons, extended GCD, modular inverse, bit counting, vector digit helpers, magnitude helpers, and CRT residue/precompute structures.
- Declares well-known constants `mpzero`, `mpone`, and `mptwo`.

Role in this group:
- Supplies big-integer contracts for RSA, DSA, ElGamal, prime generation, and related cryptographic code.

Notable risks:
- Assumes `mpdigit` is an atomic type and at least an int, as provided by architecture-specific compatibility headers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/mp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/u.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/u.h

Top-level drawterm compatibility include.

Key contents:
- Selects `unix.h` or `9windows.h` through platform macros.
- Includes `lib.h`, `user.h`, and `dtos.h`.
- Undefines several syscall-like names to avoid exposing host/libc conflicts after setting up drawterm’s own namespace.

Role in this group:
- The first include in most drawterm source files, establishing host and Plan 9 compatibility definitions.

Notable risks:
- Include ordering is critical because this file deliberately manipulates many global macros.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/u.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/unix.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/unix.h

Unix host compatibility header.

Key contents:
- Defines feature-test macros for BSD/SVID/XOpen and large-file behavior.
- Includes standard Unix/POSIX C headers and optionally pthreads.
- Defines `p9_vlong`, `p9_uvlong`, and `uintptr`.

Role in this group:
- Supplies host definitions before Plan 9 type and syscall remapping on Unix-like drawterm builds.

Notable risks:
- Feature-test macros are old and broad; they can interact poorly with modern libc header expectations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/unix.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/user.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/user.h

User-space syscall and runtime API declarations for drawterm’s Plan 9 facade.

Key contents:
- Maps Plan 9 syscall names to `sys*` implementations and `sleep` to `osmsleep`.
- Declares file, directory, mount, pipe, read/write, stat, error string, network dial/listen, SSL, iounit, pread/pwrite, rendezvous, kproc, process, panic, sleep/yield, locking, time, and print functions.
- Declares `argv0` and local file-descriptor helper `lfdfd`.

Role in this group:
- Provides user-level call surface used by drawterm code while avoiding direct host libc usage.

Notable risks:
- Macro syscall remapping can make debugging symbol names non-obvious.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/user.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/Makefile

Build recipe for drawterm’s user-space kernel facade archive.

Key responsibilities:
- Includes `../Make.config`.
- Builds `libkern.a` from channel, device, process, namespace, queue, draw/input, networking, SSL/TLS, terminal, locking, and OS-specific objects.
- Selects audio and OS-specific device variants using `$(AUDIO)` and `$(OS)`.

Role in this group:
- Defines the kernel compatibility layer linked into drawterm.

Notable risks:
- Object selection is configuration-sensitive; missing `AUDIO` or `OS` variants can break the build.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/allocb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/allocb.c

Plan 9 `Block` allocator for packet/queue buffers in drawterm’s kernel facade.

Key responsibilities:
- Allocates aligned `Block` structures with header slack (`Hdrspc`) for protocol headers.
- Provides process-context `allocb()` and interrupt-time `iallocb()` allocation paths.
- Tracks interrupt allocation usage against `conf.ialloc`.
- Frees blocks, honors custom block free callbacks, updates interrupt allocation accounting, and poisons freed blocks with a sentinel.
- Provides `checkb()` sanity validation and `iallocsummary()` reporting.

Important behavior:
- `allocb()` panics if called without `up`.
- `iallocb()` returns nil when allocation exceeds the configured interrupt allocation budget.
- Data pointers are aligned to `BLOCKALIGN`.

Notable risks:
- Allocation failure generally panics in process context.
- Poisoning uses a fixed invalid pointer value; diagnostics are helpful but not memory-safe if stale users dereference before checks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/allocb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/cache.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/cache.c

No-op cache shim for drawterm’s kernel facade.

Key responsibilities:
- Defines empty `cinit`, `copen`, `cupdate`, and `cwrite`.
- Defines `cread()` returning zero.

Role in this group:
- Satisfies kernel cache API references without implementing a local cache.

Notable risks:
- Any caller expecting real cache persistence or read-back behavior receives no data.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/chan.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/chan.c

Drawterm’s Plan 9 channel, pathname, mount, and namespace resolver implementation.

Key responsibilities:
- Manages `Chan` and `Cname` allocation, reference counts, clone/close/free, copy-on-write uniqueness, and debug helpers.
- Initializes/resets/shuts down all devices through `devtab`.
- Implements mount and unmount mechanics with `Mhead` and `Mount` chains, including replacement and union mount ordering.
- Resolves paths with `walk()`, handling mount traversal, union fallback, dot-dot across mounts, and partial walk errors.
- Implements `namec()` for Plan 9 access modes: access, bind, to-directory, open, mount, create, and remove.
- Handles create races by retrying as open-with-truncation when non-exclusive create fails after another creator wins.
- Parses and cleans path names, validates invalid characters/control bytes, and enforces noattach sandbox exceptions.
- Provides helpers such as `cunique`, `eqchan`, `findmount`, `domount`, `undomount`, `createdir`, `putmhead`, `validname`, and `isdir`.

Important behavior:
- Device names beginning with `#` bypass normal mounts and attach directly to `devtab` entries.
- `namec(Aopen)` and `namec(Acreate)` ensure callers get a unique channel suitable for mutation by device open/create/remove.
- Union mounts are searched when a walk fails in the first mounted element.
- Cnames are updated alongside successful walks to preserve printable path state.

Dependencies:
- Heavily depends on `dat.h` structures, device method tables, process-global `up`, mount locks, `fcall` stat conversion, and Plan 9 error unwinding.

Notable risks:
- Code is subtle and retains diagnostic prints for unexpected `umh` states.
- Some comments call out unresolved race semantics and historical complexity around union/create behavior.
- `putmhead()` poisons the mount pointer with `0xCafeBeef` on final release for diagnostics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/chan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/dat.h

Core data-structure header for drawterm’s user-space Plan 9 kernel facade.

Key contents:
- Defines constants and forward declarations for blocks, channels, devices, namespace groups, process groups, queues, rendezvous, mounts, logs, commands, and process state.
- Defines `Conf`, `Label`, `Ref`, `Rendez`, `RWlock`, `Block`, `Chan`, `Cname`, `Dev`, `Dirtab`, `Walkqid`, `Mount`, `Mhead`, `Mnt`, `Note`, `Pgrp`, `Rgrp`, `Egrp`, `Fgrp`, `Proc`, `Log`, `Cmdbuf`, and `Cmdtab`.
- Defines channel access modes, channel flags, block flags, mount/rendezvous hash sizing, fd sizing, process states, queue flags, and shared extern globals.
- Redefines `up` as `_getproc()` to support thread-local/current-process lookup.

Role in this group:
- The central ABI between drawterm’s kernel-like code, device implementations, namespace resolver, and GUI/input devices.

Notable risks:
- Many structures are reduced/adapted from the real Plan 9 kernel; code using them depends on drawterm-specific simplifications.
- `up` as a macro hides function calls and can surprise code expecting a global variable.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/data.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/data.c

Global kernel-facade data definitions for drawterm.

Key contents:
- Defines `Proc *up`.
- Initializes `conf` with one machine, 100 processes, large default page/memory/cache-like limits, and zero UARTs.
- Defines default user `eve`, `kerndate`, `cpuserver`, and `hostdomain`.

Role in this group:
- Supplies global state referenced throughout the drawterm kernel and device layer.

Notable risks:
- `up` is also macro-defined through `_getproc()` in `dat.h`; this definition is legacy/global state and must match surrounding build expectations.
- Large fixed defaults are coarse and not tied to actual host resources.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/data.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/dev.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/dev.c

Common Plan 9 device helper implementation for drawterm.

Key responsibilities:
- Provides Qid creation, device lookup by device character, directory entry construction, and generic directory generation.
- Implements generic attach, clone, walk, stat, directory read, permission check, open, create-denied, block read/write wrappers, remove-denied, wstat-denied, power-denied, and config-denied helpers.
- Documents expectations and contradictions around `Devgen` behavior for children versus siblings.

Important behavior:
- `devwalk()` clones channels, processes `.`/`..`, and handles partial walk results like Plan 9.
- `devstat()` synthesizes directory stat data if a directory generator cannot find the current directory by sibling enumeration.
- `devopen()` checks permission then marks the channel open and sets mode.
- `devbread()` and `devbwrite()` adapt byte-buffer device methods to `Block`-oriented callers.

Dependencies:
- Depends on `devtab`, `Chan`, `Dirtab`, `Dir`, 9P stat conversion, process user state, and Plan 9 error handling.

Notable risks:
- Generic helpers assume device generators honor enough of the documented contract; broken `Devgen` implementations can break walk/stat/read behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/dev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devaudio-none.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devaudio-none.c

No-audio backend for drawterm.

Key responsibilities:
- Implements all audio device hooks by raising `"no audio support"`.
- Covers open, close, read, write, set volume, and get volume.

Role in this group:
- Selected for platforms/builds without an audio implementation.

Notable risks:
- `audiodevclose()` also errors, which can make cleanup paths observe an error even when audio was never opened.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devaudio-none.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devaudio-sun.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devaudio-sun.c

Solaris/Sun `/dev/audio` backend for drawterm audio output and volume control.

Key responsibilities:
- Locates audio device from `AUDIODEV` or defaults to `/dev/audio`, deriving the control device by appending `ctl`.
- Opens playback and control file descriptors and configures 44.1 kHz, 16-bit, stereo, linear PCM playback.
- Detects host byte order and swaps Plan 9 little-endian samples on big-endian systems.
- Implements playback write loop, close, speed setting/getting, audio volume/balance setting/getting, and default treble/bass reporting.
- Converts between Plan 9 left/right percentages and Sun gain/balance values.

Important behavior:
- Only opens playback write-only; `audiodevread()` always errors `"no reading"`.
- `Vspeed` changes sample rate and stores the speed for later open/config calls.
- Volume updates preserve the side not explicitly set when passed a negative left or right value.

Dependencies:
- Depends on Solaris `<sys/audio.h>` and `AUDIO_SETINFO`/`AUDIO_GETINFO` ioctls.

Notable risks:
- Control device name is built by appending `ctl` to the audio path, matching Solaris conventions but not portable.
- Write errors call `oserror()` inside the loop; partial-write recovery is minimal.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devaudio-sun.c -->