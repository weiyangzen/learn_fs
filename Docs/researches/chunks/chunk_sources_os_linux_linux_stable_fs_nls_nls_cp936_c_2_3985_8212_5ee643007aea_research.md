# Chunk Research: sources/os/linux/linux-stable/fs/nls/nls_cp936.c lines 3985-8212

## Scope

This chunk is the middle generated data section of the Linux NLS CP936/GB2312 conversion module. It completes the byte-sequence-to-Unicode table that began in the previous chunk, defines the forward dispatch table used by `char2uni()`, and then begins the Unicode-to-CP936 reverse mapping table corpus used by `uni2char()`.

There are no function bodies in this line range. Runtime behavior is indirect: later conversion callbacks index the static tables defined or referenced here.

## APIs And Dependencies

- No callable API is defined in this chunk.
- `page_charset2uni[256]` at lines 4389-4422 is the key internal dispatch structure for later `char2uni()`. It maps CP936 lead-byte values `0x81` through `0xFE` to `c2u_XX[256]` arrays and leaves unsupported lead bytes as `NULL`.
- `u2c_XX[512]` tables starting at line 4424 are reverse lookup pages for later `uni2char()`. Each Unicode page table stores two output bytes per low-byte index, so lookup uses `cl * 2` and `cl * 2 + 1` in the later callback.
- The table definitions depend on `wchar_t`, `unsigned char`, and `NULL` declarations from earlier includes in the same translation unit. Later chunks depend on these symbols when constructing `page_uni2charset[256]` and the Linux `struct nls_table`.

## Data Tables

- Lines 3985-4008 finish `c2u_F1[256]`, whose declaration and first entries are in chunk 1.
- Lines 4010-4387 define `c2u_F2[256]` through `c2u_FE[256]`, completing the forward CP936 lead-byte tables.
- Lines 4389-4422 define `page_charset2uni[256]`.
- Lines 4424-8212 define full `u2c_00` through selected Unicode pages up to `u2c_79`, then start `u2c_7A[512]`.
- The range contains 61 `u2c_XX[512]` declarations and 13 `c2u_XX[256]` declarations, plus one forward dispatch table.

## Control Flow And State

This chunk has no local control flow, branching, allocation, locking, I/O, or mutable state. Every object is `static const`, so the chunk contributes read-only translation-unit-local lookup data.

Effective control flow appears only in consumers outside this chunk: later `char2uni()` reads `page_charset2uni[ch]`, while later `uni2char()` reads `page_uni2charset[ch]` and the `u2c_XX` tables defined here.

## Risks And Edge Cases

- `0x0000` in `c2u_*` and `0x00, 0x00` in `u2c_*` are unmapped sentinels; accidental edits can silently corrupt conversion behavior.
- Dispatch alignment is fragile: `page_charset2uni[0xF1]` must point to `c2u_F1`, `0xFE` to `c2u_FE`, and `0xFF` must remain `NULL`.
- Chunk boundaries split active tables: this chunk starts mid-`c2u_F1` and ends mid-`u2c_7A`.
- Reverse tables encode two bytes per Unicode code point, so byte order must be preserved exactly.
- Sparse pages contain many zero pairs by design.

## Cross-Chunk References

- Chunk 1 declares `c2u_81` through `c2u_F0` and begins `c2u_F1`; this chunk completes `c2u_F1` and adds `c2u_F2` through `c2u_FE`.
- This chunk’s `page_charset2uni` references all `c2u_81` through `c2u_FE` tables, including arrays declared in chunk 1.
- Chunk 3 continues `u2c_7A`, defines remaining reverse tables, builds `page_uni2charset[256]`, and defines the executable NLS callbacks and module metadata.