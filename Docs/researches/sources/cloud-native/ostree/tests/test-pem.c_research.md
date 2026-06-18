<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pem.c -->
# sources/cloud-native/ostree/tests/test-pem.c

## Purpose
`test-pem.c` unit-tests PEM block parsing for embedded public key data.

## Important APIs, Types, And Functions
The file defines sample Ed25519 public key bytes and PEM strings, then tests `_ostree_read_pem_block` from `ostree-blob-reader-private.h`.

## Control Flow
The valid test parses a normal PEM block and one with extra whitespace, then compares decoded bytes with expected Ed25519 data. The invalid test covers empty input, missing trailer, label mismatch, and other malformed PEM cases, expecting errors.

## State And Persistence
All state is static byte/string constants, local buffers, and errors. No files are read or written.

## Dependencies And Integration Points
This validates parsing used by signature/key loading paths, especially for ASCII-armored key material.

## Risks And Test Signals
PEM parsing must reject malformed labels and truncated data without accepting ambiguous input. Passing signals are exact decoded bytes for valid blocks and errors for invalid variants.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pem.c -->
