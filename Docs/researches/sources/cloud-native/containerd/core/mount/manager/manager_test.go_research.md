<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/manager_test.go -->
# sources/cloud-native/containerd/core/mount/manager/manager_test.go

Purpose: unit and local integration tests for the Bolt-backed mount manager using fake handlers and temporary Bolt databases.

Important APIs/types/functions: `TestManager`, `noopHandler`, `errOnceHandler`, `TestGC`, `checkGCActive`, `TestActivateAlreadyExists`, `TestActivateStaleIncomplete`, `TestInfo`, `TestInfoSystemMounts`, `TestActivateConcurrentSameName`, and `TestClose`.

Control flow: tests activate mounts with no handlers, fake handlers, labels, and mixed handled/system types; inspect returned and persisted activation info; drive metadata collection manually; and assert deactivation/cleanup behavior. The stale test writes a partial Bolt bucket directly and ensures a later activation replaces it and removes its target directory.

State and persistence: validates bbolt bucket lifecycle, lease/backref effects, target directory cleanup, active/system mount serialization, and manager close closing root handles plus the Bolt DB.

Dependencies and integration points: uses `metadata.CollectionContext`, `gc.Node`, `namespaces`, `errdefs`, and bbolt. Fake handlers emulate plugin-managed mounts without performing real kernel mounts except in the root-required base `TestManager`.

Risks covered: duplicate activation returns `ErrAlreadyExists`; same-name concurrent activations are serialized; GC tolerates an unmount error then succeeds later; stale incomplete records are not mistaken for valid activations.

Test signals: broad behavioral coverage for manager state transitions. Open TODOs note missing direct tests for `Deactivate`, `Sync`, and some collection methods; `Sync`/`Update` are currently not implemented.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/manager_test.go -->
