# Research: sources/distributed-fs/ceph-client/fs/nls/nls_cp950.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-005719`: lines 1-4046, `Docs/researches/chunks/subset-b-005719_research.md`
- `subset-b-005720`: lines 4047-8283, `Docs/researches/chunks/subset-b-005720_research.md`
- `subset-b-005721`: lines 8284-9483, `Docs/researches/chunks/subset-b-005721_research.md`

## Chunk Research

### subset-b-005719: lines 1-4046

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

### subset-b-005720: lines 4047-8283

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

### subset-b-005721: lines 8284-9483

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
