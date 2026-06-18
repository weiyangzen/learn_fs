# subset-b-006978 Research

Grouped source research for Ceph RGW RADOS sync modules, sync tracing, RADOS helper utilities, and multisite log trimming. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_aws.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_aws.cc

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_aws.cc` implements the RGW cloud sync module that exports multisite data changes to an S3-compatible AWS target. It parses sync-module JSON configuration, chooses per-bucket target profiles, translates source RGW object metadata/ACLs into S3 headers, creates destination buckets as needed, streams normal objects, handles resumable multipart uploads, and issues delete requests for removed objects.

## Important APIs, Types, and Functions

The central configuration types are `ACLMapping`, `ACLMappings`, `AWSSyncConfig_Connection`, `AWSSyncConfig_S3`, `AWSSyncConfig_Profile`, and `AWSSyncConfig`. `AWSSyncConfig::init()` parses the default profile, named connections, ACL profiles, S3 multipart tuning, root target, and explicit bucket/prefix profiles. `find_profile()`, `get_path()`, and `get_target()` map RGW source buckets and keys into destination bucket/object names.

The streaming path uses `RGWRESTStreamGetCRF` to fetch source objects from the source zone, `RGWAWSStreamPutCRF` to PUT to the destination S3 service, and `RGWStreamSpliceCR` to copy data between them. `RGWAWSStreamObjToCloudPlainCR` handles small objects. Large objects are coordinated by `RGWAWSStreamObjToCloudMultipartCR`, with helper coroutines for initiate, part upload, complete, and abort. `RGWAWSHandleRemoteObjCBCR` is the object stat callback that chooses plain versus multipart sync. `RGWAWSDataSyncModule` exposes the sync-module interface, and `RGWAWSSyncModule::create_instance()` builds the module instance.

## Control Flow

Initialization parses config, expands target-path variables such as `${sid}`, `${zonegroup}`, `${zone}`, `${bucket}`, and `${owner}`, then builds `S3RESTConn` objects for the root and explicit profiles. During data sync, `sync_object()` allocates `RGWAWSHandleRemoteObjCR`, which stats the remote object through `RGWCallStatRemoteObjCR`, decodes source zone/pg version attributes, picks a target profile, derives the destination path, creates the destination bucket if this coroutine has not seen it before, and starts either the plain or multipart upload flow.

The plain path creates a source GET stream and destination PUT stream and splices them. The multipart path first tries to read persisted multipart state, aborts stale state if source size/mtime/etag changed, initiates a new upload if needed, uploads each ranged part while recording ETags, writes progress after each part, completes the multipart upload, and removes the status object. `remove_object()` maps the source key to the destination path and issues a REST DELETE. Delete marker creation is logged as not implemented.

## State and Persistence Behavior

Configuration state is held in `AWSSyncInstanceEnv` and profile objects for the lifetime of the sync module instance. Multipart progress persists in a RADOS status object under the zone log pool using `RGWBucketPipeSyncStatusManager::obj_status_oid()`, encoded as `rgw_sync_aws_multipart_upload_info`. The status includes upload id, source mtime/etag/zone/pg/versioned epoch, part size, current part/offset, and uploaded part ETags. Destination buckets and objects are external S3 state. The file also injects source metadata into destination user metadata headers such as source mtime, source etag, source key, source version id, and versioned epoch.

## Dependencies and Integration Points

This module sits on RGW multisite data sync (`RGWDataSyncModule`, `RGWDataSyncCtx`, `rgw_bucket_sync_pipe`), RGW coroutine infrastructure, REST connection/coroutine helpers, source-zone connections from `svc_zone`, RGW ACL structures, and RADOS coroutine helpers for the multipart status object. It integrates with S3 signing via `S3RESTConn`, destination host style/region config, and RGW object attributes such as `RGW_ATTR_ACL`, `RGW_ATTR_PG_VER`, and `RGW_ATTR_SOURCE_ZONE`.

## Risks and Edge Cases

Multipart recovery depends on correctly detecting stale state; mismatched source metadata can leave an abandoned upload that is only best-effort aborted. ACL mapping silently ignores grants without configured mappings. Bucket creation treats `BucketAlreadyOwnedByYou` as success but relies on parsing an S3 XML error body. `bucket_created` is per callback object, so repeated create attempts may occur across objects or workers. Target path splitting assumes a slash exists after expansion. Delete marker sync is unimplemented, which is important for versioned bucket semantics. Errors while removing multipart status are ignored after successful complete, so stale status may trigger unnecessary future cleanup.

## Test Signals

High-value tests include config parsing with default, inline, referenced, duplicate, and missing profiles; target-path expansion for tenants and owners; ACL mapping coverage for id/email/uri grants; plain object sync preserving metadata; multipart sync across interruption and resume; stale multipart state abort when source changes; destination bucket already exists/owned behavior; delete object mapping; and negative REST/XML/JSON decode paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_aws.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_aws.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_aws.h

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_aws.h` declares the public AWS cloud sync module and the small encoded state records used by the implementation to track source object identity and multipart upload progress.

## Important APIs, Types, and Functions

`rgw_sync_aws_multipart_part_info` records a multipart part number, source offset, part size, and destination ETag. `rgw_sync_aws_src_obj_properties` captures source mtime, ETag, source zone short id, pg version, and versioned epoch. `rgw_sync_aws_multipart_upload_info` records the upload id, source object size/properties, chosen part size/count, current part/offset, and a map of completed part records. All three define Ceph encoders. `RGWAWSSyncModule` derives from `RGWSyncModule`, reports no data export support, and exposes `create_instance()`.

