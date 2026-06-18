<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-raw.h -->
# sources/cloud-native/ostree/src/libostree/ostree-blob-reader-raw.h

## Purpose
Declares the raw line blob reader type.

## Important APIs and Types
Defines `OSTREE_TYPE_BLOB_READER_RAW` and final type `OstreeBlobReaderRaw` deriving from `GDataInputStream`. Exposes `_ostree_blob_reader_raw_new()` and `ostree_blob_reader_raw_read_blob()`.

## Control Flow
No runtime flow; this header provides type and function declarations.

## State and Persistence
State is inherited stream position only.

## Dependencies and Integration Points
Includes `ostree-blob-reader.h` and participates in the shared blob reader interface family.

## Risks
As with the other concrete reader headers, symbol visibility and underscore naming indicate internal use; external callers should prefer the common interface when possible.

## Test Signals
Compile/type registration checks plus `.c` behavioral tests validate this declaration.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-raw.h -->
