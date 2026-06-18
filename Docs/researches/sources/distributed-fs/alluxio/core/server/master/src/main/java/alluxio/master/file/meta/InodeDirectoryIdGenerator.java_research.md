# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeDirectoryIdGenerator.java

Purpose: thread-safe generator for directory inode ids, using block container ids plus sequence numbers and journaling the next id state.

Important APIs and types: constructor accepts a `ContainerIdGenerable`. `getNewDirectoryId` initializes if needed, returns current block id, advances sequence or obtains a new container, and journals the next state. `peekDirectoryId` reads the next id. Journaled methods process, reset, and iterate `InodeDirectoryIdGeneratorEntry`; checkpoint name is `INODE_DIRECTORY_ID_GENERATOR`.

Control flow: first id allocation journals a new container id with sequence 0. Each allocation returns `BlockId.createBlockId(containerId, sequenceNumber)` and journals the next pair. When max sequence is reached, it gets a new container id and resets sequence to 0.

State and persistence behavior: durable state is the next container id and sequence number, represented by `DirectoryId` and journal entries. On replay, `processJournalEntry` restores that next-id state.

Dependencies and integration points: depends on block id utilities, container id generation, journal context, journaled interface, directory id state, and checkpoint name. Used by inode tree/directory creation paths.

Risks: `resetState` does not reset `mInitialized`, so after reset in some lifecycle scenarios initialization semantics need scrutiny. `peekDirectoryId` is not synchronized, while writes are synchronized; visibility relies on `DirectoryId` internals or external discipline.

Test signals: tests should cover first initialization, sequence increment, sequence rollover to new container, journal replay, reset, iterator output, unavailable container id generation, and concurrency.
