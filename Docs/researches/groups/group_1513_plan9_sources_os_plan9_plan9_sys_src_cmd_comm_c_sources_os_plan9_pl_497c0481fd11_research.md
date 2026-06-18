# Group Research: group_1513_plan9_sources_os_plan9_plan9_sys_src_cmd_comm_c_sources_os_plan9_pl_497c0481fd11

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/comm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/comm.c

Plan 9 implementation of `comm`, comparing two sorted text files and printing lines unique to file 1, unique to file 2, or common to both.

It parses `-1`, `-2`, and `-3` to suppress output columns, opens `-` as `/fd/0`, reads lines through `Biobuf`, compares bytewise, and drains the remaining file once the other reaches EOF. Lines are held in fixed 2048-byte buffers and are nul-terminated at newline or near buffer limit.

Dependencies are minimal: `<u.h>`, `<libc.h>`, and `<bio.h>`. The command assumes sorted input and does no locale collation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/comm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/compress/compress.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/compress/compress.c

Classic Unix `compress`/`uncompress`/`zcat` implementation using Welch LZW compression with variable-width codes and optional block-compression table resets.

The main path parses traditional flags (`-b`, `-c`, `-d`, `-f`, `-n`, `-v`, `-V`, `-C`), recognizes invocation name to select decompression or zcat behavior, writes/reads the `0x1f 0x9d` magic header, and chooses smaller hash-table sizes for small input files. Compression uses open-addressed double hashing over prefix/character pairs, increases code width from 9 bits up to `maxbits`, and emits `CLEAR` when adaptive compression ratio worsens. Decompression rebuilds the string table on the fly and handles the KwKwK special case.

The file overlays compression hash storage with decompression prefix/suffix/stack tables to save memory. File metadata is copied to generated `.Z` output by `copystat`, but the original input unlink is commented out in this Plan 9 copy. It uses POSIX-style stdio/stat/signal/utime headers rather than native Plan 9 `bio`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/compress/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/con/con.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/con/con.c

Interactive connection utility for serial devices and network login sessions. It can dial a byte stream, perform BSD rlogin setup, or open a local device path.

`main` selects simple, rlogin, or device mode from arguments and flags controlling raw/cooked keyboard mode, baud, newline/carriage-return translation, parity stripping, command execution, limited login behavior, and `/srv` posting. `stdcon` forks one process for keyboard-to-network and one for network-to-screen. `fromkbd` handles the `^\` control menu for break, quit, interrupt, return filtering, and shell escapes; `fromnet` filters returns or converts CR to NL.

It depends on Plan 9 networking (`dial`, `netmkaddr`), `/dev/consctl`, notes, rfork, and optional `/srv` registration. It is a user-level terminal bridge rather than filesystem code, but it uses Plan 9 namespace/service conventions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/con/con.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/con/hayes.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/con/hayes.c

Hayes-compatible modem dialer.

It opens an optional serial device plus its `ctl` file, sends attention/reset/setup AT commands, chooses pulse or tone dialing, waits for modem result lines, parses `CONNECT` speed, and writes baud plus modem flow control to the control file. `readmsg` polls available input via `dirfstat` with a timeout and classifies known result prefixes as OK, success, failure, or noise.

The command is designed to be used with Plan 9 serial devices and can use stdout/stdin as the modem data stream when no device argument is supplied.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/con/hayes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/con/xmr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/con/xmr.c

XMODEM receiver writing received 128-byte blocks to a named file.

It enables raw console mode, sends initial `NAK`, reads packets framed by `SOH`, sequence number, inverse sequence number, 128 data bytes, and checksum, resynchronizes on bad packets, ACKs duplicate previous packets, writes expected packets, and stops on `EOT`. `Cancel` aborts the transfer, and `alarm` notifications implement receive timeouts.

The implementation supports checksum XMODEM only; it does not receive 1K or CRC-mode blocks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/con/xmr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/con/xms.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/con/xms.c

XMODEM sender for a named file.

It waits up to 30 seconds for receiver readiness (`NAK` for checksum mode or `C` for CRC mode), sends 128-byte `SOH` blocks by default or 1024-byte `STX` blocks with `-1`, pads the final block with zero bytes, and retries each block until ACK or failure. It supports `-d` debug output and `-p` progress messages.

CRC mode uses a local CRC-CCITT update function. On repeated failure it sends `Cancel`, restores console raw mode, and exits with an error.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/con/xms.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cp.c

Simple Plan 9 file copy command.

It supports copying one file to another or multiple files into an existing directory. `-g` preserves group, `-u` preserves user and group, and `-x` preserves mode and mtime. Directories are rejected; this is not recursive copy. `samefile` compares qid, device, and type metadata to avoid copying a file onto itself.

Data is copied in 8 KiB chunks. On successful copy and requested metadata preservation, it uses `dirfwstat` on the destination fd.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cpp/cpp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cpp/cpp.c

Main driver for the Plan 9 C preprocessor.

It initializes token rows, lexer tables, keyword/macro state, hidesets, and line directives, then repeatedly tokenizes source lines, dispatches `#` control lines, expands macros when possible, suppresses skipped conditional regions, and writes output tokens. `control` implements `#define`, `#undef`, conditionals, `#include`, `#line`, `#error`, `#warning`, `#pragma`, and the extension `#eval`.

