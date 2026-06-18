# Group Research: group_71_9front_sources_os_plan9_9front_sys_src_cmd_cc_funct_c_sources_os_plan_d7f463302a20

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/funct.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cc/funct.c

Implements the Plan 9 C compiler’s `typestr` operator/function rewriting extension.

Key behavior:
- `isfunct` recognizes operators on special struct/union types with `Type.funct` metadata and rewrites them into `OFUNC` calls.
- Supports binary arithmetic/bitwise operators, comparisons, compound assignments, unary operators, and casts to/from scalar types.
- For compound assignments, inserts an address-of left operand so helper functions receive `T*`.
- Validates helper function type compatibility with `tcompat` and argument compatibility with `tcoma`.
- `dclfunct` synthesizes external helper declarations from a generated structure tag naming convention.
- Helper names are generated from `ftabinit` and `gtabinit`, such as `<tag>_add_`, `<tag>_eq_`, `<tag>_asadd_`, and scalar conversion helpers.

Dependencies:
- Uses compiler core types and AST helpers from `cc.h`: `Node`, `Type`, `Sym`, `Funct`, `new`, `typ`, `copytyp`, `dodecl`, `tcomo`, `tcompat`, and `tcoma`.

Research notes:
- This is not ordinary C operator overloading; it is a Plan 9 compiler extension tied to `typestr`.
- Rewrites preserve diagnostics by setting bad nodes to type `T` after reporting failed conversions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/funct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/lex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cc/lex.c

Main driver, input manager, lexer, symbol initialization, include handling, and formatter support for the Plan 9 C compiler.

Key behavior:
- `main` initializes compiler type tables, globals, debug flags, include paths, and command-line options.
- Supports parallel compilation of multiple files using `NPROC`, while avoiding interleaved stdout for acid/pickle output.
- `compile` chooses output file names, configures include paths, opens output buffers, optionally runs `/bin/cpp`, and invokes `yyparse`.
- `newio`, `pushio`, `newfile`, and `filbuf` manage nested file/macro input streams.
- `lookup` and `slookup` maintain the compiler symbol hash table.
- `yylex` handles identifiers, keywords, macros, comments, string/rune literals, numeric constants, operators, and Plan 9 extensions such as binary integer constants.
- Numeric scanning chooses token/type by suffix, signedness, decimal-vs-nondecimal rules, and target widths; emits truncation/widening warnings.
- `escchar` decodes character escapes, including non-ANSI long hex/octal forms used by this compiler.
- `cinit` builds primitive type nodes, installs keywords, initializes `.string`, current path, and custom formatters.
- `Oconv`, `Lconv`, `Tconv`, `FNconv`, `Qconv`, and `VBconv` implement compiler-specific formatting for diagnostics and debug output.
- `setinclude` appends unique include directories from space-separated path strings.

Dependencies:
- Includes `cc.h` and parser tokens from `y.tab.h`.
- Depends on macro expansion routines from included macro support, parser entry `yyparse`, code cleanup `gclean`, and Plan 9 libc/`Bio` routines.

Research notes:
- This file is the compiler’s process and lexical boundary.
- `Lconv` reconstructs include and `#line` history for diagnostics.
- Macro expansion is integrated into the lexer by pushing expanded text onto the same I/O stack.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/mac.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cc/mac.c

Tiny compilation unit that includes shared macro-processing implementation.

Key behavior:
- Includes `cc.h`.
- Includes `"macbody"`, which supplies the actual macro/preprocessor helper code for this compiler build.

Dependencies:
- Depends entirely on `cc.h` and the local `macbody` include file.

Research notes:
- This file is a wrapper, not an implementation body itself.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/mac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/omachcap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cc/omachcap.c

Default machine-capability hook for compiler back ends.

Key behavior:
- Defines `machcap(Node*)` to always return `0`.
- Comment notes this is the default behavior, like old `cc`.

Dependencies:
- Includes `cc.h`.

Research notes:
- Architecture-specific compiler variants can override this hook.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/omachcap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/pgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cc/pgen.c

Portable statement/code generation logic for the Plan 9 C compiler, sitting above machine-specific back-end emission.

