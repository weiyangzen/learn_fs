<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzip/gz.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/gzip/gz.cpp

## Purpose
Provides gzip read adapters: a simple zlib `gzFile` wrapper and a streaming gzip decompressor that can save a gzip index while reading from a Photon stream.

## Important APIs, Types, And Functions
Defines `GzAdaptorFile`, `GzStreamFile`, exported `open_gzfile_adaptor`, and `open_gzstream_file`. `GzStreamFile` implements `read`, `lseek`, `fstat`, `sha256_checksum`, and `save_index`.

## Control Flow
`GzAdaptorFile` delegates sequential reads/seeks to zlib `gzread/gzseek`. `GzStreamFile` reads compressed chunks from an `IStream`, validates gzip magic, inflates with `Z_BLOCK`, copies requested decompressed bytes to the caller, spills surplus decompressed bytes to a temporary buffer file, records index entries via `IndexFilterRecorder`, and later writes/renames the index using the stream SHA256.

## State And Persistence
Creates temporary buffer and index files under the workdir, tracks compressed/uncompressed offsets, zlib stream state, saved index entries, and optional SHA256 wrapper. Destructor deletes the buffer file and releases stream/index state. `save_index` persists the final `.gz_idx` file named from the checksum.

## Dependencies And Integration Points
Depends on zlib, Photon virtual files/localfs/subfs/socket streams, sha256 file wrapper, and gzindex helpers.

## Risks And Test Signals
`open_gzstream_file` ignores its `save_idx` parameter and always enables index save. `read` contains a fixed `assert(n + delta <= 65536)` even though callers can ask for larger counts. Temporary filenames use timestamp or UID and are unlinked on destructor. Covered indirectly by `gzindex/test` stream fixture. Source size reviewed: 297 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzip/gz.cpp -->
