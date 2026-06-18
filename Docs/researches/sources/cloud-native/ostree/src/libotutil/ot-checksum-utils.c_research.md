# sources/cloud-native/ostree/src/libotutil/ot-checksum-utils.c

## Purpose
Provides SHA256 checksum primitives and stream/file helper functions, abstracting over OpenSSL, GnuTLS, or GLib checksum implementations.

## Important APIs, Types, And Functions
`ot_bin2hex` converts bytes to lowercase hex. `OtRealChecksum` backs public `OtChecksum`. Core functions are `ot_checksum_init`, `ot_checksum_update`, `ot_checksum_get_digest`, `ot_checksum_get_hexdigest`, `ot_checksum_clear`, `ot_csum_from_gchecksum`, `ot_gio_write_update_checksum`, `ot_gio_splice_update_checksum`, `ot_gio_splice_get_checksum`, `ot_checksum_file_at`, and `ot_checksum_bytes`.

## Control Flow
Initialization selects the compiled crypto backend and asserts SHA256 digest length. Update feeds bytes to the backend. Getting a digest finalizes the backend and marks the checksum closed. Splice helpers either manually read/write in 4 KiB chunks while updating a checksum or delegate to `g_output_stream_splice` when no checksum is requested. File checksum opens an fd-relative read stream, splices into a checksum, and returns a hex string.

## State And Persistence Behavior
Checksum state is stack- or object-owned and transient. Digests produced here are used as persistent object identifiers and verification values by callers.

## Dependencies And Integration Points
Depends on OpenSSL EVP, GnuTLS hash APIs, or GLib `GChecksum`, plus GIO streams and libglnx file helpers. It is a core utility for repository object hashing and content validation.

## Risks
`ot_checksum_get_digest`/`get_hexdigest` close the checksum; updating afterward is invalid. `ot_gio_splice_update_checksum` uses `g_input_stream_read_all`, so it loops until a full buffer or EOF and must handle short EOF correctly. `ot_checksum_file_at` ignores the `checksum_type` argument in practice because only SHA256 is implemented.

## Test Signals
Known SHA256 vectors, backend parity tests, write/splice checksum agreement, NULL output stream checksum-only mode, fd-relative file checksums, empty input handling, and update-after-finalize assertions are useful.
