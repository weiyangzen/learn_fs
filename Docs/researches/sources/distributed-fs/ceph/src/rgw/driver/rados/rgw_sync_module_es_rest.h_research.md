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
