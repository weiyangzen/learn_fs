# Group Research: group_1627_plan9_sources_os_plan9_plan9_sys_src_cmd_unix_u9fs_des_c_sources_os_894ef362737b

Scope: `Docs/research_subset_a.md`. All listed source files were read completely, not sampled.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/des.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/des.c

- Role: Implements DES block encryption/decryption and key schedule generation for `u9fs` authentication support.
- Key functions: `block_cipher(expanded_key, text, decrypting)` runs 16 DES rounds over one 8-byte block; `key_setup(key, ek)` expands a 7-byte DES key into the 128-byte round-key table consumed by `block_cipher`.
- Data structures: Large static combined S/P-box tables (`s0p` through `s7p`), initial/final permutation helpers, and `keyexpand` bit-placement tables.
- Integration: Declared in `plan9.h`; used by authentication modules built into the u9fs makefile.
- Risks/notes: Uses `long` for bit operations, so portability depends on assumptions about width/sign behavior; DES itself is legacy cryptography and unsuitable for modern security except protocol compatibility.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/des.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/dirmodeconv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/dirmodeconv.c

- Role: Provides a custom `%M` formatter for Plan 9 directory mode bits.
- Key functions: `dirmodeconv` formats `DMDIR`, `DMAPPEND`, `DMEXCL`, and rwx owner/group/other bits into strings like `d-rwxr-xr-x`; `rwx` copies a 3-character permission triplet.
- Integration: Installed by `u9fs.c` with `fmtinstall('M', dirmodeconv)` and used by `fcallconv.c` diagnostics.
- Risks/notes: Uses a static buffer, so it is not thread-safe; this is consistent with the single-threaded u9fs formatter style.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/dirmodeconv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/doprint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/doprint.c

- Role: Reimplements a compact Plan 9-style formatting engine for Unix-hosted u9fs.
- Key functions: `doprint` parses format strings; `fmtinstall` registers custom converters; `numbconv`, `strconv`, `Strconv`, `cconv`, `sconv`, `percent`, and `column` implement core verbs.
- State: Global `printcol` tracks output columns; `fmtalloc` maps format characters to converter callbacks.
- Integration: Backing formatter for `print.c`, `u9fs.c` fatal/log output, and custom `%F`, `%D`, `%M` protocol diagnostics.
- Risks/notes: Lock macros are no-ops and buffers are caller-owned; fine for the program’s style, but not generally thread-safe.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/doprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/fcall.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/fcall.h

- Role: Defines the 9P2000 `Fcall` structure, message type constants, wire-size constants, and little-endian packing macros.
- Key declarations: `convM2S`, `convS2M`, `convM2D`, `convD2M`, `sizeD2M`, `fcallconv`, `dirconv`, `dirmodeconv`, and `read9pmsg`.
- Protocol model: Covers version/auth/attach/walk/open/create/read/write/clunk/remove/stat/wstat fields in one union-like struct.
- Integration: Central protocol header for u9fs server and old/new protocol conversion code.
- Risks/notes: Macros like `PBIT32` expand to multiple statements without `do { } while(0)`, so callers must use them carefully.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/fcall.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/fcallconv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/fcallconv.c

- Role: Formats 9P `Fcall` and `Dir` structures into readable debug strings.
- Key functions: `fcallconv` handles all 9P request/response message types; `dirconv` and `fdirconv` format `Dir`; `qidtype` renders Qid flags; `dumpsome` prints read/write payload previews.
- Integration: Registered as `%F` and `%D` by `u9fs.c`; uses old or new stat decoders depending on global `old9p`.
- Risks/notes: Uses fixed-size local buffers and `sprint`; normal debug strings fit, but unusually large formatted fields could stress buffer assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/fcallconv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/makefile

- Role: Unix makefile for building the `u9fs` executable.
- Build inputs: Compiles authentication modules, 9P conversion modules, DES, formatting, UTF, utility, and `u9fs.o`.
- Configuration: Notes platform-specific SGI/SunOS flags, optional `inttypes.h` replacement, and socket/nsl linker additions.
- Targets: `u9fs`, pattern `.c.o`, `clean`, and `install`.
- Risks/notes: Header dependency list omits some included headers such as `oldfcall.h`/`u9fs.h`, so incremental rebuilds may be incomplete.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/oldfcall.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/oldfcall.c

