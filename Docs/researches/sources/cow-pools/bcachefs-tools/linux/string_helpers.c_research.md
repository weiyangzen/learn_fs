# File Research: sources/cow-pools/bcachefs-tools/linux/string_helpers.c

## Purpose
Linux `string_get_size()` helper for human-readable byte/block size formatting.

## Behavior
- Supports decimal (`B`, `kB`, `MB`, ...) and binary (`B`, `KiB`, `MiB`, ...) units.
- Produces 3 significant figures with decimal rounding.
- Handles large `size * blk_size` products by logarithmically reducing operands before multiplication.
- Outputs `"UNK"` if unit index exceeds the known table.

## API
- `string_get_size(u64 size, u64 blk_size, enum string_size_units units, char *buf, int len)`

## Dependencies
Uses Linux math/division/string helper headers and exports the symbol.
