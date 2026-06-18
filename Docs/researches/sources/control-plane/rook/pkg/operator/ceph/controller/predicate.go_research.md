# sources/control-plane/rook/pkg/operator/ceph/controller/predicate.go

## Purpose
`predicate.go` defines controller-runtime predicates for Ceph CR watches, child Kubernetes object watches, peer-token Secret watches, duplicate CephCluster detection, and manager reload signaling.

## Important APIs, Types, and Functions
`WatchControllerPredicate()` reconciles creates/deletes and update events with spec diffs, deletion timestamp changes, or generation changes, while ignoring `do_not_reconcile=true`. `WatchPredicateForNonCRDObject()` filters child object events by owner reference and suppresses noisy resources. `objectChanged()` calculates patches with `k8s-objectmatcher`, normalizing resourceVersion. `isValidEvent()` drops `status` and `metadata` patch fields before deciding to reconcile. Helpers ignore canary/crash/exporter deployments, OSD status ConfigMaps, and `rook-ceph-config` Secret updates. `DuplicateCephClusters()` enforces one CephCluster per namespace. `GetSpec()` reflectively extracts a Spec field. `WatchPeerTokenSecretPredicate()` watches bootstrap peer token Secret create/update events. `ReloadManager()` sends SIGHUP to the operator process.

## Control Flow, State, and Persistence
Predicates do not persist state; they decide whether events enqueue reconciles. For CR updates, spec comparison uses `cmp.Diff()` and a `resource.Quantity` comparer. For child objects, create events are ignored, deletes reconcile only matching important children, and updates reconcile only meaningful data/spec changes after blacklists and patch trimming. Secret diffs are redacted and cephx keyring Secret updates are suppressed.

## Dependencies and Integration Points
The file integrates with controller-runtime event/predicate APIs, owner matching, Kubernetes Secrets/ConfigMaps/Deployments, Rook config and keyring annotations, Ceph CR specs, `k8s-objectmatcher`, `go-cmp`, and manager reload handling.

## Risks
Reflective `GetSpec()` will panic if called on an object without an exported Spec field? It logs and returns nil only when the field is missing after reflection; non-struct pointer shapes remain risky. Child object create events are always ignored, so recovery from missing owned objects relies on the primary CR reconcile path. Patch filtering removes all metadata changes, so meaningful label/annotation changes on child objects can be ignored except special config override handling. Peer-token predicates use substring name matching, which can match unintended Secret names. `DuplicateCephClusters()` returns true on list errors, effectively blocking reconciliation.

## Test Signals
`predicate_test.go` covers object diffing, patch trimming, canary detection, ConfigMap/Secret ignore rules, do-not-reconcile labels, and duplicate cluster detection. It does not cover the full typed predicates with create/update/delete events, peer token predicates, keyring Secret annotation suppression, or `ReloadManager()`.
