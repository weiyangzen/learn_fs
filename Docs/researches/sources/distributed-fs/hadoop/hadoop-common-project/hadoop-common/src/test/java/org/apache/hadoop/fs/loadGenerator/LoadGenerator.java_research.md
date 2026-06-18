# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/loadGenerator/LoadGenerator.java

## Purpose
Implements the core NameNode/filesystem load generator used by Hadoop tests and benchmarks. It can run as a standalone `Tool` or be subclassed for MapReduce-based generation. The tool creates concurrent client threads that randomly read files, create/delete temporary files, or list directories according to configured probabilities and durations.

## Important APIs, Types, and Functions
`LoadGenerator` extends `Configured` and implements `Tool`. Static configuration/state includes `root`, `fc`, `maxDelayBetweenOps`, `numOfThreads`, `durations`, `readProbs`, `writeProbs`, `currentIndex`, `totalTime`, `startTime`, file/dir tables, `seed`, `scriptFile`, and `flagFile`. Operation metrics are indexed by `OPEN`, `LIST`, `CREATE`, `WRITE_CLOSE`, and `DELETE`. The inner `DFSClientThread` extends `SubjectInheritingThread` and implements `work`, `delay`, `nextOp`, `read`, `write`, `list`, and `genFile`. Public orchestration includes `run`, `generateLoadOnNN`, `parseArgs`, `loadScriptFile`, `printResults`, and `main`.

## Control Flow
`run` parses arguments, prints target filesystem information, calls `generateLoadOnNN`, and prints aggregate results. `generateLoadOnNN` seeds a shared `Random`, initializes `FileContext`, recursively populates directory and file tables, waits at a start-time barrier, starts `numOfThreads` workers, and then stops workers based on fixed duration, script durations, or a flag file. Script mode advances `currentIndex` after each duration line. After joining workers, it merges per-thread execution times and operation counts, then returns a negative test failure code if any thread failed.

## State and Persistence
The class uses substantial static mutable state, including worker control (`shouldRun`), probability arrays, file/dir tables, and metrics. Filesystem state is read from the generated test namespace and temporarily modified by write operations: each write creates a uniquely named file in a random directory, fills it with `a`, then deletes it. A configured flag file can externally stop the run. Static state may leak between repeated in-process invocations unless reset by callers.

## Dependencies and Integration Points
It depends on `DataGenerator.DEFAULT_ROOT` and `StructureGenerator.FILE_NAME_PREFIX`, Hadoop `FileContext`, `FileStatus`, `CreateFlag`, `CreateOpts`, `ToolRunner`, `Time`, `Preconditions`, `IOUtils`, and SLF4J. `LoadGeneratorMR` in MapReduce is explicitly cited as a subclassing integration point.

## Risks and Edge Cases
Randomness is shared across threads, which can cause contention and nondeterminism. The file write loop uses `Math.min(fileSize, WRITE_CONTENTS.length)` rather than remaining bytes, so for file sizes larger than one buffer it can overshoot the intended amount; with the small default block size this may rarely matter but is a code risk. `System.exit` in script loading on open failure is hostile to embedding. Static state and arrays mean repeated tests need careful reset. Empty namespaces or namespaces without `_file_` files are rejected.

## Test Signals
This utility has operational output rather than JUnit assertions. Useful signals are nonzero operation counts, printed average latencies, positive throughput when `totalTime` is set, and exit code `-ERR_TEST_FAILED` when any worker records an exception.
