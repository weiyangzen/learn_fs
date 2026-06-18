# sources/control-plane/csi-driver-smb/hack/verify-helm-chart-index.sh

## Purpose
Validates URLs referenced in `charts/index.yaml`.

## Important APIs, Types, and Functions
Defines `check_url` using `curl -I` and local fallback path checks, plus `check_yaml` that greps HTTP URLs from the index.

## Control Flow
Iterates over index URLs, accepts HTTP 200, or verifies the equivalent local file exists before failing.

## State and Persistence
Read-only.

## Dependencies
Requires curl, grep, awk, and chart index layout.

## Integration Points
Called by `verify-all.sh` and protects Helm repository index integrity.

## Risks and Edge Cases
YAML parsing via grep/awk can catch unrelated URLs or miss quoted forms. Network failures may be treated as warnings only if local file exists.

## Test Signals
All URLs report valid or have local files, followed by success message.
