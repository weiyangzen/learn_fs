# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/CombinedHostsFileWriter.java

Purpose: `CombinedHostsFileWriter` writes JSON-based DataNode admin host configuration from a set of `DatanodeAdminProperties`.

Important APIs/types/functions: `writeFile(String, Set<DatanodeAdminProperties>)` creates a Jackson `ObjectMapper`, opens the target path as UTF-8, and writes the set as JSON.

Control flow: single-pass serialization in a try-with-resources writer.

State and persistence behavior: stateless utility that persists the supplied set to the local filesystem. Ordering follows the provided set's iteration order.

Dependencies and integration points: depends on Jackson, Java NIO, and `DatanodeAdminProperties`. It complements `CombinedHostsFileReader` for admin tooling.

Risks and test signals: set iteration order can make output nondeterministic for unordered sets. It does not create parent directories or write atomically. Tests should cover UTF-8 output, round-trip with the reader, empty set, and deterministic behavior when ordered sets are used.