## Control Flow

The header has no runtime flow. The sync module registry instantiates `RGWAWSSyncModule`, calls `create_instance()`, and the implementation returns an `RGWSyncModuleInstance` with a data handler. The encoded multipart structs are read and written by AWS multipart sync coroutines.

## State and Persistence Behavior

The structs are persisted through Ceph `bufferlist` encoding in the zone log pool for resumable multipart sync. Versioned encoders currently start at version 1, so future format changes must preserve backward decode behavior. The module class itself owns no state in the header.

## Dependencies and Integration Points

The header depends on `rgw_sync_module.h`, Ceph `bufferlist` encoding macros, and the RGW sync module interface. The implementation uses these declarations with RADOS status objects and S3 REST sync coroutines.

## Risks and Edge Cases

The persistence layout is part of the on-disk recovery contract for in-flight multipart uploads. Field changes, default value changes, or non-compatible encoder updates can break resume/abort behavior after upgrade.

## Test Signals

Test signals include encode/decode round trips for empty and populated multipart records, compatibility tests for persisted status objects across versions, and module registration tests that instantiate the AWS sync module from JSON config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_aws.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_es.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_es.cc

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_es.cc` implements the Elasticsearch metadata sync module for RGW multisite. Instead of copying object data, it indexes RGW object metadata, ACL-derived read permissions, tags, compression information, and configured custom metadata into an Elasticsearch index, and removes documents when objects are deleted.

## Important APIs, Types, and Functions

`ItemList` parses allowlist strings with exact, prefix, suffix, and wildcard matching for buckets and owners. `ElasticConfig` owns endpoint, REST connection, generated index path, allowlists, shard/replica settings, default headers, basic auth header, and probed `ESInfo`. `ESInfo` and `es_version_decoder` parse Elasticsearch version information. `es_type_v2`, `es_type_v5`, `es_index_mappings`, and `es_index_config` dump version-specific mappings/settings. `es_obj_metadata::dump()` serializes one RGW object document. `RGWElasticGetESInfoCBCR`, `RGWElasticPutIndexCBCR`, and `RGWElasticInitConfigCBCR` initialize the remote index. `RGWElasticHandleRemoteObjCBCR` and `RGWElasticRemoveRemoteObjCBCR` index and delete documents. `RGWElasticDataSyncModule` and `RGWElasticSyncModuleInstance` expose the sync-module and REST-filter integration.

## Control Flow

At module construction, `ElasticConfig::init()` builds an `RGWRESTConn`, reads config toggles such as `explicit_custom_meta`, allowlists, `override_index_path`, `num_shards`, `num_replicas`, and optional basic auth. `init()` receives the sync instance id and computes the index path unless overridden. `init_sync()` probes the ES root endpoint, then PUTs index settings/mappings, ignoring already-exists errors. `start_sync()` refreshes ES version info.

For each object sync, `sync_object()` checks bucket and owner allowlists, then stats the remote object. The callback constructs an object id from bucket id, key name, and instance, serializes metadata with `es_obj_metadata`, and PUTs the JSON document to either `/<index>/_doc/<id>` for newer ES or `/<index>/object/<id>` for older mappings. `remove_object()` performs the same path computation and issues DELETE. Delete marker creation is intentionally skipped.

## State and Persistence Behavior

Persistent state is external to RGW in the Elasticsearch index. The module stores only in-memory config and ES version data. Index names are stable for a realm plus sync instance id unless `override_index_path` is configured. Indexed documents include object identity, versioned epoch, owner, read permissions derived from ACLs, common metadata fields, custom string/int/date metadata, and tags. No RADOS state is persisted by this module beyond the normal RGW sync machinery.

## Dependencies and Integration Points

The code depends on RGW data sync, RGW REST coroutine helpers, `rgw_es_query` types shared with the search REST path, RGW ACL/tag/compression decoders, `svc_zone` for realm metadata, and `RGWRESTConn` for HTTP calls to Elasticsearch. `RGWElasticSyncModuleInstance::get_rest_filter()` replaces the S3 REST manager with `RGWRESTMgr_MDSearch_S3` so client search requests can query the ES index.

## Risks and Edge Cases

Elasticsearch version handling is central: mappings differ for pre-5, 5+, and 7+ document types, and drift can break indexing or search. The `ESType::Double_Range` string maps to `"date_range"`, which looks suspicious and deserves targeted review. Custom date metadata is skipped if it cannot be parsed, avoiding document rejection but losing searchability. ACL decode errors leave permissions incomplete. The module only supports metadata indexing and skips delete markers, so versioned semantics may not fully match object history.

## Test Signals

Useful tests include ES version parsing and mapping output for ES 2, 5, and 7; index already exists handling; allowlist matching; basic auth header generation; document serialization for ACLs, tags, compression, custom metadata, invalid custom dates, and object instances; delete path generation; and REST-filter installation for S3 metadata search.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_es.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_es.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_es.h

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_es.h` declares the Elasticsearch sync module, the metadata type enum used in index mappings, and the module instance methods needed by both data sync and the metadata-search REST filter.

## Important APIs, Types, and Functions