Key behavior:
- `codgen` emits function entry pseudo-op, handles complex return values, first register argument movement, reachability diagnostics, final return branch, register optimization, and stack-safe argument area sizing.
- `supgen` generates code in suppressed mode for dead constant branches without preserving emitted instructions.
- `uncomma` evaluates left comma operands before returning the final expression node.
- `gen` handles statement-level AST operations: expression statements, noreturn calls, returns, labels, gotos, cases, switches, loops, `break`, `continue`, `if`, `USED`, and `SET`.
- Tracks `canreach`, `warnreach`, `breakpc`, `continpc`, `nbreak`, and `ncontin` for unreachable-code diagnostics and control-flow patching.
- `OSWITCH` collects cases and delegates table emission to `doswit`.
- `bcomplex` type-checks boolean tests, optionally recognizes constant conditions, and emits boolean branches through `boolgen`.
- `usedset` emits `ANOP` markers to represent variable use/set annotations.

Dependencies:
- Includes `gc.h`.
- Uses back-end hooks such as `gpseudo`, `gbranch`, `patch`, `cgen`, `regalloc`, `regfree`, `regret`, `gmove`, `regopt`, and switch lowering via `doswit`.

Research notes:
- This file owns statement control-flow lowering, not low-level instruction selection.
- Reachability warnings intentionally suppress some habitual or yacc-generated unreachable `break` cases.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/pgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/pickle.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cc/pickle.c

Generates acid/pickle helper output for compiler `-Z` debug/introspection mode.

Key behavior:
- Maintains acid keyword escaping through `pmap`.
- `picklesue` finds the symbol naming a struct/union/enum tag for a type.
- `picklefun` finds the symbol associated with a function type.
- `pickleinit` maps compiler primitive type codes to pickle format characters, adapting `int`/`uint` to target width.
- `picklemember` emits C statements that serialize primitive, pointer, array, struct, and union members.
- `pickletype` emits `pickle_<type>` functions for structs/unions, or structure offset defines under `-s`.
- `picklevar` emits acid declarations for globals, statics, autos, params, and enum constants when `-Z` is active.

Dependencies:
- Includes `cc.h`.
- Writes generated text to `outbuf`.
- Uses compiler symbol hash, current input stack, current function, and type metadata.

Research notes:
- This is compiler-generated debugging/introspection support, not runtime serialization used by compiled programs.
- It deliberately skips nested include contexts when `debug['Z'] > 1`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/pickle.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/pswt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cc/pswt.c

Portable switch lowering helpers, long-string output, unused-result warning helper, and IEEE double conversion.

Key behavior:
- `doswit` collects `case` entries, detects duplicate cases/defaults, sorts case values, and delegates normal switch generation to `swit1`.
- Handles 64-bit switch constants on 32-bit targets by switching first on high words and then on low words.
- `casf` allocates and links a new `Case`.
- `outlstring` emits wide string data respecting target byte order/alignment.
- `nullwarn` emits “result of operation not used” and still generates operand side effects.
- `ieeedtod` converts a native double into the compiler’s `Ieee` high/low representation.

Dependencies:
- Includes `gc.h`.
- Depends on back-end `swit1`, branch patching, string emission, and target alignment helpers.

Research notes:
- The switch code preserves signed-vs-unsigned behavior by tracking whether the expression/cases require vlong handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/pswt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/scon.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cc/scon.c

Constant evaluation and additive expression reassociation for the Plan 9 C compiler.

Key behavior:
- `evconst` folds constant unary, binary arithmetic, logical, comparison, bitwise, cast, and shift operations.
- Emits warnings for divide/modulo by zero and float overflow/truncation paths handled elsewhere.
- `acom` rewrites integer additive/multiplicative expression trees into better grouped forms when safe.
- `acom1` decomposes additive expressions into coefficient terms plus constant.
- `acom2` factors and rebuilds expression trees, including constant-plus-address forms and coefficient factoring.
- `acast` inserts casts when reconstructed terms need target type conversion.
- `addo` decides whether an expression can safely participate in additive reassociation without changing overflow or unsigned semantics.

Dependencies:
- Includes `cc.h`.
- Uses compiler global `term`/`nterm`, type classification tables, `convvtox`, AST constructors, and diagnostics.

Research notes:
- Optimization is conservative around floating-point, vlong width, unsigned casts, and bit-field casts.
- This is source-tree-level expression simplification before machine-specific generation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/scon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/sub.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cc/sub.c

Large compiler utility module for AST creation/printing, type construction, type compatibility, structure member lookup, conversions, diagnostics, reachability helpers, and miscellaneous semantic utilities.

