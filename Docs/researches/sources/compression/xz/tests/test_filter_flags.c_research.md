# sources/compression/xz/tests/test_filter_flags.c

Purpose: tests `.xz` Filter Flags size, encoding, and decoding APIs.

Important data and helpers: defines `LZMA_FILTER_RESERVED_START`, global LZMA1/LZMA2/delta filter structs, compile-time lists of enabled BCJ encoders/decoders, `verify_filter_flags_encode()`, and `verify_filter_flags_decode()`.

Control flow: size tests verify supported filters produce reasonable lengths, LZMA1 is rejected for `.xz`, and invalid/reserved IDs fail. Encode tests check NULL/invalid options, BCJ default and start-offset properties, delta bounds, output-buffer size errors, and reserved ID errors. Decode tests construct Filter Flags manually using VLI and property APIs, then verify decoded option structs for LZMA2 dict size, BCJ start offset, and delta options; malformed IDs and truncated data assert correct errors.

State and persistence: allocates option structs in `main()` and decoded option structs in tests, freeing them after use. No files are used.

Dependencies and integration: uses liblzma filter support predicates, property coders, VLI coders, and `tests.h`. Compile-time macros determine which filters are present.

Risks: encode/decode of Filter Flags intentionally does not fully validate every filter option; chain initialization catches some invalid BCJ alignment later. Feature-disabled builds reduce coverage.

Test signals: catches binary encoding drift, reserved-ID handling, property-size bugs, and option allocation/freeing regressions.
