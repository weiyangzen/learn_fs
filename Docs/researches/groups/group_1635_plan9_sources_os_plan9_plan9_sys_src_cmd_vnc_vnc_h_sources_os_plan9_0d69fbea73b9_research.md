# Group Research: group_1635_plan9_sources_os_plan9_plan9_sys_src_cmd_vnc_vnc_h_sources_os_plan9_0d69fbea73b9

Scope confirmed against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/vnc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/vnc.h

This shared VNC header defines the protocol-facing data model used by both the VNC viewer and server. It includes Plan 9 base, bio, draw, and memdraw headers and declares `Pixfmt`, `Colorfmt`, and `Vnc`.

Key definitions:
- `Colorfmt` stores channel maximum and shift.
- `Pixfmt` stores bpp, depth, endian/truecolor flags, and red/green/blue channel formats.
- `Vnc` embeds a `QLock`, network control/data fds, buffered input/output, framebuffer dimensions, pixel format, and client-side desktop name.
- `Color` is an `ulong` used as a byte container in little-endian order.

The enum block maps RFB/VNC wire constants:
- Authentication negotiation: `AFailed`, `ANoAuth`, `AVncAuth`.
- VNC auth results and challenge length.
- Server-to-client messages such as `MFrameUpdate`, `MSetCmap`, `MBell`, `MSCut`.
- Client-to-server messages such as `MPixFmt`, `MSetEnc`, `MFrameReq`, `MKey`, `MMouse`, `MCCut`.
- Encodings: raw, copyrect, RRE, CoRRE, hextile, zlib/tight variants, and mouse warp.
- Hextile tile flags.

It declares the protocol/auth I/O API implemented elsewhere:
- Handshake/auth: `vncauth`, `vnchandshake`, `vncsrvauth`, `vncsrvhandshake`.
- Readers/writers for VNC wire primitives, strings, rectangles, points, and pixel formats.
- Buffered output lifecycle: `vncflush`, `vncterm`, `vncinit`.
- Lock helpers for serialized writes: `vnclock`, `vncunlock`.
- `vnchungup` is deliberately implemented by clients of the I/O library, so server/viewer define their own failure policy.

