# sources/control-plane/juicefs-csi-driver/pkg/dashboard/utils/index.go

## Purpose
This subpackage file provides a generic creation-time ordered index for cached dashboard services and predicates for JuiceFS secrets and upgrade jobs.

## Important APIs, Types, And Functions
It defines `k8sResource`, `TimeOrderedIndexes[T]`, `NewTimeIndexes`, `Iterate`, `Length`, `AddIndex`, `RemoveIndex`, `Debug`, `IsJuiceCustSecret`, `IsJuiceSecret`, and `IsUpgradeJob`.

## Control Flow
`AddIndex` locks the list, computes a namespaced name, scans backward through existing entries, removes stale entries whose resources can no longer be fetched, deduplicates by UID, inserts after the first older resource when the new resource is newer, or pushes to the front. `Iterate` returns a channel produced by a goroutine that holds an RLock while walking front-to-back or back-to-front until context cancellation.

## State And Persistence
State is an in-memory doubly linked list protected by an RWMutex. It stores namespaced names, not resource objects, and revalidates objects through caller-provided getters.

## Dependencies And Integration Points
The index is used by cached pod, PV, PVC, Job, and Secret services. Predicate helpers encode dashboard-specific resource classification using JuiceFS labels and secret data.

## Risks
`Iterate` sends on an unbuffered channel while holding an RLock; if a consumer stops early without canceling context, the goroutine can block and hold the lock. `AddIndex` deduplicates by UID, so a deleted/recreated resource with same namespace/name and different UID can leave both until stale cleanup observes the old object as missing. Secret custom detection treats either token or metaurl data as enough.

## Test Signals
`index_test.go` verifies ordered insertion, duplicate suppression, and stale-entry removal when re-adding a resource.
