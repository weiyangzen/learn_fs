<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/verify-gofmt -->
# sources/control-plane/juicefs-csi-driver/hack/verify-gofmt

## Purpose
Read-only formatter verifier for Go source files.

## Important APIs, Types, and Resources
Enumerates all non-vendor Go files and captures `gofmt -s -d` output. Non-empty diff output is printed and causes exit 1 with remediation text.

## Control Flow
The script runs gofmt in diff mode rather than write mode, so it reports formatting drift without mutating files.

## State and Persistence
No persistent state changes. Exit code and diff output are the state signal consumed by CI.

## Dependencies and Integration Points
Depends on Bash, Go toolchain, find/grep/xargs, and repository execution context. Paired with `hack/update-gofmt`.

## Risks
Risks are xargs edge cases for empty or unusual filenames and scanning generated Go files that may intentionally deviate.

## Test Signals
Introduce a formatting change and confirm failure; run `hack/update-gofmt` and confirm this script succeeds.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/verify-gofmt -->
