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
