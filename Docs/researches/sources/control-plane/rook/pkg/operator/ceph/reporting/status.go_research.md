# sources/control-plane/rook/pkg/operator/ceph/reporting/status.go

Purpose: thin helpers for writing object status and status conditions through controller-runtime clients.

Important APIs/types/functions: `UpdateStatus` and `UpdateStatusCondition`.

Control flow: `UpdateStatus` attempts `client.Status().Update` with a background context and falls back to full-object `client.Update` only when Status update returns NotFound. `UpdateStatusCondition` applies each new condition through `cephv1.SetStatusCondition` to the object condition slice, then calls `UpdateStatus`, wrapping errors with kind/name context.

State and persistence behavior: persists the target object's status subresource or, for not-yet-created status behavior, the whole object. Mutates the in-memory object condition slice before writing.

Dependencies/integration: uses controller-runtime client, Kubernetes NotFound detection, Ceph condition helpers, and the `statusConditionGetter` interface from `reporting.go`.

Risks: uses `context.Background()` instead of caller-provided context, so status writes are detached from reconcile cancellation. The fallback only covers NotFound from status update, not status-subresource unsupported errors unless fake clients represent them as NotFound. Condition ordering and replacement are delegated to `cephv1.SetStatusCondition`.

Test signals: `status_test.go` checks status update when status is initially nil, ordinary phase update, adding one condition, adding two condition types, and replacing an existing condition.
