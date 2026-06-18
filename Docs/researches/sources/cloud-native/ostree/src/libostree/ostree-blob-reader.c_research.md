<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader.c -->
# sources/cloud-native/ostree/src/libostree/ostree-blob-reader.c

## Purpose
Defines the `OstreeBlobReader` GObject interface and the common dispatch function for reading blobs.

## Important APIs and Types
`G_DEFINE_INTERFACE()` registers the interface. `ostree_blob_reader_read_blob()` asserts the instance implements `OSTREE_TYPE_BLOB_READER` and calls the implementation's `read_blob` vfunc.

## Control Flow
Initialization only logs a debug message. Runtime dispatch is one virtual call through `OSTREE_BLOB_READER_GET_IFACE(self)->read_blob`.

## State and Persistence
The interface owns no state. Concrete implementations define stream cursor and decoding state.

## Dependencies and Integration Points
Depends on `ostree-blob-reader.h` and GObject. It integrates raw, base64, and PEM readers under a single nullable `GBytes` read contract.

## Risks
The interface does not provide a default `read_blob`; a class that fails to set the vfunc will crash when dispatched. Callers must use the `GError` convention to distinguish EOF from failure.

## Test Signals
Interface conformance tests should instantiate each concrete reader through the interface and validate EOF/error behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader.c -->
