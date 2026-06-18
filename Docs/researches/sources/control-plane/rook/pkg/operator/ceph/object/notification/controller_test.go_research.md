# sources/control-plane/rook/pkg/operator/ceph/object/notification/controller_test.go

## Purpose
`notification/controller_test.go` verifies CephBucketNotification reconciliation and object-store resolution from ObjectBuckets.

## Important APIs, Types, and Functions
`mockSetup()` creates fake cluster context, schemes, monitor Secret, and replaces `createNotificationFunc`, `getAllNotificationsFunc`, and `deleteNotificationFunc`. `testReconciler()` runs `ReconcileNotifications`, and `verifyEvents()` checks recorder output. `TestCephBucketNotificationController` covers topic/cluster readiness paths. `TestCephBucketNotificationControllerWithOBC` covers selected OBCs and ObjectBucket provisioning. `TestGetCephObjectStoreName` exercises legacy bucket-host parsing through the controller wrapper.

## Control Flow, State, and Persistence
Tests use fake controller-runtime clients and fake Kubernetes clients. Mocked provisioner functions record notification creation/deletion in slices. Event verification drains a fake recorder. OBC tests mutate OBC status from pending to bound and set `Spec.ObjectBucketName` before adding an ObjectBucket.

## Dependencies and Integration Points
The tests register Ceph, ObjectBucket, and Kubernetes schemes and use Rook test clients. They validate notification controller interactions with topic status, CephCluster readiness, monitor secret loading, OBC label selection, ObjectBucket lookup, and object-store DNS parsing.

## Risks and Test Signals
Signals include requeue without creation for missing topic/cluster/topic ARN/OB, success with no OBCs, creation when a bound OBC has an ObjectBucket, and parsing failures for malformed bucket hosts. Gaps include object-store mismatch validation, AdditionalState-based store resolution, createNotification errors, status conflict behavior, and companion OBC label controller behavior beyond shared mocks.
