# Group Research: group_1616_plan9_sources_os_plan9_plan9_sys_src_cmd_tcs_gb_c_sources_os_plan9__069295c0890b

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/gb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/gb.c

## Role

`gb.c` is a static GB character-set mapping table for Plan 9’s `tcs` character-set conversion tool. It defines `tabgb`, an array indexed by a GB ordinal, where each populated entry contains the corresponding Plan 9 `Rune`/Unicode code point and each unsupported or unused position is `-1`.

The file is data-only apart from `#include "gb.h"` and the single global definition:

```c
long tabgb[GBMAX] = { ... };
```

## Table Contract

`tabgb` has exactly `GBMAX` entries, matching `GBMAX == 8795` from `gb.h`.

The GB ordinal scheme is documented in `gb.h`: GB byte pairs from `0xA1A1` through `0xF7FE` are mapped “kuten-like” to ordinals `101` through `8794`. Runtime users compute:

```c
n = (first_byte - 0xA0) * 100 + (second_byte - 0xA0);
```

So `0xA1A1` becomes ordinal `101`, and the table deliberately leaves ordinals below `101` as `-1`.

## Contents

The initializer contains:

- `8795` total entries.
- `7445` mapped rune values.
- `1350` `-1` sentinel gaps.
- First mapped entry: index `101`, value `0x3000`.
- Last mapped entry: index `8794`, value `0x9f44`.
- Minimum mapped rune value observed: `0x00a4`.
- Maximum mapped rune value observed: `0xffe5`.
- One duplicate mapped rune value: `0x2225`, appearing at indexes `112` and `146`.

The early table entries cover punctuation and symbols, then numbered/circled forms, Roman numerals, fullwidth ASCII-like forms, hiragana, katakana, Greek, Cyrillic, pinyin/Bopomofo, box drawing, and then the bulk GB Han character mapping. Later ranges include many simplified Chinese code points and compatibility/specialized CJK-related forms.

## Runtime Use

`conv_gb.c` consumes this table in both directions.

For GB input, `gbproc()` forms the ordinal from a two-byte GB sequence and does:

```c
ch = tabgb[n];
```

A negative entry is treated as an unknown GB glyph and emits `BADMAP` unless clean mode suppresses it.

For GB output, `gb_out()` builds a reverse lookup table by scanning all `GBMAX` entries and assigning:

```c
tab[tabgb[i]] = i;
```

Only non-`-1` values participate. If duplicate rune values exist, the later index wins in the reverse table; for `0x2225`, ordinal `146` overrides ordinal `112`.

`font/gmap.c` also scans `tabgb` to create GB glyph maps for requested rune ranges.

## Error and Boundary Behavior

The table itself performs no checks. Correctness depends on callers respecting the documented ordinal range. `conv_gb.c` only forms table indexes for second bytes `>= 0xA1`; because the documented high byte range ends at `0xF7`, valid GB ordinals stay within `0..8794`. Bytes beyond the documented GB high-byte range could compute ordinals beyond `GBMAX` if not filtered elsewhere.

`-1` is a semantic value, not an initialization artifact: it marks unmapped GB ordinal slots, reserved positions, and ordinals outside the useful `101..8794` range.

## Filesystem Relevance

This file is not part of Plan 9’s filesystem implementation. Its relevance to the repository subset is as OS userland support code: Plan 9 ships `tcs` for text encoding conversion, and this table provides GB encoding translation data used by command-line tooling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/gb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/gb.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/gb.h

## Role

`gb.h` declares the shared interface for Plan 9 `tcs` GB encoding conversion support. It defines the size and indexing convention for `tabgb`, which is implemented in `gb.c`.

## Contents

The header documents that GB byte pairs range from `0xA1A1` to `0xF7FE` inclusive and are mapped with a “kuten-like” ordinal scheme to `101..8794`.

It defines:

```c
#define GBMAX 8795
```

and declares:

```c
extern long tabgb[GBMAX];
```

The comment on `tabgb` states that it stores runes indexed by GB ordinal.

## Consumers

`gb.c` includes this header to size and define `tabgb`.

`conv_gb.c` includes it to translate GB input byte pairs into runes and to build a reverse rune-to-GB table for output.

`font/gmap.c` includes it via `../gb.h` to map rune ranges back to GB ordinals for font tooling.

## Contract Notes

The `GBMAX` value is one greater than the maximum documented ordinal, so ordinal `8794` is the last valid table index. Ordinals below `101` are possible array indexes but do not correspond to valid GB byte pairs under the documented scheme.

This header contains no include guards, but it only provides a macro and an `extern` declaration, so repeated inclusion would not define storage.

## Filesystem Relevance

This file is not filesystem code. It is OS userland conversion-tool infrastructure within the Plan 9 source tree.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/gb.h -->