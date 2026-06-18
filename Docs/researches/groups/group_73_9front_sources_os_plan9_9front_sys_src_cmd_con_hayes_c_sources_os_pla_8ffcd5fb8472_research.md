# Group Research: group_73_9front_sources_os_plan9_9front_sys_src_cmd_con_hayes_c_sources_os_pla_8ffcd5fb8472

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/con/hayes.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/con/hayes.c

Small Hayes-compatible modem dialer. It opens a data device, optionally opens the matching `ctl` file, initializes the modem with `ATZ`, `ATQ0V1E1M1`, and `ATW1`, then dials with pulse or tone via `ATD%c%s`.

Important behavior:
- `readmsg()` polls the file length with `dirfstat()` and reads modem result lines until timeout.
- Known responses classify as `Ok`, `Success`, `Failure`, or `Noise`.
- `getspeed()` parses `CONNECT <baud>` and defaults to 9600.
- `setspeed()` writes baud and modem flow-control commands to the ctl file when present.
- Errors are fatal through `punt()`, which prints `hayes:` messages and exits.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/con/hayes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/con/xmr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/con/xmr.c

XMODEM receiver writing fixed 128-byte data blocks to a named output file. It enables raw console mode, sends an initial `Nak`, receives `Soh` blocks, validates sequence/complement/checksum, writes payloads, and acknowledges valid blocks.

Important behavior:
- Handles `Eot` by acknowledging and ending, `Cancel` by aborting.
- `readupto()` tolerates partial reads and supports alarm-based timeouts.
- Invalid blocks trigger resynchronization by searching for the next `Soh`.
- Duplicate previous sequence numbers are acknowledged without rewriting.
- Debug mode dumps resync details to stderr.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/con/xmr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/con/xms.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/con/xms.c

XMODEM sender. It opens an input file, enables raw console mode, waits for receiver readiness (`Nak` for checksum or `C` for CRC mode), then sends 128-byte or 1024-byte packets.

Important behavior:
- Options: `-d` debug, `-p` progress, `-1` 1K blocks.
- Builds `Soh` or `Stx` packets with sequence and complement bytes.
- Supports classic additive checksum and CRC-16 via `updcrc()`.
- `send()` retries packets up to 10 times until `Ack`, then reports failure.
- `errorout()` sends `Cancel`, restores raw mode, and exits.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/con/xms.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cp.c

Plan 9 `cp` implementation for file-to-file and file-to-directory copying. It rejects directory sources and detects source/destination identity via qid, dev, and type.

Important behavior:
- Options: `-x` preserves mode and mtime, `-g` preserves gid, `-u` preserves uid and gid.
- Uses `iounit()` or `IOUNIT` to size the copy buffer.
- Copies using plain `read()`/`write()` loop in `copy1()`.
- Creates destination with source permission bits masked to `0777`.
- Metadata preservation uses `dirfwstat()` after successful content copy.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cpp/cpp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cpp/cpp.c

Main control loop for the Plan 9 C preprocessor. It initializes token rows, lexical tables, command-line setup, hidesets, line directives, and then processes token rows until EOF.

Important behavior:
- `process()` reads lines into token rows, routes `#` lines to `control()`, expands macros, suppresses skipped conditional lines, and emits output.
- `control()` implements directives including `define`, `undef`, `include`, conditionals, `line`, `error`, `warning`, `pragma once`, and `eval`.
- Tracks nested `#if` state globally and per include source.
- `#pragma once` stores file identity using qid/type/dev in `incblocked`.
- `error()` formats source stack diagnostics and handles warning/error/fatal severity.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cpp/cpp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cpp/cpp.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cpp/cpp.h

Shared declarations for the preprocessor. Defines token kinds, keyword kinds, token rows, source stack frames, macro symbol records, include tracking, and global state.

