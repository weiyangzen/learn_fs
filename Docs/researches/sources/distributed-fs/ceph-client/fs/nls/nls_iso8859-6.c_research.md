# Research: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-6.c

## Purpose

This generated module registers ISO 8859-6 for Arabic. It is a single-byte NLS table for Arabic letters and marks, with many unassigned positions represented as invalid mappings.

## Important APIs, Types, and Functions

`charset2uni[256]` decodes bytes. Reverse pages `page00` and `page06` map common symbols and Arabic Unicode page entries back to byte values. `charset2lower` and `charset2upper` are effectively identity/ASCII-oriented because Arabic has no simple case folding. `uni2char()`, `char2uni()`, and the `iso8859-6` table implement the NLS ABI.

## Control Flow

Encoding uses Unicode high-byte dispatch and emits one byte for nonzero reverse entries. Decoding indexes one byte in `charset2uni` and rejects zero. Module init/exit register and unregister the table.

## State and Persistence Behavior

The generated tables are static and read-only. No runtime state is held beyond NLS registry membership.

## Dependencies and Integration Points

The file depends on the Linux NLS core and is consumed by filesystems through `register_nls()`.

## Risks

Unassigned bytes in ISO 8859-6 must remain invalid. The module performs no bidirectional shaping or normalization; it only maps encoded characters. Callers expecting Arabic presentation handling must do it elsewhere.

## Test Signals

Round-trip Arabic letters and punctuation in `page06`, verify unassigned byte failures, verify no unexpected case changes beyond ASCII tables, and exercise short output buffer and unmapped Unicode failures.
