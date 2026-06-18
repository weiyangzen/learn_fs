# Group Research: group_1620_plan9_sources_os_plan9_plan9_sys_src_cmd_troff_suftab_c_sources_os__296380eaf213

This group covers Plan 9 troff internals, troff-to-HTML conversion, small text/unit utilities, an interactive bitmap editor, an old FreeBSD 9P mount utility, and drawterm CPU/exportfs support. The files are mostly command-level code rather than filesystem core code, except the drawterm/exportfs and mount_9fs pieces, which implement 9P-facing client/export functionality.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/suftab.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/suftab.c

Read fully: 612 lines, 19337 bytes. SHA-256 prefix: `f5f174e8a1b058ce`.

This is a static suffix-pattern table for troff hyphenation. It defines `Uchar` arrays `sufa`, `sufc`, `sufd`, `sufe`, `suff`, `sufg`, `sufh`, `sufi`, `sufk`, `sufl`, `sufm`, `sufn`, `sufo`, `sufp`, `sufr`, `sufs`, `suft`, and `sufy`, then indexes them through `suftab[]` by final letter.

The data encodes suffixes and preferred hyphenation points with high-bit-marked characters and flag bits in the leading length byte. Comments document examples such as `-TION`, `-ABLE`, `-ING`, `-NESS`, `-BILITY`, and many other English endings.

Integration: consumed by troff’s hyphenation algorithm, alongside exception lists and TeX-style hyphenation support. There is no executable logic in this file.

Risk notes: this is compact, hand-maintained table data. Any edit needs to preserve the encoded byte convention, zero terminators, and `suftab[]` letter alignment.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/suftab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/t10.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/t10.c

Read fully: 514 lines, 9498 bytes. SHA-256 prefix: `0ce481e7bd725421`.

This is troff’s typesetter-output interface. `t_ptinit()` installs troff-specific function pointers, reads the device `DESC`, emits initial `x T`, `x res`, and `x init` commands, mounts fonts, initializes tabs/page geometry, and installs special character names.

Important routines:
- `t_ptout()` buffers output line characters until newline, then emits movement and character commands.
- `ptout0()` handles motions, size/font changes, `\X` pass-throughs, character output, drawing commands, bold overstriking, constant spacing, and zero-width characters.
- `ptchname()` serializes named characters as UTF/multibyte, numeric `N`, or troff `C` names.
- `ptflush()`, `ptps()`, `ptfont()`, `ptlead()`, `ptesc()`, `ptpage()`, `pttrailer()`, `ptstop()`, and `t_ptpause()` maintain typesetter state and page/trailer protocol.

Integration: depends on width/font state from `t6.c`, font/device data from `t11.c`, and shared globals/macros from `tdef.h`.

Risk notes: output position state is split across `hpos`, `vpos`, `esc`, and `lead`; incorrect updates desynchronize generated device output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/t10.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/t11.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/t11.c

Read fully: 256 lines, 7097 bytes. SHA-256 prefix: `8e9bb243efafafbc`.

This file parses troff device and font description files. It owns global character-name storage (`chnames`, `nchnames`), point-size tables (`pstab`, `nsizes`), and mounted font records (`fonts`).

Important routines:
- `getdesc()` reads a device `DESC`, extracting resolution, horizontal/vertical motion units, unit width, sizes, mounted fonts, and global charset names.
- `checkfont()` sanity-checks likely font description files.
- `getfont()` reads font metadata and charset rows, building per-character width/kern/code arrays and ligature/default/space width data.
- `chadd()` and `chname()` maintain the global character-name table with type prefixes for UTF, troff names, and numeric `\N` names.
- `getlig()` maps ligature names into `LFI`, `LFL`, `LFF`, `LFFI`, and `LFFL`.

Integration: `t6.c` uses loaded `Font` width tables, and `t10.c` uses character names to emit device commands.

Risk notes: fixed-size temporary arrays (`MAXCH`, `MAXPS`, 100-byte fields) mean malformed or very large font files can hit historical limits.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/t11.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/t6.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/t6.c

Read fully: 883 lines, 15446 bytes. SHA-256 prefix: `2575aa22d1adf149`.

This file implements troff width, font, point-size, motion, and spacing behavior. It is the main bridge between parsed character tokens and mounted font/device metrics.