The file also provides checked allocation wrappers and formatted diagnostics with source include-stack locations and token/token-row formatting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cpp/cpp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cpp/cpp.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cpp/cpp.h

Shared private header for the Plan 9 C preprocessor.

It defines buffer and nesting limits, token type and keyword enums, macro flags, sentinel bytes, token/source/name-list/include-list structs, quick macro lookup bitsets, and all cross-module function prototypes. `Tokenrow` is the central mutable token sequence abstraction; `Source` forms the include/string-source stack; `Nlist` stores preprocessor keywords and macro definitions.

The header also exposes global state such as `cursource`, `incdepth`, `ifdepth`, `skipping`, include lists, current time string, and output pointer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cpp/cpp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cpp/eval.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cpp/eval.c

Evaluator for `#if`, `#elif`, `#ifdef`, and `#ifndef`.

It expands the expression row with `defined` temporarily activated, then uses operator and value stacks to evaluate integer preprocessor expressions with precedence, unary/binary operators, logical short-circuit undefined tracking, ternary `?:`, signed/unsigned comparison handling, shifts, arithmetic, and comma. `tokval` parses numeric constants, character constants including escapes and UTF runes, treats bare names as zero, and reports strings as errors.

Undefined division/modulo and unresolved logical operands are represented with an `UND` value type and produce diagnostics when final expression value is undefined.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cpp/eval.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cpp/hideset.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cpp/hideset.c

Macro hideset manager used to prevent recursive macro re-expansion.

A hideset is an interned, sorted, null-terminated array of `Nlist*` entries. The module supports membership testing, adding one macro to a hideset, unioning two hidesets, initialization of the empty hideset, and debug printing.

It interns equivalent hidesets to small integer indices stored on tokens, with a fixed temporary construction limit of 32 entries.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cpp/hideset.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cpp/include.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cpp/include.c

`#include` and line-directive support for `cpp`.

`doinclude` parses quoted and angle-bracket includes, expands macro-derived include names when needed, searches absolute paths, configured include directories, and finally the current source directory, then pushes the opened file as a new `Source`. With `-M`, it emits dependency lines using the object name from `setobjname`.

`genline` writes `#line` directives using the current file and working directory unless `-P` disabled line info.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cpp/include.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cpp/lex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cpp/lex.c

Lexer for the C preprocessor.

It encodes a compact lexical FSM, expands it into `bigfsm[256][MAXSTATE]`, and tokenizes input rows through `gettokens`. It recognizes identifiers, numbers, strings, character constants, comments, whitespace, C operators, `##`, ellipsis, trigraphs, escaped-newline folding, UTF-2/UTF-3 lead bytes in identifiers, end-of-buffer, and end-of-file sentinels.