Notable dependency role:
- This file is the protocol contract for `vncs.c`, `vncv.c`, `wsys.c`, and likely the omitted `auth.c`, `proto.c`, `draw.c`, `color.c`, `rre.c`, and `rlist.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/vnc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/vncs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/vncs.c

This is the Plan 9 VNC server. It starts a private Plan 9 draw/mouse/console environment, runs a command inside it, announces a VNC service, accepts clients, and exports the screen with dirty-rectangle updates.

Startup flow:
- Parses options for TLS cert, display number, geometry, pixel channel, kill mode, verbosity, and alternate network mount.
- `-k :display` locates the server's TCP control file and writes `hangup`.
- Daemonizes with `rfork`, allocates per-process private data with `privalloc`, initializes the compatibility/screen layer, exports draw/mouse/cons devices, rebuilds `/dev`, and starts the target command, defaulting to interactive `/bin/rc`.
- Announces TCP on `baseport + display`; default base is `5900`, TLS mode uses `35729`.
- Accept loop creates a `Vncs`, links it into the global `clients` list under `clients.QLock`, fills remote/netpath metadata, and calls `vncaccept`.

Client lifecycle:
- `vncaccept` forks per connection and optionally wraps the data fd in TLS with `tlsServer`.
- Performs VNC server handshake/auth via `vncsrvhandshake` and `vncsrvauth`.
- Reads the shared flag; if not shared, `killclients` hangs up existing clients.
- Sends server init: dimensions, pixel format converted from `gscreen->chan`, and desktop name `Plan9 Desktop`.
- Forks reader and writer loops sharing memory.
- Per-process `atexit(exiting)` drives `vncclose`, which removes the client from the global list and frees resources only after both client procs have exited.

Client read path:
- `clientreadproc` consumes client-to-server messages.
- `MPixFmt` installs client pixel format once and derives a Plan 9 image channel via `fmt2chan`.
- `MSetEnc` records the first supported encoding callback pair from raw/RRE/CoRRE/hextile and optional copyrect/mousewarp support.
- `MFrameReq` marks update demand and adds full requested rectangles for non-incremental requests.
- `MKey` forwards keyboard events to `vncputc`.
- `MMouse` forwards mouse state to `mousetrack`.
- `MCCut` receives client clipboard text and updates Plan 9 snarf state.

Client write path:
- `clientwriteproc` allocates/reallocates a per-client `Memimage` in the requested channel, sends snarf updates, and calls `updateimage` when an update has been requested.
- `updateimage` snapshots dirty rectangles from `v->rlist`, handles cursor redraw damage, copies changed screen pixels from `gscreen` into the client image, counts encoded rectangles, sends `MFrameUpdate`, and optionally emits a mouse-warp pseudo-rectangle.
- It carefully drops the client lock and draw lock during expensive or blocking phases.

Global update integration:
- `flushmemscreen(Rectangle)` clips screen damage to `gscreen->r` and appends it to every client's rectangle list.
- `mousewarpnote(Point)` marks `needwarp` for clients that advertised `EncMouseWarp`.

Pixel format conversion:
- `fmt2chan` converts VNC RGB masks/shifts to a Plan 9 channel descriptor, adding one ignore channel if bpp exceeds RGB depth.
- `chan2fmt` converts a Plan 9 channel descriptor into VNC max/shift fields.

Shutdown behavior:
- `killall` posts a hangup to the command process group, closes service/export fds, and posts `die vnc kin` to its own process group.
- `shutdown` is registered with `atexit`; `noteshutdown` handles external notes.

Notable risks and quirks:
- Several comments state pixel format and encoding changes are effectively one-shot because supporting later changes would need more locking and image lifetime management.
- `fmt2chan` assumes at most one contiguous run of ignored bits.
- TLS mode reads a certificate and wraps the connection but this file does not perform client authentication.
- Shared global `shared` is overwritten per connecting client, so it is not a per-client setting despite client-specific semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/vncs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/vncs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/vncs.h

This server-side VNC header defines `Rlist` and `Vncs`, extending the common `Vnc` state with server-specific per-client state.

Key structures:
- `Rlist` tracks dirty rectangles using a bounding box, allocation size, count, and rectangle array.
- `Vncs` embeds `Vnc`, then adds linked-list membership, remote/netpath strings, encoding callbacks, encoding feature flags, mouse-warp state, update request state, rectangle list, process-exit accounting, cursor/snarf versions, and a per-client translated `Memimage`.

Important fields:
- `countrect` and `sendrect` select the active framebuffer encoding implementation.
- `copyrect`, `canwarp`, `needwarp`, and `warppt` track optional client capabilities.
- `updaterequest` controls whether writer loop should emit a frame update.
- `ndead` and `nproc` ensure shared client resources are freed only after all per-client processes exit.
- `imagechan` records the Plan 9 channel corresponding to the client-requested VNC pixel format.

Declared external implementations:
- Encoding count/send functions for raw, RRE, CoRRE, and hextile.
- Rectangle-list helpers `addtorlist` and `freerlist`.

Role:
- This header is the private contract between `vncs.c`, rectangle-list management, and rectangle encoders.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/vncs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/vncv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/vncv.c

This is the Plan 9 VNC viewer entry point. It dials a VNC server, negotiates auth/session setup, opens a draw window, and starts concurrent server-read, snarf, keyboard, and mouse loops.

Command-line behavior:
- `-c` requests 12-bit pixel conversion mode via `bpp12`.
- `-e` overrides preferred encoding list, defaulting to `copyrect hextile corre rre raw mousewarp`.
- `-s` requests a shared VNC session.
- `-t` enables TLS and changes the default port base from 5900 to 35729.
- `-v` enables verbose logging.
- `-k` supplies an auth key pattern.

Network/session flow:
- `netmkvncaddr` parses `host[:n]`, applies display number to the base port, and returns a Plan 9 network address.
- Dials via `dial`; TLS mode wraps the fd with `tlsClient`.
- Initializes the common VNC state with `vncinit`.
- Performs client handshake/auth with `vnchandshake` and `vncauth`.
- `vncstart` sends the shared flag, then reads server dimensions, pixel format, and desktop name.

UI/process flow:
- Calls `initdraw`, enables display locking, computes desired window size including border, chooses color translation, sends encoding preferences, and opens mouse device.
- Registers `shutdown` with `atexit`; shutdown hangs up network fds and posts `die vnc kin` to sibling procs.
- Forks:
  - Server reader: `readfromserver(vnc)`.
  - Snarf watcher: `checksnarf(vnc)`.
  - Keyboard reader if `/dev/snarf` exists: `readkbd(vnc)`.
- Main process runs `readmouse(vnc)`.

Important globals:
- `encodings`, `bpp12`, `shared`, `verbose`, `vnc`, `mousefd`, and `tls` are shared with viewer helper files.

Notable risks:
- TLS client path has an explicit `XXX check thumbprint`; server certificate validation is not implemented here.
- `pids[3]` is assigned after the conditional keyboard fork; if `/dev/snarf` is absent, `p` may retain an old value from the prior fork path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/vncv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/vncv.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/vncv.h

This viewer-side header declares cross-file VNC viewer helpers.

Color/display declarations:
- `choosecolor`, `settranslation`, and `cvtpixels` choose/perform framebuffer pixel conversion.
- `zero[]` is an external byte buffer used by drawing code.

Server protocol/draw declarations:
- `sendencodings` sends the viewer's preferred encoding list.
- `requestupdate` asks the server for framebuffer changes.
- `readfromserver` consumes server messages and paints the local draw window.

Viewer globals:
- `encodings`, `bpp12`, `vnc`, and `mousefd` are defined by `vncv.c`.

Window-system/input declarations:
- `readkbd`, `initmouse`, `mousewarp`, `readmouse`, `senddim`, `writesnarf`, and `checksnarf`.

Role:
- This is the shared contract among `vncv.c`, `wsys.c`, and omitted viewer draw/color modules.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/vncv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/wsys.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/wsys.c

This file handles the Plan 9 window-system integration for the VNC viewer: resizing, cursor setup, mouse event forwarding, mouse warp, and snarf synchronization.

Window resize:
- `resize(Vnc*, int first)` calls `getwindow`, computes the server image size plus borders, and writes `/dev/wctl` resize commands when first opened or when the window is larger than the VNC desktop.
- `eresized` resizes and requests a full framebuffer update.

Mouse handling:
- Defines a small dot cursor and writes it to the draw device cursor file.
- `initmouse` opens the display device's mouse file as `ORDWR`.
- `readmouse` reads fixed-size Plan 9 mouse events, handles resize messages, subtracts `screen->r.min` to produce VNC-relative coordinates, clips to the VNC desktop, and sends `MMouse` messages.
- Mouse wheel buttons are sent as press followed by synthetic release for non-button-1/2/3 bits.
- `mousewarp` writes an `mX Y` command to the mouse fd after converting VNC-relative coordinates to screen coordinates.

Clipboard/snarf:
- `writesnarf` receives VNC clipboard bytes from the network and writes them to `/dev/snarf`, incrementing local `snarfvers`.
- `getsnarf` reads the entire local snarf file into a dynamically grown buffer.
- `checksnarf` polls `/dev/snarf` once per second, compares `qid.vers`, and sends `MCCut` to the server when local snarf changes.

Notable risks:
- `getsnarf` reallocates without checking for failure.
- Snarf polling is coarse and relies on qid version changes.
- Clipboard reads can grow unbounded except by available memory.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/wsys.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vt/cons.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vt/cons.h

This header is the shared interface for the Plan 9 terminal emulator.

Console control:
- Defines `Consstate` with `raw` and `hold`.
- Declares `consctl()` and global `cs`, used to emulate `/dev/consctl` state.

Screen constants:
- Margins/insets, buffer sizes, history size, and state constants for canonical input and scrolling.

Text attributes:
- Bit flags for high intensity, underline, blink, reverse, and invisible text.

Input helpers:
- `button2()` and `button3()` macros interpret Plan 9 mouse button state.
- `ttystate` maps raw/cooked modes to CR/NL translation settings.

Function key model:
- `struct funckey` maps names to escape sequences.
- Declares key tables for VT100, VT220, ANSI, and xterm.

Shared emulator state:
- Cursor coordinates and limits, scrollback, attributes, terminal name, scroll region, colors, cursor state, and no-color flag.

Shared functions:
- Terminal core: `emulate`, `host_avail`, `get_next_char`.
- Drawing/layout: `clear`, `newline`, `scroll`, `backup`, `pt`, `drawstring`, `curson`, `cursoff`, `setdim`.
- Host I/O: `sendnchars`, `sendnchars2`, `funckey`.
- Parsing utilities: `number`.

Role:
- This file ties together `main.c`, `vt.c`, `hp.c`, `event.c`, and `consctl.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vt/cons.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vt/consctl.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vt/consctl.c

This file simulates Plan 9 console control files for the terminal emulator.

Core behavior:
- `consctl` attaches a small shared segment named `shared` to hold a `Consstate`.
- Binds pipes over `/dev/consctl` and `/dev/cons` using `/mnt/cons/consctl` and `/mnt/cons/cons`.
- Forks a child that watches `/mnt/cons/consctl/data` for control messages.

Recognized control tokens:
- `rawon` / `rawoff` toggle `x->raw`.
- `holdon` / `holdoff` toggle `x->hold`.

Lifecycle:
- Parent returns the shared `Consstate*`.
- Child loops up to 100 failed/open cycles, resetting state when reopening the control pipe.
- `notify(0)` disables note handling in the watcher child.

Role:
- Allows the shell or hosted program running under the terminal to control raw/cooked behavior through Plan 9-style `/dev/consctl`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vt/consctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vt/event.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vt/event.c

This file starts the hosted shell process and integrates it with Plan 9's event library.

