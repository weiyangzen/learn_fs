# Group Research: group_1511_plan9_sources_os_plan9_plan9_sys_src_cmd_cc_dcl_c_sources_os_plan9__efe3756e78e9

Scope verified against `Docs/research_subset_a.md`: all files are under included source tree `sources/os/plan9/plan9`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/dcl.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/dcl.c

This file implements declaration, type layout, initializer, prototype, enum, tag, label, and symbol-scope handling for the shared Plan 9 C compiler.

Key behavior:
- Builds declarator types from parser nodes in `dodecl()`, including arrays, pointers, functions, and bitfields.
- Expands aggregate initializers with `doinit()`, `init1()`, `peekinit()`, and `nextinit()`, including string-to-array expansion and auto-initializer assignment trees.
- Computes struct/union layout in `sualign()`, including bitfield packing and calls into Acid/pickle debug output hooks.
- Manages old-style and ANSI function prototypes with `fnproto()`, `fnproto1()`, `walkparam()`, and `argmark()`.
- Maintains declaration stack rollback with `markdcl()`, `push1()`, and `revertdcl()`, including unused local/parameter warnings and volatile-use emission.
- Checks type equivalence and type signatures with `sametype()`, `rsametype()`, `signature()`, and `sign()`.
- Handles struct/union tags, labels, parameter conversion, auto/global/parameter declarations, type merging, struct element declarations, and enum constants.

Important details:
- Incomplete arrays in typedefs are copied so per-variable array widths can diverge from the typedef.
- `CLOCAL` static locals are rewritten to private static symbols via `mkstatic()`.
- Structure layout also triggers `acidtype()` and `pickletype()` side effects for debug/introspection output.
- `contig()` attempts a specialized zero-fill loop for large contiguous automatic objects after initialization.

Filesystem relevance:
- Indirect. This is compiler infrastructure used to build Plan 9 software, not filesystem code itself.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/dcl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/dpchk.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/dpchk.c

This file implements Plan 9 compiler checks for `#pragma varargck` and related pragmas.

Key behavior:
- Builds format-flag classifications for vararg checking with `argflag()` and `getflag()`.
- Records known vararg functions and typed format verbs through `newname()` and `newprot()`.
- Parses `#pragma varargck argpos`, `type`, and `flag` forms in `pragvararg()`.
- Checks calls in `dpcheck()` by finding the declared format-string parameter and comparing actual arguments against registered format prototypes.
- Implements `#pragma pack`, `#pragma fpround`, `#pragma profile`, and `#pragma incomplete`.

Important details:
- Checks are gated by debug flag `F`; warnings are emitted only when enabled.
- Star width arguments must be `int` or `uint`.
- `#pragma incomplete` can mark struct/union types as deliberately incomplete or toggle debug `T`.

Filesystem relevance:
- Indirect. Provides compiler diagnostics and pragma controls.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/dpchk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/funct.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/funct.c

This file supports Plan 9 `typestr` operator/function rewriting, effectively a compiler extension for struct/union-like operator hooks.

Key behavior:
- `dclfunct()` recognizes eligible type tags, synthesizes external declarations for operation helper functions, and records them in a `Funct` table on the type.
- `isfunct()` rewrites arithmetic, comparison, unary, assignment-op, and cast AST nodes into `OFUNC` calls to generated helper symbols.
- Tables map C operators to helper suffixes such as `add`, `eq`, `asadd`, `neg`, and built-in scalar cast suffixes.

Important details:
- Binary operators become calls like `T f(T,T)`, comparisons become `int f(T,T)`, assignment ops become address-taking calls, and casts use `_scalarT_` / `T_scalar_` naming.
- Normal structure assignment is left to the compiler and not rewritten through this path.
- Rewriting includes type compatibility checks against the generated helper prototype.

Filesystem relevance:
- Indirect compiler extension support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/funct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/lex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/lex.c

This file is the compiler driver and lexical/input layer for the shared Plan 9 C compiler.

