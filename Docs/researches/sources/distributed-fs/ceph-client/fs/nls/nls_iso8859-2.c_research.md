# Research: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-2.c

## Purpose

This generated NLS module registers ISO 8859-2 / Latin-2 for Central and Eastern European languages. It provides exact single-byte mappings for ASCII, selected Latin-1 symbols, and extended Latin characters used by Slavic and Central European alphabets.

## Important APIs, Types, and Functions

`charset2uni[256]` maps bytes to Unicode. Reverse pages `page00`, `page01`, and `page02` map Unicode pages `0x00`, `0x01`, and selected spacing modifier letters back to charset bytes. `charset2lower` and `charset2upper` encode byte-level case folding for ASCII and Latin-2-specific pairs. `uni2char()`, `char2uni()`, and the `struct nls_table` registered as `iso8859-2` implement the NLS ABI.

## Control Flow

Encoding and decoding are one-byte table lookups with `-ENAMETOOLONG` for zero output capacity and `-EINVAL` for missing mappings. There are no dynamic allocations, locks, or multibyte branches.

## State and Persistence Behavior

The module stores immutable generated tables and registers/unregisters them at module load/unload. The table values are effectively persistent compatibility data for filenames encoded as ISO 8859-2.

## Dependencies and Integration Points

The file depends on kernel module/NLS headers and is consumed by filesystem charset conversion code through the generic NLS registry.

## Risks

Central European accented letters have many similar-looking precomposed Unicode values; table drift can silently corrupt filenames. Case tables must match byte positions, not Unicode ordering. The zero-entry sentinel excludes NUL conversion.

## Test Signals

Validate round trips for Polish, Czech, Slovak, Hungarian, Slovenian/Croatian letters, spacing modifier entries in `page02`, invalid Unicode pages, empty output buffers, and high-byte case-fold pairs.