Important routines:
- `t_width()` returns character or motion width, consulting translations, current font/size bits, and `widcache`.
- `getcw()` computes widths from `Font` tables, special fonts, bold simulation, constant spacing, and default widths.
- `t_setch()` and `t_setabs()` parse named `\(xx`/`\C'...'` and numeric `\N'...'` characters.
- `t_findft()`, `caseft()`, `t_setfont()`, `casefp()`, and `setfp()` resolve and mount fonts.
- `caseps()`, `t_setps()`, `findps()`, and `t_mchbits()` manage point sizes and encoded size/font bits.
- `t_setwd()` implements `\w`, updating width, baseline, height, and horizontal position registers.
- `t_mot()`, `t_vmot()`, `t_hmot()`, `t_sethl()`, and `t_makem()` encode motions.
- `getlg()`, `caselg()`, `casecs()`, `casebd()`, `casevs()`, `casess()`, and `t_xlss()` handle ligatures and spacing requests.

Risk notes: width caching depends on current font/point-size state and must be invalidated by font/spacing changes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/t6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/tdef.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/tdef.h

Read fully: 674 lines, 18401 bytes. SHA-256 prefix: `2aa89e43962c9104`.

This is troff’s central private definition header. It establishes site paths, default device names, starting typesetting parameters, array limits, internal control characters, Tchar bit layout, block-based macro/string storage, and the main shared structures.

Key definitions:
- `Tchar` internal character/motion encoding, with `MOT`, `VMOT`, `NMOT`, `ZBIT`, size/font masks, and `cbits`/`sbits`/`fbits` helpers.
- Internal control characters such as `DRAWFCN`, `XON`, `XOFF`, `WORDSP`, `HX`, `FLSS`, and motion marker `MOTCH`.
- Storage types `Blockp`, `Diver`, `Stack`, `Contab`, `Numtab`, `Env`, `Font`, `Chwid`, `Term`, and `Numerr`.
- Environment-field macros mapping names like `pts`, `font`, `line`, `word`, `tabtab`, and `lss` into `envp`.
- Device/font constants and limits such as `NCHARS`, `MAXFONTS`, `NTAB`, `NDI`, `NTRTAB`, and buffer sizes.

Integration: included by the troff implementation files and tightly coupled to matching environment layout in initialization code.

