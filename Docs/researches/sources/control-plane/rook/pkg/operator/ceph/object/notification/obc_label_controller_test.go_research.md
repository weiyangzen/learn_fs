# sources/control-plane/rook/pkg/operator/ceph/object/notification/obc_label_controller_test.go

Purpose: verifies the OBC label notification controller behavior using fake Kubernetes objects and mocked notification operations.

Important APIs/types: helper constructors `createOBResources`, `createBucketNotification`, and `setNotificationLabels`; main test `TestCephBucketNotificationOBCLabelController`; test constants for alternate provisioner identity. The test relies on package-level test hooks such as `getAllNotificationsFunc`, `createNotificationFunc`, and `deleteNotificationFunc` configured by shared `mockSetup`/`resetValues` helpers elsewhere in the package.

Control flow: each subtest builds a runtime object set containing a ready `CephCluster`, OBC/OB objects, optional notification CRs, and optional topic CRs. It invokes `testOBCLabelReconciler`, then asserts reconcile result, error presence, whether notification listing was called, and created/deleted notification ID slices. Cases cover waiting for an object bucket name, missing object bucket, missing notification CR, missing topic ARN, successful provisioning, already existing labels, removing labels, multiple labels, simultaneous stale and new IDs, and non-Ceph provisioner filtering.

State and persistence: all state is in fake API objects and in-memory test globals for created/deleted notifications and event capture. The test intentionally mutates a shared OBC from pending to bound before later cases, mirroring controller readiness progression.

Dependencies and integration points: depends on kube-object-storage API types, Rook Ceph CRDs, fake runtime object clients, the topic status ARN contract, and event verification helpers from the notification test suite.

Risks: tests validate high-level reconcile outcomes but not actual AWS/Ceph request serialization, label map iteration order, duplicate labels, or mismatched label key/value warning behavior. Shared mutable objects and globals require `resetValues` to avoid test coupling.

Test signals: strong unit coverage exists for the label-to-notification diff and readiness paths. The main missing signal is direct coverage of predicate behavior and delete failure retry behavior.
