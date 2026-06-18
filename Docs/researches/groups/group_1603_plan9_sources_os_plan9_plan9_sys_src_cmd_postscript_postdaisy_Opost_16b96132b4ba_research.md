# Group Research: group_1603_plan9_sources_os_plan9_plan9_sys_src_cmd_postscript_postdaisy_Opost_16b96132b4ba

Scope checked against `Docs/research_subset_a.md`: every listed file is under `sources/os/plan9/plan9`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postdaisy/Opostdaisy.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postdaisy/Opostdaisy.c

Diablo 1640-to-PostScript translator, apparently an older or alternate copy of `postdaisy.c`.

Key responsibilities:
- Emits Adobe structuring comments, copies the `POSTDAISY` prologue, optionally includes round-page support, and writes setup/trailer sections.
- Parses Diablo printer text controls into positioned PostScript text calls.
- Maintains printer state: horizontal/vertical position, margins, HMI/VMI spacing, tabs, page counters, reverse-printing mode, CR/LF behavior, and auto-bold state.
- Handles page selection through `out_list()`/`in_olist()`, page requests through `writerequest()`, form-per-page setup, accounting, and font encoding.
- Supports font aliases through `Fontmap` and maps short names like `R`, `I`, `B`, `CO`, `CI`, and `CB`.

Input/control flow:
- `main()` runs signal setup, header/prologue emission, option parsing, setup, file arguments, trailer/accounting.
- `text()` processes each input byte and dispatches backspace, tab, newline, vertical tab, formfeed, carriage return, escape sequences, and printable characters.
- `escape()` implements Diablo escape commands for margins, tabs, horizontal/vertical motion, line count, CR/LF modes, reverse printing, auto underscore, bold/shadow printing, and several ignored escape families.
- `formfeed()` closes the current page, suppresses some trailing blank pages using `markedpage`, and starts the next page if input remains.
- `oput()` emits character data into PostScript string chunks and tracks string start, last character, last horizontal position, line state, and reverse advance.

Important behavior:
- Output strings are chunked when `stringcount > 100` to avoid excessive PostScript stack use.
- Backward print mode moves before emitting a character, then suppresses normal forward motion.
- Duplicate overstrikes of the same character at the same position are suppressed by `lastc`/`prevx`.
- `changefont()` ends the active line before emitting a PostScript `f` font change.
- `redirect()` sends unselected pages to `/dev/null`.