Risk notes: comments explicitly warn that `struct Env` must stay synchronized with `ni.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff/tdef.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff2html/chars.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/troff2html/chars.h

Read fully: 196 lines, 3957 bytes. SHA-256 prefix: `8d91abd68a233f57`.

This header supplies character mapping tables for `troff2html.c`.

It defines:
- `htmlchars[]`: UTF-8 characters mapped to HTML entities or ASCII approximations. `troff2html.c` computes each entry’s Unicode value at startup and sorts by that value for binary lookup.
- `troffchars[]`: unsorted troff special-character names mapped to HTML strings or ASCII approximations, covering ligatures, dashes, fractions, copyright/registered marks, math operators, arrows, brackets, and line-drawing fallbacks.

Integration: included directly after `Htmlchar` and `Troffchar` type declarations in `troff2html.c`.

Risk notes: `htmlchars[]` is source-sorted by Unicode value but still re-sorted at startup. `troffchars[]` is linear-searched and returns `"??"` for unknown names.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff2html/chars.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff2html/troff2html.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/troff2html/troff2html.c

Read fully: 795 lines, 14275 bytes. SHA-256 prefix: `620cad355d16e3a0`.

This command converts troff device output, especially man-page output prepared for HTML, into HTML. It parses emitted typesetter directives, tracks font and layout state, buffers attributed characters, and flushes them with properly nested tags.

Important behavior:
- `main()` handles `-d` and `-t`, initializes character mappings, emits header, processes files/stdin, then emits trailer.
- `emit()`, `emitstr()`, and `flush()` buffer runes, magic strings, paragraph markers, and active attributes.
- `setattr()` manages nested HTML tags for indent tables, headings, anchors, italic, bold, and constant-width text.
- `xcmd()` handles troff `x` commands for font mounting, resolution/type checks, inline HTML, man-page paragraph markers, headings, and man-reference anchors.
- `process()` parses troff output commands (`c`, `C`, `f`, `h`, `n`, `p`, `s`, `H`, `V`, `x`, etc.).
- `mountfont()` and `switchfont()` map troff font names to HTML styling bits.

Risk notes: the converter is tuned to `tmac.anhtml` conventions and uses heuristic indentation and line-break behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/troff2html/troff2html.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tweak.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tweak.c

Read fully: 2048 lines, 39188 bytes. SHA-256 prefix: `d3f6e8c1e7bffdd7`.

`tweak` is an interactive bitmap, cursor, face-file, and subfont editor built on Plan 9 draw/event APIs. It opens images/subfonts, displays them with optional magnification, edits pixels, edits metadata fields, copies regions, writes files, reloads files, and opens subfont character slices as child edit panes.

Core model:
- `Thing` represents an opened image/subfont or child edit view, with image, subfont, filename, regions, selected character, parent, modified flag, magnification, and subfont offset.
- Global UI regions divide control, edit, and text/status areas.
- `values[]` and `greyvalues[]` cache one-pixel images for color drawing.

Important routines:
- `tget()` detects normal image, cursor, and face-file formats and loads them.
- `drawthing()`, `redraw()`, `drawall()`, `text()`, and message helpers render the UI.
- `textedit()` edits filename, depth, rectangle, subfont metrics, character metrics, offset, count, and image width.
- `openedit()`, `twiddle()`, `twidpix()`, and `ckinfo()` implement character/region editing and update subfont top/bottom bounds.
- `twrite()`, `tread()`, `tclose()`, `tchar()`, `copy()`, `tpixels()`, and `menu()` implement user commands.

Risk notes: it assumes Plan 9 GUI/event semantics and mutates parent/child image state manually; many updates require careful redraw and ownership handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tweak.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unicode.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unicode.c

Read fully: 127 lines, 2079 bytes. SHA-256 prefix: `1df8a47aeab95c3c`.

This is a small Unicode conversion utility. Usage supports three modes:
- hex code points to UTF-8 characters,
- ranges `hexmin-hexmax` to code-point/character listings,
- `-n` or non-hex input to print numeric Unicode values for UTF-8 text.

Functions:
- `range()` parses and validates hex ranges, printing six-digit hex code points and `%C` characters in rows.
- `nums()` walks UTF-8 strings with `chartorune()`, validates genuine `Runeerror` encodings, and prints code points.
- `chars()` parses individual hex values and prints `%C`, with `-t` suppressing newlines for text output.

Integration: uses Plan 9 rune and Bio APIs.

Risk notes: range mode is selected when the first argument contains `-` and `-n` is not set; invalid input returns descriptive exit strings.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unicode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/uniq.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/uniq.c

Read fully: 165 lines, 2185 bytes. SHA-256 prefix: `8c7ba1126a9a7c8b`.

This is Plan 9’s `uniq` implementation for adjacent duplicate lines.

Behavior:
- Options parsed in historical style: `-<number>` skips fields, `+<number>` skips characters after fields, and `-u`, `-d`, `-c`, `-s` set output/comparison modes.
- Reads from stdin or one file using `Biobuf`.
- `gline()` reads newline-delimited records into fixed-size buffers.
- `equal()` compares lines after optional field/letter skipping; mode `s` treats a shorter first line ending at NUL as equal.
- `pline()` prints all, unique-only, duplicate-only, or counted output depending on `mode`.
- `skip()` advances past fields and letters for comparison.

Risk notes: only adjacent duplicates are considered. Lines longer than `SIZE` cause a fatal error; allocated buffers are not resized despite `bsize` being a variable.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/uniq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/units.y -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/units.y

Read fully: 786 lines, 10979 bytes. SHA-256 prefix: `1827c4bd74cb6c31`.

This is the yacc grammar and evaluator for Plan 9 `units`. It reads a units database, builds dimensional expressions, then interactively converts “you have” and “you want” quantities.

Core structures:
- `Node`: numeric value plus up to `Ndim` signed dimension exponents.
- `Var`: hashed unit name to `Node`.
- `Prefix`: metric prefix table, including Greek micro.

Grammar supports definitions (`: name expr`), fundamental dimensions (`: name #`), queries (`? expr`), arithmetic, implicit multiplication, division, powers, superscript 1/2/3, and parenthesized expressions.

Important routines:
- `yylex()` tokenizes runes, names, numeric values, multiplication/division symbols, and superscripts.
- `lookup()` hashes names and resolves metric prefixes/plural `s` suffixes.
- `add()`, `sub()`, `mul()`, `div()`, and `xpn()` compute values and dimensions.
- `specialcase()` handles Celsius/Fahrenheit offset conversions.
- `Ufmt()` prints values with numerator and denominator dimensions.
- `fmul()` and `fdiv()` guard overflow/underflow with logarithms.

