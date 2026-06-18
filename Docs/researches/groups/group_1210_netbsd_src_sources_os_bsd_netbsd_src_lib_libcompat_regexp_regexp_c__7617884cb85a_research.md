# Group Research: group_1210_netbsd_src_sources_os_bsd_netbsd_src_lib_libcompat_regexp_regexp_c__7617884cb85a

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/netbsd-src` is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcompat/regexp/regexp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcompat/regexp/regexp.c

Read completely: 1330 lines.

Implements Henry Spencer’s legacy regular-expression compiler and executor for NetBSD libcompat, exported with compatibility names such as `__compat_regcomp()` and `__compat_regexec()`. The compiler emits a compact bytecode program where each node is an opcode plus a two-byte relative next pointer, with operands stored inline for literals and character classes.

The parser supports anchors, `.`, bracket classes and ranges, grouping, alternation via `|` or newline, `*`, `+`, `?`, escaped literals, and BSD word-boundary escapes `\<` and `\>`. It compiles twice: first to count and validate bytecode size, then to allocate and emit the final `regexp` object. It also extracts optimization hints: required start character, anchoring, and a longest required literal for expensive patterns.

Execution uses global static match state, so calls are not reentrant. Matching is recursive for branches and subexpressions, with iterative handling for simple node chains and greedy `STAR`/`PLUS` through `regrepeat()`. Capturing groups fill the `startp`/`endp` arrays in the compiled object. Risks are mostly historical: global state, recursion/backtracking cost, fixed bytecode-size limit, byte-oriented character handling, and permissive old syntax rather than POSIX regex semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcompat/regexp/regexp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcompat/regexp/regmagic.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libcompat/regexp/regmagic.h

Read completely: 7 lines.

Defines the magic byte `MAGIC` (`0234`) used as the first byte of compiled legacy regexp programs. `regexp.c` writes this before the first node, and `regexp.c`/`regsub.c` validate it before execution or substitution.

The file is intentionally tiny but important for ABI/data-format consistency between the compiler, executor, and substitution helper. A mismatched value would make valid compiled regexps appear corrupt.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcompat/regexp/regmagic.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcompat/regexp/regsub.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcompat/regexp/regsub.c

Read completely: 87 lines.

Implements `__compat_regsub()`, the replacement/substitution helper for Henry Spencer regexp matches. It validates non-null inputs and the compiled regexp magic byte, then copies a replacement template into the caller-provided destination buffer.

Substitution syntax is legacy and minimal: `&` expands to the whole match, `\0` through `\9` expand to captured subexpressions, and escaped `\\` or `\&` emit literal backslash/ampersand. Match text comes from `prog->startp[]` and `prog->endp[]`, which are populated by `__compat_regexec()`.

The destination has no explicit length argument, so callers must provide enough space. It uses `strncpy()` for captured substrings and checks whether a copied NUL implies a damaged match string.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcompat/regexp/regsub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/Makefile

Read completely: 54 lines.

Builds NetBSD `libcrypt`. Core sources are DES/dispatcher `crypt.c`, `md5crypt.c`, `bcrypt.c`, `crypt-sha1.c`, `util.c`, `pw_gensalt.c`, and `hmac_sha1.c`. The build force-includes `namespace.h` to hide imported Argon2 and helper symbols.

When `MKARGON2` is enabled, it defines `HAVE_ARGON2`, adds `crypt-argon2.c`, imports Argon2 upstream source files from `external/apache2/argon2`, disables Argon2 threads with `ARGON2_NO_THREADS`, and marks imported sources hidden. The Makefile installs `crypt.3` and `pw_gensalt.3` manuals and exposes `encrypt`/`setkey` manual links.

It also carries a compiler workaround for `crypt.c` stringop-overflow warnings around DES permutation table initialization and supports unit-test builds through a `.c.test` suffix rule.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/bcrypt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/bcrypt.c

Read completely: 376 lines.

Implements bcrypt password hashing and bcrypt salt generation. It includes `blowfish.c` directly, then uses EksBlowfish setup: initialize Blowfish state, expand with salt and password, repeat key expansion for `2^log_rounds`, encrypt the fixed ciphertext `OrpheanBeholderScryDoubt` 64 times, and encode salt plus ciphertext in bcrypt’s custom base64 alphabet.

`__gensalt_blowfish()` parses the log-round option, clamps it to 4..31, generates 16 random salt bytes with `arc4random()`, and emits `$2a$NN$...`. `bcrypt_gensalt()` is a compatibility wrapper returning a static salt buffer.

`__bcrypt()` validates `$2a$`-style salts, decodes 16 salt bytes, caps passwords at 72 bytes, includes the NUL terminator for minor version `a`, and returns a static `_PASSWORD_LEN` buffer. The function scrubs the Blowfish state before returning, but the static output buffer makes the API non-thread-safe in the traditional `crypt(3)` style.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/bcrypt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/blowfish.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/blowfish.c

Read completely: 495 lines.

Contains the trimmed Blowfish block cipher implementation used only by `bcrypt.c`; it is included directly rather than built as an independent object. It defines `blf_ctx` with four 256-entry S-boxes and eighteen P-subkeys initialized from the standard Blowfish Pi-derived constants.

Implemented helpers include `Blowfish_encipher()`, `Blowfish_initstate()`, `Blowfish_stream2word()`, `Blowfish_expand0state()`, `Blowfish_expandstate()`, and `blf_enc()`. These are exactly the bcrypt-needed operations: initialize state, fold in key material and salt, expand P/S arrays, and encrypt 64-bit block pairs.

The file is crypto core code with no external API boundary in this library. Risks are mostly integration-related: it assumes bcrypt’s byte order and key-stream cycling behavior, and its static functions rely on being included into `bcrypt.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/blowfish.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/crypt-argon2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/crypt-argon2.c

