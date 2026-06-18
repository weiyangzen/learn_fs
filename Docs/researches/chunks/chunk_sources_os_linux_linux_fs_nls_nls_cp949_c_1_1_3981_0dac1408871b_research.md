# Chunk Research: sources/os/linux/linux/fs/nls/nls_cp949.c lines 1-3981

## Scope

This chunk is the opening data segment of the Linux NLS CP949/EUC-KR charset module. It contains the file banner, kernel includes, and the first byte-to-Unicode translation pages. It does not contain the executable conversion functions or module registration code; those appear later in the file.

## APIs and Public Surface

- Includes kernel module/NLS dependencies: `<linux/module.h>`, `<linux/kernel.h>`, `<linux/string.h>`, `<linux/nls.h>`, and `<linux/errno.h>` at lines 10-14.
- Defines only `static const` data, so nothing in this chunk is exported directly.
- The arrays in this chunk are private implementation data for later NLS callbacks, especially the later `char2uni()` path that indexes `page_charset2uni[first_byte][second_byte]`.

## Data Defined

- Lines 16-3966 define complete `static const wchar_t c2u_*[256]` pages for CP949 lead bytes: `c2u_81` through `c2u_C8`, then `c2u_CA` through `c2u_F0`.
- `c2u_C9` is deliberately absent in this range. Later `page_charset2uni` context maps the C9 lead-byte slot to `NULL`, so C9 is treated as an unmapped lead page rather than a missing symbol.
- Lines 3968-3981 begin `c2u_F1[256]` but stop mid-initializer at the `0x60-0x67` row. The table continues in the next chunk.
- Most early pages use 256 explicit entries, where `0x0000` marks unmapped byte positions. Several compatibility/symbol pages have shorter initializers; C zero-initialization fills the trailing entries.
- The chunk contains 112 table declarations total: 111 complete tables plus the partial `c2u_F1`.

## Table Semantics

- Each `c2u_XX` table maps a CP949 two-byte sequence whose first byte is `0xXX`; the second byte is used as the direct 0-255 array index.
- `0x0000` is the invalid/unmapped sentinel, not a valid translation result for multibyte CP949 entries.
- The first groups (`0x81` onward) map mostly Hangul syllables in the Unicode `0xAC00` range and beyond.
- The `0xA1`-`0xAC` region includes symbols, punctuation, compatibility jamo, Greek/Cyrillic, kana, and enclosed/alphanumeric symbols alongside Hangul-extension entries.
- The `0xCA`-`0xF0` pages contain mostly Hanja/CJK compatibility mappings, including private/compatibility-style Unicode values such as `0xF9xx`.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is data-driven: later `char2uni()` reads a first byte, fetches the matching page pointer from `page_charset2uni`, indexes by the second byte, and rejects `0x0000`. Later ASCII/single-byte fallback behavior is outside this chunk.

## State and Dependencies

All tables are `static const`, file-local, immutable module-lifetime data. There is no locking, allocation, reference counting, or mutable global state in this chunk.

The data depends on Linux NLS conventions from `<linux/nls.h>`, C static array zero-fill semantics, and later file-local pointer tables that make these pages reachable from conversion callbacks.

## Risks and Cross-Chunk References

The main correctness risk is table integrity: a shifted, missing, or mistyped value changes filename transcoding behavior for that CP949 byte pair. Since `0x0000` drives invalid-character handling, accidental zeros can reject valid names, while accidental nonzero values can admit invalid byte sequences.

`c2u_F1` begins here and continues after line 3981. Later chunks define `c2u_F2` through `c2u_FD`, `page_charset2uni`, Unicode-to-charset tables, case-conversion tables, `uni2char()`, `char2uni()`, `struct nls_table`, and module init/exit.