<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/utils.sh -->
## sources/control-plane/ceph-csi/scripts/utils.sh

Purpose: shared Kubernetes retry helper for shell scripts.

APIs and control flow: `kubectl_retry action args...` runs `kubectl`, capturing stdout/stderr to temp files. It retries up to `KUBECTL_RETRY` with delay, logs diagnostics to stderr, ignores `AlreadyExists`/warnings for create and `NotFound`/warnings for delete, then emits captured stdout/stderr and returns final status.

State and persistence: creates temporary files named `rook-kubectl-stdout.*` and `rook-kubectl-stderr.*`, removed at end.

Dependencies: kubectl, mktemp, grep, sleep.

Integration points: used by operator, Helm, snapshot, Rook, and Minikube scripts to tolerate transient Kubernetes API failures and idempotent create/delete.

Risks: temp files are in current directory and can remain if interrupted. Only create/delete have special idempotency handling. stdout is appended through retries, so callers parsing stdout can receive output from failed attempts plus success.

Test signals: no unit tests; operational scripts depend on it.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/utils.sh -->
