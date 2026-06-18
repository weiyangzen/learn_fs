# Research: sources/distributed-fs/ceph-client/fs/nls/nls_koi8-r.c

## Purpose

This generated NLS module registers KOI8-R for Russian. It maps KOI8-R bytes to Unicode Cyrillic, line-drawing, and symbol characters and provides exact reverse lookup for filesystem filename conversion.

## Important APIs, Types, and Functions

`charset2uni[256]` decodes bytes. Reverse pages `page00`, `page04`, `page22`, `page23`, and `page25` encode Latin/symbol, Cyrillic, mathematical, box drawing, and block/line drawing mappings. `charset2lower` and `charset2upper` implement KOI8-R byte-level case folding. `uni2char()`, `char2uni()`, and the registered `koi8-r` table implement the NLS interface.

## Control Flow

The callbacks are one-byte table lookups with standard NLS failure modes. Module init/exit register and unregister the generated table.

## State and Persistence Behavior

Translation data is immutable. Persistent effects are indirect: mounted filesystems using KOI8-R interpret on-disk names through these tables.

## Dependencies and Integration Points

The file depends on Linux NLS/module headers and integrates through `register_nls()` under `koi8-r`.

## Risks

KOI8-R includes box drawing and Cyrillic code points with non-obvious byte order. Table changes can break round-trip compatibility with legacy filesystems. Case folding must preserve KOI8-specific byte positions.

## Test Signals

Round-trip Russian Cyrillic, `Ё/ё`, box-drawing symbols, invalid Unicode pages, zero-length output, and high-byte case-fold pairs.
