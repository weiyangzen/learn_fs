# Chunk Research: sources/os/linux/linux-stable/fs/nls/nls_cp932.c lines 1-4152

## Scope

This report covers only `sources/os/linux/linux-stable/fs/nls/nls_cp932.c` lines 1-4152 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely. The chunk begins at the file header and ends inside the `u2c_6B` reverse mapping table; the actual conversion functions and NLS registration are in later chunks.

## APIs And Data

This chunk defines generated, file-local lookup data for the Linux NLS `cp932`/Shift-JIS charset module. The only visible public-facing contract is indirect through `<linux/nls.h>` and later `struct nls_table` registration; no callable function is defined in this chunk.

Forward CP932-to-Unicode data:

- `c2u_81` through `c2u_84`, `c2u_87` through `c2u_9F`, `c2u_E0` through `c2u_EA`, `c2u_ED`, `c2u_EE`, and `c2u_FA` through `c2u_FC`: `static const wchar_t[256]` tables keyed by the second byte after a CP932 lead byte. Zero entries mark unmapped byte positions.
- `page_charset2uni[256]`: dispatch table keyed by CP932 lead byte. It contains `NULL` for invalid/non-table lead bytes and points to the matching `c2u_*` table for valid two-byte ranges.

Reverse Unicode-to-CP932 data starts here:

- `u2c_00hi[256 - 0xA0][2]`: compact table for Unicode `U+00A0` through `U+00FF`, storing two output bytes per Unicode code point.
- `u2c_03`, `u2c_04`, `u2c_20` through `u2c_26`, `u2c_30`, `u2c_32`, `u2c_33`, and `u2c_4E` through the beginning of `u2c_6B`: `static const unsigned char[512]` pages, where each low-byte index maps to a two-byte CP932 sequence or `{0x00, 0x00}` for unmapped.

## Control Flow

There is no executable control flow in this chunk: no functions, branches, loops, allocation, locking, registration, or error handling. Runtime behavior is table-driven in later code.

The table shapes imply the later conversion paths:

- CP932-to-Unicode conversion selects `page_charset2uni[lead]`, rejects `NULL`, then indexes the selected `wchar_t[256]` table by trail byte.
- Unicode-to-CP932 conversion selects a Unicode high-byte page table, then reads the two-byte pair at `2 * low_byte`.
- Entries of all zeroes represent missing mappings; single-byte ASCII/kana handling and NLS return codes are outside this chunk.

## State And Dependencies

All state here is immutable static data in kernel text/rodata once linked. There is no mutable state and no per-mount, per-superblock, or per-inode data.

Direct dependencies visible in this chunk:

- Kernel headers: `<linux/module.h>`, `<linux/kernel.h>`, `<linux/string.h>`, `<linux/nls.h>`, and `<linux/errno.h>`.
- Kernel `wchar_t` and NLS table conventions from `<linux/nls.h>`.
- Generated Microsoft CP932 mapping data, including NEC/IBM extension ranges and compatibility mappings.

The data is tightly coupled to later declarations in the same file: `page_uni2charset`, `charset2lower`, `charset2upper`, `uni2char`, `char2uni`, `struct nls_table`, and module init/exit registration all consume or expose this table set in later chunks.

## Risks

The main risk is silent filename translation corruption. A single wrong table cell can make filesystem names fail to round-trip, collide after conversion, or display differently across systems using CP932.

Several ranges contain CP932 compatibility and vendor-extension mappings, especially lead bytes `0x87`, `0xED`, `0xEE`, `0xFA`-`0xFC`, and reverse rows using `0xED`/`0xFA` output bytes. These are not generic Shift-JIS tables; replacing them with a JIS-only mapping would change behavior for existing media.

Duplicate or compatibility Unicode code points are visible across extension tables, for example Roman numerals and fullwidth/compatibility symbols in `c2u_87`, `c2u_EE`, and `c2u_FA`. Later reverse tables must choose one canonical byte sequence, so round-trip behavior may be asymmetric for duplicate Unicode mappings.

The `{0x00, 0x00}` sentinel in reverse tables is also the representation for "no mapping"; later code must special-case ASCII/NUL or avoid interpreting the sentinel as a valid encoded NUL pair.

## Cross-Chunk References

This is chunk 1 for `nls_cp932.c`. It starts at the file header and complete forward mapping block, then begins the reverse mapping block.

The next chunk must continue from the middle of `u2c_6B`, complete the remaining reverse Unicode pages, and define `page_uni2charset`. It must also cover `charset2lower`, `charset2upper`, `uni2char`, `char2uni`, `struct nls_table`, and module registration.

No final per-file report was created for this chunk.