Risk notes: the dimensional limit is fixed at 15, names at 40 runes, and query state alternates by line number.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/units.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/9pfreebsd/mount_9fs/9auth.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/9pfreebsd/mount_9fs/9auth.h

Read fully: 159 lines, 4612 bytes. SHA-256 prefix: `d9c295f96404fa17`.

This header defines legacy Plan 9 authentication constants, wire structures, and prototypes for the FreeBSD 9FS mount utility.

Definitions include:
- Length constants for DES keys, challenges, domains, secrets, APOP, MD5, and key database entries.
- Auth message numbers such as `AuthTreq`, `AuthChal`, `AuthOK`, `AuthErr`, `AuthTs`, `AuthTc`, `AuthAs`, and `AuthAc`.
- Wire structs `Ticketreq`, `Ticket`, `Authenticator`, `Passwordreq`, `Nvrsafe`, `Chalstate`, `Apopchalstate`, `Chapreply`, and `MSchapreply`.
- Conversion/authentication function prototypes for tickets, authenticators, password requests, challenge/response, login, and SSL negotiation.

Integration: `crypt.c` uses `U9AUTH_DESKEYLEN`; `mount_9fs.c` uses `passtokey()`-compatible DES key material and auth constants.

Risk notes: these are old DES-era Plan 9 auth formats and not modern cryptographic interfaces.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/9pfreebsd/mount_9fs/9auth.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/9pfreebsd/mount_9fs/9fs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/9pfreebsd/mount_9fs/9fs.h

Read fully: 219 lines, 8290 bytes. SHA-256 prefix: `a5e4551be7db6fdd`.

This header defines FreeBSD-side 9FS mount arguments and kernel-facing state, derived from old BSD NFS headers.

Key content:
- Mount option flags such as `U9FSMNT_SOFT`, `U9FSMNT_INT`, `U9FSMNT_KERB`, and `U9FSMNT_READAHEAD`.
- `struct p9user`, mapping Unix UIDs to Plan 9 names.
- `struct u9fs_args`, passed to `mount()`, containing server socket info, sizes, hostname, auth server info, username, DES key, and user mappings.
- `struct u9fsnode`, a vnode-private node with cached attributes, mode cache, fid pointer, vnode pointer, lock/error flags, and legacy disabled NFS fields.
- `struct u9fsmount`, mount-private socket and size state.
- Macros converting vnode/mount pointers to 9FS structures.

Integration: used by `mount_9fs.c` and expected by a matching FreeBSD kernel `u9fs` module.

Risk notes: much of the layout and comments are inherited from NFS and include disabled or stale fields.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/9pfreebsd/mount_9fs/9fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/9pfreebsd/mount_9fs/9p.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/9pfreebsd/mount_9fs/9p.h

Read fully: 226 lines, 4707 bytes. SHA-256 prefix: `949c1cd13d5710ef`.

This header defines old 9P message constants and request structures for FreeBSD 9FS support.

Key content:
- Fixed wire sizes: auth, name, ticket, error, domain, challenge, directory, and max data sizes.
- Open mode and permission macros.
- `struct u9fd_qid`, `struct u9fsreq`, and `struct u9fsdir`.
- Request union fields for flush, attach, session, create/walk/open, read/write, and stat messages.
- Message type enum from `Tnop`/`Rnop` through `Ttunnel`/`Rtunnel`.
- `u9p_types[]`, a static type-name table.
- Serialization prototypes for memory and mbuf forms: `u9p_m2s`, `u9p_s2m`, `u9p_m2d`, `u9p_d2m`, and related mbuf helpers.

Integration: consumed by the FreeBSD kernel/client side and included by `mount_9fs.c`.

Risk notes: it describes pre-9P2000 fixed-length messages, not modern 9P2000 variable-length strings.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/9pfreebsd/mount_9fs/9p.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/9pfreebsd/mount_9fs/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/9pfreebsd/mount_9fs/Makefile

Read fully: 21 lines, 412 bytes. SHA-256 prefix: `a20b3d49e9eb2fc0`.

This BSD makefile builds the FreeBSD `mount_9fs` command.

It sets:
- `PROG=mount_9fs`
- sources `mount_9fs.c`, `getmntopts.c`, and `crypt.c`
- man page `mount_9fs.8`
- debug-oriented `CFLAGS = -ggdb -O0`
- include path and `-DNFS` from `/usr/src/sbin/mount`
- optional Kerberos libraries when present and enabled
- standard `.include <bsd.prog.mk>`

