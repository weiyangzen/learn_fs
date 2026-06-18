# sources/distributed-fs/ceph-client/fs/nls/nls_cp950.c lines 1-4046

## Scope

This chunk covers the generated CP950/Big5 NLS translation data at the start of `nls_cp950.c`. It includes the module comment, Linux kernel/NLS headers, all forward charset-to-Unicode page tables from `c2u_A1` through `c2u_F9`, the `page_charset2uni[256]` dispatcher table, and the first reverse Unicode-to-charset tables through most of `u2c_53`. The assigned range ends inside `u2c_53`; `u2c_54` and later reverse tables plus the conversion functions and module registration live after this chunk.

## Purpose

The code provides the static lookup data used by the Linux NLS layer to translate Traditional Chinese CP950/Big5 byte sequences to Unicode and back. CP950 is a mixed single-byte/double-byte encoding: ASCII is handled algorithmically in the later conversion functions, while non-ASCII two-byte sequences use these page tables. The first byte selects a charset page, and the second byte indexes a 256-entry `wchar_t` table for charset-to-Unicode conversion.

The reverse tables encode Unicode code-point pages into two-byte CP950 values. Each `u2c_*[512]` table stores 256 pairs of bytes, so a Unicode value's low byte selects a two-byte result. A zero pair means no CP950 mapping in this table.

## Important APIs, Types, and Data

The chunk does not define executable APIs or functions. Its important objects are static constant data consumed by `char2uni()` and `uni2char()` later in the same file.

- `static const wchar_t c2u_A1[256]` through `c2u_F9[256]`: forward mapping pages for CP950 lead bytes `0xA1` through `0xF9`, with some page gaps. Populated entries map trail-byte offsets to Unicode code points; `0x0000` denotes unmapped or invalid positions.
- `static const wchar_t *page_charset2uni[256]`: page selector for forward conversion. It points lead bytes `0xA1`-`0xC6`, skips `0xC7`/`0xC8`, maps `0xC9`-`0xF9`, and leaves unsupported lead-byte values as `NULL`.
- `static const unsigned char u2c_02[512]`, `u2c_03[512]`, `u2c_20[512]`, `u2c_21[512]`, `u2c_22[512]`, `u2c_23[512]`, `u2c_25[512]`, `u2c_26[512]`, `u2c_30[512]`, `u2c_31[512]`, `u2c_32[512]`, `u2c_33[512]`: reverse mappings for punctuation, Greek, roman numerals, arrows, mathematical symbols, box drawing, Bopomofo, and compatibility/fullwidth ranges.
- `static const unsigned char u2c_4E[512]` through `u2c_52[512]` and the beginning of `u2c_53[512]`: reverse mappings for CJK Unified Ideographs in Unicode pages `0x4E`-`0x53`, covering many of the common Han characters that appear in Big5/CP950.
- Headers: `<linux/module.h>`, `<linux/kernel.h>`, `<linux/string.h>`, `<linux/nls.h>`, and `<linux/errno.h>` provide module metadata, kernel types, NLS table definitions, and error codes for the later conversion/registration code.

The generated source comment says the translation table came from Microsoft CP/Unicode mapping data. That matters because the code is table-driven rather than hand-authored algorithmic conversion logic.

## Control Flow

There is no runtime control flow in this chunk. The control path is implicit and table-driven:

1. Forward conversion later reads the first byte of a raw CP950 sequence.
2. If the byte is ASCII, later code can emit the same Unicode scalar directly.
3. If the byte is a double-byte lead byte, later code indexes `page_charset2uni[first_byte]`.
4. A `NULL` page or a `0x0000` entry for the second byte means the sequence is invalid or unmapped.
5. A nonzero `wchar_t` entry is returned as the Unicode code point.

Reverse conversion follows the opposite shape:

1. Later code derives a Unicode high-byte page from the input `wchar_t`.
2. It selects the matching `u2c_*` reverse table through a registry defined after this chunk.
3. It indexes two bytes at `2 * low_byte`.
4. A nonzero pair is emitted as the CP950 sequence; a zero pair indicates no representable CP950 character.

## State and Persistence Behavior