`ESType` enumerates Elasticsearch field types used by mapping generation, including string/text/keyword, numeric, date, boolean, binary, range, geo point, and IP types. `RGWElasticSyncModule` derives from `RGWSyncModule`, reports no data export support, and creates module instances. `RGWElasticSyncModuleInstance` owns a `RGWElasticDataSyncModule` and exposes `get_data_handler()`, `get_rest_filter()`, `get_rest_conn()`, `get_index_path()`, `get_request_headers()`, and `supports_user_writes()`.

## Control Flow

The header defines the external shape of the module. The sync registry calls `create_instance()`, data sync asks the instance for its handler, and the REST path asks for a filter manager. For S3 dialects, the implementation replaces the normal manager with metadata-search-aware handling.

## State and Persistence Behavior

The instance owns the data handler through a `unique_ptr`; Elasticsearch connection, index path, and request headers are internal implementation state reachable through accessors for the search REST module. No persisted state is declared in this header.

## Dependencies and Integration Points

It depends on `rgw_sync_module.h` and forward declares `RGWElasticDataSyncModule` and `RGWRESTConn`. Its main integration points are the RGW sync-module interface and `rgw_sync_module_es_rest.cc`, which downcasts the sync module instance to access ES connection details.

## Risks and Edge Cases

The REST search path assumes the active sync module instance is an Elasticsearch instance. If the filter is installed in the wrong context or the sync module is absent, downcast assumptions in the implementation can become fragile.

## Test Signals

Compile/link coverage for module registration, data-handler access, S3 REST filter replacement, and metadata-search calls that use `get_rest_conn()`, `get_index_path()`, and `get_request_headers()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_es.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_es_rest.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_es_rest.cc

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_es_rest.cc` implements the S3-facing metadata-search REST extension backed by the Elasticsearch sync module. It accepts search query parameters, compiles them to Elasticsearch query JSON, enforces bucket/user constraints, calls the configured ES endpoint, decodes search hits, and returns RGW-style XML or JSON responses.

## Important APIs, Types, and Functions

`es_index_obj_response` decodes the indexed document shape produced by `es_obj_metadata`, including identity, versioned epoch, owner, permissions, base metadata, and custom metadata arrays. `es_search_response` decodes Elasticsearch `_search` responses. `RGWMetadataSearchOp` is the base `RGWOp` that validates permissions, compiles queries, sends ES requests, and decodes results. `RGWMetadataSearch_ObjStore_S3` parses S3 query parameters and formats responses. `RGWHandler_REST_MDSearch_S3` selects metadata-search operations for GET requests. `RGWRESTMgr_MDSearch_S3::get_handler()` installs the S3 handler only for bucket-level requests without an object component.

## Control Flow

For a bucket GET with a `query` parameter, the handler creates `RGWMetadataSearch_ObjStore_S3`. `get_params()` reads `query`, clamps `max-keys` to 10000, parses `marker` as an ES `from` offset, and computes `NextMarker`. `execute()` adds permission and bucket constraints unless the user is a system user, configures `ESQueryCompiler` with field aliases, generic type mapping, restricted fields, and the bucket's custom metadata type map, then serializes the query and calls `RGWRESTConn::get_resource()` on `<index>/_search` with `size` and optional `from`. The response is parsed as JSON and decoded into `es_search_response`. `send_response()` writes `SearchMetadataResponse`, pagination fields, object entries, owner, and custom metadata.

## State and Persistence Behavior

The REST operation is per-request and persists no local state. It reads from the Elasticsearch index maintained by the sync module and uses request-scoped values such as expression, max keys, marker, next marker, and decoded response. Visibility is constrained by indexed ACL permissions and the request bucket.

## Dependencies and Integration Points

This file depends on `rgw_sync_module_es.h`, `rgw_es_query.h`, RGW S3 REST handling, `rgw_op`, and `rgw_sal_rados`. It downcasts `driver->get_sync_module()` to `RGWElasticSyncModuleInstance` and uses its REST connection, index path, and headers. It also integrates with bucket `mdsearch_config` to type custom metadata queries.

## Risks and Edge Cases

Pagination uses ES `from` offset derived from marker rather than a stable search-after token, so concurrent index updates can shift results. Non-system users are filtered by the indexed `permissions` field; stale or incomplete index data can affect authorization results. The handler returns no operation if `query` is absent and no bucket `mdsearch` request matches. JSON parsing/decoding failures become `-EINVAL`. The downcast assumes the active sync module is Elasticsearch.

## Test Signals

Tests should cover query compilation aliases, restricted `permissions` field behavior, custom metadata type maps, non-system user and bucket constraints, max-keys clamping, marker parsing, XML/JSON output formatting, malformed ES responses, ES request failure propagation, and handler selection for bucket versus object requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_es_rest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_es_rest.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_es_rest.h

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_es_rest.h` declares the REST manager used by the Elasticsearch sync module to add S3 metadata-search operations.

## Important APIs, Types, and Functions

`RGWRESTMgr_MDSearch_S3` derives from `RGWRESTMgr` and overrides `get_handler()` to return a metadata-search-aware S3 handler. The header forward declares `RGWElasticSyncModuleInstance` because the implementation is coupled to Elasticsearch sync module state.

## Control Flow

There is no executable flow in the header. The sync module instance returns this manager from `get_rest_filter()` for S3 dialects; RGW frontend dispatch later calls `get_handler()` during request routing.

## State and Persistence Behavior

The manager owns no persistent state in the header. Per-request state is allocated by the implementation handler and operation classes.

## Dependencies and Integration Points

The header depends on `rgw_rest.h` and integrates with RGW REST manager dispatch. It is paired with `rgw_sync_module_es.cc`, which installs it, and `rgw_sync_module_es_rest.cc`, which implements the operation.

## Risks and Edge Cases

The manager is only valid when an Elasticsearch sync module instance backs the store, because the implementation needs ES connection and index details. Routing mistakes can produce null handlers or unsafe assumptions in the implementation.

## Test Signals

Compile and dispatch tests should verify that S3 bucket GET metadata-search requests receive the custom handler, object requests are rejected by the manager, and non-S3 dialects retain the original REST manager.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_es_rest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_log.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_log.cc

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_log.cc` implements a diagnostic RGW sync module that logs data-sync operations instead of exporting or indexing data. It is useful for observing multisite sync callbacks and remote object stats.

