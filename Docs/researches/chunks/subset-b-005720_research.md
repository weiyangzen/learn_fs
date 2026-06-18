# sources/distributed-fs/ceph-client/fs/nls/nls_cp950.c lines 4047-8283

## Scope

This chunk covers the middle of the generated Unicode-to-CP950 conversion data in `nls_cp950.c`. It starts at the final four rows of `u2c_53`, contains the full explicit initializer blocks for `u2c_54` through `u2c_91`, and ends inside `u2c_92` just before that table's final `0xFC-0xFF` row and closing brace.

The source file as a whole is a Linux NLS module for Traditional Chinese CP950/Big5. Earlier chunks define CP950-to-Unicode `c2u_*` tables and the start of the Unicode-to-CP950 `u2c_*` tables. Later lines define the remaining `u2c_*` pages, `page_uni2charset[]`, ASCII case-fold tables, `uni2char()`, `char2uni()`, the `struct nls_table`, and module registration.

## Purpose

The purpose of this range is to provide static reverse mapping data for Unicode code points whose high byte is mostly in the contiguous CJK area from `0x54` through `0x92`. Each `u2c_XX[512]` array is indexed by the low byte of a Unicode `wchar_t`; the two bytes at `low * 2` and `low * 2 + 1` are the encoded CP950 lead and trail bytes returned by `uni2char()`.

The tables are sparse. A `0x00, 0x00` pair means that the Unicode code point has no CP950 mapping in this generated table. Some arrays have fewer than 512 explicit initializer bytes; C zero-initialization fills the rest, so omitted trailing entries are also unmapped.

## Important Data Structures

- `static const unsigned char u2c_53[512]`: this chunk contains only low-byte rows `0xF0-0xFF`, mapping the end of Unicode page `0x53xx`.
- `static const unsigned char u2c_54[512]` through `u2c_91[512]`: full page arrays in this chunk. These cover a large portion of the CJK Unified Ideographs block and related CP950 mappings.
- `static const unsigned char u2c_92[512]`: this chunk contains rows `0x00-0xFB`; the final row and closing brace continue immediately after the chunk.
- Later `page_uni2charset[256]`: points Unicode high-byte indexes to these `u2c_*` tables. For example, high byte `0x54` selects `u2c_54`, high byte `0x91` selects `u2c_91`, and high byte `0x92` selects `u2c_92`.

The chunk contains 31,880 explicit hex byte initializers. These are data bytes, not executable instructions. Pairs with at least one non-zero byte represent CP950 encodings; all-zero pairs represent invalid or unsupported Unicode-to-CP950 conversions.

## Runtime API Integration

The executable consumer is `uni2char()` later in the file:

- It splits a Unicode value into `ch = (uni >> 8) & 0xff` and `cl = uni & 0xff`.
- It loads `page_uni2charset[ch]`.
- If the page pointer is non-NULL, it requires at least two output bytes, reads `table[cl * 2]` and `table[cl * 2 + 1]`, and returns `-EINVAL` when both bytes are zero.
- If no page table exists and the value is non-zero ASCII (`ch == 0 && cl`), it emits one byte.
- Otherwise it rejects the Unicode code point.

This chunk therefore supplies the lookup backing for many successful two-byte conversions. It has no direct calls, exported symbols, locks, allocations, or local function definitions.

## Control Flow

There is no local control flow in lines 4047-8283. Runtime behavior is table-driven:

1. Filesystem or VFS charset code calls the NLS table's `uni2char` callback.
2. `uni2char()` chooses a `u2c_*` page from `page_uni2charset[]` by Unicode high byte.
3. The low byte indexes a two-byte slot in the selected array.
4. A non-zero pair is copied to the caller's output buffer as CP950.
5. A zero pair becomes `-EINVAL`, signaling an unmappable character.

The start and end boundaries are partial table boundaries. The merge lane should connect this report with adjacent chunks for the beginning of `u2c_53` and the final row of `u2c_92`.

## State and Persistence Behavior

The arrays are `static const`, so they are read-only after compilation and shared by all callers of the loaded NLS module. They hold no mutable process, inode, mount, or Ceph state. Persistence is limited to compiled kernel/module image data.

The only observable state behavior is deterministic conversion success or failure. A table edit changes every consumer's interpretation of affected Unicode code points for CP950/Big5 names and strings, including mounted filesystems that request this NLS charset.

## Dependencies

This chunk depends on standard C initializer semantics and the Linux NLS interface used elsewhere in the same file:

- `<linux/nls.h>` defines `struct nls_table` and registration APIs.
- `<linux/errno.h>` supplies `-EINVAL` and `-ENAMETOOLONG` used by the conversion functions.
- `page_uni2charset[]` later in this file must include pointers for the high-byte pages defined here.
- `uni2char()` assumes every pointed table has 512 bytes addressable as 256 two-byte entries.

The data itself appears generated from a CP950 mapping source, matching the file header's note that the translation table was generated from Microsoft Unicode code page data.

## Integration Points

This NLS table is registered as charset `"cp950"` with alias `"big5"`. Kernel clients that use `load_nls("cp950")` or the Big5 alias can invoke these mappings through the generic NLS conversion callbacks.

In this repository tree, the file is under `sources/distributed-fs/ceph-client/fs/nls/`, so the practical integration surface is filesystem filename and string conversion code in the Ceph-client kernel source snapshot, plus any other filesystem path that uses Linux NLS modules. This data does not call Ceph-specific APIs; it is a common kernel charset implementation used by filesystem layers.

## Risks

- Table corruption is silent at compile time when byte pairs remain syntactically valid. A wrong pair maps a Unicode character to the wrong CP950 byte sequence.
- All-zero pairs are semantically significant. Changing a zero pair to non-zero broadens accepted conversions; changing a non-zero pair to zero creates `-EINVAL` failures.
- Partial initializers rely on C zero-fill. Automated rewrites that expand, trim, or reorder initializers can accidentally alter unmapped trailing ranges.
- Bounds are enforced by `uni2char()` only through table size and `boundlen`; a mismatched `page_uni2charset[]` pointer to an array with the wrong shape would make low-byte indexing unsafe.
- CP950/Big5 contains vendor-specific and compatibility mappings. Regenerating from a different mapping source can change behavior even when Unicode names look similar.

## Test Signals

Useful validation signals for this chunk are table-driven:

- Build the NLS module and ensure the compiler accepts every `u2c_*[512]` initializer without size warnings.
- Unit or integration tests should verify representative Unicode points from pages `0x54`, `0x5F`, `0x6D`, `0x7E`, `0x8B`, `0x91`, and `0x92` convert to expected two-byte CP950 output.
- Negative tests should choose known zero-pair entries and assert `uni2char()` returns `-EINVAL`.
- Buffer-boundary tests should call `uni2char()` with `boundlen == 1` for mapped two-byte characters and expect `-ENAMETOOLONG`.
- Round-trip tests should compare this reverse mapping with the earlier `c2u_*` tables for characters that are expected to be bijective in CP950.

## Cross-Chunk Notes

The final per-file report should merge this with adjacent chunks because this range is not independently meaningful as a complete module:

- `u2c_53` begins before line 4047.
- `u2c_92` ends after line 8283.
- `page_uni2charset[]` and `uni2char()` are after this chunk and are required to explain exactly how the arrays are dispatched.
- `char2uni()`, `page_charset2uni[]`, `charset2lower`, `charset2upper`, and module registration are outside this range but complete the file's public NLS behavior.
