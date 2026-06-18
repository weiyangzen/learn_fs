# Group Research: group_187_9front_sources_os_plan9_9front_sys_src_cmd_troff_suftab_c_sources_os_8b394d000c39

Scope confirmed against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. I read every listed file completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/suftab.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/suftab.c

This file is a static suffix-pattern table for troff hyphenation. It defines `Uchar` arrays named by final letter (`sufa`, `sufc`, `sufd`, etc.) and exports `Uchar *suftab[]`, indexed by alphabet position, to locate applicable suffix rules.

Each rule is byte-coded: the first byte encodes length plus flags, and subsequent bytes encode suffix characters, with `0200+ch` marking hyphenation break positions. The comments show the intended word-part pattern, such as `-TION`, `-ABLE`, `-ING`, or `AL-I-ZA-TION`.

There is no executable logic here. It is data consumed by troff’s older hyphenation algorithm. Maintenance risk is mainly semantic opacity: the octal flags and high-bit markers require knowledge of the hyphenation engine to edit safely.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/suftab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/system.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/system.c

This file provides a Plan 9 implementation of `system(char *s)` for troff code that expects a Unix-like `system()` helper.

It forks, runs `/bin/rc -c <command>` in the child, waits for the matching child PID, and returns `0` on empty wait message, `1` on non-empty wait status, and `-1` on fork or wait failure.

The implementation is intentionally small and Plan 9-specific. It ignores waits for unrelated children until the target process exits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/system.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/t10.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/t10.c

This file implements troff’s typesetter output interface. `t_ptinit()` installs troff-mode function pointers, selects the device from `$TYPESETTER` or defaults, reads the device `DESC`, initializes fonts, page dimensions, tab stops, spacing, and special character names.

`t_ptout()` buffers `Tchar` output until newline, normalizes vertical motion, calls `ptout0()` over the buffered line, and emits device output records. `ptout0()` handles motions, point size/height/slant changes, word spaces, XON/XOFF passthrough, drawing functions, simple characters, named characters, width accounting, bold overstriking, and cached metrics.

The file emits classic device-independent troff commands: `x T`, `x res`, `x init`, `H`, `V`, `s`, `f`, `c`, `C`, `N`, `D`, `n`, `p`, trailer, stop, and pause. It depends heavily on globals from `tdef.h`/`ext.h`, especially `oline`, `lead`, `esc`, font state, and character-name tables.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/t10.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/t11.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/t11.c

This file reads troff device and font description files and manages global troff character names. `getdesc()` parses a device `DESC`, loading resolution, motion units, unit width, supported sizes, mounted font labels, and the device charset.

`getfont()` validates and parses font files, loading width, kern, code, space/default widths, special-font status, and ligature support into `Font`/`Chwid` arrays. Character names are installed with `chadd()`, which prefixes stored names with a type byte: multibyte rune, troff named character, or numeric `\N`.

`chname()` resolves internal character numbers back to their type-prefixed names. `getlig()` converts font ligature declarations to bit flags. The file is central to mapping troff logical characters to device widths and output names.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/t11.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/t6.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/t6.c

This file contains troff width, point-size, font, motion, ligature, and font-mount logic. It owns font label caches (`fontlab`), constant spacing tables, bold simulation tables, and special-font fallback state.

`t_width()` computes character or motion widths, honoring zero-width bits, translation tables, current font/size bits, width cache, constant spacing, and bold adjustments. `getcw()` finds a character on the current font or special fonts, falls back to default widths, sets kern state, applies unit scaling, and populates `widcache` when safe.

The file also parses escapes and requests: `t_setch`, `t_setabs`, `caseps`, `t_setps`, `t_setht`, `t_setslant`, `caseft`, `t_setfont`, `t_setwd`, vertical/horizontal motions, half-line motions, ligatures, `.lg`, `.fp`, `.cs`, `.bd`, `.vs`, `.ss`, and `\x`. `setfp()` mounts fonts by reading device font files and notifying the output device.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/t6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/tdef.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff/tdef.h

This is the core troff definition header. It includes Plan 9 libc/std headers, defines site-dependent paths, device defaults, default point size/font/line length/spacing, output-buffer macros, error macros, and large sets of sizing limits.

It defines troff’s internal `Tchar` representation: motion bits, vertical/negative motion, zero-width bit, font and size fields, character bits, masks, and setters/getters. It also defines internal pseudo-characters for escapes, drawing, X commands, optional hyphens, transparent text, word spaces, and related formatter control states.

