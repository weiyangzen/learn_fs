# sources/control-plane/csi-driver-smb/hack/update-gomod.sh

## Purpose
Updates `replace` directives for Kubernetes staging modules to match a specified Kubernetes version.

## Important APIs, Types, and Functions
Accepts a version argument, fetches Kubernetes `go.mod`, extracts staging module names with sed, resolves `kubernetes-$VERSION` module versions via `go mod download -json`, and applies `go mod edit -replace`.

## Control Flow
Strips leading `v` from the version, validates it, downloads upstream go.mod, loops over modules, prints module/version, and edits local go.mod.

## State and Persistence
Mutates local `go.mod` replace directives.

## Dependencies
Requires curl, sed, Go modules network access, and a valid Kubernetes release tag.

## Integration Points
Used during Kubernetes dependency bumps before dependency/vendor update verification.

## Risks and Edge Cases
Remote `go.mod` parsing is brittle. Network or missing pseudo-version modules fail the update. No `go mod tidy` is run here.

## Test Signals
Printed module versions, changed replace directives, and subsequent `go mod tidy/vendor` success.
