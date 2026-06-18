# Group Research: group_185_9front_sources_os_plan9_9front_sys_src_cmd_tcs_ms_h_sources_os_plan9_31ae912ec893

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/ms.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/ms.h

This header is a generated-style lookup-table bundle for `tcs`, Plan 9's character set converter. It contains `long tabcpNNN[256]` tables mapping Microsoft/OEM single-byte code page byte values to Unicode rune values.

Key contents:
- A leading commented rc pipeline documents how the tables were originally generated from Microsoft code-page reference pages.
- Tables include IBM/OEM pages such as `cp437`, `cp720`, `cp737`, `cp775`, `cp850`, `cp852`, `cp855`, `cp857`, `cp858`, `cp862`, `cp866`, `cp874`.
- Tables include Windows pages `cp1250` through `cp1258`.
- Valid byte mappings are Unicode scalar values stored as `long`; unmapped bytes are represented as `-1`.

Integration:
- Included by `tcs.c`.
- Entries are registered in `convert[]` under names such as `ibm437`, `windows-1252`, and aliases like `microsoft`.
- Used by table-driven input conversion through `intable()` and output conversion through `outtable()`.

Risk notes:
- This file is pure static data, but table correctness is critical: `-1` entries trigger conversion errors unless `-c` clean mode is enabled.
- Vietnamese `windows-1258` includes combining marks such as `0x0300`, so downstream Unicode normalization/output behavior matters.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/ms.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/tcs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/tcs.c

`tcs.c` is the main driver for the Plan 9 character set conversion command.

Main behavior:
- Parses `-f from`, `-t to`, `-l`, `-c`, `-s`, and `-v`.
- Defaults to UTF input and UTF output.
- Resolves charset names through `aliasname()` and `conv()`.
- Converts stdin or each named file through either table-driven or function-driven converters.
- Tracks `ninput`, `nrunes`, `noutput`, and `nerrors`.

Core paths:
- `main()` selects input and output `struct convert` entries and dispatches each file.
- `list()` prints available character sets from `convert[]`.
- `intable()` maps each input byte through a 256-entry table to `Rune`.
- `outtable()` builds an inverse byte map from a 256-entry Unicode table and writes single-byte output.
- `unicode_in*()` and `unicode_out*()` handle UTF-16-like “unicode” big/little endian input/output, including BOM processing.
- `fixsurrogate()` combines surrogate pairs into runes.

Important data:
- Includes many charset data headers: Cyrillic, ISO-8859, Microsoft/OEM, Big5, GB, etc.
- Defines `convert[]`, the central registry of supported charsets and aliases.
- Table charsets use `Table`; stateful/multibyte charsets use function pairs.

Risk notes:
- `unicode_in()` has a deliberate `default: OUT(out, &r, 1);` fallthrough into little-endian processing; this treats the first non-BOM word as data then continues.
- `outtable()` rebuilds the inverse map on every call, which is simple but repeated work for large output streams.
- Error handling depends on `squawk` and `clean`: invalid input/output chars can warn, count errors, drop chars, or map to `BADMAP`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/tcs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/tune.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/tune.c

`tune.c` implements conversion between Unicode Tamil code points and TUNE private-use encoded Tamil glyph sequences.

Main data:
- `t1[]`: independent Tamil vowels and aytham to TUNE private-use code points.
- `t2[]`: Tamil vowel signs/virama indexed by low nibble positions.
- `t3[]`: Tamil consonant bases to TUNE base forms.

Core functions:
- `findbytune()`, `findbyuni()`, `findindex()` perform small linear table searches.
- `tune_in()` reads UTF runes through `Bgetrune()`, maps TUNE ranges back to Tamil Unicode sequences, and passes runes to the selected output converter.
- `tune_out()` is a state machine converting Tamil Unicode sequences into TUNE glyph code points.

