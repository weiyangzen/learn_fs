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