Key functions:
- `edie` closes `outfd` and posts `exit` to the current process group once.
- `start_host` initializes console control via `consctl`, forks a hosted `/bin/rc` process in a new namespace/fd/note group, wires its stdio to `/dev/cons`, and returns the writable host side `/mnt/cons/cons/data`.
- `ebegin` registers `edie`, initializes mouse/keyboard events, starts the host, and registers the host fd as an event source using `estart`.
- `send_interrupt` posts an `interrupt` note to the hosted shell process group.

Role:
- Bridges the GUI terminal event loop with a child shell's console I/O.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vt/event.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vt/event.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vt/event.h

This small header defines event constants and a compact event payload structure.

Definitions:
- `BSIZE` is 4000.
- Event indices: `MOUSE`, `KBD`, `HOST`.
- Block flags: `HOST_BLOCKED`, `KBD_BLOCKED`.
- `IOEvent` contains a short key, short size, and `data[BSIZE]`.

Role:
- It appears to describe an older or alternate event representation. The main VT files use Plan 9 `<event.h>` directly rather than this `IOEvent` in the read code shown.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vt/event.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vt/hp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vt/hp.c

This file implements an HP 2621-style terminal emulation, with `term = "2621"` and a local `fk[32]`.

Emulation behavior:
- Main loop reads characters through `get_next_char`.
- Handles null, bell, tab, backspace, newline, carriage return, and printable text.
- Escape handling supports HP-style cursor positioning, underline/standout toggles, home, insert/delete line, clear-to-end, delete char, insert mode, rolling scroll, and directional cursor movement.
- Printable text is batched in cooked mode when contiguous printable host data is available.
- Insert mode shifts existing line content to the right before drawing.
- Standout mode inverts the drawn rectangle.

Drawing dependencies:
- Uses old `ndraw` functions such as `xtipple`, `bitblt`, `string`, and `rectf`.

State:
- Tracks local `standout` and `insmode`.
- Uses shared cursor position, scroll, raw-mode translations, and screen geometry from `cons.h`.

Role:
- Alternate terminal emulator implementation sharing the same `main.c` substrate as the VT100 parser.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vt/hp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vt/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vt/main.c

This file provides the generic window, input, history, menus, drawing, and host I/O substrate for the terminal emulator. It calls `emulate()`, which is implemented by either `vt.c` or `hp.c`.

Initialization:
- Parses terminal mode options:
  - `-2` VT220 key table.
  - `-a` ANSI key table.
  - `-b` black background.
  - `-c` disables color.
  - `-f` font.
  - `-l` log file.
  - `-x` xterm key table.
- Allocates host input buffer, initializes draw window, starts host event source via `ebegin`, initializes menus, colors, font metrics, and default colors.
- Exports `XPIXELS`, `YPIXELS`, `LINES`, `COLS`, and `TERM`.

Screen behavior:
- `newline` scrolls within `yscrmin..yscrmax` and supports page mode blocking.
- `scroll` copies screen rectangles and clears the vacated line.
- `bigscroll` scrolls up about one third of the screen for local scrollback behavior.
- `resize` recomputes character grid and clears screen.
- `setdim` requests a `/dev/wctl` resize for fixed rows/cols.

Input behavior:
- `waitchar` multiplexes resize, mouse menus, snarf playback, host data, keyboard events, and cursor display.
- In raw mode, keyboard special keys are mapped through current `funckey` table; newline and carriage return are translated.
- In cooked mode, `canon` implements backspace, line kill, word kill, interrupt, quit/newline, EOT, and local echo buffering.
- `sendnchars2` writes to the hosted shell fd.

Menus:
- Button 3 menu toggles 24x80, CR/NL translations, raw/cooked mode, and exit.
- Button 2 menu handles backup, forward, reset, clear, send snarf buffer, and page/scroll mode.

History:
- `hist[HISTSIZ]` stores received chars in a circular buffer.
- `backup` locates older content by line count and replays through `backp`.

Drawing:
- `curson` saves current cell background and draws a red/border cursor.
- `cursoff` restores cursor background.
- `drawstring` applies reverse and high-intensity color behavior and paints text.

Notable risks:
- `sendnchars` writes `p[n+1] = 0`, which assumes writable space beyond the transmitted buffer and can be unsafe for arbitrary caller buffers.
- Fixed-size buffers for echo/send impose practical typeahead limits.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vt/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vt/vt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vt/vt.c

This file implements the VT100/ANSI/xterm-ish terminal parser and renderer.

Supported key tables:
- `vt100fk`, `ansifk`, `vt220fk`, and `xtermfk` map named keys and function keys to escape sequences.
- `vt220` mode is documented as mostly VT100 with different cursor key defaults.

Character-set handling:
- `gmap` maps DEC graphics characters to ASCII approximations.
- SO/SI switch between G1/G0 graphics state using `g0set`, `g1set`, and `isgraphics`.

Main parser:
- Handles control characters: bell, backspace, tab, linefeed/formfeed/vertical tab, carriage return, SO/SI, ignored controls, delete.
- Handles ESC commands: save/restore cursor, reset, index/next-line/reverse-index, tab set, identification, ANSI/keypad toggles, character set selection, OSC title setting, and many ignored VT features.
- CSI parsing accepts numeric operands separated by `;` or `?`.

CSI capabilities:
- Identification/status/cursor position reports.
- Tab clearing.
- Mode set/reset: linefeed mode, 80/132 columns, origin relative/absolute, wraparound, cursor visibility.
- Character attributes via `setattr`.
- Scroll region.
- Cursor movement up/down/right/left, absolute column/row, and home.
- Display/line erase.
- Delete/insert/erase chars.
- Insert/delete lines.
- Scroll up/down.

Rendering:
- Printable text is optionally mapped through graphics table, line-wrapped, batched, and drawn via `drawstring`.
- `setattr` maps SGR attributes and 8-color foreground/background values to shared image pointers.

Documented limitations:
- Does not handle cursor movement characters inside escape sequences.
- Tab stops beyond fixed table size are limited.
- Whole-screen reverse video ignored.
- ESC `#` double-width/double-height/confidence tests ignored.
- Cursor key sequences not affected by keypad application mode.
- VT52 and some rare features omitted.

Notable quirks:
- Debug `print` calls remain for reset and unknown escape cases, which can write into terminal output stream.
- Several DEC private mode branches are parsed by operand count rather than explicit `?` state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vt/vt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/wc.c

This is a Plan 9 `wc` implementation with rune awareness.

Options:
- `-l` lines.
- `-w` words.
- `-r` runes.
- `-b` bad runes.
- `-c` bytes/chars by file offset.
- Defaults to line, word, and byte counts when no flags are given.

Counting behavior:
- Uses `Bgetrune`, so UTF text is counted as runes.
- `Runeerror` increments bad-rune count and is excluded from line/word classification.
- Word state toggles between `Space` and `Word` using `isspacerune`.
- Byte count is taken from `Boffset`.

Output:
- `report` builds a single aligned line containing requested counts and optional filename.
- Totals are accumulated and printed when multiple files are processed.