Notable differences from `postdaisy.c`:
- Does not include the Plan 9 `isascii()` compatibility definition or `<sys/types.h>`.
- Declares `int interrupt()` locally in `init_signals()`.
- In `text()`, only ASCII printable default characters reach `oput()`.
- In `oput()`, output characters are written directly after escaping `\`, `(`, and `)`; non-printable/non-ASCII octal escaping is not present.

Dependencies:
- Uses shared PostScript support headers and globals from `comments.h`, `gen.h`, `path.h`, `ext.h`, and common objects such as `glob.o`, `misc.o`, and `request.o`.
- Expects PostScript prologue procedures `setup`, `pagesetup`, `t`, `f`, and `done`.

Risks and quirks:
- `cleartabs()` iterates `ROWS` over `htabstops[COLUMNS]`, which can write past the horizontal tab array.
- `htab()` scans up to `ROWS` while indexing `htabstops`, another possible out-of-bounds read.
- Several tab and margin indices use divisions like `hpos/ohmi` and `vpos/ovmi` without bounds checks.
- Escape command `'\015'` sets `leftmargin = BOTTOMMARGIN`, likely a typo for `LEFTMARGIN`.
- Comments explicitly say reverse printing, tabs, page comments, and some Diablo behavior are not well tested.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postdaisy/Opostdaisy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postdaisy/postdaisy.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postdaisy/postdaisy.c

Diablo 1640-to-PostScript translator, updated from `Opostdaisy.c` for Plan 9 and binary-safe character emission.

Key responsibilities:
- Emits conforming PostScript job structure, copies the `POSTDAISY` prologue, writes setup/trailer comments, and supports multiple forms per sheet.
- Translates Diablo 1640 text and motion controls into positioned PostScript strings handled by the prologue `t` procedure.
- Tracks horizontal/vertical motion, margins, tabs, page boundaries, CR/LF modes, reverse printing, automatic underline, and bold/shadow mode.
- Parses command-line options for aspect ratio, copies, font, HMI/VMI, lines per page, magnification, page list, orientation, offsets, accounting, copied PostScript snippets, encoding, prologue, and requests.

Input/control flow:
- `header()` pre-scans only for `-L` so the selected prologue can be copied before setup options are emitted.
- `options()` mutates translator state and emits PostScript definitions.
- `arguments()` translates stdin or each named input file through `text()`.
- `text()` starts with a dummy redirected page, initializes tabs, and dispatches input bytes to motion/control handlers.
- `escape()` implements Diablo escape sequences for margins, tabs, motion indexes, CR/LF policy, absolute column/line movement, half-line motion, font changes, and unimplemented graphics modes.
- `oput()` handles line/string chunking, character escaping, reverse printing, duplicate overstrike suppression, and page marking.

Important behavior:
- For ordinary bytes, `text()` calls `oput(ch)` unconditionally in the default case.
- `oput()` emits ASCII printable bytes directly, escaping PostScript string metacharacters, and emits other bytes as three-digit octal escapes.
- `formfeed()` increments `printed` only when current output is stdout, allowing page selection to suppress accounting for skipped pages.
- `ungetc(getc(fp_in), fp_in)` is used to decide whether another page should be started.
- `markedpage` suppresses trailing blank-page `showpage` for some jobs.

Dependencies:
- Shared common layer: `comments.h`, `gen.h`, `path.h`, `ext.h`, `cat()`, `out_list()`, `in_olist()`, `writerequest()`, `setencoding()`, `saverequest()`, `error()`, `interrupt()`.
- Local constants and `Fontmap` come from `postdaisy.h`.
- Expects prologue procedures `setup`, `pagesetup`, `t`, `f`, `done`, and optionally form setup procedures.

Risks and quirks:
- Same tab array problems as `Opostdaisy.c`: `cleartabs()` writes `ROWS` entries to `htabstops[COLUMNS]`, and `htab()` scans with the wrong upper bound.
- Escape commands index tab arrays without validating computed columns/lines.
- `leftmargin = BOTTOMMARGIN` in the “clear all margins” escape case looks wrong.
- Error handling for malformed multi-byte escape sequences does not check EOF before using `getc()` results.
- The source comments state graphics mode is not implemented and reverse-printing behavior is untested.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postdaisy/postdaisy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postdaisy/postdaisy.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postdaisy/postdaisy.h

Local definitions for the Diablo 1640 PostScript translator.

Contents:
- Defines a working resolution of `RES=240`, with Diablo horizontal/vertical scaling factors `HSCALE=2` and `VSCALE=5`.
- Defines default horizontal and vertical motion indexes:
  - `HMI = 12 * HSCALE`
  - `VMI = 8 * VSCALE`
- Defines default margins and page bounds in the 240-dpi coordinate system.
- Defines fixed tab array sizes `ROWS=400` and `COLUMNS=200`.
- Defines `Fontmap`, mapping user-facing aliases to PostScript font names.
- Provides `FONTMAP` initializer for Courier, Courier-Oblique, and Courier-Bold aliases.
- Declares `char *get_font()`.

Role:
- Supplies the printer geometry, font alias table, and tab table dimensions consumed by `postdaisy.c` and `Opostdaisy.c`.

Risks and quirks:
- Comments acknowledge that fixed tab arrays should ideally be allocated after HMI/VMI are known.
- The code using these constants confuses `ROWS` and `COLUMNS` in several loops, making the fixed dimensions part of a real bounds-risk surface.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postdaisy/postdaisy.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postdaisy/postdaisy.mk -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postdaisy/postdaisy.mk

Low-level makefile for building and installing `postdaisy`.

Key responsibilities:
- Defines build/install variables: `SYSTEM=V9`, `VERSION=3.3.2`, owner/group, manpage directory, PostScript binary directory, library directory, common directory, compiler flags, and linker flags.
- Builds `postdaisy` from:
  - `postdaisy.o`
  - `../common/glob.o`
  - `../common/misc.o`
  - `../common/request.o`
- Tracks headers `postdaisy.h`, `comments.h`, `ext.h`, `gen.h`, and `path.h`.
- Installs executable, prologue `postdaisy.ps`, and manpage `postdaisy.1`.
- Provides `clean`, `clobber`, and `changes` targets.

Integration:
- Common object targets delegate into `../common` with `common.mk`.
- `changes` rewrites selected makefile variables and the manpage `.ds dQ` PostScript library path.

Risks and quirks:
- Uses historical `chgrp`/`chown` install steps that assume privileged installation.
- The `changes` target edits files through temporary `XXX.*` names and simple `sed` substitutions.
- Does not include `Opostdaisy.c`; the built program is `postdaisy.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postdaisy/postdaisy.mk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postdmd/postdmd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postdmd/postdmd.c

PostScript translator for DMD bitmap files, including Eighth/Ninth Edition bitfile format handling.

Key responsibilities:
- Emits PostScript job structure and copies the `POSTDMD` prologue.
- Reads one or more bitmaps per input file and prints each bitmap as its own page.
- Detects Eighth Edition bitmap headers and decodes their run-length format.
- Optionally undoes Eighth Edition scanline XOR on the host or leaves it for the printer.
- Encodes raster data into a compact pattern/count format for a PostScript `bitmap` procedure.
- Supports page selection, copies, forms per page, orientation, offsets, magnification, accounting, and arbitrary PostScript passthrough.

