# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSNetworkProviderSupport.cpp

## Purpose
`AFSNetworkProviderSupport.cpp` is the redirector-library side of the Windows network-provider connection interface. It maintains per-logon-session mapped-drive and UNC connection records, exposes add/cancel/get/list/get-info helpers for provider IOCTLs, validates AFS `\\server\share` names against the redirector's global-root namespace, and bridges provider enumeration requests into live AFS directory enumeration.

## Important APIs, Types, And Functions
The main entry points are `AFSAddConnection`, `AFSCancelConnection`, `AFSGetConnection`, `AFSListConnections`, `AFSInitializeConnectionInfo`, `AFSLocateEnumRootEntry`, `AFSEnumerateConnection`, `AFSGetConnectionInfo`, and `AFSIsDriveMapped`. They exchange packed `AFSNetworkProviderConnectionCB` and `AFSCancelConnectionResultCB` records with callers and store kernel-side state in `AFSProviderConnectionCB`.

`AFSAddConnection` obtains `AFSGetAuthenticationId`, rejects duplicates, validates the server against `AFSServerName`, validates the share through `AFSLocateEnumRootEntry`, allocates a provider node plus inline remote-name storage, initializes resource metadata, and appends to `ProviderConnectionList`. `AFSCancelConnection` removes and frees one matching connection. `AFSGetConnection` maps a local drive to its remote UNC path. `AFSListConnections` handles both connected-resource enumeration and `RESOURCE_GLOBALNET` namespace enumeration. `AFSGetConnectionInfo` finds the best component-boundary connection prefix or dynamically creates a valid share entry through `AFSEvaluateTargetByName` and `AFSAddConnectionEx`.

## Control Flow
Provider-list mutation is protected by `ProviderListLock` in exclusive mode; read/enumeration paths use shared mode. Add flow normalizes names, searches the list, validates server/share, allocates/copies a node, derives `ComponentName`, and appends. List flow either walks provider enumeration roots, enumerates share directory entries through `AFSEnumerateConnection`, or filters attached connections by authentication id. Connection-info flow intentionally validates only the server/share prefix and returns any deeper path as `RemainingPath`.

## State And Persistence Behavior
State is in-memory redirector state in `AFSDeviceExt->Specific.RDR.ProviderConnectionList` and `ProviderEnumerationList`. Nodes own inline `RemoteName` storage and separately allocated `Comment.Buffer` strings. There is no disk persistence; durable Windows mappings are outside this file, while namespace freshness depends on global-root and service-backed directory evaluation.

## Dependencies And Integration Points
The code depends on `FsRtlDissectName`, `RtlCompareUnicodeString`, provider structures from `common/AFSProvider.h`, redirector globals (`AFSRDRDeviceObject`, `AFSGlobalRoot`, `AFSServerName`), allocation callbacks, lock helpers, B-tree directory lookup, `AFSEvaluateRootEntry`, `AFSEvaluateTargetByName`, and the external `AFSAddConnectionEx` callback. `AFSIsDriveMapped` integrates directly with name parsing for drive-letter opens.

## Risks And Edge Cases
The linked-list ownership is manual, including inline remote names and allocated comments. Some parsing paths adjust `UNICODE_STRING.Buffer` to point inside an allocation; `AFSListConnections` advances the allocated remote-name buffer when trimming leading slashes and later frees the adjusted pointer, a cleanup risk. `AFSGetConnectionInfo` has a diagnostic path that logs an uninitialized local `UNICODE_STRING`. Partial-prefix matching is intentional but can produce false positives below a share. Add and get-info differ because get-info can dynamically create share entries.

## Test Signals
Test duplicate adds, mapped-drive and UNC-only connections, per-authentication-id isolation, invalid server/share names, cancellation by drive and UNC, top-level/global/share enumeration, `CurrentIndex` resume, buffer-full handling, comment and remaining-path offsets, dynamic share creation, case-insensitive share collisions, low-memory allocation failures, and concurrent add/cancel/list operations.