## Important APIs, Types, and Functions

`RGWLogStatRemoteObjCBCR` logs the result of a remote object stat, including source zone, bucket, key, size, mtime, and attributes. `RGWLogStatRemoteObjCR` wraps the callback in the standard remote-stat coroutine. `RGWLogDataSyncModule` implements `sync_object()`, `remove_object()`, and `create_delete_marker()` by logging operation details. `RGWLogSyncModuleInstance` exposes the data handler, and `RGWLogSyncModule::create_instance()` reads a `prefix` config value.

## Control Flow

On object sync, the module logs the requested bucket/key/versioned epoch and returns a remote stat coroutine whose callback logs full stat details. Remove and delete-marker callbacks only log and return null, so no downstream export action is performed. Instance creation is a simple prefix read plus object allocation.

## State and Persistence Behavior

The only state is the configured log prefix stored in the data handler. No RADOS or external state is written by this module.

## Dependencies and Integration Points

It depends on RGW data sync abstractions, coroutine support, remote stat helpers, and Ceph logging. It plugs into the same `RGWSyncModule`/`RGWDataSyncModule` path as production sync modules, making it a low-impact observer.

## Risks and Edge Cases

Logging at level 0 can be noisy under high object churn. Because delete and delete-marker operations return null, using this module as anything other than a diagnostic sink will not replicate state changes.

## Test Signals

Tests can instantiate the module with a prefix, trigger sync/remove/delete-marker callbacks, and assert that the expected coroutine is returned only for sync_object. Integration smoke tests should verify remote stat logging does not alter sync state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_log.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_log.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_log.h

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_log.h` declares the diagnostic log sync module.

## Important APIs, Types, and Functions

`RGWLogSyncModule` derives from `RGWSyncModule`, reports no data export support, and exposes `create_instance()` for module registration.

## Control Flow

The header has no executable flow. RGW module registration calls into the implementation to create an instance whose data handler logs sync events.

## State and Persistence Behavior

No state is declared in the header. The implementation stores only a log prefix and writes no persistent data.

## Dependencies and Integration Points

It depends on `rgw_sync_module.h` and the generic RGW sync module interface.

## Risks and Edge Cases

The class shape is intentionally minimal. The main risk is accidental use in a path expecting actual data export or deletion behavior.

## Test Signals

Compile coverage and module instantiation from JSON config are sufficient header-level signals; behavior is covered in the `.cc` diagnostic logging tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_trace.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_trace.cc

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_trace.cc` implements runtime tracing for RGW multisite sync activity. It tracks active and recently completed sync trace nodes, records per-node history, exposes admin socket commands, logs sync status updates, and periodically publishes active sync names into the service map.

## Important APIs, Types, and Functions

`RGWSyncTraceNode` constructs hierarchical prefixes from parent/type/id, stores status and circular history, logs messages, and supports regex matching. `RGWSyncTraceServiceMapThread` extends `RGWRadosThread` and calls `update_service_map()` with `current_sync`. `RGWSyncTraceManager::add_node()` allocates handles and returns a shared pointer with a custom deleter that calls `finish_node()`. `hook_to_admin_command()` registers `sync trace show`, `sync trace history`, `sync trace active`, and `sync trace active_short`. `call()` formats running and complete trace nodes. `finish_node()` moves entries from active map to completed LRU.

## Control Flow

Initialization starts the service-map thread. Sync code creates child nodes with `add_node()`, sets flags/resource names, and calls `log()`. When the returned shared pointer is destroyed, the custom deleter moves the node from the active map to the completed circular buffer. Admin socket calls acquire a shared lock, filter by optional regex and active flags, and dump JSON. The service-map thread periodically calls `get_active_names()` and publishes a JSON array of resource names.

## State and Persistence Behavior

State is in memory only: an active `nodes` map keyed by handle, a bounded `complete_nodes` circular buffer, per-node bounded history buffers, an atomic handle counter, and admin command registration. The service map receives current active names, but trace history itself is not persisted across daemon restart.

## Dependencies and Integration Points

The implementation depends on Ceph admin socket, JSON formatting, RGW worker thread infrastructure, RGWRados service-map updates, Ceph logging subsystems, regex, shared locks, and configuration values such as per-node history size and service-map update interval. Sync code consumes `RGWSyncTraceNodeRef` to bracket work.

## Risks and Edge Cases

`RGWSyncTraceNode::log()` updates `status` and `history` without taking the node mutex declared in the header, so concurrent updates/readers deserve scrutiny. Bad regex filters are caught and logged, returning no match. The destructor unconditionally stops `service_map_thread`; if `init()` was never called, null handling depends on callers. `get_active_names()` flushes within the loop, so output shape should be checked under multiple active nodes.

## Test Signals