Read completely: 442 lines.

Provides optional Argon2 support for `libcrypt` when `HAVE_ARGON2` is enabled. It supports `$argon2i$`, `$argon2d$`, and `$argon2id$` encodings, parses version and labeled parameters (`m=`, `t=`, `p=`), decodes the unpadded base64 salt, and calls `argon2_hash()` to generate the encoded output.

`estimate_argon2_params()` chooses default memory/time/threads based on `HW_USERMEM64`, `RLIMIT_AS`, and a roughly one-second trial hash loop. It bounds memory coarsely from small systems up to 32 MiB defaults and falls back to conservative values if probing/hash setup fails.

`decode_option()` is permissive about unknown top-level algorithm names, defaulting to Argon2id, but rejects unknown parameter labels. `__crypt_argon2()` uses fixed stack buffers for password, salt, raw hash, and encoded output, then returns a static 512-byte buffer. It wipes temporary buffers but prints Argon2 library failures to stderr, which is unusual for a libc hashing routine.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/crypt-argon2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/crypt-sha1.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/crypt-sha1.c

Read completely: 189 lines.

Implements NetBSD’s `$sha1$` password hash using repeated HMAC-SHA1. The format is `$sha1$<iterations>$<salt>$<digest>`. If the salt lacks the magic prefix, it generates a randomized iteration count using `__crypt_sha1_iterations()`.

`__crypt_sha1_iterations()` treats the provided hint as a maximum-ish value and subtracts a random amount up to one quarter of it, reducing precomputed dictionary reuse. `__crypt_sha1()` builds the initial HMAC input from salt, magic string, and iteration count, then repeatedly HMACs the previous digest with the password as key.

The output digest is encoded using the library’s traditional crypt base64 via `__crypt_to64()`. It returns a static buffer and wipes the HMAC scratch buffer. Salt scanning is bounded by `CRYPT_SHA1_ITERATIONS` rather than the salt-length constant, but output storage effectively limits accepted salt size.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/crypt-sha1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/crypt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/crypt.c

Read completely: 1095 lines.

Central `crypt(3)` implementation and legacy DES engine. `crypt()` calls private `__crypt()` and returns traditional failure sentinels `*0` or `*1` if hashing fails.

At the top level, `__crypt()` dispatches non-DES schemes by parsing the substring between leading `$` separators: `$2a$` to bcrypt, `$sha1$` to SHA1-HMAC, `$1$` to MD5 crypt, and optional `$argon2id$`, `$argon2i$`, or `$argon2d$` to Argon2. Unknown or malformed non-DES schemes fail.