- Role: Bridges old 9P1 wire messages to the newer `Fcall` structure used by the server.
- Key functions: `oldhdrsize`, `iosize`, `convM2Sold`, `convS2Mold`, `convM2Dold`, `convD2Mold`, `sizeS2M`, and `sizeD2Mold`.
- Control flow: Incoming old opcodes are decoded into modern `Twalk`, `Topen`, `Tread`, etc.; outgoing responses are re-encoded as fixed-format 9P1 messages.
- Compatibility details: Maps old clone/walk semantics into `Twalk`; squashes Qid path/type through `FIXQID`; treats old session as a special flush/session response path.
- Risks/notes: Fixed 28/64/116 byte fields mirror legacy protocol limits; string fields point into the receive buffer rather than owned memory.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/oldfcall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/oldfcall.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/oldfcall.h

- Role: Declares old 9P conversion routines and old protocol opcode constants.
- Key declarations: Old message conversion, stat conversion, header sizing, and write data sizing helpers.
- Integration: Included by `u9fs.c`, `oldfcall.c`, and `fcallconv.c` for old/new protocol auto-detection and debug formatting.
- Risks/notes: Contains constants only; correctness depends on `oldfcall.c` preserving fixed legacy field layout.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/oldfcall.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/plan9.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/plan9.h

- Role: Portability shim that gives Unix builds Plan 9-like types, constants, argument parsing macros, UTF declarations, formatting declarations, Qid/Dir definitions, and DES prototypes.
- Key content: Large-file feature macros, platform workarounds for SGI/Sun, `uchar`/`ulong`/`vlong` aliases, `ARGBEGIN`, open mode constants, Qid type bits, Dir mode bits, `Qid`, and `Dir`.
- Integration: Included first by most u9fs support files to normalize the Unix C environment.
- Risks/notes: Sets `UTFmax` to 3 while `rune.c` has code paths for 4-byte UTF guarded by `UTFmax >= 4`; this preserves older Plan 9 UTF behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/plan9.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/print.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/print.c

- Role: Provides Plan 9-style `print`, `fprint`, `sprint`, `snprint`, and `seprint` wrappers over `doprint`.
- Behavior: Formats into stack buffers or caller buffers, writes to file descriptors for `print`/`fprint`, and restores `printcol` after string-formatting calls.
- Integration: Used throughout u9fs for diagnostics and string assembly.
- Risks/notes: `sprint` uses a fixed 4096-byte bound even though the caller’s buffer size is unknown; use `snprint`/`seprint` where bounds matter.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/print.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/random.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/random.c

- Role: Supplies `randombytes` for authentication nonce/key material in u9fs.
- Key functions: `getseed` tries `/dev/urandom`, then falls back to time and PID; `randombytes` seeds libc `random()` once and fills output bytes.
- Integration: Declared in `u9fs.h`; consumed by auth modules.
- Risks/notes: After seeding, bytes come from `random()`, not directly from a cryptographic RNG; adequate only for legacy compatibility, not modern cryptographic use.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/random.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/readn.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/readn.c

- Role: Blocking helper to read up to an exact byte count unless EOF/error occurs.
- Key function: `readn(f, av, n)` loops until `n` bytes are read, returns the first error/EOF if no bytes were read, or partial count otherwise.
- Integration: Used for 9P message framing and random seed reads.
- Risks/notes: Does not retry on `EINTR`; callers treat short reads as fatal in protocol paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/readn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/remotehost.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/remotehost.c

- Role: Discovers the peer hostname for an accepted network connection on fd 0.
- Key function: `getremotehostname(name, nname)` defaults to `unknown`, calls `getpeername` and `gethostbyaddr`, then enables `SO_KEEPALIVE` and optionally `TCP_NODELAY`.
- Integration: `u9fs.c` calls it when network mode is enabled; authentication modules can use `remotehostname`.
- Risks/notes: Reverse DNS failure leaves `unknown`; socket option errors are ignored.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/remotehost.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/rune.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/rune.c