Input/control flow:
- `bitmap()` loops over all bitmaps returned by `dimensions()`, emits page setup, reads compressed raster records through `addrast()`, emits scanlines with `putrast()`, and closes the page.
- `dimensions()` distinguishes V8 bitfiles by an initial zero word, reads origin/corner coordinates or direct scanline/pattern counts, allocates `raster` and `prevrast`, and initializes the previous raster to all ones.
- `addrast()` expands input pattern runs into the current raster line.
- `putrast()` optionally XOR-reconstructs V8 rasters, then emits repeated or literal hex chunks.
- `patncmp()` detects repeated `bytespp`-sized patterns.
- `getint()` reads little-endian 16-bit words.

Important behavior:
- `bytespp <= 0` disables normal repeated-pattern chunking by using whole scanlines as a pattern size.
- `flip` is passed to the PostScript prologue rather than applied in C.
- Bounding box comments are computed from the maximum bitmap width and height seen.
- Page count increments only for pages actually sent to stdout by `redirect()`.

Dependencies:
- Shared common headers and routines: `comments.h`, `gen.h`, `path.h`, `ext.h`, `cat()`, `out_list()`, `in_olist()`, `setencoding()`, `writerequest()`, `saverequest()`, `error()`, `interrupt()`.
- Expects prologue procedures `setup`, `pagesetup`, `bitmap`, and `done`.

Risks and quirks:
- `addrast()` does not bounds-check `rptr` against `eptr`; malformed input can overflow the raster buffer.
- EOF handling in raster expansion can leave partially filled buffers before later format checks.
- `dimensions()` frees/reallocates buffers for each bitmap but does not reset all global format state except what it reads.
- Uses `char` buffers for binary raster data and masks on output, which works for emission but is signedness-sensitive in comparisons.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postdmd/postdmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postdmd/postdmd.mk -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postdmd/postdmd.mk

Low-level makefile for `postdmd`.

Key responsibilities:
- Defines V9 build/install variables and common compiler/linker flags.
- Builds `postdmd` from `postdmd.o`, `../common/glob.o`, `../common/misc.o`, and `../common/request.o`.
- Installs executable, `postdmd.ps` prologue, and `postdmd.1` manpage.
- Provides `clean`, `clobber`, and `changes`.

Integration:
- Delegates shared object builds to `../common/common.mk`.
- Depends on shared PostScript headers `comments.h`, `ext.h`, `gen.h`, and `path.h`.

Risks and quirks:
- Install target assumes destination directories can be created and ownership changed.
- `changes` keeps makefile and manpage install paths synchronized via simple text substitution.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postdmd/postdmd.mk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postgif/postgif.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postgif/postgif.c

GIF87a-to-PostScript translator.

Key responsibilities:
- Emits PostScript job structure and copies the `POSTGIF` prologue.
- Reads GIF87a screen descriptors, global/local color maps, image descriptors, extension blocks, and LZW image data.
- Converts GIF pixels to either indexed color-table data or grayscale hex image data.
- Supports negative/inverted colors, grayscale output, gamma adjustment, alignment, forms per page, page selection, magnification, orientation, offsets, copied PostScript, and prologue override.
- Emits screen/page wrappers through `gifscreen` and image data through `gifimage`.

Input/control flow:
- `readgif()` initializes GIF code-size lookup table, verifies the GIF87a signature, reads the logical screen descriptor, loads or synthesizes a global color map, starts a page, and processes image/extension/terminator blocks.
- `readimage()` reads image metadata, chooses local or global color maps, allocates `pmap`, decodes LZW codes into pixel indices, skips remaining raster sub-blocks, writes the image, and restores the global map after local-map images.
- `initstbl()`, `getcode()`, `putcode()`, and `firstof()` implement GIF LZW table state.
- `writeimage()` emits color tables and pixel streams, handling interlace pass reordering when needed.
- `readextensionblock()` skips extension sub-block chains.
- `writebgscr()` and `writeendscr()` wrap each GIF screen as one PostScript page.

Important behavior:
- If the first six bytes are not `GIF87a`, it skips 122 bytes and tries again, suggesting support for a wrapper/header format.
- Grayscale uses weighted RGB conversion with defaults `0.3`, `0.59`, `0.11`.
- Gamma correction is applied to color maps when `-G` is used.
- Bounding box is tracked with `bburx` and `bbury`.

Dependencies:
- Shared common layer: `comments.h`, `gen.h`, `path.h`, `ext.h`, `cat()`, `out_list()`, `in_olist()`, `error()`, `interrupt()`.
- Links with math support for `pow()` depending on build context.
- Expects `POSTGIF` prologue procedures `setup`, `gifscreen`, `gifimage`, and `done`.