The header declares major structs: `Blockp`, `Diver`, `Stack`, `Contab`, `Numtab`, `Wcache`, `Tbuf`, `Env`, `Chwid`, `Font`, `Term`, and `Numerr`. It maps environment fields through macros like `lss`, `font`, `word`, and `line`, making this the shared ABI between most troff implementation files.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff/tdef.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff2html/chars.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff2html/chars.h

This header provides character translation tables for `troff2html.c`.

`htmlchars[]` maps UTF-8 characters to HTML entity strings or ASCII fallbacks. It is sorted by Unicode value after runtime initialization because `troff2html.c` fills each entry’s rune value and then binary-searches it.

`troffchars[]` maps troff named characters such as `A*`, `ff`, `em`, `hy`, `mu`, arrows, math symbols, brackets, and rule characters to HTML entities or rough text substitutes. Coverage is pragmatic rather than complete; unsupported troff names return `??` in the caller.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff2html/chars.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff2html/troff2html.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/troff2html/troff2html.c

This program converts device-independent troff output for the `utf` typesetter into HTML. It parses troff output commands, maintains current font, position, point size, indentation, heading/link attributes, and emits HTML through a buffered character stream.

The converter recognizes mounted fonts, font switches, horizontal/vertical positions, simple characters, named characters, X commands, manpage references, paragraph hints, inline HTML hints, and paragraph/heading/bold/italic markers. It ignores drawing commands and approximates spacing/indentation using tables and `&nbsp;`.

It stores output as `Char` values with high-bit attributes, then `flush()` opens and closes HTML tags in a stable nesting order. It is tailored to Plan 9 manpage output generated by `tmac.anhtml`, especially the fixed wide-page convention used to detect no-fill text.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/troff2html/troff2html.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/truetypefs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/truetypefs.c

This program is a 9P file server exposing TrueType fonts as Plan 9 font/subfont files under `/n/ttf`. Font names are expected as `<fontname>.<size>`, resolved under `/lib/font/ttf` by default or `-F fontpath`.

`tryfont()` opens and caches `TTFont` instances. `mksubfonts()` builds a Plan 9 `font` file listing Unicode ranges split into 256-codepoint subfonts. `compilesub()` lazily renders glyphs into Plan 9 subfont bitmap format using libttf glyph metrics and bitmap data.

The 9P handlers support attach, clone, walk, stat, and read. A font directory contains `font` plus generated `s.xxxx-yyyy` subfont files. Data is cached per subfont after first read.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/truetypefs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ttfrender.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ttfrender.c

This is a command-line TrueType text renderer. It reads text from a file or stdin, opens a TTF with a requested pixels-per-em, renders text to a bitmap via `ttfrender()`, optionally scales down for antialiasing, and writes a Plan 9 image to stdout.

Options control alignment/justification, target width/height, ppem, oversampling scale, newline whitespace handling, and crop mode. `elidenl()` normalizes whitespace when requested. `scaledown()` converts oversampled 1-bit render output to grayscale coverage.

`cropwrite()` trims white margins and writes a compact `k8` image. Without crop mode, output is the full rendered grayscale bitmap.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ttfrender.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tweak.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tweak.c

`tweak` is an interactive graphical editor for Plan 9 images, face files, cursor files, and subfonts. It uses libdraw/event/plumb, maintains a linked list of open `Thing` objects, and supports magnified pixel editing plus parent/child edit views.

It can open regular images, legacy hex face files, cursor files, and subfont-bearing image files. `drawthing()` lays out each object, renders magnified pixels, shows metadata, and keeps child edit panes synchronized. Text metadata fields are clickable and editable for file name, depth, rectangle, subfont metrics, offsets, character widths, and magnification.

Mouse interactions support opening subregions or glyphs, twiddling pixels with configurable button values, sweeping/copying pixel regions, inspecting pixel values, writing files back in the original-ish format, re-reading, closing, and opening glyph ranges. It also handles plumber `imageedit` messages and temporary files for `showdata`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tweak.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/uhtml.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/uhtml.c

`uhtml` detects an HTML document’s input character set and converts it to UTF/HTML-safe output through `tcs`. It reads an initial buffer, checks BOMs, scans tags for `encoding=` or `charset=`, and falls back to UTF validation or Latin-1 on rune errors.

With `-p`, it prints the detected charset only. Otherwise it spawns `/bin/rc` running `{tcs -f <charset> || cat} | tcs -f html`, feeds the buffered prefix and remaining stdin through the pipe, and waits.

The attribute parser is simple and tolerant of quoted/unquoted alphanumeric charset values with `-` and `_`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/uhtml.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/unicode.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/unicode.c