Risk notes: despite the target name, it depends heavily on FreeBSD NFS mount support files and conditionals.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/9pfreebsd/mount_9fs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/9pfreebsd/mount_9fs/crypt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/9pfreebsd/mount_9fs/crypt.c

Read fully: 415 lines, 18042 bytes. SHA-256 prefix: `c0d0f0af0350efa4`.

This file implements the DES block cipher routines needed by old Plan 9 password/key handling.

Important routines:
- `encrypt9()` destructively encrypts a buffer of at least 8 bytes using Plan 9’s overlapping 7-byte stepping convention.
- `decrypt()` reverses the same convention from the end of the buffer.
- `block_cipher()` performs 16 DES rounds using combined S/P-box lookup tables.
- `ip_low()`, `ip_high()`, and `fp()` implement initial/final permutations.
- `key_setup()` expands a 7-byte Plan 9 DES key into the 128-byte internal round-key table.

Integration: `mount_9fs.c` uses `passtokey()` and `encrypt9()` to derive a Plan 9-compatible DES key from a password.

Risk notes: this is legacy DES code. It also relies on assumptions about `long` width and signed byte behavior typical of the original environment.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/9pfreebsd/mount_9fs/crypt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/9pfreebsd/mount_9fs/mount_9fs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/9pfreebsd/mount_9fs/mount_9fs.c

Read fully: 1045 lines, 25118 bytes. SHA-256 prefix: `42739908fca7f8c6`.

This is a FreeBSD mount helper adapted from `mount_nfs.c` for a 9FS/u9fs filesystem. Large portions of NFS option handling and Kerberos scaffolding remain, but the active path builds `struct u9fs_args` for a 9P-style mount.

Important behavior:
- Parses many NFS-style options, plus `-u user[@authhost]` to set Plan 9 username and auth address.
- `getnfsargs()` accepts `host:path` or `path@host`, resolves the server, sets port `U9FS_PORT`, fills socket/mount args, prompts for a Plan 9 password, derives a DES key, and loads `/etc/9uid.conf`.
- `load_9uid()` builds UID-to-Plan 9-name mappings.
- `passtokey()` converts a password into a Plan 9 DES key using `encrypt9()`.
- `load_9key()` prompts with `getpass()`.
- `gethostaddr()` resolves numeric or named hosts.
- `xdr_dir()` and `xdr_fh()` are retained NFS mount RPC helpers, mostly disabled in the active code.

Risk notes: the command still reports NFS usage text, has disabled NFS mount-protocol sections, and contains an `XXX` in Kerberos encryption code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/9pfreebsd/mount_9fs/mount_9fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/Makefile

Read fully: 75 lines, 1165 bytes. SHA-256 prefix: `067ab30d37cd2be9`.

This is the top-level drawterm makefile. It includes `Make.config`, builds object files for main CPU/readconsole/secstore/factotum support, and links a large set of static Plan 9 compatibility libraries.

Key targets:
- `$(TARG)` links `$(OFILES)` with repeated `$(LIBS1)` and `libmachdep.a`.
- Pattern rule compiles `%.c` to `%.$O`.
- `clean` removes object archives and drawterm binaries.
- Recursive targets build `kern`, `exportfs`, auth/authsrv, crypto/math, memdraw/memlayer/draw, GUI backend, libc, and libip.

Risk notes: comment “stupid gcc” explains repeating libraries to satisfy link ordering.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/args.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/args.h

Read fully: 20 lines, 709 bytes. SHA-256 prefix: `8d3fa47b883657cc`.

This header provides Plan 9-style argument parsing macros for drawterm.

It defines:
- external `argv0`
- `ARGBEGIN` / `ARGEND`
- `ARGF()` for optional attached/next-argument option values
- `EARGF(x)` for required option values with fallback expression
- `ARGC()` for the current rune option character

Integration: used by `cpu.c` and `cpu-bl.c` to parse drawterm command-line options while preserving Plan 9 coding style.

Risk notes: these macros mutate `argc`/`argv` and local hidden variables, so they depend on conventional usage shape.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/args.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/cpu-bl.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/cpu-bl.c

Read fully: 730 lines, 14388 bytes. SHA-256 prefix: `18e665a404a49810`.

