<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-checksum-input-stream.c -->
# sources/cloud-native/ostree/src/libostree/ostree-checksum-input-stream.c

## Purpose
Implements `OstreeChecksumInputStream`, a `GFilterInputStream` that updates a caller-owned `GChecksum` with bytes successfully read from the base stream.

## Important APIs and Types
Private state stores `GChecksum *checksum`. `ostree_checksum_input_stream_new()` constructs the filter with `base-stream` and construct-only pointer property `checksum`. The class overrides `read_fn`.

## Control Flow
Read checks cancellation, delegates to the base stream, and calls `g_checksum_update()` only when the delegated read returns a positive byte count. EOF and errors do not update the checksum.

## State and Persistence
The stream does not own or free the checksum; it mutates caller-owned checksum state as reads progress. The only stream state comes from the base `GFilterInputStream`.

## Dependencies and Integration Points
Depends on GLib/GIO checksum and stream APIs. It integrates with code that needs streaming hashing without manually wrapping each read call.

## Risks
The checksum pointer is borrowed; callers must keep it alive longer than the stream. Partial reads update incrementally, so abandoning the stream yields a partial checksum by design.

## Test Signals
Tests should compare checksum results against hashing the full input, cover partial reads, EOF, cancellation, read errors, and lifetime expectations.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-checksum-input-stream.c -->
