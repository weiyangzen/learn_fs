# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/AbstractMaster.java

## Purpose
`AbstractMaster` is the base implementation for Alluxio master services, providing common lifecycle, executor, journal creation, and state-lock-aware journal context handling.

## Important APIs, Types, And Functions
The constructor stores `MasterContext`, `Clock`, an `ExecutorServiceFactory`, and creates this master's journal from the journal system. `start` creates the maintenance executor and records primary/standby mode. `stop` interrupts and waits for executor shutdown. `createJournalContext` acquires the shared state lock and wraps the journal context in `StateChangeJournalContext`.

## Control Flow, State, Dependencies, Risks, And Tests
Primary startup is expected to occur after journal replay and before RPC serving, while state mutations later journal through a shared lock so backups can pause them. Persistent state is owned by the journal; this class guards writes through `JournalContext`. Dependencies include `JournalSystem`, `StateLockManager`, `ExecutorServiceFactory`, and `LockResource`. Risks include non-thread-safe lifecycle, failure to release locks when journal context creation fails, and executor shutdown timeout leaving background work. Tests should cover start/stop idempotency expectations, lock acquisition failure mapping to `UnavailableException`, and `StateChangeJournalContext` close ordering.
