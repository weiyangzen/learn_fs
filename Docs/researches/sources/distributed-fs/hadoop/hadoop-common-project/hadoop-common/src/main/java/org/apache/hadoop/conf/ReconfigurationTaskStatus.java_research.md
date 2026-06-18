# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ReconfigurationTaskStatus.java`

## Purpose

`ReconfigurationTaskStatus` is a lightweight status value object for the most recent background reconfiguration task.

## Important APIs and Types

The constructor accepts `startTime`, `endTime`, and a map from `ReconfigurationUtil.PropertyChange` to `Optional<String>` error messages. Public methods are `hasTask`, `stopped`, `getStartTime`, `getEndTime`, and `getStatus`.

## Control Flow

`hasTask` reports whether any task has started by checking `startTime > 0`. `stopped` reports that a task has finished by checking `endTime > 0`. A running task is represented by nonzero start, zero end, and null status.

## State and Persistence

The object stores package-visible `startTime` and `endTime`, plus a final status map reference. It does not defensively copy the map, so immutability depends on the producer. There is no persistence.

## Dependencies and Integration Points

It is produced by `ReconfigurableBase.getReconfigurationTaskStatus` and consumed by management APIs/tools. It uses `Optional` to distinguish success from a property-specific error message.

## Risks

Null status is a legitimate running-state value, so clients must check `stopped()` before iterating. Package-visible timestamp fields are mutable within the package. Status contains `PropertyChange` keys whose class does not override equality/hashCode, which is acceptable for direct reporting but not semantic lookup across separately constructed changes.

## Test Signals

Tests should verify running, never-started, and completed states; null status handling; success/error optional semantics; and that callers do not assume `getStatus()` is non-null before completion.
