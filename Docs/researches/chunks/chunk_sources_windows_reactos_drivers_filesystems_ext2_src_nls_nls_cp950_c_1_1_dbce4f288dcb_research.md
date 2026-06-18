# Chunk Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp950.c lines 1-3890

## Scope

This chunk covers the opening 1-3890 lines of ReactOS ext2's Linux-style NLS module for CP950/Big5 filename character conversion. The file is generated table code originally identified as `linux/fs/nls_cp950.c`; this chunk contains module includes, all byte-to-Unicode CP950 lead-byte pages, the byte-to-Unicode page index, and the beginning of Unicode-to-CP950 reverse pages. The executable converter functions and module registration are outside this chunk, but adjacent context shows these tables are consumed by `char2uni()`, `uni2char()`, and the `nls_table` registration later in the same file.

## APIs And Entry Points

No callable API is defined inside this chunk. The chunk defines private static data for the later Linux NLS callbacks:

- `static wchar_t c2u_XX[256]` tables map a CP950/Big5 two-byte character with first byte `0xXX` and second byte used as an array index to a Unicode `wchar_t`.
- `static wchar_t *page_charset2uni[256]` maps each possible first byte to the corresponding `c2u_XX` table or `NULL`.
- `static unsigned char u2c_XX[512]` tables map Unicode pages to encoded CP950 bytes, storing two bytes per low-byte Unicode index.

Adjacent context at lines 9401-9461 shows the table API contract:

- `char2uni(rawstring, boundlen, uni)` reads `page_charset2uni[ch]`, indexes by `cl`, rejects `0x0000`, and otherwise falls back to one-byte ASCII-style output when no lead-byte table exists.
- `uni2char(uni, out, boundlen)` reads `page_uni2charset[ch]`, indexes `cl * 2`, rejects an all-zero two-byte pair, and otherwise falls back to one-byte values for Unicode page zero.

## Data Definitions

The file includes Linux kernel/NLS headers at lines 10-14: `linux/module.h`, `linux/kernel.h`, `linux/string.h`, `linux/nls.h`, and `linux/errno.h`.

The forward CP950-to-Unicode tables span lines 16-3129:

- Defined lead-byte pages: `A1` through `C6`, `C9` through `F9`.
- Omitted lead-byte pages visible in this chunk: `C7`, `C8`, and `FA` through `FF` are left unmapped by `page_charset2uni`.
- Every full forward page is a 256-entry `wchar_t` array. Most pages reserve non-trail-byte slots with `0x0000`.
- `c2u_C6` is a shorter initialized array than surrounding pages; because it has explicit `[256]` size, remaining entries are implicitly zero.

The lead-byte dispatch table `page_charset2uni[256]` spans lines 3131-3164 and maps `0xA1-0xC6`, `0xC9-0xF9` to table pointers, with `0xC7`, `0xC8`, and `0xFA-0xFF` as `NULL`.

The reverse Unicode-to-CP950 tables begin at line 3166 and continue past the chunk boundary. This chunk includes `u2c_02`, `u2c_03`, `u2c_20`, `u2c_21`, `u2c_22`, `u2c_23`, `u2c_25`, `u2c_26`, `u2c_30`, `u2c_31`, `u2c_32`, `u2c_33`, `u2c_4E`, `u2c_4F`, `u2c_50`, and the start of `u2c_51`. The chunk ends in the middle of `u2c_51`.

## Control Flow

There is no runtime branch or loop in this chunk. Control flow is encoded as data-driven dispatch for later callbacks:

1. CP950-to-Unicode decoding reads first byte `ch`.
2. `page_charset2uni[ch]` selects a page table only for recognized two-byte lead bytes.
3. The second byte `cl` indexes the selected page.
4. A zero result marks an invalid byte pair.
5. If no page exists for `ch`, adjacent `char2uni()` treats the byte as a single-byte character.

The reverse direction uses Unicode high byte to select `page_uni2charset[ch]`, then low byte to index a two-byte pair in `u2c_XX`.

## State And Mutability

All data in this chunk is file-scope `static` storage. None is declared `const`, even though the tables are intended to be immutable after module load. Later conversion callbacks read these arrays but do not modify them.

## Dependencies

This chunk depends on the Linux NLS/module compatibility environment used by the ReactOS ext2 driver:

- `wchar_t` and `NULL`
- `struct nls_table`, `register_nls()`, `unregister_nls()`, `THIS_MODULE`, `module_init()`
- errno values such as `-EINVAL` and `-ENAMETOOLONG`

The data is generated from Microsoft CP950 Unicode mapping data according to the file header.

## Risks And Edge Cases

- Invalid two-byte sequences are represented by `0x0000` in forward tables and `0x00, 0x00` in reverse tables.
- Unicode NUL is not encodable through the two-byte path; adjacent `uni2char()` also requires page-zero `cl` to be nonzero.
- Adjacent `char2uni()` returns a single-byte character whenever `page_charset2uni[ch]` is `NULL`, which may be permissive for malformed CP950 byte streams.
- Adjacent `char2uni()` treats `boundlen == 1` as a one-byte character, so a dangling CP950 lead byte decodes as that byte.
- Tables are writable static data because they are not `const`.
- The chunk boundary interrupts `u2c_51`; reverse-map coverage must be continued in later chunks.

## Cross-Chunk References

- Later chunk completes `u2c_51`, defines the rest of the `u2c_XX` reverse tables, `page_uni2charset[256]`, `charset2lower[256]`, and `charset2upper[256]`.
- Later chunk defines `uni2char()` and `char2uni()`, the actual NLS callbacks consuming these tables.
- Later chunk defines the `nls_table` for charset `"cp950"` and alias `"big5"`, plus module init/exit registration.