Key behavior:
- `main()` parses compiler flags, definitions, includes, output mode, and optional parallel compilation via `NPROC`.
- `compile()` sets output names, include paths, diagnostic/output buffers, optional external ANSI preprocessor invocation, and starts parsing.
- `yylex()` tokenizes identifiers, keywords, numbers, strings, character constants, operators, comments, and macro expansions.
- Handles UTF/rune-aware identifiers and string/character escapes through `getr()` and `escchar()`.
- Initializes symbols and base types in `cinit()`.
- Maintains include/file stack and source history for diagnostics with `newio()`, `newfile()`, `filbuf()`, and line-history formatting.
- Provides custom formatters for operators, types, source locations, node names, type-bit names, and indentation.
- Supplies arena-style allocation with `alloc()` and `allocn()` plus include-path registration.

Important details:
- Recognized debug flags control Acid output, pickle output, warnings, format checks, assembly, structure offsets, registerization, preprocessor selection, and other compiler internals.
- `L"..."` and `L'x'` constants are converted into target `TRune` values.
- Macro expansion is integrated by pushing expanded text onto the input stack.
- Output may be normal object/assembly, Acid declarations, or generated pickle C depending on flags.

Filesystem relevance:
- Indirect. Uses local source/include files and emits compiler outputs, but is not filesystem implementation logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/mac.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/mac.c

This file includes the shared compiler header and the generated/included macro preprocessor body.

Key behavior:
- Includes `cc.h`.
- Includes `macbody`, which supplies macro/preprocessor implementation used by the lexer.

Important details:
- The file itself is only an inclusion wrapper; behavior lives in `macbody`.

Filesystem relevance:
- Indirect compiler support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/mac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/omachcap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/omachcap.c

This file provides the default machine-capability hook for the compiler.

Key behavior:
- Defines `machcap(Node*)` to always return `0`.

Important details:
- This is the default “old cc” behavior; architecture-specific compiler variants can override capability decisions elsewhere.
- It is consulted by code paths such as boolean generation/64-bit optimization decisions.

Filesystem relevance:
- Indirect compiler target hook.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/omachcap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/pgen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/pgen.c

This file generates high-level control-flow code from typed ASTs into architecture back-end operations.

Key behavior:
- `codgen()` emits function prologue pseudo-ops, handles complex returns and register arguments, generates the function body, checks missing returns, and invokes register optimization.
- `gen()` walks statement ASTs and emits branches/code for lists, returns, labels, gotos, cases, switches, loops, `if`, `break`, `continue`, and used/set markers.
- `bcomplex()` type-checks and emits boolean branches for conditions.
- `supgen()` emits code in suppressed-warning mode for unreachable/constant branches.
- `usedset()` emits no-op references to mark volatile/addressed names as used or set.

Important details:
- Reachability state (`canreach`, `warnreach`) drives unreachable-code diagnostics.
- Switch generation delegates case table emission to `doswit()`.
- Loop generation carefully tracks `breakpc`, `continpc`, `nbreak`, and `ncontin`.
- Complex return values are copied through a synthetic `.ret` indirect node.

Filesystem relevance:
- Indirect compiler code generation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/pgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/pickle.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/pickle.c

This file emits “pickle” helper code and complex type declarations for compiler debug/introspection output.

Key behavior:
- Maps Acid/pickle-reserved names to `$`-prefixed names with `pmap()`.
- Finds symbols associated with struct/union/enum and function types through hash-table scans.
- Initializes per-type pickle format characters.
- `picklemember()` emits code to pickle scalar, pointer, array, struct, and union fields.
- `pickletype()` emits `pickle_<type>()` functions for structs/unions or structure-offset defines under structure-debug mode.
- `picklevar()` emits Acid-style `complex` declarations for variables whose types are structs/unions, including local function scoping.

Important details:
- Output is gated by debug flag `P`, with additional suppression for nested includes when `P > 1`.
- Integer pickle codes depend on target `int`, `short`, and `long` widths.
- Arrays emit explicit loops over elements.

Filesystem relevance:
- Indirect compiler debug-output support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/pickle.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/pswt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/pswt.c

This file handles switch-case table preparation plus a few codegen helpers.

