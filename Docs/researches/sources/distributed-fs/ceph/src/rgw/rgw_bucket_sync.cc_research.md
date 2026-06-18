# sources/distributed-fs/ceph/src/rgw/rgw_bucket_sync.cc

Purpose: implements bucket sync policy flow resolution for multisite RGW, converting zonegroup and bucket policies into source/destination pipe sets used by data sync.

Important APIs/types/functions: stream operators for sync entities/pipes, `filter_relevant_pipes()`, `rgw_sync_group_pipe_map` methods, `RGWBucketSyncFlowManager::pipe_rules`, `pipe_set`, `allowed_data_flow()`, `init()`, `reflect()`, `RGWSyncPolicyCompat::convert_old_sync_config()`, and `RGWBucketSyncPolicyHandler` constructors, `init()`, `reflect()`, pipe getters, and export/import checks.

Control flow: group map initialization filters policy pipes touching the local zone/bucket, chooses explicit group data flow or a parent-derived default flow, and populates source/dest multimaps for symmetrical and directional flows. `reflect()` recursively applies parent policy, then local group policy, with `FORBIDDEN` disabling matching pipes and enabled/allowed groups inserting pipes. `pipe_rules` select highest-priority matching prefix/tag filters and can detect when tag fetch is required before choosing params.

State/persistence: no direct storage writes. It reads zonegroup sync policy, optional bucket sync policy, bucket sync hints from `RGWSI_Bucket_Sync`, and builds in-memory pipe maps, handler sets, zone sets, hints, and resolved pipe sets.

Dependencies/integration: `rgw_sync_policy`, zone services, bucket sync service, object tags, `RGWBucketInfo`, buffer attrs, logging, and Ceph context. Data sync and REST/admin policy code use handler results to decide import/export routes.

Risks: policy precedence is subtle: forbidden beats enabled, and bucket-level allowed without zonegroup enabled can disable sync. Prefix selection uses sorted `multimap` and comments note a trie would be better. `find_basic_info_without_tags()` can return false/need-more-info on conflicting same-priority params. Disabled pipe matching must stay consistent with `match()` semantics.

Test signals: legacy zone sync conversion, symmetrical/directional flows, parent plus bucket policy precedence matrix, forbidden overrides, wildcard bucket fallback, prefix/tag priority selection, source/target zone maps, resolved hints, `bucket_exports_object()`, and sync-module disabled behavior.
