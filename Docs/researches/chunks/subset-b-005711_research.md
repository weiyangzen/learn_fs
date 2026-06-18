# sources/distributed-fs/ceph-client/fs/nls/nls_cp932.c lines 4153-7934

## Scope

This chunk covers the tail of the Linux kernel CP932 NLS translation module. It starts in the final rows of the `u2c_6B` Unicode-to-charset page and then contains the remaining Unicode-to-CP932 pages, the `page_uni2charset` dispatch table, ASCII-only case-folding tables, the `uni2char()` and `char2uni()` conversion callbacks, and the module registration boilerplate for the `"cp932"` charset with `"sjis"` as its alias.

The earlier chunk for the same source file defines the reverse CP932-to-Unicode pages (`c2u_*`), `page_charset2uni`, `u2c_00hi`, and the first Unicode-to-charset pages through most of `u2c_6B`. This report therefore focuses on the generated data and executable logic present in lines 4153-7934; the final per-file report should merge it with the earlier table coverage.

## Purpose

`nls_cp932.c` implements a kernel National Language Support table for Microsoft Code Page 932, a Shift-JIS variant used for Japanese filenames and filesystem metadata conversion. Filesystems that request this NLS table can translate between Linux Unicode `wchar_t` code points and on-disk CP932 byte sequences.

The chunk's main purpose is to finish the Unicode-to-CP932 lookup coverage and wire both conversion directions into `struct nls_table`. The static lookup pages encode the generated mapping from selected Unicode high-byte pages to one- or two-byte CP932 sequences. The conversion callbacks are the small runtime layer that validates buffer lengths, handles ASCII and half-width Katakana fast paths, indexes the generated pages, and reports kernel errno-style failures for unmappable or truncated input.

## Important APIs, Types, and Data

Important symbols in this chunk are:

- `u2c_6C` through `u2c_9F`, plus the final rows of `u2c_6B`: generated 512-byte lookup pages for Unicode high bytes `0x6B` through `0x9F`. Each Unicode low byte indexes two adjacent output bytes with `cl * 2` and `cl * 2 + 1`.
- `u2c_DC`, `u2c_F9`, `u2c_FA`, and `u2c_FF`: sparse special pages for compatibility/private-use/full-width mappings. `u2c_FF` includes full-width punctuation, full-width ASCII letters/digits, and half-width Katakana-related values.
- `page_uni2charset[256]`: a high-byte dispatch array that maps a Unicode page number to the corresponding `u2c_*` page pointer, or `NULL` when the page has no generated CP932 mappings in this table.
- `charset2lower[256]` and `charset2upper[256]`: byte-wise case-folding tables used by the NLS layer. They only fold ASCII A-Z/a-z and leave high CP932 bytes unchanged.
- `uni2char(const wchar_t uni, unsigned char *out, int boundlen)`: Unicode-to-CP932 callback installed in `struct nls_table`.
- `char2uni(const unsigned char *rawstring, int boundlen, wchar_t *uni)`: CP932-to-Unicode callback installed in `struct nls_table`.
- `table`: the `struct nls_table` instance with `.charset = "cp932"`, `.alias = "sjis"`, conversion callbacks, and case maps.
- `init_nls_cp932()` / `exit_nls_cp932()`: module lifecycle hooks that register and unregister the table with the kernel NLS registry.
- `MODULE_DESCRIPTION`, `MODULE_LICENSE`, and `MODULE_ALIAS_NLS(sjis)`: module metadata and aliasing for autoload/discovery.

The table format is intentionally simple: a missing Unicode mapping is encoded as output bytes `0x00, 0x00`, while a missing CP932-to-Unicode mapping in the earlier `c2u_*` tables is encoded as `0x0000`. Because `uni2char()` checks for a zero pair after lookup and `char2uni()` checks for `0x0000`, the data tables are both payload and validity bitmap.

## Control Flow

`uni2char()` begins by deriving `cl = uni & 0xFF` and `ch = (uni >> 8) & 0xFF`, so it only consults the low 16 bits of the `wchar_t` input. It first rejects zero or negative output capacity with `-ENAMETOOLONG`. It then handles Unicode `U+FF61` through `U+FF9F` as single-byte half-width Katakana by returning `cl + 0x40`, matching CP932 bytes `0xA1` through `0xDF`.

For most non-ASCII characters, `uni2char()` indexes `page_uni2charset[ch]`. When a page exists, the function requires `boundlen >= 2`, copies the two-byte mapping into `out[0]` and `out[1]`, rejects `0x00,0x00` as `-EINVAL`, and otherwise returns `2`. If no generated page exists and the Unicode high byte is zero, it handles `U+0000` through `U+007F` as one-byte ASCII and `U+00A0` and above through the earlier `u2c_00hi` table. Non-ASCII `U+0000` page mappings that are absent or zero pairs return `-EINVAL`.

`char2uni()` is the reverse runtime path. It first rejects `boundlen <= 0` with `-ENAMETOOLONG`. Bytes `0x00` through `0x7F` map directly to the same Unicode scalar and consume one byte. Bytes `0xA1` through `0xDF` map to `U+FF61` through `U+FF9F` by subtracting `0x40` and ORing with `0xFF00`, again consuming one byte. All other non-ASCII bytes require a second byte; if unavailable, the function returns `-ENAMETOOLONG`.

