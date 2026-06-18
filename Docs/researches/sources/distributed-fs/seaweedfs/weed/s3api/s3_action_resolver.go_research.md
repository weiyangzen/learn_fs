# sources/distributed-fs/seaweedfs/weed/s3api/s3_action_resolver.go

Purpose: resolves coarse handler actions plus HTTP request context into precise AWS S3 IAM action strings for bucket policy and IAM authorization.

Important APIs and functions: `ResolveS3Action` is the public entry point. Internals include `bucketQueryActions`, `resolveFromQueryParameters`, `resolveObjectLevelAction`, `resolveBucketLevelAction`, and `mapBaseActionToS3Format`.

Control flow: nil requests fall back to base-action mapping. Otherwise, query parameters have highest priority, distinguishing multipart upload, ACL, tagging, object attributes, version IDs, version listing, bucket policy/CORS/lifecycle/versioning/notification/object-lock, location, retention, legal hold, and batch delete. If no query-specific action matches, object-level or bucket-level method/resource logic maps methods such as GET, PUT, DELETE, and POST. Final fallback maps legacy actions like `Read`, `Write`, `List`, and `Admin` to S3 action strings.

State and persistence: stateless except for the package-level query action map.

Dependencies and integration: uses `net/http`, `net/url`, `strings`, and `s3_constants`. It is intended to unify bucket policy and IAM integration action resolution.

Risks: query parameter ordering matters; `attributes` intentionally precedes `versionId`. Empty object key and object value `"/"` are treated as bucket-level. Missing resolver coverage for a future S3 subresource will fall back to a coarse action, possibly weakening fine-grained policy behavior.

Test signals: resolver tests and granular security tests cover service-prefix passthrough, STS passthrough, attributes-before-versionId, DELETE mapping, ACL/tagging/multipart/bucket-policy precision, and coarse fallback behavior.