- Role: Implements Plan 9 UTF/Rune conversion helpers for the Unix port.
- Key functions: `chartorune`, `runetochar`, `runelen`, and `utflen`.
- Behavior: Validates UTF encodings, rejects overlong forms and surrogate halves, maps bad input to `Runeerror`.
- Integration: Used by argument parsing, formatting, tokenization, and UTF-aware string search.
- Risks/notes: `plan9.h` defines `UTFmax` as 3 and `Rune` as `ushort`, so 4-byte Unicode support is effectively disabled in this build profile.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/rune.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/safecpy.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/safecpy.c

- Role: Fixed-width, zero-padded copy helper.
- Key function: `safecpy(to, from, tolen)` clears destination, copies up to `tolen` bytes from optional source.
- Integration: Declared in `u9fs.h`, likely used by authentication code for protocol fixed fields.
- Risks/notes: If `from == nil`, `memcpy(to, from, 0)` is invoked; usually harmless, but strictly depends on C library tolerance for zero-length null copies. It also includes `<stdio.h>` without declaring `memset`, `strlen`, or `memcpy`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/safecpy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/strecpy.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/strecpy.c

- Role: Plan 9-style bounded string copy returning the end pointer.
- Key function: `strecpy(to, e, from)` copies through NUL if it fits, otherwise truncates and NUL-terminates at `e-1`.
- Integration: Used in old fixed-field protocol encoding and hostname handling.
- Risks/notes: If `from` is null, behavior is undefined; callers pass real strings.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/strecpy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/sun-inttypes.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/sun-inttypes.h

- Role: Compatibility replacement for missing SunOS 5.5.1 `inttypes.h`.
- Content: Defines signed and unsigned 8/16/32/64-bit integer typedefs plus pointer integer typedefs.
- Integration: Makefile comments instruct copying it to `inttypes.h` on affected SunOS systems.
- Risks/notes: Type widths assume the target compiler/platform layout noted in the file comment.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/sun-inttypes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/tokenize.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/tokenize.c

- Role: Tokenizes mutable strings using Plan 9 UTF-aware delimiter scanning.
- Key functions: `getfields` splits on any rune in `set`; `tokenize` splits on whitespace.
- Integration: Declared in `plan9.h`; used by control-message parsing and argument handling patterns.
- Risks/notes: Modifies the input buffer in place by writing NULs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/tokenize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/u9fs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/u9fs.c

- Role: Main Unix-hosted 9P file server that exports a chrooted Unix filesystem to Plan 9 clients.
- Protocol flow: `serve` reads old/new 9P requests, dispatches to handlers, logs optional `%F` traces, and writes responses; `getfcall` auto-detects 9P1 vs 9P2000.
- Filesystem handlers: Implements version, auth, attach, walk, open, create, read, write, clunk, remove, stat, and wstat by mapping to Unix `stat`, `open`, `pread`, `pwrite`, `mkdir`, `remove`, `rename`, `chmod`, `utime`, `chown`, and `truncate`.
- State: Tracks `Fid` objects with path, stat cache, user, open mode, directory stream, auth flag, and auth magic; tracks users/groups in small hash tables.
- Security model: Auth method selected by `-a`; attaches reject root unless `-u defaultuser` is set; per-request `userchange` switches effective uid and group membership; special files require `aname=device`.
- Filename handling: `enfrog`/`defrog` escape Plan 9-invalid path bytes using backslash hex encoding.
- Risks/notes: Permission checks intentionally rely mostly on effective uid operations but some prechecks are racy. `freefid` closes `fd` only if nonzero, so fd 0 would not close, though file fds are normally opened after stdio/log setup. Wstat is explicitly non-atomic across chmod/utime/chgrp/rename/truncate.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/u9fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/u9fs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/u9fs.h

- Role: Shared declarations for u9fs authentication modules and server globals.
- Key content: `Auth` interface with auth/attach/init/read/write/clunk callbacks; exported auth methods; `remotehostname`, `Eauth`, `autharg`, `msize`; auth fid helpers; `randombytes`; `safecpy`.
- Integration: Included by `u9fs.c`, `random.c`, and auth modules.
- Risks/notes: `Auth` differs from older `u9fsauth.h`, reflecting the expanded auth-fid callback model.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/u9fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/u9fsauth.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/u9fsauth.h

