<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-base64.h -->
# sources/cloud-native/ostree/src/libostree/ostree-blob-reader-base64.h

## Purpose
Declares the base64 blob reader implementation type and its constructor/read function.

## Important APIs and Types
Defines `OSTREE_TYPE_BLOB_READER_BASE64` and declares final type `OstreeBlobReaderBase64` deriving from `GDataInputStream`. Exports `_ostree_blob_reader_base64_new()` and `ostree_blob_reader_base64_read_blob()`.

## Control Flow
No runtime control flow is present. The header provides type metadata and function prototypes used by the implementation and callers.

## State and Persistence
The type's state is inherited stream state; the header does not define additional fields.

## Dependencies and Integration Points
Includes `ostree-blob-reader.h`, so users can treat the type as an `OstreeBlobReader`. `_OSTREE_PUBLIC` annotations expose the symbols according to libostree's internal/public visibility rules.

## Risks
The leading underscore constructor suggests internal API despite public visibility annotations. Callers must preserve the `GInputStream` lifetime through the object construction contract rather than retaining raw pointers.

## Test Signals
Compile-time type checks, interface casts, and construction through the declared constructor are sufficient for the header; behavioral tests belong to the `.c` file.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-base64.h -->
