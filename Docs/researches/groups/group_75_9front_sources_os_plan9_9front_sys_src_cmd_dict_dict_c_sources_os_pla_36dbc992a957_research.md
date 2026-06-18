# Group Research: group_75_9front_sources_os_plan9_9front_sys_src_cmd_dict_dict_c_sources_os_pla_36dbc992a957

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`.

This group covers the Plan 9/9front `dict` command core, dictionary-specific decoders/index helpers, East Asian codepoint tables used by world dictionaries, and the small `diff` command entry/header files.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/dict.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/dict.c

Interactive and command-line front end for the Plan 9 `dict` command.

Key elements:
- Selects the first installed dictionary from `dicts[]`, or a named one via `-d`.
- Supports `-k` pronunciation key printing, `-c cmd`, debug `-D`, and a shorthand positional search pattern.
- Maintains `dot`, an address set of dictionary byte offsets with current selection.
- Parses commands `a`, `h`, `p`, `r` and uppercase all-entry variants.
- Address syntax includes current `.`, regex `/.../`, non-folding regex `!...!`, result number, absolute dictionary offset `#n`, and `+`/`-` entry navigation.
- Searches the sorted index by extracting a literal prefix, binary-locating it in the folded index, then regex/filtering matching entries.
- `getentry` reads an entry by using the active dictionary `nextoff` callback to find its end.
- `setdotprev` scans backward heuristically by expanding a previous search window and repeatedly calling `nextoff`.

Dependencies:
- Uses `Dict` callbacks from `dict.h`/`utils.c`.
- Uses Plan 9 `Biobuf`, `regexp`, `ARGBEGIN`, rune APIs, and `qsort`.
- Relies on index records of `key<TAB>offset`, sorted by folded key plus numeric offset.

Research notes:
- Case-folded search is intentionally aligned with `sort(1)` folding for dictionary indexes.
- Prefix search is a performance optimization: it avoids scanning the whole index for anchored regexes.
- Uppercase commands iterate over all current matches; lowercase commands operate on `dot->cur`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/dict.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/dict.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/dict.h

Shared API and private-use rune definitions for the `dict` command modules.

Key elements:
- Defines private-use sentinel runes for output suppression, tags, special names, paragraphs, accent ligature states, and multi-rune expansions.
- Defines `Entry`, `Assoc`, `Nassoc`, and `Dict`.
- `Dict` binds a dictionary name/description/data path/index path to callbacks: `nextoff`, `printentry`, and `printkey`.
- Declares common utility functions for lookup, output formatting, folding, ligature handling, and translation-table stack management.
- Declares all dictionary adapter callbacks used by `utils.c`.

Dependencies:
- Requires Plan 9 `Rune` and `Biobuf` types from including files.
- Shared by all dictionary source files in this group.

Research notes:
- The private-use constants are internal markup tokens, not output characters.
- The adapter contract is narrow: find next entry offset, print an entry for command mode, and print pronunciation/help key.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/dict.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/egfix -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/egfix

`rc`/`sed` cleanup pipeline for English-German index material.

Key elements:
- Removes trailing whitespace.
- Drops lines without tabs.
- Splits comma-separated alternatives into additional index lines.
- Expands parenthesized variants by emitting both forms.
- Normalizes repeated spaces and tab spacing.

Dependencies:
- Uses Plan 9 `rc` and `sed`.
- Takes an input filename as `$1`.

Research notes:
- This is a preprocessing helper for raw dictionary index generation, not runtime `dict` code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/egfix -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/egfix2 -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/egfix2

Secondary English-German index transformer.

Key elements:
- Uses `awk` with tab/comma-space field splitting.
- Emits `term<TAB>offset` pairs by reversing fields after the first.
- Lowercases ASCII with `tr A-Z a-z`.
- Sorts uniquely using tab as delimiter and folded first field plus numeric offset.

Dependencies:
- Uses Plan 9 `rc`, `awk`, `tr`, and `sort`.

Research notes:
- Complements `egfix` by converting cleaned offset-to-term lines into canonical index order.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/egfix2 -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/gb2312.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/gb2312.c

Static GB2312 kuten-to-Unicode rune table.

