# sources/distributed-fs/ceph-client/fs/nls/nls_cp936.c lines 1-3984

## Scope

This chunk covers the opening 3,984 lines of `sources/distributed-fs/ceph-client/fs/nls/nls_cp936.c`, a Linux kernel NLS module implementation for the Simplified Chinese CP936 / GB2312 character set. The assigned range starts with the module comment and kernel/NLS includes, then defines most of the CP936 byte-to-Unicode translation tables from lead byte `0x81` through the beginning of `0xF1`. It stops in the middle of `c2u_F1`; the later chunk continues the remaining `c2u_*` tables, the `page_charset2uni` dispatch table, Unicode-to-CP936 reverse tables, conversion functions, NLS registration, and module metadata.

## Purpose

The code in this range is generated lookup data. Its job is to map two-byte CP936 character sequences to Unicode `wchar_t` values for use by the kernel NLS subsystem. Filesystems and other kernel paths that need filename or text conversion for the `cp936` charset indirectly consume these constants through the NLS table registered later in the file.

This chunk does not implement executable conversion logic itself. It supplies the immutable `c2u_*` pages that later `char2uni()` indexes through `page_charset2uni[ch][cl]`, where `ch` is the CP936 lead byte and `cl` is the trailing byte.

## Important APIs, Types, and Data

- `#include <linux/module.h>`, `<linux/kernel.h>`, `<linux/string.h>`, `<linux/nls.h>`, and `<linux/errno.h>` establish that this file is a kernel module/NLS implementation. In this chunk, only `wchar_t` is directly visible in the data declarations, but later code uses `struct nls_table`, `module_init`, `module_exit`, and `-EINVAL` / `-ENAMETOOLONG`.
- `static const wchar_t c2u_81[256]` through `static const wchar_t c2u_F1[256]` are per-lead-byte CP936-to-Unicode pages. Each array has 256 slots so the second byte can be used directly as an index.
- `0x0000` entries are sentinel values for unmapped or invalid CP936 byte pairs. The downstream `char2uni()` path treats a looked-up `0x0000` as `-EINVAL`, except single-byte fallback handling is outside this chunk.
- Table comments such as `/* 0x40-0x47 */` document the low-byte range for each group of eight entries. These comments are important maintenance aids because this is otherwise dense generated data.

## Table Coverage and Shape

The table set begins at lead byte `0x81`, which is the first non-ASCII CP936 lead-byte page represented by this generated file. Many arrays have no valid entries for low-byte ranges `0x00-0x3F`, and most use `0x0000` at `0x7F`, matching the invalid CP936 trail-byte gap.

The early pages `c2u_81` through `c2u_A0` mostly map into CJK Unified Ideographs and related ranges in increasing Unicode order. `c2u_A1` through `c2u_A9` contain symbol, punctuation, width, kana, Greek, Cyrillic, phonetic, box drawing, and compatibility mappings, including full-width ASCII in `c2u_A3`, Hiragana in `c2u_A4`, Katakana in `c2u_A5`, Greek and vertical forms in `c2u_A6`, Cyrillic in `c2u_A7`, Bopomofo and box/block symbols in `c2u_A8`, and CJK/box drawing/compatibility forms in `c2u_A9`.

From `c2u_AA` onward the chunk alternates between extension ideograph ranges and GB2312-style common Simplified Chinese mappings. For example, `c2u_B0` starts with extended CJK values and then maps common words beginning with Unicode values such as `0x554A`, `0x963F`, `0x57C3`, and `0x6328`; subsequent pages continue the primary GB2312 order through Chinese lexical groups. Later pages in this chunk, including `c2u_D8` through `c2u_F0`, map additional radicals, compatibility ideographs, simplified forms, punctuation-adjacent blocks, radicals/components, and less common CJK ranges.

The assigned range ends after the first visible rows of `c2u_F1`, so `c2u_F1` is incomplete in this chunk. The merge lane should combine this report with the following chunk before deriving whole-file conclusions about complete lead-byte coverage.

## Control Flow

There is no runtime branch or loop in lines 1-3984. The effective control flow is table-driven and occurs later:

