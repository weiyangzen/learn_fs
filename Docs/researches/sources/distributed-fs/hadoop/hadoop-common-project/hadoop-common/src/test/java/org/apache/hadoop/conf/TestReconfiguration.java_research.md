# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestReconfiguration.java

## Purpose

`TestReconfiguration` validates Hadoop's runtime reconfiguration framework. It covers property-difference detection, synchronous reconfiguration, visibility of configuration changes across threads, asynchronous reconfiguration task status, single-task enforcement, shutdown behavior, and correct updates/unsets of the parent cached configuration after successful reconfiguration.

## Important APIs and types

- `ReconfigurationUtil.getChangedProperties(Configuration newConf, Configuration oldConf)` returns `PropertyChange` records.
- `ReconfigurableBase` methods under test include `reconfigureProperty`, `startReconfigurationTask`, `getReconfigurationTaskStatus`, `shutdownReconfigurationTask`, `getConf`, `isPropertyReconfigurable`, and subclass hooks.
- Local `ReconfigurableDummy` implements synchronous behavior and `Runnable`.
- Local `AsyncReconfigurableDummy` blocks in `reconfigurePropertyImpl` with a latch to make running-task state observable.
- `ReconfigurationTaskStatus` exposes task start/end/stopped/hasTask state and per-property status.

## Control flow

`setUp` builds two configurations with one unchanged property, one changed property, one removed property, and one newly added property. `testGetChangedProperties` asserts all three change kinds are reported.

`testReconfigure` creates a dummy with three reconfigurable properties, verifies `isPropertyReconfigurable`, and exercises setting same value, null, changed value, unset-to-null, unset-to-value, and failures for non-reconfigurable properties. `testThread` runs a loop that watches a property until a synchronous reconfiguration changes it.

`testAsyncReconfigure` spies an async dummy to return synthetic changes, mark some properties reconfigurable, return success for one property, report non-reconfigurable for another, and throw for a third. It starts the background task, waits for stopped status, and inspects result messages. `testStartReconfigurationFailureDueToExistingRunningTask` holds the first task with a latch, verifies a second start fails, releases the task, starts a later task, then shuts down and verifies future starts fail. The final tests use `makeReconfigurable` to prove successful sync/async reconfiguration updates or unsets the stored `Configuration`.

## State and persistence behavior

State is held in `Configuration` objects owned by `ReconfigurableBase` and in background task status. No files are written. Asynchronous tests create background threads and must release latches/shutdown tasks to avoid lingering work.

## Dependencies and integration points

The suite integrates configuration comparison utilities, runtime reconfigurable services, `SubjectInheritingThread`, Hadoop `Time`, `GenericTestUtils.waitFor`, AssertJ, Mockito spies/stubs, latches, and optional status strings. It models behavior used by long-running Hadoop daemons that change selected configuration values without restart.

## Risks and edge cases

- Async task tests are timing-sensitive; helper polling must balance reliability and runtime.
- Property status maps omit successful changes without messages, so assertions must distinguish no-error optional from absent result.
- The parent configuration should only change after hook success; exception paths need careful coverage because partial changes could leave runtime state inconsistent.
- Starting after shutdown must fail deterministically to prevent task leaks.

## Test signals

Strong signals include change-kind detection, sync and async mutation/unset behavior, non-reconfigurable rejection, exception capture in task status, running-task exclusion, task timestamp ordering, shutdown rejection, and cross-thread visibility.
