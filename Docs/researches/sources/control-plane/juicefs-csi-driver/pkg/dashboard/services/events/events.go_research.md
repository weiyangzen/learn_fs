# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/events/events.go

## Purpose
This service lists Kubernetes events associated with dashboard resources by involved object UID.

## Important APIs, Types, And Functions
It defines `EventService`, `eventService`, `NewEventService`, `EventResource`, constants for Pod/PVC/PV/Job/StorageClass, and `ListEvents`.

## Control Flow
`ListEvents` calls the typed Kubernetes CoreV1 Events client for the supplied namespace and filters with field selector `involvedObject.uid=<uid>`. The resource kind is passed in `ListOptions.TypeMeta`, but the effective filter is the UID.

## State And Persistence
The service is read-only and keeps only a `k8sclient.K8sClient` pointer.

## Dependencies And Integration Points
It is used by pod and PV/PVC handlers to show event timelines. It depends on Kubernetes legacy core/v1 Events and field selectors.

## Risks
Events are namespace-scoped except PV events may be cluster-ish in presentation; callers pass empty namespace for PVs. TypeMeta in list options does not filter events, so UID uniqueness is the real selector. Clusters using events.k8s.io/v1 only through aggregation may need compatibility consideration.

## Test Signals
No tests are present. A fake-client test could verify namespace and field selector usage.
