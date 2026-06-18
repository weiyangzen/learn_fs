# sources/control-plane/rook/pkg/operator/ceph/controller.go

## Purpose
This file defines the controller-runtime reconciler for the Rook Ceph operator configuration ConfigMap. It watches `rook-ceph-operator-config` and applies changes to operator-wide runtime settings without requiring a full operator restart for every setting.

## Important APIs, Types, and Functions
`ReconcileConfig` stores the controller-runtime client, shared `clusterd.Context`, `OperatorConfig`, and operator manager context. `Add()` registers the controller. `add()` creates the controller named `rook-ceph-operator-config-controller` and watches ConfigMaps with `operatorSettingConfigMapPredicate()`. `Reconcile()` wraps panics with `opcontroller.RecoverAndLogException()`. `reconcile()` applies operator settings, refreshes Ceph command timeout, log level, discovery daemon state, loop-device allowance, host-network enforcement, revision history limit, and OBC extra config field allowance. `reconcileDiscoveryDaemon()` starts or stops the discovery DaemonSet.

## Control Flow, State, and Persistence
On a matching ConfigMap event, the reconciler loads operator settings through `k8sutil.ApplyOperatorSettingsConfigmap()`, then updates several process-global settings in memory. Some settings also cause cluster-side persistence: discovery daemon start/stop creates or deletes Kubernetes DaemonSet resources. Other settings mutate package globals used by later reconciles.

## Dependencies and Integration Points
The controller depends on controller-runtime manager/controller/source/handler primitives, `k8sutil` operator settings, `discover.New()`, shared `clusterd.Context.Clientset`, and the helper globals in `pkg/operator/ceph/controller`. Every Ceph CR controller indirectly observes these settings through shared process state.

## Risks
Most effects are global mutable state, so ordering and concurrency matter if reconciles overlap. The code only applies the operator settings ConfigMap when the request name exactly matches `OperatorSettingConfigMapName`, but still refreshes settings for any watched request that passes the predicate. Discovery daemon operations depend on manager context lifetime and operator namespace/image/service account values. Panics are logged but not converted into explicit reconcile errors by `RecoverAndLogException()`.

## Test Signals
No direct tests are listed for this file in the subset. Related coverage exists in `controller_utils_test.go` for individual setting parsers, but controller registration, predicate selection, discovery daemon side effects, and end-to-end ConfigMap reconciliation need integration tests.
