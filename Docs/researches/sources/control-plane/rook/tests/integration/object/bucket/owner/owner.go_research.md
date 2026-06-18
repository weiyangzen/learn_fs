# sources/control-plane/rook/tests/integration/object/bucket/owner/owner.go

Focused object-bucket-owner integration test package. It validates the `bucketOwner` OBC additional config path: creating buckets owned by existing CephObjectStoreUsers, changing owners, preserving quotas, sharing owners across buckets, rejecting nonexistent owners, and cleanup.

`WaitForPodLogContainingText` streams logs from the first pod matching a selector. `TestObjectBucketClaimBucketOwner` creates a namespace, bucket StorageClass, two users (`osu1` without quotas and `osu2` with quotas), valid OBCs, and a bogus-owner OBC. It waits for OBC/OB bound states, checks OBC/OB state and backend RGW bucket owner through go-ceph admin API, updates/removes/re-adds owners, verifies user quotas are unchanged, deletes OBCs while users remain, verifies bogus-owner Pending behavior and missing backend user, then deletes users/storage class/namespace.

State includes Namespace, StorageClass, CephObjectStoreUsers, ObjectBucketClaims, ObjectBuckets, backend RGW buckets/users/quotas, and OBC `AdditionalConfig` updates. Dependencies are Rook Ceph APIs, lib-bucket-provisioner APIs, Kubernetes core/storage clients, go-ceph RGW admin, shared admin client helper, installer, K8s helper, and capnslog.

Risks: `WaitForPodLogContainingText` returns nil if logs end without finding text because it does not track a found flag; expected bogus-user log text appears to use a different prefix than the configured default; some bucket lookups assume OBC name equals bucket name; TLS is skipped. Signals include OBC/OB Bound, owner state propagation, RGW bucket owner, preserved user quotas, user persistence after OBC deletion, bogus OBC Pending, `ErrNoSuchUser`, operator log text, and cleanup absence checks.
