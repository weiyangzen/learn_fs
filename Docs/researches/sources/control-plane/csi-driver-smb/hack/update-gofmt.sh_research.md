# sources/control-plane/csi-driver-smb/hack/update-gofmt.sh

## Purpose
Formats all non-vendor Go files with simplified gofmt.

## Important APIs, Types, and Functions
Runs `find . -name "*.go" | grep -v "/vendor/" | xargs gofmt -s -w`.

## Control Flow
Fails on command errors through `set -euo pipefail`; otherwise rewrites matching files in place.

## State and Persistence
Mutates Go source files.

## Dependencies
Requires bash, find, grep, xargs, and gofmt.

## Integration Points
Repair companion for `verify-gofmt.sh`.

## Risks and Edge Cases
Whitespace-only changes can touch many files. It assumes file names are safe for xargs whitespace handling.

## Test Signals
Subsequent `verify-gofmt.sh` reports no diff.
