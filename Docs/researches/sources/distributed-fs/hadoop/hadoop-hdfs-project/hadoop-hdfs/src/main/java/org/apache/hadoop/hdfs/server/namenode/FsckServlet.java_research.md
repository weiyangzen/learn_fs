# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FsckServlet.java

## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FsckServlet.java

Purpose: `FsckServlet` is the NameNode HTTP endpoint that runs HDFS fsck from the web server. It adapts a servlet request into a privileged `NamenodeFsck` invocation and records an audit event for success or failure.

Important APIs and types: it extends `DfsServlet` and overrides `doGet(HttpServletRequest, HttpServletResponse)`. It uses servlet request parameters, response writer, remote address, servlet context, NameNode HTTP helpers, caller UGI, `FSNamesystem`, `BlockManager`, `DatanodeReportType.LIVE`, and `NamenodeFsck`.

Control flow: `doGet` obtains the raw parameter map, output writer, parsed remote address, `Configuration`, and caller UGI. It executes the fsck body inside `ugi.doAs`. Inside the privileged action, it retrieves the `NameNode`, namesystem, block manager, network topology, and live datanode count, constructs `NamenodeFsck`, captures its audit source, runs `fsck.fsck()`, and marks success only after it returns. The `finally` block calls `namesystem.logFsckEvent` with success state, audit source, and remote address. Interrupted fsck execution maps to HTTP 400.

State and persistence behavior: the servlet itself has no mutable state beyond `serialVersionUID`. It reads live NameNode state and writes response output. Persistent side effects are indirect: audit logging and any operational effects of fsck reporting; fsck itself is primarily diagnostic.

Dependencies and integration points: it integrates with the NameNode web server context, servlet container, Hadoop security impersonation, `NamenodeFsck`, block management, network topology, live datanode reporting, and audit logging through `FSNamesystem`.

Risks: request parameter map is passed through directly to fsck, so fsck must validate option semantics. Reverse DNS or invalid remote addresses can throw `IOException`. Only `InterruptedException` is converted to a client error; other exceptions propagate through servlet handling after the audit `finally`. Long fsck runs can tie up servlet threads and NameNode read paths depending on fsck internals.

Test signals: tests should cover UGI selection, parameter propagation, successful and failing audit logging, live datanode count wiring, remote-address handling, interrupted execution returning HTTP 400, and servlet-context lookup failures.
