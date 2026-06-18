# sources/distributed-fs/ceph/src/rgw/radosgw-admin/orphan.cc

## Purpose
This source implements RGW admin orphan-object tooling. `RGWOrphanSearch` builds temporary shard indexes of all candidate RADOS objects, all bucket instances, and all objects reachable from bucket indexes/manifests, then reports pool objects that appear unlinked and stale. `RGWRadosList` lists RADOS object IDs reachable from buckets, including manifest parts, DLO/SLO references, versions, and incomplete multipart uploads.

## Important APIs, types, and functions
- `obj_fingerprint()` normalizes raw RGW object IDs by bucket marker and logical object key, stripping namespace/suffix detail for comparison.
- `RGWOrphanStore::{init,read_job,write_job,remove_job,list_jobs,store_entries,read_entries}` persists job state and shard entries in the zone log pool omap.
- `RGWOrphanSearch::init()` loads or creates a job, sets defaults, and names per-shard temporary index objects.
- `build_all_oids_index()` scans every namespace in the target data pool and records non-head object IDs by fingerprint shard.
- `build_buckets_instance_index()` scans metadata section `bucket.instance`.
- `build_linked_oids_for_bucket()` lists bucket index entries, stats objects asynchronously, reads manifests, and records referenced raw objects.
- `build_linked_oids_index()` iterates bucket-instance shard omaps and records linked object fingerprints.
- `compare_oid_indexes()` walks all-vs-linked shard omaps and prints `leaked:` objects after an mtime stale threshold.
- `run()` advances the persisted stage machine; `finish()` removes temporary indexes and job state.
- `RGWRadosList::{run,process_bucket,handle_stat_result,do_incomplete_multipart}` prints reachable RADOS object IDs from bucket traversal.

## Control flow
Orphan search starts by opening the log pool and loading job state. A new job begins at `INIT`, then `run()` falls through stages after each successful save: list pool objects, list bucket instances, iterate bucket indexes to build linked-object indexes, then compare. Pool listing skips unidentified object names and head objects because heads are mutable and cleanup would race with normal object lifecycle. Bucket traversal skips stale bucket instances and buckets under resharding, lists versions with namespace enforcement disabled, avoids stats for small head-only objects unless detailed mode is enabled, and caps concurrent async stat operations by `max_concurrent_ios`.

`compare_oid_indexes()` creates one `OMAPReader` per all/linked shard pair. For each all-object key it computes a fingerprint, advances the linked reader while keys compare lower, and treats absence from linked as a potential leak. It re-stats the data object and suppresses objects newer than `start_time - stale_secs`.

`RGWRadosList` starts from a bucket or all buckets. It keeps a process map of whole buckets, prefixes, and exact keys discovered through DLO/SLO manifests. `process_bucket()` lists bucket index entries, handles versioned heads, stats objects, and prints raw manifest locations. In normal output mode it also lists incomplete multipart parts after the initial bucket traversal; when field-separator mode is enabled it includes bucket/object names and skips incomplete multipart post-processing.

## State and persistence behavior
Durable state lives in the log pool object `orphan.index`, keyed by job name, as encoded `RGWOrphanSearchState`. Temporary shard omap objects are named `orphan.scan.<job>.rados.<shard>`, `.buckets.<shard>`, and `.linked.<shard>`. `search_stage.shard` and `search_stage.marker` are saved while iterating bucket index shards, allowing partial resume. `finish()` removes temporary objects and job state. `RGWRadosList` does not persist state; it holds in-memory `bucket_process_map` and `visited_oids`.

## Dependencies and integration points
The code integrates with RGW SAL/RadosStore, RGWRados bucket/object APIs, metadata listing, bucket instance parsing/loading, bucket reshard state, object manifests, multipart upload abstractions, DLO/SLO attrs, Ceph bufferlist encoding, log pool ioctx, and Ceph admin formatter/dout output. It is intended for `radosgw-admin` commands and operational diagnostics.

## Risks and edge cases
- The search is inherently racy with object create/delete, bucket delete, and reshard; the code skips some races but can still produce false positives/negatives.
- `obj_fingerprint()` loops backward with unsigned `size_t`; unusual short object names or suffixes deserve tests.
- `RGWOrphanStore::store_entries()` and `read_entries()` currently return 0 even after logging certain lower-level errors, which can hide persistence failures.
- `log_oids()` batches 100 entries per omap write and the scan can create many omap keys; large clusters need operational limits.
- The comparison assumes shard omap key ordering by fingerprint-compatible strings and uses empty `cur_linked` initial state carefully; edge ordering bugs would affect leak results.
- Indexless buckets make `radoslist` incomplete unless explicitly bypassed.
- DLO/SLO recursion is bounded only by `visited_oids` for object IDs and the evolving bucket process map.

## Test signals
Tests should simulate job create/resume/finish, omap read/write/list/remove errors, bucket-instance sharding, pool objects with heads/shadows/multipart suffixes, stale threshold boundaries, bucket deletion races, reshard skip behavior, manifest traversal for multipart/versioned/head-only objects, DLO/SLO references including loops and malformed paths, indexless bucket behavior, field-separator output, and incomplete multipart listing. Integration tests need a controlled RGW/RADOS fixture because most behavior depends on live metadata and object manifests.