Key behavior:
- `new`/`new1` allocate AST nodes and assign source line numbers.
- `prtree`/`prtree1` print annotated ASTs for debugging.
- `typ`, `copytyp`, `garbt`, `simpleg`, `simplec`, and `simplet` construct and classify compiler types from parsed specifiers.
- `stcompat`/`tcompat` validate type compatibility tables and emit diagnostics.
- `dotsearch`, `dotoffset`, and `makedot` support named and unnamed struct/union field access, including bit-field and embedded-structure extensions.
- `constas` warns about assignment through `const`-qualified types.
- `typeext` inserts implicit extensions for null pointer constants, float constant lowering, and unnamed-substructure assignment/address conversions.
- `nocast` and `nilcast` classify no-code and semantically no-op casts.
- `arith` implements usual arithmetic conversions and pointer arithmetic scaling/differencing.
- Includes helpers for shift simplification, rotate/or transforms, side-effect detection, constant classification, log2/top-bit utilities, relational constant folding, condition inversion, bit lookup, type bit merging, diagnostics, type initialization, dead-head reachability scans, mixed assignment-op checks, and unsigned-comparison casts.

Dependencies:
- Includes `cc.h`.
- Uses many compiler global tables: type width/classification arrays, compatibility tables, operator names, diagnostics state, and parser/compiler symbols.

Research notes:
- This file is the semantic glue for the compiler front end.
- It contains Plan 9 C extensions for unnamed substructures and target-width-aware pointer arithmetic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/sub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cdfs/buf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cdfs/buf.c

Buffered block I/O wrapper for `cdfs` track reading and writing.

Key behavior:
- `bopen` allocates a `Buf`, block buffer, and optional internal cache sized by block size and number of blocks.
- `bread` services arbitrary byte reads from block-oriented media by reading whole blocks through the device callback, caching aligned data, and copying requested byte ranges.
- `bwrite` buffers byte writes into full blocks and calls the write callback when the buffer fills.
- `bterm` flushes pending writes and frees buffer state.

Dependencies:
- Includes Plan 9 libc, disk headers, `dat.h`, and `fns.h`.
- Uses the callback stored in `Buf.fn`, normally MMC read/write routines.

Research notes:
- This layer bridges 9P byte-oriented reads/writes and MMC sector-oriented I/O.
- Short final writes depend on `bterm`/close to flush buffered data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cdfs/buf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cdfs/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cdfs/dat.h

Shared data model and constants for the CD/DVD/BD file server.

Key definitions:
- Media constants for track counts, CD/DVD/BD block sizes, SCSI peripheral types, MMC media types, track types, writability classes, and tri-state flags.
- MMC mode-page offsets and bits for capabilities, write parameters, track modes, data block types, session formats, cache controls, and close-track/session commands.
- `Msf` stores minute/second/frame positions.
- `Track` stores discovered track size, block size, block range, type, MSF boundaries, name, mode, and mtime.
- `Otrack` represents an open track with drive pointer, mode, buffer, change generation, and refcount.
- `Dev` is a method table for drive operations: open, create, read, write, close, TOC refresh, fixate, control, and speed control.
- `Drive` embeds `QLock` and `Scsi` plus media state, tracks, speed information, and device operation table.
- `Buf` stores block-buffering state around an `Otrack`.

Dependencies:
- Requires Plan 9 `Scsi`, `QLock`, and disk/libc types from including compilation units.

Research notes:
- `Drive` is the core cross-file object shared by the 9P server and MMC command layer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cdfs/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cdfs/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cdfs/fns.h

Shared function declarations for `cdfs`.

Key declarations:
- Buffer API: `bopen`, `bread`, `bwrite`, `bterm`, `bufread`, `bufwrite`.
- Utility/API declarations: `disctype`, `emalloc`, `geterrstr`, and `mmcprobe`.

Dependencies:
- Uses `Buf`, `Otrack`, `Drive`, and `Scsi` types from `dat.h` and included system headers.

Research notes:
- This header is intentionally small and only exposes cross-module entry points.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cdfs/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cdfs/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cdfs/main.c

9P file server presenting CD/DVD/BD drive contents as a filesystem.

