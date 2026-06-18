# Group Research: group_1515_plan9_sources_os_plan9_plan9_sys_src_cmd_db_output_c_sources_os_pla_13367f485b50

Scope: `Docs/research_subset_a.md`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/output.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/db/output.c

This file implements shared I/O plumbing for the Plan 9 `db` debugger: formatted output, output redirection, input redirection stack management, and line-column tracking.

Key behaviors:
- Maintains `printcol`, `infile`, `maxpos`, and a global `Biobuf stdout`.
- `dprint()` formats into a fixed 4096-byte buffer, writes to `stdout`, and updates `printcol` by decoding UTF runes.
- `flushbuf()`, `newline()`, `endline()`, `flush()`, `prints()`, and `printc()` form the debugger’s low-level output API.
- `redirout()` appends to an existing output file or creates a new one, reinitializing the output `Biobuf`.
- `iclose()` manages debugger input nesting for `$<` and `$<<` style command files, with a hard maximum depth of five.
- `outputinit()` initializes output and installs `%t` formatting as a literal tab via `tconv()`.

Notable implementation details:
- `dprint()` suppresses output while `mkfault` is set.
- `iclose(err=1)` unwinds all stacked input files after an error.
- The output redirection path calls `flushbuf()` before replacing the buffered descriptor.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/output.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/pcs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/db/pcs.c

This file implements the debugger’s `:` subprocess-control command dispatcher.

Key behaviors:
- `subpcs(int modif)` handles breakpoint control, process execution, single stepping, continuing, killing, note management, and stopping/resuming an attached process.
- `:b`/`:B` set normal or temporary breakpoints at `dot`, optionally reading a command string to execute at the breakpoint.
- `:d`/`:D` clear a breakpoint at `dot`.
- `:r`/`:R` restarts the debugged program via `endpcs()`, `setup()`, and `runpcs(CONTIN, ...)`.
- `:s` single-steps; `:S` single-steps until source-line changes, using `pc2line()`.
- `:c`/`:C` continue a running process.
- `:n` lists or deletes pending notes.
- `:h` grabs/stops a current process or ungrabs it when address `0` is supplied.
- `:x` resumes an already grabbed process.

Notable implementation details:
- Breakpoint commands default to an effectively infinite count when no explicit count is given and the command is non-empty.
- On command completion it removes installed breakpoints with `delbp()`, prints the current PC, and displays pending notes.
- It depends on globals from process-control code: `pid`, `nnote`, `note`, `pcsactive`, `loopcnt`, and breakpoint list state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/pcs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/print.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/db/print.c

This file implements the debugger’s `$` command family and general debugger inspection output.

Key behaviors:
- `printtrace(int modif)` dispatches `$` commands:
  - `$<`, `$<<` redirect input from command files.
  - `$>` redirects output.
  - `$a` attaches to a process.
  - `$k` switches map handling for kernel addresses.
  - `$q`/`$Q` exits.
  - `$w` changes line width and `$s` changes symbol offset tolerance.
  - `$m` prints symbol/core maps.
  - `$r`/`$R` print registers.
  - `$f`/`$F` print floating-point registers.
  - `$c`/`$C` stack-trace using machine-specific `ctrace`.
  - `$e` prints external globals and their current values.
  - `$b`/`$B` prints breakpoints.
  - `$M` selects a machine by name.
- `ptrace()` is the stack-trace callback; it prints function name, parameters, source location, caller, and optionally locals.
- `getfname()` parses a file name up to end-of-record.
- `redirin()` opens input files directly or under `Ipath`.
- `printmap()`, `printsym()`, `printsource()`, `printpc()`, `printlocals()`, and `printparams()` provide display helpers.

