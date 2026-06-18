# Research: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-7.c

## Purpose

This generated NLS module registers ISO 8859-7 for Modern Greek. It maps Greek single-byte filenames to Unicode and supports exact reverse conversion for the covered Greek and punctuation characters.

## Important APIs, Types, and Functions

`charset2uni[256]` decodes the byte set. Reverse pages `page00`, `page02`, `page03`, and `page20` cover Latin/symbol bytes, spacing modifier characters, Greek code points, and selected punctuation. `charset2lower` and `charset2upper` encode Greek and ASCII byte-level case pairs. The registered table is `.charset = "iso8859-7"`.

## Control Flow

The conversion callbacks are generated one-byte lookups. `uni2char()` rejects insufficient output or absent reverse mappings; `char2uni()` rejects zero decode entries and consumes one byte.

## State and Persistence Behavior

All mapping arrays are constant. Runtime state is only module registration with the NLS core.

## Dependencies and Integration Points

The module depends on Linux NLS infrastructure and integrates with filesystem charset conversion under `iso8859-7`.

## Risks

Greek tonos/dialytika characters and punctuation page entries are easy to confuse with other Greek encodings. Case folding is byte-based and does not implement full Unicode Greek casing rules.

## Test Signals

Round-trip Greek uppercase/lowercase, accented Greek characters, punctuation from `page20`, invalid byte/table holes, invalid Unicode pages, and case-folding entries.