Key behavior:
- Exposes root directory, `ctl`, writable audio/data directories `wa`/`wd`, and one file per discovered track.
- `fsattach`, `fsclone`, `fswalk1`, `fsopen`, `fsread`, `fswrite`, `fscreate`, `fsremove`, `fsstat`, and `fsdestroyfid` implement the lib9p server interface.
- `checktoc` refreshes the table of contents and synthesizes track names such as `aNNN`, `dNNN`, `uNNN`, or hidden blank entries.
- `readctl` reports CDDB query data for audio discs, current/max speeds, media type, and next writable sector.
- `writectl` parses speed control commands and passes other control commands to the drive backend.
- Track reads/writes are delegated through `Otrack` and `Buf`.
- `fscreate` creates new writable audio/data tracks under `wa`/`wd`.
- Removing `wa`/`wd` triggers disc fixation.
- `main` opens an SCSI device, probes it through `mmcprobe`, refreshes TOC, and mounts the 9P service.

Dependencies:
- Uses Plan 9 `thread`, `9p`, `disk`, SCSI/MMC backend, and local `dat.h`/`fns.h`.

Research notes:
- This is the user-visible filesystem boundary for optical media.
- Directory qid versions are tied to drive media-change generation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cdfs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cdfs/mmc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cdfs/mmc.c

MMC/SCSI optical drive backend for `cdfs`, supporting CD/DVD/BD probing, reading, writing, blanking, speed setting, and fixation.

Key behavior:
- Builds SCSI CDBs for mode sense/select, inquiry, start unit, read TOC, read disc/track info, read disc structure, read/write, reserve track, close track/session, synchronize cache, blank, format, and speed control.
- `mmcprobe` validates an MMC device, learns capabilities, caches write-parameter mode page 5 when available, configures cache behavior, and fills the drive method table.
- `mmcgettoc` handles media-change detection, blank-disc probing, disc type inference, DVD/BD structure reads, writeability flags, track discovery, and TOC-derived MSF data.
- `mmctrackinfo` reads per-track metadata, determines audio/data/blank type, computes block ranges/sizes, and tracks next writable address.
- `mmcinfertracks` infers track ends from successive TOC entries for non-writing drives.
- `mmcopenrd` opens a read track and creates a block buffer.
- `mmcread` reads sectors using `READ CD` for non-data CD tracks and `READ(12)` otherwise, truncating at track end.
- `mmccreate`, `mmcxwrite`, `mmcwrite`, `reserve`, `mmcclose`, and `mmcfixate` manage writable track creation, sector writes, cache sync, track/session close, and TOC refresh.
- `mmcblank`, `format`, `mmcctl`, and `mmcsetspeed` implement control operations.
- Tracks aggregate total written bytes/blocks for diagnostics.

Dependencies:
- Includes Plan 9 SCSI request definitions from `../scuzz/scsireq.h`, plus `dat.h`/`fns.h`.
- Relies on shared `Drive`, `Track`, `Otrack`, `Buf`, and `Scsi` structures.

Research notes:
- The file includes many MMC-6 comments and pragmatic fallbacks for inconsistent drives/media.
- BD detection includes both official structure reads and optional inquiry-string guessing when enabled.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cdfs/mmc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cec/cec.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cec/cec.c

Coraid Ethernet Console client using a custom Ethernet protocol.

Key behavior:
- Parses options for escape character, target Ethernet address, host, shelf, service posting, debug, and persistent probing.
- Can post itself under `/srv` and run over a pipe for service-style use.
- Opens a Plan 9 Ethernet interface, probes shelves by broadcasting discovery packets, records offers in a sorted table, and optionally lets the user choose a target.
- Maintains packet headers with custom EtherType `0xbcbc`, connection id, sequence, type, and payload length.
- Implements timeout helpers via `alarm`/notes.
- Provides byte-order helpers for Ethernet packet fields.
- Connection loop multiplexes keyboard input and CEC network packets, handles acknowledgements/data/reset/discovery traffic, escape handling, and clean exit paths.
- `exits0` centralizes raw-mode cleanup and exit behavior.

Dependencies:
- Includes Plan 9 libc, `ip.h` for Ethernet address formatting/parsing, and `cec.h`.
- Uses platform networking functions from `plan9.c`, mux helpers from `mux.c`, and raw console helpers from `utils.c`.

Research notes:
- This is a low-level console-over-Ethernet program, not IP/TCP.
- The default escape character is control-backslash.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cec/cec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cec/cec.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cec/cec.h

Shared CEC protocol and helper declarations.

Key definitions:
- `Pkt` defines Ethernet destination/source, EtherType, CEC type/connection/sequence/length, and data payload.
- Multiplexer message types: `Fkbd`, `Fcec`, `Ffatal`.
- Protocol constants: `Iowait` and custom `Etype`.
- Declares opaque `Mux` and functions for muxing, network I/O, dumping packets, raw console mode, and exit cleanup.
- Exposes global `debug`.

