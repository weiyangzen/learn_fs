# sources/cloud-native/buildkit/source/identifier.go

## Purpose
Defines the common interface all BuildKit source identifiers implement.

## Important APIs, Types, And Functions
- `Identifier` requires `Scheme()` for routing and `Capture(*provenance.Capture, pin)` for provenance recording.
- Package errors `errInvalid` and `errNotFound` are used by the manager for parse and scheme failures.

## Control Flow
Concrete source packages implement `Identifier`; `Manager.Resolve` uses `Scheme()` to find the registered source, and solver/provenance paths call `Capture` after a source pin is known.

## State And Persistence
No runtime state beyond static error values.

## Dependencies And Integration Points
Imports BuildKit provenance and pkg/errors. Used by `source.Manager`, git/http/local identifiers, and other source backends outside this subset.

## Risks And Edge Cases
The interface keeps source contracts small; errors are unexported, so callers match wrapped messages/types only within package usage.

## Test Signals
Indirectly tested by all source manager and backend resolution tests; no local unit tests in this subset.
