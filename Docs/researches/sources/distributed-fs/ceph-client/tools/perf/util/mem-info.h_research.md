# sources/distributed-fs/ceph-client/tools/perf/util/mem-info.h

## Purpose

`mem-info.h` defines the refcounted memory sample metadata object used across perf memory analysis.

## Important APIs, Types, and Functions

`DECLARE_RC_STRUCT(mem_info)` contains instruction address `iaddr`, data address `daddr`, `union perf_mem_data_src data_src`, and `refcount_t refcnt`. The header declares new/clone/get/put and defines zput plus inline accessors for instruction address, data address, data source, const data source, and refcount.

## Control Flow

There is no implementation flow. Inline accessors return addresses of fields through rc-check access.

## State and Persistence Behavior

`mem_info` persists resolved address metadata and kernel-provided memory data-source bits. Refcounting controls lifetime; embedded map-symbol fields own thread/map references according to implementation helpers.

## Dependencies and Integration Points

It depends on Linux refcount, perf event memory data-source definitions, rc-check infrastructure, and `map_symbol.h`. It is consumed by machine sample resolution, mem-events formatting, c2c, hist entries, and scripts.

## Risks and Edge Cases

All accessors assume a valid `mem_info` pointer. The object contains borrowed symbol pointers through `addr_map_symbol`, so map/DSO lifetime must be managed by the owned map references. Any new field must be added to clone and free paths.

## Test Signals

Compile tests should cover accessors in const and mutable contexts. Runtime tests should verify zput nulls pointers and final put releases embedded address references.
