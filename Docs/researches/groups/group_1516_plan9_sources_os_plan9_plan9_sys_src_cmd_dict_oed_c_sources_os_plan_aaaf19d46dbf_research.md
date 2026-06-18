# Group Research: group_1516_plan9_sources_os_plan9_plan9_sys_src_cmd_dict_oed_c_sources_os_plan_aaaf19d46dbf

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`. I read each listed source file completely. This group covers Plan 9 dictionary backends, the Plan 9 `diff` implementation, ISO 9660 image/dump tooling, and two standalone disk utilities.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/oed.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/oed.c

Implements the `dict` backend for the Oxford English Dictionary 2nd Edition. It translates OED SGML-like tags and entity names into Plan 9/Unicode output through the common `dict.h` callback contract: `oedprintentry`, `oednextoff`, and `oedprintkey`.

The file is mostly format tables and a parser. `tagtab` maps OED tags such as `hw`, `s1`, `etym`, `pr`, `gk`, `ph`, and quote/sense tags to internal enum values. `auxtab` parses tag attributes including sense number and status. `spectab` maps hundreds of entity names to Unicode runes, private ligature codes, or multi-rune expansions shared through `utils.c`.

`oedprintentry` walks the entry bytes with a current translation table. Normal text is emitted through `outrune`; special-character starts are parsed by `getspec`; tags are parsed by `gettag`. It switches translation tables for phonetic, Greek, superscript, and subscript regions via `changett`, delays one rune to combine accents with the previous rune through `liglookup`, expands multi-rune entities through `multitab`, and uses `outinhibit` to print only headwords for `cmd == 'h'`.

Entry layout behavior is tag-driven. Main entries and variant entries start new output lines; etymology/editor tags add brackets; pronunciation tags add parentheses; sense tags add indentation and labels from `num=`; paragraph/quote/table tags affect line breaks; `st=` statuses are rendered by `dostatus` as dagger/parallel/paragraph markers where recognized. Unknown tags/entities/statuses are debug-only diagnostics except unknown entities become replacement characters.

`oednextoff` scans `bdict` for the next `<e...>` or `<ve...>` start tag and returns the byte offset for the next entry. `oedprintkey` prints a built-in pronunciation key string.

Integration points: registered in `utils.c` as dictionary name `oed`, using `/lib/dict/oed2` and `/lib/dict/oed2index`. It depends on common output wrapping, binary-search association lookup, ligature handling, and global debug/output state in `utils.c`.

Risks and notes: the parser is permissive and fixed-buffer based (`Buflen`, `Maxaux`), so malformed long tags or many attributes truncate silently. Many special symbols are approximate, with comments noting missing exact Unicode equivalents. The tag parser assumes simple unquoted `name=value` attributes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/oed.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/pcollins.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/pcollins.c

Implements dictionary callbacks for the Paperback Collins French/Spanish/Italian-style format, where tags are delimited by `>` and `<`.

`tagtab` maps short formatting/character tags to literal runes, ligature accent codes, multi-rune codes, or control states: `H` starts headword, `X` ends headword, `[`/`{` start pronunciation suppression, and `]` ends it. `normtab` maps input bytes to runes and marks `>` as tag start.

`pcollprintentry` streams an entry, optionally raw (`cmd == 'r'`) or headword-only (`cmd == 'h'`). It buffers the previous rune so accent tags can combine through `liglookup`, expands multi-rune tags via `multitab`, suppresses pronunciation text, and inserts line breaks or `.  ` after headword close in normal output.

`pcollnextoff` seeks forward line by line until it finds a line beginning `>H<`, the format’s entry/headword marker. `pcollprintkey` reports that no pronunciation key is implemented.

Integration points: registered by `utils.c` for Collins French, Italian, and Spanish dictionaries. It uses shared `lookassoc`, `changett`, `out*`, and ligature/multi-rune helpers.

Risks and notes: tag text is read into a fixed 1000-byte buffer and unknown tags are ignored except debug diagnostics. Pronunciation is intentionally hidden because the key is not understood.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/pcollins.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/pcollinsg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/pcollinsg.c

Implements callbacks for the Paperback Collins German format. This format uses byte escapes `0x05...0x06` for font/style tags and `0xba...0xba` numeric symbol escapes.

`intab` maps all 256 input bytes to output runes or internal sentinel codes. `numtab` converts numeric symbol escapes to runes, mostly phonetic and typographic symbols. `overtab` maps overstrike/accent characters to shared ligature accent codes.

`pcollgprintentry` streams the entry byte by byte. Font escape tags are gathered by `reach`; the first tag byte controls headword filtering, with font `h` treated as headword text. Numeric symbol escapes are looked up in `numtab`; unknown numeric escapes are printed as `\N'...'`. A caret byte begins an overstrike/accent sequence, which attempts ligature composition with the previous rune or emits a fallback caret/accent representation.

`pcollgnextoff` searches for the `0x05 'h' 0x06` headword marker. It also remembers the most recent carriage-return offset and returns it at EOF as a fallback definition boundary. `pcollgprintkey` has no implemented key.

Integration points: registered in `utils.c` for Collins German-English and English-German dictionaries. Depends on shared output and ligature helpers.

Risks and notes: the parser is byte-format-specific and treats font tags mostly as output suppression/selection, not style. `reach` truncates tags at 31 bytes. Unknown symbol escapes degrade to visible escape text.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/pcollinsg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/pgw.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/pgw.c

Implements the Project Gutenberg Webster dictionary backend. Its structure is a lighter variant of `oed.c`: SGML-like tags, entity decoding, translation tables, and callbacks `pgwprintentry`, `pgwnextoff`, and `pgwprintkey`.

The file defines tag and special-character tables for Webster markup, normal/Greek/subscript/superscript byte translation tables, and parser state for current tag and entity. Entities are parsed with `getspec`, ending at `;`, unlike OED’s `.` terminator.

`pgwprintentry` streams entries with optional raw and headword-only modes. It decodes text through `normtab`, combines accent entities with buffered previous runes, expands multi-rune entities, handles paragraph sentinel `PAR`, and reacts to tags such as `hw`, `sn`, `p`, `col`, `blockquote`, and `u` for headword selection, sense breaks, paragraph breaks, and a slash marker.

`pgwnextoff` scans for Webster entry starts, normally `<p><hw>`, with a fallback path for `<p>{...`. `pgwprintkey` reuses a built-in OED-like pronunciation key.

Integration points: registered by `utils.c` as `pgw` with `/lib/dict/pgw` and `/lib/dict/pgwindex`.

Risks and notes: like `oed.c`, it is a permissive hand parser with fixed buffers and approximation-heavy entity translation. Formatting is flattened to plain text; table/block styling becomes simple line breaks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/pgw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/rev.awk -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/rev.awk

Tiny AWK helper for two-field tabular dictionary/index data. If a record has exactly two fields, it prints them reversed as `$2<TAB>$1`. Otherwise it prints `ERROR ` plus the original record.

Likely used while generating reverse lookup indexes. It assumes AWK’s default field splitting unless the caller sets `FS`.

Risks: records with embedded whitespace or more than two fields are treated as errors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/rev.awk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/robert.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/robert.c

Implements callbacks for Robert Électronique dictionaries, including main index entries and verb-form entries.

The backend uses binary pointer/index records. `robertindexentry` decodes offsets and lengths for etymology and definition data from the index entry, opens `defs.rob` and `etym.rob` lazily through `Bouvrir`, reads those slices into `Entry` objects, then calls the internal `robertprintentry`.

`intab` maps the source character set and embedded control bytes to Unicode runes or internal controls: citation pointer, font changes, superscript/subscript state, and ignored style markers. `suptab` and `subtab` map ASCII digits/operators to super/subscript runes.

`robertprintentry` emits definition text, handles newlines/line counting, injects etymology after the first definition line when available, follows citation controls into `cits.rob`, and applies one-character superscript/subscript conversions. Style controls are mostly ignored unless debug is enabled. `citation` reads one citation record ending at byte `0xc8` and recursively prints it.

`robertnextoff` advances fixed 16-byte pointer records. `robertprintkey` dumps `/lib/dict/robert/_phon`. `robertflexentry` handles verb forms from `flex.rob`, turning `$` into line breaks and limiting headword output to the second line. `robertnextflex` advances to the next `$`.

Integration points: registered in `utils.c` as `robert` and `robertv`.

Risks and notes: opens hard-coded auxiliary files, exits on open failure, and assumes binary record layouts exactly. Citation recursion and pointer data rely on trusted dictionary files. Many style/font controls are discarded.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/robert.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/roget.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/roget.c

Implements callbacks for Project Gutenberg Roget’s Thesaurus plain-text format.

`rogetprintentry` has separate behavior for headword-only and full output. Headword mode skips the numeric class prefix, bracketed/brace sections, punctuation, and digits until the first ` -- ` delimiter, emitting a cleaned phrase. Full mode skips the numeric prefix, treats ` -- ` as a major break, cleans continuation lines, rewrites useful `&c (...)` cross references as slash-delimited references, suppresses less useful `&c` numeric references, and normalizes spacing before punctuation.

`rogetnextoff` scans line by line for a line beginning with a digit and containing ` -- `, returning that line’s offset. `rogetprintkey` has no key.

Integration points: registered as `roget` in `utils.c`.

Risks and notes: format detection is heuristic and line-oriented. There is a stale `Last` global that is not used. One string comparison checks `p < e.end -2` but compares four bytes, so malformed very short tails could be fragile, though normal dictionary records likely avoid this.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/roget.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/simple.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/simple.c

Minimal UTF dictionary backend for one-record-per-line data with headword and entry separated by a tab.

`simpleprintentry` emits bytes until tab/newline/end. In headword mode it stops at the tab; in normal mode it converts the tab to a space and continues until newline. `simplenextoff` reads one newline-delimited record and returns the next offset. `simpleprintkey` reports no key.

Integration points: registered in `utils.c` for Leon Ungier Russian/English dictionaries.

Risks and notes: no escaping or validation; entries cannot contain embedded newlines, and tab is the only headword/body separator.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/simple.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/slang.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/slang.c

Implements the English Slang dictionary backend for a tagged line format. Tags are two-letter keys followed by a space: `me`, `df`, `dx`, `et`, `ex`, `la`, `nu`, `pr`, `ps`, `xr`, and `xx`.

`slangprintentry` uses `sget` to find the next tagged value region. Headword mode prints only the first `ME` tag. Full mode formats each tag type into plain text: definitions and examples with periods, etymology and pronunciation in brackets, labels in parentheses, sense numbers as indented numbered sections, parts of speech as indented labels, and cross references as `See ...`.

`slangnextoff` scans for a line beginning `me `. `sget` finds the next recognized tag line and returns the value range up to the following tag or entry end. `soutpiece` emits a value while changing newlines to spaces, coalescing repeated spaces, and dropping `@`.

Integration points: registered as `slang` in `utils.c`.

Risks and notes: unknown two-letter tag-looking lines can produce debug diagnostics and are skipped. The parser assumes `*e == 0` per its comment, so entry construction must provide a terminating byte.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/slang.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/t.awk -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/t.awk

AWK helper that expands two-field rows whose second field contains ` or `. If `$2` contains ` or ` and does not contain `(or`, it splits `$2` on ` or ` and emits one `$1<TAB>variant` row per piece. All other two-field rows pass through unchanged; non-two-field rows also pass through unchanged.

Likely used in index preparation to split alternate forms while preserving parenthesized literal “or” text.

Risks: depends on AWK field splitting and simple regex heuristics; values with tabs/spaces outside the expected format can be mis-split or passed through unexpectedly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/t.awk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/thesaurus.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/thesaurus.c

Implements callbacks for Collins Thesaurus data.

`thesprintentry` streams records and interprets a compact markup. Raw mode emits bytes unchanged. `*L` marks headword records; in headword mode, non-`L` starred sections terminate output, while in normal mode `*L` starts a new line. `*S` emits a parenthesized single-character sense marker. `#` escapes accented vowels and cedilla variants by selecting from fixed strings. `+` and `<` are dropped. A space before `*` ends headword output.

`thesnextoff` scans for the next line starting `*L`. `thesprintkey` reports no key.

Integration points: registered as `thesaurus` in `utils.c`.

Risks and notes: accent escape handling only covers a small hard-coded set and indexes `0..4`. Unrecognized markup is mostly skipped or emitted literally.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/thesaurus.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/utils.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/utils.c

Shared support for the Plan 9 `dict` command backends.

`dicts[]` is the central registry mapping dictionary names to descriptions, data paths, index paths, and callback triplets. It registers OED, AHD, Webster, thesaurus, Roget, world-language dictionaries, Collins variants, Russian simple dictionaries, movies, slang, and Robert data.

The file defines shared ligature and multi-rune expansion tables. `ligtab` maps private-use accent codes from `dict.h` to accent runes and base/accented rune pairs. `multitab` maps private-use multi-character codes to rune strings such as ligatures, Greek breathing combinations, `and`, `or`, and em-space approximations.

Utility APIs include sorted association binary searches (`lookassoc`, `looknassoc`), formatted diagnostics (`err`), output wrappers (`outrune`, `outchar`, `outchars`, `outprint`, `outpiece`, `outnl`) that respect `outinhibit` and `breaklen`, rune folding for search (`fold`, `foldre`), accent-insensitive comparison helper `acomp`, rune copy and numeric conversion helpers, `liglookup`, and `changett` for a stack of translation tables.

Integration points: every dictionary backend depends on this file for output normalization, line wrapping, tag/entity lookup, fold/search behavior, and callback registration.

Risks and notes: global output state (`linelen`, `outinhibit`, `breaklen`, `debug`) makes callbacks non-reentrant. `changett` has a fixed stack depth of 20 and debug-only overflow/underflow handling. Accent/multi-rune handling is table-driven and intentionally approximate for some source glyphs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/world.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/world.c

Implements callbacks for “Languages of the World” dictionary files, including mixed single-byte text plus embedded Japanese JIS and Chinese GB2312 sequences.

Records begin with three big-endian 16-bit lengths: headword, pronunciation, and definition. `worldprintentry` skips the header, limits output to the headword length for `cmd == 'h'`, and streams bytes through `putchar` unless raw mode is requested.

`chartab` maps 256 single-byte codes to Unicode runes, including Latin, phonetic, Greek, and special symbols. `putchar` maintains a small state machine: UTF/single-byte mode, Kana/JIS high-byte mode, GB high-byte mode, and low-byte completion. Bytes `0xfe` and `0xff` enter Japanese or GB multibyte modes; `S2J`, `tabjis208`, and `tabgb2312` convert encoded pairs to runes. Unknown or control bytes become `\xx` escapes when not otherwise used for shift controls.

`worldnextoff` seeks to `fromoff - 1`, reads the three lengths, and returns the next record offset as `fromoff - 1 + 6 + nh + np + nd`. The comment notes callers must pass `<address of valid entry> + 1`.

Integration points: registered for several bilingual dictionaries in `utils.c`; depends on `kuten.h`, `jis208.c`, and `gb2312.c` tables.

Risks and notes: offset convention is unusual and must match the main dictionary/index code. Unrecognized multibyte pairs degrade to byte escapes. The state variable `xflag` is local and always zero in the visible code, leaving some `NONE` branches effectively unreachable for escaped emission.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/dict/world.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/diff/diff.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/diff/diff.h

Shared header for Plan 9 `diff`. It declares global option flags: output `mode`, whitespace handling `bflag`, recursive directory flag `rflag`, multi-file context `mflag`, `anychange`, and external `stdout`/`binary`.

It defines allocation macros and `MAXPATHLEN`, then declares the cross-module functions for path construction, allocation, top-level dispatch, directory diffing, regular-file diffing, file preparation, error handling, line verification, change output, and context flush.

Integration points: consumed by `main.c`, `diffdir.c`, `diffio.c`, and `diffreg.c`.

Risks and notes: global mutable flags couple all modules. The header exposes only old-style C declarations and relies on external definitions rather than an encapsulated state object.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/diff/diff.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/diff/diffdir.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/diff/diffdir.c

Directory comparison layer for `diff`.

`scandir` opens a directory, reads all entries with `dirreadall`, copies names into a NULL-terminated string array, sorts names with `qsort`, and returns an empty list on open failure. `isdotordotdot` filters `.` and `..`.

`diffdir` walks the two sorted name arrays in merge order. Missing names produce `Only in ...` output in normal and `-n` modes. Matching names are joined with their parent paths using `mkpathname` and recursively passed to `diff`.

Integration points: called from `main.c` when both operands are directories and recursion/level rules allow.

Risks and notes: it holds whole directory listings in memory. Open failure is treated as an empty directory after printing an error, which can suppress hard failure in multi-file mode.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/diff/diffdir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/diff/diffio.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/diff/diffio.c

Input, hashing, verification, and change-output layer for regular-file `diff`.

`readline` reads one logical line into a 4096-byte buffer, truncating overlong lines after consuming the rest. `readhash` computes the historical 7-bit/16-bit one’s-complement line hash, with `bflag` modes for exact, coalesced whitespace, or whitespace-stripped comparison.

`prepare` opens a file, detects likely binary data by sampling runes, builds the per-line hash array, records input buffers and file names, and sets `binary` if needed. `check` rereads both files using the match vector `J` from `diffreg.c`, computes line offsets (`ixold`, `ixnew`), and invalidates hash-collision matches after comparing actual line text with whitespace policy applied.

`change` emits one edit hunk in normal, ed-script, reverse-script, `-n`, or buffered context/all-context modes. `fetch` prints saved source ranges using line-offset arrays. `flushchanges` groups buffered context changes with three lines of context, or prints entire files for mode `a`.

Integration points: `diffreg.c` produces `J`, then calls `check` and `output`/`change`; `main.c` controls flags.

Risks and notes: lines longer than 4095 bytes are truncated for textual diffing. Binary detection is heuristic. Context buffering uses a global dynamically grown array and fixed three-line context.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/diff/diffio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/diff/diffreg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/diff/diffreg.c

Regular-file diff algorithm implementation. The header comment documents Harold Stone’s longest common subsequence approach.

Core data structures are global arrays of line hashes, sorted line records, equivalence classes, candidate chains, match vector `J`, and line offsets. `prune` removes common prefix/suffix from consideration. `sort` shell-sorts line hashes. `equiv` builds equivalence classes of equal line hashes in file 1. `unsort` restores file 0 equivalence indexes to original order.

`stone` walks file 0 equivalence classes to build k-candidates for the longest common subsequence, using `search` and `newcand`. `unravel` converts the candidate chain into the match vector `J`, restoring pruned prefix/suffix matches. `output` scans `J` to call `change` for additions/deletions/changes, in reverse order for ed-script mode.

`cmp` compares binary files byte-for-byte in buffered chunks. `diffreg` orchestrates opening/preparing files, binary path, pruning/sorting/equivalence/LCS, verification with `check`, output, and cleanup.

Integration points: called by `main.c` for regular files; uses `diffio.c` for prepare/check/change output.

Risks and notes: memory is manually overlaid/reused between arrays to reduce footprint, making ownership subtle. The line hash can collide, but `check` corrects false matches. There is a typo in the fallback S_ISREG macro area in unrelated conditional macros, but the file’s own logic does not use those macros.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/diff/diffreg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/diff/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/diff/main.c

Front end and dispatcher for Plan 9 `diff`.

It parses options `-e`, `-f`, `-n`, `-c`, `-a`, `-w`, `-b`, `-r`, `-m`, and `-h`. It initializes buffered stdout, validates argument counts, detects multi-file/directory mode, and loops over all source operands against the final target operand.

`statfile` normalizes operands. It handles `-` stdin by copying to a temp file, and copies non-regular/non-directory inputs to temp files so the regular diff path can read them repeatedly. `mktmpfile` creates `/tmp/diff...` files and records them for cleanup. `diff` dispatches directory-vs-directory to `diffdir`, regular-vs-regular to `diffreg`, and file-vs-directory by appending the basename to the directory path.

`panic`, `done`, and `rmtmpfiles` handle errors, exit statuses, and temp cleanup. `emalloc`/`erealloc` are fatal allocation wrappers.

Integration points: owns global flags declared in `diff.h` and coordinates `diffdir.c`, `diffreg.c`, and `diffio.c`.

Risks and notes: temp names use `mktemp`, consistent with old Plan 9 style but inherently race-prone by modern standards. Errors in multi-file mode can be nonfatal through status `0` panics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/diff/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/boot.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/boot.c

El Torito boot support for ISO 9660 images.

`Cputbootvol` writes a boot record volume descriptor with `EL TORITO SPECIFICATION` and reserves a pointer location for the boot catalog. `Cupdatebootvol` later patches that pointer with `cd->bootcatblock`.

`Cputbootcat` writes the boot catalog validation header and records `bootimageptr` for later patching. `Cupdatebootcat` writes the initial/default boot entry: bootable flag, emulation type or no-emulation, load segment, sector count, and boot image block. No-emulation images are limited to loading at most four 512-byte sectors with a warning.

`Cfillpbs` patches a Plan 9 PBS boot image with loader block and size metadata. `findbootimage` and `findloader` locate named files in the staged `Direc` tree and store pointers in `Cdimg`.

Integration points: invoked from `createcd` and `dump9660.c` when boot flags are set; depends on directory block assignments from `writefiles`.

Risks and notes: boot catalog fields are patched after the boot image is discovered. Missing boot image/loader only warns. Emulation type is inferred solely from image length.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/boot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/cdrdwr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/cdrdwr.c

Core ISO image read/write abstraction for the 9660 toolset.

`createcd` creates a new image, initializes paired read/write `Biobuf`s, writes the 16-sector lead-in, primary volume descriptor, optional El Torito and Joliet descriptors, terminator, optional dump block, boot catalog, and flags. `opencd` opens an existing image, validates length and primary descriptor, infers flags from the system identifier, probes Joliet and dump support, and prepares the same `Cdimg` abstraction.

`big`, `little`, `Cputnl`, `Cputnm`, and `Cputn` handle endian conversions. `Creadblock`, `Cread`, `Cgetc`, `Crdline`, and seek/offset helpers coordinate read buffering with write flushes. `Cputc`, `Cwrite`, `Cputs`, `Cputr*`, `Crepeat`, and `Cpadblock` write structured data and maintain `nextblock`. `Cputdate` and `Cputdate1` write ISO directory and volume timestamps.

`parsedir` converts an on-disc ISO/Joliet directory record into `Direc`, including Plan 9 system-use fields when present. `setroot`, `setvolsize`, and `setpathtable` patch descriptor fields after directory and path table locations are known. `readisodesc` and `readjolietdesc` parse primary/secondary descriptors into `Voldesc`.

Integration points: nearly every 9660 module uses this file’s `Cdimg` I/O and patching APIs.

Risks and notes: asserts enforce many layout invariants. Primary descriptor flag inference uses lowercase string matching after `isostring`. Plan 9 system-use parsing is partial; Rock Ridge parsing is noted as a BUG.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/cdrdwr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/conform.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/conform.c

Manages conforming ISO 9660 names and `_conform.map` output.

A global `Conform *map` stores `Tx` mappings from original atomized names to generated conforming names. `txsearch` binary-searches this array by atom pointer. `addtx` inserts a new mapping, preserving sorted order and warning on duplicates. `conform` returns an existing mapping or creates `Dnnnnnn`/`Fnnnnnn` names for directories/files.

`wrconform` writes new mappings as text lines `good bad` at the current image end, sorted by generated good name for output, then restores map order by original-name atom. It reports the block and byte length to the caller and pads to a block boundary.

Integration points: `direc.c` calls `conform` during name conversion; `dump.c` reconstructs mappings with `addtx`; `dump9660.c` writes full or incremental `_conform.map`.

Risks and notes: sorting by atom pointer, not string, depends on the process-wide string interning table. The generated names are sequential based on map size and can change if map reconstruction changes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/conform.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/direc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/direc.c

In-memory directory tree management for ISO image construction.

`mkdirec` initializes a `Direc` from an `XDir`. Children are kept sorted by UTF name while building. `dbsearch` performs binary search by name segment, `walkdirec` resolves slash-separated paths, and `adddirec` inserts a file or directory, requiring intermediate directories to already exist.

`copydirec` recursively copies a tree, used for building a Joliet tree from the ISO tree after file blocks are assigned. `checknames` marks nodes with `Dbadname` when a supplied predicate rejects the name, and always marks `_conform.map` bad. `convertnames` assigns `confname`, either by conform-map generated names or a supplied conversion function such as `struprcpy`/`strcpy`. `dsort` recursively sorts child arrays with ISO or Joliet comparison functions.

Integration points: populated by `dump9660.c` from proto files and used by write/path/boot/dump modules.

Risks and notes: after `dsort`, `adddirec` should not be used because build-order sort assumptions change. Path insertion mutates the input string temporarily around the last slash.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/direc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/dump.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/dump.c

Implements incremental “dump CD” state, deduplication, and dump-tree reconstruction.

Deduplication uses `Dumpdir` nodes in two binary trees: one keyed by MD5 digest and one by block number. `md5cd`, `addfile`, `insertmd5`, and `lookupmd5` scan existing image file data so new files can reuse blocks when content matches.

`readkids` parses on-disc directory blocks into child `Direc` arrays, and `adddir` recursively scans existing trees into the dump index. `dumpcd` seeds a `Dump` from existing dump roots. `freekids` releases temporary child arrays.

Dump directory names are year/day paths. `adddumpdir`, `createdumpdir`, `rmdumpdir`, and `copybutname` maintain in-memory dump roots. `Cputdumpblock` writes a magic dump header block; `hasdump` finds such a block in descriptor sectors. `readdumpdirs` follows the linked dump-header chain to reconstruct dump root directories and root block/length pairs. `readdumpconform` follows the same chain to rebuild `_conform.map`.

Integration points: central to `dump9660.c` incremental mode and `write.c` content deduplication.

Risks and notes: dump headers are plain text inside 2048-byte blocks with strict field expectations. MD5 collisions are not handled beyond a duplicate warning. Some tree walks are unbalanced binary trees, not self-balancing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/dump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/dump9660.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/dump9660.c

Main program for `disk/dump9660` and, via `-M`, `disk/mk9660`.

It parses options for Plan 9 fields, conforming ISO names, Joliet, Rock Ridge, boot images/loaders, proto file, source root, volume name, maximum image size, timestamp, data offset/block alignment, and fix/commit behavior. Defaults create/update a dump CD using `/sys/lib/sysconfig/proto/allproto` and source `./`.

The main flow creates or opens a `Cdimg`, builds a new ISO tree from a proto file through `rdproto` and `addprotofile`, reconstructs existing dump state in incremental mode, writes file data with deduplication, resolves boot image/loader, creates a Joliet copy if requested, validates/converts/sorts names, writes ISO/Joliet directories, writes conform maps, writes or repairs dump header blocks, patches volume descriptors, writes path tables, enforces max-size rollback, commits the old null dump block, truncates the image, and exits.

`addprotofile` converts Plan 9 `Dir` metadata to `XDir`, optionally replaces colons with spaces, inserts the entry, and records the source file path.

Integration points: orchestrates all other 9660 modules plus Plan 9 `libdisk`/`libproto`.

Risks and notes: this is a stateful image-updater with many late patches. The max-size abort path rewrites old trees and jumps to the fix path. Correctness depends on block pointers assigned before directory/tree patching and on dump header chain integrity.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/dump9660.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/ichar.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/ichar.c

ISO 9660 character/name handling and primary volume descriptor writer.

`isostring` converts fixed-width ISO strings to lowercase atomized Plan 9 strings, trimming trailing spaces. `isisofrog` and `isbadiso9660` enforce the tool’s ISO name policy: lowercase letters/digits/underscore only, 8.3 constraints, and avoidance of generated `Ddddddd`/`Fdddddd` names.

`isocmp` compares conforming names in ISO base/extension order, matching ISO semantics more closely than a plain string compare. `mkisostring` uppercases Plan 9 lowercase names and pads fixed fields.

`Cputisopvd` writes the primary volume descriptor, including system identifier flags (`plan 9`, `rrip`, `boot`, `iso9660` or `utf8`), volume metadata, placeholder sizes/path tables/root directory, dates, and file structure version.

Integration points: used by descriptor read/write, name validation/conversion, and directory sorting.

Risks and notes: this tool treats lowercase source names as canonical and uppercases only when writing ISO fields, so uppercase input names are considered non-conforming. FAT-like generated conform names are reserved.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/ichar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/iso9660.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/iso9660.h

Shared data model and function declarations for the ISO 9660 tools.

Defines host-side structures: `XDir` for filesystem metadata, `Direc` for staged image tree entries, `Voldesc` for parsed descriptor metadata, `Cdimg` for image file state and flags, `Cdinfo` for creation options, `Conform`/`Tx` for conform-name mappings, and `Dump`/`Dumpdir`/`Dumproot` for incremental dump support.

Defines on-disc structure layouts: `Cvoldesc`, `Cdir`, and `Cpath`, matching ISO volume descriptor, directory record, and path table records. Defines feature flags for Joliet, Plan 9 extensions, conforming names, Rock Ridge, new images, dump CDs, bootability, no-emulation boot, and PBS patching.

Also defines Rock Ridge/SUSP constants (`RR_*`, `TF*`, `NM*`), block size (`2048`), directory allocation chunk size, directory-entry pseudo-types (`DTdot`, `DTdotdot`, `DTiden`, `DTroot`, `DTrootdot`), all cross-module prototypes, and global variables owned by the program.

Integration points: included by every `disk/9660` C file.

Risks and notes: this header exposes all module internals globally. Several declared functions are not implemented in the assigned files or are platform/build-specific (`setparents`, `uidno`, `gidno`, `rdconform`).
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/iso9660.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/jchar.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/jchar.c

Joliet/UCS-2 name handling and secondary volume descriptor writer.

`jolietstring` decodes big-endian UCS-2 bytes to Plan 9 UTF strings and interns them. `isjolietfrog` and `isbadjoliet` enforce Joliet name limits: at most 64 runes and no `*`, `/`, `:`, `;`, `?`, or backslash. `jolietcmp` compares base and extension portions as rune sequences, matching the big-endian encoded ordering.

`Cputjolietsvd` writes a Joliet secondary volume descriptor with UCS-2 fixed strings, escape sequence `%/C`, placeholder root/path/size fields, metadata strings, dates, and file structure version.

Integration points: used by descriptor parsing, name validation/sorting, and optional Joliet tree writing.

Risks and notes: buffers in `jolietcmp` are fixed at 256 runes with a BUG comment. UCS-2 handling does not address surrogate pairs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/jchar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/path.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/path.c

Writes ISO 9660 path tables after directory data has been written.

`writepathtable` starts from the root directory entry in a volume descriptor, writes path table entries breadth-first, and uses the path table itself as the traversal queue. Because path entries do not include directory lengths, it keeps a parallel in-memory length array. It reads directory blocks to discover subdirectories and writes either little-endian or big-endian table entries.

`writepathtablepair` writes little and big path tables for one descriptor and patches descriptor path-table fields with `setpathtable`. `writepathtables` writes ISO tables and, if present, Joliet tables.

Integration points: called near the end of `dump9660.c` after root descriptors are patched.

Risks and notes: comments explicitly reject padding path table entries across block boundaries despite the rest of ISO’s block-alignment style, for Windows compatibility. Traversal relies on valid previously written directory records.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/path.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/plan9.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/plan9.c

Plan 9 platform adapter for the 9660 tool.

`dirtoxdir` copies Plan 9 `Dir` metadata into `XDir`, atomizing name/user/group and preserving mode, atime, mtime, and length. Numeric uid/gid are set to zero. `fdtruncate` is a no-op on Plan 9.

Integration points: alternative to `unix.c` depending on build target.

Risks and notes: no truncation support in this adapter, and numeric uid/gid are not resolved.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/plan9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/rune.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/rune.c

Small rune-string utility file for the 9660 tools.

`strtorune` converts a UTF string to a NUL-terminated `Rune` array and returns the destination start. `runechr` finds a rune in a NUL-terminated array. `runecmp` lexicographically compares rune arrays.

Integration points: used by Joliet conversion/sorting and UCS-2 writing helpers.

Risks and notes: callers must supply sufficiently large buffers. `strtorune(nil)` returns nil.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/rune.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/sysuse.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/sysuse.c

Writes Rock Ridge and SUSP system-use fields for directory records.

The core challenge is fitting records into limited system-use space. `Cbuf`, `freespace`, `ensurespace`, and `setcelen` manage continuation areas and CE records. `Cputstring` splits long NM-like strings across records. `Cputsysuse` computes and optionally writes the SUSP/RRIP records for one directory entry: SP and ER records at the root, RR flags, PX POSIX mode/link/user/group metadata, NM alternate names, SL symlink components, and TF timestamps.

Helper writers emit specific records: `CputsuspCE`, `CputsuspER`, `CputsuspRR`, `CputsuspSP`, `Cputrripname`, `CputrripSL`, `CputrripPX`, and `CputrripTF`. `mode` maps Plan 9 mode bits to POSIX file type/mode fields; `nlink` fabricates POSIX link counts.

Integration points: `write.c` calls `Cputsysuse` from `genputdir` when `CDrockridge` is active.

Risks and notes: comments emphasize complexity and several approximations. Symbolic link support depends on `CHLINK`. The `mode` function asserts only directory/regular support even though it has symlink logic, so symlink handling may be build-sensitive. Continuation record logic is assertion-heavy and layout-sensitive.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/sysuse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/uid.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/uid.c

Appears to be an unfinished or placeholder sketch for detecting user/group database format.

It includes comments describing Plan 9 `/adm/users` and Unix `/etc/passwd`/`/etc/group` field layouts. `sniff` is written in pseudocode-style C without a return type and contains non-C statements such as “read first line of file into p;”. It attempts to split the first line on `:` and infer Plan 9 vs Unix format based on whether field 0 or field 2 is numeric. `isnumber` is the only complete function, using `strtol` and checking full consumption.

Integration points: `iso9660.h` declares `uidno`/`gidno`, but this file does not provide them. The real Unix adapter resolves numeric IDs in `unix.c`; Plan 9 adapter sets them to zero.

Risks and notes: as written, this file is not valid C. It is likely not built or is a historical stub.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/uid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/unix.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/unix.c

Unix platform adapter for the 9660 tool.

`dirtoxdir` copies `Dir` metadata into `XDir`, resolves textual user/group names to numeric uid/gid with `getpwnam`/`getgrnam`, preserves times/length/mode, and records symlink targets when the mode has `CHLINK`, forcing symlink permissions to `0777`.

`fdtruncate` calls POSIX `ftruncate`. `numericuid` and `numericgid` warn once if name lookup fails and return zero.

Integration points: alternative to `plan9.c` for Unix builds; provides numeric IDs used by Rock Ridge PX records.

Risks and notes: only the first lookup failure warning is printed per uid/gid resolver. Failed lookups silently become uid/gid 0 after warning.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/unix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/util.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/util.c

Common utility support for 9660 tools.

`atom` interns strings in a 1024-bucket hash table so repeated names compare cheaply by pointer in some code paths. `emalloc` zeroes allocations and fails fatally; `erealloc` fails fatally. `struprcpy` uppercases a string copy. `chat` conditionally writes verbose diagnostics when global `chatty` is nonzero.

Integration points: used across directory, conform, descriptor, and main modules.

Risks and notes: interned strings are never freed. `erealloc` does not zero newly allocated tail memory. `atom` depends on process lifetime and is part of conform-map ordering assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/write.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/write.c

Writes file data, directory records, dump directories, and descriptor terminators.

`writefiles` recursively copies non-directory source files into the image while computing MD5. If an existing dump entry has the same digest and length, it reuses the old block and rewinds `nextblock`; otherwise it inserts the new content into the dump index. It supports block alignment through global `blocksize`.

`writedirs` writes directory trees bottom-up. `_writedirs` first computes directory record lengths with `dowrite == 0`, reserves blocks, writes dot/dotdot/children records, pads, assigns `block`/`length`, and patches dot/dotdot records using `rewritedot` and `rewritedotdot`. `writedumpdirs` handles the special dump-root/year/day hierarchy, where day roots may already be written.

`Cputplan9` writes Plan 9 system-use metadata. `genputdir` writes one ISO/Joliet directory record, handles block-boundary padding, file flags, dates, names, Plan 9 or Rock Ridge extensions, and length calculations. `Cputisodir` and `Cputjolietdir` specialize it. `Cputendvd` writes the volume descriptor set terminator.

Integration points: central write path called by `dump9660.c`; uses `sysuse.c` for Rock Ridge and `cdrdwr.c` for primitive writes.

Risks and notes: directory record length must stay under 255 bytes, enforced by assertions. Empty files get block zero. If a source changes while being written, length is updated with a warning but content consistency depends on the read that just occurred.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/9660/write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/exsort.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/exsort.c

Standalone utility for inspecting and optionally rewriting `/adm/cache`-style arrays of 32-bit block numbers.

It reads the whole file as `ulong` values, counts how many values have bit 7 and bit 31 set, and if high-bit count exceeds low-bit count treats the data as byte-swapped and swaps every word. It sorts values numerically, then reports counts per disk-sized range using `Wormsize = 157933` for disk numbers 0 through 99 and a total.

With `-w`, it opens the file read/write and writes the sorted values back, swapping back first if it originally detected swapped byte order. Without `-w`, it is read-only. Default file is `/adm/cache`.

Risks and notes: reads entire file into memory, assumes file length is a multiple of `sizeof(long)`, and uses a heuristic for byte order. It prints `cant` style errors and exits with simple status strings.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/exsort.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/format.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/format.c

Plan 9 disk/FAT formatting utility. It can format floppies, files, and disk partitions, write a Plan 9 boot sector, initialize FAT12/FAT16 filesystems, and copy initial root-directory files.

The file defines known disk `Type` geometries, DOS boot sector and root directory structures, a built-in nonbootable boot program, and global FAT/root allocation state. `main` parses options for boot block, cluster size, DOS/FAT mode, file creation, label, reserved sectors, disk type, verbosity, and safety bypass. It opens the disk through `opendisk`, infers type, optionally formats floppies through the control file, runs `sanitycheck`, dry-runs `dosfs`, then commits by running `dosfs` again.

`sanitycheck` protects against formatting a Plan 9 partition table sector without enough reserved sectors and against formatting an entire SCSI disk instead of a partition unless `-x` is used. `getdriveno` maps Plan 9 sd device names to BIOS drive numbers.

`dosfs` writes the boot sector/PBS and optionally initializes FAT. It sizes FAT12 vs FAT16 by iterating cluster and FAT-sector counts, writes BIOS parameter block fields, allocates in-memory FAT/root tables, copies requested files into the file area rounded to cluster boundaries, chains clusters with `clustalloc`, writes root directory entries with `addrname`, then writes both FAT copies and the root. `putname` formats 8.3 uppercase names, `puttime` writes DOS date/time, and `writen` throttles writes in 8 KiB chunks.

Integration points: uses Plan 9 `disk.h` `Disk` abstraction and standard `Dir` metadata. It is independent of the 9660 modules.

Risks and notes: FAT32 is explicitly unsupported. Initial files are read whole into memory. The dry-run/commit double call recalculates state and relies on deterministic sizing. A debug-style `fprint(2, "add ...")` is unconditional when adding files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/disk/format.c -->