The rest implements classic DES and extended DES. It builds a DES key from up to eight password characters, handles `_PASSWORD_EFMT1` extended DES with a 24-bit iteration count and 24-bit salt, and otherwise uses 25 iterations with a 12-bit salt. `des_setkey()`, `des_cipher()`, `setkey()`, and `encrypt()` provide compatibility DES APIs.

The DES implementation initializes permutation, key-schedule, S/P/E, and final-permutation tables lazily. State such as `KS`, `cryptresult`, and table readiness is static global state, so the classic API is not reentrant. The file also preserves historical invalid-salt behavior while rejecting passwd-format-unsafe salt characters.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/crypt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/crypt.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/crypt.h

Read completely: 32 lines.

Private header for `libcrypt` internals. It marks internal functions with hidden ELF visibility through `crypt_private`, declares hash implementations, salt generators, utility encoders, and optional Argon2 entry points.

It defines `SHA1_MAGIC` as `$sha1$` and `SHA1_SIZE` as 20. This header ties together `crypt.c`, `pw_gensalt.c`, `crypt-sha1.c`, `hmac_sha1.c`, `md5crypt.c`, `bcrypt.c`, `util.c`, and optional Argon2 code without exporting these helper symbols as public ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/crypt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/hmac.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/hmac.c

Read completely: 309 lines.

Generic macro-parametrized HMAC implementation based on RFC 2104. It expects the including file to define `HMAC_FUNC`, `HASH_LENGTH`, `HASH_CTX`, `HASH_Init`, `HASH_Update`, and `HASH_Final`. In this library it is included by `hmac_sha1.c` to produce `__hmac_sha1()`.

The core function hashes oversized keys down to digest length, builds inner and outer pads using `0x36` and `0x5c`, computes `HASH(K xor ipad, text)`, then computes `HASH(K xor opad, inner_digest)` into the caller’s digest buffer.

Under `MAIN` or `UNIT_TEST`, it also includes hex conversion helpers, RFC 2202-style known-answer tests, and a small command-line driver. The production function does not explicitly wipe pad/key scratch buffers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/hmac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/hmac_sha1.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/hmac_sha1.c

Read completely: 20 lines.

Instantiates the generic `hmac.c` template for SHA1. It includes `<sha1.h>` and `crypt.h`, maps `HMAC_FUNC` to `__hmac_sha1`, sets `HASH_LENGTH` to `SHA1_DIGEST_LENGTH`, maps context and init/update/final macros to NetBSD SHA1 routines, and then includes `hmac.c`.

