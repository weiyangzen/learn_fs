# sources/control-plane/rook/pkg/operator/ceph/object/bucket/controller.go

## Purpose
`controller.go` registers and runs Rook's Object Bucket Claim provisioner integration. It watches operator ConfigMaps and CephCluster creation events, loads cluster info, and starts the lib-bucket-provisioner controller with Rook's `Provisioner` implementation.

## Important APIs, Types, and Functions
`ReconcileBucket` stores the Kubernetes client, Rook context, cluster info, operator config, and manager context. `Add()` honors the `DisableOBCEnvVar` environment variable and registers the reconciler. `newReconciler()` constructs the reconciler. `add()` creates the controller and attaches ConfigMap and CephCluster watches with custom predicates. `Reconcile()` delegates to `reconcile()` with panic recovery. `reconcile()` performs cluster checks and starts `NewBucketController()`.

## Control Flow, State, and Persistence
On reconcile, the controller fetches the CephCluster named by the request. If missing, deleting, or under data-dir cleanup policy, it returns without action. Otherwise it loads cluster info from monitor Secrets and cluster spec. It creates a `Provisioner`, constructs a lib-bucket-provisioner controller using the operator kubeconfig, starts `RunWithContext()` in a goroutine, and immediately checks whether startup reported an error. The main persistent effect is not a Kubernetes object from this controller itself, but a long-running bucket controller that later creates/updates ObjectBucket resources and claim Secrets/ConfigMaps through the library.

## Dependencies and Integration Points
The file integrates controller-runtime, Rook operator readiness helpers, Ceph cluster info loading, the lib-bucket-provisioner, ConfigMap and CephCluster predicates, and the object bucket provisioner implementation. It also relies on manager reload behavior when the OBC watch namespace setting changes.

## Risks
Every successful reconcile starts a new goroutine running a bucket controller; without an explicit guard, repeated reconciles could start multiple controllers until the shared manager context is canceled. The startup error channel is unbuffered and only checked immediately, so later goroutine errors may block when sending if no receiver remains. The CephCluster watch only triggers on create, so changes after startup depend on manager reload or other external events. Tests intentionally cannot fully mock lib-bucket-provisioner internals.

## Test Signals
`controller_test.go` covers no-op behavior when no CephCluster exists and a nominal startup path with fake cluster info and a cancelable context. It does not assert duplicate-controller prevention, delayed goroutine errors, cleanup-policy skip behavior, or disable-env behavior.
