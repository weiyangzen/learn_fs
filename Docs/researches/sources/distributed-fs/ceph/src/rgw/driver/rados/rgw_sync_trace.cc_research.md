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