This file exists so the generic HMAC body can be compiled as a concrete hidden `libcrypt` helper for `crypt-sha1.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/hmac_sha1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/md5crypt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/md5crypt.c

Read completely: 148 lines.

Implements Poul-Henning Kamp’s MD5 password hash for `$1$` salts. `__md5crypt()` strips the `$1$` prefix if present, truncates salt at the first `$` or eight characters, and performs the standard MD5-crypt mixing sequence of password, magic, salt, alternate digest, and 1000 strengthening rounds.

The final 16-byte MD5 digest is rearranged into the traditional MD5-crypt base64 order and encoded with `__crypt_to64()`. It returns a static 120-byte password buffer and wipes the final digest before returning.

This is compatibility code for an old password hash. It is not thread-safe because of static storage and is cryptographically obsolete compared with bcrypt/Argon2.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/md5crypt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/namespace.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/namespace.h

Read completely: 94 lines.

Force-included namespace isolation header for `libcrypt`. It remaps imported Argon2, BLAKE2b, Argon2 core/encoding/ref helper symbols, `estimate_argon2_params`, and `getnum` to `__libcrypt_internal_*` names.

This prevents bundled Argon2 implementation symbols from leaking into or conflicting with the public process symbol namespace when `libcrypt` is linked. It is build infrastructure rather than runtime logic, but it is important for ABI cleanliness and avoiding clashes with external Argon2/BLAKE2 libraries.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/namespace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/pw_gensalt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/pw_gensalt.c

Read completely: 300 lines.

Implements `pw_gensalt()`, dispatching named salt types to scheme-specific generators: `old`, `new`/`newsalt`, `md5`, `sha1`, `blowfish`, and optional Argon2 variants. It returns `EINVAL` for unknown types.

The DES generators emit two-character traditional salts or extended DES salts with clamped rounds from 7250 to `0xffffff`. MD5 emits `$1$` plus eight random crypt-base64 characters. SHA1 emits `$sha1$<randomized iterations>$<8 random chars>$`. Blowfish delegates to `__gensalt_blowfish()`.

When Argon2 is enabled, option parsing accepts `m=`, `t=`, and `p=`, fills missing/too-small values with `estimate_argon2_params()`, emits ordered `$argon2*$v=<version>$m=...,t=...,p=...$`, then appends 16 random standard-base64 characters and a trailing `$`. Some buffer-too-small paths return `0` without setting `errno`, reflecting historical API looseness.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/pw_gensalt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/util.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/util.c

Read completely: 91 lines.

Shared `libcrypt` utility helpers. `getnum()` parses an unsigned long with `strtoul()`, accepting `NULL` as zero, rejecting empty or trailing-junk input, and propagating range errors. It stores the result as `size_t`.

`__crypt_to64()` encodes low-order six-bit groups with the traditional crypt alphabet `./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz`. `__crypt_tobase64()` does the same with the standard base64 alphabet used by Argon2 salts.

These helpers are used by salt generators and hash encoders. They append exactly `n` characters and do not NUL-terminate; callers own buffer sizing and terminators.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcrypt/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/EXAMPLES/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/EXAMPLES/Makefile

Read completely: 54 lines.

Developer/example Makefile for building curses demonstration programs from `view.c` and `ex1.c`. It builds variants against local NetBSD curses, system curses, and pkgsrc ncurses, with optional `HAVE_WCHAR` and `NCURSES` defines.

Targets include `wcview`, `nwview`, `ccview`, `tcview`, `ncview`, and `ex1`. It hardcodes `gcc`, include/library paths, rpaths, and optional debug `CFLAGS`, so it is a convenience/example Makefile rather than part of the normal NetBSD bsd.lib build.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/EXAMPLES/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/EXAMPLES/ex1.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/EXAMPLES/ex1.c

Read completely: 342 lines.

Interactive wide-curses exercise program. It initializes locale and curses, replaces `stdscr` with a small custom window, enables cbreak/noecho/scrolling, and then reads raw input commands to exercise many narrow and wide-character APIs.

It tests `add_wch`, `add_wchstr`, `addwstr`, `get_wch`, `get_wstr`, `in_wch`, `in_wchstr`, `inwstr`, `hline_set`, `vline_set`, `border_set`, `box_set`, `bkgrnd`, insertion functions, keypad mode, timeout modes, and basic erase/clear/refresh operations. It constructs `cchar_t` values with multiple elements and attributes to stress combining/nonspacing handling.

This is not polished application code: it uses old-style `main()`, hardcoded multibyte sample strings, fixed buffers, direct `getchar()` in some paths, and manual `delwin()` cleanup. Its role is regression/manual testing for wide curses behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/EXAMPLES/ex1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/EXAMPLES/view.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/EXAMPLES/view.c

Read completely: 527 lines.

Small interactive file viewer adapted from ncurses examples. It reads a file into memory, expands tabs, optionally escapes nonprintable bytes in narrow mode, and stores each line as either `chtype` strings or `cchar_t` strings when `HAVE_WCHAR` is enabled.

The UI initializes curses, optional color, keypad input, nonblocking input, and insert/delete-line optimization. Commands scroll up/down, jump home/end, shift horizontally, set delay modes, and quit. Numeric prefixes repeat motion commands. `show_all()` redraws a status/header line with filename, terminal size, shift, current time, and visible file lines.

Wide-character mode converts multibyte input with `mbrtowc()`, builds complex characters with `setcchar()`, and uses `get_wch()`/`add_wchstr()`. Risks are example-level: fixed maximum lines, minimal allocation failure handling, direct file slurping, and old portability branches for ncurses/NetBSD curses.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/EXAMPLES/view.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/Makefile

Read completely: 226 lines.

Main NetBSD `libcurses` build file. It defines `LIB=curses`, warning level, include paths, optional `DEBUG_CURSES` and `SMALL` flags, dependency on `libterminfo`, installed headers `curses.h` and `unctrl.h`, and the large source list for the curses implementation.

Wide-character support is enabled unless `DISABLE_WCHAR` is defined, adding `cchar.c`, `add_wch.c`, `add_wchstr.c`, `addwstr.c`, `echo_wchar.c`, `ins_wch.c`, `ins_wstr.c`, `get_wch.c`, `get_wstr.c`, `in_wch.c`, `in_wchstr.c`, and `inwstr.c`. Otherwise it defines `DISABLE_WCHAR`.

Most of the file is manual-page `MLINKS`, mapping curses family pages to individual function names. It also builds `fileio.h` from `shlib_version` through `genfileioh.awk` and includes the `PSD.doc` documentation subdirectory.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/Makefile

Read completely: 32 lines.

Documentation Makefile for the curses paper/manual article. It builds article `curses` in section `reference/ref3` from `Master`, dependencies, and formatted C examples.

The `.c.gr` rule uses `TOOL_VFONTEDPR` and filters out `^'wh` lines to generate troff-ready example listings. `intro.2.tbl` is generated from `intro.2` with `TOOL_TBL`. Comments note that vgrind output should not be regenerated casually because it may require patching.