Error handling:
- Failed file opens call `perror`, set final status to `"can't open"`, and continue.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webcookies.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/webcookies.c

This standalone cookie filesystem lets clients such as `hget` and multiple `webfs` instances collaborate through a shared persistent cookie jar. It mounts conventionally at `/mnt/webcookies`.

Filesystem surface:
- `http`: clients write a URL first, read generated outgoing `Cookie:` headers, then write response headers so `Set-Cookie` values can be stored.
- `cookies`: editable textual view of the full cookie jar.

Cookie model:
- `Cookie` stores name/value, domain, path, version, comment, expiration, secure flag, explicit-domain/path flags, Netscape-style marker, and internal deleted/mark/ondisk flags.
- `Jar` stores dynamic cookie array, file qid/dirty state, jar file path, and lock file path.

Formatting:
- `%J` emits HTTP `Cookie:` header format.
- `%K` emits the editable/persistent cookie line format with quoted string fields and integer flags.

Jar management:
- `addcookie` replaces cookies with matching name/domain/path unless exact match already exists.
- `purgejar` compacts deleted cookies.
- `syncjar` locks with `L.<filename>`, merges disk state, removes marked entries, writes non-session cookies back, and updates qid.
- `readjar` derives lockfile name and loads the jar.
- `closejar` expires cookies and syncs.

Matching and validation:
- `isdomainmatch` implements RFC2109-style host/domain matching.
- `iscookiematch` checks domain, path prefix, and expiration.
- `cookiesearch` builds a sorted subjar for outgoing cookies, respecting `secure`.
- `isbadcookie` rejects invalid Set-Cookie domains/paths.

HTTP Set-Cookie parsing:
- Handles RFC-style and old Netscape-style cookies.
- Netscape detection looks for no spaces around `=`, no quotes, no Version attribute.
- `strtotime` parses GMT expiration date variants.
- `parsehttp` scans response headers for `Set-Cookie:` and calls `parsecookie`.
- `parsecookie` parses NAME=VALUE plus domain/path/comment/version/expires/max-age/secure attributes; missing domain/path default to the request host/path-derived directory.

9P request handling:
- `fsopen` creates per-fid `Aux` state for `http` or `cookies`.
- `fswrite` on `http` either captures URL/domain/path and computes outgoing cookies or appends response headers.
- `fsread` on `http` returns outgoing header text after URL has been written.
- `fsdestroyfid` parses accumulated response headers or applies edited cookie text, then syncs jar.
- `main` installs formatters, creates default `$home/lib/webcookies` if needed, builds a static tree with `http` and `cookies`, and posts the server.

Notable risks and differences from `webfs/cookies.c`:
- This version's `isdomainmatch` is stricter than `webfs/cookies.c`; it does not accept a bare `google.com` for `.google.com`.
- Cookie/header buffers for `http` are fixed at 4096 bytes.
- Secure/certificate concerns are outside this file; it trusts callers to identify `https://` correctly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webcookies.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/buf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/buf.c

This file implements simple buffered input for webfs network connections.

Functions:
- `initibuf` initializes fd, `Ioproc`, and buffer read/write pointers.
- `readibuf` first drains buffered bytes, otherwise uses `ioreadn`.
- `unreadline` pushes a line plus newline back in front of unread buffered bytes.
- `readline` reads until newline or EOF, using half the internal buffer at a time, and trims trailing spaces, tabs, carriage returns, and newlines.

Role:
- Used by HTTP response parsing to read status lines and MIME headers while supporting one-line pushback for header continuations.

Notable constraints:
- `unreadline` assumes the internal buffer has enough front space for the pushed line plus unread bytes.
- `readline` truncates lines longer than caller buffer while continuing to consume through newline.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/buf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/client.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/client.c

This file manages `webfs` client slots, per-client worker threads, control-file parsing, redirects, authentication retries, and plumbed URL handling.

Client lifecycle:
- `newclient` reuses a zero-ref slot or allocates a new `Client`, request channel, worker thread, I/O proc, copied global controls, and client number.
- `closeclient` decrements `ref`; when it reaches zero, it closes open body transport, frees content type, post body, URL, redirect/auth strings, and resets body state.
- `clonectl` deep-copies string fields in `Ctl`.

Body open/read:
- `clientbodyopen` follows redirects up to `redirectlimit`, calls the URL scheme's `open`, retries once for authentication, parses redirected URLs relative to current URL, and responds to pending open request.
- `clientbodyread` delegates to URL scheme `read` and responds.
- `clientthread` receives 9P requests over `creq`; for plumbed clients it opens immediately and replumbs a generated body path.

Plumbing:
- `plumburl` parses optional base URL and target URL, creates a plumbed client, holds a reference, and nudges its worker.

Control commands:
- Tables define global and per-client controls:
  - `acceptcookies`, `sendcookies`, `redirectlimit`, `useragent`.
  - Global debug knobs: `chatty9p`, `fsdebug`, `cookiedebug`, `urldebug`, `httpdebug`.
  - Client URL setters: `baseurl`, `url`.
- `parseas` applies bool, string, URL, and integer values.
- `ctlwrite`, `clientctlwrite`, and `globalctlwrite` dispatch commands.
- `ctlread` and `globalctlread` render current settings.

Notable risks:
- URL control writes replace existing `Url*` immediately after parsing, but no explicit synchronization with active body I/O beyond normal 9P sequencing.
- Authentication retry only permits one retry via `nauth++ < 1`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/client.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/cookies.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/cookies.c

This is the cookie engine embedded in `webfs`. It shares much of the standalone `webcookies.c` design but is wired directly into the webfs 9P `cookies` file and HTTP client.

Cookie/jar model:
- `Cookie` stores RFC-facing fields and internal deleted/mark/ondisk flags.
- `Jar` stores dynamic cookie array, qid, dirty bit, file, and lockfile.
- `%J` formats outgoing HTTP `Cookie:` headers.
- `%K` formats persistent/editable cookie lines.

Jar persistence:
- `readjar` constructs `L.<name>` lockfile path and calls `syncjar`.
- `syncjar` detects external file changes by qid, locks, merges disk cookies, deletes stale marked cookies, purges deleted slots, rewrites persistent non-session cookies, and updates qid.
- `closejar` expires and syncs on shutdown.

Cookie parsing/matching:
- Supports RFC2109-style and old Netscape-style Set-Cookie headers.
- `strtotime` parses GMT expiry formats.
- `parsehttp` scans raw response headers for `Set-Cookie:`.
- `parsecookie` parses cookie attributes, derives default domain/path, honors `expires`, `max-age`, and `secure`.
- `isbadcookie` implements path/domain security checks.
- `cookiesearch` returns sorted matching cookies for a request and honors `secure`.

9P integration:
- `cookieopen` syncs jar and creates an editable snapshot in fid aux state.
- `cookieread` returns that snapshot.
- `cookiewrite` edits the snapshot with a 16 MB cap.
- `cookieclunk` replaces jar contents according to edited text using mark/delete logic and syncs.
- `httpsetcookie` parses and stores response cookies.
- `httpcookies` syncs, searches, formats `%J`, closes the temporary subjar, and returns a heap string.

