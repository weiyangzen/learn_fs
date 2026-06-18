# sources/control-plane/rook/pkg/operator/k8sutil/name.go

## Purpose
`name.go` converts numeric daemon indexes to compact alphabetic names and back. Rook uses this for Ceph daemon IDs such as monitor names.

## Important APIs, Types, and Functions
`IndexToName(index int)` maps zero-based indexes to base-26 lowercase sequences: `0 -> a`, `25 -> z`, `26 -> aa`. `NameToIndex(name string)` is the inverse and rejects non-lowercase alphabetic characters. `maxPerChar` is the fixed alphabet size.

## Control Flow, State, and Persistence
There is no persistent state. `IndexToName()` repeatedly prepends calculated runes and subtracts one after division to model spreadsheet-style base-26 names. `NameToIndex()` computes a positional factor and validates each rune.

## Dependencies and Integration Points
The only dependency is `fmt` for formatting and errors. Higher-level operator code can rely on stable daemon IDs that remain compact while scaling past 26 entries.

## Risks
Negative indexes are not rejected by `IndexToName()` and can produce unexpected rune output. `NameToIndex("")` returns zero because no characters are processed. Only lowercase ASCII letters are valid, which is intentional but should be documented for callers.

## Test Signals
`name_test.go` verifies round-trip conversion across one-, two-, and three-letter boundaries. Missing signals include invalid names, empty names, and negative indexes.
