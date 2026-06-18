# Chunk Research: sources/os/linux/linux-stable/fs/nls/nls_cp949.c lines 3982-8200

## Scope

This chunk is within subset A (`Docs/research_subset_a.md`) under `sources/os/linux/linux-stable`. I read the requested range completely. Adjacent context was used only to identify the containing declarations and the later converter callbacks that consume these tables.

The range is generated/static CP949/EUC-KR conversion data. It has no function bodies, branches, locks, allocation, or direct filesystem operations of its own.

## APIs And Symbols

All symbols in this chunk are file-local `static const` lookup tables backing the NLS module:

- Tail of `c2u_F1[256]`: the chunk begins inside this charset-to-Unicode page table at low-byte comments `0x68-0x6F` and continues through the close at line 4002.
- Complete charset-to-Unicode page tables `c2u_F2[256]` through `c2u_FD[256]`: these map CP949 lead bytes `0xF2` through `0xFD` plus trailing byte index to Unicode `wchar_t` values.
- Complete `page_charset2uni[256]`: pointer dispatch table that maps the first CP949 byte to a `c2u_*` page. It references `c2u_81` through `c2u_FD`, leaves unsupported lead-byte slots as `NULL`, and notably has `NULL` for `0xC9`, `0xFE`, and `0xFF`.
- Complete Unicode-to-charset page tables from `u2c_01[512]` through `u2c_79[512]`, with gaps matching declared Unicode high-byte pages: `01`, `02`, `03`, `04`, `11`, `20`-`26`, `30`-`33`, and `4E`-`79`.
- Start of `u2c_7A[512]`: the chunk includes the declaration and entries through Unicode low-byte comment `0x10-0x13`; the table continues in the next chunk.

There are no exported symbols here. The public module surface is created later by `struct nls_table table`, whose `.uni2char` and `.char2uni` callbacks consume these static arrays.

## Data Model And State

The data is immutable conversion state:

- `c2u_*` entries are indexed by the second CP949 byte and store Unicode code points. `0x0000` is the invalid/unmapped sentinel.
- `page_charset2uni[first_byte]` chooses the correct `c2u_*` table for two-byte decoding; `NULL` means that byte is not a double-byte lead in this table.
- `u2c_*` entries are two output bytes per Unicode low-byte index, so each 512-byte table covers one Unicode high-byte page. A pair of `0x00, 0x00` is the unmapped sentinel.
- The tables include compatibility/private mapping values visible in this range, such as Unicode compatibility ideograph/codepoint range entries around `F9xx` and `FAxx`, which must remain synchronized with the reverse `u2c_*` data.

There is no mutable global state, reference counting, initialization side effect, or teardown behavior in the chunk.

## Control Flow

There is no local executable control flow. Effective runtime flow, from adjacent context, is table-driven:

- Decode path: `char2uni()` reads one or two input bytes, uses `page_charset2uni[ch]`, then returns `charset2uni[cl]` when the page exists and `cl != 0`; `0x0000` returns `-EINVAL`. If no page exists, it treats the first byte as a one-byte character.
- Encode path: `uni2char()` splits a Unicode `wchar_t` into high and low bytes, selects `page_uni2charset[ch]`, then returns the two bytes at `cl * 2`; `0x00,0x00` returns `-EINVAL`. If the Unicode high byte is zero and the low byte is nonzero, it emits one byte.
- This chunk supplies many of the pages selected by those two dispatch arrays; it does not itself perform bounds checks or error handling.

## Dependencies

Compile-time dependencies come from the wider file:

- Kernel NLS types and API definitions, including `wchar_t`, `struct nls_table`, `register_nls()`, and `unregister_nls()`.
- The later `page_uni2charset[256]` table depends on the `u2c_*` symbols defined here.
- The later `char2uni()` and `uni2char()` callbacks depend on the sentinel conventions and exact 256/512-entry sizing of these arrays.

No external libraries, filesystem internals, block-layer APIs, or VFS objects are used directly in this chunk.

## Risks And Invariants

- The chunk is high-risk to edit manually: a single literal change can silently corrupt filename transcoding for CP949/EUC-KR mounts.
- `0x0000` in `c2u_*` and `0x00,0x00` in `u2c_*` are semantic sentinels, not ordinary data.
- Table sizes and index formulas are coupled to callers: `c2u_*` must have 256 `wchar_t` entries; `u2c_*` must have 512 bytes because callers index `cl * 2` and `cl * 2 + 1`.
- The chunk begins and ends inside table symbols, so whole-symbol validation requires adjacent chunks.
- Round-trip correctness depends on consistency between the forward `c2u_*` tables and reverse `u2c_*` tables across the whole file, not only this line range.
- Invalid lead-byte behavior is determined by `page_charset2uni`: unsupported double-byte lead bytes fall back to single-byte decoding in `char2uni()`, while invalid mapped entries return `-EINVAL`.

## Cross-Chunk References

- Previous chunk: defines earlier `c2u_*` tables and the start of `c2u_F1`; this chunk starts inside `c2u_F1`.
- This chunk: completes the high CP949 forward mapping pages through `c2u_FD`, defines the forward dispatch table, defines many reverse Unicode pages, and starts `u2c_7A`.
- Next chunk: continues and closes `u2c_7A`, then defines the remaining reverse `u2c_*` pages.
- Final chunk/file tail: defines `page_uni2charset`, ASCII case tables, `uni2char()`, `char2uni()`, `struct nls_table table`, module init/exit, and module metadata.