This is documentation build glue, not runtime curses code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/ex1.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/ex1.c

Read completely: 100 lines.

Historical curses documentation example embedded as a C listing with roff-style leading comments. It initializes curses, installs a SIGINT cleanup handler, switches to cbreak/noecho, replaces `stdscr` with a 10x20 window, enables flushing and scrolling, and loops on `getchar()`.

Commands are minimal: `q` quits, `s` enters standout mode, `e` exits standout mode, `r` forces refresh from `curscr`, and any other character is added to the window. `quit()` erases, refreshes, calls `endwin()`, deletes `curscr`/`stdscr`, prints a newline, and exits.

It demonstrates elementary curses lifecycle and output control. It is K&R-era code with implicit `main`, old `crmode()`, and no modern prototypes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/ex1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/ex2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/ex2.c

Read completely: 208 lines.

Historical curses screen-manipulation example for the documentation. It fills the screen with numbered rows and repeated digits, then lets the user manipulate the display using simple commands.

Commands include clearing to end of line/bottom/screen, standout on/off, deleting or inserting a one-digit count of lines, cursor movement, home, full refresh, simulated carriage return with insert line and clear-to-EOL, and quit. When movement goes above or below the screen, it inserts/deletes lines and adjusts a logical base row number to simulate scrolling.

The program demonstrates line insertion/deletion, cursor state, scrolling behavior, and refresh calls. It uses old curses interfaces (`crmode()`), K&R-style `main()`, `getchar()`, fixed command parsing, and minimal bounds validation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/ex2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/life.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/life.c

Read completely: 161 lines.

Partial historical Game of Life demonstration listing for the curses documentation. The file defines a doubly linked `LIST` of live cells, global `Head`, initializes curses, gathers an initial board from the user, and repeatedly calls `prboard()` and `update()`.

Visible functions include `main()`, `die()`, `getstart()`, and `prboard()`. `getstart()` lets users move with vi-like surrounding keys, add/remove cells, load a file, and quit setup; then it scans the screen for live cells and adds them to the linked list. `prboard()` erases, boxes the screen, draws live cells, and refreshes.

The listing references functions not present in this file segment, such as `evalargs`, `adjustyx`, `readfile`, `dellist`, `addlist`, and `update`, implying the documentation excerpt is incomplete or split elsewhere. It is old K&R-style demo code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/life.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/twinkle1.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/twinkle1.c

Read completely: 161 lines.

Curses animation demo that randomly chooses one of four screen patterns and “twinkles” it by drawing all stars in randomized order, then erasing them in another randomized order. Patterns include alternating lines, a border box, checkerboard-like parity, and a center bar.

It initializes curses, ignores cursor placement with `leaveok()`, disables echo/newline translation, and loops forever through `makeboard()`, `puton('*')`, and `puton(' ')`. `puton()` shuffles the `Layout` array and calls `mvaddch()` plus `refresh()` for each position, intentionally exercising many small updates.

