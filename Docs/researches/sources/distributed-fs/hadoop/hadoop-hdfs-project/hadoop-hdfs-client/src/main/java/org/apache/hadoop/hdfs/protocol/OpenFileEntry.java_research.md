# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/OpenFileEntry.java

## Purpose
`OpenFileEntry` represents one open file for DFSAdmin/open-file listing commands. It identifies the inode ID, file path, client name, and client machine.

## APIs and Behavior
The constructor initializes final fields. Accessors expose `id`, `filePath`, `clientName`, and `clientMachine`.

## State, Dependencies, and Integration
It is immutable and used by `ClientProtocol.listOpenFiles` and `OpenFilesIterator`. The ID acts as the batching cursor.

## Risks and Test Signals
There is no validation and no equality implementation. Tests should cover batched cursor ordering by ID, filtering by path/type, and display behavior when client fields are null or empty.
