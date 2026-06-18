# sources/control-plane/csi-driver-smb/hack/verify-gofmt.sh

## Purpose
Checks that non-vendor Go files are gofmt-simplified.

## Important APIs, Types, and Functions
Captures `gofmt -s -d` output for all `.go` files outside vendor.

## Control Flow
Prints the diff and remediation hint if any formatting diff exists, otherwise prints "No issue found".

## State and Persistence
Read-only.

## Dependencies
Requires find, grep, xargs, and gofmt.

## Integration Points
Called by `verify-all.sh`; repaired by `update-gofmt.sh`.

## Risks and Edge Cases
Whitespace in filenames can confuse xargs. Very large diffs are printed in full.

## Test Signals
Empty gofmt diff and zero exit code.