Important elements:
- `Token` carries type, flags, hideset index, whitespace length, token length, and text pointer.
- `Tokenrow` is the mutable token sequence abstraction used by lexer, expander, and output.
- `Source` tracks file/string input buffers and include nesting.
- `Nlist` stores macro values, arguments, keyword values, and flags.
- Constants bound preprocessor sizes: include dirs, `#pragma once` entries, macro args, input/output buffers, and `#if` depth.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cpp/cpp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cpp/eval.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cpp/eval.c

Evaluator for `#if`, `#elif`, `#ifdef`, and `#ifndef`. It uses a shunting-yard style operator/value stack with Plan 9 `vlong` values and simple signed/unsigned/undefined type tracking.

Important behavior:
- Temporarily activates special `defined` handling before macro expansion.
- Supports arithmetic, relational, shift, logical, unary, comma, and ternary operators.
- Treats ordinary undefined names as zero; `NAME1` from `defined` tests symbol presence.
- Parses decimal/octal/hex integer constants and character constants, including escapes and UTF runes.
- Division/modulo by zero and undefined logical paths propagate an undefined expression state.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cpp/eval.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cpp/hideset.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cpp/hideset.c

Macro hideset table used to prevent recursive macro re-expansion. A hideset is a sorted, null-terminated array of `Nlist*`, referenced by index from tokens.

Important behavior:
- Hideset 0 is the empty set.
- `newhideset()` inserts a macro into an existing set, interns identical sets, and grows the global set table.
- `unionhideset()` repeatedly adds all symbols from one hideset into another.
- `checkhideset()` tests membership and aborts on invalid indices.
- Maximum per-set size is constrained by `HSSIZ`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cpp/hideset.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cpp/include.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cpp/include.c

Include-file handling and generated line directives for cpp. It supports quoted includes, angled includes, macro-expanded include operands, dependency output, and `#pragma once`.

Important behavior:
- Searches absolute paths directly; quoted includes first search the current file directory.
- Include directories are searched from high index to low and may be marked `always` or deleted.
- Angled includes skip non-`always` entries until fallback current-directory lookup.
- `incblocked` prevents re-including files already seen by `#pragma once`.
- `genline()` emits `#line <n> "<path>"`, optionally prefixing the working directory for relative paths.
- `setobjname()` formats dependency target names for `-M`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cpp/include.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cpp/lex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cpp/lex.c

Lexer for cpp. It encodes a compact finite-state machine and expands it into a `bigfsm[256][MAXSTATE]` table for tokenization speed.

Important behavior:
- Recognizes C preprocessing tokens: names, numbers, strings, char constants, comments, whitespace, operators, newlines, and EOF.
- Supports UTF byte sequences as identifier characters.
- Handles backslash-newline line folding, including ignored carriage returns before newline.
- Converts comments to whitespace while tracking line increments.
- `setsource()` loads an entire file or string into memory and appends EOFC sentinels.
- `gettokens()` fills a token row through newline or END and reports whether possible macro names were seen.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cpp/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cpp/macro.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cpp/macro.c

Macro definition and expansion engine. It handles object-like macros, function-like macros, variadic macros, argument gathering, `#` stringification, `##` token pasting, builtin macros, and hideset propagation.

Important behavior:
- `dodefine()` parses macro names, parameters, duplicate names, ellipsis, and replacement rows.
- `doadefine()` supports command-line `-D` and `-U`.
- `expandrow()` scans token rows and expands normal or builtin macros unless hidden by a token hideset.
- `gatherargs()` can extend token rows across newlines while collecting balanced argument lists.
- `substargs()` expands arguments normally except around stringification/pasting cases.
- `glue()` re-lexes pasted token text and warns if it does not form one valid token.
- Builtins implement `__LINE__`, `__FILE__`, `__DATE__`, and `__TIME__`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cpp/macro.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cpp/nlist.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cpp/nlist.c

Symbol table and command-line setup for cpp. It installs preprocessor keywords and builtin macros, constructs include search paths, parses options, opens input/output, and initializes the source stack.

