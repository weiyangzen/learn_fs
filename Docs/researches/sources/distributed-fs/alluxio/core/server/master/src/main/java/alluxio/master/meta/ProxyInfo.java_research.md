# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/ProxyInfo.java

## Purpose
`ProxyInfo` stores liveness and version metadata for an Alluxio proxy process as tracked by the meta master.

## Important APIs and Types
- Fields include immutable `NetAddress mAddress`, last heartbeat time, start time, version, and revision.
- Constructor initializes address and sets last heartbeat to current time.
- Getters expose address, heartbeat time, start time, version, and revision.
- Setters update start time, version, and revision.
- `updateLastHeartbeatTimeMs()` refreshes liveness timestamp via `CommonUtils.getCurrentMs()`.
- `toString()` uses Guava `MoreObjects.toStringHelper`.

## Control Flow
Meta master proxy heartbeat handling creates or updates `ProxyInfo`, sets metadata from heartbeat options, and calls `updateLastHeartbeatTimeMs` on each heartbeat.

## State and Persistence
This is in-memory liveness state. It is not itself journaled in this file.

## Dependencies and Integration Points
Uses wire `NetAddress`, `CommonUtils`, and Guava string helper. Integrated with proxy heartbeat service handling and cluster status reporting.

## Risks and Edge Cases
Annotated `NotThreadSafe`; callers must synchronize or confine updates. Default version/revision are empty strings and start time defaults to zero until reported.

## Test Signals
Tests should verify initial heartbeat timestamp, setters/getters, heartbeat time refresh, and string representation including expected fields.