Risks and quirks:
- Accepts only `GIF87a`; GIF89a is rejected.
- Most `fread()` calls do not check return counts.
- LZW decode writes to `pmap` without checking `pmindex < imagewidth * imageheight`.
- Global `terminate` is not reset inside `readgif()`, which can affect multiple input files in one run.
- Graphic control extensions are skipped, so transparency/delay/disposal metadata is ignored.
- Interlace lookup arrays allocated in `writeimage()` are not freed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postgif/postgif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postio/ifdef.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postio/ifdef.c

System-dependent serial-line, terminal, and Datakit support for `postio`.

Key responsibilities:
- Provides conditional implementations of:
  - `setupline()`
  - `resetline()`
  - `setupstdin()`
  - `readline()`
- Supports `SYSV`, `V9`, and `BSD4_2` terminal APIs.
- Supports optional `DKHOST` Datakit connection setup.
- Supplies fallback `strspn()`, `strpbrk()`, and `strtok()` for BSD builds.
- Manages terminal modes for raw/interactive input and split reader/writer processes.

System V path:
- Opens a tty or optional DKHOST destination, duplicates input/output descriptors, enables nonblocking reads, sets termio flags, configures baud/stop bits, flushes the line, and wraps `ttyi` in `fp_ttyi`.
- `resetline()` disables nonblocking mode, enables XON/XOFF flow control, and makes reads blocking for split-process mode.
- `setupstdin()` saves/restores stdin termio and sets noncanonical no-echo mode for interactive mode.
- `readline()` reads one byte at a time, assembles complete printer status lines in `mesg`, synthesizes `endofjob` on control-D, and has a split-reader workaround for repeated zero-length reads.

V9 path:
- Includes `<ipc.h>` and can open either local device paths or Datakit IPC paths.
- Pushes a tty line discipline, configures `ttydevb` speeds and `sgttyb` flags, disables echo/CRMOD, and sets CBREAK.
- `readline()` uses `FIONREAD` and an internal `tbuf` buffer for efficiency, with different behavior for interactive mode and split read/write mode.

BSD4_2 path:
- Uses `sgtty`, `TIOCSETD`, `TIOCLGET`, `LDECCTQ`, `CBREAK`, and `TANDEM`.
- Provides similar stdin setup and line-reading semantics.
- Defines local string tokenization helpers for older libc environments.

DKHOST path:
- `dkhost_connect()` dials a Datakit destination, temporarily redirects `stderr` to the printer log during dialing, handles retry backoff, configures Datakit read mode/window parameters when available, maps to a tty name, and opens it for normal I/O.

Dependencies:
- Uses globals declared in `ifdef.h` and defined in `postio.c`: `line`, `ttyi`, `ttyo`, `fp_log`, `mesg`, `endmesg`, `baudrate`, `stopbits`, `interactive`, `whatami`, `canread`, `canwrite`.
- Uses shared `gen.h` error constants and `error()`.

Risks and quirks:
- Large portions are platform-specific legacy tty code and comments note some V9/BSD split-process paths were not tested.
- System V split-reader zero-read handling is explicitly a workaround for printer-offline hangs.
- Some APIs and constants are obsolete outside their target systems.
- DKHOST support changes `line` after connecting and depends on external Datakit library behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postio/ifdef.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postio/ifdef.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postio/ifdef.h

Conditional include and external-declaration header shared by `postio.c` and `ifdef.c`.

Contents:
- Includes system terminal headers based on `SYSV`, `V9`, `BSD4_2`, `DKHOST`, and `DKSTREAMS`.
- Declares V9 `tty_ld`.
- Provides BSD `FD_ZERO` and `FD_SET` macros and `errno` declaration.
- Includes Datakit headers and declares Datakit helpers when `DKHOST` is enabled.
- Declares `postio.c` globals needed by `ifdef.c`: printer line, tty descriptors, log file, message buffer, baud/stop settings, interactive flag, process role flags, and read/write permissions.

Role:
- Keeps platform-dependent build branches centralized so `postio.c` can call `setupline()`, `resetline()`, `setupstdin()`, and `readline()` without direct system-header clutter.

Risks and quirks:
- Exposes many globals across translation units.
- BSD `FD_*` macros are simplistic integer bitset definitions rather than modern `fd_set` use.
- Build correctness depends on exactly one expected platform macro being defined by `postio.mk`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postio/ifdef.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postio/postio.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postio/postio.c

Serial/Datakit I/O manager for PostScript printers.