Control flow:
- TUNE consonant forms in `0xe210..0xe38c` are decoded using the code-point low nibble as a vowel-sign selector.
- Special ligatures/compound Tamil sequences are handled explicitly, including `க்ஷ` and `ஶ்ரீ`.
- Output state tracks a pending consonant/vowel combination and flushes it when the next rune proves it cannot combine.

Risk notes:
- The output path is stateful across calls through static `state` and `lastr`; the final zero-length `OUT` call is required to flush pending state.
- Invalid private-use TUNE runes warn as “not in output cs,” count errors, and may be dropped in clean mode.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/tune.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/utf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/utf.c

`utf.c` supplies UTF-related converters for `tcs`: Plan 9 UTF-8, UTF-1/ISO 10646 Annex A, and Unicode normalization output.

Core functions:
- `utf_in()` reads bytes, preserves incomplete UTF sequences between reads, decodes with `our_mbtowc()`, and emits runes.
- `utf_out()` encodes runes with `our_wctomb()`.
- `utfnfc_out()` and `utfnfd_out()` wrap `utfnorm_out()` using Plan 9 normalization APIs.
- `isoutf_in()` and `isoutf_out()` implement UTF-1 input/output through `isochartorune()` and `runetoisoutf()`.
- `fullisorune()` determines whether enough bytes exist for a UTF-1 sequence.

Important implementation details:
- `our_wctomb()` supports historical UTF encodings up to 6 bytes.
- `our_mbtowc()` rejects bad continuation bytes and overlong encodings.
- `mktable()` builds translation tables for UTF-1 byte remapping.

Integration:
- Registered from `tcs.c` as `utf`, `utf-8`, `utf1`, `nfc`, and `nfd`.
- Uses global `runes`, `obuf`, counters, `squawk`, `clean`, and `nerrors` from the `tcs` program.

Risk notes:
- `utfnorm_out()` uses static normalization state, so it depends on the final zero-length flush call to finish a stream.
- UTF-8 handling accepts historical Plan 9 rune width behavior rather than modern strict Unicode scalar constraints.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/utf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tee.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tee.c

This is Plan 9 `tee`, copying stdin to stdout and all named files.

Behavior:
- `-a` appends by opening existing files or creating them, then seeking to end.
- `-i` installs a notify handler that ignores `"interrupt"`.
- `-u` is accepted but ignored as an undocumented Unix relic.
- Files are duplicated onto descriptors starting at `FDSTART` (`3`) and written sequentially for every input block.

Risk notes:
- Write errors are ignored after files are opened; a later failed file or stdout write does not affect exit status.
- Open failures are reported but do not stop copying to other destinations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tee.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/telco/telco.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/telco/telco.c

`telco.c` implements a user-space 9P filesystem over serial modem devices. It publishes `/net/telco`, `clone`, per-device directories, and per-device `data`/`ctl` files, while also monitoring rings and dispatching incoming fax/data calls.

Major structures:
- `Fid`: tracks 9P fid state, qid, open state, and user.
- `Dev`: tracks real modem ctl/data fds, device type, file permissions, buffered input ring, pending read requests, and monitor process state.
- `Request`: queued blocked data reads.
- `Type`: modem type descriptors and command strings.

Filesystem model:
- Qids encode level/type and device index.
- `devgen()` enumerates root, `/telco`, `clone`, device directories, and `data`/`ctl`.
- `devstat()` synthesizes Plan 9 `Dir` metadata.
- `rversion`, `rattach`, `rwalk`, `ropen`, `rread`, `rwrite`, `rclunk`, `rstat`, and `rwstat` implement 9P operations.
- Opening `clone` assigns a free modem and returns its control file qid.

Modem behavior:
- `monitor()` opens real serial ctl/data files and forks a background reader.
- `attention()`, `apply()`, and `readmsg()` issue Hayes commands and parse modem responses.
- `modemtype()` probes modem speed/type and configures data/fax mode.
- `dialout()` parses `connect number[!speed][!nocompress][!fax]`, configures the modem, dials, and adjusts serial speed if needed.
- `receiver()` answers `RING`, distinguishes data versus fax by modem response, and execs `/bin/service/telcodata` or `/bin/service/telcofax`.
- `onhook()` toggles modem control lines and reinitializes fax-capable mode.

