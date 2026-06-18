<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/gzip_index_create.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/gzindex/gzip_index_create.cpp

## Purpose
Builds gzip index files by scanning gzip streams, recording restartable deflate block positions and saved dictionaries.

## Important APIs, Types, And Functions
Implements `IndexFilterRecorder`, `zlib_compress`, `dict_compress`, `create_index_entry`, `new_index_filter`, `delete_index_filter`, `build_index`, `get_compressed_index`, `save_index_to_file`, `init_index_header`, and `create_gz_index`.

## Control Flow
`create_gz_index` validates dictionary compression options and span, creates/truncates index file, initializes header, inflates the gzip file with `inflateInit2(..., 47)` and `Z_BLOCK`, records entries when zlib reports block boundaries at or after span intervals, writes dictionary blobs as they are discovered, compresses and appends the final `IndexEntry` array, then writes the finalized header with CRC.

## State And Persistence
Writes a durable index file containing header, saved dictionaries, and compressed or raw entry array. In-memory `INDEX` owns heap `IndexEntry` pointers during creation.

## Dependencies And Integration Points
Uses zlib, Photon local file adapter, logging, and format declarations from `gzfile_index.h`. Stream indexing in `gzip/gz.cpp` reuses the recorder/save helpers.

## Risks And Test Signals
Index quality depends on zlib `data_type` block-boundary bits. Span below 64 KiB is rejected. `build_index` reads through sequential `read`, so caller file offset is consumed. Dictionary compression buffer assumes 64 KiB is enough for compressed 32 KiB dictionaries, which is safe for zlib overhead. Tested by `gzindex_test`. Source size reviewed: 386 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/gzip_index_create.cpp -->