1. A caller invokes the file's registered NLS `char2uni()` callback.
2. `char2uni()` reads one or two bytes from the input byte string.
3. For a two-byte candidate, it takes the first byte as a page selector and obtains `page_charset2uni[ch]`.
4. If the page pointer is non-NULL and the trailing byte is nonzero, it reads `charset2uni[cl]`.
5. A `0x0000` table result is rejected as invalid; otherwise the Unicode code point is returned.

This chunk provides the page arrays used in step 4. It is therefore performance-critical in layout but behaviorally simple: correctness depends on byte-exact generated constants.

## State and Persistence

All data in this range is `static const`. It is compiled into the module or kernel image as read-only data and has no mutable state, no persistence, no allocation, no reference counting, and no cleanup requirement. The arrays are shared by all callers once the NLS module is loaded.

There are no locks because the data is immutable. The main state risk is not runtime mutation but static table corruption, truncation, or dispatch-table mismatch.

## Dependencies and Integration Points

- Depends on the kernel NLS contract from `<linux/nls.h>`, although the actual `struct nls_table` initializer is outside this chunk.
- Integrated later by `page_charset2uni[256]`, which maps byte values `0x81` onward to the corresponding `c2u_*` page pointers. The downstream scan shows this index references `c2u_81` through `c2u_FE`.
- Integrated by `char2uni()`, which relies on each page being exactly 256 `wchar_t` entries and on invalid pairs being encoded as `0x0000`.
- Integrated with reverse Unicode-to-CP936 conversion tables (`u2c_*`) later in the file. Those reverse tables should be consistent with the forward mappings here for round-trip behavior where CP936 supports a character.
- Exposed to filesystems through the registered NLS table named `"cp936"` with alias `"gb2312"` later in the file.

## Risks and Edge Cases

- Generated-table drift is the main risk. A single wrong constant silently converts filenames or text to the wrong Unicode character.
- Truncation or missing entries are high-impact. Since array indexing is direct, every `c2u_*` page must have exactly 256 elements. This chunk ends mid-table only because it is a research chunk; the source file itself must continue cleanly.
- `0x0000` is both a valid Unicode code point and the invalid-entry sentinel in two-byte pages. The later `char2uni()` path rejects two-byte mappings to zero, so these pages cannot represent NUL via a two-byte CP936 sequence.
- Lead-byte dispatch must stay aligned with table names. If `page_charset2uni[0xB0]` pointed at the wrong page, conversion would still be memory-safe but semantically broken.
- `wchar_t` size and signedness are kernel/platform concerns hidden behind NLS conventions. The constants in this range fit in the BMP, so they are safe for 16-bit or wider `wchar_t` representations used by the kernel build.
- Bound-length behavior is controlled outside this chunk. The tables assume the caller has already validated that a second byte is available before two-byte lookup.

## Test Signals

Useful validation for this chunk should be data-oriented:

- Compile the file/module to catch malformed initializers, incorrect array lengths, or incomplete declarations.
- Verify `page_charset2uni` later maps every visible page in this chunk to the same lead-byte suffix, especially `0x81` through the completed portion of `0xF1`.
- Spot-check known CP936 mappings against a trusted reference, including `B0 A1 -> U+554A`, `D2 BB -> U+4E00`, full-width ASCII from `A3 A1..A3 FE`, Hiragana/Katakana pages `A4`/`A5`, Greek `A6`, Cyrillic `A7`, and box drawing around `A9 A4`.
- Exercise invalid pairs such as low bytes below `0x40` and `0x7F` in these pages and expect `char2uni()` to return `-EINVAL` for two-byte lookups.
- Round-trip representative values through `char2uni()` and `uni2char()` once the reverse tables from later chunks are included.

## Unresolved Cross-Chunk References

- `c2u_F1` is incomplete at the end of this chunk; pages `c2u_F2` through `c2u_FE` are outside the assigned range.
- `page_charset2uni`, `u2c_*`, `page_uni2charset`, `charset2lower`, `charset2upper`, `uni2char()`, `char2uni()`, `struct nls_table table`, and module init/exit are outside this chunk and must be covered by later chunk reports before producing the final per-file research document.
