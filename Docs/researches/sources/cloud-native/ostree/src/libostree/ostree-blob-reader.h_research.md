<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader.h -->
# sources/cloud-native/ostree/src/libostree/ostree-blob-reader.h

## Purpose
Declares the `OstreeBlobReader` interface used by line/block-oriented blob decoders.

## Important APIs and Types
Defines `OSTREE_TYPE_BLOB_READER`, declares `G_DECLARE_INTERFACE`, and defines `OstreeBlobReaderInterface` with one vfunc: `GBytes *(*read_blob)(OstreeBlobReader*, GCancellable*, GError**)`. Exposes `ostree_blob_reader_read_blob()`.

## Control Flow
The header defines the dispatch contract but no implementation flow.

## State and Persistence
No state is defined at interface level. Implementations are free to maintain parser or stream state.

## Dependencies and Integration Points
Includes `ostree-types.h` and `<gio/gio.h>`. Concrete readers implement this interface and callers can consume all formats through a single API.

## Risks
The nullable return conflates EOF and error unless `GError` is checked. The interface is synchronous and reads one complete blob per call, so large blob formats can imply whole-blob buffering.

## Test Signals
ABI/type checks, vfunc dispatch tests, and concrete implementation coverage validate the interface contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader.h -->