This utility converts between Unicode code points and UTF text. Default mode prints UTF characters for hexadecimal code values. `-n` prints numeric code points for input UTF strings. `-t` emits characters without trailing newlines.

It also supports ranges like `0041-005a`, printing code point and character columns, eight per line. Input validation checks hex syntax, `Runemax`, and UTF round-trip validity for `Runeerror`.

Output uses Plan 9 `%C` rune formatting through a `Biobuf`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/unicode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/uniq.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/uniq.c

This is a Plan 9 implementation of `uniq`. It reads adjacent lines, compares them after optional field and character skipping, and prints according to mode.

Supported options include `-u` unique-only, `-d` duplicate-only, `-c` counts, `-s` prefix mode behavior in `equal()`, numeric `-N` field skip, and `+N` character skip. It uses fixed `Bsize` line buffers and exits on too-long lines.

The implementation tracks duplicate counts in `linec` and a `uniq` flag set by successful equality comparisons.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/uniq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/units.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/units.y

This yacc grammar implements the Plan 9 `units` converter. It reads `/lib/units` or a supplied database file, builds named unit definitions and fundamental dimensions, then enters an interactive “you have / you want” conversion loop.

`Node` stores a numeric value plus signed dimension exponents. The grammar supports unit definitions, fundamental dimension declarations with `#`, expressions with addition/subtraction for like units, multiplication/division, implicit multiplication, `|` division, integer exponents, and Unicode superscripts/multiply/divide characters.

The runtime includes unit lookup with metric prefix stripping and plural `s` stripping, special Celsius/Fahrenheit affine conversions, formatted dimension output, overflow/underflow-checked multiply/divide, and error-limited parsing diagnostics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/units.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/unlnfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/unlnfs.c

`unlnfs` restores long filenames from a `.longnames` file. It reads long names, computes each name’s encoded MD5-derived short name with `enc32`, then recursively walks a directory and renames any entry whose name matches the 26-character encoded form.

The mapping list is stored as linked `Name` records. `renamedir()` descends into subdirectories before checking entries for rename candidates. `rename()` uses `dirwstat()` to change the directory entry name.

It exits if `.longnames` cannot be opened. Memory/error handling is minimal but consistent with a small Plan 9 utility.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/unlnfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/unmount.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/unmount.c

This is a small command wrapper around Plan 9 `unmount()`. It accepts either `unmount mountpoint` or `unmount mounted mountpoint`.

The argument order matches `mount`: optional mounted spec first, mount point second. On failure it reports the mount point and `%r`; on success it exits cleanly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/unmount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/Mail/comp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/Mail/comp.c

This file manages Acme compose windows for the `Mail` client. `compose()` creates a new window, writes tags, fills headers, optionally quotes a replied-to message body, records reply metadata, and starts `compmain()`.

`compmain()` handles Acme events for compose windows. `Post` reads the body, pipes it to `/bin/upas/marshal -8`, optionally with savebox and reply path options, marks replied-to messages with the answered flag, renames the compose window to `:Sent`, and marks it clean. `Del` checks the Acme dirty flag and requires a second deletion if composing content is still dirty.

Reply generation uses `respondto()` and `show()` to construct `To`/`CC` fields, deduplicating reply-all addresses.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/Mail/comp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/Mail/mail.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/Mail/mail.h

This header defines the shared data model for the Acme `Mail` program.

It declares `Event`, `Win`, `Comp`, `Mesg`, and `Mbox`. `Win` wraps Acme file descriptors and I/O helpers. `Comp` adds marshal pipe state and reply metadata. `Mesg` stores mailbox identity, open/delete state, threading relationships, multipart parts, and parsed mail headers. `Mbox` stores message arrays, message-id hash table, open windows, plumber channels, view mode, and mailbox path.

It also defines state/flag enums (`Sopen`, `Szap`, `Fseen`, `Ftodel`, etc.), view modes, stack/buffer sizes, globals, and function prototypes for window, message, mailbox, compose, and utility modules.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/Mail/mail.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/Mail/mbox.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/Mail/mbox.c

This is the main mailbox controller for Acme `Mail`. It loads `/mail/fs/<mailbox>`, builds `Mesg` objects, sorts by time, groups messages into threads using `Message-ID`/`In-Reply-To`, tracks dummy placeholders, and keeps a message-id hash table.

It handles plumber channels for new/modified/deleted mail, show-mail requests, and send-mail requests. It also reads Acme mailbox events and dispatches commands: `Put`, `Mail`, `Delmesg`, `Undelmesg`, `Del`, `Redraw`, `Next`, `Mark`, and `Filter`.

