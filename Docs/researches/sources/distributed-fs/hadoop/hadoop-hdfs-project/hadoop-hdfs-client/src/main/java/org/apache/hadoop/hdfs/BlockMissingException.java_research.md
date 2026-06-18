# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/BlockMissingException.java

Purpose: private evolving `IOException` thrown when a read encounters a block with no available locations.

Important APIs and functions: constructor takes filename, description, and offset; `getFile()` and `getOffset()` expose the affected file and corruption offset.

Control flow and state: no custom flow beyond exception construction. Filename and offset are final and serializable with the exception.

Dependencies and integration: used by DFS read paths to report missing block location failures to callers.

Risks and test signals: accurate filename/offset population is critical for client retry and diagnostics. No direct tests in this subset.
