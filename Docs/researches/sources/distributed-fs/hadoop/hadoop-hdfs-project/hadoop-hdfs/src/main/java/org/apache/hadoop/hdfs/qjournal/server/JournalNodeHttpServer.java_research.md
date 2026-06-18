<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalNodeHttpServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalNodeHttpServer.java

Purpose: Encapsulates the JournalNode HTTP/HTTPS server used for edit-log transfer and web servlet context.

Important APIs/types/functions: Constructor, `start`, `stop`, `getAddress`, `getHttpAddress`, `getHttpsAddress`, `getServerURI`, static `getJournalFromContext`, and `getConfFromContext`.

Control flow: Startup builds an `HttpServer2` from DFS HTTP policy, HTTP bind address, HTTPS address/bind-host overrides, SPNEGO principal/keytab, and X-Frame settings. It stores the local `JournalNode` and configuration in the servlet context, registers `/getJournal`, starts the server, and records actual bound connector addresses back into configuration.

State and persistence behavior: No durable state. Runtime state is HTTP server instance and bound connector addresses. It exposes access to persistent journal files through servlet lookup.

Dependencies/integration: Owned by `JournalNode`; registers `GetJournalEditServlet`; uses `DFSUtil.getHttpServerTemplate`, `HttpConfig.Policy`, `NetUtils`, `JspHelper`, and qjournal HTTP config keys.

Risks: Connector index assumptions depend on DFS HTTP policy ordering. `getAddress` asserts at least one connector is present. The servlet context lookup creates journals lazily when HTTP fetches reference a journal id.

Test signals: Verify HTTP-only, HTTPS-only, and dual policies; bind-host overrides; config update with actual ports; servlet registration and context attributes; server URI scheme; and clean stop error wrapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalNodeHttpServer.java -->