Key behavior:
- Sorts and validates switch cases in `doswit()`, detects duplicate cases, supplies default targets, and delegates compact switch emission to `swit1()`.
- Handles 64-bit switch expressions on 32-bit machines by switching on high words then low words.
- Allocates case records with `casf()`.
- Emits wide string storage with `outlstring()`.
- Provides unused-result warning support through `nullwarn()`.
- Converts native doubles into compiler `Ieee` representation with `ieeedtod()`.

Important details:
- 32-bit switch expressions with 64-bit case constants are warned about and impossible cases are skipped.
- Wide string output honors target byte order via alignment behavior.
- Switch emission depends on architecture-provided `swit1()`.

Filesystem relevance:
- Indirect compiler code generation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/pswt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/scon.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/scon.c

This file performs constant folding and additive expression normalization.

Key behavior:
- `evconst()` folds unary, binary arithmetic, bitwise, relational, logical, cast, divide, and modulo expressions when operands are constant.
- `acom()` identifies additive/multiplicative-by-constant expressions suitable for normalization.
- `acom1()` flattens additive terms into multiplier/node terms.
- `acom2()` combines constants, factors common multipliers, reorders terms, and rebuilds a simplified expression tree.
- `addo()` decides whether a node is eligible for additive normalization.

Important details:
- Divide/modulo by zero are warned and not folded.
- Integer fold results are converted back through `convvtox()` for the target type.
- The additive optimizer avoids floating-point and unsupported vlong/pointer-width cases.
- Constants may be combined with address terms to improve address generation.

Filesystem relevance:
- Indirect compiler optimization support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/scon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/sub.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/sub.c

This file is a large shared utility module for compiler AST/type construction, type compatibility, expression rewriting, diagnostics, and static initialization tables.

Key behavior:
- Allocates and prints AST nodes with `new()`, `new1()`, `prtree()`, and `prtree1()`.
- Builds/copies/qualifies types and maps parser type/class bitmasks to compiler type/class objects.
- Checks type compatibility, assignment/cast compatibility, no-op casts, nil casts, and usual arithmetic conversions.
- Supports structure field lookup, unnamed substructure lookup, field-offset materialization, and bitfield access rewriting.
- Rewrites pointer arithmetic and pointer subtraction with element-size scaling.
- Simplifies shift/mask patterns in `simplifyshift()`.
- Detects side effects, constant small values, power-of-two constants, relation inversion/indexing, and list reversal.
- Emits diagnostics, warnings, yacc errors, and fatal errors with source-location formatting.
- Initializes name tables, type-class tables, operation names, relation maps, type compatibility masks, and hash constants in `tinit()`.
- Determines whether statement trees have “dead heads” for reachability analysis.

Important details:
- `typeext()` implements Plan 9 C extensions for unnamed embedded struct/union assignment and pointer conversion.
- `constas()` warns about discarding const qualifiers through assignment.
- `relcon()` narrows constants to avoid widening variables in comparisons.
- Most compatibility logic is table-driven through initialized masks such as `tadd`, `tsub`, `tcast`, `trel`, and `tasign`.

Filesystem relevance:
- Indirect compiler support; no direct filesystem behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/sub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cdfs/buf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cdfs/buf.c

This file implements buffered block I/O for `cdfs` track reading and writing.

Key behavior:
- `bopen()` allocates a `Buf` with block size, block count, mode, data area, and device callback.
- `bread()` refills the buffer on cache miss at a block-aligned offset, then serves byte-range reads from the cached data.
- `bwrite()` appends write data into a block buffer and flushes complete buffered chunks through the callback.
- `bterm()` flushes a final partial write buffer and frees storage.

Important details:
- Read buffering is offset-aware; write buffering intentionally ignores offset and is sequential.
- Write flushes are in whole media blocks except the final partial flush, rounded up by `bterm()`.
- The callback receives block counts, not byte counts.

Filesystem relevance:
- Direct. This is the buffering layer under the `cdfs` 9P CD/DVD/BD filesystem server’s track files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cdfs/buf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cdfs/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cdfs/dat.h

This header defines the `cdfs` media model, drive abstraction, constants, and buffer state.