All data in this chunk is `static const`, so it is read-only module text/data once loaded and has no persistence side effects. It maintains no locks, counters, heap allocations, caches, or mutable conversion state. The only persistent behavior it influences is encoded filename/string representation when a filesystem mounts with this NLS table: names are converted consistently according to these fixed lookup tables.

The `0x0000` sentinel values are state-like in the sense that they encode absence of a mapping. They are critical for rejecting invalid byte sequences rather than silently translating them to NUL.

## Dependencies and Integration Points

The primary integration point is the Linux NLS subsystem declared in `<linux/nls.h>`. Later in this file, the static tables are wired into an `nls_table` with `.charset = "cp950"` and conversion callbacks, then registered by module init/exit functions. Filesystems that request CP950/Big5 NLS support, including FAT-like or network/file-sharing paths that depend on Linux NLS tables, use those callbacks rather than accessing these arrays directly.

Within this file:

- `page_charset2uni` is the forward page registry used by `char2uni()`.
- The `u2c_*` arrays are reverse-page tables used through `page_uni2charset[256]`, defined after this chunk.
- Case-folding tables and module metadata are outside the chunk, so lower/upper conversion and registration behavior must be reconciled with later chunks.

The source path is under `sources/distributed-fs/ceph-client/fs/nls`, but this file itself is a generic Linux NLS module copied into the Ceph-client source tree. It does not call Ceph APIs directly.

## Risks

- Table corruption is the dominant risk. A single wrong literal changes filename/string conversion for one CP950 byte sequence or Unicode scalar and can create round-trip mismatches.
- Forward and reverse tables must remain consistent. If `c2u_*` maps a byte pair to a Unicode value but the matching `u2c_*` entry is missing or different, conversions become lossy or asymmetric.
- `0x0000` has dual meaning as the unmapped sentinel and Unicode NUL. The later conversion code must ensure only valid ASCII NUL handling can produce U+0000; double-byte table zeroes should be treated as invalid mappings.
- Page selector gaps are intentional. Accidentally filling `page_charset2uni` entries for unsupported lead bytes, or removing valid pages, would change which byte sequences are accepted.
- The chunk boundary splits `u2c_53`; any per-file report must merge this with the next chunk before claiming full reverse coverage for Unicode page `0x53`.
- Generated code is difficult to review manually. Edits should come from an authoritative generator or upstream table update, not ad hoc table changes.
- CP950/Big5 has vendor-specific and compatibility mappings. Replacing this data with a different Big5 variant can break interoperability for filenames created on systems expecting Microsoft CP950 behavior.

## Test and Validation Signals

Useful validation should focus on table correctness and round-trip behavior:

- Build the NLS module with `CONFIG_NLS_CODEPAGE_950` enabled and ensure no initializer size warnings or const/type warnings appear.
- Test representative forward mappings from symbol pages, Bopomofo/fullwidth pages, common CJK pages, and box-drawing/private compatibility entries near `0xF9`.
- Test invalid lead bytes and known unmapped trail-byte slots, expecting conversion failure rather than U+0000 output.
- Round-trip byte pairs from each populated `c2u_*` page through Unicode and back to CP950 where a reverse mapping exists.
- Verify Unicode-to-CP950 for pages covered in this chunk: `0x02`, `0x03`, `0x20`-`0x23`, `0x25`, `0x26`, `0x30`-`0x33`, and CJK pages `0x4E`-`0x53` up to the assigned boundary.
- Include boundary tests around page selector gaps: valid `0xC6`, invalid/NULL `0xC7` and `0xC8`, valid `0xC9`, and final valid `0xF9`.
- Mount or conversion-level tests should include filenames containing fullwidth ASCII, punctuation, Traditional Chinese common characters, and unmapped characters to confirm expected encode/decode behavior.

## Cross-Chunk Notes

The actual `uni2char()`/`char2uni()` functions, `page_uni2charset`, case conversion tables, `struct nls_table`, module init/exit, and metadata occur after line 4046. This chunk should be merged with those later sections before drawing conclusions about error returns, bounds checks, ASCII handling, case folding, and module registration.

The assigned range ends inside the `u2c_53` initializer. Treat this document as table-data coverage for the first half of reverse CJK mappings, not as complete analysis of the CP950 module.