Dependencies:
- Consumed by `cec.c`, `mux.c`, `plan9.c`, and `utils.c`.

Research notes:
- The packet layout is fixed around raw Ethernet frames.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cec/cec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cec/mux.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cec/mux.c

Two-source multiplexer for keyboard and CEC network input.

Key behavior:
- Defines `Muxmsg` with a source type and embedded `Pkt`.
- `muxcec` reads packets from `netget` and forwards them to a pipe tagged as `Fcec`.
- `muxkbd` reads keyboard bytes, packs them into `Pkt.data`, and forwards them tagged as `Fkbd`; sends `Ffatal` on EOF.
- `muxproc` forks worker processes for each input source.
- `mux` initializes a singleton mux with one keyboard worker and one CEC worker.
- `muxread` reads tagged events and copies packet data out.
- `muxfree` closes pipes, posts notes to workers, waits, and resets singleton state.

Dependencies:
- Includes `cec.h` and Plan 9 process/pipe APIs.

Research notes:
- The singleton `smux` means only one mux instance can be active.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cec/mux.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cec/plan9.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cec/plan9.c

Plan 9 raw Ethernet interface adapter for CEC.

Key behavior:
- `netopen0` opens `<iface>/clone`, connects to the CEC EtherType, opens control/data files, and makes the channel nonblocking.
- `netopen` wraps `netopen0`, prints errors, and closes partially opened fds on failure.
- `netclose` closes clone/control/data fds and resets globals.
- `netget` reads one frame and optionally dumps it under debug.
- `netsend` writes a frame, padding to minimum Ethernet payload size when needed.

Dependencies:
- Includes Plan 9 libc and `cec.h`.

Research notes:
- This is the platform-specific piece; the rest of CEC code uses `netget`/`netsend`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cec/plan9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cec/utils.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cec/utils.c

Console raw-mode and packet dump utilities for CEC.

Key behavior:
- `rawon` opens `/dev/consctl` and writes `rawon` unless running as a posted service.
- `rawoff` closes the console control fd unless running as a service.
- `dump` formats bytes in 16-byte rows as hex for diagnostics.

Dependencies:
- Includes Plan 9 libc and `cec.h`.
- Uses external `svc` to skip console manipulation for service mode.

Research notes:
- `format` uses a static line buffer, so dump output is simple diagnostic output rather than a reusable formatter.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cec/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/bcache.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/bcache.c

Fixed-size block cache for the caching filesystem.

Key behavior:
- `bcinit` initializes block size, disk fd, LRU list, and allocates data buffers for `Nbcache` entries.
- `bcfind` locates an existing cached block or chooses the least-recently-used entry, writing it first if dirty.
- `bcalloc` assigns a cache entry to a block without reading from disk.
- `bcread` reads a block into cache when missing or stale.
- `bcmark` marks a block dirty and appends it to the ordered dirty list; if already dirty, forces writeback.
- `bcwrite` writes dirty blocks in order through a requested block.
- `bcsync` flushes all dirty blocks.
- `bread`/`bwrite` perform positional full-block disk I/O.

Dependencies:
- Includes `cformat.h`, `lru.h`, and `bcache.h`.
- Calls `error`/`warning` supplied by the main program.

Research notes:
- Dirty ordering is explicit and important for on-disk consistency.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/bcache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/bcache.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/bcache.h

Block-cache structures and declarations for `cfs`.

Key definitions:
- `Nbcache` is 32 cached disk blocks.
- `Bbuf` embeds `Lru`, block number, in-use flag, dirty-list link, dirty flag, and data pointer.
- `Bcache` embeds `Lru`, block size, disk fd, dirty-list head/tail, and fixed `Bbuf` array.
- Declares cache init/read/write/mark/sync APIs and main-program error hooks.

Dependencies:
- Requires `Lru` and on-disk block constants.

Research notes:
- `Lru` must be first in `Bbuf` because list routines cast entries through embedded list nodes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/bcache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/cformat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/cformat.h

On-disk format definitions for the Plan 9 caching filesystem.

Key definitions:
- Allocation and inode magic values: `Amagic`, `Imagic`.
- `Indbno` marks indirect pointer blocks; `Notabno` marks absent blocks.
- `Dalloc` allocation blocks contain header metadata and bitmaps.
- `Dptr` records file block number, disk block number, and valid byte range within the block.
- `Inode` records qid, cached length, root data pointer, and in-use flag.
- `Dinode` inode blocks contain header metadata plus inode array.