Important behavior:
- Symbol table is a 128-bucket chained hash keyed by token bytes.
- `quickset`/`quicklook` accelerate “might be macro” checks using first two name bytes.
- Default include paths are `/$objtype/include` and `/sys/include`; `$include` can add more.
- Options include `-I`, `-D`, `-U`, `-M`, `-V`, `-P`, `-N`, `-.`, and ignored `+`.
- `setup()` installs current-directory include behavior and calls `setsource()` for the input.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cpp/nlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cpp/test/edges.in -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cpp/test/edges.in

Cpp edge-case test input focused on macro expansion semantics. It is not C code meant for compilation; it exercises preprocessor output behavior.

Important coverage:
- `##` with empty left/right arguments.
- Nested token pasting and expansion ordering.
- Variadic macros with and without `__VA_ARGS__`.
- Comma expansion inside macro arguments.
- C standard complex macro examples involving self-reference/hidesets.
- Empty argument stringification and token pasting.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cpp/test/edges.in -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cpp/tokens.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cpp/tokens.c

Token-row storage, copying, insertion, whitespace normalization, output buffering, and debug printing for cpp.

Important behavior:
- `maketokenrow()`/`growtokenrow()` manage dynamic token arrays.
- `insertrow()` replaces tokens at the current cursor and normalizes whitespace on both sides.
- `makespace()` prevents accidental token merging after macro expansion.
- `normtokenrow()` deep-copies token text and canonicalizes leading whitespace availability.
- `puttokens()` coalesces contiguous token text into a buffered writer unless dependency mode suppresses output.
- `setempty()` reduces a row to a newline token for skipped/control lines.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cpp/tokens.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/crc32.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/crc32.c

Configurable CRC-32 calculator. It builds a 256-entry table from a polynomial and computes checksums over stdin or named files.

Important behavior:
- Defaults: reflected CRC polynomial `0xedb88320`, initial value 0, final xor `-1`.
- Options: `-x xorval`, `-i initial`, `-p poly`.
- `sum()` streams data in `IOUNIT` chunks and prints either just the CRC or `CRC<TAB>filename`.
- Read/open failures set the process exit string but processing continues for later files.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/crc32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/crop.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/crop.c

Plan 9 image crop utility using `draw`/`memdraw`. It reads an image, computes or applies a rectangle transform, fills a new image, draws the selected region, adjusts origin, and writes the result.

Important behavior:
- Options support background fill color, automatic blank-color crop, uniform inset, x/y insets, absolute rectangle, and translation.
- Auto crop converts non-`RGBA32` images to temporary RGBA for simple pixel comparison.
- The crop color and background color are encoded as `R<<24|G<<16|B<<8|0xFF`.
- Output origin is shifted by adjusting `new->r` and `new->zero`.
- Fatal errors use `sysfatal()`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/crop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/32bit.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/32bit.h

On-disk layout constants for old 32-bit-compatible cwfs builds.

Important details:
- `NAMELEN=28`, `NDBLOCK=6`, `NIBLOCK=2`.
- `Off` is `long`.
- Defines `COMPAT32`.
- `swaboff` maps to `swab4`.
- Comments warn that changing these values breaks disk compatibility and 9P1 compatibility.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/32bit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/64bit.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/64bit.h

64-bit cwfs on-disk layout constants.

Important details:
- `NAMELEN=56`, `NDBLOCK=6`, `NIBLOCK=4`.
- `Off` is `vlong`.
- Undefines `COMPAT32`.
- `swaboff` maps to `swab8`.
- This layout is intentionally incompatible with old 32-bit filesystems.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/64bit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/64xbit.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/64xbit.h

Extended-name 64-bit cwfs layout variant.

Important details:
- `NAMELEN=144`, `NDBLOCK=6`, `NIBLOCK=4`.
- `Off` is `vlong`.
- Undefines `COMPAT32`.
- `swaboff` maps to `swab8`.
- It trades compatibility for much longer directory component names.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/64xbit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/9netics32.16k/conf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/9netics32.16k/conf.c

