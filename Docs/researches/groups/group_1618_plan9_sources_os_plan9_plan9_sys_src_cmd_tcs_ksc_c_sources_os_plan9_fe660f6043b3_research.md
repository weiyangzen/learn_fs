# Group Research: group_1618_plan9_sources_os_plan9_plan9_sys_src_cmd_tcs_ksc_c_sources_os_plan9_fe660f6043b3

Scope: `Docs/research_subset_a.md` includes `sources/os/plan9/plan9`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/ksc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/ksc.c

## Purpose

`ksc.c` is a generated/static mapping table for Plan 9 `tcs` Korean character conversion. It maps KS C 5601 / KSC 5601 two-byte code positions to Unicode rune values.

## Contents

- Includes `ksc.h`.
- Defines `long tabksc5601[]`.
- Defines `int ksc5601max = sizeof(tabksc5601)/sizeof(tabksc5601[0])-1`.

The table comment explains the indexing rule:

- KSC uses 94x94 code positions.
- Each byte’s 7-bit portion is offset by `33` (`0x21`), not `32`.
- Lookup index is `(n - 33) * 94 + (m - 33)` for KSC bytes `(n, m)`.
- `-1` entries mean undefined/unmapped code positions.
- The final `0` is a sentinel/end marker, excluded from `ksc5601max`.

## Integration

`conv_ksc.c` uses this file through `ksc.h`:

- Input path computes `n = ((lastc & 0x7f) - 33) * 94 + (c & 0x7f) - 33`.
- It rejects indexes `>= ksc5601max` or table values `< 0`.
- Output path builds the reverse global `tab[NRUNE]` from `tabksc5601`.

The table supports `euc-k`, `euc-kr`, and `ks_c_5601-1987` converter entries registered in `tcs.c`.

## Notes

This file contains no executable conversion logic beyond `ksc5601max`; its correctness depends entirely on table order, sentinel placement, and the `conv_ksc.c` indexing formula. Any edit to table length or ordering can silently corrupt Korean conversion.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/ksc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/ksc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/ksc.h

## Purpose

`ksc.h` declares the KSC 5601 mapping table and its usable length for Korean conversion code.

## Contents

- `extern long tabksc5601[];`
- `extern int ksc5601max;`

Both are defined in `ksc.c`.

## Integration

`conv_ksc.c` includes this header to access the forward and reverse mapping source for Korean EUC/KSC conversion. The comments state that the table is indexed by kuten-style positions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/ksc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/kuten208.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/kuten208.c

## Purpose

`kuten208.c` defines the JIS X 0208 Unicode mapping table used by Plan 9 `tcs` Japanese encoders and decoders.

## Contents

- Includes `kuten208.h`.
- Defines `long tabkuten208[KUTEN208MAX]`.
- Uses `-1` for invalid or unassigned kuten positions.
- Starts with padding entries so callers can index directly by the encoded kuten number used in `conv_jis.c`.

The table includes punctuation, kana, Greek, Cyrillic, box drawing characters, common CJK ideographs, and extended rows represented as Unicode code points.

## Integration

`conv_jis.c` includes `kuten208.h` and uses `tabkuten208` for several Japanese input paths:

- ISO-2022-JP / `jis-kanji`.
- Shift-JIS / `ms-kanji`.
- EUC-JX / `ujis`.
- Guessing mode `jis`.

Typical lookup flow:

- Convert input bytes into a kuten208 integer.
- Check `n >= KUTEN208MAX` or `tabkuten208[n] == -1`.
- Emit `BADMAP` on unmapped input unless `clean` is enabled.
- For output, `tab_init()` builds a reverse map from rune to kuten index.

`font/kmap.c` also reads `tabkuten208` to create font mapping data.

## Notes

This is a core data dependency for Japanese conversion. The fixed macro size from `kuten208.h` is part of the ABI between the table and callers. Table order and padding are semantically significant.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/kuten208.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/kuten208.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/kuten208.h

## Purpose

`kuten208.h` declares the JIS X 0208 mapping table contract.

## Contents

- `#define KUTEN208MAX 8407`
- `extern long tabkuten208[KUTEN208MAX];`

## Integration

`conv_jis.c` uses `KUTEN208MAX` for bounds checks before indexing `tabkuten208`. `font/kmap.c` also iterates exactly `KUTEN208MAX` entries. The macro must match the initializer length in `kuten208.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/kuten208.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/kuten212.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/kuten212.c

## Purpose

`kuten212.c` defines a JIS X 0212-style supplementary kuten-to-Unicode table.

## Contents

- Includes `kuten212.h`.
- Defines `long tabkuten212[KUTEN212MAX]`.
- Uses `-1` for unassigned positions.
- Contains large ranges of symbols, accented Latin/Greek/Cyrillic characters, and many CJK ideographs.

The layout mirrors the other kuten table style: direct numeric indexing into a fixed-length array, with many sparse holes.

## Integration

The local cross-reference pass found `kuten212.h` and `kuten212.c` in the tree, but no active converter in this `tcs` directory references `tabkuten212`. In the current source snapshot, it appears to be a prepared/static mapping asset rather than wired into the converter registry in `tcs.c`.

## Notes

Because no active call site was found, the primary risks are dead-code drift and table-size mismatch if a future converter starts using it. If activated, callers should follow the same pattern as `tabkuten208`: bounds check against `KUTEN212MAX`, treat `-1` as unmapped, and preserve table indexing semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/kuten212.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/kuten212.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/kuten212.h

## Purpose

`kuten212.h` declares the JIS X 0212 supplementary mapping table contract.

## Contents

- `#define KUTEN212MAX 7768`
- `extern long tabkuten212[KUTEN212MAX];`