Notable behavior:
- `iscookiematch` treats `expire == 0` as non-expiring/matching, in addition to future expirations.
- `isdomainmatch` includes a compatibility case accepting `google.com` against `.google.com`, unlike the standalone `webcookies.c`.
- `httpcookies` calls `snprint("%J", j)` even when `cookiesearch` returns nil; `%J` emits an empty string for nil.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/cookies.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/dat.h

This header defines the core `webfs` data model.

Structures:
- `Ibuf`: buffered fd reader paired with an `Ioproc`.
- `Ctl`: per-client/global controls for accepting cookies, sending cookies, redirect limit, and user-agent.
- `Client`: active web request/session state, including URL/base URL, controls, request channel, content type, post body, redirect/auth state, extension for plumbed body path, I/O busy flag, body-open flag, I/O proc, refcount, and scheme auxiliary state.
- `Url`: parsed URL with scheme type, original URL, scheme/open/read/close callbacks, authority/user/pass/host/port/path/query/fragment, and scheme-specific HTTP/FTP fields.

URL scheme enum:
- `USunknown`, `UShttp`, `UShttps`, `USftp`, `USfile`, `UScurrent`.

Global declarations:
- Client table and counts.
- Debug flags.
- Global controls.
- 9P server `fs`.
- `status[]`.

Role:
- Shared internal ABI for all `webfs` implementation files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/fns.h

This header declares `webfs` internal functions by implementation file.

Covered APIs:
- Buffered input: `initibuf`, `readibuf`, `unreadline`, `readline`.
- Client management and control: `newclient`, `closeclient`, `clonectl`, `ctlwrite`, client/global ctl helpers, `plumburl`.
- Cookie operations: read/write/open/clunk/init/close, HTTP set-cookie, outgoing cookie formatting.
- Filesystem init: `initfs`.
- HTTP scheme implementation: `httpopen`, `httpread`, `httpclose`.
- I/O helpers: `iotlsdial`, `ioprint`.
- Plumbing: `plumbinit`, `plumbstart`, `replumb`.
- URL operations: parse/free/rewrite/set query/copy/escape/unescape/init.
- Utility allocation/string helpers.

Role:
- Central prototype list for all `webfs` C files and sample clients.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/fs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/fs.c

This file implements the `webfs` 9P filesystem surface, conventionally mounted at `/mnt/web`.

Filesystem layout:
- Root files: `ctl`, `clone`, `cookies`.
- Per-client directories named by client number.
- Per-client files: `ctl`, `body`, `body.<ext>`, `contenttype`, `postbody`, `parsed/`.
- `parsed/` exposes URL fields: `url`, `scheme`, `schemedata`, `user`, `passwd`, `host`, `port`, `path`, `query`, `fragment`, `ftptype`.

Qid model:
- Low 8 bits are type; upper bits encode client number.
- `PATH(type, n)`, `TYPE(path)`, and `NUM(path)` pack/unpack.

Directory/stat:
- `fillstat` names files and synthesizes `body.<ext>`.
- `rootgen`, `clientgen`, and `parsedgen` generate directory listings.

Read/write/open:
- `fsread` handles directory reads, global/client ctl reads, cookie reads, content type/post body reads, body reads via per-client worker, and parsed URL field reads.
- `fswrite` handles cookie writes, ctl command parsing/dispatch, and `postbody` writes with a 128 MB offset sanity cap.
- `fsopen` enforces mode bits, initializes cookie editing, increments client refs, opens body through the client worker, and implements `clone` by creating a new client and redirecting the fid to its ctl file.
- `fswalk1` implements manual walking through root/client/parsed directories and dynamic `body.<ext>` names.

Concurrency:
- `fsthread` serializes most 9P operations through channels, coordinates clunks, starts plumbing, and forwards body I/O to per-client workers.
- `fsflush` routes body open/read flushes to the client worker and interrupts its I/O proc.
- `fssend` serializes lib9p callbacks by sending requests to `fsthread` and waiting on `creqwait`.

Shutdown:
- `takedown` closes cookies and exits all threads.

Notable behavior:
- The implementation avoids direct handling of spurious flushes by making lib9p callbacks synchronous through `fssend`.
- Body reads/open are guarded by `c->iobusy` to prevent overlapping I/O per client.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/http.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/http.c

This file implements HTTP and HTTPS URL scheme handling for `webfs`.

HTTP state:
- `HttpState` stores fd, client pointer, redirect location, accumulated set-cookie headers, network address, Basic auth credentials, auth error text, and `Ibuf`.

Header handlers:
- `Location:` sets redirect location.
- `Content-Type:` updates client content type.
- `Set-Cookie:` appends normalized header text to `hs->setcookie`.
- `WWW-Authenticate:` handles Basic auth challenge.

Authentication:
- `wwwauthenticate` supports Basic only.
- Uses URL user/pass if present; otherwise asks factotum via `auth_getuserpasswd` with server and realm.
- Encodes `user:pass` using base64 and stores `Authorization: Basic ...`.

Open/request:
- `httpopen` dials `url->host` using URL port or scheme service; HTTPS wraps with TLS through `iotlsdial`.
- Sends HTTP/1.0 GET or POST, Host, optional User-Agent, cookies, post content headers/body, and optional Authorization.
- Parses status line with `httprcode`.
- Handles redirects 301/302/303/307, auth 401, success 200/201/202/204/205/304, and many error status codes.
- Parses MIME headers after status handling.
- Stores accepted cookies via `httpsetcookie`.
- Sets `c->redirect` or `c->authenticate` for caller-driven retry.

Read/close:
- `httpread` reads response body through `readibuf`.
- `httpclose` closes fd via client `Ioproc` and frees all `HttpState` allocations.

Notable risks:
- TLS certificate validation is explicitly missing in the lower-level dial path.
- HTTP/1.0 is used; no chunked-transfer decoding is present.
- Unknown response codes are treated as errors instead of class-based handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/http.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/io.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/io.c

This file wraps blocking network and print operations in `Ioproc` calls.

Functions:
- `iovfprint` runs `vfprint` through `iocall`.
- `ioprint` is a varargs wrapper around `iovfprint`.
- `_iotlsdial` dials an address, optionally wraps the fd with `tlsClient`, and returns the TLS fd.
- `iotlsdial` exposes `_iotlsdial` through `iocall`.

TLS behavior:
- Initializes a blank `TLSconn`.
- Contains a commented-out certificate chain read.
- Frees `conn.cert` when present.
- Prints TLS errors to stderr.

Notable risk:
- Certificate checking is explicitly marked as a bug: TLS transport is encrypted but not authenticated here.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/main.c

This is the `webfs` server entry point.

Defaults:
- Cookie file: `$home/lib/webcookies` unless overridden.
- Mount point: `/mnt/web`.
- Global controls: accept cookies on, send cookies on, redirect limit 10, user-agent `webfs/2.0 (plan 9)`.

Options:
- `-d` enables paranoid/antagonistic pool flags.
- `-D` increments `chatty9p`.
- `-c` cookie file.
- `-m` mount point.
- `-s` service name.

