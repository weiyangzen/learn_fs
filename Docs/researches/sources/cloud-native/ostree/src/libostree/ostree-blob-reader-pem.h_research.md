<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-pem.h -->
# sources/cloud-native/ostree/src/libostree/ostree-blob-reader-pem.h

## Purpose
Declares the PEM blob reader implementation type and public helper functions for PEM block reading.

## Important APIs and Types
Defines `OSTREE_TYPE_BLOB_READER_PEM` and declares final type `OstreeBlobReaderPem` deriving from `GDataInputStream`. Exposes `_ostree_blob_reader_pem_new()`, `_ostree_read_pem_block()`, and `ostree_blob_reader_pem_read_blob()`.

## Control Flow
The header has no runtime flow. It establishes the constructor and parsing APIs used by PEM reader consumers and by the implementation.

## State and Persistence
State is implementation-private: expected label plus underlying stream position.

## Dependencies and Integration Points
Includes `ostree-blob-reader.h` so the type can be consumed through the shared blob-reader abstraction. `_ostree_read_pem_block()` accepts a `GDataInputStream`, making the parser reusable outside the object wrapper.

## Risks
The helper returns nullable `GBytes` for both EOF and error, so callers must observe `GError`. The label out parameter transfers ownership when requested.

## Test Signals
Header-level signals are compile and introspection checks for type declaration, constructor linkage, and interface compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-pem.h -->
