# sources/distributed-fs/ceph-client/fs/nls/mac-croatian.c

## Purpose
This generated NLS module registers the `maccroatian` Macintosh Croatian codepage for single-byte legacy filename conversion.

## Important APIs, Types, And Functions
The module provides `charset2uni[256]`, reverse pages `page00`, `page01`, `page02`, `page03`, `page20`, `page21`, `page22`, `page25`, and `pagef8`, and a sparse `page_uni2charset` index. The `pagef8` entry handles the private-use Unicode point used by this mapping. `uni2char()`, `char2uni()`, and `struct nls_table table` follow the standard NLS table pattern with charset name `maccroatian`.

## Control Flow
Module initialization registers the table. Runtime conversion is one byte at a time. Unicode-to-byte conversion fails when the high-byte page is absent or the page entry is zero; byte-to-Unicode conversion fails only when the direct table yields zero.

## State, Persistence, And Dependencies
All conversion data are immutable static tables generated from Unicode source data. The only runtime state is whether the table is registered. The file depends on `linux/nls.h`, module infrastructure, and `errno.h`.

## Integration Points
`CONFIG_NLS_MAC_CROATIAN` and `mac-croatian.o` expose this module to kernel builds. Filesystems that store HFS-style Croatian Mac filenames can request the `maccroatian` NLS table.

## Risks
The private-use mapping requires exact agreement with userspace tools; substituting a different mapping table could break round trips. Like the sibling Mac tables, this file does not implement normalization or meaningful case maps. Generated table edits are easy to get wrong by hand.

## Test Signals
Round-trip every mapped byte, explicitly test Croatian letters and the private-use `0xf8ff` mapping, verify unmapped Unicode failure, and confirm module lookup by `maccroatian`.