Rendering is controlled by `listfmt`, with directives for subject, from, to, cc, reply-to, indentation, child markers, and date formatting. `mbflush()` applies pending deletions to `/mail/fs/ctl`, removes zapped messages, reparents thread children, and updates the Acme buffer. Quit logic protects open message/compose windows and dirty mailbox buffers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/Mail/mbox.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/Mail/mesg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/Mail/mesg.c

This file loads, opens, displays, and manages individual messages. `mesgload()` reads a message `info` file from `/mail/fs`, parses ordered metadata fields, derives flags, date/time, digest, message-id hash, and a display `fromcolon`.

Multipart handling is lazy. `readparts()` recursively scans attachment directories, records parts, and selects a preferred body, favoring `text/plain` then `text/html`. `mesgopenbody()` opens the chosen body directly or pipes HTML through `/bin/htmlfmt -cutf-8`.

`mesgshow()` writes message headers, thread links, body text, and attachment helper commands into an Acme window. Event handling supports `Reply`, `Reply all`, `Delmesg`, `Del`, and `Mark`. Opening a message marks it seen in `/mail/fs` and redraws the mailbox line.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/Mail/mesg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/Mail/util.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/Mail/util.c

This file provides allocation, string, file-slurp, and hash helpers for the Mail client.

`emalloc`, `erealloc`, `estrdup`, `estrjoin`, and `esmprint` wrap allocation and fail with `sysfatal` on OOM. `fslurp()` reads an fd into a NUL-terminated buffer, growing by 1.5x. `rslurp()` opens and reads a file relative to either the mailbox root or a message path.

`strhash()` is a djb2-style byte hash used for message-id lookup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/Mail/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/Mail/win.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/Mail/win.c

This file abstracts Acme window operations. `wininit()` creates a new window under `/mnt/wsys`, names it, disables scroll, opens `event`, `addr`, and `data`, and creates an `Ioproc` for buffered I/O.

`winevent()` parses Acme event records, including expanded text events, and `winreturn()` writes unhandled events back. The file also provides helpers to open window files, write tags, duplicate data as `Biobuf`, close all descriptors, read arbitrary address ranges with UTF-aware trimming, read/set selections, and match message references in clicked text.

This module is the boundary between mailbox/message/compose logic and Acme’s file interface.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/Mail/win.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/alias/aliasmail.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/alias/aliasmail.c

`aliasmail` expands local mail aliases from UPAS alias databases. It lowercases input names, reads system names, selects database files from `namefiles` or `fromfiles`, and translates each requested name.

It searches alias files with support for `#include`, converts `@` addresses to bang format for loop checks, and avoids alias cycles by comparing against local and fully qualified system names. Without a match it emits `local!name`; with `-f` it prints the source system/domain side of the alias instead.

The file mutates argv strings in `mklower()`, which matches old Plan 9 utility style but is worth noting if ported.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/alias/aliasmail.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/addhash.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/addhash.c

`addhash` merges one or more serialized bayes hash tables. Arguments are pairs of `file scale`; each input hash is read with `Breadhash()` and counts are multiplied by the given scale before accumulating into a single `Hash`.

With `-o`, it creates the output file with `DMEXCL`, retrying for up to about two minutes if the file is locked. Without `-o`, it writes the merged hash to stdout.

This is a batch maintenance tool for the older text-hash bayes pipeline.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/addhash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/bayes.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/bayes.c

This program classifies message token hash files against one or more class hash tables. Invocation separates class hashes and message hashes with `~`.

For each message hash, it computes per-token conditional probabilities from class counts normalized by each class’s `*nmsg*`, keeps the most discriminating tokens, multiplies their probabilities per class, normalizes, and outputs the best class and confidence. `-k` appends keyword evidence, `-D` dumps debug evidence, and `-m` controls how many best words are retained.

It uses the custom `Hash`/`Stringtab` serialization from `hash.c`. Low-frequency tokens are biased toward table 0 with fixed fallback probabilities.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/bayes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/dfa.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/dfa.c

This file converts Plan 9 regexp programs (`Reprog`) into minimized deterministic regexp programs (`Dreprog`) and executes or serializes them. It is used by the mail tokenizer for fast repeated matching.

`dregcvt()` counts NFA instructions, computes “interesting” rune boundaries, builds subset-construction states (`Reiset`), follows empty transitions, creates transitions for beginning/end-of-line contexts, minimizes by partition refinement, and emits a compact `Dreprog`.

`dregexec()` runs the DFA and returns the best match length from a string position. `Bprintdfa()` serializes a DFA in text form, while `Breaddfa()` reads that format back with strict error handling. Optional `DUMP` code can print internal DFA structure for debugging.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/dfa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/dfa.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/dfa.h

