# File Research: sources/block-storage/lvm2/lib/misc/lvm-percent.c

This file implements extent percentage conversion.

API:
- `percent_of_extents(uint32_t percents, uint32_t count, int roundup)` returns `percents * count / 100`, optionally rounding up by adding 99 before division.

Correctness note:
- Uses 64-bit intermediate arithmetic to avoid overflow for `uint32_t` inputs.

Role:
- Converts user percentage requests into extent counts.
