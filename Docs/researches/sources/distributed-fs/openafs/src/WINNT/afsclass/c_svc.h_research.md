# sources/distributed-fs/openafs/src/WINNT/afsclass/c_svc.h

## Purpose

`c_svc.h` declares `SERVICE`, the AfsClass object for a BOS service/process and related status/key types.

## Important APIs, Types, and Functions

It defines `AFSSERVICETYPE`, `SERVICESTATE`, `SERVICESTATUS`, `ENCRYPTIONKEY`, and `ENCRYPTIONKEYINFO`. `SERVICE` exposes close/invalidate/refresh, identity and parent navigation, name/status getters, and user-param accessors.

## Control Flow

The class follows the lazy-refresh pattern and is normally obtained from a `SERVER` service list or opened by name.

## State and Persistence Behavior

The service object caches BOS process status, parent identifiers, service name, and stale flag. Key structs are shared by server-key APIs declared elsewhere.

## Dependencies and Integration Points

It depends on `afsclass.h`, Win32 `SYSTEMTIME`, AfsClass identifiers, and server/service management operations in `afsclassfn.h`.

## Risks and Edge Cases

`SERVICESTATUS` contains fixed-size strings for params/notifier/aux status. Callers should expect truncation or overflow risk in old implementation paths. Service state is a snapshot and must be invalidated or refreshed before use after operations.

## Test Signals

Compile tests should validate status/key ABI. Functional tests should verify service enumeration, status refresh, start/stop/restart operation refresh, and user-param attachment.