Key contents:
- Media constants for CD/DVD/BD block sizes, maximum tracks, read transfer sizing, feature map size, and MMC/SCSI type codes.
- Disc/track type enums, writability classes, tri-state flags, MMC mode-page offsets, write parameter bits, close-session functions, TOC formats, write types, track modes, data block types, cache-control bits, and drive capability bits.
- Structs:
  - `Msf`: minute/second/frame address.
  - `Track`: per-track size, block size, block ranges, type, MSF range, exported name/mode/mtime.
  - `Otrack`: open track state, drive pointer, change generation, mode, buffer, and server refcount.
  - `Dev`: drive operation vector for open/create/read/write/close/toc/fixate/control/speed.
  - `Drive`: locked SCSI-backed device plus media type, track table, capability flags, speed state, feature bitmap, and driver auxiliary data.
  - `Buf`: buffered I/O state used by `buf.c`.

Important details:
- `Drive` embeds `Scsi` and a `Dev` operation vector, so MMC code installs methods directly on discovered drives.
- `Readblock` limits CD reads to fit remote 9P RPC behavior.
- The `Drive` state separates drive capability, current disc type, and writable/recordable/erasable properties.

Filesystem relevance:
- Direct. This is the central data definition header for the `cdfs` filesystem service.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cdfs/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cdfs/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cdfs/fns.h

This header declares shared `cdfs` functions.

Key contents:
- Buffer APIs: `bopen()`, `bread()`, `bwrite()`, `bterm()`, `bufread()`, `bufwrite()`.
- Utility APIs: `emalloc()`, `geterrstr()`, `disctype()`.
- MMC probe entry point: `mmcprobe()`.

Filesystem relevance:
- Direct. Declares the cross-file APIs for the `cdfs` 9P service and MMC driver.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cdfs/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cdfs/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cdfs/main.c

This file is the `cdfs` 9P filesystem server entry point and request handler.

Key behavior:
- Exposes a mounted namespace with root, `ctl`, optional audio-write `wa`, optional data-write `wd`, and one file per discovered track.
- `fsattach()`, `fsclone()`, and `fswalk1()` manage lib9p fid state and namespace traversal.
- `fscreate()` creates a writable audio/data track through the drive method table.
- `fsremove()` on `wa`/`wd` finalizes/fixates media.
- `fillstat()` synthesizes directory entries and track file metadata.
- `readctl()` reports CDDB query data for audio discs, speed info, media type, and next writable sector.
- `fsread()` serves directories, `ctl`, and track data; track reads go through the current `Otrack`.
- `writectl()` parses control commands such as `speed`, forwarding other commands to the drive.
- `fswrite()` writes to an open writable track.
- `fsopen()` validates modes and opens track readers.
- `fsdestroyfid()` closes referenced open tracks and refreshes the TOC.
- `checktoc()` refreshes media state and assigns names like `d000`, `a001`, or blank-suppressed entries.
- `main()` opens the SCSI device, probes MMC, initializes the TOC, and mounts the service.

Important details:
- Default device is `/dev/sdD0`; default mount point is `/mnt/cd`.
- Verbose mode redirects stdout/stderr to `/tmp/cdfs.log`.
- Qid versions use drive media change counters to invalidate stale directory state.
- Track file sizes are bytes, while lower-level MMC I/O works in media blocks.

Filesystem relevance:
- Direct. This is the user-facing CD/DVD/BD filesystem server.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cdfs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cdfs/mmc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cdfs/mmc.c

This file implements the MMC/SCSI CD/DVD/BD drive backend for `cdfs`.

Key behavior:
- Probes MMC devices, reads capabilities, optional write parameter page, speed info, and installs `mmcdev` methods.
- Implements mode sense/select helpers for 6-byte and 10-byte MMC mode pages.
- Reads mechanism status, starts/stops/ejects/ingests media, and adjusts drive caching.
- Disc discovery:
  - reads track info, disc info, TOC, DVD/BD disc structures, and MMC configuration features;
  - infers CD tracks for non-writers;
  - detects CD, DVD minus/plus, BD, layer suffixes, recordable/erasable state, write availability, and next writable address.
