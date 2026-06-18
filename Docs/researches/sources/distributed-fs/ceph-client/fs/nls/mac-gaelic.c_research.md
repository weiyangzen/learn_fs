# sources/distributed-fs/ceph-client/fs/nls/mac-gaelic.c

## Purpose
This generated NLS module registers the `macgaelic` Macintosh Gaelic codepage. It provides exact one-byte conversion for legacy Gaelic Mac filename encodings.

## Important APIs, Types, And Functions
`charset2uni[256]` maps each byte to Unicode, including Gaelic-specific Latin extended letters and symbols. Reverse lookup pages include `page00`, `page01`, `page02`, `page1e`, `page20`, `page21`, `page22`, and `page26`, selected by `page_uni2charset[256]`. `uni2char()`, `char2uni()`, and the `struct nls_table` named `macgaelic` implement the NLS interface.

## Control Flow
The module init function registers the table; exit unregisters it. At runtime, Unicode-to-byte conversion splits a `wchar_t` into page and offset, then emits one byte if an exact reverse mapping exists. Byte-to-Unicode conversion directly indexes `charset2uni`.

## State, Persistence, And Dependencies
The conversion tables are read-only generated data. Runtime state is limited to registration in the NLS core. The file depends on module infrastructure, `linux/nls.h`, and errno definitions.

## Integration Points
`CONFIG_NLS_MAC_GAELIC` and `mac-gaelic.o` connect the module to kernel builds. Filesystems request the table by `macgaelic` when decoding or encoding legacy Mac Gaelic filenames.

## Risks
Exact-only mappings reject decomposed Unicode and unrelated but visually similar characters. Gaelic-specific extended Latin coverage must stay synchronized with the Unicode source table. Case maps are placeholders, so locale-aware case folding is outside this module.

## Test Signals
Round-trip mapped bytes, test Gaelic extended letters in pages `0x01` and `0x1e`, validate symbol mappings such as Euro, check unmapped Unicode failure, and verify module registration under `macgaelic`.
