<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/metadata.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/metadata.c

## Purpose
`metadata.c` owns Flower flow identity and lookup metadata: stats context allocation, mask ID allocation/reuse, flow-table hashing, stats updates from firmware, merge/conntrack/neigh rhashtable parameters, metadata initialization, and cleanup.

## Important APIs, Types, And Functions
The public APIs are `nfp_flower_metadata_init()`, `nfp_flower_metadata_cleanup()`, `nfp_compile_flow_metadata()`, `nfp_modify_flow_metadata()`, `__nfp_modify_flow_metadata()`, `nfp_flower_search_fl_table()`, `nfp_flower_get_fl_payload_from_ctx()`, and `nfp_flower_rx_flow_stats()`. Internal types map mask hashes to IDs (`nfp_mask_id_table`) and stats contexts to payloads (`nfp_fl_stats_ctx_to_flow`).

## Control Flow
New flow setup calls `nfp_get_stats_entry()`, inserts a stats-context-to-flow entry, allocates or reuses a mask ID unless the flow is a pre-tunnel rule, stamps a monotonically increasing `flower_version`, writes the mask ID into the compiled exact key, initializes stats, and checks for duplicate `(cookie, ingress_dev)` flow table entries. Flow modification/deletion clears manage-mask intent, increments version, releases mask ID when appropriate, removes stats-context mapping, and returns the stats context ID to the free ring. Firmware stats messages are parsed as repeated `nfp_fl_stats_frame` records and accumulated under `stats_lock`.

## State And Persistence
State is in memory only. Stats IDs use a circ_buf plus an initial unallocated range spread over firmware memory units. Mask IDs use a circ_buf, a hash table keyed by `jhash(mask_data)`, refcounts, and a `NFP_FL_MASK_REUSE_TIME_NS` holdoff before reuse. Flow table keys are tc cookie plus ingress netdev. Cleanup destroys flow, stats, merge, conntrack zone/map, and neighbor tables and frees rings and stats arrays.

## Dependencies And Integration Points
The file uses rhashtable, Jenkins hashes, vmalloc/kvmalloc, Flower conntrack cleanup helpers, and the app-private `nfp_flower_priv`. It is on the critical path for add/delete/stats in `offload.c`, CT handling, merge-flow tracking, and tunnel neighbor table cleanup.

## Risks
`nfp_search_mask_table()` compares only the mask hash, not the mask bytes, so a hash collision would incorrectly share a mask ID. Stats array sizing uses encoded field preparation and assumes firmware-provided counts align with host context ID encoding. Error paths must unwind stats context, mask IDs, and hash inserts in the right order. Cleanup warns and forcibly clears non-empty conntrack lists, indicating teardown expects higher layers to delete flows first.

## Test Signals
Important tests include duplicate tc cookie rejection per ingress device, mask ID refcounting and delayed reuse, stats context exhaustion/reuse, firmware stats accumulation and TC stats drain, pre-tunnel metadata without mask allocation, teardown with empty and deliberately non-empty CT tables, and hash-collision or fault-injection tests for insert/allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/metadata.c -->
