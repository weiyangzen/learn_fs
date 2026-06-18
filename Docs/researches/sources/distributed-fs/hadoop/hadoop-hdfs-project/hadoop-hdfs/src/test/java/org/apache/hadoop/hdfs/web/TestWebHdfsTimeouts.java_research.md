# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsTimeouts.java

Purpose: verifies WebHDFS sets finite connect/read timeouts for normal, auth, redirect, and two-step write HTTP paths.

Important APIs/types/functions: `WebHdfsFileSystem`, `URLConnectionFactory`, `ConnectionConfigurator`, timeout config keys, `ServerSocket`, `SocketChannel`, `SubjectInheritingThread`, parameterized `TimeoutSource`.

Control flow: each parameterized test runs with timeouts supplied either by a custom connection factory or configuration. Setup binds a bogus server socket on the NameNode HTTP address; read-timeout tests let it accept no useful response, while connect-timeout tests fill the server backlog with nonblocking sockets. Redirect tests start one background thread that accepts the first request, switches the filesystem to short timeouts, optionally consumes backlog, and sends an HTTP 307 redirect back to the bogus server. Tests call `listFiles`, `getDelegationToken`, `getFileChecksum`, or `create/close` and expect `SocketTimeoutException` with connect/read messaging.

State and persistence behavior: local sockets, client channel list, WebHDFS client, and one server thread per redirect test. `tearDown` closes channels, filesystem, server socket, and joins the thread.

Dependencies and integration points: covers WebHDFS URL open paths including auth URLs, redirect handling, and DataNode write follow-up connections.

Risks: backlog saturation is OS-dependent; the test aborts when unable to prove backlog consumption. Timing is bounded by short 200 ms socket timeouts and JUnit 100-second method timeouts.

Test signals: timeout exceptions for all relevant HTTP paths and both timeout configuration sources.