- Role: Older/smaller authentication interface header.
- Content: Defines `Auth` with only `session` and `attach` callbacks.
- Integration: Not referenced by the read u9fs makefile object list’s main server path; likely retained for older auth code compatibility.
- Risks/notes: Conflicts structurally with `u9fs.h` if included together.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/u9fsauth.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/utfrune.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/utfrune.c

- Role: UTF-aware equivalent of `strchr` for searching a rune in a UTF string.
- Key function: `utfrune(s, c)` uses `strchr` for ASCII-compatible runes and `chartorune` for multibyte runes.
- Integration: Used by `getfields` delimiter matching.
- Risks/notes: Invalid UTF advances by `chartorune`’s error length of 1.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/utfrune.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/winplumb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/winplumb.c

- Role: Windows helper that listens for TCP commands and launches Windows programs via `ShellExecute`.
- Control flow: Parses `tcp!ip!port`, initializes Winsock, binds/listens, accepts one-line commands, splits executable and argument tail at first space, then invokes `ShellExecute`.
- Helpers: Network byte-order helpers, legacy classful IP parsing, Windows error formatting, and `WinMain` argument splitting.
- Integration: Paired with `winstart`, which sends commands to `tcp!192.168.233.1!17890`.
- Risks/notes: Executes received network strings without authentication; suitable only on trusted/local networks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/winplumb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/winstart -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/winstart

- Role: Tiny Plan 9 rc script to forward command arguments to `winplumb`.
- Behavior: Echoes all arguments into `aux/trampoline tcp!192.168.233.1!17890`.
- Integration: Client-side trigger for the Windows `winplumb` listener.
- Risks/notes: Hard-coded IP and port.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/winstart -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unlnfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unlnfs.c

- Role: Restores long filenames from LNFTS-style encoded names using `.longnames`.
- Control flow: Reads long names, computes 26-character base32 MD5 short names, recursively scans directories, and renames matching encoded entries to long names via `dirwstat`.
- Key functions: `long2short`, `readnames`, `renamedir`, and `rename`.
- Integration: Uses Plan 9 `libsec` MD5 and base32 encoding.
- Risks/notes: Recurses through all directories before renaming matching entries; duplicate hash-derived names would collide.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unlnfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unmount.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unmount.c

- Role: Command wrapper around Plan 9 `unmount`.
- Behavior: Accepts either `mountpoint` or `mounted mountpoint`, preserving argument order equivalent to `mount`.
- Integration: Calls `unmount(mnted, mtpt)` and reports errors with `%r`.
- Risks/notes: Minimal command with no special edge handling beyond usage validation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unmount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/alias/aliasmail.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/alias/aliasmail.c

- Role: Translates mail aliases from upas library alias files.
- Control flow: Reads system names, reads alias file list from `namefiles` or `fromfiles`, lowercases input names, searches alias DB files including `#include` directives, and emits local fallback or alias expansion.
- Key functions: `getdbfiles`, `translate`, `lookup`, `attobang`, `compare`, `mklower`.
- Integration: Uses `common.h` String/Sinstack helpers and `UPASLIB`.
- Risks/notes: Intentionally lowercases names, warned in file header. `mklower` mutates `argv` strings in place.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/alias/aliasmail.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/addhash.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/addhash.c

- Role: Merges one or more serialized token hash tables with integer scaling factors.
- Control flow: Reads pairs of `file scale`, accumulates counts into global `Hash`, optionally creates an exclusive output file with retry-on-lock, writes merged hash.
- Integration: Uses `Breadhash`, `Bwritehash`, and `Bopenlock` from `hash.c`.
- Risks/notes: Rejects scale zero; old entries may be dropped by `Bwritehash` date aging.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/addhash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/bayes.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/bayes.c

- Role: Classifies message token hash files against multiple mailbox/class hash tables.
- Algorithm: For each message token, computes per-class frequencies normalized by message count, clamps probabilities, retains the most informative words, multiplies class probabilities, and prints best class plus confidence.
- Inputs: `boxhash ... ~ msghash ...`; options enable debug, keyword output, and max informative words.
- Integration: Uses `Hash`/`Stringtab` serialized tables from `hash.c`.
- Risks/notes: Multiplies many doubles directly and can underflow for larger `mbest`; current default is small.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/bayes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/dfa.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/dfa.c