For two-byte candidates, `char2uni()` uses the first byte as a high-byte page index into `page_charset2uni`, which is defined earlier in the file, and the second byte as the offset into that 256-entry `wchar_t` page. If the page pointer is non-NULL and the second byte is nonzero, a nonzero Unicode result is accepted and the function returns `2`. Missing page pointers, zero second bytes, and zero table results return `-EINVAL`.

Module initialization is linear: `module_init(init_nls_cp932)` calls `register_nls(&table)` when the module is loaded or built-in init runs; `module_exit(exit_nls_cp932)` calls `unregister_nls(&table)` during unload. The conversion callbacks are only reachable after successful registration through NLS consumers.

## State and Persistence Behavior

This chunk has no mutable per-file or per-mount state. The generated mapping tables, dispatch tables, and case-folding arrays are `static const` and persist for the lifetime of the module image. They are read-only after load and safe for concurrent callers without locks.

The only global mutable effect is NLS registry membership. `init_nls_cp932()` registers `table` under the `"cp932"` charset name and `"sjis"` alias; `exit_nls_cp932()` unregisters the same table. Consumers that obtain the table through the NLS core use these callbacks without per-conversion allocation.

Output state is caller-provided. `uni2char()` writes one or two bytes into `out` only after sufficient capacity checks for the path being used. `char2uni()` writes one `wchar_t` result through `uni` only after a mapping candidate is found or for direct ASCII/half-width paths. Both callbacks signal problems through negative errno values instead of storing persistent error state.

## Dependencies and Integration Points

The module depends on kernel headers for module metadata, errno constants, and the NLS core: `linux/module.h`, `linux/kernel.h`, `linux/string.h`, `linux/nls.h`, and `linux/errno.h`.

The key external integration point is the Linux NLS subsystem. `struct nls_table` defines the ABI expected by filesystem and VFS charset conversion code: `uni2char`, `char2uni`, `charset2lower`, and `charset2upper`. Filesystems that mount with CP932/SJIS conversion can request this table and use it when translating filenames between Unicode-facing kernel paths and CP932-compatible on-disk encodings.

The conversion functions also depend on data defined outside this chunk:

- `page_charset2uni` and the `c2u_*` tables are used by `char2uni()`.
- `u2c_00hi` and `u2c_03` through `u2c_6B` are referenced by `uni2char()` through direct code or `page_uni2charset`.

Because `MODULE_ALIAS_NLS(sjis)` advertises the SJIS alias, module autoloading can satisfy users that request `"sjis"` even though the registered charset string is `"cp932"`.

## Risks

- Table integrity is the highest risk. A single generated byte pair in `u2c_*` or Unicode scalar in `c2u_*` can silently corrupt filename round trips or make valid names unmappable.
- The chunk starts inside `u2c_6B`, so any manual review or regeneration must preserve continuity with the earlier chunk. Dropping or duplicating entries around the line boundary would shift low-byte indexes and break every later entry in that page.
- `uni2char()` always requires a two-byte output buffer before checking whether a generated page entry is valid. That is correct for the table format but means callers must retry with enough capacity even when the ultimate result would be `-EINVAL`.
- `char2uni()` rejects two-byte sequences with a zero trail byte before lookup. That matches the CP932 table model here, but any attempted extension for unusual vendor bytes must preserve this validation intentionally.
- The case-folding tables fold only ASCII. That is expected for a byte-oriented filesystem NLS table, but callers must not assume full Unicode or Japanese-width case normalization.
- `wchar_t` values above `0xFFFF` are effectively truncated to low 16 bits by the `ch`/`cl` extraction. In Linux NLS tables this is conventional for legacy encodings, but it is a risk if callers expect supplementary-plane awareness.
- The data encodes many sparse extension mappings under high Unicode pages and CP932 vendor rows such as `ED`/`EE` byte ranges. Compatibility with Microsoft CP932 depends on preserving those extension values exactly.

## Test and Validation Signals

Useful validation should focus on table consistency, errno behavior, and NLS registration:

- Build the module or kernel configuration that includes `nls_cp932.c`; table-size or initializer mistakes should fail compilation.
- Load and unload the NLS module and confirm `register_nls()`/`unregister_nls()` succeed, including alias lookup through `"sjis"` where the test environment exposes NLS modules.
- Round-trip representative mappings: ASCII, half-width Katakana `U+FF61..U+FF9F`, full-width ASCII and punctuation from `u2c_FF`, common kanji in pages `u2c_6C` through `u2c_9F`, and vendor/private extension values in the `ED`/`EE` byte ranges.
- Exercise negative paths: zero output/input lengths should return `-ENAMETOOLONG`; one-byte output buffers for two-byte Unicode mappings should return `-ENAMETOOLONG`; unmapped Unicode entries that resolve to `0x00,0x00` should return `-EINVAL`; unknown two-byte lead/trail combinations should return `-EINVAL`.
- Compare generated mappings against a known CP932 reference table, especially around sparse pages `u2c_DC`, `u2c_F9`, `u2c_FA`, and `u2c_FF`.
- Filesystem-level tests should create, lookup, rename, and remove filenames containing ASCII, half-width Katakana, full-width Roman characters, common Japanese characters, and CP932 extension characters on a mount configured to use CP932/SJIS conversion.
