# sources/control-plane/csi-driver-smb/hack/verify-spelling.sh

## Purpose
Runs misspell across tracked non-vendor files.

## Important APIs, Types, and Functions
Uses `misspell` version `v0.3.4`, installs it into a temp `GOBIN` if missing, and scans `git ls-files | grep -v vendor`.

## Control Flow
Creates temp dir, ensures misspell is available, writes misspell output to temp log, prints errors with `error:` prefix, and exits nonzero if any exist.

## State and Persistence
Uses temp directory and Go module/cache. Does not edit source.

## Dependencies
Requires git, Go toolchain, misspell or network access to install it.

## Integration Points
Optional CI quality gate.

## Risks and Edge Cases
`go get` for tool installation is outdated in newer Go versions. Grep vendor filtering is broad. False positives require dictionary or source changes elsewhere.

## Test Signals
Empty errors log and zero exit status.
