# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/CombinedHostsFileReader.java

Purpose: `CombinedHostsFileReader` reads JSON-based DataNode include/exclude/admin configuration into `DatanodeAdminProperties[]`.

Important APIs/types/functions: `readFile(String)` parses the modern top-level JSON array format with Jackson. On `JsonMappingException`, it falls back to legacy concatenated-object parsing with `ObjectReader.readValues`. Empty files warn and return an empty array. `readFileWithTimeout(String, int)` runs `readFile` inside a `SubjectInheritingThread`/`FutureTask` and throws `IOException` on timeout, interruption, or execution failure.

Control flow: modern parse is attempted when file length is positive. Legacy parse collects all parsed objects and logs a warning; invalid legacy parse logs and returns whatever was collected, usually empty. Timeout wrapper starts a thread, waits bounded time, cancels on timeout, and maps several failure modes to an IOException message.

State and persistence behavior: stateless utility. Reads UTF-8 files from local filesystem; no writes.

Dependencies and integration points: depends on Jackson, `DatanodeAdminProperties`, Java NIO, and `SubjectInheritingThread` for security context propagation. Used by NameNode host refresh/admin state handling.

Risks and test signals: invalid legacy JSON is logged but not rethrown, which can silently produce empty configuration. `readFileWithTimeout` maps execution failures to a timeout-flavored IOException. Tests should cover modern array format, legacy format, empty file, invalid JSON, timeout cancellation, and subject inheritance where relevant.
