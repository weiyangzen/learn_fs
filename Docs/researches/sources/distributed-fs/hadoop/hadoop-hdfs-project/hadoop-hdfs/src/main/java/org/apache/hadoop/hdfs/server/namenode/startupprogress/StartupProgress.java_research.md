<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StartupProgress.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StartupProgress.java

## Purpose

`StartupProgress` is the thread-safe mutable recorder for NameNode startup instrumentation. Startup code marks phase and step begin/end, records file/size/total metadata, and increments counters for long-running tasks.

## Important APIs and types

- `beginPhase`, `endPhase`, `beginStep`, `endStep` update monotonic timestamps.
- `setFile`, `setSize`, `setTotal`, and `setCount` attach metadata and counters.
- `getCounter(Phase, Step)` returns an atomic `Counter` optimized for repeated loop increments.
- `getStatus(Phase)` reports `PENDING`, `RUNNING`, or `COMPLETE`.
- `createView()` returns `StartupProgressView`, a stable snapshot for readers.

## Control flow

The constructor initializes a `PhaseTracking` for every `Phase`. Mutating methods mostly no-op after overall startup completion, and step methods no-op after their phase completes. `lazyInitStep` uses `putIfAbsent` against the phase's concurrent map so multiple threads can race safely to create a step record.

## State and persistence behavior

State is in-memory, concurrent, and frozen by behavior once all phases complete. Counters use `AtomicLong` through `StepTracking`; timestamps and metadata fields are plain writes relying on eventual consistency until cloned into a view. No filesystem persistence occurs.

## Dependencies and integration points

NameNode startup code calls this class; servlets/JMX call `createView`. It depends on `Time.monotonicNow`, `PhaseTracking`, `StepTracking`, `Step`, and `Status`.

## Risks and edge cases

- `setCount` does not check phase completion, unlike counter increments and total updates, so callers can overwrite counts after completion.
- Overall completion checks all phases; missing an `endPhase(SAFEMODE)` keeps progress mutable and percent below complete.
- Duplicate `Step` objects with same file/size/type compare equal but can carry different sequence numbers for sorting if one becomes the map key.
- Plain field writes are safe from corruption but not strongly ordered across multiple metadata fields.

## Test signals

`TestStartupProgress` covers phase/step status, counters, completion freeze, metadata, view snapshots, and elapsed/percent calculations. Additional useful signals are concurrent counter increments and duplicate logical step behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StartupProgress.java -->