- Track I/O:
  - opens read tracks with buffered `READ CD` or `READ(12)`;
  - creates writable tracks with proper block size/write-parameter setup;
  - writes with `WRITE(10)` or write-and-verify where appropriate;
  - closes/syncs tracks and handles final lead-out.
- Media management:
  - formats BD/DVD rewriteable media as needed;
  - reserves DVD-R tracks;
  - closes sessions/finalizes discs;
  - blanks or quick-blanks rewriteable media;
  - handles `format`, `blank`, `quickblank`, `eject`, `ingest`, and speed controls.

Important details:
- BD-R may be formatted on first configuration read to allocate spares before writing.
- Write-once media writes are deliberately not retried by the write path to avoid invalid duplicate writes.
- `Readblock` and read CDB sizing are chosen to avoid remote 9P transfer failures.
- The code reconciles drive-reported and computed next writable addresses conservatively and logs disagreements.
- BD capacity is used to infer single/dual/triple/quad layer suffixes.

Filesystem relevance:
- Direct. This is the device implementation that makes `cdfs` track files readable and writable over 9P.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cdfs/mmc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cdfs/scsi.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cdfs/scsi.c

This file wraps Plan 9 raw SCSI device access for `cdfs`.

Key behavior:
- Loads optional sense-code text from `/sys/lib/scsicodes` and maps ASC/ASCQ pairs to readable errors.
- `_scsicmd()` writes CDBs to a raw device, transfers read/write/no-data payloads, then reads command status.
- `scsiready()` sends test-unit-ready with retries.
- `scsi()` serializes access with `QLock`, issues commands, requests sense on failure, retries limited media-change/not-ready cases, and updates media change state.
- `openscsi()` opens `<dev>/raw`, reads `<dev>/ctl` inquiry text, verifies readiness, and builds a `Scsi`.
- `closescsi()` frees the SCSI handle.

Important details:
- Read-TOC failures are common, so verbosity treats them specially.
- Recovered read errors are treated as successful data transfers.
- Write commands are not retried in the general retry loop.
- Media change updates `nchange` and `changetime`, which feed `cdfs` Qid versions.

Filesystem relevance:
- Direct. Provides raw device command transport and media-change detection for the `cdfs` filesystem.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cdfs/scsi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cec/cec.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cec/cec.c

This file implements `cec`, the Coraid Ethernet console client.

Key behavior:
- Parses options for service posting, escape character, debug, target Ethernet address, host, persistent probing, shelf, and interface.
- Discovers shelves by broadcasting `Tdiscover` packets and collecting `Toffer` replies.
- Filters discovered shelves by shelf number, host name, or Ethernet address, then sorts and optionally prompts for selection.
- Establishes a console connection with a three-step Ethernet handshake (`Tinita`, `Tinitb`, `Tinitc`).
- Runs an interactive loop multiplexing keyboard input and Ethernet console packets.
- Sends data packets with sequence numbers, handles ACK/reset, retransmits outstanding keyboard data on timeout, and writes received data to stdout after CR stripping.
- Supports escape commands to quit, interrupt, or continue.
- Can post itself under `/srv` and connect stdin/stdout to a pipe for service use.

Important details:
- Uses private EtherType `0xbcbc`.
- Console raw mode is skipped when running as a posted service.
- `exits0()` cleans up raw mode, active connection, and `/srv` file.
- Packet headers use local helper byte-order conversions.

Filesystem relevance:
- Indirect. Uses `/srv`, `/net/ether*/...`, and console control files, but is not a filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cec/cec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cec/cec.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cec/cec.h

This header defines shared packet, mux, and platform APIs for `cec`.

Key contents:
- `Pkt`: Ethernet-console packet layout with destination/source MACs, EtherType, packet type, connection id, sequence, length, and payload.
- Packet source type enum: `Fkbd`, `Fcec`, `Ffatal`.
- Incomplete `Mux` type and mux APIs.
- Timing and EtherType constants.
- Global `debug`.
- Network API declarations: `netopen()`, `netget()`, `netsend()`.
- Utility declarations: `dump()`, `exits0()`, `rawon()`, `rawoff()`.

