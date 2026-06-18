# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/options/MountInfoTest.java

## Purpose
`MountInfoTest` validates the simple mount metadata value object.

## Important APIs, Types, and Functions
It constructs `MountInfo` with Alluxio URI, UFS URI, mount id, and `MountPOptions`, then exercises `getAlluxioUri`, `getUfsUri`, `getOptions`, `getMountId`, and `toUfsInfo`.

## Control Flow, State, and Persistence
The test performs direct field round-trip assertions and converts to gRPC `UfsInfo`. No mutable or persistent state is used.

## Dependencies and Integration Points
It depends on `AlluxioURI`, `MountContext.defaults`, `MountPOptions`, and the `UfsInfo` wire type consumed by mount-related APIs.

## Risks
The main risk is serialization drift: `toUfsInfo` currently exposes the UFS URI string but not every `MountInfo` field.

## Test Signals
The signal is basic constructor/getter/wire conversion integrity for mount table entries.