`setsource` and `unsetsource` manage file or string input buffers; `fillbuf` grows buffers for very long input and installs sentinel bytes. `fixlex` disables `//` comments unless C++ mode is enabled.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cpp/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cpp/macro.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cpp/macro.c

Macro definition and expansion engine.

`dodefine` parses object-like, function-like, and variadic macros; `doadefine` handles command-line `-D`/`-U`; `expandrow` scans token rows for expandable names while respecting hidesets and the special `defined` operator. `expand` gathers macro arguments across lines, substitutes arguments, expands arguments except around `##`, applies stringification, performs token pasting, distributes hidesets, and replaces the macro invocation in-place.

Built-in macros expand `__LINE__`, `__FILE__`, `__DATE__`, and `__TIME__`. `__VA_ARGS__` maps to the final variadic argument when present.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cpp/macro.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cpp/nlist.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cpp/nlist.c

Setup and name-table implementation for `cpp`.

`setup` installs preprocessor keywords and built-ins, configures Plan 9 include search paths from `$objtype`, `/sys/include`, `$include`, and `-I`, handles options such as `-N`, `-D`, `-U`, `-M`, `-V`, `+`, `-i`, `-P`, and `-.`, opens input/output files, and pushes the initial source.

`lookup` is a 128-bucket hash table keyed by token text. Installing a name also sets the quick lookup bit used by the lexer/macro expander.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cpp/nlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cpp/test.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cpp/test.c

Tiny macro-expansion test input.

It defines an empty function-like macro `M1`, a function-like macro `M2(A1)` that invokes its argument as a macro, then tests `M2(M1)` and `M2(P1)`. This exercises nested macro invocation and behavior when an argument names an undefined macro.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cpp/test.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cpp/tokens.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cpp/tokens.c

Token-row storage, rewriting, whitespace, and output routines for `cpp`.

It allocates/grows token rows, compares macro definitions, inserts replacement rows, shifts token ranges, normalizes token rows by copying token text, and creates explicit whitespace when adjacent tokens could merge. `puttokens` coalesces contiguous source spans into an output buffer and suppresses normal output under dependency-generation mode.

It also provides debug token printing, newline-only row creation, decimal output formatting, and `newstring` allocation with optional leading-space offset.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cpp/tokens.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cpu.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cpu.c

Plan 9 `cpu` client/server command for remote login with namespace export.

Client mode dials a cpu server, negotiates authentication and optional encryption, sends an optional command and current directory, starts local note forwarding, waits for remote filesystem readiness, then execs `exportfs` to serve the local namespace to the remote side. Listener mode authenticates, sets user/home environment, mounts the client export at `/mnt/term`, redirects stdio to `/mnt/term/dev/cons`, and execs an interactive or command shell.

Authentication supports `p9` and `netkey`; p9 mode uses `auth_proxy`, shared secret material, SHA1-derived directional secrets, and `pushssl` when encryption algorithms are enabled. The file also implements a small 9P filesystem mounted into `/dev` exposing `cpunote`, used to forward notes between local and remote processes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cpu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/crop.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/crop.c

Image crop/translate utility built on Plan 9 `memdraw`.

It reads a `Memimage` from stdin or a file, optionally computes the non-background bounding rectangle for a specified RGB crop color, applies uniform inset, x/y inset, or absolute rectangle selection, fills the destination with a background color or opaque black, draws the clipped source into the new image, applies an output coordinate translation, and writes the image.

The crop-color scan converts non-RGBA32 images to RGBA32 for simple pixel comparison.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/crop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/32bit.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/32bit.h

cwfs 32-bit on-disk layout constants.

It fixes `NAMELEN` to 28, `NDBLOCK` to 6, `NIBLOCK` to 2, and defines `Off` as `long`. The comments warn not to change these values because they preserve compatibility with old 32-bit Plan 9 file-server disks and 9P1 service.