Key elements:
- Defines `tabgb2312[GB2312MAX]`.
- `GB2312MAX` is 8795 from `kuten.h`.
- Table contains 8795 entries: 7445 mapped Unicode codepoints and 1350 `NONE` gaps.
- Used by `world.c` to decode GB-encoded double-byte sequences embedded in world dictionary data.

Dependencies:
- Includes `kuten.h`.
- Uses `NONE` sentinel `0xffff`.

Research notes:
- This file is data-only: no executable logic beyond the static initializer.
- Lookup index is produced in `world.c` from transformed JIS-style row/column bytes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/gb2312.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/gefix -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/gefix

German-English raw index cleanup and canonicalization pipeline.

Key elements:
- Strips trailing whitespace and drops malformed non-tabbed lines.
- Removes pronunciation marker `\N'349'` and apostrophe-like quote markers.
- Normalizes leading/trailing hyphens around headword fields.
- Expands parenthesized variants and `(r, s)` suffix variants.
- Emits both `ß` and `ss` forms.
- Uses `awk` to emit `term<TAB>offset`, lowercases, and sorted-uniques the output.

Dependencies:
- Uses Plan 9 `rc`, `sed`, `awk`, `tr`, and `sort`.

Research notes:
- Encodes German-specific index normalization rules before feeding data to `dict`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/gefix -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/getneeds -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/getneeds

Debug-log postprocessor for missing OED/PGW-style markup needs.

Key elements:
- Iterates categories `spec`, `tag`, `aux`, and `status`.
- Greps matching diagnostics from an input file.
- Sorts and deduplicates by diagnostic fields.
- Emits `needspec`, `needtag`, `needaux`, and `needstatus` files.

Dependencies:
- Uses Plan 9 `rc`, `grep`, `sort`, `awk`, and temporary `junk*` files.

Research notes:
- Intended for maintaining markup translation tables by extracting unknown tokens from debug output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/getneeds -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/jis208.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/jis208.c

Static JIS X 0208 kuten-to-Unicode rune table.

Key elements:
- Defines `tabjis208[JIS208MAX]`.
- `JIS208MAX` is 8407 from `kuten.h`.
- Table contains 8407 entries: 6879 mapped Unicode codepoints and 1528 `NONE` gaps.
- Used by `world.c` for Japanese double-byte sequence decoding.

Dependencies:
- Includes `kuten.h`.
- Uses `NONE` sentinel `0xffff`.

