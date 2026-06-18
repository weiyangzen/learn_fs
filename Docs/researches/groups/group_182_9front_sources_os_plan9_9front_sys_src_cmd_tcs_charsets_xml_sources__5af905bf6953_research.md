# Group Research: group_182_9front_sources_os_plan9_9front_sys_src_cmd_tcs_charsets_xml_sources__5af905bf6953

Scope: `Docs/research_subset_a.md`, specifically `sources/os/plan9/9front/sys/src/cmd/tcs` and its `font` helper subdirectory. I read all 21 listed files completely.

This group covers `tcs` character-set registry data, conversion entry points for Big5/GB/GBK/JIS/KSC encodings, Cyrillic single-byte tables, GB2312 mapping data, and small font-generation helpers that turn Han mapping tables plus bitmap sources into Plan 9 subfonts.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/charsets.xml -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/charsets.xml

Stores a local copy of the IANA Character Sets registry XML used by the `tcs` build tooling.

Key points:
- XML registry root is `id="character-sets"` with `updated` date `2013-12-20`.
- Describes charset registration rules, MIBenum ranges, alias conventions, and synchronization expectations with the IANA charset MIB.
- Contains 215 `<record>` entries for charset registrations, plus a `<people>` section of registry contacts.
- Contains 653 `<alias>` or `<preferred_alias>` tags and 546 `<xref>` tags.
- Early records cover US-ASCII, ISO-8859 variants, JIS, Shift_JIS, EUC-JP, and many ISO-646 national variants.
- Later records include Unicode/ISO-10646 forms, vendor and Windows/IBM code pages, Mac encodings, GB/KSC/Big5/HZ, UTF-7/8/16/32 variants, BOCU/SCSU, and other registered names.

Dependencies and interactions:
- `mkfile` can fetch this file and uses it with `charsets.awk` and `alias.txt` to generate `alias.h`.
- The XML itself is registry data; it is not parsed by runtime conversion code.

Research relevance:
- Important build-time metadata source for keeping `tcs` charset aliases aligned with IANA names.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/charsets.xml -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/conv.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/conv.h

Declares conversion-function entry points shared by the non-table encoders/decoders.

Key points:
- Declares input functions for JIS variants, Big5, GB2312, GBK, Korean EUC/KSC, HTML entities, and Tune.
- Declares output functions for the same function-backed encodings.
- Defines `emit(x)` as `*(*r)++ = (x)`, the common decoder helper for appending a Rune.
- Defines `NRUNE` as `65536`.
- Declares global `long tab[]`, a shared reverse-lookup table indexed by Rune values for output conversion.

Dependencies and interactions:
- Included by conversion implementations such as `conv_big5.c`, `conv_gb.c`, `conv_gbk.c`, `conv_jis.c`, and `conv_ksc.c`.
- Function pointers are registered from `tcs.c`.

Research relevance:
- Central ABI-like header for `tcs` state-machine conversions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/conv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/conv_big5.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/conv_big5.c

Implements Big5 decoding and encoding around the `tabbig5` mapping table.

Key points:
- `big5proc` is a two-state byte parser: ASCII/control bytes are emitted directly, while bytes `>= 0xA1` start a two-byte Big5 sequence.
- Second bytes are normalized from Big5 trail ranges `0x40-0x7E` and `0xA1-0xFE` into a `BIG5FONT` ordinal.
- Lead bytes are normalized from `0xA1-0xFE`; invalid lead/trail bytes increment `nerrors`, optionally warn, and emit `BADMAP` unless `clean` is set.
- `big5_in` streams file input in `N`-byte chunks, flushes output through `OUT`, sends EOF with `big5proc(-1, ...)`, and terminates downstream with a zero-length `OUT`.
- `big5_out` lazily builds the shared reverse table from `tabbig5`, emits ASCII directly, and writes two-byte Big5 sequences for mapped Runes.
- Unmappable output Runes warn under `squawk`, increment `nerrors`, and emit `BYTEBADMAP` unless `clean` is set.
- There is a branch for `r >= BIG5MAX` after reverse lookup, but reverse table values are built only from indices below `BIG5MAX`, so that branch appears unreachable for the local table.