Notable implementation details:
- `$C` traces locals as well as call frames.
- `printfp()` delegates register formatting to machine-specific `fpformat()`.
- `printpc()` reads `mach->pc`, resolves source and symbol offsets, and disassembles through `machdata->das()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/print.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/regs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/db/regs.c

This file manages debugger register lookup, reading, writing, and formatted register display.

Key behaviors:
- `rname()` resolves a register name against `mach->reglist`.
- `getreg()` reads a register from a `Map` using register format metadata:
  - `'x'`: 2-byte value.
  - `'f'`, `'X'`: 4-byte value.
  - `'F'`, `'W'`, `'Y'`: 8-byte value.
- `rget()` reads a named register.
- `rput()` writes a named register unless marked read-only.
- `printregs()` prints integer registers by default and floating-point registers only for `$R`, then prints machine exception text and current PC.

Notable implementation details:
- Error messages include the register name when a map read fails.
- `printregs()` formats 64-bit `'Y'` registers wider than ordinary registers.
- Floating register display skips some register formats for normal `$r` output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/regs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/runpcs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/db/runpcs.c

This file coordinates high-level execution of the debugged process and breakpoint state.

Key behaviors:
- Defines global breakpoint list `bkpthead`, breakpoint-installed flag `bpin`, process `pid`, note buffer `note`, and process-ending state.
- `runpcs()` drives repeated single-step or continue execution according to `loopcnt`.
- Handles breakpoint skip logic, temporary breakpoint clearing, breakpoint command execution, and count reset.
- `endpcs()` kills/cleans an active process, clears temporary breakpoints, and resets installed breakpoints to `BKPTSET`.
- `setup()` starts a fresh process with `startpcs()`.
- `execbkpt()` steps over a breakpoint and re-enables it.
- `scanbkpt()` finds a breakpoint at an address.
- `setbp()` installs all active breakpoints; `delbp()` removes them.

Notable implementation details:
- When stopped for real notes, `runpcs()` keeps note delivery pending.
- `BKPTSKIP` is used to avoid immediately re-triggering a breakpoint while stepping past it.
- `runpcs()` writes `dot` to the PC when `adrflg` is set before running.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/runpcs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/setup.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/db/setup.c

This file initializes symbol and core maps for the debugger.

Key behaviors:
- Maintains `symfil`, `corfil`, `symmap`, `cormap`, `dotmap`, `fsym`, and `fcor`.
- `setsym()` opens the symbol file, cracks its executable header, selects machine type, loads maps, initializes symbols, and records static-base register value if present.
- `setcor()` opens the core/proc memory file and either attaches to a running process or builds text/data mappings from the executable header.
- `dumbmap()` builds a single all-address data segment and defaults the machine to i386 if no machine is set.
- `cmdmap()` lets debugger commands mutate map segment base/end/file offsets.
- `getfile()` opens files read-write with read-only fallback, optionally creating files under write mode.
- `kmsys()` adjusts symbol maps for kernel address layout.
- `attachprocess()` switches `corfil` to `/proc/<pid>/mem`, calls `setcor()`, and warns if `/proc/<pid>/text` does not match the loaded symbol file.

Notable implementation details:
- `setcor()` closes existing core-map segment descriptors before rebuilding.
- `cmdmap()` supports mapping `?` and `/` maps onto each other by sharing `symmap` and `cormap`.
- Kernel remapping uses machine-specific `ktmask` and `kbase`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/setup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/trcrun.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/db/trcrun.c

This file contains Plan 9 `/proc` control operations used to run and trace a debugged process.

Key behaviors:
- Maintains `/proc/<pid>/ctl` and `/proc/<pid>/note` descriptors.
- `setpcs()` opens control and note files for the current `pid`, refreshing when `pid` changes.
- `msgpcs()` writes process-control messages such as `hang`, `waitstop`, `startstop`, `stop`, `start`, and `kill`.
- `unloadnote()` reads pending notes and discards `"sys: breakpoint"` notes.
- `loadnote()` writes saved notes back before continuing.
- `notes()` displays saved notes.
- `grab()` stops a process and waits; `ungrab()` starts it.
- `doexec()` parses arguments and simple `<`/`>` redirections, then `exec()`s `symfil`.
- `startpcs()` forks, hangs the child, execs target program, sets `corfil` to `/proc/<pid>/mem`, waits for stop, and optionally sets the PC.
- `runstep()` implements single stepping using machine-specific follow addresses and temporary breakpoints.
- `bpwait()` refreshes `cormap` and note state after stops.
- `runrun()` starts/stops the process, preserving notes only when requested.
- `bkput()` installs/removes breakpoint instructions in process memory.

Notable implementation details:
- Single-step fallback assumes the next instruction is `loc + mach->pcquant`.
- `bkput()` applies optional machine breakpoint address fixup before patching memory.
- Breakpoint patch failure prompts on stdin after printing an error.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/trcrun.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dc.c

This file is a complete implementation of Plan 9 `dc`, the arbitrary-precision reverse-Polish calculator.

Key behaviors:
- Represents numbers and strings as `Blk` buffers with read/write cursors.
- Uses base-100 internal numeric digits plus a trailing scale byte for decimal scale.
- `main()` initializes buffered I/O, calculator state, then enters `commnds()`.
- `commnds()` is the command interpreter for arithmetic, stack operations, registers, arrays, macros, conditionals, shell escapes, input execution, scale/input-base/output-base changes, and printing.
- Arithmetic core includes `add()`, `subt()`, `mult()`, `div()`, `dcexp()`, `dcsqrt()`, `scale()`, `removc()`, `removr()`, and `dscale()`.
- Input/output conversion includes `readin()`, `dcprint()`, `tenot()`, `oneot()`, `hexot()`, and `bigot()`.
- Register and array support uses a fixed 256-slot symbol table, with stackable symbols and array registers starting at `ARRAYST`.
- Macro execution uses `readstk` and block-backed strings.
- Memory management uses `salloc()`, `copy()`, `more()`, `release()`, `morehd()`, and a simple free list of `Blk` headers.

Notable command coverage:
- Arithmetic: `+`, `-`, `*`, `/`, `%`, `^`, `v`.
- Stack: `p`, `P`, `f`, `d`, `c`, `z`, `Z`.
- Scale/base: `k`, `K`, `i`, `I`, `o`, `O`, `X`.
- Registers: `s`, `S`, `l`, `L`.
- Arrays: `:`, `;`.
- Macros/control: `[ ... ]`, `x`, `?`, `!`, `<`, `>`, `=`, `q`, `Q`.

Notable implementation details:
- Division keeps quotient in the return value and remainder in global `rem`; fractional remainder support also uses `irem`.
- Negative numbers are represented by complement-like digit handling via `chsign()`.
- Output base selection switches between decimal, unary-like, hex fast path, and general-base rendering.
- `command()` executes shell commands through `/bin/rc -c`.
- `Y` is a debug command that dumps allocator and stack statistics.
- The garbage collector hook exists but is empty; allocation failures abort through `ospace()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dd.c