Buffered I/O:
- `monitor()` writes serial input into a circular `rbuf`.
- `rread()` queues `Request` objects for data reads.
- `serve()` drains pending read requests when bytes are available.

Risk notes:
- `serve()` allocates `buf = malloc(messagesize-IOHDRSZ)` but compares `r->count > sizeof(buf)`, which is pointer size, not allocation size; this can artificially limit reads and is suspicious.
- Permission logic assumes Plan 9 user/group conventions described in the comment rather than parsing `/adm/users`.
- Modem command handling is highly device-specific and depends on old Hayes/fax behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/telco/telco.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/telco/telcodata -->
# File Research: sources/os/plan9/9front/sys/src/cmd/telco/telcodata

This is a tiny rc service script for incoming modem data calls.

Contents:
- Prints: `This is the plan 9 incoming fax line.`
- Prints: `Please do not make data calls to us.`

Integration:
- `telco.c` selects `/bin/service/telcodata` for answered calls where `ATA` reports a normal data connection rather than fax `+FCON`.

Risk notes:
- It does not interact with the modem stream beyond writing the message.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/telco/telcodata -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/telco/telcofax -->
# File Research: sources/os/plan9/9front/sys/src/cmd/telco/telcofax

This is a tiny rc service script for incoming fax calls.

Contents:
- Runs `/bin/aux/faxreceive`.

Integration:
- `telco.c` selects `/bin/service/telcofax` when answering a ring yields fax connection indication `+FCON`.

Risk notes:
- All real fax handling is delegated to `faxreceive`; this script has no local error handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/telco/telcofax -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/test.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/test.c

This is Plan 9 `test` / `[` implementing POSIX-style expression evaluation plus Plan 9 mode predicates.

Expression parser:
- `e()` handles `-o`.
- `e1()` handles `-a`.
- `e2()` handles `!`.
- `e3()` handles primaries, parentheses, unary predicates, binary string/integer/time operators.
- Evaluation is short-circuited by passing `eval` flags into subexpressions.

Supported checks:
- File: `-f`, `-d`, `-r`, `-w`, `-x`, `-e`, `-s`.
- Plan 9 mode bits: `-A` append-only, `-L` exclusive-use, `-T` temporary.
- TTY: `-t [fd]`.
- Strings: `-n`, `-z`, `=`, `!=`.
- Integers: `-eq`, `-ne`, `-gt`, `-lt`, `-ge`, `-le`.
- Time: `-older`, `-ot`, `-nt`.

Implementation helpers:
- `hasmode()`, `isdir()`, `isreg()`, `fsizep()` use `dirstat`.
- `isatty()` compares fd qid to `/dev/cons`.
- `isolder()` parses duration suffixes `y M d h m s`.
- `synbad()` prints syntax errors and exits `"bad syntax"`.

Risk notes:
- `isolderthan()` and `isnewerthan()` names appear inverted relative to common `-ot`/`-nt` expectations: `isolderthan(a,b)` returns `ad->mtime > bd->mtime`, while `isnewerthan(a,b)` returns `ad->mtime < bd->mtime`.
- Unsupported Unix primaries like `-c`, `-b`, `-u`, `-g` always return false.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/test.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/test/patch/basic.in -->
# File Research: sources/os/plan9/9front/sys/src/cmd/test/patch/basic.in

This is a numeric line fixture for patch tests.

Contents:
- 93 lines.
- Starts at `3` and mostly increments through `98`.
- Contains deliberate irregularities: repeated `13`, `12`, missing ranges, and jumps around `39` to `42` and `86` to `88`.

Purpose:
- Serves as an input baseline for a basic patch application test where line identity is simple and visually verifiable.

