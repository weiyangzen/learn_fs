# Research: sources/distributed-fs/ceph-client/fs/nls/nls_koi8-u.c

## Purpose

This generated NLS module registers KOI8-U for Ukrainian. It extends KOI8-R-style Cyrillic coverage with Ukrainian-specific letters while retaining symbol and line-drawing mappings.

## Important APIs, Types, and Functions

`charset2uni[256]` decodes KOI8-U bytes. Reverse pages `page00`, `page04`, `page22`, `page23`, and `page25` map Unicode pages for common symbols, Cyrillic, math, box drawing, and drawing/block symbols back to bytes. `charset2lower` and `charset2upper` encode KOI8-U byte-level case pairs. The registered table uses `.charset = "koi8-u"`.

## Control Flow

`uni2char()` and `char2uni()` are one-byte table lookups with the standard generated NLS sentinel handling. Init and exit register and unregister the NLS table.

## State and Persistence Behavior

All mapping data is immutable. The table can also be a dependency for `koi8-ru`, so unloading order matters through NLS reference handling.

## Dependencies and Integration Points

The file integrates through the Linux NLS registry and may be loaded directly by filesystems or indirectly by the KOI8-RU adapter.

## Risks

Ukrainian Cyrillic overrides must not be confused with KOI8-R or KOI8-RU. Box-drawing and symbol pages need exact reverse mappings for round trips. Case-folding is charset-byte-specific.

## Test Signals

Round-trip Ukrainian-specific letters, Russian overlap, box-drawing symbols, delegated use by KOI8-RU, invalid Unicode pages, and upper/lower case table behavior.
