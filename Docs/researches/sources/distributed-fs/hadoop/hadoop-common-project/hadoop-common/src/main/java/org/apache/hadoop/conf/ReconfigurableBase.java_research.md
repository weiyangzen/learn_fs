# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ReconfigurableBase.java`

## Purpose

`ReconfigurableBase` is the standard helper base for runtime reconfiguration. It extends `Configured`, implements `Reconfigurable`, provides synchronous single-property changes, and adds a background task that reloads a fresh configuration, computes differences, and applies allowed changes.

## Important APIs and Types

Subclasses must implement `getNewConf()`, `getReconfigurableProperties()`, and `reconfigurePropertyImpl(String,String)`. Public APIs include `startReconfigurationTask`, `getReconfigurationTaskStatus`, `shutdownReconfigurationTask`, final `reconfigureProperty`, `isPropertyReconfigurable`, and visible-for-testing hooks for the `ReconfigurationUtil`.

## Control Flow

`startReconfigurationTask` synchronizes on `reconfigLock`, rejects stopped or already-running state, creates a daemon `ReconfigurationThread`, starts it, and records `startTime`. The thread captures old and new configs, asks `ReconfigurationUtil` for changed properties, redacts values for logging, skips non-reconfigurable changes, calls `reconfigurePropertyImpl` for each allowed change, and updates or unsets the old configuration. It records a map from `PropertyChange` to optional error message, marks `endTime`, and clears `reconfigThread`. The final `reconfigureProperty` method performs the same core operation for one property under `getConf()` synchronization.

## State and Persistence

State includes the backing `Configuration`, a replaceable `ReconfigurationUtil`, a background thread reference, `shouldRun`, `reconfigLock`, start/end timestamps, and the latest immutable status map. Persistence is in-memory only; changes update the current `Configuration` but do not rewrite configuration files.

## Dependencies and Integration Points

It integrates with `ReconfigurationUtil.PropertyChange`, `ReconfigurationTaskStatus`, `ConfigRedactor`, `SubjectInheritingThread`, `Time`, Guava-compatible `Maps`, and service-specific subclasses in HDFS/YARN daemons. Web or RPC management layers can trigger and poll the task.

## Risks

`shutdownReconfigurationTask` sets `reconfigThread` to null before joining, so status polling can report stopped state while a captured thread is still finishing. Non-reconfigurable changes are skipped and not recorded in the status map, which may make status incomplete for operators. Exceptions from `reconfigurePropertyImpl` are captured per property, but partially applied earlier properties remain applied. `shouldRun` is never reset to true after shutdown. Synchronization separates `reconfigLock` from `getConf()` locking, so subclass implementations must avoid lock-order problems.

## Test Signals

Tests should cover single-property success/failure, disallowed properties, null reset, background task rejection when running or stopped, status timestamps and optional error messages, redacted logging, subclass effective values differing from requested values, and interruption/shutdown behavior.
