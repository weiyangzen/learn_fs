# sources/control-plane/juicefs-csi-driver/pkg/controller/pv_controller.go

## Purpose
`PVController` watches JuiceFS CSI persistent volumes to discover `NodePublishSecretRef` secrets and trigger initialization of enterprise `initconfig` data for those secrets.

## Important APIs, Types, And Functions
The file defines the package-global `watchedSecrets sync.Map`, `PVController`, `NewPVController`, `Reconcile`, `shouldPVInQueue`, and `SetupWithManager`. `Reconcile` stores `namespace/name` secret keys and calls `refreshSecretInitConfig`.

## Control Flow
On reconcile, the controller fetches the PV by name, ignores not-found errors, checks for a CSI source with a node publish secret, stores that secret in `watchedSecrets`, and refreshes the secret init config. Queue predicates accept only JuiceFS CSI PVs with `NodePublishSecretRef` whose secret is not already watched. During setup, it lists all PVs once and pre-populates `watchedSecrets`, then registers create/update watches for PVs.

## State And Persistence
`watchedSecrets` is in-memory process state shared with `SecretController`. The persistent side effect is indirect: `refreshSecretInitConfig` may update Kubernetes Secret data and annotations. A controller restart rebuilds the watch set from current PVs.

## Dependencies And Integration Points
It depends on controller-runtime watches/predicates, `k8sclient.K8sClient`, corev1 PVs, and `config.DriverName`. It is coupled to `secret_controller.go` through `watchedSecrets` and `refreshSecretInitConfig`.

## Risks
Because updates are skipped once a secret is watched, a PV changing to a different secret may not refresh unless the predicate admits the new key. The process-global map has no deletion path for unused secrets, so long-running controllers can retain stale keys. Setup does not call `refreshSecretInitConfig` for pre-existing PVs because it only stores keys, so refresh behavior depends on later secret reconciles or PV events.

## Test Signals
There is no direct test in this subset. Useful coverage would assert predicate behavior, initial PV scan behavior, and interaction with `SecretController` for first-time and changed secret references.