This header defines the deterministic regexp structures used by the bayes tokenizer.

`Dreinst` stores final/loop flags and a transition case table. `Dreprog` stores four start states for combinations of beginning-of-line and end-of-line context. `Drecase` maps a starting rune boundary to the next instruction.

It declares conversion, execution, read, and write functions: `dregcvt`, `dregexec`, `Breaddfa`, and `Bprintdfa`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/dfa.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/dump.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/dump.c

This is a standalone DFA debugging utility. It compiles a regexp argument with `regcomp()`, converts it with `dregcvt()`, dumps the deterministic transition table, then tests remaining argv strings with `dregexec()`.

The dump shows start-state indexes, transition ranges, target states, final states, and loop states. It is useful for inspecting the classifier regexps used by `msgtok`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/dump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/hash.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/hash.c

This file implements the text hash table used by the older bayes tools. `Stringtab` entries are pooled in large chunks, strings are arena-copied, and `Hash` maintains both a hash table and an `all` linked list.

`findstab()` performs move-to-front lookup, creates entries when requested, and grows/rebuilds the bucket table. `sortstab()` merge-sorts entries lexicographically. `Bwritehash()` writes a `# hash table` format, skipping nonpositive and stale entries older than 30 days. `Breadhash()` reads and scales counts, preserving the newest date.

`freehash()` returns string table nodes to the free list and frees bucket storage. `Bopenlock()` retries opening locked files for up to about two minutes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/hash.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/hash.h

This header defines `Stringtab` and `Hash` for serialized token-count tables.

`Stringtab` stores linked-list and bucket-chain pointers, token bytes/length, count, and date. `Hash` stores sort status, buckets, bucket/table counts, and the all-entry list.

It declares lookup, sorting, serialization, deserialization, cleanup, and lock-retrying open helpers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/hash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/msgclass.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/msgclass.c

`msgclass` is a newer database-backed message classifier. It reads token/count files, loads one or more class databases supplied with `-d name dbfile`, computes the most discriminating tokens, and prints the selected class plus per-class probabilities and token evidence.

Options include `-a` to add the current message tokens to the selected class database, `-l` to hold a lock file while updating, `-m` update multiplier, and `-t` confidence threshold. It uses `Msgdb` from `msgdbx.c`.

Notable implementation issue: in `lockfile()`, the condition `if(strstr(err, "file is locked")==nil && strstr(err, "exclusive lock")==nil))` has an apparent extra closing parenthesis in the source as read, which would be a compile error unless hidden by build-time differences.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/msgclass.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/msgdb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/msgdb.c

This is a command-line utility for inspecting or updating a `Msgdb` token database.

With `-c`, it creates the database if needed. With `-i`, it reads tokens or `token count` lines from stdin and increments/replaces stored counts. Without `-i`, it enumerates the database and prints `token value` lines.

It is a thin wrapper around `mdopen`, `mdget`, `mdput`, `mdenum`, `mdnext`, and `mdclose`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/msgdb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/msgdb.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/msgdb.h

This header declares the opaque `Msgdb` API.

It exposes open, get, put, enumeration reset, next-entry iteration, and close functions. The implementation is in `msgdbx.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/msgdb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/msgdbx.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/msgdbx.c

This file implements `Msgdb` using Plan 9’s Berkeley-style `dbopen()` hash database interface.

Values are stored as four-byte big-endian counts. `mdget()` returns zero for missing or malformed values. `mdput()` deletes entries for nonpositive counts or stores the encoded count otherwise. `mdenum()` resets iteration, and `mdnext()` uses `db->seq()` to return token/count pairs.

The database is opened read-write, optionally with `OCREATE`, using a 2 MB cache size.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/msgdbx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/msgtok.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/msgtok.c

`msgtok` tokenizes RFC822-style messages into classifier features. It loads three precompiled DFAs from `/mail/lib/classify.re`: one for `"From "` message boundaries, one for keyword tokens, and one for ignored spans.

The scanner streams through a 1 KB sliding buffer, tracks header/body state, tags tokens from selected headers with prefixes like `From*`, `To*`, `Subject*`, and `Return-Path*`, emits `*From*` at message starts, and ignores tokens longer than `maxtoklen`.

For each emitted token it also generates normalized variants through `trim()`, prefixed as `stem*...`: stripping punctuation, compressing repeated trailing punctuation, and lowering uppercase/capitalized ASCII forms. Debug mode prints matched spans to stderr.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/upas/bayes/msgtok.c -->