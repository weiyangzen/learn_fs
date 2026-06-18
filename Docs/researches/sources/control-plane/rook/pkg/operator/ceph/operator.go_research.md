# sources/control-plane/rook/pkg/operator/ceph/operator.go

## Purpose

This file defines the top-level Ceph operator process lifecycle. It creates operator configuration, initializes the cluster controller, starts and restarts the CRD manager, responds to process signals, reloads configuration on SIGHUP, and decides whether the operator watches only its namespace or all namespaces.

## Important APIs, Types, and Functions

- Package globals include `ImmediateRetryResult`, `ShutdownSignals`, `opManagerContext`, `opManagerStop`, and `mgrCRDErrorChan`.
- `Operator` stores the shared clusterd context, registered custom resources, operator config, and cluster controller.
- `New(context, rookImage, serviceAccount)` constructs an operator with cluster CR resource registration and a `cluster.ClusterController`.
- `Run()` installs signal handling, starts the CRD manager, watches SIGHUP for config reload, watches manager errors, and exits on shutdown signals.
- `runCRDManager()` creates a new cancellable manager context, applies operator settings from ConfigMap, updates namespace watch scope, assigns the context to the cluster controller, starts the CRD manager goroutine, and logs goroutine count after one minute.
- `namespaceToWatch()` reads `ROOK_CURRENT_NAMESPACE_ONLY` from operator settings and sets `config.NamespaceToWatch` to the operator namespace or `corev1.NamespaceAll`.

## Control Flow

`New` sets `OperatorNamespace` from the pod namespace environment variable, stores the image/service account, and creates the cluster controller. `Run` creates a root process context bound to interrupt and SIGTERM. It starts the CRD manager once, then loops over three event sources: shutdown, SIGHUP reload, and CRD manager error. Shutdown cancels the manager and exits cleanly. SIGHUP cancels the current manager and starts a fresh one, which also cancels active orchestration through the shared `opManagerContext`. A manager error is wrapped and returned.

`runCRDManager` recreates the manager error channel and operator manager context every time it is called. It panics if operator settings cannot be loaded. It updates namespace scope before starting the manager, and sets `clusterController.OpManagerCtx` so background monitoring goroutines can stop with manager reload/shutdown.

## State and Persistence Behavior

The file manages in-memory process state only: contexts, cancel functions, error channels, namespace watch config, and cluster-controller context. It reads Kubernetes ConfigMap-backed operator settings through `k8sutil.ApplyOperatorSettingsConfigmap`, but does not persist Kubernetes objects itself.

## Dependencies and Integration Points

It integrates with `clusterd.Context`, the Ceph cluster controller, Rook controller config, `k8sutil` operator settings, process signals, controller-runtime reconcile result conventions, and Kubernetes namespace constants. The missing `startCRDManager` implementation is in another file and is the actual controller registration path.

## Risks and Edge Cases

- Package-level manager context globals make lifecycle state process-wide and require careful ordering; `Run` assumes `runCRDManager` has initialized `opManagerStop` before shutdown.
- `runCRDManager` panics on settings ConfigMap load failure instead of returning an error.
- SIGHUP reload cancels all orchestrations, which is intentional but disruptive.
- There is no explicit signal stop for the SIGHUP channel in this file.

## Test Signals

`operator_test.go` only tests `New`: non-nil operator, cluster controller, resources, context identity, and registration of the cluster resource. `Run`, signal handling, manager reload, and namespace watch selection are not covered here.