- Role: Converts Plan 9 regexp NFAs into minimized deterministic regex programs and executes/serializes them.
- Key functions: `dregcvt`, `dregexec`, `Bprintdfa`, `Breaddfa`; helper phases include empty-transition closure, interesting-rune detection, transition exploration, minimization, and compact program construction.
- Data structures: Internal `Deter` state and `Reiset` sets; public `Dreprog`, `Dreinst`, and `Drecase`.
- Integration: Used by `regen.c` to precompile classifier regexes and by `msgtok.c` to tokenize messages.
- Risks/notes: Handles only 16-bit rune space in `findchars`; uses `longjmp` for allocation/format errors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/dfa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/dfa.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/dfa.h

- Role: Public interface and data layout for deterministic regexp programs.
- Key types: `Dreprog` with four start states, `Dreinst` with final/loop/case array, and `Drecase` with range start and next state.
- Key declarations: `dregcvt`, `dregexec`, `Breaddfa`, `Bprintdfa`.
- Integration: Included by DFA compiler, dumper, regex generator, and message tokenizer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/dfa.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/dump.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/dump.c

- Role: Diagnostic utility for compiling and dumping one regexp as DFA.
- Behavior: Compiles `argv[1]`, converts it with `dregcvt`, prints state/case ranges, then tests remaining arguments with `dregexec`.
- Integration: Includes libregexp internals and `dfa.h`.
- Risks/notes: Minimal argument validation; assumes at least one regexp argument.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/dump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/hash.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/hash.c

- Role: String-count hash table implementation and serialized hash table I/O for Bayes tools.
- Key functions: `findstab`, `sortstab`, `Bwritehash`, `Breadhash`, `freehash`, `Bopenlock`.
- Memory model: Allocates `Stringtab` entries in large pools and string bytes in 512 KiB chunks; free list recycles entries.
- Format: `# hash table` header followed by `token<TAB>count date`; writes skip nonpositive and older-than-30-day entries.
- Risks/notes: `freehash` frees the `Hash` pointer itself, so callers must allocate hashes dynamically unless they avoid freeing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/hash.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/hash.h

- Role: Declares token hash table structures and operations.
- Key types: `Stringtab` for token/count/date entries and `Hash` for bucket table plus all-entry list.
- Integration: Shared by hash merging, message classification, and Bayes classifier tools.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/hash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/msgclass.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/msgclass.c

- Role: Classifies token-count input against Berkeley DB-backed class databases and optionally trains the winning database.
- Control flow: Reads token files/stdin into an in-memory `Msgdb`, locks optional lockfile, opens class DBs, computes informative-word probabilities, prints class probabilities and keyword evidence, then updates class counts when `-a` is set.
- Key functions: `noteword`, `process`, `lockfile`.
- Integration: Uses `msgdb.h` and `msgdbx.c`.
- Risks/notes: The source contains an apparent syntax error in `lockfile`: `if(strstr(err, "file is locked")==nil && strstr(err, "exclusive lock")==nil))` has an extra `)`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/msgclass.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/msgdb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/msgdb.c

- Role: Command-line tool for reading, writing, and dumping message token databases.
- Behavior: Opens DB with optional create; in input mode reads `token [value]` lines and updates counts; otherwise enumerates all key/value pairs.
- Integration: Front-end for `Msgdb` implementation in `msgdbx.c`.
- Risks/notes: `-i` is accepted but omitted from usage text.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/msgdb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/msgdb.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/msgdb.h