It defines `COMPAT32` and maps `swaboff` to `swab4`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/32bit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/64bit.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/64bit.h

cwfs 64-bit on-disk layout constants.

It sets `NAMELEN` to 56, `NDBLOCK` to 6, `NIBLOCK` to 4, and defines `Off` as `vlong`, creating an incompatible 64-bit filesystem format. The comment notes the name length choice keeps three dentries per magnetic disk sector.

It undefines `COMPAT32` and maps `swaboff` to `swab8`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/64bit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/9netics32.16k/conf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/9netics32.16k/conf.c

Configuration module for a 9netics 32-bit, 16 KiB-block cwfs build.

It defines build time `fs_mktime`, starts the default filesystem at superblock `"main", 2`, initializes local configuration values for dump behavior, superblock selection, and message-buffer counts, and enables both `serve9p1` and `serve9p2`.

This profile can serve legacy 9P1 because it uses the 32-bit layout.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/9netics32.16k/conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/9netics32.16k/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/9netics32.16k/dat.h

Data/configuration header for the 9netics 32-bit, 16 KiB-block cwfs build.

It fixes `RBUFSIZE` at 16 KiB, includes `32bit.h`, sets `FIXEDSIZE = 1`, includes shared `portdat.h`, and declares a small physical memory configuration structure with two memory banks.

This header chooses the on-disk format and raw buffer size for the build.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/9netics32.16k/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/9netics64.8k/conf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/9netics64.8k/conf.c

Configuration module for a 9netics 64-bit, 8 KiB-block cwfs build.

It defines `fs_mktime`, default superblock startup, and local message/dump settings like the 32-bit variant, but its protocol table enables only `serve9p2`. The comment states 64-bit file servers cannot serve 9P1 correctly because `NAMELEN` is too large.

This profile is for the incompatible 64-bit disk format.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/9netics64.8k/conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/9netics64.8k/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/9netics64.8k/dat.h

Data/configuration header for the 9netics 64-bit, 8 KiB-block cwfs build.

It fixes `RBUFSIZE` at 8 KiB, includes `64bit.h`, sets `FIXEDSIZE = 1`, includes `portdat.h`, and declares the same two-bank memory configuration structure used by sibling builds.

The key effect is selecting the 64-bit `Off` layout and larger name/indirect-depth constants.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/9netics64.8k/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/9p1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/9p1.c

Legacy 9P1 protocol implementation for cwfs.

It handles session challenge generation, DES-ticket authorization, attach, clone, walk, open, create, read, write, clunk, remove, stat, wstat, and clwalk. Operations are implemented directly over cwfs `File`, `Dentry`, `Iobuf`, `Filsys`, and `Wpath` structures, with qid validation, permission checks, append/lock handling, directory traversal, raw read escape for `--raw--` files, remove-on-close, and old fixed-size directory record conversion.

`serve9p1` decodes incoming 9P1 messages with `convM2S9p1`, dispatches through `call9p1`, converts errors to `Rerror`, and serializes replies with `convS2M9p1`. It shares removal logic (`doremove`) with the 9P2000 path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/9p1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/9p1.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/9p1.h

Definitions for cwfs’s legacy 9P1 protocol.

It defines fixed 9P1 directory and error record sizes, the 9P1 `Fcall` union layout, old message type numbers, and conversion/dispatcher prototypes. The `Fcall` layout includes fixed-size names, tickets, authenticators, old qids, and fixed directory stat records.

This header is consumed by `9p1.c` and `9p1lib.c`, and bridges old protocol messages onto the cwfs internal dentry model.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/9p1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/9p1lib.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/9p1lib.c

Serialization and deserialization helpers for 9P1 messages, dentries, tickets, and authenticators.

`convS2M9p1` and `convM2S9p1` pack/unpack all 9P1 request and response types using little-endian fixed fields. `convD2M9p1` converts cwfs `Dentry` into old fixed-length directory records, including compatibility qid rewriting for top dump filesystem levels. `convM2D9p1` decodes old stat records back into `Dentry` fields.

