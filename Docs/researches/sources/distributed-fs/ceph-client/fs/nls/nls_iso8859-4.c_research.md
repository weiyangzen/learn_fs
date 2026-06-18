# Research: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-4.c

## Purpose

This generated module registers ISO 8859-4 / Latin-4, an older Baltic charset. It supplies single-byte filename conversion tables for ASCII plus Baltic and Nordic extended Latin letters.

## Important APIs, Types, and Functions

`charset2uni[256]` decodes bytes. `page00`, `page01`, and `page02` reverse selected Unicode pages to byte values. `charset2lower` and `charset2upper` implement byte-level folding. `uni2char()`, `char2uni()`, and the `iso8859-4` table provide the NLS interface.

## Control Flow

Conversion is a single table lookup in each direction. `uni2char()` checks `boundlen`, dispatches by Unicode high byte, and returns one byte or `-EINVAL`. `char2uni()` decodes one byte and treats zero as invalid.

## State and Persistence Behavior

The generated arrays are read-only. The module only mutates global NLS registry state when loaded or unloaded.

## Dependencies and Integration Points

The code depends on kernel NLS infrastructure and integrates with any filesystem that requests `iso8859-4`.

## Risks

ISO 8859-4 overlaps visually with other Latin/Baltic sets but has different byte assignments. Case tables and reverse pages must be validated against the exact standard, not inferred from neighboring ISO-8859 files.

## Test Signals

Round-trip Baltic/Nordic characters, verify spacing marks in `page02`, check high-half case folding, reject unmapped Unicode and NUL, and build-test the generated initializers.