Useful tests include node hierarchy prefix construction, custom deleter movement to completed LRU, admin socket output with and without history, regex filtering including invalid regex, active flag filtering, bounded history behavior, service-map publication, and thread lifecycle init/destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_trace.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_trace.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_trace.h

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_trace.h` declares RGW multisite sync tracing nodes and the trace manager/admin-socket hook.

## Important APIs, Types, and Functions

Macros define `RGW_SNS_FLAG_ACTIVE` and `RGW_SNS_FLAG_ERROR`. `RGWSyncTraceNode` stores parent, flags, status, type/id-derived prefix, resource name, handle, and circular history. Public methods set resource name, set/unset/test flags, log status, return string/prefix/history, and match search terms. `RGWSyncTraceManager` derives from `AdminSocketHook`, owns active and complete trace node containers, allocates handles, creates nodes, initializes the service-map thread, hooks admin commands, serves admin calls, and returns active names.

## Control Flow

Callers create nodes through `RGWSyncTraceManager::add_node()` rather than direct construction. Node lifetime drives completion through the implementation's custom deleter. Admin socket dispatch calls `RGWSyncTraceManager::call()` for registered commands.

## State and Persistence Behavior

All declared state is in-memory and bounded by circular buffers. The manager uses a shared timed mutex for its node maps and an atomic counter for handles. No on-disk persistence is defined.

## Dependencies and Integration Points

The header depends on Ceph mutex/shared-lock helpers, admin socket APIs, atomic counters, STL containers, and Boost circular buffers. It forward declares `RGWRados` and the service-map thread to avoid broad includes.

## Risks and Edge Cases

Thread-safety depends on implementation discipline around node mutation and manager container access. Because `root_node` is declared but not initialized in this header, construction behavior must remain consistent in implementation/users. Admin command output depends on stable JSON formatting and bounded history sizing.

## Test Signals

Header-level coverage comes from compiling users that create trace managers and nodes, set flags/resource names, and invoke admin socket hooks. Runtime tests should focus on the implementation's lifecycle and concurrency behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_tools.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_tools.cc

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_tools.cc` implements common RGW RADOS utility functions for pool/ioctx initialization, raw object references, synchronous or coroutine-aware RADOS operations, system object access, attribute filtering, monitor security checks, cluster log warnings, and pool listing.

## Important APIs, Types, and Functions

`rgw_init_ioctx()` opens or optionally creates a pool, enables the RGW application, sets mostly-omap/bulk pool flags, applies namespace, and enables pool-full try behavior. `rgw_get_rados_ref()` initializes `rgw_rados_ref`. `rgw_rados_ref::watch()` and `unwatch()` provide blocking or yield-context async watch APIs. `rgw_put_system_obj()`, `rgw_get_system_obj()`, `rgw_stat_system_obj()`, and `rgw_delete_system_obj()` wrap `RGWSI_SysObj` reads/writes/stats/removes. `rgw_rados_operate()` overloads and `rgw_rados_notify()` choose async librados calls when `optional_yield` is present. `rgw_filter_attrset()`, `rgw_complete_aio_completion()`, `rgw_check_secure_mon_conn()`, `rgw_clog_warn()`, and `rgw_list_pool()` provide focused helpers.

## Control Flow

Most functions are thin wrappers. The pool init path attempts `ioctx_create`, creates the pool on `-ENOENT` if allowed, reopens it, enables application metadata, optionally sets pool tunables through monitor commands, applies namespace, and returns errors directly. RADOS operate/notify wrappers branch on `optional_yield`: with a yield context they call async librados and convert error codes; otherwise they warn about blocking and call synchronous APIs. Pool listing parses an object cursor, iterates up to `max`, filters object names, updates the marker, and reports truncation.

## State and Persistence Behavior

The utilities can create pools, set pool properties, write/delete system objects, perform raw object operations, and emit cluster log messages. `no_change_attrs()` returns a static sentinel map used by `rgw_put_system_obj()` to distinguish preserving attributes from clearing attributes. `rgw_rados_ref` stores an ioctx plus raw object reference and may hold watch registrations.

## Dependencies and Integration Points

This file depends on librados, librados_asio, RGW system object service, RGW aio helpers, auth registry, Ceph monitor commands, RGW pool/object types, and optional coroutine yield contexts. It is a shared substrate used by sync, trim, metadata, bucket, and system-object code throughout the RADOS driver.

## Risks and Edge Cases

Pool creation partially succeeds before later monitor tuning commands can fail; mostly-omap tuning failures are logged but not fatal. The async wrappers return negative `ec.value()` while synchronous APIs return librados negatives, so consistency relies on error-code conventions. `rgw_list_pool()` returns `-ENOENT` for an empty/end iterator, which callers must treat appropriately. The `no_change_attrs()` sentinel relies on pointer identity.

## Test Signals