- Role: Abstract interface for a message token database.
- Key API: `mdopen`, `mdget`, `mdput`, `mdenum`, `mdnext`, and `mdclose`.
- Integration: Used by `msgdb.c` and `msgclass.c`; implemented by `msgdbx.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/msgdb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/msgdbx.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/msgdbx.c

- Role: Berkeley DB hash implementation of the `Msgdb` interface.
- Key behavior: Opens a DB hash with 2 MiB cache, stores counts as 4-byte big-endian values, deletes keys for nonpositive counts, enumerates with `seq`.
- Integration: Backing store for token/class databases.
- Risks/notes: `mdopen(nil, 1)` relies on `dbopen` behavior for unnamed/temp DBs; values larger than 32 bits are truncated.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/msgdbx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/msgtok.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/msgtok.c

- Role: Tokenizes RFC822 messages into features for spam/classification databases.
- Control flow: Loads three DFA regexes, streams input through a rolling buffer, recognizes `From ` message boundaries, ignores noise, emits header-tagged and normal keyword tokens, and emits stem variants via `trim`.
- Key functions: `buildre`, `trim`, main tokenization loop.
- Integration: Reads DFA set generated by `regen.c`; feeds `msgdb`/`bayes` pipelines.
- Risks/notes: Debug path prints unmatched bytes before fatal; token lowercasing is intentionally disabled/commented for UTF complexity.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/msgtok.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/regcomp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/regcomp.c

- Role: Local copy/variant of Plan 9 regexp compiler with adjusted allocation behavior.
- Key functions: `regcomp`, `regcomplit`, `regcompnl`; parser helpers build NFA instructions from regex syntax, character classes, alternation, concatenation, and repetition.
- Data structures: Operator and operand stacks, `Reinst` program, `Reclass` character classes.
- Integration: Consumed by `regen.c`, `dump.c`, and DFA conversion.
- Risks/notes: File header states it leaks extra classes when it runs out; fixed stack sizes (`NSTACK`) limit regex complexity.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/regcomp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/regen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/regen.c

- Role: Generates the serialized DFA regex file used by `msgtok`.
- Behavior: Defines ignore patterns, keyword pattern, and `^From ` detector; compiles each into deterministic programs and writes three `# dreprog` blocks.
- Helpers: `strcpycase` expands lowercase letters outside character classes into case-insensitive classes; `dregcomp` wraps `regcomp` plus `dregcvt`.
- Risks/notes: Static 16 KiB regex assembly buffer assumes combined patterns fit.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/regen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/common/appendfiletombox.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/common/appendfiletombox.c

- Role: Appends a message/file stream to a mailbox or file while preserving mbox format rules.
- Key functions: `appendfiletombox` escapes line-start `From ` by inserting a leading space and ensures mailbox entries end with blank lines; `appendfiletofile` appends raw content.
- State: `Inbuf` maintains a 64 KiB buffer, read/write cursors, byte count, and last byte written.
- Integration: Used by mail delivery code.
- Risks/notes: Operates on raw file descriptors and returns `-1` on read/write failure; caller owns locking.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/common/appendfiletombox.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/common/aux.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/common/aux.c

- Role: Shared string/path/address utility functions for upas tools.
- Key functions: `abspath`, `basename`, `append_match`, `shellchars`, `escapespecial`, `unescapespecial`, `returnable`.
- Behavior: Encodes shell-special characters as `%%HH`, decodes those escapes, and flags CR/LF as illegal shell characters.
- Integration: Declared in `common.h`.
- Risks/notes: Only escapes a fixed special-character set; callers must not treat it as a complete shell quoting system.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/common/aux.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/common/become.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/common/become.c

- Role: Drops process identity/namespace to a powerless user.
- Key function: `become(cmd, who)` supports `who == "none"` by writing `none` to `#c/user` and installing a new namespace with `newns`.
- Integration: Called by process spawning helpers when a child should run as another user.
- Risks/notes: Only implements special handling for `none`; other names return success without changing identity.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/common/become.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/common/common.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/common/common.h

- Role: Shared upas common header aggregating system wrappers, mail header regex globals, mailbox constants, process stream types, and utility prototypes.
- Key content: `IS_HEADER`, `IS_TRAILER`, mailbox type constants, `stream`, `process`, process control APIs, append/copy APIs, and auxiliary string/path APIs.
- Integration: Included by alias, filterkit, and common source files.
- Risks/notes: Includes broad global state and prototypes; modules are tightly coupled through this header.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/common/common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/common/config.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/common/config.c

- Role: Defines default upas filesystem paths and mailbox mode.
- Values: `MAILROOT=/mail`, `UPASLOG=/sys/log`, `UPASLIB=/mail/lib`, `UPASBIN=/bin/upas`, `UPASTMP=/mail/tmp`, `SHELL=/bin/rc`, `POST=/sys/lib/post/dispatch`, `MBOXMODE=0662`.
- Integration: Referenced through `sys.h` by common utilities and mail tools.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/common/config.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/common/libsys.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/common/libsys.c

