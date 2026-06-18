<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-boilerplate.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-boilerplate.sh

## Purpose
Validates that source files have the expected Kubernetes license boilerplate headers.

## Important APIs, Types, and Functions
The script locates Python, installs an alternatives link to python3 if needed, sets `REPO_ROOT`, `boilerDir`, and `boiler`, runs `${boiler} --rootdir=${REPO_ROOT} --verbose`, and reports any returned file paths as failures. It defines a cleanup trap for a temporary `unitTestOut` file.

## Control Flow, State, and Persistence
It executes the Python checker, stores the list of bad files in a shell array, prints each bad path, and exits non-zero if any header is wrong. It does not repair files.

## Dependencies and Integration Points
It depends on `hack/boilerplate/boilerplate.py`, boilerplate templates, Python availability, and shell array handling. `verify-all.sh` includes it in the CI gate.

## Risks and Test Signals
Risks include attempting `update-alternatives` on systems without privileges, unused unit-test temp file plumbing, and path names with whitespace being split by shell arrays. Signals are "Done" with no listed files, or explicit "Boilerplate header is wrong for" messages.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-boilerplate.sh -->
