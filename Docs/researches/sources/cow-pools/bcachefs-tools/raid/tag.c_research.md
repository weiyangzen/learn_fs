# File Research: sources/cow-pools/bcachefs-tools/raid/tag.c

This file maps active RAID function pointers to short backend tags for diagnostics or reporting.

Key behavior:
- Builds a static `RAID_FUNC[]` table from function pointer to backend name.
- Always includes generic integer backends such as `int8`, `int32`, and `int64`.
- Conditionally includes x86/x86_64 SIMD backends depending on build flags:
  - `sse2`
  - `ssse3`
  - `avx2`
  - extended x86_64 variants such as `sse2e`, `ssse3e`, and `avx2e`
- `raid_tag()` returns the matching string for a function pointer, or `"unknown"` as a fallback.

Exported tag helpers:
- Parity generation tags: `raid_gen1_tag()` through `raid_gen6_tag()`, plus `raid_genz_tag()`.
- Recovery tags: `raid_rec1_tag()`, `raid_rec2_tag()`, and `raid_recX_tag()`.

Dependencies:
- Uses dispatch globals from `internal.h`, including `raid_gen_ptr[]`, `raid_genz_ptr`, and `raid_rec_ptr[]`.
