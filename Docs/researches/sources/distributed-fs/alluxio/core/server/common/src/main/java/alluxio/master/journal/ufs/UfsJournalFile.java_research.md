# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalFile.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalFile.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalFile.java

### Purpose
`UfsJournalFile` models UFS journal files and encodes/decodes the naming convention for checkpoints, completed logs, incomplete logs, and temporary checkpoints.

### Important APIs, Types, And Functions
Factory methods create checkpoint, log, and tmp checkpoint instances. Encoding methods build URIs such as `0x0-0x<end>` for checkpoints and `0x<start>-0x<end>` for logs. Decoders parse log/checkpoint filenames and skip temporary rename artifacts. Accessors expose location, start, end, and type predicates. `compareTo()` sorts by end sequence.

### Control Flow
Decoding splits names on `-`, parses hex/decimal-compatible `Long.decode()` values, validates checkpoint start is zero, and returns null for non-range names. Incomplete logs are represented by end `UfsJournal.UNKNOWN_SEQUENCE_NUMBER` (`Long.MAX_VALUE`).

### State, Persistence, And Dependencies
Instances are immutable and represent persistent UFS paths. Dependencies include `URIUtils`, Guava `Preconditions`/`MoreObjects`, and the `UfsJournal` directory helpers.

### Integration Points
All UFS journal readers, writers, snapshots, checkpoint writers, and garbage collection use this class to reason about file ranges and whether data has been superseded.

### Risks
Natural ordering by end sequence does not imply object equality; callers must not use compare result as identity. Range naming is the source of replay ordering, so bad filenames can cause gaps, duplicate scanning, or illegal-state exceptions. `UNKNOWN_SEQUENCE_NUMBER` sorts incomplete logs after completed logs.

### Test Signals
Test encoding/decoding for checkpoints, completed logs, incomplete logs, tmp files, invalid names, checkpoint start validation, type predicates, compare ordering, equality/hashCode, and URI directory placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalFile.java -->