Tests should cover create-existing/missing pool paths, namespace application, mostly-omap and bulk command failures, coroutine versus blocking operate/notify results, system object attr preservation with `no_change_attrs()`, secure/insecure auth method detection, pool listing markers/truncation/filtering, and watch/unwatch with and without yield.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_tools.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_tools.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_tools.h

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_tools.h` declares shared RGW RADOS helper APIs and inline/asynchronous helpers used across the RADOS-backed RGW driver.

## Important APIs, Types, and Functions

The header declares pool/ioctx helpers (`rgw_init_ioctx()`, `rgw_shard_id()`, `rgw_shard_name()`), system object helpers, MIME lookup, attr filtering, RADOS operate/notify wrappers, `rgw_rados_ref`, tool init/cleanup, aio completion helper, `no_change_attrs()`, monitor security and cluster log helpers, and `rgw_list_pool()`. It also defines `rgw::mostly_omap` and `rgw::create` tag types plus Boost.Asio composed operations: `set_mostly_omap()`, `create_pool()`, and several `init_iocontext()` overloads for neorados.

## Control Flow

Inline sharding helpers compute stable shard ids from Ceph string hashes and prime modulo schemes. `rgw_rados_ref` methods forward operations to the declared wrappers. The Asio composed operations perform coroutine-style lookup/create/configure flows: create pool, enable RGW application, optionally set mostly-omap tunables, look up pool ids, set namespaces, and return `neorados::IOContext` or error codes through the completion token.

## State and Persistence Behavior

The header declares helpers that create pools, initialize IO contexts, operate on RADOS objects, and update monitor pool settings. `rgw_rados_ref` instances carry an `IoCtx` and raw object. The inline neorados helpers may persist pool creation and pool configuration through monitor commands.

## Dependencies and Integration Points

Dependencies include Boost.Asio composed operations, fmt, neorados, Ceph hash/types/time/dout, OSD pool types, RGW object/pool/common types, librados, and optional yield contexts. The header is a broad integration point for legacy librados code and newer neorados coroutine code.

## Risks and Edge Cases

Because this header contains template coroutine implementations, compile errors or behavior changes affect many translation units. The monitor command JSON for setting recovery priority appears sensitive to exact formatting. Error handling maps exceptions to generic `EIO` in several paths, which can hide specific causes. Shard modulo constants are compatibility-sensitive and should not change casually.

## Test Signals

Compile coverage across librados and neorados users is essential. Behavioral tests should cover shard distribution compatibility, async pool create/init paths, existing pool handling, namespace propagation, mostly-omap tuning, and error conversion from system exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_tools.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_bilog.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_bilog.cc

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_bilog.cc` implements bucket-index-log trimming for RGW multisite. It chooses hot and cold bucket instances to trim, queries peer zones for their bucket sync progress, trims safe bilog markers, removes obsolete bucket index generations, persists the cold-list cursor, and coordinates multiple gateways through RADOS locks and watch/notify.

## Important APIs, Types, and Functions

The watch/notify protocol is built from `TrimNotifyType`, `TrimCounters`, `TrimComplete`, `TrimNotifyHandler`, and `BucketTrimWatcher`. `BucketTrimShardCollectCR` trims bilog shards concurrently. `BucketCleanIndexCollectCR` removes old bucket index generation objects. `RGWReadRemoteStatusShardsCR` reads peer bucket-index sync status. `BucketTrimInstanceCR` is the main per-bucket trim state machine. `take_min_status()` correlates peer markers. `AsyncMetadataList` and `MetadataListCR` list bucket instance metadata with wraparound from a saved marker. `BucketTrimCR` selects buckets and runs trims for one interval. `BucketTrimPollCR` runs periodic locked trims. `RecentEventList` tracks recently trimmed buckets. `BucketTrimManager::Impl` implements counter sharing and observer behavior. `configure_bucket_trim()` reads config, and `bilog_trim()` exposes direct shard trimming.

## Control Flow

Gateways call `BucketTrimManager::on_bucket_changed()` as data sync sees bucket changes, incrementing a bounded counter unless the bucket was recently trimmed. The manager starts a `BucketTrimWatcher` on the `bilog.trim` object in the log pool. Periodic trim sleeps for the configured interval, takes a RADOS lock on that object, then runs `BucketTrimCR`.

`BucketTrimCR` notifies peer gateways for their hot-bucket counters, merges responses, selects top hot buckets, then fills remaining capacity by listing bucket.instance metadata from the saved `BucketTrimStatus` marker while skipping recently trimmed or already selected buckets. It trims selected buckets concurrently. Afterward it writes the new cold marker and sends a trim-complete notify so peers reset counters.

`BucketTrimInstanceCR` fetches the bucket sync policy and current bucket info, queries relevant destination zones for merged bucket-index status, finds the minimum generation peers still need, optionally removes an obsolete generation and updates/removes bucket instance metadata with retries, or computes per-shard minimum markers and trims the current generation's bilogs.

## State and Persistence Behavior

Persistent state includes `BucketTrimStatus` stored at `bilog.trim` in the zone log pool, bucket index log objects, bucket instance metadata layout generations, and destination peer sync progress queried over REST. In-memory state includes bounded hot-bucket counters, a recent-trim circular buffer, notify replies, selected bucket lists, retry counters, and per-trim last markers. Watch/notify replies are transient but coordinate all gateways in the same zone.

## Dependencies and Integration Points

This file integrates with RGW coroutine collectors, RADOS lock/notify/watch helpers, bucket sync policy handlers, bucket instance metadata, bilog RADOS service, zone service connection maps, REST admin log endpoints, metadata manager listing, and `BoundedKeyCounter`. It uses `no_change_attrs()` from `rgw_tools` when updating bucket info without changing attributes.

## Risks and Edge Cases

All peer statuses must be fetched before trimming, so missing zone connections or REST failures stop a bucket trim. Generation cleanup modifies bucket info and can race, handled with retries but still high risk. The code refuses to remove the only live non-deleted log generation. Old peers without v2 status fall back to generation 0, which can limit trimming. Notify decode errors or timeouts reduce hot-bucket selection. The periodic lock is intentionally held for the interval unless errors unlock, so lock duration and lease behavior matter.

