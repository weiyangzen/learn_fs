# sources/cloud-native/nydus/storage/src/meta/toc.rs

## Purpose
Defines the RAFS blob table-of-contents format and extraction logic for inlined blob components such as `image.boot`, `blob.meta`, `blob.meta.header`, `blob.digest`, and `rafs.blob.toc`.

## Important APIs, Types, And Functions
Constants name well-known ToC entries. `TocEntryFlags` maps supported entry compression algorithms. `TocEntry` is a 128-byte on-disk record with flags, 16-byte name, uncompressed digest, compressed offset/size, and uncompressed size. `TocEntryList` manages entries, parsing, cache fallback, extraction, and RAFS metadata extraction. `TocLocation` describes explicit or auto-detected ToC offset/size and optional digest validation.

## Control Flow
`TocEntryList::read_from_cache_file()` validates location, tries a small cache file, parses it if valid, otherwise downloads ToC data from the blob into a `.toc_downloading` file and atomically renames it. `read_toc_header()` either reads the final up-to-4K area of the blob or an explicit location. `parse_toc_header()` validates the trailing tar header for `rafs.blob.toc`, checks optional digest, and copies 128-byte records into entries. Extraction locates requested entries, verifies existing output by digest, writes to temporary files, and renames on success.

## State And Persistence
The ToC list itself is in-memory, but it persists cache files for downloaded ToC headers and extracted bootstrap/digest files. `toc_digest` and `toc_size` summarize parsed ToC content. Temporary `.toc_downloading` files protect against partial cache writes.

## Dependencies And Integration Points
Uses `BlobReader`/`BlobBufReader`, `BlobFactory`, `ConfigV2`, `RafsDigest`, tar headers, zstd decoding, and allocation helpers. `meta/mod.rs` uses ToC extraction to fetch inlined chunk digest files, and `extract_rafs_meta()` builds a backend reader from config to extract `image.boot`.

## Risks
The entry name field is limited to 16 bytes and invalid UTF-8 makes lookup fail for that entry. LZ4 is accepted as a flag but extraction returns unsupported, so producer/consumer compression choices must match this limitation. `read_toc_header()` returns `offset + 0x1000` as blob-size-like context for fallback bootstrap extraction, which assumes the auto-detect 4K read window semantics. Cache parsing only accepts files larger than 512 bytes, aligned to 128 bytes, and at most 4K.

## Test Signals
Tests with localfs fixtures cover ToC reading, explicit digest mismatch, auto-detect fallback, cache download/reuse, bootstrap extraction idempotence, compression-flag conversion, buffer extraction errors/success, entry name parsing, field getters, compressor round trips, ToC location validation, and `TocEntry` size. Source size reviewed: 1,084 lines.
