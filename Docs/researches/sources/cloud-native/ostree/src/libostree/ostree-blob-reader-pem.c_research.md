<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-pem.c -->
# sources/cloud-native/ostree/src/libostree/ostree-blob-reader-pem.c

## Purpose
Implements a simple RFC 7468 PEM reader that extracts base64 payloads from `-----BEGIN LABEL-----` / `-----END LABEL-----` blocks and optionally filters by an expected label.

## Important APIs and Types
`OstreeBlobReaderPem` is a final `GDataInputStream` subclass implementing `OstreeBlobReader`. It has construct-only string property `label`. `_ostree_blob_reader_pem_new()` creates the reader. `_ostree_read_pem_block()` is a reusable parser returning the next decoded block and optional label. `ostree_blob_reader_pem_read_blob()` enforces the instance label.

## Control Flow
The parser alternates between `PEM_INPUT_STATE_OUTER` and `PEM_INPUT_STATE_INNER`. It strips input lines, ignores blanks, searches for a begin marker, accumulates inner base64 lines, validates the end marker label with `strncmp()`, decodes the accumulated buffer in place, zeroes trailing encoded bytes, and returns the payload. EOF inside a block raises `PEM trailer not found`; a mismatched trailer raises `Unmatched PEM header`; a label mismatch raises `Unexpected label`.

## State and Persistence
Reader state consists of the expected label and the base stream cursor. Each read consumes through exactly one matching block or an error/EOF. Payloads are returned as detached `GBytes`.

## Dependencies and Integration Points
Depends on `ostree-blob-reader-pem.h`, `ostree-blob-reader-private.h`, GLib base64/string APIs, and the `OstreeBlobReader` interface. It is suitable for PEM encoded signatures, certificates, or keys where libostree wants no legacy PEM headers.

## Risks
The label comparison checks only `end - start` bytes and does not independently verify equal label length, so prefixes deserve tests. The parser deliberately does not support RFC 1421 headers and treats any non-END inner line as base64 data. Decoding large PEM payloads accumulates the full encoded body in memory.

## Test Signals
Tests should cover multiple blocks, blank lines, label filtering, mismatched labels, missing trailer, payload decoding, EOF behavior, and malformed or header-bearing PEM inputs.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-pem.c -->
