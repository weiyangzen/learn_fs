# sources/cloud-native/ostree/src/libotutil/ot-checksum-instream.h

## Purpose
Declares the `OtChecksumInstream` GObject type and constructors/accessors for checksum-filtered input streams.

## Important APIs, Types, And Functions
Defines type macros, instance/class structs, private pointer, `ot_checksum_instream_get_type`, `ot_checksum_instream_new`, `ot_checksum_instream_new_with_start`, and `ot_checksum_instream_get_string`.

## Control Flow
No runtime flow in the header. Consumers construct a stream, read through it, then request the checksum string.

## State And Persistence Behavior
Declares an instance containing private checksum state and inherited filter-stream state. No persistent state is declared.

## Dependencies And Integration Points
Depends on GIO. The macro definitions appear to reference `OT_TYPE_CHECKSUM_INPUT_STREAM` while the type macro is `OT_TYPE_CHECKSUM_INSTREAM`; that mismatch is a header risk unless hidden by lack of macro use or compatibility definitions elsewhere.

## Risks
The type macro mismatch can break code using the cast/check macros. The API does not document that only SHA256 is supported or that retrieving the digest finalizes checksum state.

## Test Signals
Compile tests using each macro, GObject type registration tests, and implementation digest tests cover this header.