## Test Signals

Key tests include notify encode/decode and counter aggregation, watcher restart on disconnect, bucket selection from hot counters plus cold metadata listing, persistent marker wraparound, peer status parsing v1/v2, min generation and min marker selection, old generation cleanup and bucket-info retry races, deleted bucket cleanup, shard-count mismatch errors, recent-trim filtering, and direct `bilog_trim()` generation lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_bilog.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_bilog.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_bilog.h

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_bilog.h` declares the bucket-index-log trim manager, configuration, persistent trim cursor, bucket change observer interface, and direct bilog trim helper.

## Important APIs, Types, and Functions

`rgw::BucketChangeObserver` lets data-sync code report active bucket instances. `rgw::BucketTrimConfig` holds trim interval, counter size, buckets per interval, minimum cold buckets, concurrency, notify timeout, and recent-trim bounds. `configure_bucket_trim()` fills this config from Ceph options. `rgw::BucketTrimManager` implements `BucketChangeObserver` and `DoutPrefixProvider`, with `init()`, `on_bucket_changed()`, `create_bucket_trim_cr()`, and `create_admin_bucket_trim_cr()`. `rgw::BucketTrimStatus` encodes the metadata-list marker and exposes static `oid`. `bilog_trim()` trims a single bucket log generation/shard range.

## Control Flow

The manager is initialized once, starts its watcher, receives bucket-change notifications, and creates either a periodic trim coroutine or one-shot admin trim coroutine. `bilog_trim()` is a synchronous/yield-aware helper used by admin paths to locate a log generation and delegate to the bilog RADOS service.

## State and Persistence Behavior

`BucketTrimStatus` is encoded to RADOS to persist the cold bucket listing cursor. The manager's implementation owns in-memory counters and recently trimmed lists. `bilog_trim()` mutates bilog objects by trimming entries in a supplied marker range.

## Dependencies and Integration Points

The header depends on Ceph encoding, time, dout, async yield, and RGW common types. It forward declares `RadosStore`, `RGWCoroutine`, and `RGWHTTPManager`, allowing RGW sync services and admin commands to create trim coroutines without depending on implementation internals.

## Risks and Edge Cases

Config values control cluster-wide trim aggressiveness; too much concurrency or too few cold buckets can starve buckets or overload OSDs. The persistent marker is a simple string cursor and must remain compatible with metadata listing behavior. `bilog_trim()` requires a valid generation and shard id.

## Test Signals

Tests should validate config loading bounds, `BucketTrimStatus` encode/decode, manager watcher initialization, observer counter updates, periodic/admin coroutine creation, and direct trim error handling for missing generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_bilog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_datalog.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_datalog.cc

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_datalog.cc` implements data-log trimming for RGW multisite. It queries peer zones for data-sync progress, computes the minimum stable marker per datalog shard, and trims local datalog entries that all peers have consumed.

## Important APIs, Types, and Functions

`DatalogTrimImplCR` sends the actual `datalog_rados->trim_entries()` request for one shard and marker. `get_stable_marker()` chooses `next_step_marker` during full sync and `marker` otherwise. `take_min_markers()` folds peer statuses into per-shard minimum markers. `DataLogTrimCR` queries all peers and spawns shard trims. `DataLogTrimPollCR` periodically takes a RADOS lock and runs trim. `create_data_log_trim_cr()` and `create_admin_data_log_trim_cr()` are the exported factories.

## Control Flow

The periodic coroutine sleeps for the configured interval, locks the first datalog shard object with lock name `data_trim`, and runs `DataLogTrimCR`; it intentionally does not unlock after success so other gateways avoid duplicate work for the lease interval. `DataLogTrimCR` sends `/admin/log/?type=data&status&source-zone=<zone>` requests to all notify targets, requires all responses to succeed, computes minimum stable markers, and spawns `DatalogTrimImplCR` only for shards whose marker advanced beyond `last_trim`.

## State and Persistence Behavior

Trimmed datalog entries are removed from RADOS by `trim_entries()`. The periodic coroutine keeps in-memory `last_trim` markers per shard to avoid repeated trims. There is no separate persisted trim cursor in this file; safety comes from peer sync markers and the RADOS lock.

## Dependencies and Integration Points

The code depends on RGW coroutine infrastructure, REST admin log status endpoints, `RGWHTTPManager`, zone service notify maps, datalog RADOS service, RADOS lock coroutine helpers, and multisite data sync marker types.

## Risks and Edge Cases

All peer status requests must succeed before trimming; one unavailable peer blocks progress. The code assumes peer marker vectors match `num_shards`; malformed or unexpected status can lead to incorrect marker folding if not caught elsewhere. `-ENODATA` from trim is treated as no data and can update `last_trim_marker` except for max marker. The lock is held for the interval by design.

## Test Signals