Risk notes:
- No code or parser logic; correctness is exact fixture content.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/test/patch/basic.in -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/test/patch/header.in -->
# File Research: sources/os/plan9/9front/sys/src/cmd/test/patch/header.in

This is a numeric fixture for patch header parsing tests.

Contents:
- Identical numeric sequence to `basic.in`.
- 93 lines of small decimal numbers with deliberate repeats and gaps.

Purpose:
- Provides stable input for testing patch behavior involving headers while keeping file content simple.

Risk notes:
- Exact duplication with `basic.in` is likely intentional for test isolation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/test/patch/header.in -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/test/patch/multifile1.in -->
# File Research: sources/os/plan9/9front/sys/src/cmd/test/patch/multifile1.in

This is the first input file for a multifile patch test.

Contents:
- Same 93-line numeric sequence as `basic.in`.
- Contains repeated and missing values to make patch edits easy to inspect.

Purpose:
- Used with `multifile2.in` to test patches that modify more than one file.

Risk notes:
- Fixture file only; no executable behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/test/patch/multifile1.in -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/test/patch/multifile2.in -->
# File Research: sources/os/plan9/9front/sys/src/cmd/test/patch/multifile2.in

This is the second input file for a multifile patch test.

Contents:
- 21 lines.
- Decimal values from `77777` through `77797`.

Purpose:
- Distinct large-number sequence makes it easy to verify that a multifile patch touched the intended second file.

Risk notes:
- Fixture file only; exact line ordering is the contract.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/test/patch/multifile2.in -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/test/patch/rej.in -->
# File Research: sources/os/plan9/9front/sys/src/cmd/test/patch/rej.in

This is a numeric fixture for patch rejection tests.

Contents:
- 93 lines.
- Similar to `basic.in`, but differs at key locations: includes `16` where the basic fixture has `13`, and ends with repeated `96`.

Purpose:
- Designed to create context mismatches or rejected hunks when applying a patch made for a slightly different input.

Risk notes:
- Fixture value lies in exact differences from sibling `.in` files.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/test/patch/rej.in -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/time.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/time.c

This is Plan 9 `time`, executing a command and reporting user, system, and real time.

Behavior:
- Requires at least one command argument.
- Forks; child execs `argv[1]`, and if not absolute/relative, retries `/bin/<cmd>`.
- Parent waits, tolerating interrupted `wait()` calls.
- Prints `<user>u <sys>s <real>r` followed by up to several command arguments.
- Appends `# status=...` when child wait message is non-empty.
- Exits with the child wait message.

Helpers:
- `add()` appends formatted fields to a global output buffer.
- `notifyf()` continues on interrupt.
- `error()` reports syscall failures and exits.

Risk notes:
- `add()` has an old-style undeclared `static beenhere=0`; Plan 9 C accepts this style, but it is non-modern C.
- Output buffer is fixed at 4096 bytes, with `vseprint()` preventing overflow.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/time.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/timepic.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/timepic.c

`timepic.c` converts `.TPS` timing-diagram blocks into pic `.PS/.PE` drawing commands while passing other input lines through.

Data model:
- `Symbol`: named numeric expression bindings.
- `Event`: timestamp, value type, optional data label, optional vertical marker line.
- `Signal`: signal name and event list.

Parsing:
- `lex()` tokenizes commands, symbols, numbers, strings, punctuation, and EOF.
- `expr()`, `term()`, and `factor()` implement arithmetic expressions.
- `assign()` binds numeric symbols.
- `events()` parses event timelines, relative `+` offsets, repeats with `{...}`, labels, and marker `|`.
- `signal()` parses one signal definition.

Rendering:
- `.TPS width rowheight` starts a diagram.
- `.TPE` ends it.
- `sigout()` renders each signal as high/low/z/unknown/multivalue waveforms.
- `slantfill()` draws diagonal fill for unknown (`x`) intervals.
- `diagram()` computes extents and emits pic output.