This file implements Plan 9 `dd`, with block copying, seeking, conversion, and record statistics.

Key behaviors:
- Parses option/value pairs such as `-ibs`, `-obs`, `-bs`, `-if`, `-of`, `-skip`, `-seek`, `-iseek`, `-oseek`, `-count`, `-files`, `-trunc`, `-quiet`, and `-conv`.
- Supports conversion flags `ebcdic`, `ibm`, `ascii`, `block`, `unblock`, `lcase`, `ucase`, `swab`, `noerror`, and `sync`.
- Uses `ibs`, `obs`, and optional `bs` fast path when input/output block sizes match and no conversion is needed.
- Performs input and output seeking in block or byte units.
- Tracks full/partial input and output records plus truncated fixed-length conversion records.
- `number()` parses numeric suffixes `k`, `b`, and multiplicative `x`.
- `flsh()` writes output blocks and handles short writes/errors.
- `ascii()`, `unblock()`, `ebcdic()`, `ibm()`, and `block()` implement character-set and fixed-record transformations.
- Includes full 256-byte translation tables for EBCDIC-to-ASCII, ASCII-to-EBCDIC, and ASCII-to-IBM EBCDIC.

Notable implementation details:
- With `conv=noerror`, read errors are reported, stats are printed, and copying seeks past the failed input block.
- With `conv=sync`, short reads are padded with zeros to `ibs`.
- The program uses `sbrk()` for buffers.
- Output file truncation is controlled by the `trunc` option.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/deroff.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/deroff.c

This file implements `deroff`, a troff/eqn/tbl/pic stripper that can output plain text or one word per line.

Key behaviors:
- Supports options:
  - `-w`: output one word per line.
  - `-_`: word mode preserving underscores inside words.
  - `-m m`, `-m s`, `-m l`: interpret MM/MS/list macro behavior.
  - `-i`: ignore `.so` and `.nx` includes.
