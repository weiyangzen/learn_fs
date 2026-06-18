# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/DFSRouter.java

Purpose: command-line entry point for starting an HDFS Router-Based Federation `Router`.

Important APIs: `main` handles help, logs startup/shutdown message, constructs `Router`, registers a composite-service shutdown hook at priority 30, loads configuration, initializes, and starts the router. `getConfiguration` creates `HdfsConfiguration` and adds FedBalance default/site resources.

Control flow and state: static utility class with private constructor. On any throwable during startup, logs and exits via `ExitUtil.terminate(1, e)`.

Dependencies and integration points: Hadoop CLI conventions, `DFSUtil.parseHelpArgument`, `ShutdownHookManager`, `Router`, and FedBalance config resources.

Risks: startup failures terminate the JVM. Resource loading includes FedBalance XMLs, so router behavior can be affected by those configs. No explicit blocking loop is in this class; lifecycle is owned by `Router` services.

Test signals: help argument handling, configuration resource inclusion, shutdown hook registration, and failure path termination.
