# sources/control-plane/rook/pkg/operator/k8sutil/deployment.go

Purpose: Kubernetes Deployment and CronJob utilities for image lookup, declarative update, rollout waiting, owner reference lookup, labeling, and create/update operations.

Important APIs/types/functions: `GetDeploymentImage`, `GetDeploymentSpecImage`, `UpdateDeploymentAndWait`, `WaitForDeploymentToStart`, `DeploymentNames`, `DeploymentsUpdated`, `Failure`, `Failures.CollatedErrors`, `UpdateMultipleDeployments`, `WaitForDeploymentsToUpdate`, `UpdateMultipleDeploymentsAndWait`, `deploymentIsDoneUpdating`, `progressDeadlineExceeded`, `updateDeployment`, `GetDeployments`, `DeleteDeployment`, `GetDeploymentOwnerReference`, version/label helpers, `CreateDeployment`, `CreateOrUpdateDeployment`, `CreateOrUpdateCronJob`, and `maxInt32Ptr`.

Control flow: update helpers compare desired vs current objects using `k8s-objectmatcher` patches, annotate last-applied hash, update only changed deployments, and record old observed generation. Rollout wait loops list deployments, detects progress deadline exceeded, checks observed generation plus updated/ready replicas, and times out based on the max progress deadline. Single-deployment update additionally calls a verification callback before stop and before continuing. Create/update helpers create with last-applied annotation and update on AlreadyExists.

State and persistence: reads and writes Kubernetes Deployments, CronJobs, Jobs, Pods, ReplicaSets, labels, annotations, and owner references through client-go. No durable state beyond Kubernetes objects.

Dependencies/integration: depends on client-go, Rook `clusterd.Context`, objectmatcher patch annotations, `util.RetryWithTimeout`, version label helpers, and generic deletion helpers.

Risks: rollout readiness check requires both updated and ready replicas greater than zero, which may not represent desired zero-replica deployments. `Failures.CollatedErrors` builds errors in reverse-ish order with a trailing nil string. Long waits use package globals and sleeps. Create/update directly updates full objects, so resourceVersion/spec conflicts must be managed by callers.

Test signals: `deployment_test.go` covers multi-deployment update and wait integration, no-change detection, missing deployments, rollout success, timeouts, list errors, missing listed deployments, progress deadline exceeded, and `maxInt32Ptr`.
