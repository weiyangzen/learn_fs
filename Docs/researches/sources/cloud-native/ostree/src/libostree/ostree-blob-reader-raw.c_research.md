<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-raw.c -->
# sources/cloud-native/ostree/src/libostree/ostree-blob-reader-raw.c

## Purpose
Implements `OstreeBlobReaderRaw`, a line-oriented raw blob reader that returns each input line as bytes without decoding.

## Important APIs and Types
`_ostree_blob_reader_raw_new()` constructs the `GDataInputStream` subclass. `ostree_blob_reader_raw_read_blob()` implements `OstreeBlobReaderInterface.read_blob`.

## Control Flow
The read method calls `g_data_input_stream_read_line()`, propagates any local read error, returns `NULL` on EOF, and otherwise wraps the line buffer with `g_bytes_new_take()` using the line length returned by GIO.

## State and Persistence
The reader persists only the underlying stream cursor. Each successful call consumes one line and returns an owned immutable byte blob.

## Dependencies and Integration Points
Depends on `ostree-blob-reader-raw.h`, `GDataInputStream`, and the shared blob reader interface. It is used wherever libostree needs newline-delimited opaque blobs.

## Risks
Newline terminators are not included in returned data because `g_data_input_stream_read_line()` strips them. This reader is unsuitable for blobs that may contain embedded newlines or require exact original line endings.

## Test Signals
Tests should cover multi-line input, EOF, empty lines, cancellation/read errors, and exact returned byte lengths.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-raw.c -->