Key responsibilities:
- Opens/configures the printer line, verifies printer readiness, sends PostScript jobs, monitors printer status, and waits for completion.
- Supports single-process mode and optional split read/write processes.
- Supports interactive mode, quiet mode, slow-send fallback, page/job data returned to stdout, printer log files, custom initial PostScript, baud/stop-bit settings, and Datakit window size.
- Parses printer status/error messages like `%%[ status: idle ]%%`, `%%[ Error: ... ]%%`, and `%%[ PrinterError: ... ]%%`.
- Handles signal cleanup, printer reset/EOF, child process termination, and terminal restoration.

Control flow:
- `main()` calls signal setup, option parsing, initialization, printer startup, optional process split, input argument sending, completion wait, and cleanup.
- `initialize()` resolves mode interactions, allocates the send buffer, initializes message bounds, calls platform `setupline()`, and saves stdin terminal state.
- `start()` clears stale line data and polls status until the printer is idle/interactive, sending control-C or EOF when needed.
- `split()` forks into read and write processes when requested and supported by platform `resetline()`.
- `arguments()` sends stdin or each named input file when the current process can write.
- `send()` reads file blocks and writes them based on current printer state; it aborts on PostScript errors, flushing, or disconnects.
- `done()` waits for end-of-job or idle state after writing, coordinating split reader/writer completion through `joinsig`.
- `cleanup()` kills and waits for the peer process in split mode.

Status and parsing:
- `getstatus()` reads a complete line using platform `readline()`, parses it, logs state changes, optionally forwards non-status output to stdout, or sends control-T status queries.
- `parsemesg()` extracts bracketed printer reports, tokenizes key/value pairs, recognizes status/error keywords through `STATUS`, and maps Datakit conversation end to `DISCONNECT`.
- `find()` is a local substring search returning the match or string end.

I/O helpers:
- `readblock()` fills `block` from input and optionally logs fake busy status in quiet mode.
- `writeblock()` writes pending bytes from `block` to `ttyo`.
- `Read()` and `Write()` wrap system calls so split read-only/write-only processes can share code.
- `Rest()` suppresses sleeps in read-only processes.
- `clearline()` drains printer input only in single-process mode.

Error/signal handling:
- `interrupt()` handles normal termination signals and the split-process join signal.
- `error()` logs messages, sets `x_stat`, and exits via `quit()` for fatal errors unless `ignore` is enabled.
- `quit()` signals the peer, restores stdin, sends printer interrupt/EOF when connected, waits briefly, and exits.

Dependencies:
- Platform line operations from `ifdef.c`.
- Constants and lookup tables from `postio.h`.
- Shared `gen.h` booleans/error constants.
- Optional `slowsend()` from `slowsend.c`.

Risks and quirks:
- Heavy global mutable state couples process role, current printer state, buffers, message parsing, and signal cleanup.
- Split-process coordination is signal-based and timing-sensitive.
- `parsemesg()` uses `strtok()` and simplified parsing; unusual status values with embedded delimiters may be misclassified.
- The `getbaud()` fatal path has no explicit return after `error()`, relying on `error()` exit behavior.
- `Write()` treats `EINTR` as a successful full write, which can hide interrupted writes in some paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postio/postio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postio/postio.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postio/postio.h

Constants, state codes, and lookup-table definitions for `postio`.

Contents:
- Defines default `POSTBEGIN` PostScript sent before jobs: disables printer job timeout.
- Defines high-level connection states: `NOTCONNECTED`, `START`, `SEND`, `DONE`.
- Defines process role flags: `READ`, `WRITE`, `READWRITE`.
- Defines printer status codes: `BUSY`, `WAITING`, `PRINTING`, `IDLE`, `ENDOFJOB`, `PRINTERERROR`, `ERROR`, `FLUSHING`, `INITIALIZING`, `DISCONNECT`, `UNKNOWN`, `NOSTATUS`, plus dummy states `WRITEPROCESS` and `INTERACTIVE`.
- Defines `Status` and `STATUS` initializer mapping lowercase status strings to status codes.
- Defines default baud rate `BAUDRATE=B9600`.
- Defines `Baud` and `BAUDTABLE` mapping strings like `9600`, `19200`, `38.4`, `EXTB` to terminal speed constants.
- Defines `BLOCKSIZE=2048` and `MESGSIZE=512`.
- Declares `find()`, `malloc()`, and `strtok()`.

Role:
- Provides the shared protocol between option parsing, status parsing, send/done control flow, and platform I/O code.

Risks and quirks:
- Baud table assumes legacy speed constants `EXTA`/`EXTB`.
- Status recognition depends on lowercase strings and ordering before the `NULL` terminator.
- Function declarations are pre-ANSI and incomplete by modern C standards.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postio/postio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postio/postio.mk -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postio/postio.mk

Low-level makefile for `postio`.

