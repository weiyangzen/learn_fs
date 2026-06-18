<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-base64.c -->
# sources/cloud-native/ostree/src/libostree/ostree-blob-reader-base64.c

## Purpose
Implements `OstreeBlobReaderBase64`, a final `GDataInputStream` subclass that implements `OstreeBlobReader` by reading one newline-delimited base64 blob at a time.

## Important APIs and Types
`_ostree_blob_reader_base64_new()` constructs the reader around a base stream using the `base-stream` property inherited from `GDataInputStream`. `ostree_blob_reader_base64_read_blob()` is the interface implementation and returns a decoded `GBytes` for the next line.

## Control Flow
The interface initializer assigns `iface->read_blob`. On each read, the code calls `g_data_input_stream_read_line()`, propagates I/O errors, returns `NULL` on EOF, decodes the line in place with `g_base64_decode_inplace()`, clears the now-unused trailing encoded bytes with `explicit_bzero()`, and transfers the buffer into `GBytes`.

## State and Persistence
The only persistent state is the underlying stream cursor. Decoded data is returned as owned bytes; no blob cache is kept.

## Dependencies and Integration Points
Depends on `ostree-blob-reader-base64.h`, GLib/GIO stream APIs, and the shared `OstreeBlobReader` interface. It integrates with consumers that need line-oriented base64 signature/key/blob input.

## Risks
Malformed base64 handling is delegated to GLib's decoder; callers must distinguish EOF from error by checking the `GError`. Because one blob equals one input line, embedded newlines in encoded data are not supported here.

## Test Signals
Tests should cover valid base64 lines, EOF after last line, read cancellation/error propagation, invalid base64 behavior, and ensuring no trailing decoded buffer bytes leak into the returned `GBytes`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-base64.c -->
