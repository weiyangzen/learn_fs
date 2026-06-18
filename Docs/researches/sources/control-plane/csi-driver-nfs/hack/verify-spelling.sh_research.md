<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-spelling.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-spelling.sh

## Purpose
Runs spelling checks over tracked repository files outside vendor.

## Important APIs, Types, and Functions
The script pins `misspell` tool version `v0.3.4`, creates a temporary directory, installs `github.com/client9/misspell/cmd/misspell` into that directory if absent, then runs `git ls-files | grep -v vendor | xargs misspell`.

## Control Flow, State, and Persistence
It changes to the repository root, installs the tool in a temp directory when needed, captures misspell output to `errors.log`, prefixes errors, and exits with status 1 if any spelling issue is found. Temp files are removed via an EXIT trap.

## Dependencies and Integration Points
It depends on git, Go, network access if misspell is missing, and the external misspell ruleset. It is a standalone quality gate, not shown in `verify-all.sh`.

## Risks and Test Signals
Risks include false positives in code or generated files, broad vendor filtering by substring, network installs, and old tool behavior. Signals are an empty errors log and zero exit status.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-spelling.sh -->
