<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_server_grpc.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_server_grpc.go

Purpose: implements the generated `SeaweedS3IamCacheServer` methods used by the filer to push unidirectional IAM cache updates into an S3 API server.

Important APIs/functions: `PutIdentity` validates and upserts an identity; `RemoveIdentity` deletes by username; `PutPolicy`, `DeletePolicy`, `GetPolicy`, and `ListPolicies` mutate or query cached IAM policy documents; `PutGroup` and `RemoveGroup` update group membership policy state. All methods are `S3ApiServer` methods and use `iam_pb` request/response types with gRPC status errors.

Control flow: each mutating RPC validates required fields, checks `s3a.iam` where needed, logs the update, invokes the corresponding `IdentityAccessManagement` cache method, and returns either an empty protobuf response or `InvalidArgument`/`Internal` status. `GetPolicy` treats lookup failure as cache miss rather than RPC failure and returns an empty response.

State and persistence behavior: this file does not persist data itself. It updates process-memory IAM caches that are backed elsewhere by filer configuration, metadata subscriptions, or credential stores. Updates are intended as cache refreshes, not authoritative writes from S3 back to the filer.

Dependencies and integration: depends on generated `iam_pb` messages, `IdentityAccessManagement` cache APIs, `glog`, and gRPC status/codes. It complements metadata-event subscription in `s3api_server.go` and embedded IAM API mutation paths.

Risks: nil `s3a.iam` checks are inconsistent: identity removal/upsert assumes IAM exists, while policy/group methods check. Cache miss in `GetPolicy` is indistinguishable from other `GetPolicy` errors. Since this is cache-only, ordering and delivery guarantees from the filer matter; stale updates could leave one S3 gateway with divergent auth behavior.

Test signals: useful tests would exercise invalid argument handling, nil IAM behavior, successful identity/policy/group cache mutation, `GetPolicy` cache miss behavior, and concurrent update/read races under the IAM cache locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_server_grpc.go -->
