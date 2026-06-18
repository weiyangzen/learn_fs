# sources/cloud-native/composefs-rs/crates/composefs-storage/src/tar_split.rs

Purpose: Implements tar-split metadata consumption for containers-storage layers. It reads gzip-compressed NDJSON tar-split streams, returns raw tar segments, and opens layer file contents as owned file descriptors so callers can reconstruct or stream layer tars without serializing file payloads into memory.

Important APIs and types: `TarSplitItem` exposes `Segment(Vec<u8>)` and `FileContent { fd, size, name }`. `TarSplitEntryRaw` is the serde-facing NDJSON shape; `TarSplitEntry::from_raw` validates type ids 1 and 2. `TarHeader::from_bytes` parses 512-byte tar headers with `tar_core` and exposes helpers for regular files, directories, links, and normalized names. `TarSplitFdStream::new`, `next`, `entry_count`, `open_file_in_chain`, parent-layer search helpers, and `verify_crc64` are the core runtime surface.

Control flow: `new` opens `overlay-layers/<layer>.tar-split.gz`, wraps it in `GzDecoder` and `BufReader`, reopens the `Layer`, and clones the storage root dir. `next` loops over metadata lines, decodes segment payloads directly, and for file entries with nonzero size opens the path from the current layer or lower layers. Parent lookup follows overlay `lower` files and `overlay/l/<link>` symlinks recursively with a depth cap of 500. If a CRC64 value is present, the file is read, checked, rewound, and then converted into an `OwnedFd`.

State and persistence: The stream keeps only the active layer handle, storage root `Dir`, reader position, and an entry counter. It reads persistent state from containers-storage overlay and overlay-layers directories but does not mutate storage. File descriptors transfer ownership to callers.

Dependencies and integration: Uses `cap_std` for capability-oriented path access, `flate2`, `serde_json`, `base64`, `crc`, `tar_core`, and local `Storage`/`Layer`/`StorageError`. It feeds `userns_helper` streaming and any caller needing file-descriptor-backed tar reconstruction.

Risks: Path names are normalized only by stripping leading `./`; malicious or malformed tar-split paths rely on `cap_std` directory confinement. Parent traversal treats any `TarSplitError` as branch-not-found in some recursive paths, which can hide non-not-found tar-split errors. CRC verification is full-file I/O and may be expensive. Symlink-target parsing for overlay links assumes `../<layer-id>/diff`. Non-UTF-8 tar header paths are rejected.

Test signals: Unit tests cover tar header type helpers and type-id deserialization, including invalid types. More integration coverage would need real overlay/tar-split fixtures, CRC mismatch cases, parent chain lookup, and malformed overlay links.
