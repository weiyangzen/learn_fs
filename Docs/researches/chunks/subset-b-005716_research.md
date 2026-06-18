# sources/distributed-fs/ceph-client/fs/nls/nls_cp949.c lines 3982-8200

## Scope

This chunk covers a data-heavy middle section of the Linux NLS CP949 module. It starts inside the tail of `c2u_F1`, continues through the remaining high-byte CP949-to-Unicode pages `c2u_F2` through `c2u_FD`, includes the `page_charset2uni[256]` dispatch table, and then covers the first large run of Unicode-to-CP949 reverse pages from `u2c_01` through the beginning of `u2c_7A`.

The range contains no executable conversion functions by itself. Its behavior is realized later by `char2uni()` and `uni2char()`, which index the tables defined here through `page_charset2uni[]` and `page_uni2charset[]`.

## Purpose

The source file implements the `cp949` / `euc-kr` Linux Native Language Support charset. This chunk supplies the static lookup data needed to translate Korean CP949 double-byte sequences to Unicode code points and to translate selected Unicode pages back to CP949 byte pairs.

The first half is the tail of the forward mapping. Each `c2u_XX[256]` array represents one possible CP949 lead byte. The second byte is used as the array index, and a zero `wchar_t` means the byte pair is unmapped or invalid. The chunk includes high lead-byte pages `0xF1` through `0xFD`, which are mostly compatibility Hanja and other CP949 extension mappings, with large zero-filled gaps for invalid trail ranges.

The second half begins the reverse mapping. Each `u2c_XX[512]` array represents one Unicode high byte/page. For a Unicode character `uni`, later code computes `ch = uni >> 8` and `cl = uni & 0xff`; if `page_uni2charset[ch]` points at one of these arrays, bytes at offsets `cl * 2` and `cl * 2 + 1` provide the CP949 encoded pair. A `0x00, 0x00` pair marks an unmapped Unicode scalar.

## Important APIs, Types, and Tables

`static const wchar_t c2u_F1[256]` is already in progress when the chunk begins. Lines 3982-4002 cover the valid tail of CP949 lead byte `0xF1`, with mappings beginning at trail byte `0xA1` and ending with an invalid `0xFF` slot.

`static const wchar_t c2u_F2[256]` through `c2u_FD[256]` define complete forward pages for lead bytes `0xF2` through `0xFD`. These arrays follow the generated layout used throughout the file: 256 `wchar_t` entries, comments identifying each trail-byte range, and zero entries for invalid CP949 pairs.

`static const wchar_t *page_charset2uni[256]` is the forward dispatch table. It maps CP949 lead bytes to the corresponding `c2u_*` page pointer. For this chunk, the important entries are `c2u_F1` through `c2u_FD`; it also shows the broader file-wide table shape, including a deliberate `NULL` hole at lead byte `0xC9` and `NULL` entries for unused bytes such as `0xFE` and `0xFF`.

`static const unsigned char u2c_01[512]` through `u2c_7A[512]` begin the reverse mapping from Unicode high-byte pages to CP949 byte pairs. The chunk includes complete reverse pages for Unicode pages `0x01`, `0x02`, `0x03`, `0x04`, `0x11`, `0x20`-`0x26`, `0x30`-`0x33`, `0x4E`-`0x79`, and the first entries of `u2c_7A`.

The reverse arrays use `unsigned char` instead of `wchar_t` because each mapped Unicode low byte stores a two-byte encoded CP949 result. Array length is 512 rather than 256, with two output bytes per Unicode low-byte index.

## Control Flow

Forward conversion is driven by code outside this chunk. `char2uni()` checks `boundlen`, treats a one-byte input as a single-byte character, otherwise reads `rawstring[0]` as `ch` and `rawstring[1]` as `cl`. It then loads `charset2uni = page_charset2uni[ch]`. If that page pointer is non-NULL and `cl` is nonzero, `charset2uni[cl]` becomes the Unicode result unless it is `0x0000`, in which case conversion fails with `-EINVAL`. If there is no page pointer, the lead byte is treated as a single-byte value.

For this chunk, that means the `c2u_F1` tail and the complete `c2u_F2`-`c2u_FD` tables are reachable only when the first CP949 byte is in that range and a second byte is present. Zero-filled portions of these tables are active validation data, not padding: they cause `char2uni()` to reject otherwise well-formed two-byte inputs.

Reverse conversion is also driven later. `uni2char()` derives the Unicode page and low byte, loads `uni2charset = page_uni2charset[ch]`, and, when present, copies the two bytes at `cl * 2`. If both bytes are zero, it returns `-EINVAL`; otherwise it returns `2`. If there is no reverse page and the Unicode value is nonzero ASCII-compatible page zero, the function emits one byte directly.