Tests should cover stable marker selection for full/incremental sync, minimum marker folding across peers, skipping already-trimmed shards, peer REST failure behavior, `-ENODATA` handling, lock contention in poll mode, and factory behavior for periodic versus admin trim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_datalog.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_datalog.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_datalog.h

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_datalog.h` declares factory functions for periodic and admin data-log trim coroutines.

## Important APIs, Types, and Functions

`create_data_log_trim_cr()` creates the periodic datalog trim coroutine from a `DoutPrefixProvider`, `RadosStore`, `RGWHTTPManager`, shard count, and interval. `create_admin_data_log_trim_cr()` creates a one-shot/admin trim coroutine with caller-supplied last markers.

## Control Flow

The header contains no executable flow. Callers choose the periodic factory for daemon trim loops or the admin factory for direct trim commands.

## State and Persistence Behavior

No state is owned by the header. The admin factory accepts a marker vector by reference so the implementation can update caller-visible in-memory trim positions.

## Dependencies and Integration Points

It depends on `common/dout.h`, forward-declared RGW coroutine/RADOS/HTTP types, and `utime_t`. It integrates with RGW service startup and radosgw-admin trim commands.

## Risks and Edge Cases

Callers must pass the correct shard count and a marker vector sized consistently with the datalog. Incorrect values can limit or misdirect trimming in the implementation.

## Test Signals

Compile coverage for service/admin callers and runtime tests that instantiate both factories with representative shard counts and intervals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_datalog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_mdlog.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_mdlog.cc

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_mdlog.cc` implements metadata-log trimming for RGW multisite. It handles both metadata master and peer zones, purges obsolete period logs, trims current-period mdlog shards only when safe for peer sync progress, and coordinates trim work with RADOS locks.

## Important APIs, Types, and Functions

`PurgeLogShardsCR` removes all shards for one mdlog period. `PurgePeriodLogsCR` walks mdlog period history and removes old period logs before updating the oldest-log-period cursor. `make_peer_connections()` builds REST connections for realm zones. `get_stable_marker()`, `operator<`, and `take_min_status()` calculate safe master-side trim status. `TrimEnv`, `MasterTrimEnv`, and `PeerTrimEnv` carry shared state. `MetaMasterStatusCollectCR` fetches peer metadata sync status. `MetaMasterTrimShardCollectCR` trims master mdlog shards by marker. `MetaPeerTrimShardCR` derives safe peer trim timestamps from the master's first mdlog entries. `MetaPeerTrimShardCollectCR`, `MetaMasterTrimCR`, and `MetaPeerTrimCR` coordinate master/peer flows. `MetaTrimPollCR` handles periodic lock/sleep/unlock-on-error behavior. Factory functions create periodic or admin trim coroutines.

## Control Flow

Periodic trim sleeps, locks `RGWMetadataLogHistory::oid` with lock name `meta_trim`, and runs either master or peer trim depending on `is_meta_master()`. Master trim fetches metadata sync status from all peer zones, computes the minimum realm epoch and per-shard markers, purges older period logs if peers advanced, and trims current-period shards when the minimum epoch equals the current epoch. Peer trim fetches mdlog info from the master, adopts the master's shard count, purges old period logs if the master advanced, and for current-period shards reads the master's first entry or shard info to compute a safe timestamp before trimming local mdlog entries older than that.

## State and Persistence Behavior

The code deletes mdlog shard objects from the zone log pool, updates mdlog history/oldest-log-period metadata through `svc_mdlog`, and trims timelog entries. In-memory state tracks last purged epoch, last current-period master trim markers, and last peer trim timestamps. Locks are RADOS objects in the log pool. No independent trim status object is introduced here.

## Dependencies and Integration Points

Dependencies include RGW sync types, metadata log service, zone service and period history, cls/log trim coroutines, REST admin log status endpoints, master connection helpers, RADOS lock/remove/timelog trim coroutines, and RGWHTTPManager. The implementation is tightly coupled to realm period history and multisite metadata sync status.

## Risks and Edge Cases

Endpoint sanity checks refuse trimming if any zone has no endpoint, because peer status/master reads would be unsafe. Master trim requires all peer status responses and matching shard counts. Peer timestamp trimming subtracts one second from the master's first entry timestamp, which is conservative but depends on timestamp ordering. Purging period logs races with other gateways; `-ENOENT` is treated as a successful race. Periodic trim intentionally keeps the lock after success but unlocks on errors so another gateway can try.

## Test Signals

Important tests include endpoint sanity checks, peer connection construction, minimum status calculation across epochs and markers, shard-count mismatch, period purge races, master current-period marker trims, peer empty/non-empty master shard timestamp derivation, old period purge on master/peer, lock contention and unlock-on-error, and factory selection for master versus peer zones.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_mdlog.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_mdlog.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_mdlog.h

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_mdlog.h` declares factory functions for metadata-log trim coroutines.

## Important APIs, Types, and Functions

`create_meta_log_trim_cr()` creates the daemon periodic metadata-log trim coroutine. `create_admin_meta_log_trim_cr()` creates a one-shot/admin metadata-log trim coroutine. Both take a `DoutPrefixProvider`, `RadosStore`, `RGWHTTPManager`, and shard count; the periodic factory also takes a `utime_t` interval.

## Control Flow

The header has no executable flow. The implementation chooses master or peer trim behavior based on the zone service's metadata-master role and validates endpoints before returning a coroutine.

## State and Persistence Behavior

No state is owned by the header. The returned coroutines mutate mdlog RADOS state and mdlog history through the implementation.

## Dependencies and Integration Points

The header forward declares RGW coroutine, RADOS store, HTTP manager, and interval types. It is consumed by RGW service startup and radosgw-admin trim paths.

## Risks and Edge Cases

Callers must provide the correct shard count and a live HTTP manager; a null returned coroutine from failed endpoint sanity checks must be handled by callers.

## Test Signals

Compile coverage for daemon/admin callers and runtime tests for factory behavior in metadata-master and peer zones, including misconfigured endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_mdlog.h -->
