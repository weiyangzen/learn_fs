<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/tracing_map.h -->
# sources/distributed-fs/ceph-client/kernel/trace/tracing_map.h

Purpose: declares the tracing aggregation map ABI used inside the kernel tracing subsystem. The header documents the relationship between map entries, element pools, key/sum fields, sort entries, and client callbacks.

Important types and constants: `TRACING_MAP_BITS_*` bounds map size; `TRACING_MAP_KEYS_MAX`, `TRACING_MAP_VALS_MAX`, `TRACING_MAP_FIELDS_MAX`, and `TRACING_MAP_VARS_MAX` bound field capacity. Core types include `struct tracing_map`, `struct tracing_map_entry`, `struct tracing_map_elt`, `struct tracing_map_field`, `struct tracing_map_array`, `struct tracing_map_sort_key`, and `struct tracing_map_sort_entry`. `struct tracing_map_ops` defines optional `elt_alloc`, `elt_free`, `elt_clear`, and `elt_init` hooks.

Control flow and API contract: clients create a map, add key and sum fields, optionally add variables, call `tracing_map_init()` to preallocate elements, then use insert/lookup/update during tracing. Sorting returns an allocated array that the caller must destroy. The array macros map logical indices onto page-backed arrays and are central to the implementation.

State and persistence: the header describes a no-delete in-memory table with a preallocated element pool. `hits` and `drops` counters are part of `struct tracing_map`. `private_data` exists at both map and element levels for client ownership.

Dependencies and integration: this is included by tracing map implementation and tracing clients. It exports comparison helpers and update/read helpers rather than exposing internal insertion details.

Risks: consumers must respect fixed limits and the required setup order. Destroying sort entries and map instances is caller-owned. Misusing field indexes, offsets, or sort keys can produce invalid comparisons. Test signals include compile-time consumers across histogram code, limit boundary tests, and API misuse tests that expect `-EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/tracing_map.h -->