- Reads through helper macros `C`/`C1`, implemented as `fC()`/`fC1()`, tracking line count and inline eqn delimiters.
- `work()` dispatches command lines to `comline()` and ordinary lines to `regline()`.
- `regline()` strips troff backslash constructions and either prints the line, macro-filtered text, or words.
- `putwords()` classifies runes and emits word tokens by the historical deroff definition.
- `comline()` handles troff commands, macro definitions, includes, next-file directives, eqn/table/pic blocks, MS/MM display macros, references, and selected macros like `.UX`.
- `eqn()` skips `.EQ`/`.EN` regions and tracks `delim` declarations for inline equations.
- `tbl()`/`stbl()` skip table regions.
- `sdis()` skips display/list-like macro regions.
- `backsl()` parses and removes troff escape constructions.
- `inpic()` extracts quoted text from pic input when applicable.
- `getfname()` opens `.so`/`.nx` targets while avoiding directories, non-mounted files, tmac files, and repeated includes.

Notable implementation details:
- Maintains a stack of up to 15 input files.
- `charclass()` treats non-ASCII runes as `EXTENDED`, except en/em dash are special separators.
- The source has duplicate `infile` declarations in the Plan 9 style block, but the effective code uses the later `Biobuf *infile`.
- The macro-skipping logic is highly stateful through globals such as `msflag`, `mac`, `disp`, `inmacro`, `intable`, `eqnflag`, `ldelim`, and `rdelim`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/deroff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dial/at.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dial/at.c

This file implements a small AT-command driver used by dial scripts.

Key behaviors:
- Usage: `at [-q] [-t seconds] command`.
- For each command argument, sends `at<command>\r` to stdout one byte at a time with 100 ms pacing.
- Reads modem response lines from stdin using `readln()`, ignoring carriage returns.
- Recognizes success responses `ok\n` and `connect\n`.
- Recognizes failure responses such as `no carrier`, `no dialtone`, `error`, `busy`, `no answer`, `delayed`, and `blacklisted`.
- Mirrors modem output to `/dev/cons` unless `-q` is set.
- Default timeout is 2 minutes for dial commands beginning with `d`/`D`, otherwise 5 seconds.

Notable implementation details:
- `writewithoutcr()` strips carriage returns when echoing to console.
- Responses are compared case-insensitively.
- An alarm bounds response waiting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dial/at.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dial/drain.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dial/drain.c

This file implements a tiny stdin-draining helper.

Key behaviors:
- Sets a short 100 ms alarm.
- Reads from stdin into a 256-byte buffer until read returns EOF/error or the alarm terminates/interrupts the read.
- Exits with status `0`.

Notable implementation details:
- A `ding()` note handler is defined to continue on alarm notes, but `main()` does not install it with `notify()`.
- In practice the helper is intended to consume any immediately pending input from a pipeline or modem connection.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dial/drain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dial/expect.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dial/expect.c

This file implements an expect-style helper for dial scripts.

Key behaviors:
- Usage: `expect [-q] [-t secs] goodstring [badstring ...]`.
- Reads from stdin into a sliding buffer sized to the longest target string plus 4096 bytes.
- Exits successfully when the good string appears.
- Exits with the matching bad string as status if any bad string appears first.
- Supports case-insensitive matching with `-i`.
- Mirrors input to `/dev/cons` unless `-q` is set.
- Default timeout is 5 minutes.

Notable implementation details:
- Keeps enough previous bytes to match strings crossing read boundaries.
- `writewithoutcr()` strips carriage returns before echoing.
- A `catch()` note handler is defined but not installed; timeout relies on Plan 9 alarm behavior if no notify handler is active.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dial/expect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dial/pass.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dial/pass.c

This file implements an interactive pass-through helper for one line of console/modem exchange.

Key behaviors:
- Usage: `pass [-q]`.
- Opens `/dev/cons` for console I/O and enables raw mode through `/dev/consctl` when available.
- Uses `rfork(RFPROC|RFFDG|RFMEM)` so parent and child share globals.
- Parent reads stdin one byte at a time with a short alarm and echoes to console unless quiet.
- Child reads one console line and writes it to stdout.
- Stops when a newline/carriage return is seen or when the shared `done` flag is set.

