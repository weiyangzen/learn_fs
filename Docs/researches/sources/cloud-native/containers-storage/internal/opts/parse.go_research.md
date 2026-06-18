<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/opts/parse.go -->
# sources/cloud-native/containers-storage/internal/opts/parse.go

## Purpose
`parse.go` implements Docker-derived filter argument parsing and matching.

## Important APIs, Types, And Functions
`Args` stores `map[key]map[value]bool`. `KeyValuePair`, `Arg`, `NewArgs`, `ParseFlag`, `ToParam`, `ToJSON`, `MarshalJSON`, `Get`, `Add`, `Del`, `Len`, `MatchKVList`, `Match`, `ExactMatch`, `UniqueExactMatch`, `FuzzyMatch`, `Include`, `Contains`, `Validate`, and `WalkValues` are the main API. `ErrBadFormat` and `invalidFilterError` model errors.

## Control Flow
`ParseFlag` accepts `name=value`, trims/lowercases names, trims values, and adds them to a value set. Matching helpers interpret absent filters as match-all, exact matches before regex matching, and prefix matching for fuzzy checks. `Validate` rejects keys absent from an accepted map. `WalkValues` calls a callback for each value under a field.

## State And Persistence
All filter state is in-memory. JSON encoding returns an empty byte slice or string for no filters.

## Dependencies And Integration Points
`FilterOpt` wraps this type for flag parsing. Higher-level commands can use it to filter images, containers, or metadata maps.

## Risks And Edge Cases
Map iteration order is intentionally unstable, so `Get`, JSON object key ordering, and `WalkValues` should not be treated as ordered. Regex errors in `Match` are ignored. Empty filters match everything in exact, unique, and key/value list paths.

## Test Signals
The listed `opts_test.go` does not cover this file beyond `FilterOpt` indirectly not being tested. Dedicated tests should cover bad format, JSON output, matching modes, validation, and callback errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/opts/parse.go -->
