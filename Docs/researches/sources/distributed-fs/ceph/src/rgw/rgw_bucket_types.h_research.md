# sources/distributed-fs/ceph/src/rgw/rgw_bucket_types.h

Purpose: declares fundamental serialized bucket identity, placement, and shard types that must remain independent of RGW-only contexts.

Important APIs/types/functions: `rgw_bucket_key`, `rgw_bucket`, `std::hash<rgw_bucket>`, stream operator for `rgw_bucket`, `rgw_bucket_placement`, `rgw_bucket_shard`, `std::hash<rgw_bucket_shard>`, and encode/decode declarations for shards.

Control flow: `rgw_bucket::match()` treats an empty bucket id on either side as wildcard. `encode()` writes version 10 fields with optional explicit placement; `decode()` supports legacy versions with old pool fields, numeric ids through v3, tenant from v8, and explicit-placement flag from v10. `get_namespaced_name()` uses `tenant/name` when tenant exists.

State/persistence: `rgw_bucket` is a core persisted identifier with tenant, name, marker, bucket id, and explicit placement. `rgw_bucket_shard` combines bucket id and shard id for index/log/sync/cache keys.

Dependencies/integration: pool/user/placement types, formatter, hashing, and cls user bucket conversion implemented elsewhere. Used broadly by bucket metadata, sync, logging, cache, and REST.

Risks: legacy decode defaults are compatibility-critical. `operator<<` appears to include an extra closing parenthesis in display. Equality requires exact bucket id while `match()` allows empty-id wildcard, so callers must choose correctly.

Test signals: all legacy decode versions, explicit-placement absence/presence, wildcard matching, hashing stability, ordered comparisons, shard key formatting, and stream output expectations.