Authenticator and ticket converters optionally encrypt/decrypt using the supplied DES key. The file is the protocol-format boundary between legacy clients and cwfs internals.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/9p1lib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/9p2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/9p2.c

9P2000 protocol implementation for cwfs.

It maps cwfs dentry modes/qids to 9P2000 `Dir`/`Qid`, implements `Tversion`, `Tauth`, `Tattach`, `Tflush`, `Twalk`, `Topen`, `Tcreate`, `Tread`, `Twrite`, `Tclunk`, `Tremove`, `Tstat`, and `Twstat`, and dispatches them from `serve9p2`. Authentication uses auth files backed by `auth.c`; auth fids are represented as `QTAUTH` files and routed to `authread`/`authwrite`.

Compared with 9P1, this path supports variable-length 9P2000 stat records, negotiated message size, multi-element walks with partial-walk semantics, cached directory read position, and detailed `Twstat` validation for qid, mode, length, name, uid, gid, and muid changes. It still shares cwfs core routines for directory blocks, data blocks, permission checks, qid generation, truncation, and removal.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/9p2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/all.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/all.h

Top-level include and shared global declaration header for cwfs.

It includes Plan 9 system headers, disk/network/auth-facing headers, `dat.h`, and `portfns.h`, redirects `malloc` to `ialloc`, defines common macros and time helpers, declares qid/permission constants, and exposes major global state: users/groups, file tables, channels, locks, queues, devices, config flags, service name, filesystems, and error strings.

This is the common glue included by cwfs protocol, auth, check, and configuration modules.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/all.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/auth.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/auth.c

cwfs authentication and nvram password support.

The nvram functions read machine auth data, validate the machine key checksum, expose config-device handling, and implement console password checking. The 9P2000 auth-file state machine negotiates `p9sk1`, serves protocol/domain/challenge/ticket-request data, accepts client challenge and ticket+authenticator data, validates tickets with the machine key, maps authenticated server uid, and returns a server authenticator.

`authnew`, `authfree`, `authread`, `authwrite`, `authuid`, `authaname`, and `authuname` are consumed by `9p2.c` auth fids. Authentication state is pooled according to `conf.nauth`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/chk.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/chk.c

cwfs filesystem checker and optional repair logic.

`cmd_check` parses check options, locks the filesystem when writable, reads the superblock/root, allocates block/qid bitmaps, recursively walks the directory tree, validates tags and qids, detects duplicate/out-of-range blocks, optionally reads all file data, prints files/directories, rebuilds tags, clears bad references, touches old blocks, trims filesystem size, and rebuilds or checks the free list. It reports used/free/missing/bad/qid counts and recursion stack usage.

The checker traverses direct and multi-level indirect blocks using `fsck`, `dirck`, `indirck`, and address validators. Free-list handling differs for normal and copy-on-write/read-only devices: `mkfreelist` rebuilds from scratch for writable normal devices, while `trfreelist` filters an existing list for cw devices.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/chk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/choline/conf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/choline/conf.c

Site-specific cwfs configuration for `choline`.

It sets `fs_mktime`, starts filesystem `"main"` at superblock 2, and initializes local parameters including a larger file table (`conf.nfile = 60000`), `firstsb = 12565379`, and smaller large-message count. It enables both `serve9p1` and `serve9p2`.

This build uses the 32-bit, 16 KiB-block layout from its companion `dat.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/choline/conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/choline/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/choline/dat.h

Data/configuration header for the `choline` cwfs build.

It fixes `RBUFSIZE` at 16 KiB, includes `32bit.h`, sets `FIXEDSIZE = 1`, includes shared `portdat.h`, and declares the same two-bank memory configuration structure used by other 32-bit cwfs profiles.

This selects old 32-bit disk compatibility while allowing both 9P1 and 9P2000 service in `conf.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/choline/dat.h -->