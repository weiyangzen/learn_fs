# Group Research: group_168_9front_sources_os_plan9_9front_sys_src_cmd_postscript_postbgi_postbg_4fc808949c76

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included. All listed files were read completely. This group is legacy 9front/PostScript userland tooling, not filesystem implementation code.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postbgi/postbgi.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postbgi/postbgi.c

`postbgi.c` is a BGI (Basic Graphical Instructions) to PostScript translator. It reads a byte-oriented BGI command stream from stdin or named files and emits DSC-structured PostScript built around the `postbgi.ps` prologue.

Main flow:
- `main()` initializes signal handling, writes DSC header/prologue, parses options, runs setup, converts each input, emits trailer/accounting.
- `header()` scans `-L` early to choose the prologue, emits conforming comments, copies the prologue, and opens setup.
- `options()` handles layout, page list, font, copy count, offsets, line width, encoding, raw PostScript pass-through, request injection, debug, and ignore-fatal modes.
- `conv()` is the BGI interpreter loop. It switches on opcodes such as character modes, graph mode, subroutine definition/call, page end, position changes, vectors, rectangles, points, lines, arcs, colors, trapezoids, patterns, and character size.

Important state:
- `hpos`/`vpos` track current BGI coordinates.
- `bgisize` and `linespace` drive text sizing.
- `fp_out` is redirected to stdout or `/dev/null` via page selection.
- `displacement[64]` records subroutine relative movement so calls update the current coordinate.
- `fontmap[]` maps short printer font names to PostScript font names.

Implemented drawing:
- Text modes emit escaped PostScript strings through `t`.
- Vectors emit relative displacement stacks for PostScript procedure `v`.
- Rectangles, trapezoids, points, lines, arcs, colors, and averaged pattern colors are translated into prologue calls/operators.
- Subroutines are emitted as PostScript procedures named `S<id>` inside DSC global sections.

Limitations and risks:
- `BREP` repeat and `BRASRECT` raster rectangle are explicitly fatal/unimplemented.
- Filled arcs/slices are not truly filled; `arc()` always emits `arcn stroke`, ignoring `mode`.
- Color mixing cannot match BGI semantics because PostScript overprints fills.
- Parsing assumes valid 7-bit BGI command/data bytes and uses old K&R C style.
- `repeat()` calls `get_int()` with no argument in old K&R style despite the function taking `highbyte`; this is legacy C behavior and fragile under modern prototypes.

Filesystem relevance: none direct; it is a userland graphics conversion utility in the 9front source tree.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postbgi/postbgi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postbgi/postbgi.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postbgi/postbgi.h

`postbgi.h` defines the BGI opcode constants, byte decoding masks, drawing mode constants, line style tables, color component selectors, and small helper structs used by `postbgi.c`.

Key contents:
- BGI opcodes include character modes, graph mode, subroutines, page end, repeat, absolute positioning, vectors, rectangles, points, line plot, character size, line style, arcs, filled shapes, raster rectangle, color, trapezoid, and pattern.
- Byte decoding macros distinguish opcode/data bytes: `CHMASK`, `DMASK`, `MSB`, `SGNB`, `MSBMAG`.
- Vector mode constants identify Manhattan x/y alternation, long vectors, and short vectors.
- `OUTLINE`/`FILL` control closed path handling.
- `STYLES` maps BGI line style IDs to PostScript dash arrays.
- `get_color()` component selectors are `RED`, `GREEN`, and `BLUE`.
- `Disp` stores subroutine displacement deltas.
- `Fontmap` maps user font aliases to PostScript names.
- `MAG(A, B)` builds a sign-magnitude integer magnitude from two BGI data bytes.
- `LINESPACE(A)` derives text line spacing from BGI character grid size.

This header is tightly coupled to `postbgi.c` and has no standalone behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postbgi/postbgi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postbgi/postbgi.mk -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postbgi/postbgi.mk

