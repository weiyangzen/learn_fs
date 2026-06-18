<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/LowRedundancyBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/LowRedundancyBlocks.java

## Purpose

`LowRedundancyBlocks` maintains prioritized in-memory queues of blocks or striped block groups that need reconstruction. It is the BlockManager's scheduling input for deciding which endangered data should be reconstructed first.

## Important APIs and types

The class owns five `LightWeightLinkedSet<BlockInfo>` queues: highest priority, very low redundancy, low redundancy, badly distributed, and corrupt. Public package APIs include `add`, `remove`, `update`, `contains`, `chooseLowRedundancyBlocks`, queue iterators, and metric getters for low-redundancy, corrupt, EC, badly distributed, and highest-priority counts. Counters are maintained with `LongAdder`.

## Control flow

`getPriority` chooses a queue from live, read-only, out-of-service, and expected replica counts. Contiguous blocks with one live copy or only read-only/out-of-service copies are highest priority; zero usable copies are corrupt. Striped blocks compare live internal blocks against data and parity unit counts. `update` removes the block using its old computed priority, searches other queues if needed, and re-adds at the current priority. `chooseLowRedundancyBlocks` walks queues in priority order using bookmarks, skips corrupt blocks for reconstruction output, removes deleted blocks, and resets bookmarks at the end or on request.

## State and persistence behavior

All state is in-memory and synchronized on the instance. Queue membership and counters must change together; there is no fsimage persistence because block health is recomputed from block maps and reports.

## Dependencies and integration points

It depends on `BlockInfo`, `BlockInfoStriped`, `LightWeightLinkedSet`, and NameNode/BlockManager logging and metrics. BlockManager uses it during redundancy monitor scans, block report handling, placement checks, and reconstruction scheduling.

## Risks and edge cases

Counter consistency depends on every queue mutation flowing through increment/decrement helpers. Priority calculations differ for contiguous and striped blocks, making read-only, maintenance, decommissioned, and corrupted states easy to misclassify. The corrupt queue is still scanned to purge deleted blocks but not returned for reconstruction. Bookmark iteration can delay recently skipped blocks until reset.

## Test signals

Tests should cover each priority threshold, EC data/parity boundaries, update moves between queues, delete cleanup during `chooseLowRedundancyBlocks`, replication-one corrupt counters, badly distributed counters, and iterator reset fairness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/LowRedundancyBlocks.java -->
