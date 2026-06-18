# Chunk Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp950.c lines 7951-9487

## Scope

This chunk covers the tail of the generated ReactOS ext2 NLS table for CP950/Big5. It begins one line after the declaration of `u2c_8E`, finishes the remaining Unicode-to-charset lookup pages, builds the `page_uni2charset` dispatch table, defines byte-case folding tables, implements the `uni2char` and `char2uni` conversion callbacks, and registers the `cp950` NLS module aliasing `big5`.

The opening line range is inside `u2c_8E`; the table declaration starts at line 7950, just before this chunk. Earlier chunks define the includes, the reverse `c2u_*` charset-to-Unicode pages, `page_charset2uni`, and Unicode-to-charset pages up through `u2c_8D`.

## APIs And Entry Points

- `uni2char(const wchar_t uni, unsigned char *out, int boundlen)` converts one Unicode code point to CP950/Big5 bytes for the NLS table.
- `char2uni(const unsigned char *rawstring, int boundlen, wchar_t *uni)` converts one CP950/Big5 byte sequence to a Unicode `wchar_t`.
- `init_nls_cp950()` registers the local `struct nls_table table` with `register_nls()`.
- `exit_nls_cp950()` unregisters the same table with `unregister_nls()`.
- `module_init(init_nls_cp950)`, `module_exit(exit_nls_cp950)`, `MODULE_LICENSE("Dual BSD/GPL")`, and `MODULE_ALIAS_NLS(big5)` expose this file as a loadable NLS module.

## Data Tables

The first major block is generated static mapping data:

- `u2c_8E` through `u2c_9F` map Unicode pages `0x8E00` through `0x9FFF` to two-byte CP950/Big5 sequences, using `{0x00, 0x00}` as unmapped sentinels.
- `u2c_DC` is a sparse page with only zero entries in this chunk.
- `u2c_F9` and `u2c_FA` cover compatibility/private mapping ranges used by CP950.
- `u2c_FE` and `u2c_FF` cover fullwidth/symbol ranges, including punctuation, fullwidth digits/letters, and related Big5 symbol-zone mappings.
- `page_uni2charset[256]` maps the high byte of a Unicode value to the corresponding `u2c_*` page pointer. NULL high-byte entries are treated as unsupported pages, except low ASCII handled separately by `uni2char()`.
- `charset2lower[256]` and `charset2upper[256]` perform single-byte ASCII-only case folding: `A-Z` lower to `a-z`, `a-z` upper to `A-Z`, and all non-ASCII bytes remain unchanged.

The tables are mutable only because they are declared as `static unsigned char` rather than `static const`; this chunk does not write to them.

## Control Flow

`uni2char()` first rejects a non-positive output bound with `-ENAMETOOLONG`. It splits `uni` into low byte `cl` and high byte `ch`, indexes `page_uni2charset[ch]`, and if a page exists requires at least two output bytes. It copies the two bytes at `cl * 2` and `cl * 2 + 1`, rejects the `{0,0}` sentinel with `-EINVAL`, and returns `2`. If no page exists but `ch == 0 && cl` is true, it emits the low byte directly as one-byte ASCII and returns `1`. All other Unicode values return `-EINVAL`.

`char2uni()` first rejects a non-positive input bound with `-ENAMETOOLONG`. If only one input byte is available, it treats that byte as a complete single-byte character, stores it directly in `*uni`, and returns `1`. With at least two bytes available, it reads lead byte `ch` and trail byte `cl`, looks up `page_charset2uni[ch]` from the earlier chunk, and if a page exists and `cl` is nonzero, returns `charset2uni[cl]` unless that entry is `0x0000`, in which case it returns `-EINVAL`. If there is no page for the lead byte or the second byte is zero, it falls back to treating the lead byte as a one-byte character and returns `1`.

The module registration flow is minimal: the static `table` binds charset name `cp950`, alias `big5`, the two conversion callbacks, the case-fold tables, and `THIS_MODULE`; init registers it and exit unregisters it.

## State And Dependencies

The important local state is table-driven and process-global: all `u2c_*` arrays, `page_uni2charset`, `charset2lower`, `charset2upper`, and the final `struct nls_table table`.

This chunk depends on earlier file definitions for `page_charset2uni` and the `c2u_*` charset-to-Unicode arrays used by `char2uni()`. It also depends on kernel/ReactOS NLS infrastructure types and symbols visible from the file header, including `wchar_t`, `struct nls_table`, `THIS_MODULE`, `register_nls()`, `unregister_nls()`, `module_init`, `module_exit`, `MODULE_LICENSE`, `MODULE_ALIAS_NLS`, and errno constants `ENAMETOOLONG` and `EINVAL`.

There is no dynamic allocation, locking, filesystem I/O, or mutable conversion state in this chunk. Conversion behavior is deterministic for one code point or one byte sequence at a time.

## Risks And Edge Cases

- The chunk starts inside `u2c_8E`; its declaration is just outside the range at line 7950, so any table-boundary audit must include that adjacent line.
- Several `u2c_*` arrays are declared as `[512]` but are sparsely initialized or shorter than a full 512-byte literal block. C zero-initialization fills the remainder; conversion correctness relies on `{0,0}` continuing to mean unmapped.
- `char2uni()` treats any single available byte as a valid single-byte Unicode value. For truncated double-byte CP950 input, the callback cannot distinguish truncation from intended single-byte data and returns success with the lead byte.
- `char2uni()` also falls back to one-byte output when the second byte is `0x00` or when no lead-byte page exists, rather than returning `-EINVAL`.
- `uni2char()` only allows direct one-byte output for `ch == 0 && cl`, so Unicode NUL (`U+0000`) is rejected rather than encoded as byte zero.
- Case folding is ASCII-only. Multibyte CP950 letters and any locale-specific mappings are identity mappings in `charset2lower`/`charset2upper`.
- The static lookup tables are not `const`; accidental writes elsewhere in this compilation unit would corrupt global conversion behavior, although this file does not write them.

## Cross-Chunk References

- Earlier chunks define the file header/includes, licensing preamble, and `page_charset2uni`; `char2uni()` cannot be understood independently of those tables.
- Earlier Unicode-to-charset pages `u2c_02` through `u2c_8D` are referenced by `page_uni2charset` in this chunk, so this chunk completes the dispatch table for data declared across the whole file.
- The final `struct nls_table table` is the integration point for the entire file: all generated tables from previous chunks feed the two callbacks registered here.

## Summary

This chunk is the executable tail of an otherwise generated CP950/Big5 NLS mapping file. It finishes the Unicode-to-charset data, wires the high-byte page dispatch table, provides ASCII-only case conversion, implements bounded one-character encode/decode callbacks, and registers the mapping with the ReactOS/Linux-style NLS module system.