Dependencies and interactions:
- Includes `big5.h` for `BIG5MAX`, `BIG5FONT`, and `tabbig5`.
- Uses globals/macros from `hdr.h` and `conv.h`: `BADMAP`, `BYTEBADMAP`, `OUT`, `obuf`, counters, `file`, `clean`, and `squawk`.

Research relevance:
- Runtime implementation for Big5 in `tcs`; tightly coupled to the generated/static Big5 table.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/conv_big5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/conv_gb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/conv_gb.c

Implements GB2312 decoding and encoding around the `tabgb` mapping table.

Key points:
- `gbproc` is a two-state parser: bytes below `0xA1` are emitted directly; bytes `>= 0xA1` begin a two-byte GB sequence.
- Valid pairs are converted to a kuten-like ordinal with `(lead - 0xA0) * 100 + (trail - 0xA0)`.
- Unknown or invalid pairs increment `nerrors`, optionally warn with byte offsets and source filename, and emit `BADMAP` unless `clean` is set.
- `gb_in` streams input through `gbproc`, flushes full output buffers via `OUT`, handles EOF, and emits a final zero-length downstream marker.
- `gb_out` lazily builds the shared reverse table from `tabgb`, emits ASCII directly, and encodes mapped Runes as two bytes using the stored ordinal.
- Unmappable Runes warn under `squawk`, increment `nerrors`, and emit `BYTEBADMAP` unless clean output is requested.

Dependencies and interactions:
- Includes `gb.h` for `GBMAX` and `tabgb`.
- `tcs.c` registers this as the functional converter for `gb2312`.

Research relevance:
- Main runtime bridge between GB2312 bytes and Unicode Runes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/conv_gb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/conv_gbk.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/conv_gbk.c

Implements GBK decoding and encoding around the `tabgbk` mapping table.

Key points:
- `gbkproc` treats bytes below `0x80` as direct output and bytes `>= 0x80` as the first byte of a two-byte GBK sequence.
- Combines a byte pair into `lead << 8 | trail`, checks it against `GBKMIN <= code < GBKMAX`, and indexes `tabgbk[code - GBKMIN]`.
- Invalid or unmapped pairs increment `nerrors`, optionally warn, and emit `BADMAP` unless `clean` is set.
- `gbk_in` uses the same buffered streaming pattern as the other multibyte decoders.
- `gbk_out` lazily populates the shared reverse table from `tabgbk`, emits bytes below `0x80` directly, and writes mapped Runes as two GBK bytes.

Dependencies and interactions:
- Includes `gbk.h` for `GBKMIN`, `GBKMAX`, and `tabgbk`.
- Registered by `tcs.c` as the `gbk` converter.

Research relevance:
- Runtime implementation for GBK, including byte-range validation and reverse mapping.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/conv_gbk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/conv_jis.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/conv_jis.c

Implements Japanese JIS-family decoders and encoders for ISO-2022-JP, Shift-JIS, EUC-JP, and a permissive guessing mode.

Key points:
- Includes `kuten208.h`, `kuten212.h`, and `jis.h`.
- Defines four decoder state machines:
  - `alljis`: permissive decoder that handles ISO-2022 escape shifts, 7-bit/8-bit JIS, and Shift-JIS-like pairs.
  - `ms`: Shift-JIS/MS-Kanji decoder with half-width katakana mapping to `0xFEC0 + c`.
  - `ujis`: EUC-JP decoder for JIS X 0208 and JIS X 0212 codeset 3; codeset 2 is reported unsupported.
  - `jis`: stricter ISO-2022-JP/JIS-kanji decoder.