`postbgi.mk` is the historical Unix makefile for building and installing `postbgi`.

Build behavior:
- Uses `/bin/make`, `SYSTEM=V9`, `VERSION=3.3.2`, owner/group `bin`.
- Installs binaries under `/usr/bin/postscript`, prologue under `/usr/lib/postscript`, and manpage under `/tmp` by default.
- Includes common headers from `../common`.
- Builds `postbgi.o` plus common objects `glob.o`, `misc.o`, and `request.o`.
- Links with `-lm` because `postbgi.c` uses math functions such as `atan2`.
- Delegates common object builds to `../common/common.mk`.
- `changes` rewrites configurable make variables and updates the `.ds dQ` path in `postbgi.1`.

This is not the native Plan 9 `mkfile`; it is a preserved portable makefile.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postbgi/postbgi.mk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postdaisy/Opostdaisy.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postdaisy/Opostdaisy.c

`Opostdaisy.c` is an older copy of the Diablo 1640 to PostScript translator. It is almost identical to `postdaisy.c` but lacks the later Plan 9/nonprintable character adjustments.

Main behavior:
- Converts Diablo 1640 printer text/control streams into PostScript.
- Emits DSC header/prologue/setup, processes input files, emits trailer and accounting.
- Maintains printer-like state: horizontal/vertical position, margins, horizontal and vertical motion indexes, tab stops, line/page limits, reverse print mode, and shadow/bold font mode.
- Implements control characters for backspace, tabs, line feed, form feed, carriage return, and ESC sequences.
- Emits accumulated text strings to PostScript procedure `t`, minimizing stack entries by grouping runs at the same y/hmi state.
- Uses page redirection through `in_olist()` and `/dev/null`.

