# sources/control-plane/longhorn/chart/templates/uninstall-job.yaml

Purpose: runs a Helm pre-delete hook job that invokes `longhorn-manager uninstall --force` before chart deletion.

Important APIs/types/functions: Kubernetes `batch/v1` `Job`, Helm hook annotations `pre-delete` and hook delete policy, manager image command `uninstall --force`, env `LONGHORN_NAMESPACE`, image pull secrets, priority class, service account, restartPolicy `Never`, tolerations, and node selectors.

Control flow: Helm creates the job before release deletion. The pod runs the manager uninstall command using the current namespace from fieldRef, does not restart, and is cleaned up before hook creation or after success according to hook policy.

State and persistence: the job is temporary, but the command intentionally mutates and removes Longhorn-managed state. It may interact with Longhorn's deleting confirmation setting and CR cleanup behavior.

Dependencies/integration: depends on manager image, `longhorn-service-account`, RBAC, private registry settings, and live Longhorn resources. Scheduling follows manager placement values.

Risks: `--force` makes the hook powerful; accidental Helm deletion can trigger destructive cleanup if Longhorn safeguards are satisfied. RestartPolicy `Never` plus backoffLimit means failures may require manual intervention. Image pull failure during uninstall can leave resources behind.

Test signals: uninstall dry-run rendering, controlled uninstall in a disposable cluster with and without attached volumes, image pull secret validation, and verification that expected CRs/finalizers are removed or preserved according to Longhorn uninstall policy.
