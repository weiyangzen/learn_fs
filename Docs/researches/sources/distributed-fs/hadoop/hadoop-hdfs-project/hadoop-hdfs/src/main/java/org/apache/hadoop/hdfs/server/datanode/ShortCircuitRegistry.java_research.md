<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ShortCircuitRegistry.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ShortCircuitRegistry.java

## Purpose

`ShortCircuitRegistry` manages DataNode-side shared memory segments and slots used by DFSClient short-circuit reads. It coordinates slot validity and anchorability so cached or mlocked blocks can be read locally or with zero-copy semantics safely.

## Important APIs, Types, And Functions

- `RegisteredShm` extends `ShortCircuitShm` and implements `DomainSocketWatcher.Handler`; socket closure removes the segment.
- Constructor initializes `SharedFileDescriptorFactory` and `DomainSocketWatcher`, disabling the registry if prerequisites fail.
- `createNewMemorySegment` allocates a random `ShmId`, shared file descriptor, registry entry, and watcher registration.
- `registerSlot` and `unregisterSlot` map `ExtendedBlockId` to shared-memory slots.
- `processBlockMlockEvent`, `processBlockMunlockRequest`, and `processBlockInvalidation` update slot anchorability/validity.

## Control Flow

When a client requests shared memory, the registry creates a segment under lock, then drops the lock before adding the socket watcher to avoid deadlock. When clients register slots, the registry verifies the segment exists, registers the slot, marks it anchorable if the block is cached, and stores a block-to-slot mapping. Cache and invalidation events iterate affected slots and update state.

## State And Persistence

Runtime state is `enabled`, a shared file descriptor factory, a domain socket watcher, `segments` keyed by `ShmId`, and `slots` keyed by block id. Shared memory files/descriptors are process resources; `removeShm` invalidates slots, removes maps, frees memory maps, and closes shared files.

## Dependencies And Integration Points

It connects DataNode cache management, short-circuit local read protocol, UNIX domain sockets, native shared-file-descriptor support, and client-side `DfsClientShmManager`. It uses Guava-style multimaps and Hadoop short-circuit shared-memory primitives.

## Risks And Edge Cases

Native or domain-socket loading failure silently disables short-circuit shared memory except debug logs. Lock ordering is important around socket watcher callbacks. Munlock is denied while any slot remains anchored. Random `ShmId` collision handling loops until unique.

## Test Signals

Tests should cover disabled registry behavior, segment creation and removal on socket close, duplicate/missing segment errors, slot registration/unregistration, mlock/munlock/invalidation state transitions, client name aggregation, and shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ShortCircuitRegistry.java -->
