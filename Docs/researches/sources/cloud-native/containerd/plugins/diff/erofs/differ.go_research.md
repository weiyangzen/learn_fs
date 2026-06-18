# sources/cloud-native/containerd/plugins/diff/erofs/differ.go

## Purpose
Implements EROFS diff application and construction options. It can apply native EROFS blobs directly, convert tar layers to EROFS, generate tar-index EROFS layers, and optionally append dm-verity metadata.

## Important APIs, Types, And Functions
`erofsDiff` stores the content store and options. `WithMkfsOptions`, `WithTarIndexMode`, and `WithDmverity` configure behavior. `NewErofsDiffer` constructs a combined `diff.Applier`/`diff.Comparer`. `Apply` streams content through processors and writes `layer.erofs`. `readCounter` tracks uncompressed byte count.

## Control Flow
Apply determines whether the descriptor is native EROFS or a supported OCI layer, normalizes native media types for processor selection, parses apply options, resolves the snapshot layer path, opens content, fast-copies uncompressed native EROFS blobs, otherwise obtains an uncompressed layer stream, hashes and counts bytes, writes either native EROFS, tar-index EROFS, or converted EROFS, drains trailing data, optionally formats dm-verity, and returns the descriptor representing applied content.

## State And Persistence
Writes `layer.erofs` inside the snapshot layer directory. Optional dm-verity formatting extends that file and writes adjacent metadata. Content blobs remain in the content store and are only read.

## Dependencies And Integration Points
Integrates with `core/diff`, content store readers, OCI media types, `images.DiffCompression`, `internal/erofsutils`, Google UUID generation, and platform-specific `formatDmverityLayer`.

## Risks
Native media suffix handling only accepts `+zstd`. Fast-copy returns the original descriptor without rehashing. Tar-index mode has block-size implications for dm-verity. Any mismatch between EROFS snapshot layout and `MountsToLayer` breaks apply.

## Test Signals
Dm-verity helpers have unit tests. EROFS apply behavior is mainly covered by integration tests requiring mkfs.erofs and EROFS snapshotter support.
