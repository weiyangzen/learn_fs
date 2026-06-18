# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CpuTimeTracker.java

Purpose: `CpuTimeTracker` converts cumulative CPU jiffies into a CPU usage percentage sampled over wall-clock time.

Important APIs and types: constructor takes jiffy length in milliseconds. Methods include `getCpuTrackerUsagePercent`, `getCumulativeCpuTime`, `updateElapsedJiffies`, and `toString`.

Control flow: `updateElapsedJiffies` multiplies elapsed jiffies by jiffy length, monotonically advances cumulative CPU time, and records sample time. `getCpuTrackerUsagePercent` computes CPU delta divided by elapsed sample time times 100 when enough time has passed, updates last-sample fields, and returns the cached usage otherwise.

State and persistence behavior: stores sample time, last sample time, cumulative and last cumulative CPU time as `BigInteger`, jiffy length, and cached usage. No persistence.

Dependencies and integration points: used by process/resource monitoring code reading OS counters.

Risks: cumulative CPU time is monotonic even if input counter decreases, which hides counter resets. Usage can exceed 100% for multi-core processes. The misspelled `Cummulative` text appears in `toString` compatibility.

Test signals: cover first sample behavior, minimum interval gating, monotonic cumulative handling, decreasing jiffy input, multi-core percentages, big jiffy values, and string diagnostics.
