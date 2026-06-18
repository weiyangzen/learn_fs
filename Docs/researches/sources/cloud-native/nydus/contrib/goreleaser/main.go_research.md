# sources/cloud-native/nydus/contrib/goreleaser/main.go

## Purpose
This tiny Go program is a placeholder binary used to work around goreleaser behavior when it cannot prebuild another target binary.

## Important APIs, Types, and Functions
The only API is `main`, which calls `fmt.Println`.

## Control Flow
Execution prints `Hello, World!` and exits.

## State, Persistence, and Dependencies
There is no state or persistence. The only dependency is the Go standard library `fmt`.

## Integration Points
Its integration point is release tooling, not runtime Nydus behavior. It gives goreleaser a buildable Go main package.

## Risks and Test Signals
Risk is low, but accidental shipping or invocation would be misleading because it does not perform real release logic. No tests are present.
