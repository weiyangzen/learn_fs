# Research: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-3.c

## Purpose

This generated NLS module registers ISO 8859-3 / Latin-3 for Esperanto, Maltese, Galician, and older Turkish usage. It is a single-byte translation table with several undefined byte positions represented as invalid mappings.

## Important APIs, Types, and Functions

`charset2uni[256]` contains byte-to-Unicode values and explicit zero holes for undefined charset bytes. Reverse pages `page00`, `page01`, and `page02` provide exact Unicode-to-byte mappings. `charset2lower` and `charset2upper` encode ASCII and Latin-3 case folding, including zero entries for unassigned high-half bytes. `uni2char()`, `char2uni()`, and the `iso8859-3` `struct nls_table` are the exported behavior.

## Control Flow

`uni2char()` performs a capacity check and emits exactly one byte when the selected reverse table has a nonzero entry. `char2uni()` decodes one byte and rejects entries that are `0x0000`. Module init/exit only add or remove the NLS table.

## State and Persistence Behavior

All mapping state is static and read-only. Runtime persistence is limited to the table being registered with the NLS core.

## Dependencies and Integration Points

The module is integrated through Linux NLS and filesystem charset conversion. It has no dependency on other NLS modules.

## Risks

Undefined ISO 8859-3 byte slots are represented by zero and must not be accidentally made valid. Some case-table entries for dotted/dotless and Esperanto/Maltese letters are non-obvious, so byte-position tests matter more than visual inspection.

## Test Signals

Round-trip Esperanto, Maltese, and Turkish-era Latin-3 letters, assert undefined bytes fail decode, assert unmapped Unicode fails encode, and validate case mappings for the high-half charset-specific letters.
