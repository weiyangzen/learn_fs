# Research: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-9.c

## Purpose

This generated module registers ISO 8859-9 / Latin-5 for Turkish. It is mostly Latin-1-compatible but replaces selected Icelandic letters with Turkish dotted/dotless I and G/S variants.

## Important APIs, Types, and Functions

`charset2uni[256]` is the byte-to-Unicode table. Reverse pages `page00` and `page01` map Latin and Turkish extended letters back to bytes. `charset2lower` and `charset2upper` encode ASCII and Turkish high-byte case pairs. `uni2char()`, `char2uni()`, and the `iso8859-9` table provide the NLS callbacks.

## Control Flow

Encoding and decoding are one-byte generated lookups. Missing reverse entries and zero decode entries return `-EINVAL`; no output capacity returns `-ENAMETOOLONG`.

## State and Persistence Behavior

Tables are static constants. The module only registers/unregisters the NLS table and has no per-consumer state.

## Dependencies and Integration Points

The module is used by filesystems through the Linux NLS registry under `iso8859-9`.

## Risks

Turkish dotted/dotless I case behavior is charset-specific and not equivalent to locale-aware Unicode casing. Confusing ISO 8859-9 with ISO 8859-1 corrupts high-byte Turkish letters.

## Test Signals

Round-trip Turkish `Ğ/ğ`, `İ/i`, `Ş/ş`, dotless `ı`, ASCII, and Latin-1 overlap. Validate case tables and failure for unmapped Unicode.
