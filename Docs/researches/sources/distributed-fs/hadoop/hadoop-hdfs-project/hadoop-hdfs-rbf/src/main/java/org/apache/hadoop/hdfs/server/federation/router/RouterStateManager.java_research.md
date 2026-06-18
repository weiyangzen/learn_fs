# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterStateManager.java

## Purpose
`RouterStateManager` defines the admin/state-store contract for changing and querying Router safe mode state.

## Important APIs and Types
It declares `enterSafeMode(EnterSafeModeRequest)`, `leaveSafeMode(LeaveSafeModeRequest)`, and `getSafeMode(GetSafeModeRequest)`, returning the corresponding protocol response types. All methods throw `IOException`.

## Control Flow
Implementations are expected to translate admin/state-store requests into Router safe-mode changes, probably by calling `RouterSafemodeService.setManualSafeMode` and updating `RouterServiceState`.

## State and Persistence
The interface stores nothing. Implementations may update in-memory Router state and state-store records that advertise Router availability.

## Dependencies and Integration Points
It depends on federation store protocol request/response types. It is the abstraction for Router admin RPCs or state-store service code that manages safe mode.

## Risks
Because this is an interface, consistency depends on implementation behavior. Enter/leave operations must coordinate manual safe mode with automatic stale-cache safe mode to avoid accidental exit while State Store data is stale.

## Test Signals
Tests should verify admin enter/leave/get behavior, idempotency, IOException propagation, and Router state transitions through the concrete implementation.