Build-specific runtime defaults for a 9netics 32-bit, 16K-block cwfs instance.

Important behavior:
- Sets `fs_mktime` from `DATE`.
- Declares a `main` start superblock at block 2.
- `localconfinit()` disables dump-read-reread, sets no first/recovery superblock override, and sizes large/small message pools.
- Protocol table exposes only `serve9p2`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/9netics32.16k/conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/9netics32.16k/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/9netics32.16k/dat.h

Build configuration header for 9netics 32-bit, 16K-block cwfs.

Important details:
- Defines `RBUFSIZE` as `16*1024` unless already supplied.
- Includes `32bit.h`.
- Sets `FIXEDSIZE=1`, assuming equal-sized optical media.
- Includes common `portdat.h`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/9netics32.16k/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/9netics64.8k/conf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/9netics64.8k/conf.c

Build-specific runtime defaults for a 9netics 64-bit, 8K-block cwfs instance.

Important behavior:
- `main` starts at superblock 2.
- `localconfinit()` mirrors the 9netics32 pool/dump defaults.
- Protocol table exposes `serve9p2`; comment notes 64-bit fileservers cannot serve 9P1 correctly because `NAMELEN` is too large.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/9netics64.8k/conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/9netics64.8k/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/9netics64.8k/dat.h

Build configuration header for 9netics 64-bit, 8K-block cwfs.

Important details:
- Defines `RBUFSIZE` as `8*1024`.
- Includes `64bit.h`.
- Sets `FIXEDSIZE=1`.
- Includes shared `portdat.h`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/9netics64.8k/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/9p2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/9p2.c

Primary 9P2000 protocol implementation for cwfs. It translates between 9P requests and cwfs dentries, qids, locks, authentication fids, directory layout, block allocation, and metadata operations.

Important behavior:
- Converts between older cwfs/9P1 mode/qid encoding and 9P2000 `Qid`/`Dir`.
- Implements `version`, `auth`, `attach`, `walk`, `open`, `create`, `read`, `write`, `clunk`, `remove`, `stat`, and `wstat`.
- Uses `File` records keyed by fid and maintains `Wpath` parent chains for `..`, remove, rename, and dump rewalk support.
- Auth fids use factotum RPC through `authnew`, `authread`, and `authwrite`.
- Read/write validate qids, permissions, append/exclusive locks, count bounds, offsets, and read-only devices.
- Directory reads convert live dentries into 9P stat records and maintain cached directory read offsets/slots.
- `wstat` performs detailed validation for qid/mode/name/owner/group/length changes before modifying dentries.
- `serve9p2()` decodes `Fcall`, dispatches, maps cwfs error codes to strings, encodes replies, and sends them to the channel reply queue.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/9p2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/all.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/all.h

Common include and global declaration header for cwfs.

Important elements:
- Pulls in Plan 9 libc, fcall, disk, bio, and IP headers plus generated `dat.h` and `portfns.h`.
- Defines common macros like `CHAT()` and qid helpers.
- Declares global filesystem state: uid/gid tables, locks, time, channels, queues, files, wpaths, flags, devices, superblock starts, and config fields.
- Declares configuration globals such as `service`, `filsys`, `fspar`, read-only/auth/noatime switches, and buffer/file accounting.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/all.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/auth.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/auth.c

Factotum-backed authentication support and config-device stubs.

Important behavior:
- `nvrgetconfig()` returns `conf.confdev`; `nvrsetconfig()` is a no-op success stub here.
- `authnew()` mounts `/srv/factotum` if needed, opens `/mnt/factotum/rpc`, allocates an `AuthRpc`, and starts `proto=p9any role=server`.
- `authread()` advances the auth protocol, returns challenge bytes, and on `ARdone` records the authenticated user id in the `File`.
- `authwrite()` feeds client data into factotum.
- Errors are reported through the channel’s error buffer.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/chk.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/chk.c

