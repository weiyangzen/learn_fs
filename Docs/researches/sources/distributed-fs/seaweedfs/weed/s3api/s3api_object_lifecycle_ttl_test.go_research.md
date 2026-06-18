# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_lifecycle_ttl_test.go

Purpose: this file validates the lifecycle TTL fast-path resolver and the bucket-config derived-field wiring that enables or disables it. It documents safety constraints around versioning, object lock, mutable tags, overflow, size filters, and stale cache refresh.

Important APIs/types/functions: helper `enabledRule` builds enabled `s3lifecycle.Rule` values, `mustResolver` constructs non-versioned resolvers, and tests call `NewLifecycleTTLResolver`, `Resolve`, and `populateBucketConfigDerivedFields`. Benchmarks measure nil, one-rule, and five-rule no-match resolver paths.

Control flow: constructor tests assert nil for empty rules and versioned buckets, exclusion of tag-filtered/disabled/non-expiration rules, and preservation of plain eligible rules. Resolve tests check prefix matching, overlapping shortest-expiration precedence, overflow deferral to the worker, overflow skipping while shorter rules still fire, size greater-than behavior, unknown-size skip, and nil receiver zero. Derived-field tests mutate `BucketConfig.Entry.Extended` lifecycle XML and opt-in flags across add/replace/delete transitions to ensure resolver state refreshes and does not linger after lifecycle removal.

State and persistence behavior: tests simulate persisted bucket config through `filer_pb.Entry.Extended` keys: lifecycle XML, object lock enabled flag, and `ExtLifecycleTtlFastPathKey`. They do not write filer state, but they validate the in-memory cache object (`BucketConfig.LifecycleTTL`) that later determines persisted object TTL on writes.

Dependencies and integration points: depends on `s3lifecycle`, `filer_pb`, `s3_constants`, and bucket config parsing in `populateBucketConfigDerivedFields`. The tests directly protect `PutObjectHandler` and `PostPolicyBucketHandler` from applying stale or unsafe volume TTL.

Risks: benchmarks are micro-level and do not cover bucket-config cache invalidation under concurrent metadata subscription updates. XML parsing coverage is narrow but targets the derived resolver transitions most likely to cause irreversible stale TTL application. Time is not used directly in resolver tests, making them deterministic.

Test signals: strong safety signal for no fast path unless explicitly opted in, no fast path for object-lock/versioned buckets, no tag-filter TTL, shortest expiration wins, long retention policies are not capped, and stale resolver removal after lifecycle XML deletion.
