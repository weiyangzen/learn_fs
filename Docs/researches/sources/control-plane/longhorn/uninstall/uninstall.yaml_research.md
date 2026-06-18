# sources/control-plane/longhorn/uninstall/uninstall.yaml

## Purpose
Kubernetes manifest for a Longhorn uninstall job. It creates a service account, broad ClusterRole, ClusterRoleBinding, and batch Job that runs `longhorn-manager uninstall --force` in namespace `longhorn-system`.

## Important APIs and Resources
Resources include `ServiceAccount longhorn-uninstall-service-account`, `ClusterRole longhorn-uninstall-role`, `ClusterRoleBinding longhorn-uninstall-bind`, and `Job longhorn-uninstall`. The ClusterRole grants `*` verbs over CRDs, core pods/PVs/PVCs/nodes/configmaps/secrets/services/endpoints, apps workloads, batch jobs/cronjobs, pod disruption budgets, storage resources, leases, and many Longhorn CRD resources. Webhook configurations get `get` and `delete`. PriorityClasses get `watch` and `list`.

## Control Flow
When applied, Kubernetes creates RBAC and starts the job. The job runs container image `longhornio/longhorn-manager:master-head` with command `longhorn-manager uninstall --force`, `LONGHORN_NAMESPACE=longhorn-system`, `activeDeadlineSeconds: 900`, `backoffLimit: 1`, and `restartPolicy: Never`.

## State and Persistence
Applying this manifest creates cluster-wide RBAC and a namespaced job. The job is intentionally destructive: it deletes Longhorn resources and related cluster resources according to manager uninstall logic. The manifest itself is static but should be updated by `scripts/update-uninstall-manifest.py` as CRDs change.

## Dependencies and Integration Points
Depends on Kubernetes batch/RBAC APIs, Longhorn manager image availability, and the Longhorn CRD/resource model. Integrates with uninstall documentation and release manifests.

## Risks
RBAC is intentionally broad and cluster-scoped. The image tag `master-head` is unsuitable for stable releases unless rewritten. Forced uninstall can remove data-plane resources; operators must understand data-loss implications. Longhorn CRD list can drift if not regenerated from manifests.

## Test Signals
YAML parse and Kubernetes dry-run validation are basic signals. In a disposable cluster, apply the manifest and verify the job completes, Longhorn resources are removed, and no unrelated resources are deleted. Confirm RBAC resource list matches generated CRDs.