Integration:
- `main()` processes stdin or each file.
- Non-`.TPS` input is copied unchanged.

Risk notes:
- `cleansym()` frees `Event` nodes but not `Event.data`, unlike `freeev()`; this is a small leak per diagram.
- Error reporting is non-fatal; parser often continues after reporting syntax problems.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/timepic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tl/asm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tl/asm.c

`asm.c` is the ARM code and object-image emitter for `tl`, the Plan 9 ARM linker.

Major responsibilities:
- `entryvalue()` resolves numeric or symbolic entry point addresses.
- `asmb()` emits text, string literals, data, symbols, line tables, Thumb maps, dynamic metadata, and final executable headers.
- Output helpers `cput`, `wput`, `hput`, `lput`, `lputl`, and `cflush` manage buffered endian-specific writes.
- `asmsym()` and `putsymb()` emit Plan 9 symbol records.
- `asmlc()` emits compressed line-number tables.
- `asmthumbmap()` records Thumb code ranges.
- `datblk()` materializes initialized data and string blocks.

Instruction emission:
- `asmout()` maps `Optab.type` cases to ARM machine words.
- Handles arithmetic, moves, branches, loads/stores, halfword ops, floating point ops, switch/case ops, relocatable address loads, and ARM/Thumb interworking branch forms.
- Emits one to six 32-bit words depending on selected expansion size.
- `oprrr()`, `opbra()`, `olr()`, `olhr()`, `osr()`, `oshr()`, `olrr()`, `olhrr()`, `ofsr()`, and `omvl()` build instruction encodings.

File format support:
- Header type `0`: raw/no header.
- `1`: AIF/RISC OS.
- `2`: Plan 9.
- `3`: NetBSD boot.
- `4`: IXP1200 raw.
- `5`: iPAQ boot.

Risk notes:
- Many cases assume `span()` and `oplook()` have already selected valid expansions; errors here are often reported as diagnostics but output may continue until `errorexit`.
- `datblk()` detects multiple initialization except for `AINIT`/`ADYNT`, and does relocation handling for DLM mode.
- Thumb interworking behavior is controlled by `CALLEEBX` and symbol flags `thumb`, `foreign`, and `fnptr`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tl/asm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tl/compat.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tl/compat.c

This file only includes linker headers:

- `#include "l.h"`
- `#include "../cc/compat"`

Purpose:
- Pulls shared compiler compatibility support into the `tl` build.

Risk notes:
- The include path lacks `.h` on `../cc/compat`, matching Plan 9 source conventions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tl/compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tl/l.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tl/l.h

`l.h` is the central shared header for the ARM linker.

Core types:
- `Adr`: instruction operand/address, with offset/string/IEEE payload and symbol/auto references.
- `Prog`: linked instruction record with operands, branch condition target, pc, line, opcode, condition, register, and cached class data.
- `Sym`: linker symbol with type, version, value, signature, Thumb/interworking flags, and use lists.
- `Autom`: automatic variable/history metadata.
- `Optab`: instruction selection table row.
- `Oprang`, `Count`, and `Use`: opcode ranges, counters, and symbol-use records.

Key constants:
- Symbol types: `STEXT`, `SDATA`, `SBSS`, `SXREF`, `SLEAF`, `SUNDEF`, import/export types, etc.
- Operand classes: register, constants, branches, autos, externs, Thumb-specific classes, floating constants, etc.
- Mark flags: `FOLL`, `LABEL`, `LEAF`.
- Linker sizes and limits: `NHASH`, `NHUNK`, `MINSIZ`, `MAXIO`, `MAXHIST`.

Globals:
- Declares all shared linker state: text/data sizes, segment origins, debug flags, hash table, program lists, symbol output sizes, architecture flags, import/export state, opcode tables, etc.
- `EXTERN` toggles between declaration and definition; `obj.c` defines `EXTERN` before including this header.