Filesystem consistency checker and optional repair tool for cwfs. It walks dentries recursively, validates tags/qids/block ownership, audits or rebuilds free lists, and can repair bad tags/blocks or clear temporary files.

Important behavior:
- Console entry is `cmd_check`.
- Options include `rdall`, `tag`, `pfile`, `pdir`, `free`, `ream`, `bad`, `touch`, `trim`, and `rtmp`.
- Tracks allocated/free/qid bitmaps and reports duplicate, missing, bad, and out-of-range blocks.
- `fsck()` recursively checks direct and indirect blocks, directory contents, names, qids, and temporary files.
- `mkfreelist()` rebuilds normal free lists; `trfreelist()` preserves/free-list-translates cache-worm devices.
- `xtag()` validates block tags and can reset them under selected repair flags.
- Locks `mainlock` for writable checking and disables aging during scans.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/chk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/choline/conf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/choline/conf.c

Site-specific runtime defaults for the `choline` cwfs build.

Important behavior:
- `main` starts at superblock 2.
- `localconfinit()` sets `conf.nfile=60000`, enables dumps, uses `firstsb=12565379`, and sizes message pools.
- Protocol table exposes `serve9p2`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/choline/conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/choline/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/choline/dat.h

Build configuration header for `choline`.

Important details:
- `RBUFSIZE=16*1024`.
- Includes 32-bit on-disk layout.
- Sets `FIXEDSIZE=1`.
- Includes `portdat.h`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/choline/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/con.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/con.c

Interactive console command framework for cwfs. It installs commands/flags, starts a console command loop, and provides administrative actions for filesystems, users, stats, checks, dumps, profiling, and maintenance.

Important behavior:
- `consserve()` initializes console session, selects `main`, loads users, prints version, optionally touches cw superblock, then starts command processing.
- Command registry is sorted and invoked by whitespace-splitting `cmd_exec()`.
- Commands include `allow`, `cfs`, `check`, `clean`, `clri`, `create`, `dump`, `fstat`, `halt`, `remove`, `sync`, `users`, `version`, `who`, `hangup`, `printconf`, and others.
- Flag registry controls global/channel tracing and auth behavior.
- `walkto()` uses console 9P wrapper calls to resolve paths.
- `number()` parses signed vlongs for command arguments.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/con.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/config.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/config.c

Configuration parser, config-block merger, system initializer, and device-copy helper for cwfs. It parses compact device expressions and the persistent config block.

Important behavior:
- Device syntax covers concatenation, interleave, mirrors, fake worm, none, mapped file, wren/worm/labeled worm, ro companion, jukebox, cache-worm, partitions, and byte-swapped devices.
- Supports numeric iteration syntax with `<start-end>`.
- `mergeconf()` reads config block keywords: `service`, auth/noatime/readonly switches, `newcache`, `filsys`, and declared geometry parameters.
- `sysinit()` reads/creates config, fills missing geometry declarations, rewrites modified configs, compiles file system device expressions, reams/recovers/init devices, and optionally copies devices/worms.
- `arginit()` provides interactive boot-time config commands including `config`, `nvram`, `filsys`, `ream`, `recover`, `copyworm`, `copydev`, and policy toggles.
- Copy helpers stream block-by-block and include basic sizing/sanity checks.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/config.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/console.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/console.c

Console-side wrappers around cwfs 9P handlers and low-level destructive/admin helpers.

Important behavior:
- `con_session`, `con_attach`, `con_clone`, `con_walk`, `con_open`, `con_create`, `con_read`, `con_write`, and `con_remove` synthesize `Fcall` structures and call the same 9P operations under `mainlock`.
- `con_create()` injects console uid/gid into global console state before creating.
- `doclri()` clears a dentry directly without normal emptiness checks.
- `con_fstat()` prints raw dentry metadata and block pointers.
- `con_clri()` invokes the direct-clear path.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/console.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/cw.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/cw.c

Cache-worm device implementation. It layers a writable cache device over a worm/read-only backing device and manages copy-on-write state, dumps, cache metadata, recovery, and cw-specific console commands.

