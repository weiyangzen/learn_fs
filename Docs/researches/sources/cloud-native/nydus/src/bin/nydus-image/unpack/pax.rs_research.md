# sources/cloud-native/nydus/src/bin/nydus-image/unpack/pax.rs

## Purpose
`pax.rs` implements the OCI tar/PAX section builders used by the RAFS unpacker. It maps RAFS inode metadata and blob chunks into tar headers, PAX extended headers, xattr records, link records, special-device records, and streaming file data.

## Important APIs, Types, And Functions
OCI builders include `OCISocketBuilder`, `OCILinkBuilder`, `OCIDirBuilder`, `OCIRegBuilder`, `OCISymlinkBuilder`, `OCIFifoBuilder`, `OCICharBuilder`, and `OCIBlockBuilder`. Shared builders are `PAXSpecialSectionBuilder`, `PAXExtensionSectionBuilder`, and `PAXLinkBuilder`. `PAXUtil` converts xattrs and long path/link names to PAX records. `Util` normalizes paths, truncates ustar names, masks Unix modes, and computes tar checksums. `ChunkReader` implements `Read` across RAFS blob chunks, including decompression.

## Control Flow
Each builder first checks inode type with `can_handle`. Directory, regular, link, and special-file builders create a ustar header, call `set_header_by_inode`, add type-specific fields, collect PAX extensions for long paths/links and xattrs, set checksums, optionally prepend an XHeader section, then emit the main section. Hardlink handling stores the first path per inode and emits later appearances as hard links. `ChunkReader::read` loads the next chunk when its current cursor is exhausted, reads compressed bytes from the appropriate blob reader at `compressed_offset`, decompresses when `is_compressed`, then fills the caller buffer across chunk boundaries.

## State And Persistence
The module writes only through the tar writer owned by `unpack/mod.rs`. In-memory state includes hardlink first-path tracking, per-blob readers and compressor algorithms, pending chunk iterator state, and current decompressed chunk data. PAX xattrs are represented as `SCHILY.xattr.*` records. Username and group name are resolved from host UID/GID databases during unpacking, so output can vary by host.

## Dependencies And Integration Points
It depends on `tar::Header`, `EntryType`, RAFS inode traits, `InodeWrapper`, `BlobReader`, `BlobChunkInfo`, `alloc_buf`, Nydus compression algorithms, Unix `nix::unistd` user/group lookup, and the parent `SectionBuilder`/`TarSection` traits. It is not a standalone tar writer; `OCITarBuilderFactory` instantiates these builders and controls ordering.

## Risks
There are several unwrap/expect paths: symlink target, chunk info lookup, xattr reads, blob reader/compressor lookup, username/group lookup fallbacks, and header path reads. Long-path truncation cuts to valid UTF-8 before relying on PAX full path records; non-UTF-8 path prefixes can still be fragile. `MockBlobReader` tests expose that short reads are possible, but production `ChunkReader::load_chunk` does not verify that the reader filled the requested compressed size. Host-dependent username/group backfill can break reproducibility. Socket inodes are silently skipped.

## Test Signals
The sibling `pax/test.rs` validates `ChunkReader` behavior for exact-size, smaller, larger, zero-length, and compressed reads. Additional useful signals are tar round trips for long names, xattrs, hardlinks, symlinks, device nodes, FIFOs, directories with trailing slash normalization, non-UTF-8 paths, and partial backend reads.
