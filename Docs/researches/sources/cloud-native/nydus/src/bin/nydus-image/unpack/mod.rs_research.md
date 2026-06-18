# sources/cloud-native/nydus/src/bin/nydus-image/unpack/mod.rs

## Purpose
`unpack/mod.rs` converts a RAFS bootstrap plus blob backend into an OCI-style tar stream. It provides the `Unpacker` trait, `OCIUnpacker`, tar writer construction, RAFS iteration, and a chain of inode-type-specific section builders.

## Important APIs, Types, And Functions
`Unpacker::unpack` is the public abstraction. `OCIUnpacker::new` records bootstrap, optional blob backend, output path, and a builder factory. `OCIUnpacker::load_rafs` loads `RafsSuper`. `OCITarBuilderFactory::create` opens the output tar and builds section builders. `create_builders` assembles socket, hardlink, directory, regular-file, symlink, FIFO, char-device, and block-device builders from `pax.rs`. `OCITarBuilder::append` picks the first builder whose `can_handle` returns true and appends every `TarSection`.

## Control Flow
`OCIUnpacker::unpack` loads the RAFS metadata, creates an `OCITarBuilder`, iterates all RAFS inodes using `RafsIterator`, and appends each node/path pair to the tar. Builder order matters: sockets are skipped, hardlinks are detected before regular files, directories are emitted before regular files, and special nodes fall through to their own builders. Regular-file builder creation resolves every blob in the RAFS blob table into a `BlobReader` and stores per-blob compressors.

## State And Persistence
The module writes one tar file, truncating any existing output. It reads RAFS metadata and blob data through the configured backend. It keeps short-lived builder state, including the tar writer, hardlink map in the PAX hardlink builder, per-blob readers, and compressor maps.

## Dependencies And Integration Points
It integrates `nydus-image unpack`, `RafsSuper`, `RafsIterator`, `RafsInodeExt`, `BlobBackend`, `BlobInfo`, `tar::Builder`, and the PAX/OCI builders in `pax.rs`. Backend resolution is provided by `main.rs`, either from `--blob`, `--blob-dir`, or non-local backend configuration.

## Risks
All regular files require a valid blob backend; missing backend readers fail builder creation. Builder ordering is semantically important for hardlinks and sockets. `append` fails on any inode type not recognized by the chain. Tar output is truncated before iteration, so later RAFS/blob errors leave a partial tar. The module does not call `Builder::finish` explicitly, relying on drop behavior.

## Test Signals
There are no direct tests in this file. `pax/test.rs` covers chunk reading, while end-to-end unpack tests should validate directories, hardlinks, symlinks, special files, xattrs, long paths, compressed/uncompressed chunks, and missing backend errors.
