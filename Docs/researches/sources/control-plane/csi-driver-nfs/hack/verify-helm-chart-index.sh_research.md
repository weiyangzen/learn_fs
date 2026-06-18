<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-helm-chart-index.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-helm-chart-index.sh

## Purpose
Checks that HTTP URLs referenced by `charts/index.yaml` are reachable or correspond to local files.

## Important APIs, Types, and Functions
The script defines `check_url()` using `curl -I -m 5` and `check_yaml()` that greps `http` lines from the index and extracts the second whitespace-delimited field. It computes `PKG_ROOT` from git and validates each URL.

## Control Flow, State, and Persistence
For each URL, a non-200 HTTP status is treated as a warning only if a corresponding local path under the repository exists; otherwise the script exits non-zero. It does not mutate the repository.

## Dependencies and Integration Points
It depends on `curl`, git, shell text parsing, and `charts/index.yaml`. It is part of Helm release verification.

## Risks and Test Signals
Risks include brittle YAML parsing with `grep`/`awk`, transient network failures, redirects or auth returning non-200, and local path derivation assuming `master` in URLs. Signals are all URLs returning HTTP 200 or resolving to existing local files.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-helm-chart-index.sh -->
