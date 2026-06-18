# sources/control-plane/juicefs-csi-driver/pkg/dashboard/batch.go

## Purpose
`batch.go` implements dashboard endpoints and helpers for smooth upgrade batch jobs that upgrade mount pods through a Kubernetes Job and ConfigMap-backed batch plan.

## Important APIs, Types, And Functions
Important types are `ListJobResult`, `UpgradeJob`, `PodDiff`, and `ListDiffPodResult`. Key functions include `createUpgradeJob`, `listUpgradeJobs`, `getUpgradeJob`, `updateUpgradeJob`, `deleteUpgradeJob`, `getUpgradeJobLog`, `watchUpgradeJobLog`, `NewUpgradeJob`, `genPodDiffs`, `GenPodDiffs`, `GenUpgradeJobName`, `GenUpgradeConfig`, `getAllUpgradeConfig`, `getPodOfUpgradeJob`, `CanDoAction`, and `doActionInUpgradeJob`.

## Control Flow
Job creation validates smooth upgrade is enabled, binds request body filters, selects upgrade-eligible mount pods, computes config diffs, creates a batch ConfigMap, creates a dashboard Job, then sets the ConfigMap owner reference to the Job. Listing joins Jobs from `JobService` with loaded batch configs. Get-job loads the Job/config, lists current batch pods, recomputes diffs, and paginates them. Update-job validates action state transitions and sends POSIX signals to PID 1 in the job pod through Kubernetes exec. Log endpoints either return current pod logs or stream them to a websocket after waiting for the job pod to leave Pending.

## State And Persistence
Persistent state is the batch upgrade ConfigMap, the Kubernetes Job, its pod, and Job-owned ConfigMap references. Runtime state includes computed diff maps for PVs/PVCs/secrets/nodes. `NewUpgradeJob` uses `DASHBOARD_IMAGE` and optionally `JUICEFS_CSI_DASHBOARD_SA`.

## Dependencies And Integration Points
This file integrates pod, PV, PVC, secret, and job services; `config.BatchConfig`; `config.GetDiffWithNode`; Kubernetes batch/core APIs; SPDY remotecommand; websocket log piping; and dashboard utilities for pod classification and log streaming.

## Risks
Several paths assume labels and config references exist on Jobs. `getUpgradeJobLog` lists the job pod but calls `GetLogs(jobName, ...)`, which relies on pod name matching job name and can break if Kubernetes creates a suffixed pod name. Actions send signals to PID 1 in the upgrade container, so image entrypoint behavior is part of the API contract. Diff generation returns errors when any pod setting cannot be reconstructed, which can block job creation.

## Test Signals
No direct tests are included. Test coverage should focus on `CanDoAction`, `GenPodDiffs` map joins, generated Job spec, and log/action behavior against fake or envtest Kubernetes clients.
