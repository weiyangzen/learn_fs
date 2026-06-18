# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/health.go

## Purpose
This file implements periodic OSD health monitoring. It checks Ceph OSD dump state, optionally removes OSD Deployments that are out and safe to destroy, and periodically applies `require-osd-release` once all OSD daemons converge on one Ceph release.

## Important APIs, Types, and Functions
`OSDHealthMonitor` stores Kubernetes/Ceph context, cluster info, the removal policy `removeOSDsIfOUTAndSafeToRemove`, the health interval, and `lastRequireOSDRelease` cache. `NewOSDHealthMonitor()` applies the default 60 second interval or a user-specified OSD health check interval. `Start()` runs until the cluster health context is canceled or the monitoring routine map no longer contains the daemon key. `Update()` changes the removal policy.

`checkOSDHealth()` calls `checkOSDDump()` and then `checkRequireOSDRelease()`. `checkRequireOSDRelease()` reads all Ceph daemon versions, requires exactly one OSD version entry, extracts the release name, skips if it matches the cached value, and calls `client.EnableReleaseOSDFunctionality()`. `checkOSDDump()` reads `ceph osd dump`, iterates OSD status, skips healthy `up` OSDs, and when an OSD is both down and out, calls removal logic if enabled. `removeOSDDeploymentIfSafeToDestroy()` looks up the Deployment by `ceph-osd-id`, checks `ceph osd safe-to-destroy`, waits a one-hour grace time from Deployment creation, and deletes the Deployment.

## Control Flow
The monitor runs as a long-lived goroutine controlled by `monitoringRoutines` and `ClusterHealth.InternalCtx`. Errors from health checks are logged and retried rather than terminating monitoring. OSD deletion requires multiple gates: down, out, removal feature enabled, Deployment exists, Ceph reports safe-to-destroy, and the grace period elapsed.

## State and Persistence
Persistent state affected by this file is OSD Deployment deletion and Ceph's require-osd-release setting. `lastRequireOSDRelease` is in-memory and prevents redundant Ceph commands during one monitor lifetime. The grace-time decision uses Deployment creation timestamps from Kubernetes.

## Dependencies and Integration Points
The code depends on Ceph client commands for OSD dump, safe-to-destroy, daemon versions, and release enablement. It integrates with Rook controller monitoring routines, Kubernetes Deployment helpers, and Ceph version parsing.

## Risks and Edge Cases
Deletion safety relies on accurate Ceph safe-to-destroy output and Deployment timestamps. If versions never converge, require-osd-release is not applied here, but reconcile also has a one-shot path in `applyUpgradeOSDFunctionality()`. The monitor logs and continues on many errors, which is resilient but can delay cleanup or release enablement indefinitely if errors persist.

## Test Signals
`health_test.go` covers down/out safe-to-destroy Deployment deletion, monitor startup/cancel behavior, default and custom intervals, and all major `checkRequireOSDRelease()` branches including convergence, cache skip, mixed versions, version query error, and enable failure.