- Escape handling recognizes `ESC $ @`, `ESC $ B`, and `ESC ( J/H/B`, including Japanese Roman mode where backslash maps to Yen and tilde maps to spacing macron.
- Kuten indices are computed from byte pairs and resolved through `tabkuten208` or `tabkuten212`; negative table entries are treated as ambiguous mappings and emitted after sign removal with a warning.
- EOF in the middle of a two-byte sequence is handled by warning and synthesizing a low byte.
- `do_in` centralizes the buffered input loop for all four decoders.
- Exposes `jis_in`, `ujis_in`, `msjis_in`, and `jisjis_in`.
- `tab_init` builds the shared reverse table from `tabkuten208`, using absolute values for ambiguous entries.
- `jisjis_out` emits ISO-2022-JP escape shifts into and out of JIS mode.
- `msjis_out` converts kuten bytes to Shift-JIS using `J2S`.
- `ujis_out` emits EUC-JP bytes by OR-ing both bytes with `0x80`.

Dependencies and interactions:
- Uses conversion macros such as `CANS2J`, `S2J`, and `J2S` from `jis.h`.
- Registered by `tcs.c` under `jis`, `jis-kanji`, `iso-2022-jp`, `ms-kanji`, and `ujis`.

Research relevance:
- Most complex converter in this group; it encodes the stateful Japanese charset handling in `tcs`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/conv_jis.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/conv_ksc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/conv_ksc.c

Implements Korean EUC/KSC 5601 decoding and encoding.

Key points:
- Credits contribution by Teruhiko Kurosaka.
- Defines `SS2` and `SS3`, but support for codesets 2 and 3 is commented out; only codesets 0 and 1 are used.
- `ukscproc` maps ASCII directly, except backslash maps to Unicode Won sign `0x20A9` when `korean646` is enabled.
- Non-ASCII bytes start a two-byte KSC 5601 sequence; the ordinal is `((lead & 0x7f) - 33) * 94 + ((trail & 0x7f) - 33)`.
- Invalid or unknown KSC values increment `nerrors`, optionally warn, and emit `BADMAP` unless `clean` is set.
- `uksc_in` follows the standard buffered decoder pattern.
- `uksc_out` lazily builds the shared reverse table from `tabksc5601`, respecting negative ambiguous entries by indexing their absolute Rune value.
- Mapped output Runes are encoded as two EUC bytes by OR-ing row/cell values with `0x80`.

Dependencies and interactions:
- Includes `ksc.h` for `tabksc5601` and `ksc5601max`.
- Registered by `tcs.c` as `euc-k`.

Research relevance:
- Runtime converter for Korean EUC/KSC handling in `tcs`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/conv_ksc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/cyrillic.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/cyrillic.h

Defines five 256-entry single-byte Cyrillic mapping tables.

Key points:
- Defines `long tabucode[256]`, `tabkoi8[256]`, `tab866[256]`, `tabav[256]`, and `tabov[256]`.
- All tables map ASCII `0x00-0x7f` to identical Unicode code points.
- Unassigned or unsupported byte positions are represented with `-1`.
- `tabucode` maps a compact Russian U-code range to Cyrillic capitals/lowercase beginning around byte `0xB0`.
- `tabkoi8` maps KOI-8/KOI8-R-style byte positions to Cyrillic, including Ukrainian/Belarusian additions such as `0x0404`, `0x0406`, `0x0407`, `0x0490`, and lowercase counterparts.
- `tab866` maps DOS code page 866 Cyrillic ranges, with uppercase and lowercase split across high-byte regions and `0x0401/0x0451` near the end.
- `tabav` and `tabov` cover Alternativnyj Variant and Osnovnoj Variant layouts, including Cyrillic plus symbols such as combining acute/grave, arrows, division, plus-minus, numero, and currency sign.

Dependencies and interactions:
- Included directly by `tcs.c`.
- `tcs.c` registers these arrays as table-backed charsets: `ucode`, `koi8`, `koi8-r`, `866`, `av`, and `ov`.

Research relevance:
- Static single-byte charset mapping data for Cyrillic encodings.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/cyrillic.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/font/bbits.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/font/bbits.c

Reads Big5 bitmap font data and builds a packed Plan 9 `Bitmap`.

