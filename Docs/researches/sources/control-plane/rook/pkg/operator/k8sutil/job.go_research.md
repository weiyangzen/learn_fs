# sources/control-plane/rook/pkg/operator/k8sutil/job.go

Purpose: helpers for replaceable Kubernetes Jobs, batch job deletion, and Rook version labeling on Jobs.

Important APIs/types/functions: `RunReplaceableJob`, `DeleteBatchJob`, and `AddRookVersionLabelToJob`.

Control flow: `RunReplaceableJob` checks for an existing job. If it exists and is active and caller did not request deletion, it leaves it running. Otherwise it deletes the old job with wait, then creates the new job. `DeleteBatchJob` foreground-deletes with zero grace, ignores NotFound, optionally polls up to 30 times at 3 seconds for NotFound, and logs timeout as warning without returning an error. `AddRookVersionLabelToJob` initializes labels and delegates to the shared rook-version label sanitizer.

State and persistence behavior: creates/deletes Kubernetes Jobs and mutates Job labels in memory before persistence by callers.

Dependencies/integration: client-go BatchV1 Jobs, Kubernetes API error helpers, and deployment/k8sutil label helpers.

Risks: delete wait timeout is non-fatal, so a later create can still fail if the old job remains. Existing-job get errors other than NotFound are only warned before create is attempted. The wait loop is fixed at up to roughly 90 seconds.

Test signals: no direct tests in this subset; `cmdreporter.Run` depends on this behavior.
