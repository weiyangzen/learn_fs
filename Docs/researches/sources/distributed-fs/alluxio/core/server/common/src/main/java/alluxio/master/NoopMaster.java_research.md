# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/NoopMaster.java

## Purpose
`NoopMaster` is a placeholder master for tests and formatting paths that require a master identity without real services or state.

## Important APIs, Types, And Functions
Constructors accept default/custom names and optional `UfsManager`, building a `MasterContext` with `NoopJournalSystem` and `AlwaysStandbyPrimarySelector`. It implements `Master` and `NoopJournaled`, returns its name/context, no-ops lifecycle, and rejects `createJournalContext`.

## Control Flow, State, Dependencies, Risks, And Tests
There is no persisted state. The class is integrated by `Format` and journal setup to create named journals without real masters. Dependencies include noop journal and primary selector classes. Risks include returning `null` from `getDependencies` and `getServices`, which can surprise callers expecting empty collections, and illegal journal context creation. Tests should cover constructors, name propagation, context composition, no-op checkpoint behavior, and callers' tolerance of null service/dependency maps.
