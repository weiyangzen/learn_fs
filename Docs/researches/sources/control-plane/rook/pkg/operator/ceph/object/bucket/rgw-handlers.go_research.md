# sources/control-plane/rook/pkg/operator/ceph/object/bucket/rgw-handlers.go

## Purpose
`rgw-handlers.go` contains RGW-specific helper operations used by the bucket provisioner for user credential lookup/creation, bucket existence checks, deterministic OBC user naming, bucket deletion, generated-user deletion, and generated-user detection.

## Important APIs, Types, and Functions
The temporary `bucket` struct groups per-request provisioner state, lib-bucket options, and parsed additional config. `(*bucket).getUserCreds()` creates or reads the bucket user depending on whether `bucketOwner` is configured. `(*Provisioner).bucketExists()` wraps `AdminOpsClient.GetBucketInfo`. `createCephUser()` gets or creates an RGW user. `genUserName()` derives the current OBC user format from namespace, name, and UID. `deleteBucket()` purges buckets through Admin Ops. `deleteOBUser()` removes only generated users. `isObcGeneratedUser()` recognizes current and historical generated-user formats while respecting explicit bucket owners.

## Control Flow, State, and Persistence
For generated users, `getUserCreds()` calls `createCephUser()`, which first attempts `GetUser` and creates only on `ErrNoSuchUser`. For explicit `bucketOwner`, it only reads an existing user. Bucket deletion uses `RemoveBucket` with purge enabled and treats `ErrNoSuchBucket` as success. For `ErrNoSuchKey`, it checks `GetBucketInfo` to distinguish not-found from other failures. User deletion reconstructs an OBC identity from the ObjectBucket claim reference, restores `bucketOwner` from additional state if present, and deletes the user only if it matches generated formats. Persistent state changes are RGW user creation, user deletion, and bucket purge/delete.

## Dependencies and Integration Points
The helpers depend on go-ceph Admin Ops, lib-bucket-provisioner ObjectBucket/ObjectBucketClaim types, ObjectBucket additional state written by `composeObjectBucket`, and logging. They are called by `Provision`, `Grant`, `Delete`, and `Revoke`.

## Risks
Both credential paths assume `user.Keys[0]` exists. `createCephUser()` logs "successfully created" even when it found an existing user. `deleteOBUser()` intentionally logs delete failures as warnings and returns nil, which favors access revocation progress over strict cleanup but can leave stale generated users. Historical generated-user matching is broad (`obc-namespace-name` prefix and `ceph-user-...` regex), so a manually named user can be treated as generated unless `bucketOwner` is recorded. The current username format includes namespace/name without truncation, relying on RGW's high user-name limit.

## Test Signals
`rgw-handlers_test.go` validates idempotent bucket deletion for `NoSuchBucket`, the `NoSuchKey` compatibility path, error return when `NoSuchKey` is not actually not-found, and generated-user detection for current, old, very old, and explicit-bucketOwner cases. Missing signals include `getUserCreds()` with empty key arrays, create-user conflict behavior, and delete-user warning-only semantics.
