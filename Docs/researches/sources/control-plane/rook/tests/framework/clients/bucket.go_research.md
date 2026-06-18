# sources/control-plane/rook/tests/framework/clients/bucket.go

Purpose: `BucketOperation` wraps ObjectBucketClaim, bucket storage class, credentials, quota, and notification checks for Rook RGW object bucket integration tests.

Important APIs/types/functions: constructor `CreateBucketOperation`; resource methods `CreateBucketStorageClass`, `DeleteBucketStorageClass`, `CreateObc`, `CreateObcNotification`, `DeleteObc`, `UpdateObc`, and notification update variants; validators `CheckOBC`, `CheckOBMaxObject`, and `CheckBucketNotificationSetonRGW`; credential readers `GetAccessKey` and `GetSecretKey`.

Control flow: create/update/delete methods render manifests from `CephManifests` and delegate to kubectl via `K8sHelper.ResourceOperation`. `CheckOBC` checks OBC/Secret/ConfigMap existence, validates Bound phase when requested, confirms `spec.objectBucketName`, then verifies the ObjectBucket claim reference. Credential methods read Kubernetes secrets using JSONPath and base64-decode the result. RGW notification validation builds an S3 agent from OBC credentials and calls AWS SDK `GetBucketNotificationConfiguration`.

State and persistence behavior: persistent state includes storage classes, OBCs, ObjectBuckets, Secrets, ConfigMaps, and bucket notification configuration in RGW. No local state is persisted.

Dependencies and integration points: integrates Kubernetes object bucket APIs, Rook object operator S3 agent, AWS SDK v2 S3 client, test manifests, and `TestClient` object endpoint lookup.

Risks: base64 decode errors are ignored. `CheckOBC` treats any `GetResource` error as missing, hiding authorization/API failures. Access and secret keys are logged in notification checks, which is acceptable only for isolated test environments. RGW notification checks assume non-nil notification IDs.

Test signals: OBC created/bound/deleted checks, generated Secret/ConfigMap validation, ObjectBucket claim reference checks, maxObjects propagation, and real RGW notification configuration retrieval.
