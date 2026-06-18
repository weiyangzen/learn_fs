# sources/control-plane/longhorn/chart/templates/postupgrade-job.yaml

Purpose: runs a Helm post-upgrade hook job that invokes `longhorn-manager post-upgrade` after chart upgrade.

Important APIs/types/functions: Kubernetes `batch/v1` `Job`, Helm hook annotations `post-upgrade` and `hook-delete-policy`, `activeDeadlineSeconds: 900`, `backoffLimit: 1`, manager image command, `POD_NAMESPACE`, timezone env, image pull secrets, priority class, service account, tolerations, and node selectors.

Control flow: Helm creates the job after an upgrade. The pod runs the manager image with `post-upgrade`, restarts on failure, and is deleted before future hook creation or after success according to hook policy.

State and persistence: the hook job is temporary cluster state, but the command can perform persistent Longhorn upgrade migrations or cleanup. Successful hook resources are deleted, so logs may be transient.

Dependencies/integration: depends on the manager image, `longhorn-service-account`, RBAC permissions, namespace fieldRef, private registry configuration, and manager upgrade implementation. Scheduling follows manager toleration and node-selector values.

Risks: failure blocks or degrades Helm upgrade flows, and hook deletion can remove diagnostics after success. `activeDeadlineSeconds` may be too short on very large or unhealthy clusters. Image pull or scheduling failures prevent post-upgrade reconciliation.

Test signals: `helm upgrade --dry-run` should render the hook; real upgrade tests should verify the job starts, completes within deadline, uses expected image pull secrets, and leaves Longhorn resources in the target version state.
