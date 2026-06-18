# File Research: sources/block-storage/lvm2/libdm/vdo/vdo_parse.c

Purpose: provides shared token parsing helpers for libdm VDO status and stats parsers.

Read coverage: complete file read, 101 lines.

Key responsibilities:
- Skips ASCII whitespace over bounded string slices.
- Compares bounded tokens to NUL-terminated expected strings.
- Parses unsigned decimal tokens into `uint64_t` with empty-token, invalid-character, and overflow detection.
- Maps VDO operating-mode tokens to `enum dm_vdo_operating_mode`.

Important entry points:
- `vdo_parse_eat_space()`
- `vdo_parse_tok_eq()`
- `vdo_parse_uint64()`
- `vdo_parse_operating_mode()`

Dependencies:
- Includes `vdo/vdo_parse.h` and `libdm/misc/dmlib.h`.
- Uses `<ctype.h>` and `UINT64_MAX`.

Risk and edge cases:
- `vdo_parse_uint64()` zeroes the output on parse failure.
- Operating-mode parsing currently recognizes `recovering`, `read-only`, and `normal`.
- Token comparison requires exact length and content.