Filesystem relevance:
- Indirect. Defines APIs used by code that opens Plan 9 network and console files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cec/cec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cec/mux.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cec/mux.c

This file multiplexes keyboard and Ethernet-console input for `cec`.

Key behavior:
- Starts one child process reading keyboard fd and another reading the network fd.
- Child processes wrap data in `Muxmsg` records tagged as keyboard, console, or fatal keyboard error.
- `mux()` creates a pipe, starts both reader processes, and returns a singleton `Mux`.
- `muxread()` reads the next multiplexed packet from the pipe.
- `muxfree()` closes fds, posts notes to both child processes, waits, and resets singleton state.

Important details:
- Only one mux can be active at a time (`smux` singleton).
- Keyboard reader reports `Ffatal` when input ends or errors.
- Console reader uses `netget()` and stops on failed pipe writes.

Filesystem relevance:
- Indirect. Coordinates fd-based console/network streams.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cec/mux.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cec/plan9.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cec/plan9.c

This file implements Plan 9 network-file access for `cec`.

Key behavior:
- `netopen0()` opens `<interface>/clone`, reads the conversation number, writes `connect <etype>`, opens conversation `ctl`, enables nonblocking mode, then opens conversation `data`.
- `netopen()` wraps `netopen0()` with cleanup and error reporting.
- `netclose()` closes clone/control/data fds.
- `netget()` reads packets from the data fd and optionally dumps them under debug.
- `netsend()` writes packets to the data fd, padding short Ethernet frames to 60 bytes.

Important details:
- Global `fd` is the active network data fd used by the main loop.
- The control fd is set nonblocking so receive timeouts can be driven by alarms.
- Packet dumping uses shared `dump()`.

Filesystem relevance:
- Direct Plan 9 namespace use: opens and controls `/net/ether*/clone`, `ctl`, and `data` files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cec/plan9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cec/utils.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cec/utils.c

This file provides console raw-mode and hex-dump utilities for `cec`.

Key behavior:
- `rawon()` opens `/dev/consctl` and writes `rawon` unless running as a service.
- `rawoff()` closes the raw-mode fd unless running as a service.
- `dump()` formats packet bytes as hex, 16 bytes per line.

Important details:
- Raw-mode failure is reported but not fatal.
- The dump formatter uses a static line buffer.

Filesystem relevance:
- Indirect/direct Plan 9 device use through `/dev/consctl`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cec/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/bcache.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/bcache.c

This file implements the fixed-size block cache used by `cfs` for its on-disk cache partition.

Key behavior:
- `bcinit()` initializes cache buffers, LRU list, dirty list, block size, and backing fd.
- `bcfind()` locates an in-use buffer by block number or chooses the least-recently-used buffer, flushing dirty contents before reuse.
- `bcalloc()` assigns a buffer to a block without reading from disk.
- `bcread()` reads a block into cache on miss.
- `bcmark()` marks buffers dirty and queues them in write order.
- `bcwrite()` writes dirty buffers through a target buffer, preserving ordering.
- `bcsync()` writes all dirty buffers.
- `bread()` and `bwrite()` perform positional block-sized I/O using `pread`/`pwrite`.

Important details:
- `Indbno` is masked out for physical block reads/writes.
- Dirty-page ordering is explicit because inode/pointer/data update order matters to cache consistency.
- Cache size is fixed by `Nbcache` from `bcache.h`.

Filesystem relevance:
- Direct. This is the block-cache layer for `cfs`’s persistent local cache.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/bcache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/bcache.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/bcache.h

This header defines the `cfs` block-cache structures and APIs.

Key contents:
- `Nbcache = 32` fixed buffer count.
- `Bbuf`: LRU node, block number, in-use flag, dirty-list link, dirty flag, and data pointer.
- `Bcache`: LRU head, block size, disk fd, dirty-list head/tail, and fixed buffer array.
- Prototypes for block-cache initialization, allocation, reads, dirty marking, writes, sync, raw block I/O, and error/warning helpers.

Important details:
- `Lru` must be first in `Bbuf` and `Bcache`, allowing casts between list nodes and containing objects.