Notable implementation details:
- `ding()` is installed with `notify()` and turns alarm notes into resumable interruptions.
- Shared globals `alarmed` and `done` coordinate parent/child shutdown.
- The helper is designed for half-duplex scripted interaction where a user supplies one line.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dial/pass.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/ahd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/ahd.c

This file implements support for the encrypted American Heritage Dictionary backend.

Key behaviors:
- `ahdprintentry()` decrypts entry bytes by XORing each byte with `(addr++ >> 1) & 0xff`.
- Initializes a 256-entry translation table to map special encoded bytes to runes such as accented characters, degree sign, and middle dot.
- Parses inline tags delimited as `%@TAG@%`.
- For command `h`, stops output at tag `EH`.
- For command `r`, preserves tag syntax in output.
- Otherwise emits decoded text through dictionary output helpers.
- `ahdnextoff()` scans encrypted bytes for entry-boundary marker patterns `%@NL@%` and `%@2@%`.
- `ahdprintkey()` reports no pronunciations.

Notable implementation details:
- Temporarily changes `breaklen` to 80 while printing AHD entries.
- Uses a small state machine: `Run`, `Openper`, `Openat`, `Closeat`.
- `ahdnextoff()` returns a definition offset fallback if the second marker is not found.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/ahd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/canonind.awk -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/canonind.awk

This AWK script canonicalizes raw dictionary index output for use by `dict`.

Key behaviors:
- Expects one input file argument.
- Treats each raw line as an offset followed by index terms.
- Emits `term<TAB>offset` records.
- For terms with parenthesized alternates, emits both the version without the parenthesized text and the version including it.
- Writes temporary records to `junk`, then runs Plan 9 `sort -u -t'\t' +0f -1 +0 -1 +1n -2`.
- Removes the temporary file and exits.

Notable implementation details:
- Intended as a postprocessor for `mkindex`.
- Sort order folds first field while preserving exact field tie-breaking and numeric offset ordering.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/canonind.awk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/comfix.awk -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/comfix.awk

This AWK script expands comma-suffixed dictionary index entries into separate terms.

Key behaviors:
- Input records are expected as `offset<TAB>term`.
- If a term contains commas, the first comma-separated value is the base word.
- Later comma-separated suffixes are converted into derived words where possible.
- Single-letter suffixes replace the last base-word letter.
- Multi-letter suffixes search backward in the base word for a matching suffix start and accept approximate suffix-length matches.
- Unmatched suffixes are retained as `base, suffix`.

Notable implementation details:
- `matchsuflen()` implements the suffix-replacement heuristic and allows a length difference up to 3.
- Records not having exactly two fields are passed through unchanged.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/comfix.awk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/dict.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/dict.c

This file is the main Plan 9 `dict` command implementation.

Key behaviors:
- Selects the first installed dictionary from `dicts[]`, or one named by `-d`.
- Supports `-k` to print the dictionary’s key, `-c` to run one command, `-D` for debug, and a single word argument as shorthand for `/word/P`.
- Opens dictionary and index files and tracks `dot`, the current address set.
- Command parser accepts addresses followed by commands:
  - `a`: print address.
  - `h`: headword/brief output.
  - `p`: formatted entry.
  - `r`: raw-ish entry where dictionary backend supports it.
  - Uppercase commands operate over all matches.
- Address parser supports:
  - `/re/`: folded anchored regex.
  - `!re!`: non-folded anchored regex.
  - `#offset`: absolute dictionary byte offset.
  - numeric result selector.
  - `.` current result.
  - `+`/`-` next/previous entry motion.
- `search()` uses folded prefixes to binary-search the sorted index, then scans matching index lines, regex-filtering if needed.
- `locate()` performs binary search in the index file and then a linear correction pass.
- `getentry()` materializes an entry by asking the active dictionary for the next entry offset.

Notable implementation details:
- Index format is `key<TAB>dictionary_offset`.
- Search results are sorted and uniqued by `sortaddr()`.
- `setdotprev()` searches backward by widening a lookback window and repeatedly using the backend `nextoff()`.
- The main command loop is interactive and prompts with `*`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/dict.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/dict.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/dict.h

