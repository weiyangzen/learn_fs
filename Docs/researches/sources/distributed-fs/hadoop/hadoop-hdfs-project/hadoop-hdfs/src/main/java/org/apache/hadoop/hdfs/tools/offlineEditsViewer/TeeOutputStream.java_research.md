## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineEditsViewer/TeeOutputStream.java

Purpose: `TeeOutputStream` is a small `OutputStream` adapter that duplicates writes, flushes, and closes to multiple underlying streams. It supports verbose offline edits output to both a file and the console.

Important APIs and control flow: the constructor stores an `OutputStream[]`. `write(int)`, `write(byte[])`, and `write(byte[], int, int)` iterate in array order and forward the call to each stream. `flush()` and `close()` similarly forward to each stream.

State, persistence, and dependencies: state is just the array reference. The output side effects are entirely determined by the wrapped streams. There are no Hadoop dependencies in this class.

Integration points: `OfflineEditsVisitorFactory` uses it when `printToScreen` is true for XML or stats processors, pairing a file stream with `System.out`.

Risks and test signals: tests should cover forwarding for all write overloads and flushing. Failure semantics are simple but important: if an earlier stream throws, later streams are not called. Closing also closes every wrapped stream, including `System.out` in current usage; embedding tests should detect whether this is acceptable. The class does not guard against null entries or concurrent writes.