This is the Bell Labs-default variant of drawterm’s CPU client connection code. It dials a CPU server, negotiates authentication/encryption, sends optional command and working directory, waits for remote export setup, then runs local `exportfs()` over the connection.

Important behavior:
- Defaults `authserver` to `p9auth.cs.bell-labs.com` and `system` to `plan9.bell-labs.com`.
- Supports options for auth server, CPU server, clear/encrypted algorithms, command, key spec, root base, secstore, and user.
- `mountfactotum()` tries to mount factotum and falls back to secstore retrieval.
- `rexcall()` dials TCP port `17010`, negotiates auth method and algorithms, then calls the selected auth method.
- `netkeyauth()` implements manual challenge/response.
- `p9auth()` runs `p9any`, exchanges nonces, derives SHA1 secrets, and pushes SSL/RC4 if enabled.
- `p9any()` uses factotum if available, otherwise performs p9sk1 ticket/authenticator exchange manually.

Risk notes: server-side auth functions are stubs returning `-1`; this is client-focused.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/cpu-bl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/cpu.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/cpu.c

Read fully: 731 lines, 14259 bytes. SHA-256 prefix: `5c7f3e5c3c14214c`.

This is drawterm’s normal CPU client connection code. It is nearly identical to `cpu-bl.c`, but defaults `authserver` to `auth` and `system` to `cpu`, making it suitable for local/site configuration.

Main flow:
- `cpumain()` sizes exportfs messages from `/dev/draw`, parses options, determines user/auth/cpu/secstore settings, mounts factotum or fetches secstore data, connects with `rexcall()`, sends command and current directory, waits for remote `FS` and `/` markers, replies `OK`, then calls `exportfs(data, msgsize)`.
- `p9auth()` performs p9any authentication and optional SSL wrapping.
- `p9any()` delegates to factotum when possible, otherwise performs manual p9sk1 ticket exchange.
- `askuser()`, `promptforkey()`, and `sendkey()` collect missing key attributes and add them to factotum.

Risk notes: command building uses repeated `strcat()` into a fixed `MaxStr` buffer, matching historical assumptions rather than robust argv sizing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/cpu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/drawterm.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/drawterm.h

Read fully: 13 lines, 472 bytes. SHA-256 prefix: `dca4c99cfd4ee707`.

This small header declares cross-module drawterm entry points and globals.

It exposes secstore/auth helpers, console input, exportfs, user/key lookup helpers, factotum dialing, user lookup, and `cpumain()`.

Integration: included by CPU/auth-related drawterm files to share interfaces without a larger public header.

Risk notes: it is purely declarations and relies on matching definitions across the drawterm portability tree.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/drawterm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/exportfs/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/exportfs/Makefile

Read fully: 16 lines, 200 bytes. SHA-256 prefix: `43b63e6454b4980d`.

This makefile builds drawterm’s `libexportfs.a`.

It includes `../Make.config`, sets `LIB=libexportfs.a`, compiles `exportfs.$O` and `exportsrv.$O`, archives them with `$(AR) r`, and runs `$(RANLIB)`. The pattern rule compiles local C files with configured compiler flags.

Integration: invoked by the top-level drawterm makefile’s `exportfs/libexportfs.a` target.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/exportfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/exportfs/exportfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/exportfs/exportfs.c

Read fully: 511 lines, 8414 bytes. SHA-256 prefix: `32a938bacbd12b80`.

This file is the front end and state manager for drawterm’s 9P export service. It reads 9P messages from the CPU connection, dispatches them, tracks fids/files/qids, and sends replies.

Important routines:
- `exportfs()` installs the 9P handler table, initializes work buffers, fid hash, formatting, root file state, then loops on `read9pmsg()` and `convM2S()`.
- `reply()` builds `R*` or `Rerror` messages and writes them to the network.
- `newfid()`, `getfid()`, and `freefid()` manage fid hash entries and file references.
- `getsbuf()` allocates/reuses `Fsrpc` work buffers lazily.
- `file()`, `freefile()`, `initroot()`, and `makepath()` maintain a cached file tree rooted at `.`.
- `uniqueqid()`, `qidlookup()`, `qidexists()`, and `freeqid()` create stable unique exported qids when local dev/type/path combinations collide.
- `fatal()` reports and exits.

Risk notes: several locking and child-process note paths are commented out; this version relies on drawterm’s local runtime assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/exportfs/exportfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/exportfs/exportfs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/exportfs/exportfs.h