Key responsibilities:
- Defines V9/default build variables, install directories, common directory, compiler/linker flags, and Datakit options.
- Builds `postio` from `postio.o`, `ifdef.o`, and `slowsend.o`.
- Installs executable and manpage.
- Provides platform-aware compile target that exports `SYSTEM`, `DKHOST`, `DKSTREAMS`, and `DKLIB` settings.
- Provides `clean`, `clobber`, and `changes`.

Important behavior:
- For V9, links with `-lipc`.
- For non-V9 with `DKHOST=TRUE`, may force `SYSTEM=SYSV`, define `DKHOST`, optionally define `DKSTREAMS`, and link `-ldk`.
- Adds `-D$SYSTEM` to `CFLAGS` before compiling.

Dependencies:
- Headers: `postio.h`, `ifdef.h`, and `../common/gen.h`.
- No shared common objects are linked, because `postio.c` provides its own logging/error path.

Risks and quirks:
- Build behavior is controlled by shell-variable mutation inside a recursive make target.
- Commented `DKHOSTDIR` guidance shows this makefile expects site-local Datakit library/header layout.
- `postio ::` target recursively invokes `compile`, so environment leakage matters.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postio/postio.mk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postio/slowsend.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postio/slowsend.c

Slow-send fallback for `postio`.

Key responsibilities:
- Provides `slowsend(fd_in)`, a conservative transmission loop for printers or links with unreliable flow control.
- Sends large chunks only when the printer reports `WAITING`.
- Sends small chunks for `BUSY`, `IDLE`, and `PRINTING`.
- Sleeps on `PRINTERERROR`, ignores transient `NOSTATUS`/`UNKNOWN`, and aborts on PostScript errors, flushing, or disconnect.
- Provides a local static `writeblock(num)` that limits each write to at most `num` bytes.

Integration:
- Uses global `postio` send buffer state: `block`, `blocksize`, `head`, `tail`, `line`, `mesg`, and `ttyo`.
- Calls `readblock()`, `getstatus()`, `error()`, and writes directly to `ttyo`.
- Enabled by `postio -S`, which also disables split mode and caps block size in `initialize()`.

