# sources/distributed-fs/ceph-client/fs/nls/nls_cp950.c lines 8284-9483

## Scope

This chunk covers the final section of the Linux NLS CP950/Big5 translation module. It starts at the tail of the previous Unicode-to-charset table entry, then defines the remaining `u2c_*` Unicode page tables from `u2c_93` through `u2c_FF`, the `page_uni2charset` dispatcher, ASCII-only upper/lower case tables, the two conversion entry points, the exported `struct nls_table`, and the module registration metadata.

The source file is generated table code for Microsoft's CP950 charset. The visible range is mostly static lookup data; the executable logic is concentrated in `uni2char`, `char2uni`, `init_nls_cp950`, and `exit_nls_cp950`.

## Purpose

The module provides bidirectional conversion between Unicode `wchar_t` code points and CP950/Big5 byte sequences for kernel filesystem name handling. It is registered as charset `"cp950"` with alias `"big5"`, so filesystem code can request this NLS table by either name.

Within this chunk, the main purpose is Unicode-to-CP950 conversion for higher Unicode pages:

- `u2c_93` through `u2c_9F` cover Unicode pages `0x9300` through `0x9FFF`, mostly CJK ideograph ranges.
- `u2c_DC` is a sparse page with no visible mappings in this chunk.
- `u2c_F9` and `u2c_FA` cover compatibility ideograph and special compatibility ranges.
- `u2c_FE` and `u2c_FF` cover presentation/fullwidth forms and related punctuation/numeric/Latin symbols.
- `page_uni2charset` connects Unicode high-byte page indexes to the matching `u2c_*` arrays.

Each `u2c_*` table has 512 bytes, two bytes per low-byte Unicode value. For a Unicode value `0xHHLL`, `uni2char` selects `page_uni2charset[HH]` and reads bytes at `LL * 2` and `LL * 2 + 1`. A table pair of `0x00, 0x00` means "not representable in CP950".

## Important APIs, Types, and Data

The data tables are all `static const`, so they become read-only module data and are not mutated at runtime.

- `static const unsigned char u2c_93[512]` through `u2c_FF[512]`: Unicode-page conversion tables. Most arrays are dense enough to include many valid two-byte CP950 sequences, but long zero runs intentionally mark unmapped Unicode code points.
- `static const unsigned char *const page_uni2charset[256]`: top-level Unicode-to-charset page directory. `NULL` entries mean no CP950 mappings exist for that Unicode high byte, except ASCII is handled separately by `uni2char`.
- `static const unsigned char charset2lower[256]` and `charset2upper[256]`: byte-wise case conversion tables. They only fold ASCII letters; bytes `0x80` through `0xFF` map to themselves.
- `static int uni2char(const wchar_t uni, unsigned char *out, int boundlen)`: converts one Unicode code point into one or two CP950 bytes.
- `static int char2uni(const unsigned char *rawstring, int boundlen, wchar_t *uni)`: converts one CP950 byte sequence into one Unicode code point.
- `static struct nls_table table`: advertises the charset name, alias, conversion callbacks, and casefold tables to the kernel NLS core.
- `init_nls_cp950` / `exit_nls_cp950`: register and unregister the NLS table with `register_nls` and `unregister_nls`.
- Module metadata: `module_init`, `module_exit`, `MODULE_DESCRIPTION`, `MODULE_LICENSE`, and `MODULE_ALIAS_NLS(big5)`.

The reverse conversion tables used by `char2uni` are not defined in this chunk, but they are referenced through `page_charset2uni`, which is defined earlier in the same source file.

## Control Flow

`uni2char` is table-driven:

1. It rejects `boundlen <= 0` with `-ENAMETOOLONG`.
2. It splits `uni` into low byte `cl` and high byte `ch`.
3. It looks up `page_uni2charset[ch]`.
4. If a page table exists, it requires room for two output bytes. It copies the pair indexed by `cl`; if both bytes are zero, it returns `-EINVAL`.
5. If no page table exists but `ch == 0` and `cl != 0`, it emits the single ASCII byte.
6. Otherwise it returns `-EINVAL`.

`char2uni` is also table-driven:

1. It rejects `boundlen <= 0` with `-ENAMETOOLONG`.
2. If only one input byte is available, it treats that byte as a single-byte Unicode value and returns `1`.
3. With at least two input bytes, it uses the first byte as the CP950 lead-byte page and the second byte as the index into `page_charset2uni[ch]`.
4. If a reverse page exists and the second byte is nonzero, it returns the mapped Unicode value unless that value is `0x0000`, which signals `-EINVAL`.
5. Otherwise it falls back to treating the first byte as a one-byte character and consumes only one byte.