Exit is via SIGINT handler `die()`, which moves to the lower-left corner using `mvcur()`, calls `endwin()`, and exits. It is documentation/demo code with fixed 80x24 layout assumptions and random animation behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/twinkle1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/twinkle2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/twinkle2.c

Read completely: 207 lines.

Variant of the twinkle demo that uses lower-level terminal capabilities for output. It initializes curses only enough to get terminal mode and cursor movement, calls termcap/terminfo-style routines such as `tgetent()`, `tgetflag()`, `tgetstr()`, `tputs()`, and direct `mvcur()`/`putchar()` output.

It requires a terminal on stdin, fetches `am`, `ti`, `vs`, and `cl` capabilities, enters terminal initialization/visual mode, clears the screen, then repeatedly generates patterns and writes stars/spaces in randomized order. `puton()` tracks the last cursor position and avoids auto-margin scrolling at the lower-right cell when needed.

This example contrasts curses window drawing with direct terminal-control output. It relies on fixed 80x24 dimensions, global capability strings, and old terminal APIs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/twinkle2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/win_st.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/win_st.c

Read completely: 56 lines.

Documentation excerpt defining the historical internal `WINDOW` structure as `struct _win_st`. Fields include cursor position, max/begin coordinates, flags, character offset, clear/leave/scroll booleans, line storage, first/last changed-column arrays, and linked/original window pointers.

It also defines old internal flag constants such as `_ENDLINE`, `_FULLWIN`, `_SCROLLWIN`, `_FLUSH`, `_FULLLINE`, `_IDLINE`, `_STANDOUT`, and `_NOCHANGE`.

This is explanatory documentation for historical curses internals, not the active NetBSD `WINDOW` definition used by current `libcurses`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/win_st.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/acs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/acs.c

Read completely: 299 lines.

Initializes alternate character set tables for curses line-drawing and symbol characters. Global `_acs_char[]` stores narrow ACS mappings; with wide-character support, `_wacs_char[]` stores `cchar_t` mappings.

`__init_acs()` fills defaults, overlays terminal `acs_chars` pairs from terminfo, emits `ena_acs` if available, and snapshots the result into the `SCREEN`. `_cursesi_reset_acs()` restores globals from a `SCREEN`.

`__init_wacs()` initializes wide ACS defaults. In non-UTF-8 locales it uses character approximations; in UTF-8 it assigns Unicode box-drawing, arrows, bullets, math, and currency symbols and marks corresponding narrow ACS values with `__ACS_IS_WACS`. It then overlays terminfo ACS mappings as `WA_ALTCHARSET` entries. Risks are locale-sensitive behavior and global ACS state shared with screen snapshots.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/acs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/add_wch.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/add_wch.c

Read completely: 114 lines.

Implements the wide-character single-cell add wrappers: `add_wch()`, `mvadd_wch()`, `mvwadd_wch()`, and `wadd_wch()`.

The stdscr and move variants delegate to `wadd_wch()` after optional `wmove()`. `wadd_wch()` validates the window, fetches the current line pointer, and calls the shared internal `_cursesi_addwchar()` with pointers to the window cursor coordinates and `char_interp=1`.