Read fully: 148 lines, 2738 bytes. SHA-256 prefix: `85480938cf1a5c94`.

This is the private header for drawterm’s exportfs library.

It defines:
- `Fsrpc`, holding a pending 9P request, buffer, process/flushtag state, and interrupt flag.
- `Fid`, mapping 9P fid numbers to local file descriptors and cached `File` nodes.
- `File`, a cached path tree node with qid and parent/child links.
- `Proc`, tracking blocking slave worker processes.
- `Qidtab`, mapping local qids to unique exported qid paths.
- Limits for worker count, fid hash size, fid chunk allocation, pseudo mount points, and qid hash size.
- Error string aliases, global state declarations, request handler prototypes, utility prototypes, and no-op `notify`/`noted`/`exits` macros for this portability context.

Integration: included with `Extern` defined differently by `exportfs.c` and `exportsrv.c`.

Risk notes: this header controls global ownership conventions across both exportfs implementation files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/exportfs/exportfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/exportfs/exportsrv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/exportfs/exportsrv.c

Read fully: 676 lines, 11048 bytes. SHA-256 prefix: `f6be7b01ce2762f0`.

This file implements drawterm exportfs’s 9P request handlers and blocking I/O worker path.

Handlers:
- `Xversion()` negotiates `9P2000` and message size.
- `Xauth()` rejects auth because authentication is handled before exportfs.
- `Xflush()` marks or replies to flush requests.
- `Xattach()` attaches fids to the exported root.
- `Xwalk()` walks path elements, cloning fids when requested.
- `Xclunk()`, `Xstat()`, `Xcreate()`, `Xremove()`, and `Xwstat()` map 9P operations to local Plan 9 file operations.
- `slave()` starts/reuses worker processes for potentially blocking `Topen`, `Tread`, and `Twrite`.
- `blockingslave()` dispatches to `slaveopen()`, `slaveread()`, and `slavewrite()`.
- `flushaction()` handles notes in the worker context.

Risk notes: comments acknowledge races and unimplemented mount traversal (`openmount()` returns an error). This is sufficient for drawterm’s exported namespace use case, not a general hardened 9P server.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/exportfs/exportsrv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/Makefile

Read fully: 19 lines, 220 bytes. SHA-256 prefix: `c1568f24931ca68a`.

This makefile builds the OS X GUI backend archive `libgui.a` for drawterm.

It includes `../Make.config`, compiles `alloc`, `cload`, `draw`, `load`, and `screen` objects, archives them, and runs `ranlib`.

Integration: invoked by the top-level drawterm makefile through `gui-$(GUI)/libgui.a`.

Risk notes: only the small wrapper files listed in this group were in scope; `load.c` and `screen.c` are referenced but not part of this batch.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/alloc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/alloc.c

Read fully: 23 lines, 286 bytes. SHA-256 prefix: `9a9d5e565ce7dc5c`.

This file provides public memdraw allocation wrappers for the OS X GUI backend.

Functions:
- `allocmemimage()` calls `_allocmemimage()`.
- `freememimage()` calls `_freememimage()`.
- `memfillcolor()` calls `_memfillcolor()`.

Integration: supplies expected libdraw/memdraw symbols while delegating to underscored internal implementations.

Risk notes: no logic beyond direct forwarding.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/cload.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/cload.c

Read fully: 10 lines, 188 bytes. SHA-256 prefix: `cd64e127ed8664bf`.

This file provides the OS X GUI backend wrapper for compressed image loading.

Single function:
- `cloadmemimage()` delegates to `_cloadmemimage()` with the same image, rectangle, data pointer, and byte count.

Integration: exposes the expected memdraw API name for code linked against this GUI backend.

Risk notes: no validation or transformation is performed here.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/cload.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/draw.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/draw.c

Read fully: 22 lines, 365 bytes. SHA-256 prefix: `ab2e1a1b8e32dfc6`.

This file provides OS X GUI backend wrappers around internal memdraw drawing helpers.

Functions:
- `memimagedraw()` calls `_memimagedrawsetup()` and passes the result to `_memimagedraw()`.
- `pixelbits()` delegates to `_pixelbits()`.
- `memimageinit()` delegates to `_memimageinit()`.

Integration: bridges public memdraw-style symbols to underscored internal implementations for the drawterm OS X GUI library.

Risk notes: direct forwarding only; correctness depends entirely on the internal memdraw implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/draw.c -->