Important behavior:
- Cache entry states include `Cnone`, `Cdirty`, `Cdump`, `Cread`, `Cwrite`, `Cdump1`, and `Cerror`.
- `cwio()` is the core state machine for read/write/grow/dump/release/free operations.
- `dumpblock()` copies queued dump entries from cache to worm and updates cache entry state.
- `cwream()` initializes a fresh cache-worm filesystem with cache metadata, superblock, cw root, and ro root.
- `cwrecover()` rebuilds cache metadata from the latest valid worm superblock chain.
- `getcentry()` maps worm addresses to cache buckets and maintains age/resequence state.
- `cfsdump()` recursively snapshots dirty blocks, updates cw and ro roots, creates dated dump directory entries, writes a new superblock, rewrites cache metadata, and rewalks active fids.
- Console `cwcmd` subcommands inspect or mutate cache state, dump chains, cache warm-up files, superblocks, and accounting.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/cw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/cwfs/conf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/cwfs/conf.c

Generic old-cw runtime defaults.

Important behavior:
- `main` starts at superblock 2.
- `localconfinit()` sets `conf.nfile=40000`, enables dumps by default, and sizes message pools.
- Contains a commented read-only jukebox `nodump` setting.
- Protocol table exposes `serve9p2`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/cwfs/conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/cwfs/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/cwfs/dat.h

Generic old-cw data layout header.

Important details:
- `RBUFSIZE=16*1024`.
- Includes `32bit.h`.
- Sets `FIXEDSIZE=1`.
- Includes `portdat.h`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/cwfs/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/cwfs64/conf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/cwfs64/conf.c

Generic old-cw runtime defaults reused for a 64-bit build.

Important behavior:
- Same defaults as `cwfs/conf.c`: `main` at 2, `conf.nfile=40000`, dump enabled, message pool sizing.
- Protocol table exposes `serve9p2`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/cwfs64/conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/cwfs64/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/cwfs64/dat.h

Generic 64-bit cwfs data layout header.

Important details:
- `RBUFSIZE=16*1024`.
- Includes `64bit.h`.
- Sets `FIXEDSIZE=1`.
- Includes `portdat.h`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/cwfs64/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/cwfs64x/conf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/cwfs64x/conf.c

Generic old-cw runtime defaults reused for the extended-name 64-bit build.

Important behavior:
- Same runtime defaults as `cwfs/conf.c`.
- Protocol table exposes `serve9p2`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/cwfs64x/conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/cwfs64x/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/cwfs64x/dat.h

Generic extended-name 64-bit cwfs data layout header.

Important details:
- `RBUFSIZE=16*1024`.
- Includes `64xbit.h`, giving `NAMELEN=144`.
- Sets `FIXEDSIZE=1`.
- Includes `portdat.h`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/cwfs64x/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/data.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/data.c

Static diagnostic string tables for cwfs.

Important contents:
- `errstr9p` maps internal cwfs error codes to 9P error strings.
- `wormscode` maps optical/WORM device sense/error codes to human-readable diagnostics.
- `tagnames` maps block tag enum values to names such as `Tdir`, `Tfile`, `Tfree`, indirect tags, `Tsuper`, `Tvirgo`, and `Tcache`.
- These strings are consumed by 9P error replies, check/debug output, and cache-worm diagnostics.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/data.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/dentry.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/dentry.c

Dentry block-address translation, read-ahead, and truncation support.

Important behavior:
- `getdir()` returns a dentry slot inside an `Iobuf`.
- `accessdir()` updates atime/mtime/muid/qid version and respects `Devro` and `noatime`.
- `rel2abs()` resolves relative file block numbers through direct and multi-level indirect pointers, allocating blocks when a target tag is supplied.
- `dnodebuf()` and `dnodebuf1()` fetch data/dir/indirect blocks by relative index.
- `dbufread()` implements simple sequential read-ahead scheduling.
- `dtrunclen()` shrinks files by freeing blocks past the final retained block and zeroing partial tails.
- `dtrunc()` frees all direct and indirect blocks.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/dentry.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/emelie/conf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/emelie/conf.c

