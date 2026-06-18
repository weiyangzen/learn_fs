# sources/cloud-native/ostree/src/libotutil/ot-checksum-instream.c

## Purpose
Implements `OtChecksumInstream`, a `GFilterInputStream` that updates a SHA256 checksum as bytes are read from an underlying stream.

## Important APIs, Types, And Functions
The private struct contains an `OtChecksum`. `ot_checksum_instream_new` creates a SHA256 checksum stream. `ot_checksum_instream_new_with_start` optionally seeds the checksum with initial bytes. `ot_checksum_instream_read` proxies reads and updates the checksum for positive byte counts. `ot_checksum_instream_get_string` returns the final hex digest.

## Control Flow
Construction validates the base stream, initializes the checksum, and optionally updates with a prefix. Reads delegate to the base stream and update the checksum with the returned buffer. Finalization clears the checksum. Calling `get_string` finalizes the checksum through `ot_checksum_get_hexdigest`.

## State And Persistence Behavior
State is in-memory checksum context plus the base stream reference managed by `GFilterInputStream`. It does not persist data, but callers use its digest to identify or verify persisted objects.

## Dependencies And Integration Points
Depends on GObject, GIO stream classes, `ot-checksum-utils`, and SHA256 constants. It integrates into code paths that need streaming reads and checksums without buffering whole files.

## Risks
Only SHA256 is currently accepted via assertion. Fetching the digest closes the underlying checksum context, so further reads/checksum updates after `get_string` are invalid. Error propagation is exactly the base stream read error.

## Test Signals
Read-through tests comparing digest against known SHA256, seeded-prefix tests, short reads, read errors, finalization leak checks, and misuse tests around digest-before-finish are useful.
