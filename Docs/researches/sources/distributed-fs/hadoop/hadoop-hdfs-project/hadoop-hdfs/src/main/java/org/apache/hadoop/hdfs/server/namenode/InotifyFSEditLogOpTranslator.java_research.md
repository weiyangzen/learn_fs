<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/InotifyFSEditLogOpTranslator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/InotifyFSEditLogOpTranslator.java

## Purpose

`InotifyFSEditLogOpTranslator` converts NameNode edit-log operations into public HDFS inotify `EventBatch` objects.

## Important APIs and Types

The static `translate(FSEditLogOp op)` switch handles create/append/close, replication changes, concat/delete, old and new rename operations, delete, mkdir, permission/owner/time updates, symlink creation, XAttr add/remove, ACL changes, and truncate. `getSize` sums block sizes for close events.

## Control Flow, State, and Persistence

The translator is stateless. For `OP_ADD`, it treats zero blocks as file creation and nonzero blocks as append. Some edit operations produce multiple events: concat emits append for target, unlink for each source, and close for target. Unsupported opcodes return `null`, meaning no inotify event is emitted. Event batches preserve the edit transaction id.

## Dependencies and Integration Points

It depends on `FSEditLogOp` subclasses, `org.apache.hadoop.hdfs.inotify.Event`, block sizes, permissions, ACL/XAttr payloads, and `ErasureCodeConstants.REPLICATION_POLICY_ID` to mark created files as erasure-coded.

## Risks and Test Signals

Risks include incomplete opcode coverage, semantic mismatch between edit-log fields and user-visible inotify events, and create-versus-append inference from block array length. Tests should feed representative edit ops, verify event ordering and txids, cover concat multi-event output, EC create flags, ACL/XAttr removed flags, and ensure unsupported operations are intentionally silent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/InotifyFSEditLogOpTranslator.java -->