Initialization and teardown are simple NLS-core registration calls. There is no allocation, locking, reference counting, or dynamic table construction in this chunk.

## State and Persistence Behavior

The module keeps no mutable runtime state. All conversion behavior is encoded in compile-time static tables.

Observable persistent behavior comes from the installed NLS table registration: once `init_nls_cp950` succeeds, kernel clients can resolve `"cp950"` and `"big5"` through the NLS subsystem until `exit_nls_cp950` unregisters the table. Case conversion state is deterministic and byte-local: ASCII letters are folded, while multibyte CP950 bytes are left unchanged by the casefold tables.

The conversion tables intentionally encode absence as zero. This means `0x0000` cannot be used as a successful reverse-mapping value in `char2uni`, and `0x00,0x00` cannot be used as a successful forward-mapping pair in `uni2char`.

## Dependencies and Integration Points

This chunk depends on kernel NLS and module infrastructure:

- `<linux/nls.h>` for `struct nls_table`, `register_nls`, and `unregister_nls`.
- `<linux/errno.h>` for `-EINVAL` and `-ENAMETOOLONG`.
- `<linux/module.h>` for module lifecycle and metadata macros.
- Earlier `c2u_*` and `page_charset2uni` tables in the same file for CP950-to-Unicode conversion.

The integration surface is the kernel NLS API. Filesystem code that needs Big5/CP950 filename conversion obtains this table through the NLS subsystem and invokes `.uni2char`, `.char2uni`, `.charset2lower`, and `.charset2upper`. In this repository layout the file sits under the Ceph client source tree, but the implementation is the generic Linux `fs/nls` CP950 charset module pattern rather than Ceph-specific protocol logic.

## Risks

- Table accuracy is the primary risk. A single wrong byte pair maps a Unicode character to the wrong CP950 sequence or makes a valid character unrepresentable.
- Zero pairs are semantic sentinels. Accidentally inserting `0x00, 0x00` for a valid mapping or a nonzero pair for an invalid mapping changes error behavior.
- `page_uni2charset` must match the declared `u2c_*` tables exactly. A wrong pointer or missing page makes an entire Unicode page convert incorrectly.
- Bounds behavior is caller-visible. `uni2char` requires two bytes for any table-backed mapping before it knows whether the entry is valid, so callers must pass adequate output space for non-ASCII code points.
- `char2uni` accepts a single available input byte as a one-byte character even if the byte might be a CP950 lead byte. Stream parsers must pass correct `boundlen` and handle partial multibyte sequences carefully.
- ASCII NUL is not accepted by `uni2char` through the ASCII fallback because the fallback requires `cl` to be nonzero. Callers that need NUL handling must not assume ordinary character conversion semantics for terminators.
- Casefolding is ASCII-only. That is expected for this generated NLS table, but consumers must not assume Traditional Chinese or fullwidth Latin characters are case-normalized.

## Test and Validation Signals

Useful validation signals for this chunk are conversion-focused:

- Build the CP950 NLS module or kernel configuration that includes it; this catches table declaration and registration breakage.
- Round-trip known CP950/Big5 samples through `char2uni` and `uni2char`, especially Unicode pages represented in this chunk: `0x93xx` through `0x9Fxx`, `0xF9xx`, `0xFAxx`, `0xFExx`, and `0xFFxx`.
- Verify unmapped entries return `-EINVAL` rather than producing `0x00,0x00`.
- Verify insufficient output length in `uni2char` returns `-ENAMETOOLONG` for two-byte mappings and that ASCII nonzero characters return one byte.
- Verify partial input behavior in `char2uni`: `boundlen == 1` consumes one byte, while valid two-byte CP950 sequences consume two bytes.
- Check alias resolution by loading or requesting NLS `"big5"` and confirming it resolves to the CP950 table advertised by `MODULE_ALIAS_NLS(big5)`.
- Casefold tests should confirm only ASCII `A-Z` and `a-z` differ between `charset2upper` and `charset2lower`; all high-bit CP950 bytes should remain identity-mapped.

## Cross-Chunk Notes

This chunk begins in the final entry of `u2c_92`, whose definition starts in the previous chunk. It also relies on reverse `c2u_*` tables and `page_charset2uni` defined earlier in the file. The later merge/reconciliation lane should combine those adjacent chunks with this one to describe the whole CP950 module as one source-file report.