This header defines common dictionary structures, private-use marker runes, and function prototypes for all dictionary backends.

Key contents:
- Private Use Area marker enum for special output actions: `NONE`, tag markers, special character names, paragraph breaks, ligature classes, and multi-rune expansions.
- `Entry` describes an in-memory dictionary entry with `start`, `end`, and dictionary offset `doff`.
- `Assoc` maps string keys to long values.
- `Nassoc` maps numeric keys to long values.
- `Dict` describes a dictionary backend: name, description, data path, index path, `nextoff()`, `printentry()`, and `printkey()`.
- Declares common output/conversion helpers such as `fold()`, `foldre()`, `outprint()`, `outrune()`, `outpiece()`, `liglookup()`, `changett()`, and lookup helpers.
- Declares backend entry points for OED, AHD, movie, Roget, thesaurus, world, slang, simple dictionaries, and others.
- Exposes globals `bdict`, `bout`, `linelen`, `breaklen`, `outinhibit`, `debug`, `multitab`, and `dicts`.

Notable implementation details:
- `Nligs` and `Nmulti` derive table sizes from enum ranges.
- The `Dict` interface is intentionally small: offset navigation, entry printing, and key printing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/dict.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/egfix -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/egfix

This rc script normalizes raw English/German-style dictionary index data.

Key behaviors:
- Removes trailing whitespace.
- Drops lines without tabs.
- Splits comma-separated entries by emitting both the base term and a suffix-adjusted term.
- Expands parenthesized variants by emitting versions with and without parentheses.
- Collapses tab/space runs and trims trailing whitespace.

Notable implementation details:
- Implemented as a pipeline of three `sed` programs.
- Intended as a lightweight hand-cleanup helper before canonical sorting/indexing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/egfix -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/egfix2 -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/egfix2

This rc script builds an inverted, normalized index from comma/tab-separated data.

Key behaviors:
- Uses AWK with field separators tab or comma-space.
- For every field after the first, prints `term<TAB>offset`.
- Lowercases A-Z with `tr`.
- Sorts uniquely with folded-key and numeric-offset ordering.

Notable implementation details:
- Compact helper for converting multi-term raw records into `dict` index records.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/egfix2 -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/gb2312.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/gb2312.c

This file defines the GB2312 kuten-to-Unicode rune conversion table.

Key contents:
- Includes `kuten.h`.
- Defines `NONE` as `0xffff` for unmapped entries.
- Defines `Rune tabgb2312[GB2312MAX]`.
- The table maps GB2312 kuten indexes to Unicode rune values.
- Contains many `NONE` gaps for invalid or unused positions.
- Covers punctuation, symbols, Latin, kana-like compatibility ranges, Greek, Cyrillic, Bopomofo, box-drawing, CJK ideographs, and extended components present in the source table.

Notable implementation details:
- It is data-only: no functions.
- Used by dictionary/encoding code through the external declaration in `kuten.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/gb2312.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/gefix -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/gefix

This rc script normalizes German/English-style raw dictionary index data.

Key behaviors:
- Removes trailing whitespace and drops lines without tabs.
- Removes specific encoded noise sequences and quote markers.
- Normalizes hyphenated tab fields and trailing hyphens.
- Expands parenthesized forms.
- Expands `(r, s)` endings into base, `r`, and `s` variants.
- Emits extra `ss` spellings for entries containing `ß`.
- Converts tab/comma-separated values into `term<TAB>offset`, lowercases, and sorts uniquely.

Notable implementation details:
- Uses two similar `sed` expansion passes followed by AWK, `tr`, and `sort`.
- Tailored to a particular raw index format with German orthographic variants.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/gefix -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/getneeds -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/getneeds

This rc script extracts sorted “need” files from a source data file.

Key behaviors:
- Iterates over categories `spec`, `tag`, `aux`, and `status`.
- Greps category-specific lines into a temporary file.
- Sorts by fields, removes duplicate fifth-field values with AWK, then sorts numerically by another field.
- Writes outputs named `needspec`, `needtag`, `needaux`, and `needstatus`.
- Removes temporary `junk*` files per category.

Notable implementation details:
- This is a data-preparation helper, not runtime dictionary logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/getneeds -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/jis208.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/jis208.c

This file defines the JIS X 0208 kuten-to-Unicode rune conversion table.

Key contents:
- Includes `kuten.h`.
- Defines `NONE` as `0xffff` for unmapped entries.
- Defines `Rune tabjis208[JIS208MAX]`.
- The table maps JIS208 kuten indexes to Unicode rune values.
- Covers JIS punctuation, fullwidth ASCII, kana, Greek, Cyrillic, box drawing, CJK ideographs, and other symbols with unmapped gaps.

Notable implementation details:
- It is data-only: no functions.
- Used together with conversion macros and declarations in `kuten.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/jis208.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/kuten.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/kuten.h

