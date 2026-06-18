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
