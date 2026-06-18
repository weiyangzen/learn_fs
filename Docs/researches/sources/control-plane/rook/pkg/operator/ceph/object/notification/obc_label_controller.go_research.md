# sources/control-plane/rook/pkg/operator/ceph/object/notification/obc_label_controller.go

Purpose: implements a controller-runtime reconciler that treats `bucket-notification-*` labels on `ObjectBucketClaim` resources as the desired bucket notification set for the backing Ceph RGW bucket.

Important APIs/types: `ReconcileOBCLabels`, `obcPredicate`, `addOBCLabelReconciler`, `Reconcile`, `reconcile`, and `addNewNotification`. Constants define the notification label prefix and the expected ceph bucket provisioner labels. The code uses helper functions from the notification controller file, including `getCephObjectStoreName`, `getReadyCluster`, and `validateObjectStoreName`, plus requeue constants for object bucket, topic, notification, and delete readiness.

Control flow: the predicate reconciles creates/deletes and updates where labels or `Spec.ObjectBucketName` change, while respecting `do_not_reconcile` on updates. Reconcile fetches the OBC, ignores not-found and deleted objects, requeues until the OBC has produced an object bucket name, fetches the `ObjectBucket`, ignores non-Ceph provisioned buckets, derives the object store, loads ready Ceph cluster state, and builds a notification `provisioner`. It lists existing RGW notification IDs, extracts desired IDs from OBC labels where key suffix and value match, deletes existing IDs absent from labels, then attempts to add each desired notification by fetching `CephBucketNotification`, resolving its `CephBucketTopic`, validating object store identity, and calling the S3 provisioning path.

State and persistence: desired state is encoded in OBC labels; actual state is in RGW bucket notification configuration; dependent state is in `ObjectBucket`, `CephBucketNotification`, `CephBucketTopic`, and `CephCluster` objects. The controller emits Kubernetes events via the recorder and returns requeue results for eventual consistency.

Dependencies and integration points: integrates kube-object-storage OBC/OB CRDs, Rook Ceph CRDs, object bucket helpers, topic status ARN lookup, controller-runtime watches, Rook cluster readiness loading, and notification S3 provisioning/deletion functions that are overrideable in tests.

Risks: label parsing is intentionally strict but order over map iteration is nondeterministic; create errors stop the loop after prior deletes may already have occurred; delete failures are aggregated only as a retry boolean; `strings.Contains` provisioner matching could match unexpected provisioner strings; missing object store/topic readiness is handled by requeue but still reports errors for some not-ready paths.

Test signals: `obc_label_controller_test.go` exercises missing OB, not-ready bucket, missing notification/topic, successful single and multiple creates, deletes for absent labels, mixed delete/create, and ignoring OBCs from another provisioner. Tests use overrideable notification functions and fake clients.
