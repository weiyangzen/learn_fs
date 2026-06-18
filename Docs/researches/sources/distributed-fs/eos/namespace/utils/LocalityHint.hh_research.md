# sources/distributed-fs/eos/namespace/utils/LocalityHint.hh

## Purpose
Provides a compact locality hint string for namespace entries by combining a parent container identifier with the child name. The binary prefix keeps hints sortable or shardable by parent before the human-readable name suffix.

## Important APIs, types, and functions
`LocalityHint::build(ContainerIdentifier parent, const std::string& name)` returns an eight-byte big-endian representation of the parent id, a colon, and the entry name. Private helpers convert a `uint64_t` to big-endian bytes with `htobe64()` and `memcpy()`.

## Control flow
Construction is linear: convert parent id to binary, append `:`, append name, and return the resulting string. The binary prefix may contain null bytes, so consumers must treat the return value as a length-aware `std::string`, not a C string.

## State and persistence
No mutable state is kept. If locality hints are persisted or used as database keys, byte order and delimiter placement become part of that storage contract.

## Dependencies and integration points
Depends on namespace identifiers and EOS namespace macros. It likely integrates with QuarkDB key layout, cache locality, or metadata grouping where parent-child proximity matters.

## Risks and test signals
Main risks are binary-string misuse, platform availability of `htobe64`, and ambiguity if consumers expect printable keys. Tests should validate exact byte layout, embedded zero handling, stable ordering for parent ids, empty names, and names containing colons.
