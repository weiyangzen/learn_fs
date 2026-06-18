# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/indexer.h

## Purpose
Defines the public UDS API: request types, open modes, parameters, record name/data formats, index statistics, request structure, session operations, and condition-variable helpers.

## Important APIs, Types, And Functions
Important enums are `uds_request_type`, `uds_open_index_type`, `uds_index_region`, and `uds_zone_message_type`. Important data structures are `uds_record_name`, `uds_record_data`, `uds_volume_record`, `uds_parameters`, `uds_index_stats`, `uds_zone_message`, `uds_request`, and `cond_var`. Public functions include `uds_compute_index_size()`, session create/open/suspend/resume/flush/close/destroy/stat APIs, and `uds_launch_request()`.

`struct uds_request` separates required client inputs, callback outputs, and an internal `struct_group` used by queues, index routing, message handling, and location tracking. Records use 16-byte names and 16-byte metadata.

## Control Flow
Clients create a session, open or create an index with `uds_parameters`, initialize a request, and call `uds_launch_request()`. Completion is asynchronous through the request callback. Session control APIs gate new requests and can save, suspend, resume, flush, or close the index.

## State And Persistence
The header describes client-visible state and statistics rather than persistence mechanics. `uds_parameters` carry block device, size, offset, memory size, sparse flag, nonce, zone count, and read-thread count, which determine the persistent layout and geometry produced by implementation files.

## Dependencies And Integration Points
Includes kernel mutex/wait/types headers and `funnel-queue.h`. It is the top-level interface consumed by dm-vdo code outside the indexer and by all internal indexer modules.

## Risks
Clients must not mutate internal request fields and must keep request storage valid until callback. Invalid names are not structurally rejected, but poor hash distribution can reduce capacity. API state rules matter: operations during suspended/loading/disabled states fail with busy/no-index/disabled errors.

## Test Signals
API tests should verify request type behavior, callback reuse safety, invalid argument handling, index size calculation, stats fields, sparse/dense configurations, and lifecycle operations under concurrent clients.
