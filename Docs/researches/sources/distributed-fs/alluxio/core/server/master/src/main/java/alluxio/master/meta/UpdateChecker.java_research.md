# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/UpdateChecker.java

## Purpose
`UpdateChecker` is a heartbeat executor that periodically checks for newer Alluxio versions, logs update availability with coarse cluster-size information, and marks the meta master when a newer version is detected.

## Important APIs and Types
- Implements `HeartbeatExecutor`.
- Holds a `MetaMaster` reference.
- `heartbeat(long)` builds additional info including worker count and calls `UpdateCheck.getLatestVersion` with 3-second connect/read/write timeouts.
- `close()` is a no-op.

## Control Flow
On heartbeat, it calls `mMetaMaster.getWorkerAddresses().size()` to report worker count, using `-1` when no workers are known, asks the update checker for the latest version, and compares it with `ProjectConstants.VERSION`. If they differ, it logs an upgrade message and calls `mMetaMaster.setNewerVersionAvailable(true)`. All throwables are caught and logged at debug level.

## State and Persistence
No local persistent state. It performs outbound version-check IO, logging, and updates the meta master's in-memory newer-version flag.

## Dependencies and Integration Points
Depends on `HeartbeatExecutor`, `ProjectConstants`, `MetaMaster`, and `alluxio.check.UpdateCheck`. It is scheduled by meta master maintenance when update checking is enabled.

## Risks and Edge Cases
- Network and unexpected failures are intentionally non-fatal and only debug logged.
- The class is `NotThreadSafe`; scheduler should not invoke concurrently.
- Version-check behavior depends on external service availability and privacy policy around reported info.
- A null or unexpected latest-version value would compare unequal to the current version and set the newer-version flag.

## Test Signals
Tests can mock `MetaMaster`/update-check utility to verify worker count formatting, `-1` for no workers, newer-version flag updates, logging on version mismatch, and swallowed throwables.
