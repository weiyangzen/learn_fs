# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Progress.java

## Purpose
`Progress` models hierarchical task progress for MapReduce-style execution. A root node can contain weighted or equal phases, and leaf nodes report a normalized progress value.

## Important APIs, Types, And Functions
Key APIs are `addPhase`, `addPhases`, `startNextPhase`, `phase`, `complete`, `set`, `get`, `getProgress`, `setStatus`, and `toString`. Fields track status text, leaf progress, current phase index, child phases, parent, equal-weight mode, per-phase weight, and custom weight list.

## Control Flow
Adding phases creates child `Progress` nodes and either recalculates equal weight per child or records explicit weights. `set` clamps NaN, infinities, and out-of-range values into `[0,1]`. `get` walks to the root and recursively computes completed-phase contribution plus current child contribution. `complete` marks the node complete and advances the parent phase while deliberately releasing the child lock before locking the parent.

## State And Persistence
All state is in-memory and mostly protected with synchronized methods. There is no persistence. Parent links are stable after child creation.

## Dependencies And Integration Points
It depends on SLF4J and Hadoop annotations. `QuickSort` and MapReduce code use `Progressable`/progress reporting to avoid timeout assumptions during long operations.

## Risks
Mixing equal-weight and explicit-weight phases on one node can leave inconsistent weight lists. Explicit weights can sum above one; the code warns but still allows it. `phase()` can throw if `currentPhase` is out of range.

## Test Signals
Tests should cover nested weighted and unweighted progress, clamping, `complete` parent advancement, status rendering path, over-one weight warnings, and concurrent reads during completion.