Dependencies:
- Uses Plan 9 `Qid` and integer types through including files.

Research notes:
- The cache stores sparse byte ranges, not necessarily complete file blocks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/cformat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/cfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/cfs.c

9P caching proxy filesystem that fronts a remote 9P server with a local block cache.

Key behavior:
- Parses options for remote address/server file, cache partition, formatting, authentication, debug, stats, and stdio mode.
- `mountinit` connects to the remote server and mounts a local pipe as the client-facing service.
- `cachesetup` opens/formats/initializes the cache partition with server identity checking.
- Main `io` loop receives client 9P messages, dispatches by type, and delegates or handles locally.
- `rversion`, `rauth`, `rattach`, `rwalk`, `ropen`, `rcreate`, `rclunk`, `rremove`, `rstat`, and `rwstat` maintain local fid/qid state while forwarding most operations.
- `rread` serves cached file bytes when present; on cache gaps, reads missing data from the server and writes it into the cache.
- `rwrite` delegates writes first, then updates cached data and inode version when safe; append-only data is not cached.
- Optional `cfsctl` stats file appears at the root when stats mode is enabled.
- `delegate` forwards a complete client request/reply pair to/from the server.
- `askserver` performs internal server reads for cache fills.
- `sendmsg`/`rcvmsg` marshal/unmarshal 9P messages and validate fids.
- `genstats` formats per-message latency/count deltas and cache byte counters.

Dependencies:
- Uses Plan 9 9P `Fcall` APIs, local inode/file/disk/block-cache modules, and `stats.h`.

Research notes:
- The cache keys by server qid path/version, invalidating stale entries on version changes.
- File lengths for cached inodes start at a maximum sentinel until server stat/read establishes real EOF.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/cfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/disk.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/disk.c

Disk allocation and formatting layer for `cfs`.

Key behavior:
- `dinit` reads disk size, validates logical block size and allocation blocks, initializes block cache, and checks optional expected server/cache name.
- `dformat` lays out allocation bitmap blocks, writes allocation headers, records cache name, allocates allocation blocks themselves, and syncs.
- `_balloc` finds a free bit in one allocation bitmap block.
- `dalloc` scans allocation blocks to allocate one disk block and optionally initializes a `Dptr`.
- `dpalloc` allocates and initializes an indirect pointer block, marking all child pointers absent.
- `_bfree` clears an allocation bit.
- `dfree` frees direct blocks or recursively frees indirect pointer blocks and their referenced data blocks.

Dependencies:
- Includes `cformat.h`, `lru.h`, `bcache.h`, and `disk.h`.

Research notes:
- Comments warn recursive indirect freeing can fail if there are more allocation blocks than block buffers.
- Name mismatch intentionally forces cache reformat for a different remote server identity.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/disk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/disk.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/disk.h

Disk allocator structure and declarations for `cfs`.

Key definitions:
- `Disk` embeds `Bcache` and stores total block count, allocation-block count, bitmap capacity per allocation block, pointers per indirect block, and cache name.
- Declares `dinit`, `dformat`, `dalloc`, `dpalloc`, and `dfree`.
- Defines `DPRINT` debug-print macro gated by global `debug`.

Dependencies:
- Requires `Bcache` and on-disk format types.

Research notes:
- `Disk` is intentionally a subtype-like extension of `Bcache`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/disk.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/file.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/file.c

Sparse file-data cache operations for `cfs`.

Key behavior:
- `fmerge` merges newly cached data into a block’s valid byte range.
- `fbwrite` writes one partial/full file block into the cache, allocating data blocks and converting direct pointers to indirect pointer blocks as needed.
- Write ordering marks data block, indirect block, and inode updates carefully.
- `fwrite` splits arbitrary byte writes across cache blocks.
- `fpget` locates the cached `Dptr` containing or following a requested file offset.
- `fread` reads cached bytes, returning positive bytes read, `0` for no data, or negative gap length when the requested offset starts in a cache hole.

Dependencies:
- Includes on-disk format, block cache, disk, inode, and file headers.

Research notes:
- The sparse range semantics are central to `cfs` fetching only gaps from the server.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/file.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/file.h

Declarations for cached file data operations.