Key points:
- Defines Big5 font layout constants `Charsperfont`, `Void1b`, and `Void1e`.
- `breadbits` opens a bitmap source file, allocates a per-character `done` array, and extracts glyph bitmaps for requested Big5 ordinals.
- Skips a known void range and compares glyph data against a static 32-byte `missing` pattern.
- Computes source offsets with Plan 9-specific font-layout adjustments, including a 256-byte header and a documented hole between Big5 ranges.
- Writes requested glyph rows into a wide temporary `bits` buffer, then compacts only present glyphs into `nbits`.
- Allocates a destination `Bitmap` of width `nch * size` and height `size`, writes bitmap data with `wrbitmap`, and returns it.

Dependencies and interactions:
- Called through the `readbitsfn` table in `font/main.c` when source type is Big5.
- Consumes character ordinals produced by `bmap`.

Research relevance:
- Font-build helper for deriving Plan 9 subfonts from Big5 bitmap data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/font/bbits.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/font/bmap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/font/bmap.c

Maps Unicode Rune ranges to Big5 table ordinals for font generation.

Key points:
- Initializes the `chars` output range to zero.
- Scans `tabbig5[0..BIG5MAX)` and records the Big5 ordinal for each Rune in the requested inclusive range.
- Counts missing Runes and prints a diagnostic with the number found and one missing example.
- The failure exit is commented out, so missing glyphs are tolerated.

Dependencies and interactions:
- Includes `../big5.h`.
- Used by `font/main.c` for Big5 font extraction before calling `breadbits`.

Research relevance:
- Small reverse-mapping helper connecting Big5 conversion data to font extraction.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/font/bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/font/font.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/font/font.c

Builds a Plan 9 `Subfont` descriptor from a bitmap and glyph-presence array.

Key points:
- `bf` allocates `Fontchar` metadata for `n + 1` entries.
- For each character, sets fixed-size metrics `{x, 0, size, 0, size}`.
- Advances the packed bitmap x-offset only when `done[i]` is true; missing glyphs get zero width.
- Creates a `Subfont` with `subfalloc`, using height `size` and ascent `size * 7 / 8`.

Dependencies and interactions:
- Called by `font/main.c` after a bitmap reader returns its packed bitmap and `found` array.

Research relevance:
- Converts extracted bitmap glyph data into a serializable Plan 9 subfont.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/font/font.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/font/gbits.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/font/gbits.c

Reads BDF font files for GB glyphs and builds a packed Plan 9 `Bitmap`.

Key points:
- Comment notes that BDF `ENCODING` is font dependent.
- `greadbits` opens a BDF file, allocates a `done` array, and determines the min/max requested character ordinal.
- Scans BDF `STARTCHAR` blocks, reads `ENCODING`, converts it to the GB ordinal `(high - 0xA0) * 100 + (low - 0xA0)`, and reads `BITMAP` hex rows.
- Decodes hex bitmap rows through a local nibble table.
- Copies only requested glyphs into the caller-provided row-major `bits` buffer and marks them done.
- Compacts present glyphs into `nbits`, allocates a packed `Bitmap`, and writes it with `wrbitmap`.
- Helper `field` scans for required BDF fields and exits on malformed or incomplete glyph records.
- The inner glyph-copy loop reuses variable `i` for row iteration inside a loop already using `i` for character lookup; the function breaks immediately after copying, so it works but is fragile.

Dependencies and interactions:
- Called through `font/main.c` for `Gb_bdf`.
- Consumes ordinals produced by `gmap`.

Research relevance:
- BDF-to-Plan-9-bitmap converter for GB subfont generation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/font/gbits.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/font/gmap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/font/gmap.c

Maps Unicode Rune ranges to GB2312 ordinals for font generation.

Key points:
- Initializes all requested `chars` entries to zero.
- Scans `tabgb[0..GBMAX)` and records the GB ordinal for every Rune in the requested range.
- Reports how many requested Runes were found and gives one missing example when there are gaps.
- Does not abort on missing mappings because the exit call is commented out.