Filesystem relevance:
- Direct. Defines the low-level cache used by the `cfs` filesystem cache.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/bcache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/cformat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/cformat.h

This header defines the persistent on-disk format of a `cfs` cache partition.

Key contents:
- Magic values `Amagic` and `Imagic`, bit constants, cache-name length, `Indbno`, and `Notabno`.
- Allocation structures:
  - `Dahdr`: allocation block header with magic, logical block size, cache name, and allocation-block count.
  - `Dalloc`: allocation block header plus bitmap.
- `Dptr`: cached file-data pointer containing file block number, disk block number, and valid byte range within the block.
- `Inode`: qid, cached length, root `Dptr`, and in-use flag.
- Inode structures:
  - `Dihdr`: inode block header.
  - `Dinode`: inode block header plus inode array.

Important details:
- Allocation blocks sit at the beginning of the partition.
- `Dptr` may refer to a direct data block or an indirect pointer block via `Indbno`.
- Valid ranges allow caching partial file blocks and detecting gaps.

Filesystem relevance:
- Direct. This is the disk format for `cfs`’s persistent cache.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/cformat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/cfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/cfs.c

This file is the main `cfs` caching 9P proxy filesystem.

Key behavior:
- Parses options for server address/file, cache partition, formatting, auth, debug, standard-io mode, server opening mode, and stats.
- Opens/mounts a remote 9P server and mounts a local proxy namespace.
- Initializes or formats the local cache partition through `cachesetup()`.
- Main `io()` loop receives 9P messages from the client and dispatches handlers.
- Delegates metadata and unsupported operations to the server while caching regular-file reads/writes.
- `rread()` serves cached file ranges from `Icache`/`file.c`; on gaps it asks the server, returns data, and writes fetched data into cache.
- `rwrite()` delegates writes first, then updates cached regular-file data unless append-only.
- Tracks qid/version changes and invalidates stale cache entries.
- Provides synthetic root `cfsctl` stats file when stats mode is enabled.
- Marshals/unmarshals 9P messages with `convS2M()`, `read9pmsg()`, and `convM2S()`.

Important details:
- Local cache identity can be tied to the remote server address; mismatches force formatting.
- `Tversion` negotiates `messagesize` with the client and passes it downstream.
- Directories and auth fids are not cached.
- The cache stores incomplete sparse ranges; gaps trigger targeted server reads.
- Statistics track per-message counts/timing and bytes from server, cache, dirs, and inserted into cache.

Filesystem relevance:
- Direct. This is a Plan 9 client-side caching filesystem proxy.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/cfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/disk.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/disk.c

This file manages allocation blocks and disk-level cache formatting for `cfs`.

Key behavior:
- `dinit()` reads and validates the cache partition’s allocation metadata, logical block size, allocation block count, and cache name.
- `dformat()` initializes allocation blocks and reserves the allocation blocks themselves.
- `_balloc()` finds and sets a free bit in an allocation bitmap.
- `dalloc()` allocates a data block and optionally initializes a `Dptr`.
- `dpalloc()` allocates and initializes an indirect pointer block.
- `_bfree()` clears an allocation bit.
- `dfree()` frees direct or recursively indirect data blocks.

Important details:
- Logical block size must be a multiple of the physical sector size.
- Name mismatch causes initialization failure so callers can reformat for a different server.
- `dfree()` notes a risk if recursive indirect freeing needs more allocation blocks than cache buffers.

Filesystem relevance:
- Direct. Provides free-space management for the `cfs` persistent cache.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/disk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/disk.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/disk.h

This header defines the `Disk` object and disk-allocation API for `cfs`.

Key contents:
- `Disk` embeds `Bcache` and adds total block count, allocation block count, bitmap bits per allocation block, pointers per indirect block, and cache name.
- Prototypes for disk initialization, formatting, data block allocation, pointer block allocation, and freeing.
- External `debug` and `DPRINT` macro.

Filesystem relevance:
- Direct. Declares the disk allocation layer for the `cfs` cache filesystem.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/disk.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/file.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/file.c

This file implements cached file data reads and writes on top of `Icache` and `Disk`.

