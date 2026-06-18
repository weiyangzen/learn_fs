# sources/control-plane/rook/pkg/operator/ceph/object/bucket/rgw-handlers_test.go

## Purpose
`rgw-handlers_test.go` tests RGW helper edge cases for bucket deletion idempotency and OBC-generated user detection.

## Important APIs, Types, and Functions
The file defines a small `statusError` implementing `ExitStatus()` to construct go-ceph admin errors with specific RGW codes. `TestDeleteBucket` exercises `deleteBucket()` using a fake Admin Ops client. `TestIsObcGeneratedUser` exercises `isObcGeneratedUser()` with current, historical, and explicit owner naming scenarios.

## Control Flow, State, and Persistence
`TestDeleteBucket` creates a mock Admin Ops HTTP client that returns `NoSuchBucket`, `NoSuchKey`, or other errors for bucket removal and sometimes bucket info. It asserts that missing buckets are treated as success and ambiguous `NoSuchKey` is checked through bucket info. `TestIsObcGeneratedUser` builds a provisioner with an object context, then passes synthetic OBCs and usernames through the detection helper. All state is in memory and captured in closures.

## Dependencies and Integration Points
The tests use go-ceph Admin Ops error decoding, the object `MockClient`, lib-bucket-provisioner OBC metadata, and Rook object contexts. They protect compatibility with older OBC user naming schemes that may still exist in upgraded clusters.

## Risks
The tests do not cover actual user deletion or credential lookup, only the detection logic used by deletion. The historical prefix and regex checks are deliberately permissive; tests document that behavior but cannot prevent accidental matches for manually named users unless `bucketOwner` is set. Mock HTTP paths must stay aligned with go-ceph's Admin Ops request paths.

## Test Signals
Useful signals include no error for missing buckets, correct fallback when Ceph returns `NoSuchKey` for missing buckets, error propagation when bucket info lookup fails, false for unrelated users, true for current generated names, true for old `obc-namespace-name...` names, true for very old `ceph-user-xxxxxxxx` names, and false when `bucketOwner` explicitly matches the username.
