# sources/distributed-fs/glusterfs/xlators/performance/nl-cache/src/nl-cache.h

Purpose: shared interface and data model for `nl-cache.c` and `nl-cache-helper.c`.

Important APIs, types, and functions: defines state bits `NLC_PE_FULL`, `NLC_PE_PARTIAL`, `NLC_NE_VALID`, validation macros, `NLC_STACK_UNWIND`, `nlc_ne_t`, `nlc_pe_t`, `nlc_timer_data_t`, `nlc_lru_node_t`, `nlc_ctx_t`, `nlc_local_t`, `nlc_statistics`, and `nlc_conf_t`. Declares helper functions for dentry additions/removals, negative lookup checks, real filename lookup, cache clearing, LRU pruning, child-down time, local management, and statedump.

Control flow: the macros and prototypes establish the contract that fop wrappers allocate `nlc_local_t`, helper functions mutate per-directory ctx under locks, and unwind paths must wipe locals.

State and persistence: declares all in-memory state used by the translator, including per-directory PE/NE lists, cache timers, cache size, ref counts, global LRU, and counters. No disk persistence.

Dependencies and integration: includes nl-cache memory/message headers, Gluster defaults, and atomics. It is the compile-time coupling point between the front-end fop file and the helper engine.

Risks and test signals: changing struct layout or state bits affects both implementation files and statedump interpretation. Tests should compile both files together and validate that each declared helper has one implementation with consistent lock/memory ownership.
