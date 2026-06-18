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