This file is mostly API plumbing. The actual complex behavior for tabs, newlines, nonspacing characters, wide-width continuation cells, dirty ranges, wrapping, and scrolling lives in `addbytes.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/add_wch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/add_wchstr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/add_wchstr.c

Read completely: 301 lines.

Implements wide complex-character string add APIs: `add_wchstr`, `wadd_wchstr`, `add_wchnstr`, movement variants, and core `wadd_wchnstr()`.

Unlike `wadd_wch()`, this family does not wrap. It writes at most `n` `cchar_t` entries, or the whole NUL-terminated sequence for `n == -1`, truncating at the right edge. It handles writing over the middle of an existing wide character by clearing affected continuation cells or moving to the character start for nonspacing additions.

For spacing characters, it clears old nonspacing lists, writes the base wide char and attributes, adds extra elements as nonspacing nodes, marks continuation cells for multi-column width, and updates dirty ranges. For nonspacing characters, it attaches them to the current cell’s `nsp` list. Allocation failures for nonspacing nodes return `ERR`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/add_wchstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/addbytes.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/addbytes.c

Read completely: 650 lines.

Core byte and wide-character insertion engine for curses output. Public wrappers `addbytes`, `waddbytes`, `mvaddbytes`, and `mvwaddbytes` call `_cursesi_waddbytes()`. `__waddbytes()` lets callers supply attributes.

`_cursesi_waddbytes()` validates the window, tracks cursor pointers and line pointer, and either adds narrow bytes through `_cursesi_addbyte()` or, with `HAVE_WCHAR`, converts multibyte input via `mbrtowc()` and sends `cchar_t` values to `_cursesi_addwchar()`.

`_cursesi_addbyte()` handles tabs, newlines, carriage returns, backspace, pasteol wrapping, scroll-region bottom behavior, attributes/colors/background merging, dirty first/last change pointers, and synchronization. `_cursesi_addwchar()` is the wide-character equivalent with handling for control characters, nonspacing character lists, clearing overwritten continuation cells, line-end width overflow, multi-column continuation cells, wrapping, scrolling, background cells, and dirty ranges.

This is a high-risk implementation file because cursor movement, scroll permission, dirty tracking, background attributes, subwindow offsets, and wide-character cell invariants all interact here.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/addbytes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/addch.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/addch.c

Read completely: 129 lines.

Implements narrow `addch` APIs and the low-level `__waddch()` bridge. When macros are not used, it defines `addch()`, `mvaddch()`, and `mvwaddch()` as wrappers around `waddch()` with optional movement.

With `HAVE_WCHAR`, `waddch()` converts `chtype` to `cchar_t` using `__cursesi_chtype_to_cchar()` and delegates to `wadd_wch()`, unifying narrow and wide paths. Without wide support, it fills an `__LDATA` cell with character and attributes and calls `__waddch()`.

`__waddch()` turns the character into a one-byte string and calls `_cursesi_waddbytes()` with interpretation enabled. This file is mostly compatibility/API layering over `addbytes.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/addch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/addchnstr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/addchnstr.c

Read completely: 186 lines.

Implements `chtype` string add APIs: `addchstr`, `waddchstr`, `addchnstr`, movement variants, and core `waddchnstr()`.

The core function computes the number of characters to write from `n` or NUL termination, truncates to the remaining columns on the current line, and does not wrap, matching SUSv2 addchnstr behavior. It groups runs with the same attribute into temporary byte buffers and calls `_cursesi_waddbytes()` with `char_interp=0`, so control characters are written as data rather than interpreted.

It saves and restores the original cursor position after writing. It allocates a temporary `len + 1` buffer; allocation failure or lower-level add failure returns `ERR`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/addchnstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/addnstr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/addnstr.c

Read completely: 173 lines.

Implements narrow string add APIs: `addstr`, `waddstr`, `addnstr`, `mvaddstr`, `mvwaddstr`, `mvaddnstr`, `mvwaddnstr`, and core `waddnstr()`.

Wrappers delegate through `stdscr` or movement to `waddnstr()`. The core computes length using NetBSD/ncurses-compatible semantics: `n >= 0` means at most `n` bytes, while negative means the whole C string. It then calls `waddbytes()` to perform actual output with normal character interpretation.

This file is API glue; wrapping, scrolling, tabs, newline handling, and dirty marking are handled by `addbytes.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/addnstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/addwstr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/addwstr.c

Read completely: 168 lines.

Implements wide-string add APIs for `wchar_t` strings: `addwstr`, `waddwstr`, `addnwstr`, movement variants, and core `waddnwstr()`.

The core validates the window, rejects `n < -1`, computes the number of wide characters to emit from `n` or `wcslen()`, converts each `wchar_t` into a single-element `cchar_t` with the window’s current wide attributes via `setcchar()`, and delegates each character to `wadd_wch()`.

This means all cursor movement, line wrapping, scrolling, nonspacing behavior, and dirty tracking are handled by the shared `wadd_wch()`/`_cursesi_addwchar()` path. It returns `ERR` on invalid movement, conversion failure, or add failure.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/addwstr.c -->