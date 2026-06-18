# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalSnapshot.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalSnapshot.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalSnapshot.java

### Purpose
`UfsJournalSnapshot` captures a point-in-time listing of UFS journal checkpoints, logs, and temporary checkpoints, and provides helper queries over that listing.

### Important APIs, Types, And Functions
`getSnapshot(UfsJournal)` lists and decodes checkpoint, log, and tmp directories. `getCheckpoints()`, `getLatestCheckpoint()`, `getLogs()`, and `getTemporaryCheckpoints()` expose sorted immutable-by-convention lists. `getCurrentLog()` finds the max log and returns it if incomplete. `getNextLogSequenceNumberToCheckpoint()` returns the latest checkpoint's end or zero.

### Control Flow
Listing methods tolerate absent directories via null status arrays. Checkpoints and logs are decoded through `UfsJournalFile` and sorted by end sequence; temp checkpoint files are decoded as UUID-like tmp entries without sorting requirements.

### State, Persistence, And Dependencies
The object stores lists from one UFS listing pass and does not mutate persistence. Dependencies include `UfsStatus`, `UfsJournalFile`, and Java collection sorting.

### Integration Points
Readers use it to plan replay, writers use it to find incomplete logs and recover failures, checkpoint writers use it to detect newer checkpoints, and GC uses it to delete stale files.

### Risks
It is only a snapshot; concurrent UFS writes/renames can make it stale immediately. Sorting by end sequence places incomplete logs last due to `Long.MAX_VALUE`. Invalid range filenames can throw from decoders.

### Test Signals
Cover empty/missing directories, multiple checkpoints/logs sorted by end, current incomplete log detection, no current log when max is completed, tmp checkpoint listing, latest checkpoint boundary, and invalid filename propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalSnapshot.java -->
