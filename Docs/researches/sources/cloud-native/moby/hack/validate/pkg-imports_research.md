# sources/cloud-native/moby/hack/validate/pkg-imports

## Purpose
Validates that packages under `pkg/` do not import non-public Moby internals.

## Important APIs and Types
Uses `.validate`, `validate_diff`, `go list -e -f '{{ join .Deps "\n" }}'`, and grep filters.

## Control Flow, State, and Persistence
The script lists changed `pkg/*.go` files, computes dependencies for each, filters out allowed `pkg`, `vendor`, and `internal` paths, and fails if remaining dependencies begin with `github.com/moby/moby`.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on Go package loading and changed-file detection. Risks include only checking direct `pkg/*.go` paths rather than recursive package paths if the diff glob is too narrow, and go list behavior with broken packages. CI validation protects package layering.
