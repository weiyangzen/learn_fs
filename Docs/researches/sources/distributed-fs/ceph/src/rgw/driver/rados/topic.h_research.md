# sources/distributed-fs/ceph/src/rgw/driver/rados/topic.h

## Purpose
Declares the RADOS v2 topic metadata interface and cache entry type used by `topic.cc`.

## Important APIs, types, and functions
- `cache_entry` stores topic info, object version tracker, and mtime.
- `read()`, `write()`, and `remove()` manage topic metadata.
- `link_bucket()`, `unlink_bucket()`, and `list_buckets()` manage bucket membership for a topic.
- `create_metadata_handler()` constructs the metadata sync handler.

## Control flow
Callers provide sysobj/cache/mdlog/RADOS/zone dependencies explicitly and pass topic metadata keys rather than raw object names. Bucket association APIs operate by topic key plus bucket key and support marker-based listing.

## State and persistence behavior
The header exposes that topic reads can return mtime/version and use a chained cache, while writes/removes use version trackers and mdlog.

## Dependencies and integration points
Includes RADOS forwards, Ceph time, and `rgw_pubsub.h`; forward declares metadata, sysobj/cache, zone, and chained cache types. It is consumed by pubsub admin paths, bucket notification code, account topic listing, and metadata sync.

## Risks and edge cases
Callers must pass canonical topic metadata keys from `get_topic_metadata_key()` or reads/writes will target different objects. `list_buckets()` max and marker behavior depends on RADOS omap ordering.

## Test signals
Compile tests plus integration tests should cover all declared APIs with a real or mocked sysobj/RADOS layer and chained cache.
