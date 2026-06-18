# sources/distributed-fs/openafs/src/WINNT/afsd/cm_getaddrs.c

Purpose: caches VLDB `VL_GetAddrsU` results that map a file-server UUID and unique value to one or more server IP addresses, then appends those addresses to volume server arrays used by the Windows cache manager.

Important APIs/types/functions: private `uuid2addrsEntry_t` stores queue linkage, UUID, unique value, address count, XDR `bulkaddrs`, refcount, and delete flags. `cm_getaddrsFind()` looks up a usable cached entry where requested unique is not newer than cached unique. `cm_getaddrsAdd()` inserts or updates cache entries and owns/free-transfers the `bulkaddrs` payload. `cm_getaddrsPut()` decrements references. Public `cm_GetAddrsU()` performs cache lookup, VLDB RPC fallback, result caching, and output array population. `cm_getaddrsInit()` initializes `cm_getaddrsLock` once; `cm_getaddrsShutdown()` finalizes it.

Control flow: `cm_GetAddrsU()` first probes the hash table. On miss, it constructs `ListAddrByAttributes` with `VLADDR_UUID`, loops over VL servers through `cm_ConnByMServers`, invokes `VL_GetAddrsU`, and lets `cm_Analyze` retry/rotate servers. RPC errors are mapped with `cm_MapVLRPCError`; failures free the XDR address list and return `CM_ERROR_RETRY`. Successful replies clamp `nentries` to `bulkaddrs_len`, reject empty replies, and pass ownership into `cm_getaddrsAdd()`. The returned cached entry is copied into `serverFlags`, `serverNumber`, `serverUUID`, and `serverUnique` until `NMAXNSERVERS` is reached.

State and persistence: state is an in-memory 128-bucket hash table protected by `cm_getaddrsLock`; it is not persisted. XDR-allocated address arrays are freed when obsolete unreferenced entries are encountered or when duplicate/outdated input is discarded.

Dependencies and integration: integrates with OpenAFS queue helpers, jhash, RX/VL RPC stubs, connection selection and error analysis, `cm_cell_t` VL server lists, and volume-location code that maintains server arrays.

Risks: `cm_getaddrsPut()` mutates `refCount` under a read lock, which relies on local lock semantics and is easy to regress; delete flags exist but no public invalidation path is in this file; cache growth is only bounded by UUID churn and cleanup during later adds; callers must provide arrays sized for `NMAXNSERVERS` and a valid `index`.

Test signals: cache hit with older/equal unique should avoid RPC; newer unique should replace unused old data; duplicate/outdated RPC result should be freed; VLDB server failover should retry; empty address results should return invalid; output should stop exactly at `NMAXNSERVERS`.