Dependencies and interactions:
- Includes `../gb.h`.
- Used by `font/main.c` for both BDF and quwei GB font readers.

Research relevance:
- Reverse lookup bridge from Unicode ranges to GB font source encodings.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/font/gmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/font/hdr.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/font/hdr.h

Declares the small font-generation helper interface.

Key points:
- Defines `readbitsfn`, the bitmap-reader function type.
- Defines `mapfn`, the Unicode-range-to-source-ordinal mapper type.
- Declares readers: `kreadbits`, `breadbits`, `greadbits`, and `qreadbits`.
- Declares mappers: `kmap`, `bmap`, and `gmap`.
- Declares `bf`, the helper that builds a `Subfont`.

Dependencies and interactions:
- Included by all source files in `tcs/font` except `merge.c`.
- Supports the dispatch table in `font/main.c`.

Research relevance:
- Compact local API for the font-conversion utility.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/font/hdr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/font/kbits.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/font/kbits.c

Reads JIS/kuten hex bitmap files and builds a packed Plan 9 `Bitmap`.

Key points:
- `kreadbits` opens a text bitmap source, allocates a `done` array, and computes min/max requested ordinals.
- Skips two header lines before reading glyph rows.
- Parses each line's character ordinal with `strtol(p + 17, ...)`.
- For matching requested ordinals, decodes hex bitmap bytes from `p + 25` into the interleaved `bits` buffer.
- Compacts present glyphs into `nbits`, allocates a `Bitmap` of width `nch * size` and height `size`, and writes bitmap data.
- Like `gbits.c`, reuses loop variable `i` inside the glyph-copy row loop, relying on an immediate break after a match.

Dependencies and interactions:
- Called by `font/main.c` for JIS source data.
- Usually paired with `kmap`, which maps Unicode ranges to JIS X 0208/kuten ordinals.

Research relevance:
- JIS bitmap reader for building Plan 9 Han subfonts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/font/kbits.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/font/kmap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/font/kmap.c

Maps Unicode Rune ranges to JIS X 0208/kuten ordinals for font generation.

Key points:
- Initializes requested `chars` entries to zero.
- Scans `tabkuten208[0..KUTEN208MAX)` and records the kuten ordinal for Runes in the requested range.
- Reports the count of found/missing characters and one missing example when mappings are incomplete.
- Does not abort on missing mappings because the exit call is commented out.

Dependencies and interactions:
- Includes `../kuten208.h`.
- Used by `font/main.c` for JIS font extraction.

Research relevance:
- Reverse mapping from Unicode ranges to JIS/kuten source glyph positions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/font/kmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/font/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/font/main.c

Command-line utility for producing bitmap/subfont data for selected Han character ranges.

Key points:
- Dispatch table supports four source modes: JIS, Big5, GB BDF, and GB quwei.
- Default sources include `../han/jis.bits`, `../han/jis16.bits`, `../han/big5.16.bits`, and `../han/cclib16fs.bdf`.
- Options:
  - `-f file` overrides source file.
  - `-r` treats requested values as raw source ordinals instead of Unicode Runes.
  - `-5` selects Big5.
  - `-s` selects 16-pixel glyph size instead of 24.
  - `-g` selects GB BDF.
  - `-q` selects GB quwei.
- Requires two positional arguments: inclusive `from` and `to`.
- Allocates `bits`, `chars`, and `found`; maps Unicode to source ordinals unless raw mode is set.
- Calls the selected bitmap reader, copies the bitmap into another allocated bitmap, builds a `Subfont` with `bf`, then writes both bitmap and subfont records to stdout.

Dependencies and interactions:
- Uses mappers and readers declared in `hdr.h`.
- Uses Plan 9 graphics APIs from `libg`.

Research relevance:
- Top-level generator tying charset maps and bitmap readers into Plan 9 font artifacts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/font/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/font/merge.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/font/merge.c

Merges multiple Plan 9 subfont files by selecting the first available glyph for each character.