For the reverse tables in this chunk, only Unicode high-byte pages wired into `page_uni2charset[]` are reachable. The arrays here are therefore table payloads; the later dispatch table determines which Unicode pages are consulted.

## State and Persistence Behavior

All data in this range is `static const` module-local storage. It is compiled into the NLS module image and has no runtime mutation, allocation, reference counting, locking, or persistent on-disk state.

The only observable state effect is through conversion results. A nonzero table entry allows a byte sequence or Unicode scalar to round-trip through the NLS layer. A zero table entry becomes an invalid-character signal returned by `char2uni()` or `uni2char()`.

Because the mapping is generated and static, correctness depends on table integrity rather than runtime synchronization. The conversion functions can be called concurrently by filesystem code without touching mutable state in these arrays.

## Dependencies and Integration Points

The tables depend on Linux kernel NLS conventions from `<linux/nls.h>`: charset modules expose `uni2char`, `char2uni`, and case-conversion tables through `struct nls_table`. The generated data also depends on `wchar_t` and the kernel error convention used by the executable functions later in the file.

The module registers the charset name `cp949` with alias `euc-kr`. Filesystems that request this NLS table use these mappings for filename and string conversion between on-disk/network byte encodings and the kernel's Unicode-oriented representation.

Within this file, `page_charset2uni[]` is the integration point between the `c2u_*` arrays and `char2uni()`. The `u2c_*` arrays in this chunk are later integrated through `page_uni2charset[]`, which maps Unicode high bytes to reverse-page pointers.

The code is source-tree-aligned with Linux's generic `fs/nls` pattern. It is not Ceph-specific logic despite living under the Ceph client source mirror; Ceph or other filesystems consume it only through the generic NLS registration and lookup APIs.

## Risks

- Table corruption is high impact. A single wrong value silently maps filenames or other NLS-converted strings to the wrong Unicode character or byte pair.
- Zero entries are semantically meaningful. Accidentally replacing an invalid slot with a nonzero value accepts invalid CP949 byte sequences; accidentally zeroing a valid slot rejects valid Korean or Hanja filenames.
- The chunk boundary starts inside `c2u_F1` and ends inside `u2c_7A`. Merge/reconciliation must not treat this document as covering complete definitions for those two arrays.
- Forward and reverse tables must remain mutually consistent where round-trip behavior is expected. Inconsistency can let `char2uni()` decode a CP949 pair that `uni2char()` cannot encode back, or encode a Unicode scalar to a pair that decodes differently.
- The `page_charset2uni[]` table has deliberate `NULL` holes. Filling an unused lead byte or removing a valid pointer changes whether `char2uni()` treats an input as double-byte CP949 or a single byte.
- `wchar_t` width and kernel Unicode assumptions matter. The values here fit the Linux NLS table model, but mechanical regeneration with a different type or endianness assumption would be unsafe.
- Boundary handling in the conversion functions relies on these arrays having exact sizes. Any manual edit that changes initializer count could compile with unintended padding or fail in ways that affect lookup offsets.

## Test and Validation Signals

Useful validation should focus on table-driven conversion behavior:

- Decode representative CP949 pairs from `0xF1` through `0xFD`, especially valid trail slots near `0xA1`, gaps filled with `0x0000`, and the invalid `0xFF` tail entries.
- Encode representative Unicode values from reverse pages included here, such as pages `0x4E`-`0x79`, and verify `uni2char()` returns the expected two-byte CP949 pairs.
- Negative tests should exercise zero slots in both directions and verify `-EINVAL` rather than silent fallback.
- Boundary tests should cover `char2uni()` with `boundlen == 1`, `boundlen == 2`, lead bytes with `NULL` dispatch pages, and high lead bytes whose tables are in this chunk.
- Round-trip tests should decode selected CP949 pairs from `c2u_F2`-`c2u_FD`, then encode the resulting Unicode code point and compare the resulting bytes where the reverse mapping is defined.
- Build validation should include compiling the NLS module with warnings enabled to catch malformed initializer counts or const-table type mismatches.

## Cross-Chunk Notes

Earlier chunks define `c2u_81` through most of `c2u_F1`. Later chunks continue `u2c_7A`, define the remaining reverse pages through `u2c_FF`, provide `page_uni2charset[]`, define ASCII case tables, and implement `uni2char()`, `char2uni()`, module registration, and metadata.

The final per-file report should describe this chunk as static generated mapping data rather than independent control logic, and should connect it to the executable conversion functions and `struct nls_table` registration near the end of the file.
