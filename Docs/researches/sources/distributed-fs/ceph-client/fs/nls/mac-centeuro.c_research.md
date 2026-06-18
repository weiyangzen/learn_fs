# sources/distributed-fs/ceph-client/fs/nls/mac-centeuro.c

## Purpose
This generated NLS module registers the `maccenteuro` Macintosh Central European codepage. It supports exact filename translation between the legacy single-byte Mac encoding and Unicode.

## Important APIs, Types, And Functions
The module defines `charset2uni[256]`, reverse lookup pages `page00`, `page01`, `page02`, `page20`, `page21`, `page22`, and `page25`, plus `page_uni2charset[256]`. Conversion callbacks `uni2char()` and `char2uni()` are installed in a `struct nls_table` with `.charset = "maccenteuro"`. Init and exit handlers register and unregister the table.

## Control Flow
The NLS core calls into the callbacks after a filesystem resolves the charset by name. `uni2char()` splits the Unicode value into high and low bytes, selects a reverse page, and emits one byte if the entry is nonzero. `char2uni()` indexes the direct byte table and returns one consumed byte unless the result is zero.

## State, Persistence, And Dependencies
The file is almost entirely static mapping tables generated from Unicode data. It has no mutable state beyond the registration lifetime managed by the module loader. It depends on the kernel module and NLS APIs.

## Integration Points
Availability is controlled by `CONFIG_NLS_MAC_CENTEURO` and the `mac-centeuro.o` Makefile entry. It is intended for Apple HFS-family filenames using Central European Mac encodings.

## Risks
Exact mapping means no fallback transliteration and no Unicode normalization. Some Unicode characters have no byte representation and return `-EINVAL`. The case conversion arrays are filled with sentinel values rather than useful lower/upper mappings, so case-insensitive filesystem code must not infer locale-aware folding from them.

## Test Signals
Round-trip tests across all mapped bytes, checks for Central European letters in Unicode pages `0x01` and `0x02`, module registration by the string `maccenteuro`, and negative tests for unmapped characters provide coverage.