Key declarations:
- `fread(Icache*, Ibuf*, char*, ulong, long)`
- `fwrite(Icache*, Ibuf*, char*, ulong, long)`

Dependencies:
- Uses inode cache types from `inode.h`.

Research notes:
- This header exposes only the byte-level cache read/write API used by `cfs.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/file.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/inode.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/inode.c

Inode cache and qid-to-cache-entry mapping for `cfs`.

Key behavior:
- `iinit` initializes disk allocator state, validates inode blocks, allocates qid map, initializes LRU lists, and builds in-core map from on-disk inodes.
- `iformat` formats disk allocation state and inode blocks, then reinitializes the inode cache.
- `ialloc` chooses an inode buffer from the LRU list and binds it to an inode number.
- `iget` finds or creates a cached inode for a server qid; stale qid versions trigger `iupdate`.
- If no unused inode map entry is available, `iget` evicts the least-recently-used cached inode with `iremove`.
- `iread` loads an inode block into memory and performs consistency checks.
- `iwrite` writes a cached inode back to its containing inode block.
- `iupdate` resets stale cached data while preserving update ordering.
- `iremove` marks an inode unused, frees associated data blocks, and demotes its map entry.
- `iinc` increments local cached qid version after successful cache update.

Dependencies:
- Uses `Disk` as the embedded base of `Icache`, block cache operations, LRU routines, and stats counters.

Research notes:
- The qid map is a linear array; comments explicitly note lookup could be faster.
- Ordering of inode writes before block frees is treated as consistency-critical.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/inode.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/inode.h

Inode cache structures and declarations for `cfs`.

Key definitions:
- `Nicache` is 64 cached inodes.
- `Ibuf` embeds `Lru`, in-use flag, inode number, and on-disk `Inode` contents.
- `Imap` records whether a qid map entry is in use, the qid, and any resident `Ibuf`.
- `Icache` embeds `Disk`, stores inode count/layout constants, map pointer, inode buffer array, and LRU heads.
- Declares initialization, formatting, lookup, read/write, update, remove, and version-increment operations.

Dependencies:
- Requires `Disk`, `Inode`, `Qid`, and `Lru`.

Research notes:
- Like `Disk`, `Icache` uses struct embedding to layer inode management over disk allocation and block cache.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/lru.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/lru.c

Circular doubly linked LRU list implementation.

Key behavior:
- `lruinit` initializes a list head pointing to itself.
- `lruadd` inserts a member before the head’s current first entry.
- `lruref` moves a member to the most-recent position unless it is already there.
- `lruderef` moves a member to the least-recent position.

Dependencies:
- Includes `lru.h`.

Research notes:
- `Bbuf`, `Ibuf`, and `Imap` embed `Lru` as their first field so these generic routines can operate on them.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/lru.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/lru.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/lru.h

LRU list node definition and API declarations.

Key definitions:
- `Lru` contains previous and next pointers.
- `Lruhead` is typedef’d to the same structure shape.

Key declarations:
- `lruinit`, `lruadd`, `lruref`, and `lruderef`.

Dependencies:
- Used by block-cache and inode-cache structures.

Research notes:
- This is an intrusive list; callers are responsible for embedding it correctly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/lru.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/stats.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/stats.h

Statistics structures for optional `cfs` monitoring.

Key definitions:
- `Cfsmsg` stores call count and nanosecond accumulator/start timestamp for one 9P message type.
- `Cfsstat` stores client/server per-message arrays and aggregate counters: directory reads, delegated reads, inserts, deletes, updates, bytes read/written, bytes from server/dirs/cache, and bytes written to cache.

Dependencies:
- Used by `cfs.c` and inode update paths.

Research notes:
- Stats are exposed through the synthetic `cfsctl` file when `-S` is enabled.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cfs/stats.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/chgrp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/chgrp.c

Plan 9 `chgrp` command implementation.

Key behavior:
- Parses `-u` or `-o` to change owner/user instead of group.
- Requires a group/user argument followed by one or more files.
- For each file, builds a partial `Dir` with either `uid` or `gid` set and calls `dirwstat`.
- Reports per-file failures and exits with a non-nil status if any update fails.

Dependencies:
- Includes Plan 9 `<u.h>` and `<libc.h>`.

Research notes:
- Uses Plan 9 `Dir`/`wstat` semantics rather than POSIX `chown`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/chgrp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/chmod.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/chmod.c

Plan 9 `chmod` command implementation.

Key behavior:
- Accepts octal modes or symbolic mode specs of the form `[who]op[rwxalt]`.
- `parsemode` supports `u`, `g`, `o`, `a`; operators `+`, `-`, `=`; permissions `r`, `w`, `x`; and Plan 9 flags append (`a`), exclusive (`l`), temp (`t`).
- For octal input, masks read/write/execute bits for all classes.
- For each target, reads current `Dir`, computes `(old & ~mask) | (mode & mask)`, and applies with `dirwstat`.

Dependencies:
- Includes Plan 9 `<u.h>` and `<libc.h>`.
- Uses Plan 9 mode bits `DMREAD`, `DMWRITE`, `DMEXEC`, `DMAPPEND`, `DMEXCL`, and `DMTMP`.

Research notes:
- Symbolic `-` works by masking selected bits and complementing requested mode bits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/chmod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/apinums.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/apinums.h

LAN Manager Remote Administration Protocol API number definitions.

Key behavior:
- Defines numeric constants for Microsoft LAN Manager APIs, including share, session, connection, file, server, audit, error log, char device, message, service, access, group, user, workstation, use, print, profile, statistics, NetBIOS, account replication, and related APIs.
- Preserves dead/replaced table entries as comments to maintain official numbering.
- Defines `MAX_API` as `215`.

Dependencies:
- Header-only constants, likely consumed by CIFS RAP transaction code elsewhere in the directory.

Research notes:
- This file is protocol-number mapping, not executable logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/apinums.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/auth.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/auth.c

CIFS/SMB authentication response and packet-signature support.

Key behavior:
- Supports `plain`, `lm+ntlm`, `ntlm`, and `ntlmv2` authentication methods; default is `ntlmv2`.
- `auth_plain` obtains a plaintext password via Plan 9 auth and stores it for plaintext SMB session setup.
- `auth_proto` calls `auth_respond` for NTLM/NTLMv2 challenge response and extracts LM/NT response buffers.
- `auth_ntlm` suppresses weak LM response by copying the NT response into both response slots.
- `getauth` selects the method, rejects implicit plaintext auth unless explicitly requested, and reports supported methods on error.
- `genmac` computes SMB signing MD5 over the MAC key and packet, after temporarily replacing signature bytes with the sequence number.
- `macsign` signs outgoing packets or verifies incoming signatures, using the placeholder `BSRSPYL ` before sequence generation starts.

Dependencies:
- Includes Plan 9 auth, libsec MD5, 9P/thread headers, and `cifs.h`.
- Uses `Session`, `Auth`, and `Pkt` fields defined in CIFS headers.

Research notes:
- Comments explicitly warn LM/NTLM weaknesses and recommend Kerberos for real security, though Kerberos is not implemented here.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/cifs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/cifs.c

Core SMB/CIFS client RPC construction and common file/share operations.

Key behavior:
- `cifsdial` connects to TCP CIFS or falls back to NetBIOS, initializes session state, flags, ids, MTU, signing mode, and Unicode support.
- `cifshdr` allocates a packet, emits NetBIOS and SMB headers, assigns sequence numbers for signing, and fills TID/PID/UID/MID fields.
- `pbytes` finalizes the SMB word-count area and starts the byte-count area.
- `cifsrpc` finalizes byte count, signs if enabled, serializes the request through `nbtrpc`, validates reply size/magic/command, parses status and ids, checks signing/sequence behavior, and maps NT/DOS errors.
- `CIFSnegotiate` offers only `NT LM 0.12`, parses server capabilities, time, timezone, challenge, domain/name strings, and Unicode support.
- `CIFSsession` performs session setup with encrypted or plaintext responses and records guest/remote OS state.
- `CIFStreeconnect`, `CIFSlogoff`, and `CIFStreedisconnect` manage share sessions.
- Provides SMB operations for delete file, delete/create directory, rename, NT create/open, legacy SMB open/create, read, write, flush, close, find-close, echo, and set-information.
- Read/write paths support large file offsets when server capabilities permit.

Dependencies:
- Includes Plan 9 9P/thread headers and `cifs.h`.
- Depends on packet marshaling helpers (`p8`, `pl16`, `ppath`, `gmem`, etc.), NetBIOS transport, auth/signing from `auth.c`, and error mapping functions.

Research notes:
- The code is SMB1-era CIFS, with explicit compatibility handling for old Samba and Win9x/NT families.
- A debug-only bad-MAC path currently prints but does not return failure where marked FIXME.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cifs/cifs.c -->