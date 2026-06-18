# sources/cloud-native/moby/internal/namesgenerator/names-generator.go

## Purpose
Generates Docker-style random container names from a frozen adjective list and a frozen list of notable surnames/names, formatted as `adjective_name` with an optional numeric suffix on retry.

## Important APIs, Types, And Functions
- Package-level arrays `left` and `right` hold adjectives and names with comments explaining many name origins.
- `GetRandomName(retry int)` chooses one random element from each list using `math/rand`, rejects the special `boring_wozniak` combination, and appends a random digit if `retry > 0`.

## Control Flow
The generator loops via `goto begin` only for the disallowed combination, then conditionally appends a digit and returns the string.

## State And Persistence
No package-local mutable state is maintained, but `math/rand` global state controls randomness. The lists are static and documented as officially frozen.

## Dependencies And Integration Points
Uses `math/rand` and `strconv`. The function is used by Docker/Moby name generation where a human-readable random name is needed, commonly for containers when no explicit name is provided.

## Risks And Edge Cases
Randomness is not cryptographic and is intentionally marked with `nolint:gosec`. Retry suffix is only a single digit, so it reduces but does not eliminate collisions. The function is not deterministic unless the global random source is seeded predictably by callers/runtime.

## Test Signals
Tests validate underscore format, absence of digits when `retry == 0`, presence of a digit when `retry > 0`, and benchmark allocation/performance.