Startup flow:
- Calls `quotefmtinstall`.
- Duplicates default user-agent.
- Initializes plumbing, cookies, URL regexps, and filesystem channels/thread.
- Posts the 9P server with `threadpostmountsrv`.

Role:
- Wires together the independent webfs subsystems into a mounted 9P service.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/plumb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/plumb.c

This file integrates `webfs` with Plan 9 plumbing.

Initialization:
- `plumbinit` opens `send` for writing and `web` for reading.
- `plumbstart` creates a channel and starts:
  - `plumbwebproc`: receives messages from plumb port `web`.
  - `plumbwebthread`: converts plumb messages into `plumburl` calls.

Incoming plumbing:
- Uses `baseurl` attribute if present, else message working directory as base.
- `plumburl` creates a plumbed web client and opens/replumbs it asynchronously.

Outgoing/replumbing:
- `replumb(Client*)` creates a plumb message for a fetched body.
- Adds `url` and optional `content-type` attributes.
- Maps known MIME types to extensions; otherwise guesses from URL suffix or defaults to `txt`.
- Sets `c->ext` and sends `/mnt/web/<num>/body.<ext>` as message data.
- Sends in a separate proc to avoid deadlock.

Notable behavior:
- `addattr` stores raw name/value pointers without duplicating strings; `freeattrs` frees only attribute nodes, not pointed-to strings.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/plumb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/url.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/url.c

This file is the regex-driven URL parser and URL utility library for `webfs`. It targets RFC1738/RFC2396 common internet schemes with some RFC2732 IPv6 literal support.

Supported schemes:
- Known: `http`, `https`, `ftp`, `file`.
- Unknown schemes are preserved as scheme data but not opened.
- Relative URLs are resolved against a base URL.

Regex table:
- Splits scheme, authority, path, query, and fragment.
- Validates scheme, authority, host, userinfo, absolute path, query, fragment, HTTP path, FTP path, and file path.
- `initurl` compiles regexes and validates submatch indices.

Relative resolution:
- `merge_relative_path` implements RFC2396 section 5.2 path merging and dot-segment removal.
- `resolve_relative` inherits base scheme/authority/path/query/fragment as appropriate and can expand current-document references.

Parsing pipeline:
- `parseurl` duplicates input, splits it, resolves relative references if needed, parses scheme/fragment, handles unknown schemes, parses query/authority/path, and runs scheme-specific postparse.
- `postparse_http` sets open/read/close callbacks, validates authority/host, and builds `http.page_spec`.
- `postparse_ftp` validates FTP authority/path, rejects query and unexpected params, and extracts `;type=`.
- `postparse_file` rejects user/pass/query/port, requires path, and normalizes `localhost`.

Utilities:
- `freeurl` frees all fields and scheme-specific allocations.
- `rewriteurl` reconstructs `u->url` from parsed fields.
- `seturlquery` validates and replaces query.
- `copyurl` deep-copies parsed URL state.
- `escapeurl` percent-encodes bytes selected by caller.
- `unescapeurl` decodes percent escapes to Latin-1 runes.

Notable implementation issues:
- `parse_userinfo` assigns both user and password submatches to `u->user`; the password branch should likely assign `u->passwd`.
- In `resolve_relative`, the fragment-copy branch uses `su->query.s` while appending fragment bytes, which appears wrong and can copy from the wrong component.
- `unescapeurl` checks `r[0]=='0' && r[2]=='0'` after advancing past `%`; the second hex digit is `r[1]`, so escaped-NUL detection appears off.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/url.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/util.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/util.c

This file provides allocation and string helpers for `webfs`.

Functions:
- `erealloc`: fatal realloc with allocation tag.
- `emalloc`: zeroing fatal malloc with allocation tag.
- `estrdup`: fatal strdup with allocation tag.
- `estredup`: duplicates a `[s,e)` substring and NUL-terminates.
- `estrmanydup`: concatenates a varargs list of strings into a new allocation.
- `strlower`: lowercases ASCII letters in place.

Notable issue:
- `estrmanydup` calls `va_start` twice but only calls `va_end` once; this is non-idiomatic varargs handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/webget.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/webget.c

This is a sample command-line client for `webfs`.

Behavior:
- Opens `<mtpt>/clone`, reads the allocated connection number, writes optional `baseurl`, writes target `url`, optionally writes a post body to `<mtpt>/<conn>/postbody`, opens `<mtpt>/<conn>/body`, and copies it to stdout.
- `xfer` copies from fd to fd in 12 KB chunks and treats read/write errors as fatal.

Options:
- `-b baseurl`
- `-m mtpt`, default `/mnt/web`
- `-p postbody`

Role:
- Demonstrates the expected 9P control protocol for fetching via mounted `webfs`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfs/webget.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfsget.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/webfsget.c

This is another example client for mounted `webfs`, essentially equivalent to `webfs/webget.c`.

Behavior:
- Opens `/mnt/web/clone` or custom mount point.
- Reads connection number from clone.
- Writes optional `baseurl` and required `url` to the clone ctl fd.
- Optionally writes POST data to the connection's `postbody`.
- Opens the connection's `body` and streams it to stdout.

Options:
- `-b baseurl`
- `-m mtpt`
- `-p postbody`

Role:
- A top-level example command showing how to drive the webfs 9P interface.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/webfsget.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/fs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/fs.c

This file implements the `wikifs` 9P server. It exposes wiki pages, versions, generated HTML/text views, history, diffs, edit forms, error pages, and page creation.

Filesystem model:
- Root contains:
  - `new`: write-only-ish page creation endpoint.
  - `map`: title-to-number lookup endpoint.
  - One directory per page, walkable by numeric id or title.
- Page directory contains files:
  - `index.html`, `index.txt`, `current`, `history.html`, `history.txt`, `diff.html`, `edit.html`, `werror.html`, `werror.txt`, `.httplogin`.
  - History subdirectories named by timestamp expose old `index.html`, `index.txt`, and `current`.

Qid encoding:
- Qid path packs 8-bit type, 16-bit page number, 16-bit page version/index, and 8-bit file index.
- Types: `Droot`, `D1st`, `D2nd`, `Fnew`, `Fmap`, `F1st`, `F2nd`.

Walk/materialization:
- `fswalk1` resolves root entries, page dirs, history dirs, and generated files.
- On walking generated files, it eagerly renders into `Aux.s` using `tohtml`, `totext`, or raw document formatting.
- History/diff files force loading full history via `gethistory`.

Open/read/stat:
- `fsopen` enforces read-only access except `new` and `map`, snapshots current map for root reads, loads history for page dir opens, and initializes `new` write buffer.
- `fsread` generates directory listings or reads materialized strings.
- `fsstat` synthesizes metadata from qid and cached string length.

Write behavior:
- Writing to `map` maps a title/name to page number and stores it in `Aux.n`.
- Writing to `new` appends content until a zero-length write commits.
- Commit format expects title line, optional metadata lines (`A`, `D`, `C`), blank separator, and wiki body.
- It parses body with `Brdpage`, allocates/reuses page number, formats document text, and calls `writepage`.
- Max new page buffer is `Maxfile`.