Key points:
- Loads up to 1024 bitmap/subfont pairs into global `ft`.
- `snarf` opens each file, reads its bitmap with `rdbitmapfile`, copies it into owned storage, then reads the associated subfont with `rdsubfontfile`.
- `main` computes the largest character count and checks height/ascent compatibility before allocating an output bitmap and `Fontchar` array.
- `choose` iterates all character indices and source fonts, selecting the first font whose glyph has nonzero width, copying metrics and bitmap bits into the merged output.
- Writes a bitmap file followed by a subfont file to stdout.
- Contains an apparent compatibility-check typo: inside the loop it compares each font against `ft[1].sf->height/ascent` while printing expected values from `ft[0]`; this likely should compare against `ft[0]`.
- Contains leftover interactive/debug code that blits the merged bitmap to `screen`, flushes, and sleeps for five seconds before writing the subfont.
- `choose` calls `bitblt(b, Pt(0, lastx), ...)`; given the output bitmap dimensions, this coordinate order looks suspicious and may reflect old libg coordinate conventions or a bug.

Dependencies and interactions:
- Built separately by `font/mkfile` as `merge`.
- Intended to combine generated font shards, for example `/lib/font/bit/gb/*.7000.24`.

Research relevance:
- Utility for composing generated subfonts, with notable old/debug code paths worth care if reused.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/font/merge.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/font/qbits.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/font/qbits.c

Reads GB quwei-encoded bitmap text data and builds a packed Plan 9 `Bitmap`.

Key points:
- Comment identifies input as quwei encoding for GB.
- `qreadbits` opens a source file, allocates a `done` array, and computes min/max requested ordinals.
- Parses each line's first four decimal digits as the quwei code.
- For requested codes, decodes hex bitmap rows starting at `p + 5` into the caller-provided interleaved bitmap buffer.
- Compacts present glyphs into `nbits`, allocates a packed `Bitmap`, and writes it with `wrbitmap`.
- Same variable-reuse fragility as `kbits.c`/`gbits.c`: `i` is reused for row iteration inside the character-search loop and then immediately breaks.

Dependencies and interactions:
- Used by `font/main.c` in `Gb_qw` mode, usually after `gmap` maps Unicode to GB ordinals.

Research relevance:
- Alternate GB bitmap reader for quwei text sources.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/font/qbits.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/gb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/gb.c

Defines the GB2312-to-Unicode mapping table used by `tcs`.

Key points:
- Includes `gb.h` and defines `long tabgb[GBMAX]`.
- `GBMAX` is 8795, and the file contains exactly 8795 table entries.
- Mapping ordinals correspond to the header's kuten-like GB range representation, with many unused positions represented as `-1`.
- Reading/counting found 7445 mapped entries and 1350 `-1` entries.
- Early mapped entries include CJK punctuation, fullwidth forms, symbols, Hiragana, Katakana, Greek, Cyrillic, pinyin letters, Bopomofo, and box-drawing characters.
- The bulk of the table maps GB2312 Hanzi ordinals to Unicode CJK code points.
- Dense Unicode blocks in the table include `U+30xx`, `U+4Exx`, `U+54xx`, `U+62xx`, `U+6Cxx`, `U+95xx`, `U+53xx`, `U+82xx`, `U+8Dxx`, and `U+80xx`.

Dependencies and interactions:
- Used by `conv_gb.c` for decoding GB byte pairs and by `gb_out` reverse mapping.
- Used by `font/gmap.c` to map Unicode ranges to GB font ordinals.

Research relevance:
- Static mapping data that makes GB2312 conversion and GB font lookup possible.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/gb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/gb.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/gb.h

Defines GB2312 table bounds and exposes the GB mapping table.

Key points:
- Comment states GB ranges from `a1a1` to `f7fe` inclusive.
- Uses a kuten-like mapping from that range to ordinals `101-8794`.
- Defines `GBMAX` as `8795`.
- Declares `extern long tabgb[GBMAX]`.

Dependencies and interactions:
- Included by `gb.c`, `conv_gb.c`, and `font/gmap.c`.

Research relevance:
- Small public contract for the GB2312 mapping table.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/gb.h -->