Differences from current `postdaisy.c`:
- Does not include `sys/types.h`.
- Does not define `isascii()` for Plan 9.
- Has a local `int interrupt();` declaration in `init_signals()`.
- In `text()`, default characters are only passed to `oput()` if `isascii(ch) && isprint(ch)`.
- In `oput()`, output directly writes the byte after escaping `\`, `(`, and `)`, with no octal fallback for nonprintable bytes.

Limitations:
- Graphics mode ESC commands are fatal/unimplemented.
- Tabs are fixed-size arrays and can be indexed from position-derived values without strong bounds checks.
- Comments warn that page/document font comments may be inaccurate.
- Reverse printing and some device behaviors were not fully tested.

Filesystem relevance: none direct; it is an archived/old variant of a PostScript text translator.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postdaisy/Opostdaisy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postdaisy/postdaisy.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postdaisy/postdaisy.c

`postdaisy.c` translates Diablo 1640 printer files to PostScript using a stateful emulation of Diablo text output.

Main flow:
- `main()` follows the common translator pattern: signals, header, options, setup, input arguments, trailer, accounting.
- `header()` emits DSC comments and copies `POSTDAISY`, optionally adding `ROUNDPAGE`.
- `options()` handles aspect ratio, copies, font, hmi/vmi, lines per page, forms per page, page list, orientation, CR/LF mode, point size, offsets, accounting, copy-through files, encoding, prologue, pass-through PostScript, requests, debug, and ignore-fatal.
- `text()` processes each byte and dispatches control characters and escape sequences.

Printer emulation:
- Coordinates use `RES=240`, with `HSCALE=2` and `VSCALE=5` from the header.
- `hmi`/`vmi` represent character and line spacing.
- Margins and tab stops are mutable via ESC sequences.
- `advance=-1` supports backward print mode.
- `shadowprint` switches to Courier-Bold until carriage return or explicit disable.
- Auto underscore uses Courier-Oblique.
- `markedpage` suppresses trailing blank page output.

Output strategy:
- `startline()`, `endstring()`, `endline()`, and `oput()` batch strings and positions for PostScript procedure `t`.
- Special PostScript string characters are escaped.
- Unlike `Opostdaisy.c`, current `oput()` emits octal escapes for nonprintable/non-ASCII bytes instead of dropping them before output.

Limitations and risks:
- Diablo graphics mode commands are fatal/unimplemented.
- `cleartabs()` loops appear swapped relative to array sizes (`ROWS` used for `htabstops`, `COLUMNS` for `vtabstops`), matching legacy code but potentially unsafe.
- Several tab/margin ESC operations index fixed arrays with position-derived values and no bounds checks.
- Document comments may be wrong when font changes occur through escape sequences.

Filesystem relevance: none direct; this is userland printer conversion code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postdaisy/postdaisy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postdaisy/postdaisy.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postdaisy/postdaisy.h

`postdaisy.h` provides device geometry and font alias definitions for the Diablo 1640 translator.

Key definitions:
- `RES=240` establishes internal coordinate resolution.
- `HSCALE=2` and `VSCALE=5` convert Diablo horizontal/vertical units to the internal resolution.
- Default spacing: `HMI=(12 * HSCALE)`, `VMI=(8 * VSCALE)`.
- Default margins are `LEFTMARGIN=0`, `RIGHTMARGIN=3168`, `TOPMARGIN=0`, `BOTTOMMARGIN=2640`.
- Tab arrays are fixed at `ROWS=400` and `COLUMNS=200`.
- `Fontmap` and `FONTMAP` map aliases such as `R`, `I`, `B`, `CO`, `CI`, `CB`, `CW`, and lowercase Courier names to Courier PostScript fonts.
- Declares non-integer function `get_font()`.

It is a small configuration/typing header used only by the daisy translator.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postdaisy/postdaisy.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postdaisy/postdaisy.mk -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postdaisy/postdaisy.mk

`postdaisy.mk` builds and installs the Diablo 1640 PostScript translator.

Build behavior:
- Uses `/bin/make`, `SYSTEM=V9`, `VERSION=3.3.2`.
- Compiles with `-O` and includes `../common`.
- Headers include `postdaisy.h` and shared common headers.
- Objects are `postdaisy.o` plus common `glob.o`, `misc.o`, and `request.o`.
- Links `postdaisy` without extra libraries.
- Installs executable, `postdaisy.ps`, and `postdaisy.1` to configurable directories with ownership/permissions.
- `changes` rewrites configuration variables and updates the prologue directory reference in the manpage.

This is a preserved portable makefile separate from the directory’s Plan 9 `mkfile`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postdaisy/postdaisy.mk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postdmd/postdmd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postdmd/postdmd.c

`postdmd.c` translates DMD bitmap files into PostScript bitmap pages.

Main flow:
- Standard translator sequence: signal setup, DSC header/prologue, options, setup, arguments, trailer/accounting.
- `bitmap()` reads one or more bitmaps from each input file and emits one PostScript page per bitmap.
- `dimensions()` detects bitmap format and dimensions.
- `addrast()` decodes input compressed raster patterns into a scanline buffer.
- `putrast()` re-encodes scanlines into a PostScript-friendly pattern/repeat format.
- `redirect()` implements page filtering.

Input formats:
- Supports Eighth/Ninth Edition bitfile format, detected by an initial zero 16-bit value followed by origin/corner coordinates.
- Also supports a simpler format where first two 16-bit values are scanlines and patterns.
- Eighth Edition raster lines are XORed with the previous line on host by default unless `-u` disables undoing and leaves it for the printer/prologue.

Options:
- `-b` controls bytes per output pattern; non-positive disables pattern chunking.
- `-f` flips/ones-complements output.
- Standard options include copies, magnification, forms per page, page list, orientation, offsets, accounting, copy-through, encoding, prologue, pass-through, requests, debug, ignore-fatal.

Output:
- Emits `v8format flip scanlength scanlines bitmap` call.
- Tracks maximum bounding box in `bbox`.
- Each scanline is emitted as repeated hex pattern runs terminated by `0`.

Limitations and risks:
- Uses K&R C and unprototyped libc calls.
- Raster allocation is based on dimensions from input; malformed dimensions can drive memory use.
- `putrast()` pattern scanning relies on `eptr` bounds checks through `patncmp()`.
- If input compressed pattern counts do not match expected totals, it raises fatal “bitmap format error”.

Filesystem relevance: none direct; it is a bitmap-to-PostScript user utility.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postdmd/postdmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postdmd/postdmd.mk -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postdmd/postdmd.mk

`postdmd.mk` builds and installs the DMD bitmap PostScript translator.

Build behavior:
- Uses `/bin/make`, `SYSTEM=V9`, `VERSION=3.3.2`.
- Includes `../common`.
- Header dependencies are common PostScript support headers.
- Objects are `postdmd.o` plus common `glob.o`, `misc.o`, and `request.o`.
- Installs `postdmd`, `postdmd.ps`, and `postdmd.1`.
- `changes` rewrites configurable paths/identity values and updates the manpage prologue directory string.

No runtime behavior; this is legacy build/install metadata.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postdmd/postdmd.mk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postgif/postgif.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postgif/postgif.c

`postgif.c` converts GIF87a images into PostScript using the `postgif.ps` prologue.

Main flow:
- `main()` initializes signals, writes header/prologue, parses options, sets up, reads input GIFs, and emits trailer.
- `readgif()` validates the GIF87a signature, reads logical screen descriptor/global color map, starts a PostScript page, processes image/extension/terminator blocks, and closes the page.
- `readimage()` reads an image descriptor, optional local color map, LZW minimum code size, decompresses image codes, drains remaining data sub-blocks, and calls `writeimage()`.
- `writeimage()` emits PostScript setup, color/grayscale lookup tables, and hex image data, handling interlaced and non-interlaced order.
- `readextensionblock()` skips GIF extension blocks.

GIF decoding:
- LZW tables are `prefix[4096]`, `suffix[4096]`, and `cstbl[4096]`.
- `initstbl()`, `nextbyte()`, `getcode()`, `putcode()`, and `firstof()` implement decompression.
- `pmap` stores decompressed pixel indices for the whole image.
- Interlace reconstruction uses pass order 0,4,2,1 rows.

Color handling:
- Global/local RGB color maps are read or a default grayscale map is generated.
- `-g` switches grayscale output.
- `-f` negates colors.
- `-G` applies gamma correction.
- Luminance weights default to 0.3, 0.59, 0.11.

Options:
- Includes aspect, copies, negative, grayscale, alignment, magnification, forms per page, page list, orientation, offsets, copy-through, encoding placeholder, debug, gamma, ignore-fatal, prologue, pass-through.

Limitations and risks:
- Only accepts GIF87a; GIF89a is not supported.
- Contains a fallback that skips 122 bytes and retries signature matching, likely for wrapped input formats.
- Uses whole-image decompression into memory.
- `nextbyte()` treats zero sub-block before end code as fatal.
- No accounting support unlike several sibling tools.
- Old-style globals and sparse error checking around `fread()` make malformed/truncated files risky.

Filesystem relevance: none direct; this is image conversion code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postgif/postgif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postio/ifdef.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postio/ifdef.c

`ifdef.c` contains the platform-dependent tty, Datakit, stdin, and line-reading code used by `postio.c`.

Structure:
- Conditional sections for `SYSV`, `V9`, `BSD4_2`, and `DKHOST`.
- Each platform provides `setupline()`, `resetline()`, `setupstdin(mode)`, and `readline()`.
- Shared globals are declared through `ifdef.h` and defined mostly in `postio.c`.

System V path:
- Opens a supplied tty line or uses stdout’s descriptor if no line is supplied.
- Optional DKHOST connection support.
- Configures termio flags, baud, stop bits, raw-ish mode, no-delay reads, and flow control.
- `resetline()` disables no-delay and enables IXON/IXOFF for split reader/writer mode.
- `setupstdin()` saves/restores stdin and sets noncanonical/no-echo interactive mode.
- `readline()` reads status lines one byte at a time, converts control-D to synthetic `endofjob`, and includes a two-process offline kludge after repeated zero-length reads.

V9 path:
- Supports local device opens and Datakit-style `ipcopen(ipcpath(...))`.
- Pushes tty line discipline, configures ttydev speed, CBREAK, and special chars.
- `resetline()` enables tandem flow control.
- `readline()` uses `FIONREAD` into a temporary buffer and has an interactive pass-through loop.

BSD 4.2 path:
- Configures NTTY discipline, CBREAK, speeds, DEC-style flow control, and special chars.
- Provides local fallback implementations of `strspn`, `strpbrk`, and `strtok`.
- `readline()` uses `FIONREAD` and `getc(fp_ttyi)`.

DKHOST path:
- `dkhost_connect()` dials Datakit destinations, temporarily redirects `stderr` to the printer log for dial errors, optionally configures receive mode/window size, maps the Datakit minor to a device name, and reopens it.

Risks:
- Heavy conditional compilation with unprototyped old C.
- Platform branches are explicitly described as untested in places.
- Fixed-size `mesg` handling is bounded by `endmesg`, but line truncation is possible.
- Uses legacy tty/ioctl APIs and Datakit interfaces.

Filesystem relevance: indirect OS/tty interaction only; no filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postio/ifdef.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postio/ifdef.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postio/ifdef.h

`ifdef.h` centralizes platform conditional includes and external declarations for `postio`’s platform-specific code.

Key contents:
- For `SYSV`, includes `<termio.h>` and optional STREAMS headers.
- For `V9`, includes `<sys/filio.h>` and `<sys/ttyio.h>`, and declares external `tty_ld`.
- For `BSD4_2`, includes `<sgtty.h>`, `<sys/time.h>`, `<errno.h>`, defines simple `FD_ZERO`/`FD_SET`, and declares `errno`.
- For `DKHOST`, includes Datakit headers and declares Datakit helpers.
- Declares shared globals from `postio.c`: tty line name, input/output fds, log file, message buffer state, baud/stop bits, interactive mode, process role, and read/write capability flags.

This header is glue between `postio.c` and `ifdef.c`; it has no behavior itself.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postio/ifdef.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postio/postio.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postio/postio.c

`postio.c` is an RS-232/Datakit PostScript printer I/O manager. It sends jobs, watches printer status, logs messages, supports interactive mode, and can split into separate reader/writer processes.

Main flow:
- `main()` initializes signals, parses options, initializes line/buffers, waits for printer readiness, optionally forks, sends input files, waits for job completion, and cleans up.
- `initialize()` reconciles options, allocates the send buffer, initializes message bounds, calls `setupline()`, and saves stdin settings.
- `start()` clears the line and loops until the printer is idle or interactive; it sends ctrl-C/ctrl-D as needed to recover from busy/waiting/error states.
- `split()` optionally forks into read and write processes after `resetline()`.
- `arguments()` sends stdin or each named file.
- `send()` sends buffered blocks while polling/parsing printer status.
- `done()` waits for idle/end-of-job after writes finish.
- `cleanup()` kills the paired writer process if split mode was used.

Status handling:
- Printer messages are expected as `%%[ key: value; ... ]%%`.
- `getstatus()` calls platform `readline()`, logs changed/unknown messages, optionally forwards non-status output to stdout, and sends ctrl-T status requests when appropriate.
- `parsemesg()` tokenizes status/error messages and maps strings through `status[]`.
- Recognized states include busy, waiting, printing, idle, endofjob, printererror, error, flushing, initializing, disconnect, unknown, nostatus, writeprocess, and interactive.

I/O:
- `readblock()` fills `block` from an input fd.
- `writeblock()` writes pending bytes to `ttyo`.
- Wrapper `Read()` and `Write()` respect read/write process roles and tolerate `EINTR`.
- `clearline()` drains status input in single-process mode.
- `slowsend()` can replace normal send if `-S` is selected.

Options:
- Baud, no ctrl-C, interactive, line, quiet, stop bits, data-to-stdout, Datakit window, block size, log file, initial PostScript, one/two process mode, slow send, debug, ignore fatal.

Exit/error behavior:
- `error()` marks exit status and calls `quit()` for fatal/user-fatal unless ignored.
- `interrupt()` handles normal abort signals and the join signal used by split mode.
- `quit()` restores stdin, signals peer, sends printer interrupt/EOF, sleeps briefly, and exits.

Risks:
- Security/robustness is legacy: raw tty control, forking, signal races, global state, old K&R function definitions, and format-string style logging through trusted internal strings.
- Status parsing is heuristic and comments acknowledge incomplete correctness.
- Split-mode behavior depends heavily on platform `resetline()`.
- `getbaud()` has no return after fatal error in source form, relying on `error(FATAL)` exit behavior.

Filesystem relevance: it opens job files and device paths, but its substantive role is printer line management rather than filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postio/postio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postio/postio.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postio/postio.h

`postio.h` defines constants, status mappings, baud mappings, buffer sizes, and function declarations for `postio.c` and `slowsend.c`.

Key definitions:
- `POSTBEGIN` defaults to PostScript code disabling job timeouts.
- Connection states: `NOTCONNECTED`, `START`, `SEND`, `DONE`.
- Process role flags: `READ`, `WRITE`, `READWRITE`.
- Printer status codes: `BUSY`, `WAITING`, `PRINTING`, `IDLE`, `ENDOFJOB`, `PRINTERERROR`, `ERROR`, `FLUSHING`, `INITIALIZING`, `DISCONNECT`, `UNKNOWN`, `NOSTATUS`, plus pseudo-states `WRITEPROCESS` and `INTERACTIVE`.
- `Status` struct and `STATUS` initializer map lower-case status strings to status codes.
- `BAUDRATE` defaults to `B9600`.
- `Baud` struct and `BAUDTABLE` map strings such as `9600`, `19200`, `19.2`, `38400`, etc. to tty baud constants.
- `BLOCKSIZE=2048` and `MESGSIZE=512`.
- Declares non-integer functions `find()`, `malloc()`, and `strtok()`.

This header encodes most of `postio`’s protocol vocabulary and default runtime parameters.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postio/postio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postio/postio.mk -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postio/postio.mk

`postio.mk` builds and installs the PostScript printer I/O manager.

Build behavior:
- Uses `/bin/make`, `SYSTEM=V9`, `VERSION=3.3.2`.
- Supports optional Datakit configuration through `DKLIB`, `DKHOST`, `DKSTREAMS`, `DKHOSTDIR`, and extra include/library paths.
- Objects are `postio.o`, `ifdef.o`, and `slowsend.o`.
- Headers are `postio.h`, `ifdef.h`, and common `gen.h`.
- `postio` target dynamically sets CFLAGS and DKLIB depending on `SYSTEM`, `DKHOST`, and `DKSTREAMS`, then reinvokes make on `compile`.
- On V9 it links with `-lipc`; on System V DKHOST it can link with `-ldk`.
- Installs executable and manpage, but no prologue library file.
- `changes` rewrites make variables in place.

This makefile matters because `postio`’s compiled behavior is strongly controlled by `SYSTEM` and Datakit macros.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postio/postio.mk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postio/slowsend.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postio/slowsend.c

`slowsend.c` implements the optional slow transmission path for `postio`, enabled by `-S`.

Behavior:
- `slowsend(fd_in)` loops over `readblock(fd_in)` and checks printer status before writing.
- It writes a full block only when the printer reports `WAITING`.
- For `BUSY`, `IDLE`, and `PRINTING`, it writes only 30 bytes.
- For `NOSTATUS` and `UNKNOWN`, it sends nothing.
- For `PRINTERERROR`, it sleeps for 30 seconds.
- For `ERROR`, `FLUSHING`, and `DISCONNECT`, it reports fatal errors.
- Local static `writeblock(num)` caps writes to `num` bytes and advances shared `head`.

Shared state:
- Uses globals from `postio.c`: `block`, `blocksize`, `head`, `tail`, `line`, `mesg`, and `ttyo`.
- Calls `readblock()`, `getstatus()`, and `error()` from the main postio implementation.

Purpose:
- It is a fallback for printers or Datakit connections with unreliable flow control.
- Comments warn it is slow, single-process only, and disables much of the newer `postio` behavior.

Risk:
- It defines a local `writeblock()` name that intentionally differs from `postio.c`’s no-argument `writeblock()` in old C style; this is fragile with modern prototypes but works in the legacy build model.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postio/slowsend.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postmd/postmd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postmd/postmd.c

`postmd.c` is a matrix display program that maps floating-point matrix data to grayscale PostScript images.

Main flow:
- Standard translator sequence: signals, DSC header/prologue, options, setup, arguments, done, accounting.
- `matrix()` processes one matrix per input file, with optional header metadata.
- If reading stdin, `copystdin()` writes it to a temporary file so the code can seek while discovering headers/dimensions.
- `getheader()` recognizes `dimension`, `window`, `name`, `colormap`/`grayscale`, `interval`, and `statistics`.
- `dimensions()` resolves matrix rows/columns, inferring square dimensions from element count if needed, allocates a raster row, and validates/reset window coordinates.
- Matrix elements are scanned with `fscanf("%f", &element)`, windowed, mapped to grayscale bytes, encoded row by row, and then labeled.

Mapping:
- `buildilist()` builds an interval list from comma/slash/space-separated floating values.
- The interval list partitions real values into `2n+1` regions.
- `addcolormap()` overrides default grayscale assignments.
- `mapfloat()` maps each element to a grayscale byte and updates per-region statistics.
- `labelmatrix()` emits labels and legend data, optionally zeroing stats if disabled.

Output:
- Emits `columns rows bitmap` call for the displayed window.
- `putrow()` uses the same pattern/repeat hex encoding style as `postdmd`.
- `labelmatrix()` calls prologue procedures for title, window coordinates, and legend.

Options:
- Pattern bytes, copies, default dimensions, grayscale/colormap, interval list, magnification, forms per page, page list, orientation, window, offsets, accounting, copy-through, encoding, prologue, pass-through PostScript, requests, debug, ignore-fatal.

Risks:
- Uses `tempnam()`, which is historically race-prone.
- `fscanf("%f", &element)` passes a `double *` to `%f`; modern C expects `float *` for `%f` and `double *` for `%lf`, making this legacy code fragile/undefined under strict modern compilation.
- Header parsing is prefix-based with `strncmp()` against keyword lengths, so abbreviated prefixes can match.
- Fixed `ilist[128]` can overflow if an excessive interval list is supplied.
- `matrixname` from headers can contain newline text and is written into a PostScript string without the same escaping discipline as data bytes.

Filesystem relevance: only temporary/input file handling; no filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postmd/postmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postmd/postmd.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postmd/postmd.h

`postmd.h` defines matrix interval-list defaults and the `Ilist` structure for `postmd.c`.

Key contents:
- `DFLTILIST` is `"-1,0,1"`, producing seven mapping regions by default.
- Comments explain how an ordered interval list partitions the real line into alternating less-than/equality regions.
- Comments also describe grayscale override lists, where colors map to regions and default values fill missing entries.
- `Ilist` contains:
  - `double val` for endpoint values,
  - `int color` for grayscale byte output,
  - `long count` for per-region statistics.
- Declares non-integer function `savestring()`.

This header is documentation-heavy and directly supports the matrix-to-grayscale mapping in `postmd.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postmd/postmd.h -->