Research notes:
- Data-only initializer, paired with `gb2312.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/jis208.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/kuten.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/kuten.h

Japanese/Chinese double-byte conversion macros and table declarations.

Key elements:
- Defines `J2S` for JIS X 0208 to Shift-JIS conversion.
- Defines `S2J` for Shift-JIS to JIS X 0208 conversion.
- Provides validity macros for Shift-JIS and JIS byte ranges.
- Declares table sizes: `JIS208MAX`, `GB2312MAX`, `BIG5MAX`.
- Externs `tabjis208`, `tabgb2312`, and `tabbig5`.

Dependencies:
- Used by `world.c`, `jis208.c`, and `gb2312.c`.

Research notes:
- `tabbig5` is declared here but not part of this grouped file set.
- Macros mutate their byte arguments in place.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/kuten.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/mkindex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/mkindex.c

Index seed generator for new dictionary backends.

Key elements:
- Opens a dictionary data file from `dicts[]`.
- Walks entries from offset 0 to EOF using the selected dictionary `nextoff`.
- Calls selected dictionary `printentry(e, 'h')` to extract headwords.
- Emits `offset<TAB>headword` pairs to stdout.
- Supports `-d dictname` and `-D`.

Dependencies:
- Uses `dict.h`, `dicts[]`, and adapter callbacks.
- Reuses output globals expected by adapter code.

Research notes:
- The header comment documents the workflow for adding a new dictionary: implement `nextoff` and headword printing, add `dicts[]`, run `mkindex`.
- Unlike runtime `dict`, this emits offset first and expects later canonicalization.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/mkindex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/movie.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/movie.c

Adapter for `/lib/movie/data` records.

Key elements:
- Defines two-letter movie data tags such as title, release date, country, cast, director, awards, abstract, and text.
- `movieprintentry` prints title for headword mode, raw data for `r`, and formatted metadata for normal printing.
- Handles repeated tags with comma-separated list rendering.
- `moutall2` rewrites `field1_field2` as `field2 (field1)`, with special handling for “Himself/Herself”.
- `movienextoff` finds the next record beginning with `$$`.
- `mget` finds tag values, including continuation lines.

Dependencies:
- Uses common output helpers from `utils.c`.

Research notes:
- The same data file is indexed three ways in `utils.c`: title, actor, and director.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/movie.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/oed.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/oed.c

Oxford English Dictionary SGML-like markup adapter.

Key elements:
- Large tag table maps OED element names to semantic handlers for entries, variants, headwords, pronunciations, etymology, quotes, senses, tables, Greek, subscript/superscript, and related formatting.
- Large special-character table maps entity names to Unicode runes, internal accent ligatures, or multi-rune expansions.
- Translation tables support normal text, phonetic text, Greek text, subscript, and superscript.
- `oedprintentry` scans the raw entry byte-by-byte, translates entities and tags, handles nested translation tables with `changett`, and formats headwords/senses/statuses.
- `oednextoff` locates entries beginning with `<e>`, `<ve>`, or those tags with attributes.
- `oedprintkey` emits a built-in pronunciation key.
- `getspec` parses `&name.` special entities; `gettag` parses `<tag aux=value>` and end tags.
- `dostatus` renders selected status attributes such as obsolete and alternate forms.

Dependencies:
- Uses `dict.h` private-use tokens, ligature helpers, output helpers, and binary association lookup.
- Runtime depends on OED data and index paths declared in `utils.c`.

Research notes:
- Unknown tags/entities/statuses are only reported in debug mode.
- Several special-character mappings are approximate, and the file documents names without close Unicode equivalents.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/oed.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/pcollins.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/pcollins.c

Adapter for “Paperback Collins” dictionaries using `>tag<` markup.

Key elements:
- Defines internal formatting tokens for bold, headword start/end, italics, pronunciation start/end, and roman text.
- `normtab` translates 7-bit source bytes to runes or tag sentinels.
- `tagtab` maps Collins tags to runes, accents, ligatures, or control tokens.
- `pcollprintentry` supports raw mode, headword-only mode, accent ligature combining, multi-rune expansions, pronunciation suppression, and headword boundaries.
- `pcollnextoff` finds entries beginning with `>H<`.
- `gettag` parses tag names between `>` and `<`.

Dependencies:
- Uses common ligature/multi-rune utilities and output helpers.

Research notes:
- Used for French, Italian, Spanish, and related Collins dictionaries in `dicts[]`.
- Pronunciation content is currently suppressed because the key is incomplete.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/pcollins.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/pcollinsg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/pcollinsg.c

Adapter for German Paperback Collins binary-ish markup.

Key elements:
- Input uses byte `0x05...0x06` font escapes and `0xba...0xba` numeric special escapes.
- `intab` maps source bytes to runes or sentinels.
- `numtab` maps numeric special codes to runes.
- `overtab` maps overstrike accent characters to internal accent ligatures.
- `pcollgprintentry` decodes font escapes, headword font selection, numeric specials, and overstrike accents.
- `pcollgnextoff` scans for the font escape sequence marking a headword; falls back to a carriage-return boundary.
- `reach` reads escape payloads into `tag`.

Dependencies:
- Uses ligature lookup and output helpers.

Research notes:
- Used by German-English and English-German Collins entries.
- Unknown numeric specials are emitted as `\N'...'`-style text.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/pcollinsg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/pgw.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/pgw.c

Project Gutenberg Webster dictionary adapter.

Key elements:
- Similar architecture to `oed.c`, but for PGW HTML/SGML-like tags and semicolon-terminated entities.
- Tag table handles headwords, paragraphs, definitions, senses, parts of speech, bold/italic, blockquote, breaks, and cross-reference-like markup.
- Special-character table maps HTML-like entity names to Unicode or internal ligature/multi-rune tokens.
- Translation tables support normal, phonetic, Greek, subscript, and superscript text.
- `pgwprintentry` translates source bytes/entities/tags and formats headword or full entry output.
- `pgwnextoff` finds entries beginning with `<p><hw>` or a fallback `<p>{` pattern.
- `pgwprintkey` emits the same built-in pronunciation key structure as OED.
- `getspec` parses `&name;`; `gettag` parses tag names.

Dependencies:
- Uses `dict.h` sentinels, common lookup/output/ligature utilities.

Research notes:
- Thanks comment credits Caerwyn Jones for the module.
- Several entity mappings are approximate and documented inline.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/pgw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/rev.awk -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/rev.awk

Small AWK field reverser for two-field index lines.

Key elements:
- For `NF == 2`, prints `$2<TAB>$1`.
- For malformed records, prints `ERROR` plus the record.

Dependencies:
- Standalone AWK script.

Research notes:
- Useful for converting `offset<TAB>key` style data into `key<TAB>offset`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/rev.awk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/robert.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/robert.c

Adapter for Robert Électronique dictionary data.

Key elements:
- Defines a 256-entry byte-to-rune/control table for Robert source encoding.
- Handles citation pointers, style controls, symbol/font controls, superscript, and subscript.
- `robertindexentry` decodes pointer records into definition and etymology offsets/lengths, reads auxiliary files, and delegates formatting.
- `robertprintentry` renders definition/etymology text, inline citations, baseline changes, and newline behavior.
- `citation` reads citation records from `cits.rob`.
- `robertnextoff` advances fixed-size pointer records by 16 bytes.
- `robertprintkey` streams `/lib/dict/robert/_phon`.
- `robertflexentry` handles verb-form data from `flex.rob`; `robertnextflex` uses `$` separators.
- `Bouvrir` opens Robert auxiliary files and exits with a French error message on failure.

Dependencies:
- Uses additional Robert data files: `cits.rob`, `defs.rob`, `etym.rob`, `_phon`, and pointer/flex files from `utils.c`.

Research notes:
- Main dictionary entries are indirect: the indexed file stores pointers to separate definition/etymology/citation files.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/robert.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/roget.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/roget.c

Adapter for Project Gutenberg Roget’s Thesaurus.

Key elements:
- `rogetprintentry` extracts headwords in `h` mode by skipping numbering, punctuation, and bracketed material until `" -- "`.
- Full printing removes the leading number, formats first-line delimiter `" -- "`, handles continuation lines, and rewrites selected `&c` cross references as `/target/`.
- `rogetnextoff` finds the next line beginning with a digit and containing `" -- "`.
- `rogetprintkey` reports no pronunciation key.

Dependencies:
- Uses C `ctype` helpers and common output routines.

Research notes:
- Tailored to Gutenberg text layout rather than structured tags.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/roget.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/simple.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/simple.c

Simple UTF dictionary adapter.

Key elements:
- Handles dictionaries where each entry is one line and headword is separated from body by a tab.
- `simpleprintentry` prints headword only for `h`; otherwise replaces the tab with a space and prints until newline.
- `simplenextoff` advances to the next newline.
- `simpleprintkey` reports no key.

Dependencies:
- Used by Russian-English and English-Russian dictionaries in `utils.c`.

Research notes:
- This is the minimal adapter contract implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/simple.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/slang.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/slang.c

Adapter for the English Slang dictionary format.

Key elements:
- Recognizes two-letter line tags: definition, examples, etymology, labels, main entry, sense number, pronunciation, part of speech, and cross references.
- `slangprintentry` formats tagged pieces into readable prose; `h` mode prints only the main entry.
- `slangnextoff` finds entries beginning with `me `.
- `sget` parses the next recognized tagged value and returns its range.
- `soutpiece` normalizes newlines/spaces and drops `@` characters.

Dependencies:
- Uses `Assoc` lookup and common output helpers.

Research notes:
- Unknown tags can be reported under debug mode.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/slang.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/t.awk -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/t.awk

AWK normalizer for index records containing “ or ” alternatives.

Key elements:
- For two-field records, prints unchanged unless the second field contains ` or ` and is not parenthesized as `(or...)`.
- Splits eligible alternatives on ` or ` and emits one record per alternative.
- Non-two-field records are printed unchanged.

Dependencies:
- Standalone AWK script.

Research notes:
- Used to expand alternate headword forms in index-generation pipelines.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/t.awk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/thesaurus.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/thesaurus.c

Adapter for Collins Thesaurus data.

Key elements:
- `thesprintentry` handles compact markup characters: `*` control sequences, `#` accent encodings, and suppression of selected markers.
- Headword mode stops after the leading lexical section.
- Raw mode writes bytes directly.
- `thesnextoff` locates next entries beginning with `*L`.
- `thesprintkey` reports no key.

Dependencies:
- Uses common output helpers.

Research notes:
- Accent handling is table-based for vowels and cedilla cases embedded as `#` sequences.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/thesaurus.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/utils.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/utils.c

Shared dictionary registry and utility layer.

Key elements:
- Defines `dicts[]`, mapping dictionary names to descriptions, data/index paths, and callbacks.
- Registers OED, AHD, PGW, thesaurus, Roget, world-language dictionaries, Collins variants, Russian simple dictionaries, movie indexes, slang, and Robert variants.
- Defines accent ligature tables and multi-rune expansion tables.
- Provides binary search helpers `lookassoc` and `looknassoc`.
- Provides common diagnostics and output functions with line wrapping and indentation.
- Implements folding for ASCII uppercase and Latin-1 accented characters.
- Implements regex string folding for search.
- Defines `acomp` prefix-aware comparison used by index search.
- Implements `runetol`, `liglookup`, and a translation-table stack `changett`.

Dependencies:
- Central dependency for nearly every dictionary adapter.
- Uses globals declared in `dict.h` and owned by `dict.c` or `mkindex.c`.

Research notes:
- `dicts[]` is both runtime configuration and backend registry.
- Output helpers intentionally collapse or wrap text for terminal readability.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/world.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dict/world.c

Adapter for “Languages of the World” dictionary binary format.

Key elements:
- Entry begins with three big-endian 16-bit lengths: headword, pronunciation/part, and definition sections.
- `worldprintentry` skips the six-byte header, prints only headword length in `h` mode, or the full entry otherwise.
- `worldnextoff` computes the next entry offset from header lengths and requires being called with valid-entry address plus one.
- `putchar` decodes a custom byte encoding with normal single-byte table, Shift-JIS/JIS Japanese mode, and GB mode.
- Uses `tabjis208` and `tabgb2312` after converting double-byte pairs with `S2J`.
- Maintains state for UTF/single-byte mode, Japanese high/low byte, GB high/low byte, and suppressible extended mode.

Dependencies:
- Includes `kuten.h`.
- Uses `jis208.c` and `gb2312.c` tables.

Research notes:
- This one adapter serves many bilingual dictionaries via different data/index paths in `utils.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dict/world.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/diff.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/diff.c

Main entry point for Plan 9 `diff`.

Key elements:
- Parses output mode flags `-e`, `-f`, `-n`, `-c`, `-a`, `-u`.
- Parses whitespace flags `-w` and `-b`, recursive `-r`, and merge/directory behavior `-m`.
- Validates argument count and target path.
- If multiple source files are supplied, requires the final argument to be a directory and enables merge-style path behavior.
- If two directories are compared, enables directory mode.
- Calls `diff(argv[i], target, 0)` for each source.
- Exits with Plan 9 status strings: empty for no changes, `some` for differences, `error` otherwise.

Dependencies:
- Uses globals and functions declared in `diff.h`.
- Directory and regular-file behavior is implemented in other `diff` module files.

Research notes:
- This file is only CLI dispatch; algorithmic diff logic is elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/diff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/diff.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/diff/diff.h

Shared declarations and data structures for Plan 9 `diff`.

Key elements:
- Defines `Line`, `Cand`, `Change`, and `Diff`.
- `Diff` holds original and pruned line arrays, equivalence classes, candidate lists, match vector `J`, file offsets, input buffers, binary flags, and collected changes.
- Declares global CLI state: `mode`, `bflag`, `rflag`, `mflag`, `anychange`, and `stdout`.
- Defines `MAXPATHLEN`, `MAXLINELEN`, `DIRECTORY`, and `REGULAR_FILE`.
- Declares memory helpers, pathname/temp/stat helpers, directory diff, regular diff, diff calculation, IO preparation, checking, change output, cleanup, and line reading.

Dependencies:
- Used by all files in `sys/src/cmd/diff`.

Research notes:
- Comments document deliberate memory overlaying inside `Diff` fields to reuse arrays during the diff algorithm.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/diff/diff.h -->