Risks and quirks:
- Comments explicitly call it a last-resort workaround.
- It can be very slow and depends on reliable status responses.
- Has a local `writeblock()` with the same conceptual role but different signature from `postio.c`’s `writeblock()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postio/slowsend.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postmd/postmd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postmd/postmd.c

Matrix-display translator that renders floating-point matrices as PostScript grayscale images.

Key responsibilities:
- Emits PostScript job structure and copies the `POSTMD` prologue.
- Reads one matrix per input file, optionally with a header.
- Maps matrix elements through an interval list into grayscale byte values.
- Supports custom grayscale/color maps, matrix dimensions, display windows, labels, statistics, page requests, forms per page, accounting, and arbitrary PostScript passthrough.
- Encodes each displayed row using the same repeated-pattern hex format used by bitmap translators.

Input/header support:
- Matrix headers can define:
  - `dimension`
  - `interval`
  - `colormap` or `grayscale`
  - `window`
  - `name`
  - `statistics`
- If stdin is used, `copystdin()` copies it to a temp file so header probing and seeking work.
- If dimensions are absent, `dimensions()` counts all remaining elements and assumes a square matrix using `sqrt(count)`.

Control flow:
- `matrix()` resets defaults, builds interval/color/window state, reads the optional header, validates dimensions/window, starts a page, maps matrix elements into row raster data, emits rows, labels the matrix, and closes the page.
- `buildilist()` constructs alternating less-than/equality interval regions and default grayscale values.
- `addcolormap()` overrides region colors.
- `setwindow()`, `inwindow()`, and `inrange()` select a submatrix.
- `mapfloat()` classifies each element and increments per-region counts.
- `putrow()` compresses row bytes into repeated/literal hex chunks.
- `labelmatrix()` emits PostScript calls for title, window labels, interval labels, counts, and legend.

Important behavior:
- Default interval list is `-1,0,1`, producing seven regions.
- Region colors default from near-white to black.
- `nxtstat` can suppress legend counts for the next matrix while still printing the legend structure.
- `bytespp <= 0` disables normal repeated-pattern chunking by using the row width.
- Temporary stdin copy is unlinked in `done()`.

Dependencies:
- Shared common layer: `comments.h`, `gen.h`, `path.h`, `ext.h`, `cat()`, `out_list()`, `in_olist()`, `setencoding()`, `writerequest()`, `saverequest()`, `error()`, `interrupt()`, `tempnam()`.
- Local interval structures from `postmd.h`.
- Links with math library for `sqrt()`.

Risks and quirks:
- `fscanf(fp_in, "%f", &element)` uses a `double element`; modern C expects `%lf` for `double *`.
- `rows = sqrt(count)` truncates silently and does not verify the element count is a perfect square.
- `setwindow()` writes coordinates without checking more than four tokens.
- `addcolormap()` can write beyond `ilist[]` if too many colors are supplied.
- Matrix labels are inserted into PostScript strings without escaping parentheses/backslashes.
- Uses tempnam-style temporary file creation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postmd/postmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postmd/postmd.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postmd/postmd.h

Local definitions for the matrix-display translator.

Contents:
- Defines default interval list `DFLTILIST "-1,0,1"`.
- Documents interval-to-region mapping and grayscale override behavior.
- Defines `Ilist` structure:
  - `double val`
  - `int color`
  - `long count`
- Declares `char *savestring()`.

Role:
- Provides the interval-list data model used by `postmd.c` to classify floating-point matrix elements and build legend/statistics output.

Risks and quirks:
- Comments describe equality regions as separate buckets; exact floating-point equality is therefore semantically significant.
- No size constants are defined here for `ilist`; the implementation hardcodes `ilist[128]`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postmd/postmd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postmd/postmd.mk -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postmd/postmd.mk

Low-level makefile for `postmd`.

Key responsibilities:
- Defines build/install variables for V9, package version, ownership, directories, compiler flags, and linker flags.
- Builds `postmd` from:
  - `postmd.o`
  - `../common/glob.o`
  - `../common/misc.o`
  - `../common/request.o`
  - `../common/tempnam.o`
- Links with `-lm`.
- Installs executable, prologue `postmd.ps`, and manpage `postmd.1`.
- Provides `clean`, `clobber`, and `changes`.

Integration:
- Delegates common object builds to `../common/common.mk`, passing `SYSTEM=$(SYSTEM)` for `tempnam.o`.
- Tracks `postmd.h` and shared PostScript headers.

Risks and quirks:
- `changes` rewrites makefile variables and manpage library path using simple `sed` substitutions.
- Install target assumes ownership-changing privileges.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postmd/postmd.mk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postprint/postprint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postprint/postprint.c

ASCII-to-PostScript text translator.

Key responsibilities:
- Emits conforming PostScript structure, copies the `POSTPRINT` prologue, and writes setup/trailer comments.
- Translates ASCII/text input into PostScript line-printing calls.
- Expands or compresses spaces, tabs, backspaces, carriage returns, and form feeds.
- Supports font selection, line count, point size, tab stops, CR mode, page selection, copies, forms per page, orientation, offsets, accounting, copied PostScript, encoding, prologue override, and page/global requests.

Control flow:
- `main()` runs signal setup, header/prologue emission, option parsing, setup, input processing, trailer/accounting.
- `header()` pre-scans `-L` for prologue selection.
- `setup()` emits request/encoding/setup code and derives `linespp` from point size when `-l0` or negative lines are supplied.
- `arguments()` processes stdin or each named input file, starting each file on a new page.
- `text()` dispatches newlines, tabs, backspaces, spaces, formfeeds, carriage returns, and default bytes.
- `spaces()` groups runs of spaces/tabs/backspaces/CR and chooses between literal spaces or ending the string and restarting at a target column.
- `oput()` emits printable characters with PostScript escaping and optionally emits octal escapes for non-printable bytes.
- `formfeed()` closes the current page and starts the next one if input remains.

Important behavior:
- `stringcount == 1` uses fast prologue procedure `l`; multiple string/column pairs use `L`.
- `endstring()` emits `LL` chunks when too many string/column pairs accumulate, avoiding PostScript stack overflow.
- Backspacing is represented by ending the current string and restarting at an earlier column.
- Carriage return mode:
  - default ignores CR
  - mode 1 treats CR as spacing/control inside `spaces()`
  - mode 2 treats CR as newline
- Extended octal escaping is effectively always enabled by default.

Dependencies:
- Shared common layer: `comments.h`, `gen.h`, `path.h`, `ext.h`, `cat()`, `out_list()`, `in_olist()`, `setencoding()`, `writerequest()`, `saverequest()`, `error()`, `interrupt()`.
- Local defaults and `Fontmap` from `postprint.h`.
- Expects prologue procedures `setup`, `pagesetup`, `l`, `L`, `LL`, and `done`.

Risks and quirks:
- `spaces()` uses `while ( ch = getc(fp_in) )`; EOF (`-1`) is truthy, so the loop relies on the internal `else break` path and then calls `ungetc(ch, fp_in)` even for EOF-like values.
- Page closing always emits `showpage` for the previous page, unlike `postdaisy`’s `markedpage` suppression.
- Column accounting assumes fixed-width fonts; arbitrary fonts are allowed but documented as unsuitable.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postprint/postprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postprint/postprint.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postprint/postprint.h

Local defaults and font aliases for `postprint`.

Contents:
- Defines default `LINESPP=66`, `TABSTOPS=8`, and `POINTSIZE=10`.
- Defines `Fontmap` structure for user font aliases.
- Defines `FONTMAP` aliases for Courier, Courier-Oblique, and Courier-Bold.
- Declares `char *get_font()`.

Role:
- Supplies default text layout settings and fixed-width PostScript font aliasing used by `postprint.c`.

Risks and quirks:
- Comments state only constant-width fonts are guaranteed to work well, but the translator allows arbitrary font names when lookup fails.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postprint/postprint.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postreverse/postreverse.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postreverse/postreverse.c

PostScript page-order reverser for structurally commented PostScript files.

Key responsibilities:
- Reorders pages using Adobe structuring comments and package-specific comments.
- Copies the prologue/setup/trailer while reversing selected page bodies.
- Moves page-local global definitions bracketed by `%%BeginGlobal`/`%%EndGlobal` into the prologue/setup section.
- Supports documents using `%%Page:` starts, `%%EndPage:` ends, or both.
- Handles multiple forms per physical page by reversing sheets while preserving subpage order and adding dummy pages as needed.
- Supports page selection, no-reverse mode, version override for dummy-page behavior, temporary directory override, debug, and ignore-fatal options.

Control flow:
- `arguments()` accepts at most one input file, or copies stdin to a temporary file.
- `reverse()` copies through `%%EndProlog`, records pages/globals, writes pages in new order, and copies trailer content.
- `moreprolog(str)` copies input until a target comment, updating `forms` and `version` from structuring comments.
- `readpages()` records page start/stop offsets in `pages[]`, detects setup sections, extracts global sections, and finds trailer offset.
- `writepages()` emits the end of prologue/setup, pads dummy pages when reversing multi-form documents, then copies real pages in reverse sheet order.
- `copypage()` copies a page range while skipping `%%BeginGlobal`/`%%EndGlobal` sections.
- `trailer()` copies everything after `%%Trailer`.

Important behavior:
- `-r` disables reversal but still normalizes global definitions, by setting `forms = next_page` in `writepages()`.
- Empty dummy pages are emitted differently depending on input `version` and `ignoreversion`.
- If no `%%EndProlog` is found, the file is copied through unchanged.
- If stdin is used, the input is read into a temp file and then processed with random-access `ftell()`/`fseek()`.

Dependencies:
- Shared common layer: `comments.h`, `gen.h`, `path.h`, `ext.h`, `out_list()`, `error()`, `interrupt()`, and `temp_file`.
- Local `Pages` struct from `postreverse.h`.

Risks and quirks:
- Fixed `pages[1000]` page table can overflow on larger jobs.
- Uses `ftell()`/`fseek()` and text-mode line lengths; very long lines beyond `buf[2048]` can break comment detection.
- `copystdin()` uses tempnam-style temp-file creation.
- Everything between consecutive `%%EndPage:` and `%%Page:` comments is intentionally ignored, per comments.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postreverse/postreverse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postreverse/postreverse.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postreverse/postreverse.h

Local page-offset structure for `postreverse`.

Contents:
- Defines `Pages` with:
  - `long start`
  - `long stop`
  - `int empty`
- Declares `char *copystdin()`.

Role:
- Supplies the page table entry used by `postreverse.c` to record byte ranges for each page and dummy-page markers.

Risks and quirks:
- No table size is defined here; `postreverse.c` hardcodes `pages[1000]`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postreverse/postreverse.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postscript.mk -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postscript.mk

Top-level makefile for the Plan 9/DWB PostScript support package.

Key responsibilities:
- Documents package-wide configuration variables and build/install workflows.
- Defines global defaults:
  - `SYSTEM=V9`
  - `VERSION=3.3.2`
  - owner/group
  - root, font, host font, manpage, PostScript binary/library, and tmac directories
  - compiler/linker flags
  - Datakit options
  - `ROUNDPAGE=TRUE`
- Defines default `TARGETS` for the full PostScript tool suite, including `postdaisy`, `postdmd`, `postgif`, `postio`, `postmd`, `postprint`, and `postreverse`.
- Provides aggregate `all`, `clean`, `clobber`, `install`, and `changes` targets.
- Recursively invokes each target directory’s `<target>.mk` when the directory and makefile exist.

Integration:
- Exports package-level variables into recursive makes.
- Sets `COMMONDIR=../common` for subdirectories.
- Allows `TARGETS=...` override to build/install only selected tools.
- `changes` propagates selected configuration values into lower-level makefiles/manpages.

Risks and quirks:
- Historical makefile assumes `/bin/make`, privileged install paths, and recursive make behavior.
- Target list includes many directories beyond this group; nonexistent target directories are silently ignored by the shell test.
- Comments warn that source files must be updated after changing definitions by running `make -f postscript.mk changes`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postscript.mk -->