Per-fid state:
- `Aux` stores requester name, current `Whist`, selected version index, materialized string, map snapshot, and target page number.
- `fsclone` refcounts `String`, `Whist`, `Map`, and user name across cloned fids.
- `fsdestroyfid` releases all referenced state.

Server startup:
- Options include `-D`, listen addresses, mountpoint/service, permission override, and no-mount mode.
- Validates wiki directory, initializes map, registers listeners, posts mount with create support, and optionally chmods `/srv/<service>`.

Notable behavior:
- Generated content is produced at walk time, so repeated reads use the fid's snapshot.
- Write conflicts are detected in `writepage`, and conflicting writes are appended to history but not installed as current.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/io.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/io.c

This file handles persistent storage, locking, title map management, and caching for wiki documents.

Storage layout:
- Wiki files live under `wikidir/d`.
- Per page:
  - `<n>`: current version.
  - `<n>.hist`: append-only full history.
  - `L.<n>`: page lock.
- Map:
  - `map`: append-only numeric id to title map.
  - `L.map`: map lock.

Cache model:
- `Wcache` entries keyed by page number cache current and history `Whist*`, qids, timestamps, and refs.
- Global cache hash has 64 buckets and nominal cap 128 entries.
- `getcache` returns current or full history, evicting least-recent unreferenced cache entries when needed.
- Cached file qids are refreshed after `Tcache` seconds.

Locking:
- `getlock` tries to create lock files with `DMEXCL`, retrying for up to about 200 seconds when errors mention `locked`.
- `readwhist` locks before reading and parsing a current/history file.

Map management:
- `currentmap` locks and reads `d/map`, validates `Maxmap`, builds `Mapel` entries, condenses/lowercases titles, sorts by title, and swaps global map under lock.
- `allocnum` validates title, checks duplicates, locks map, scans existing map directly to allocate next number, appends new entry, and forces map refresh.
- `nametonum` normalizes input by lowercase and underscore-to-space, then binary searches sorted map.
- `numtoname` finds map entry by numeric id.

Page write:
- `writepage` locks page, checks current version time against supplied edit base time, detects duplicate writes, appends all writes to history, marks conflicts with `X`, and only rewrites current file for conflict-free writes.
- Calls `voidcache` after writes/conflicts to invalidate cached page state.

Reference cleanup:
- `closewhist`, `freepage`, and `closemap` free refcounted wiki data.

Notable risks:
- Locking is file-based and intentionally described as a hack for read locks.
- `allocnum` comments acknowledge the ideal atomic map update is messy; it scans under lock and lets cache catch up.
- If no cache entry is evictable, the cache can grow beyond `Mcache`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/lookup.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/lookup.c

This is a tiny diagnostic utility.

Behavior:
- Includes wiki support headers and calls `nametonum(argv[1])`.
- Prints the numeric page id for the given title/name.

Notable omissions:
- No usage checking or `wikidir` initialization is present in this file, so it assumes the surrounding build/run environment supplies a usable default.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/map.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/map.c

This file only includes standard/wiki headers and defines no functions or data.

Role:
- It appears to be a placeholder, legacy build artifact, or intentionally empty compilation unit.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/map.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/parse.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/parse.c

This file parses wiki source text into a linked list of `Wpage` nodes.

Node creation:
- `mkwtxt` allocates a `Wpage` with type and text.
- `freepage` is in `io.c`, but this parser uses it when condensing.

Text normalization:
- `strcondense` collapses whitespace runs to one space and trims leading/trailing whitespace.
- `wcondense` condenses `Wplain` text and merges adjacent `Wplain` nodes.

Inline parsing:
- `mklink` parses `[text]` or `[text|url]` link bodies.
- `wlink` scans plain nodes for bracketed links and splits nodes around them.
- `findmanref` finds `name(section)` references where section is one digit.
- `wman` splits plain nodes around manpage references.
- `isheading` treats a line as heading if it has uppercase runes and no lowercase runes.

Block parsing in `Brdpage`:
- Blank lines create paragraph separators.
- `*` starts a bullet plus plain text.
- `!` starts preformatted text; optional following space is skipped.
- More than four `-` characters forms a horizontal rule.
- All-uppercase lines become headings.
- Other lines become plain text.

Post-processing:
- After reading all lines, parser condenses plain text, splits links, then splits man references.
- Empty pages set error `"empty page"`.

Debug:
- `printpage` dumps parsed node types and text/url/section values.

Role:
- This is the wiki markup front end used by history parsing and page writes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/parse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/parsehist.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/parsehist.c

This file parses a wiki history/current file into `Whist`.

File format:
- First line is the page title.
- Then a sequence of document metadata records and body lines.
- Metadata lines begin with:
  - `D`: document timestamp.
  - `A`: author.
  - `C`: comment.
  - `X`: conflict marker.
- Body lines begin with `#`; `Brdwline` strips that marker before passing lines to `Brdpage`.

Parsing behavior:
- `Brdwhist` reads title, loops through metadata/body sections, grows `Wdoc` array by 8, parses each body with `Brdpage`, marks the latest non-conflict document as `current`, and returns a refcounted `Whist`.
- On failure, frees title, author/comment strings, parsed pages, and doc array.

Role:
- Used by `io.c` to load current/history files and by conversion/test utilities.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/parsehist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/testwrite.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/testwrite.c

This is a test utility for writing a parsed wiki history file into the wiki store.

Behavior:
- Opens a supplied wiki/history file.
- Parses it with `Brdwhist`.
- Converts the last document back to serialized text with a fresh `D<time>` header and `pagetext(..., dosharp=1)`.
- Calls `writepage(atoi(argv[1]), t, h, doc->title)`.

Options:
- Code accepts `-t` to specify expected version timestamp, though usage text says `[-d dir]` and does not match implementation.

Role:
- Developer/test helper for exercising `writepage` conflict and storage behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/testwrite.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/tohtml.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/tohtml.c

This file renders parsed wiki documents and histories to HTML or plain text, using templates from the wiki directory.

Template handling:
- Template names include page/edit/diff/history/new/oldpage/werror HTML and selected text templates.
- `gettemplate` caches template contents in per-template RW-locked cache entries.
- The current code has cache freshness checks disabled with `if(0 && ...)`, so it effectively stats/reads more often than the comments imply.

HTML rendering:
- `s_escappend` escapes `<`, `>`, `&`, and optionally turns spaces into newlines outside pre mode.
- `mkurl` preserves absolute URLs and anchors, turns bare email-like strings into `mailto:`, otherwise creates relative wiki links.
- `pagehtml` emits headings with anchors, paragraphs, lists, links, manpage links, pre blocks, horizontal rules, and escaped plain text while managing open block tags.

Diff rendering:
- `s_diff` writes old/new rendered HTML to temporary files, runs `/bin/diff`, and wraps unchanged/changed spans as old/new text.
- `diffhtml` iterates history from newest to oldest and renders each version with metadata and diff to previous version.

