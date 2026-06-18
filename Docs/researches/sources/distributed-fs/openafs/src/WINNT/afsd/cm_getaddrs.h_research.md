# sources/distributed-fs/openafs/src/WINNT/afsd/cm_getaddrs.h

Purpose: declares the Windows cache-manager server-address discovery interface backed by the VLDB `GetAddrsU` RPC cache.

Important APIs/types/functions: `cm_GetAddrsU()` accepts a cell, user, request, server UUID/unique pair, caller-supplied flags, an in/out server-array index, and parallel arrays for server flags, IPv4 addresses, UUIDs, and unique values. `cm_getaddrsInit()` and `cm_getaddrsShutdown()` manage the module lock lifecycle.

Control flow and state: the header exposes no state directly; callers treat `cm_GetAddrsU()` as an append operation into existing server arrays. The implementation performs in-memory caching and VLDB RPC retry internally.

Dependencies and integration: requires OpenAFS cache-manager types (`cm_cell_t`, `cm_user_t`, `cm_req_t`), `afsUUID`, and fixed-size server arrays used by volume/cell discovery.

Risks: the API is array-based and relies on caller discipline for array size and initialized `index`; it returns AFS status codes but also mutates partial output arrays on success.

Test signals: compile users against this header, initialize/shutdown around cache-manager lifecycle, and verify multi-address UUID servers append expected parallel entries.
