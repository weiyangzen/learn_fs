# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/JournalMasterFactory.java

## Purpose
`JournalMasterFactory` creates and registers the master-domain `JournalMaster` during master startup.

## Important APIs, types, and functions
It implements `MasterFactory`. `isEnabled()` always returns true. `getName()` returns `Constants.JOURNAL_MASTER_NAME`. `create(MasterRegistry, MasterContext)` constructs `DefaultJournalMaster` with `JournalDomain.MASTER`, registers it under `JournalMaster.class`, and returns it.

## Control flow
Creation is unconditional and logs the class name before registration.

## State and persistence behavior
The factory is stateless. The created journal master is no-op journaled and delegates to the journal system.

## Dependencies and integration points
It depends on master registry/context/factory APIs, constants, `JournalDomain`, and `DefaultJournalMaster`. Master bootstrap uses it in the factory list.

## Risks
This factory only creates the master-domain journal master; job-master domain creation must be handled elsewhere. Since `isEnabled` is unconditional, failures in journal master creation affect all master startups.

## Test signals
Tests should cover enabled/name values, registry insertion, returned instance type, journal domain passed to `DefaultJournalMaster`, and logging is not functionally required.
