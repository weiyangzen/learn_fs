<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperStat.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperStat.cpp

## Purpose
Provides stat and dynamic-attribute refresh helpers for metadata files, retrieving up-to-date size/block/time data from storage targets when metadata marks dynamic attributes stale.

## Important APIs, Types, and Functions
`stat()` wraps `MetaStore::stat()`, handles `DYNAMICATTRIBSOUTDATED` by calling `refreshDynAttribs()` and retrying, and logs benign missing metadata races. `refreshDynAttribs()` references the file inode, chooses sequential or parallel target refresh based on target count, optionally persists refreshed metadata, and releases the inode. `refreshDynAttribsSequential()` sends `GetChunkFileAttribsMsg` per target, including buddy-mirror flags and mirror routing. `refreshDynAttribsParallel()` schedules `GetChunkFileAttribsWork` across the communication slave queue.

## Control Flow, State, and Persistence
Refresh mutates in-memory inode dynamic attributes and optionally persists them to disk. Stat itself may become a mutating operation when attributes are stale. Errors from individual targets are logged and propagated after updating whatever dynamic attributes were returned.

## Dependencies and Integration Points
Depends on `MetaStore`, `FileInode`, stripe patterns, storage target mappers/states, storage buddy group mapper, `GetChunkFileAttribsMsg/RespMsg`, `GetChunkFileAttribsWork`, and `SynchronizedCounter`. Used by stat, lookup intent, rename event link counts, and revalidation.

## Risks and Test Signals
Risks include indefinite stale-attribute loops avoided by accepting the second stale result, partial target failures leaving mixed dynamic attributes, buddy-mirror primary-only reads, and persistence failure after successful refresh. Tests should cover stale refresh retry, sequential/parallel paths, buddy-mirror target routing, missing metadata race logging, make-persistent failure, and dynamic attribute vector sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperStat.cpp -->
