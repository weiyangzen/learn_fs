# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_lifecycle_ttl.go

Purpose: this file implements a conservative fast path that converts eligible S3 lifecycle `Expiration.Days` rules into SeaweedFS volume TTL seconds for new non-versioned object writes. It avoids per-write lifecycle XML evaluation by storing a compact resolver on bucket configuration.

Important APIs/types/functions: `secondsPerDay`, `LifecycleTTLResolver`, `ttlRule`, `NewLifecycleTTLResolver`, `(*LifecycleTTLResolver).Resolve`, and `S3ApiServer.lifecycleTTLForObjectWrite`.

Control flow: resolver construction returns nil for versioned buckets or empty rules. It filters out nil, disabled, non-Expiration.Days, tag-filtered, and int32-overflowing rules. Eligible rules keep prefix, TTL seconds, and optional size bounds, then are stable-sorted by ascending TTL seconds so the shortest applicable expiration wins. `Resolve` walks rules, checks prefix and size predicates, skips unknown-size objects for size-filtered rules, and returns the first TTL seconds match or zero. The S3 server wrapper fetches bucket config and resolves against cached `LifecycleTTL`.

State and persistence behavior: this file does not persist lifecycle config; it derives hot-path state from parsed bucket config. The TTL value is later written into `filer_pb.Entry.Attributes.TtlSec` and `AssignVolumeRequest.TtlSec` by `putToFiler`, and `SeaweedFSExpiresS3` is recorded in extended metadata when TTL is applied.

Dependencies and integration points: depends on `s3lifecycle.Rule` and bucket config loading. It integrates with `populateBucketConfigDerivedFields`, `PutObjectHandler`, `PostPolicyBucketHandler`, and `putToFiler`. MPU parts and copy parts intentionally pass zero TTL and bypass this resolver.

Risks: volume TTL is irreversible and applies at storage level, so eligibility must stay conservative. Tag-filtered rules are excluded because tags can change after write. Versioned/object-lock buckets are excluded because TTL volumes could delete noncurrent versions together. Overflowing long policies are deferred to the lifecycle worker rather than capped. Size filters require accurate object size; POST policy explicitly passes file part size instead of multipart wire size.

Test signals: the paired tests cover nil/versioned behavior, tag-filter exclusion, disabled/non-expiration filtering, prefix match, overlapping shortest-expiration precedence, overflow deferral, size filters, nil receiver safety, cache-derived resolver refresh, object-lock-as-versioned, and explicit fast-path opt-in.
