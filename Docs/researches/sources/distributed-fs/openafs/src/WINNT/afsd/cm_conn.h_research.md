# sources/distributed-fs/openafs/src/WINNT/afsd/cm_conn.h

## Purpose
`cm_conn.h` declares the Windows cache manager's connection and request-analysis contract. It defines timeout defaults, connection objects, per-request retry/error tracking, AFS volume special errors, capability helpers, and the APIs used by filesystem operations to obtain and analyze Rx connections.

## Important APIs and Types
`cm_conn_t` stores list linkage, server pointer, Rx connection pointer, held user, mutex, refcount, ucell generation, flags, and crypt level. `cm_req_t` stores request start time, categorized error state, retry counters, flags, and path context from SMB or redirector callers. Flags include no-retry, forced-new-connection, source markers, WOW64, volume-updated, and offline-volume-check markers. Exported routines include initialization, `cm_Analyze`, server/volume/FID connection selection, Rx connection reference retrieval, GC, server availability, and connection forcing.

## Control Flow
Callers pass a `cm_req_t` through connection acquisition and RPC retry loops. A successful `cm_ConnFromFID` or `cm_ConnFromVolume` returns a held `cm_conn_t` that is normally released by the following `cm_Analyze` call. Callers use `SERVERHAS64BIT`/`SERVERHASINLINEBULK` macros to gate file-server feature use and mark unsupported features via the corresponding setters.

## State and Persistence
The header exposes timeout globals and `rx_pmtu_discovery`, all in-process runtime settings initialized elsewhere. Request state is transient per operation; connection state is transient per server/user/security tuple.

## Dependencies and Integration Points
It includes `cm_server.h` and Rx headers, references user, FID, cell, volume, server-ref, callback, fetch-status, and volsync structures, and provides constants used by SMB/redirector-facing operations.

## Risks and Test Signals
Tests should validate request flag behavior, refcount ownership expectations, timeout defaults for SMB versus redirector mode, replicated connection separation, and handling of AFS special volume errors. Header changes are high blast radius because most RPC call sites depend on these signatures.