Key behavior:
- `fmerge()` merges newly cached bytes into a cached block’s valid byte range.
- `fbwrite()` writes one file block worth of data, allocating direct or indirect data blocks and preserving write ordering.
- `fwrite()` writes arbitrary byte ranges by splitting them into cache-block chunks.
- `fpget()` finds the next valid cached data pointer at or after a file offset.
- `fread()` reads cached data, returning:
  - positive bytes read when data is present,
  - negative gap size when the first requested range is missing,
  - zero when no cached data is available.

Important details:
- Each cached disk block tracks one valid byte range.
- Direct pointers are converted to indirect blocks when multiple file-block positions need to be cached.
- `fread()`’s negative gap return is the mechanism `cfs.c` uses to ask the server only for missing ranges.

Filesystem relevance:
- Direct. Implements the cached regular-file data layer for `cfs`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/file.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/file.h

This header declares cached file-data operations for `cfs`.

Key contents:
- `fmerge()`
- `fbwrite()`
- `fwrite()`
- `fpget()`
- `fread()`

Filesystem relevance:
- Direct. Exposes file-range cache operations to the 9P proxy.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/file.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/inode.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/inode.c

This file manages cached inode records and qid-to-inode mapping for `cfs`.

Key behavior:
- `iinit()` initializes disk state, reads inode metadata, creates the in-memory qid map, initializes inode LRU lists, and loads active inodes.
- `iformat()` formats allocation blocks and inode blocks, then reinitializes the cache.
- `ialloc()` assigns an inode cache buffer, evicting old buffer mapping state as needed.
- `iget()` finds an inode by qid path, updates stale qid versions by dropping cached data, or creates/reuses an LRU inode entry.
- `iread()` loads an inode from disk into memory and validates inode-block magic/count.
- `iwrite()` writes an inode back to its containing inode block.
- `iupdate()` forgets old data for a qid version change while preserving update ordering.
- `iremove()` marks an inode unused, frees its data pages, and drops it from LRU state.
- `iinc()` increments cached qid version after successful local cache writes.

Important details:
- Qid map lookup is linear over the configured inode count.
- New cache entries start with maximum length until server stat/read data narrows it.
- Ordering of inode writes before freeing old data is called out as important.
- Stats counters track inserts, updates, and deletes.

Filesystem relevance:
- Direct. This is the inode/index layer for `cfs`’s persistent cache.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/inode.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/inode.h

This header defines inode-cache structures and APIs for `cfs`.

Key contents:
- `Nicache = 64`.
- `Ibuf`: LRU node, in-use flag, inode number, and cached `Inode`.
- `Imap`: LRU node, qid, backpointer to resident `Ibuf`, and in-use flag.
- `Icache`: embeds `Disk`, adds inode sizing/placement fields, fixed inode buffer array, buffer LRU head, qid map, and map LRU head.
- Prototypes for inode allocation, lookup, reading, formatting, initialization, removal, qid update, writing, freeing, and version increment.

Important details:
- `Lru` must be first in `Ibuf` and `Imap`.
- `Icache` composes disk, block cache, inode cache, and qid mapping state.

Filesystem relevance:
- Direct. Defines the metadata cache layer for `cfs`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/lru.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/lru.c

This file implements a small circular doubly-linked LRU list utility.

Key behavior:
- `lruinit()` initializes a list head.
- `lruadd()` appends a member at the list tail.
- `lruref()` moves a member to the tail, marking it most recently used.
- `lruderef()` moves a member to the head, marking it least recently used.

Important details:
- Lists are circular with the head acting as sentinel.
- The cache code embeds `Lru` as the first field in multiple structs so list nodes can be cast to container structs.

Filesystem relevance:
- Direct support utility for `cfs` block and inode cache eviction.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/lru.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/lru.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/lru.h

This header defines the LRU list node and operations used by `cfs`.

Key contents:
- `Lru` struct with previous and next pointers.
- Prototypes for list initialization, append, mark-recent, and mark-unrecent operations.

Filesystem relevance:
- Direct support for `cfs` cache replacement policy.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cfs/lru.h -->