History rendering:
- `historyhtml` emits a list of versions with dates, authors, conflict marker, and comments.

Top-level HTML:
- `tohtml` loads a template, substitutes `TITLE`, `VERSION`, and `DATE`, inserts generated `PAGE` content according to template type, and appends remaining template.

Plain text rendering:
- `pagetext` serializes `Wpage` nodes back to wiki text, optionally prefixing lines with `#` for history storage.
- Handles headings, paragraphs, bullets, links, man refs, pre blocks, rules, wrapping around 70 runes, and indentation prefixes.
- `historytext` renders version list.
- `totext` mirrors `tohtml` for text templates.
- `doctext` emits metadata plus serialized page body.

Notable risks:
- `s_diff` depends on external `/bin/diff` and temporary files.
- HTML link text in headings is not escaped in all paths.
- Template cache code comments do not match the disabled freshness checks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/tohtml.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/util.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/util.c

This file provides general utility helpers for `wikifs`.

Allocation/string:
- `erealloc`, `emalloc`, `estrdup`, and `estrdupn` are fatal allocation helpers with allocation tags.
- `strlower` lowercases ASCII letters in place.

String helpers:
- `s_appendsub` appends a source slice while substituting the earliest matching `Sub.match` with `Sub.sub`.
- `s_appendlist` appends a varargs list of strings to a `String`.

Temporary files:
- `opentemp` copies a template, calls `mktemp`, checks nonexistence, and creates an `ORDWR|ORCLOSE` file up to 10 tries.

Notable risks:
- `opentemp` uses `mktemp`, which is inherently race-prone, though Plan 9 semantics and immediate `create` reduce but do not eliminate concerns.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/wdir.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/wdir.c

This file wraps filesystem operations so all wiki data paths are relative to global `wikidir`.

Functions:
- `wname` builds `wikidir + "/" + relative`.
- `wopen`, `wcreate`, `wBopen`, `waccess`, and `wdirstat` call the corresponding Plan 9 filesystem operation on the expanded path and free it.

Role:
- Centralizes wiki directory prefixing for storage code in `io.c` and rendering/template reads.

Notable behavior:
- No path traversal checks are done here; callers are responsible for passing controlled relative paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/wdir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/wiki.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/wiki.h

This header defines the shared wiki data model and function contracts.

Limits:
- `Tcache`: cache freshness window.
- `Maxmap`: maximum map file size.
- `Maxfile`: maximum page write size.

Wiki node types:
- Paragraph marker, heading, bullet, link, man reference, plain text, preformatted text, horizontal rule.

Structures:
- `Wpage`: linked parsed markup node with type, text, man section, optional URL, and next pointer.
- `Whist`: refcounted page history with page number, title, doc array, count, and current index.
- `Wdoc`: one version with author, comment, conflict flag, timestamp, and parsed page.
- `Sub`: template substitution pair.
- `Mapel`: title-to-number entry.
- `Map`: refcounted title map with entries, timestamp, raw buffer, and qid.

Declared APIs:
- Allocation/string helpers.
- Parser/history readers.
- HTML/text conversion.
- Cache/map/page I/O: current/history lookup, page write, cache invalidation, allocation, title lookup.
- Map close/current functions.
- Wikidir-relative file wrappers.

Globals:
- `map`, `maplock`, `wikidir`.

Role:
- Shared interface across all wikifs implementation and utility files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/wiki.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/wiki2html.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/wiki2html.c

This is a command-line renderer for wiki pages to HTML.

Options:
- `-d dir`: sets `wikidir`.
- `-h`: render history view.
- `-o`: render old page view.
- `-D`: render diff view.
- `-P`: print parsed page node dump instead of HTML.

Behavior:
- Uses page number argument.
- Loads full history for history/diff, otherwise current page.
- Optionally dumps parser output with `printpage`.
- Calls `tohtml` on the latest document and writes to stdout.

Notable issue:
- Local `parse` is not initialized before option parsing; if `-P` is not supplied, its value is indeterminate in standard C.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/wiki2html.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/wiki2text.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/wiki2text.c

This command-line utility converts a wiki history file to serialized wiki text.

Options:
- `-d dir`: sets `wikidir`, though this utility opens the supplied file directly with `Bopen`.

Behavior:
- Parses the input history file with `Brdwhist`.
- Iterates over every document version.
- Prints a separator for each index.
- Converts each parsed page back to text with `pagetext(..., dosharp=1)` and writes to stdout.

Role:
- Debug/conversion helper for inspecting parser and serializer behavior across all history versions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/wikifs/wiki2text.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/winwatch.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/winwatch.c

This is a graphical window watcher for Plan 9 rio windows.

Behavior:
- Periodically reads `/dev/wsys`, opens each window's `label`, filters by optional exclusion regexp, and maintains an array of `Win` entries.
- Displays each window label in a tiled grid.
- Right-click selection on a label writes `unhide`, `top`, and `current` to that window's `wctl`, bringing it forward.
- Keyboard `q` or delete exits.

Layout/rendering:
- Uses configurable font, default `/lib/font/bit/lucidasans/unicode.8.font`.
- Computes rows from screen height and columns from number of windows.
- Draws labels in light blue rectangles with black borders.
- Incremental redraw uses `dirty` flags and clears removed slots.

Options:
- `-e exclude`: regexp against labels to hide entries.
- `-f font`: font path.

Notable behavior:
- The refresh logic assumes `/dev/wsys` directory entries come in stable ordering; it compares by position and label to avoid redrawing.
- Labels are truncated to the fixed 128-byte read buffer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/winwatch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/xd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/xd.c

This is a flexible binary dump utility.

Options:
- `-u`: flush output after each line.
- `-r`: collapse repeated 16-byte lines to `*`.
- `-s`: swizzle each group of four bytes.
- `-a{o|d|x}`: address base octal/decimal/hex.
- Format specs: `-c`, `-R`, or combinations of size `{b,1,w,2,l,4,v,8}` and base `{o,d,x}`.
- Multiple format specs can be supplied and are printed for each block.

Data flow:
- Reads 32 bytes but normally displays 16 so UTF rune formatting can see bytes beyond the visible block.
- Maintains `nleft` carryover when more than 16 bytes were read.
- Pads short final blocks with zero for formatting.
- Prints a final address line after short read.

Formatters:
- `fmt0`: byte values.
- `fmt1`: big-endian 16-bit words.
- `fmt2`: big-endian 32-bit words.
- `fmt3`: big-endian 64-bit values.
- `fmtc`: ASCII with escapes for tab/CR/LF/backspace and numeric fallback.
- `fmtr`: rune-aware character output with alignment handling for multi-byte runes.
- `swizz`: reverses byte order within each 4-byte word in the 16-byte block.

Input:
- Dumps stdin when no file supplied.
- Dumps one file directly or multiple files with filename titles.

Notable behavior:
- Repeat suppression only runs when `-r` is supplied and compares visible 16-byte blocks.
- 64-bit formatter constructs values from two big-endian 32-bit halves.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/xd.c -->