This header defines Japanese/Chinese character-set conversion helpers and table sizes.

Key contents:
- `J2S(_h, _l)` converts JIS X 0208 high/low bytes to Microsoft Shift-JIS bytes.
- `S2J(_h, _l)` converts Microsoft Shift-JIS bytes back to JIS X 0208 high/low bytes.
- `ISJKANA()` recognizes JIS X 0201 katakana byte range.
- `CANS2JH()`, `CANS2JL()`, and `CANS2J()` validate Shift-JIS byte pairs.
- `CANJ2SB()` and `CANJ2S()` validate JIS graphic bytes/pairs.
- Defines table sizes `JIS208MAX`, `GB2312MAX`, and `BIG5MAX`.
- Declares external rune tables `tabjis208`, `tabgb2312`, and `tabbig5`.

Notable implementation details:
- Conversion is implemented as macros that mutate caller-provided high/low byte variables.
- The comments attribute the Shift-JIS “goo” to Kogure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/kuten.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/mkindex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/mkindex.c

This file implements `mkindex`, a helper for producing raw dictionary indexes.

Key behaviors:
- Selects a dictionary backend with `-d`; defaults to `dicts[0]`.
- Supports `-D` for debug.
- Opens the dictionary data file and walks entries from offset 0 to EOF using the backend `nextoff()`.
- For each entry, prints `offset<TAB>` and then invokes the backend `printentry(e, 'h')` to emit headwords.
- Uses a very large `breaklen` to keep headword output on one line.
- `getentry()` materializes an entry from offset `b` to the next backend offset, falling back to EOF for the last entry.

Notable implementation details:
- The output is intended for later sorting and canonicalization into the index format consumed by `dict`.
- Shares global names expected by backend print functions: `bdict`, `bout`, `linelen`, `breaklen`, `outinhibit`, and `debug`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/mkindex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/mkroget -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/mkroget

This rc script builds the Roget dictionary data and index.

Key behaviors:
- Converts `roget-body.rtf` to text with `rtf2txt`.
- Drops the first 12 lines.
- Special-cases entries beginning `100. ` and `388a. ` by joining the following line.
- Writes processed dictionary text to `/lib/dict/roget`.
- Runs `mkindex -d roget`, sorts uniquely with folded-key/numeric-offset ordering, cleans spacing, and writes `/lib/dict/rogetindex`.

Notable implementation details:
- This is an install/build-time data-generation script for the Roget backend.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/mkroget -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/movie.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/movie.c

This file implements a dictionary backend for a tagged movie database.

Key behaviors:
- Defines tag IDs for fields such as title, author, cast, director, release date, country, running time, rating, video data, awards, abstract, and text paragraphs.
- `movieprintentry()`:
  - For `r`, writes the raw entry.
  - Prints title first for normal/headword output.
  - For `h`, stops after the title.
  - For full output, formats release metadata, video, authors, director, producer, cinematography, credits, cast, awards, notes, abstracts, and text paragraphs.
- `movienextoff()` finds the next entry by scanning for a line beginning `$$`.
- `movieprintkey()` prints “No key”.
- `moutall()` emits comma-separated repeated tag values.
- `moutall2()` formats values of form `field1_field2` as `field2 (field1)`, with a special case for Himself/Herself cast entries.
- `mget()` finds a tag value and continuation lines within an entry.

Notable implementation details:
- Entry parsing assumes tag lines begin with two-character tags and a following separator, with continuation lines beginning with space.
- There is a literal output typo: `Cinematograpy`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/movie.c -->