- Role: Plan 9 system abstraction layer for upas mail tools.
- Major areas: Date/user lookup, mailbox lock-file management, file open/create/close wrappers, directory/stat helpers, system/domain names, process killing, pipe-note handling, console hold, mailbox path construction, user display-name lookup, remote address discovery, and mailbox creation.
- Locking: `syslock` waits for directory lock file; `trylock` creates/opens lock and forks a refresher; `sysunlock` closes and kills refresher.
- Mailbox helpers: `mboxpath`, `mboxname`, `deadletter`, `readlock`, and `creatembox` implement upas path policy.
- Risks/notes: Some lock failures are logged but treated as live-without-lock cases. `sysopenlocked` has exclusive open disabled “until system call is fixed.”
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/common/libsys.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/common/mail.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/common/mail.c

- Role: Defines mailbox `From ` line regexes and simple parse/print helpers.
- Key functions: `print_header`, `print_remote_header`, and `parse_header`.
- Integration: Used by upas components needing Unix mbox-style header handling.
- Risks/notes: `parse_header` handles quoted sender names simply and does not perform full RFC822 parsing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/common/mail.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/common/makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/common/makefile

- Role: Unix-style makefile to build `common.a`.
- Inputs: `mail.o`, `aux.o`, `string.o`, and `${SYSOBJ}`.
- Targets: Archive creation with `ar`, optional `ranlib`, and `clean`.
- Risks/notes: Mentions dependencies such as `aux.h`, `string.h`, and `mail.h` that are not part of this grouped file list.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/common/makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/common/process.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/common/process.c

- Role: Child process and pipe stream management for upas tools.
- Key functions: `instream`, `outstream`, `stream_free`, `noshell_proc_start`, `proc_start`, `proc_wait`, `proc_free`, and `proc_kill`.
- Behavior: Creates Bio-backed pipes, forks, dup’s requested standard fds, optionally detaches and calls `become`, then execs.
- Risks/notes: Error paths after pipe/Binit allocation can leak partially allocated stream memory.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/common/process.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/common/sys.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/common/sys.h

- Role: System-dependent declarations and common includes for upas.
- Key content: Plan 9 headers, `String.h`, `Mlock`, config globals, and prototypes for all `libsys.c` wrappers plus identity/path helpers.
- Integration: Included by `common.h`.
- Risks/notes: Declares `void exit(int)` to map C-style exit calls to Plan 9 `exits`, which can conflict with standard C expectations in other contexts.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/common/sys.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/filterkit/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/filterkit/dat.h

- Role: Shared filterkit address list definition.
- Content: `Addr` singly linked list with `val`, plus `readaddrs` declaration.
- Integration: Used by `deliver.c`, `list.c`, and `readaddrs.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/filterkit/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/filterkit/deliver.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/filterkit/deliver.c

- Role: Delivery helper that appends stdin to a mailbox with locking and logging.
- Control flow: Parses recipient/fromfile/mbox, extracts delivered-to local name, reads sender address, takes mailbox lock, appends `From sender date` plus message content, unlocks, and syslogs delivery.
- Integration: Uses `readaddrs`, `syslock`, `appendfiletombox`, and upas common wrappers.
- Risks/notes: If `syslock` returns nil, delivery continues without checking; mailbox open retries only for exclusive lock errors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/filterkit/deliver.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/filterkit/list.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/filterkit/list.c

- Role: Address-list checker/updater for mail filtering.
- Control flow: Reads pattern files with exact (`=`), regexp (`~`), negated (`!`) entries and `#include`; `check` tests address files; `add` simplifies unmatched addresses and appends patterns.
- Key helpers: `simplify` lowercases and reduces domains to broad regexp patterns; `checkaddr` compiles regexes as needed.
- Integration: Uses `readaddrs`, Plan 9 regexp, String, quoting formatter, and libsec includes.
- Risks/notes: Regexes are compiled on every check rather than cached; source contains offensive comment text unrelated to behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/filterkit/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/filterkit/readaddrs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/filterkit/readaddrs.c

- Role: Reads address tokens from a file into an `Addr` linked list.
- Key functions: `tokenize822` splits on whitespace while respecting double quotes; `readaddrs` reads up to 8 KiB, tokenizes, appends newly allocated address nodes.
- Integration: Shared by filterkit list and deliver tools.
- Risks/notes: Reads only the first 8 KiB of the address file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/filterkit/readaddrs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/filterkit/token.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/filterkit/token.c

