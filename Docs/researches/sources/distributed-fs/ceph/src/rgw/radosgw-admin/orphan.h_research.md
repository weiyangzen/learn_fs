# sources/distributed-fs/ceph/src/rgw/radosgw-admin/orphan.h

## Purpose
This header declares the state model and public classes for RGW orphan search and RADOS object listing used by `radosgw-admin` tooling.

## Important APIs, types, and functions
- Constants: `RGW_ORPHAN_INDEX_OID` (`orphan.index`) and `RGW_ORPHAN_INDEX_PREFIX` (`orphan.scan`).
- `RGWOrphanSearchStageId` enumerates persisted stages from init through pool listing, bucket listing, bucket-index iteration, and comparison.
- `RGWOrphanSearchStage`, `RGWOrphanSearchInfo`, and `RGWOrphanSearchState` encode/decode and dump job metadata and progress.
- `RGWOrphanStore` wraps log-pool omap access for jobs and shard entries.
- `RGWOrphanSearch` declares the staged orphan scan, shard index maps, concurrency/staleness configuration, state saving, index builders, compare, run, and finish.
- `RGWRadosList` declares traversal helpers for listing raw RADOS objects behind RGW buckets and manifests.

## Control flow
The header defines the stage machine consumed by `orphan.cc`: `INIT -> LSPOOL -> LSBUCKETS -> ITERATE_BI -> COMPARE`. It also defines private helpers for sharding fingerprints, logging object IDs, handling async stat results, and removing temporary index objects.

## State and persistence behavior
The encoded structs are the durable job contract. `RGWOrphanSearchInfo` version 2 stores job name, target pool, shard count, and start time; `RGWOrphanSearchStage` stores stage, current shard, and marker; `RGWOrphanSearchState` combines both. `RGWOrphanSearch` keeps in-memory maps from shard id to temporary omap object names. `RGWRadosList` keeps in-memory bucket processing and visited-object state only.

## Dependencies and integration points
The header depends on Ceph config, formatter, errno helpers, and `rgw_sal_rados.h`. It exposes RGW SAL RadosStore types, librados IoCtx, `DoutPrefixProvider`, `bufferlist`, `rgw_pool`, and RGW object key types to the implementation and callers.

## Risks and edge cases
- Encoding versions must remain compatible with existing persisted orphan jobs.
- `num_shards` is a `uint16_t`; the implementation hashes into this count and assumes it is nonzero after defaulting.
- Public constructors take raw `RadosStore*`; lifetime is owned elsewhere.
- Operational safety depends on callers invoking `finish()` after successful searches to remove temporary omap objects.

## Test signals
Tests should round-trip encode/decode for all persisted structs, verify formatter output for each stage, validate default and explicit shard counts, confirm temporary object naming from job/shard data, and exercise class APIs through the implementation with mocked or fixture-backed RadosStore behavior.