Function prototypes:
- Covers all major phases: object load, data layout, patching, follow, noops, span, emit, formatting, import/export, Thumb helpers, and ARM encoding helpers.

Risk notes:
- Global mutable state is pervasive; phase ordering is critical.
- `CALLEEBX` is defined here and changes interworking code generation across multiple files.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tl/l.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tl/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tl/list.c

`list.c` provides formatting and diagnostics for linker internal instructions and operands.

Functions:
- `listinit()` installs formatters `%A`, `%C`, `%D`, `%P`, `%S`, and `%N`.
- `prasm()` prints a `Prog`.
- `Pconv()` formats full instructions.
- `Aconv()` formats opcodes through `anames`.
- `Cconv()` formats ARM condition suffixes and condition bits.
- `Dconv()` formats operands by `Adr.type`.
- `Nconv()` formats symbol/name addressing modes.
- `Sconv()` escapes string constants.
- `diag()` prints an error in current text context and aborts after too many errors.

Integration:
- Used throughout `tl` debug output and diagnostics.
- Depends on `curp`, `curtext`, `anames`, and IEEE conversion helpers.

Risk notes:
- Diagnostic count threshold is 10 before `errorexit()`.
- Formatting relies on global `curp` for branch target display.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tl/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tl/noop.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tl/noop.c

`noop.c` rewrites pseudo-instructions and normalizes instruction streams before span/code emission.

Main phase:
- `noops()`:
  - Finds leaf functions.
  - Computes frame and become sizes.
  - Removes NOPs.
  - Expands `RET` and `BECOME`.
  - Emits prologues/epilogues.
  - Handles Thumb stack/register constraints.
  - Rewrites division/modulo pseudo-ops into helper calls.
  - Converts some branch-through-register forms for Thumb/ARM interworking.

Helpers:
- `movrr()` builds register moves.
- `fnret()` emits return via `MOVW` or `ABXRET`.
- `aword()` / `adword()` inject raw words/dwords.
- `nocache()` clears cached operand class/op selection.

Division support:
- `initdiv()` resolves `_div`, `_divu`, `_mod`, `_modu`.
- `setdiv()` marks helper symbols as foreign when ARM/Thumb domains differ.
- `divsig()` and `sigdiv()` set internal signatures for helper symbols.
- `sdiv()` marks dynamic imports for DLM mode.

Risk notes:
- Thumb interworking code is complex and depends on `seenthumb`, `foreign`, `fnptr`, and `CALLEEBX`.
- Some become paths explicitly diagnose unsupported foreign/Thumb cases.
- Division expansion assumes stack layout and helper calling convention.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tl/noop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tl/obj.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tl/obj.c

`obj.c` is the `tl` linker driver and object/archive loader.

Driver flow:
- `main()` parses flags, selects output format, initializes tables/state, opens output, loads objects, loads libraries, handles import/export mode, and runs phases:
  `patch`, profiling, `reachable`, `dodata`, `fnptrs`, `follow`, `noops`, `span`, `asmb`, `undef`.
- Supports `-o`, `-E`, `-T`, `-D`, `-R`, `-H`, `-x`, `-u`, and debug-letter flags.
- Defaults output to `5.out`.

Object/archive loading:
- `isobjfile()` distinguishes object/archive inputs for option parsing.
- `objfile()` handles `-l` library names, regular object files, and Plan 9 archives.
- `loadlib()` repeatedly loads autolibs until unresolved externs stop changing.
- `ldobj()` decodes Plan 9 ARM object records, names, signatures, history, text/data directives, float constants, and branch offsets.
- `zaddr()` decodes serialized `Adr` operands and records autos/params.

Symbol/data helpers:
- `lookup()` interns symbols by name/version.
- `prg()` allocates initialized `Prog` records.
- `addhist()`, `histtoauto()`, `collapsefrog()`, `addlib()` manage history/autolib metadata.
- `nopout()` rewrites skipped duplicate text into NOP.
- `nuxiinit()`, `ieeedtof()`, `ieeedtod()` handle endian and floating conversions.
- `readundefs()` reads import/export symbol lists.