## Integration

`kuten212.c` defines the table. No active converter reference to `tabkuten212` was found in this `tcs` directory during the cross-reference pass.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/kuten212.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/misc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/misc.h

## Purpose

`misc.h` defines multiple 256-entry single-byte character-set-to-Unicode tables used directly by `tcs.c`.

## Contents

Tables defined:

- `tabatari`: Atari ST character set, with ASCII identity in the lower half and accented Latin, Hebrew, Greek, and math symbols in the upper half.
- `tabebcdic`: EBCDIC to Unicode/ASCII-ish mapping with many `-1` invalid entries and comments for known substitutions.
- `tabmacroman`: Macintosh Standard Roman mapping.
- `tabnextstep`: NEXTSTEP encoding vector mapping, including combining marks and `0xFFFF` placeholders at the end.
- `tabps2`: IBM PS/2-style mapping, noted in `tcs.c` as aliased to IBM code page 850 for the active converter registry.
- `tabsf1`, `tabsf2`: Finnish/Swedish ISO-646 variants with many invalid upper-half entries.
- `tabtis620`: Thai TIS 620 mapping.
- `tabviet1`, `tabviet2`: Vietnamese VSCII variants.
- `tabviscii`: Vietnamese VISCII 1.1 mapping.

## Integration

`tcs.c` includes `misc.h` directly and registers most tables in `convert[]` as `Table` converters:

- `atari`, `ebcdic`, `macrom`, `next`, `sf1`, `sf2`, `tis-620`, `viet1`, `viet2`, `vscii`.
- `ps2` is present in this file, but `tcs.c` maps `ps2` to `tabcp850` from `ms.h`, not to `tabps2`.

For `Table` converters, `tcs.c` dispatches through `intable()`, which treats these arrays as byte-to-rune maps.

## Notes

This header defines storage, not just declarations. It is intended to be included once by `tcs.c`; including it from multiple translation units would create duplicate global definitions. `-1` entries are meaningful conversion failures.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/misc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/ms.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/ms.h

## Purpose

`ms.h` defines Microsoft/IBM/OEM/Windows 256-entry code page tables for Plan 9 `tcs`.

## Contents

The file begins with a commented Plan 9 `rc` script showing how tables were generated from Microsoft GlobalDev reference pages. It then defines these arrays:

- `tabcp437`
- `tabcp720`
- `tabcp737`
- `tabcp775`
- `tabcp850`
- `tabcp852`
- `tabcp855`
- `tabcp857`
- `tabcp858`
- `tabcp862`
- `tabcp866`
- `tabcp874`
- `tabcp1250`
- `tabcp1251`
- `tabcp1252`
- `tabcp1253`
- `tabcp1254`
- `tabcp1255`
- `tabcp1256`
- `tabcp1257`
- `tabcp1258`

Each maps byte values `0x00..0xff` to Unicode rune values, with `-1` where the code page leaves a byte undefined.

## Integration

`tcs.c` includes `ms.h` directly and registers these tables under `ibm*`, `windows-*`, and compatibility aliases:

- `ibm437`, `msdos` -> `tabcp437`
- `ibm720`, `ibm737`, `ibm775`, `ibm850`, `ibm852`, `ibm855`, `ibm857`, `ibm858`, `ibm862`, `ibm866`, `ibm874`
- `windows-1250` through `windows-1258`
- `microsoft` -> `tabcp1252`
- `ps2` -> `tabcp850`

The arrays are used via generic table conversion in `tcs.c`.

## Notes

Like `misc.h`, this is a storage-defining header. It should not be included in multiple C files unless the build intentionally wants duplicate definitions, which standard C linkers generally reject. The active registry in `tcs.c` is the source of which arrays are reachable by command-line charset names.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/ms.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/plan9.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/plan9.h

## Purpose

`plan9.h` supplies a small Plan 9 compatibility layer for non-Plan 9 builds of `tcs`.

## Contents

- Defines `Rune` as `unsigned long`.
- Defines `uchar` as `unsigned char`.
- Defines UTF constants:
  - `Runeerror 0x80`
  - `Runeself 0x80`
  - `UTFmax 6`
- Defines Plan 9-style argument parsing macros:
  - `ARGBEGIN`
  - `ARGEND`
  - `ARGF()`
  - `ARGC()`
- Declares `extern char *argv0`.

## Integration

Several converter files include `plan9.h` under non-Plan 9 builds, including `tcs.c`, `utf.c`, and conversion modules such as `conv_jis.c`, `conv_ksc.c`, `conv_big5.c`, `conv_gb.c`, and `conv_gbk.c`.

`tcs.c` uses `ARGBEGIN`/`ARGEND` for command-line parsing and owns the `argv0` definition.

## Notes

This file is portability glue. Its macro behavior is part of the command-line parser contract, so changes can affect all option parsing in `tcs`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/plan9.h -->