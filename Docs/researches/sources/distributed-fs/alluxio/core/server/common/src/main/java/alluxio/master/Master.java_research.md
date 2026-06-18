# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/Master.java

## Purpose
`Master` defines the common contract for Alluxio master services.

## Important APIs, Types, And Functions
It extends `Journaled` and `Server<Boolean>`, requiring lifecycle, service, journaling, checkpoint, and journal-entry iteration behavior. It adds `createJournalContext`, `getMasterContext`, and default `getStandbyServices`.

## Control Flow, State, Dependencies, Risks, And Tests
Implementations use `createJournalContext` for persistent journal writes and `Journaled` methods for replay/checkpoint. Standby services default to none. Dependencies include gRPC service descriptors, `ServiceType`, journal contexts, and server lifecycle APIs. Risks are broad implementor responsibility: state changes must both mutate memory and journal consistently, and standby service exposure is optional. Tests should validate each master implementation's service maps, context creation behavior, journal replay support, and lifecycle interaction with primary/standby booleans.