Profiling:
- `doprof1()` injects counter increments into text.
- `doprof2()` injects `_profin` and `_profout` calls.

Risk notes:
- Object decoding is tightly coupled to Plan 9 `.5` object encoding.
- Archive symbol table format is assumed; stale archives trigger diagnostics.
- Duplicate `TEXT` with `DUPOK` is skipped by NOPing instructions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tl/obj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tl/optab.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tl/optab.c

`optab.c` defines the ARM instruction selection table for `tl`.

Contents:
- `Optab optab[]` rows mapping:
  - opcode (`as`)
  - operand classes (`a1`, `a2`, `a3`)
  - emitter type number
  - emitted size
  - default base register parameter
  - flags such as `LFROM`, `LTO`, `LPOOL`, and `V4`

Coverage:
- Text pseudo-ops.
- ALU/register/immediate operations.
- Branch and branch-link forms.
- Loads/stores with small/large offsets.
- Byte/halfword moves and ARMv4 halfword ops.
- Floating-point loads/stores/arithmetic.
- Case/switch support.
- Relocatable address forms.
- Interworking forms `ABX` and `ABXRET`.

Integration:
- Consumed by opcode table builders and `oplook()`.
- `asmout()` interprets the `type` field to emit actual ARM words.

Risk notes:
- Table order matters for pattern matching.
- Sizes must match `asmout()` expansion exactly or phase errors and corrupted output can result.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tl/optab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tl/pass.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tl/pass.c

`pass.c` implements linker middle-end passes: data layout, branch patching, code following, reachability pruning, function-pointer interworking optimization, and import/export table generation.

Data layout:
- `dodata()` validates data initializers, marks function-pointer references, optionally pulls string constants, assigns small data first, then large data, then BSS.
- Defines synthetic symbols `setR12`, `bdata`, `edata`, `end`, and `etext`.

Branch/control-flow:
- `undef()` reports unresolved externs.
- `brchain()` follows unconditional branch chains.
- `relinv()` inverts conditional branch opcodes.
- `follow()` and `xfol()` reorder code for fallthrough, copy short already-followed paths, and invert branches to improve layout.
- `patch()` resolves branch symbols/offsets, marks ARM/Thumb foreign calls, handles `SUNDEF` dynamic reloc branches, and finalizes `cond` pointers.
- `mkfwd()` builds skip-forward pointers to accelerate pc-to-prog lookup.
- `brloop()` detects branch loops.

Utilities:
- `atolwhex()` parses decimal, octal, hex, and signed numeric strings.
- `rnd()` rounds offsets to alignment.

Reachability:
- `reachable()` starts from entry and required division helpers, marks reachable text/data symbols through operand references, removes unused text/data, and marks unused symbols `SREMOVED`.

Function pointer optimization:
- `fused()`, `ckfpuse()`, `setfpuse()`, `cksymuse()`, `ckuse()`, and `setuse()` analyze function pointer uses.
- `fnptrs()` can simplify some indirect `BX O(R)` uses back to `BL O(R)` when all uses stay within a compatible ARM/Thumb domain.

Dynamic import/export:
- `import()` converts selected signed unresolved symbols into `SUNDEF` imports.
- `ckoff()` validates relocation offsets.
- `newdata()` creates synthetic data records.
- `export()` builds `_exporttab` plus `.string` storage for exported symbol signatures, addresses, and names.

Risk notes:
- `reachable()` has a suspicious path when removing unused data: after removing from the head, it later uses `prevt->link`, which assumes `prevt` is non-nil.
- Function-pointer simplification is conservative by default but can be relaxed with debug flag `F`.
- Import/export layout depends on `Roffset`/`Rindex` bit packing from `l.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tl/pass.c -->