- Role: Creates or checks short HMAC-based mail tokens.
- Key functions: `mktoken` masks the time-of-day in `ctime`, computes HMAC-SHA1 with the key, base64 encodes, and returns first 5 chars; `check_token` accepts tokens from the previous 14 days; `create_token` prints today’s token.
- Integration: Uses Plan 9 libsec SHA1/HMAC/base64 and String.
- Risks/notes: 5 base64 chars is a short token; security relies on deployment context and key secrecy.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/filterkit/token.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/fs/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/fs/dat.h

- Role: Core data model for `upas/fs`, the mail-as-filesystem service.
- Key types: `Message` tree with raw/header/body/MIME metadata, RFC822 fields, refs, digest, IMAP UID, POP UIDL; `Mailbox` with lock, refs, root message, version, callbacks, and backend aux data; `Hash` directory lookup entries.
- Constants: Message subfile qid types (`Qbody`, `Qheader`, `Qinfo`, etc.), top/mailbox/control qid types, encoding/disposition enums, and `PATH`/`FILE` qid helpers.
- Integration: Shared by `fs.c`, `imap4.c`, and other mailbox backends.
- Risks/notes: Many fields are raw pointers into message buffers, so lifetime and parse ownership are central correctness constraints.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/fs/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/fs/fs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/fs/fs.c

- Role: Implements the `upas/fs` 9P server exposing mailboxes and message parts as a filesystem.
- 9P flow: `main` sets up mailbox state and mounts/posts a pipe; child `io` reads 9P messages, dispatches through `fcalls`, and writes replies.
- Namespace model: Top directory contains `ctl` and mailboxes; mailbox directories contain message directories and optional `ctl`; message directories expose files such as `body`, `header`, `raw`, `from`, `subject`, `info`, `digest`, and MIME fields.
- Key operations: `rattach`, `rwalk`, `ropen`, `rread`, `rwrite`, `rremove`, `rstat`; control writes support `open`, `close`, and `delete`.
- State management: `Fid` tracks qid, mailbox, message, top-level message ref, open state, and directory-read finger pointer; hash table maps parent qid/name to qids and message/mailbox pointers.
- Message handling: `fileinfo`, `readinfo`, `readheader`, `stringconvert`, and RFC2047 helpers prepare content; body opens trigger decode/convert.
- Background sync: Optional reader process polls mailbox qid/version and `waketime`, then calls `syncmbox`.
- Risks/notes: `checkmboxrefs` aborts on reference mismatch, indicating ref-count invariants are critical. `dowalk` temporarily mutates names at dot suffixes for fallback lookup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/fs/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/fs/imap4.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/fs/imap4.c

- Role: IMAP/IMAPS mailbox backend for `upas/fs`.
- Key backend hooks: `imap4mbox` recognizes `/imap/host[/user[/mailbox]]` and `/imaps/...`, initializes `Mailbox.sync`, `Mailbox.close`, and `Mailbox.ctl`; `imap4sync` dials/logs in, reads server state, fetches new mail, purges deleted mail, and schedules refresh.
- Protocol flow: `imap4cmd` sends tagged commands; `imap4resp` parses tagged/untagged responses, `EXISTS`, `STATUS`, `FETCH`, literal bodies, quoted bodies, UID lists, and errors.
- Message fetch: `imap4read` obtains UID list, reconciles with local messages, pipelines `UID FETCH ... BODY[]` requests, calls `imap4fetch`, parses messages, computes SHA1 digest, and plumbs new/deleted mail.
- TLS/auth: `imap4dial` uses `imaps` with `tlsClient` when required; password obtained via `auth_getuserpasswd`; thumbprints are initialized but active checking is disabled by `if(0 && ...)`.
- Control: Mailbox ctl supports `debug`, `nodebug`, `thumbprint`, and `refresh [seconds]`.
- Risks/notes: Response parser uppercases entire lines, which is safe for IMAP verbs but can alter quoted/literal metadata parsing if not already separated. TLS certificate thumbprint enforcement is disabled in code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/fs/imap4.c -->