Site-specific runtime defaults for the `emelie` cwfs build.

Important behavior:
- Defines `main` and `old` start superblocks at `SUPER_ADDR`.
- `localconfinit()` sets `conf.nfile=40000` and `conf.nodump=1` because the jukebox is read-only.
- Message pool defaults match old cw builds.
- Protocol table exposes `serve9p2`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/emelie/conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/emelie/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/emelie/dat.h

Build configuration header for `emelie`.

Important details:
- `RBUFSIZE=16*1024`.
- Includes 32-bit layout.
- Sets `FIXEDSIZE=1`.
- Includes `portdat.h`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/emelie/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/fs/conf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/fs/conf.c

Runtime defaults for the `fs` 4K/32-bit build.

Important behavior:
- `main` start superblock is set to `810988`, with a comment noting a discontinuity before block `696262`.
- `localconfinit()` enables dump reread verification and uses large message pools sized for packets.
- Protocol table exposes `serve9p2`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/fs/conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/fs/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/fs/dat.h

Build configuration header for `fs`.

Important details:
- `RBUFSIZE=4*1024`.
- Includes 32-bit layout.
- Sets `FIXEDSIZE=1`.
- Includes `portdat.h`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/fs/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/fs64/conf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/fs64/conf.c

Runtime defaults for the `fs64` 8K/64-bit build.

Important behavior:
- `main` starts at superblock 2.
- `localconfinit()` enables dump reread verification and packet-sized message pools.
- Protocol table exposes `serve9p2`; comment notes 64-bit builds cannot serve 9P1 correctly due to name length.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/fs64/conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/fs64/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/fs64/dat.h

Build configuration header for `fs64`.

Important details:
- `RBUFSIZE=8*1024`.
- Includes 64-bit layout.
- Sets `FIXEDSIZE=1`.
- Includes `portdat.h`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/fs64/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/fworm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/fworm.c

Fake-WORM device adapter. It reserves a bitmap at the end of an underlying device to record which logical blocks have been written, enforcing write-once semantics over a regular block device.

Important behavior:
- `fwormsize()` subtracts bitmap storage from the underlying device size.
- `fwormream()` zeroes and tags bitmap blocks as `Tvirgo`.
- `fwormread()` checks the bitmap before reading; unwritten blocks return an error.
- `fwormwrite()` fails if the block was already marked written, otherwise marks it and writes data.
- Bounds and tag failures panic because they indicate structural corruption or misuse.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/fworm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/io.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/io.h

SCSI and target constants/types for cwfs I/O support.

Important contents:
- Defines maximum SCSI controllers/targets and network count constants.
- Lists SCSI status/sense-like codes such as `STok`, `STcheck`, `STbusy`, `STtimeout`, and controller/blank/nomem errors.
- Defines `Target`, wrapping a Plan 9 `Scsi*`, controller/target ids, inquiry/sense buffers, a lock, textual id, and ok flag.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/iobuf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/iobuf.c

I/O buffer cache implementation for cwfs. It hashes `(Device*, address)` into `Hiob` lists, returns locked mapped buffers, flushes dirty buffers, and validates block tags.

Important behavior:
- `getbuf()` searches active hash chains, promotes hits, evicts oldest unlocked non-reserved buffers, writes dirty victims, and optionally reads from device.
- `Bprobe` returns nil on cache miss without loading.
- Reserved buffers (`Bres`) are not evicted to avoid recursion/deadlock with pseudo devices.
- `syncblock()` writes at most one dirty buffer per hash line per pass; `sync()` repeats until clean or bounded attempts expire.
- `putbuf()` immediately writes `Bimm` buffers, unmaps, and unlocks.
- `checktag()` validates trailer tag/path and prints detailed diagnostics; `settag()` updates tag/path and marks modified.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cwfs/iobuf.c -->