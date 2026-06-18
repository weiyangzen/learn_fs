<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSServerWebApp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSServerWebApp.java

## Purpose
`HttpFSServerWebApp` is the servlet-context bootstrap object for HttpFS. It extends the generic `ServerWebApp`, installs the global singleton, initializes services/configuration, records the admin group, initializes HttpFS metrics, and tears everything down on webapp destruction.

## Important APIs, Types, And Functions
Constants define server name `httpfs` and `admin.group`. Constructors support production and tests. `init()` enforces a single active instance, calls `super.init()`, reads `httpfs.admin.group` defaulting to `admin`, logs the target NameNode, and calls `setMetrics`. `destroy()` clears the singleton, shuts down metrics, and delegates to the parent. Static `get()` and `getMetrics()` expose singleton state.

## Control Flow
The servlet container creates this listener. Initialization establishes `SERVER` before service initialization so filters/resources can read configuration. Metrics setup creates `HttpFSServerMetrics`, starts a `JvmPauseMonitor`, wires it into JVM metrics, sets `FSOperations` buffer size, and initializes the default metrics system.

## State And Persistence
Static fields hold the active webapp and metrics singleton. Instance state holds `adminGroup`. No persistent data is written, but metrics and pause monitoring are process-wide side effects.

## Dependencies And Integration Points
It depends on `ServerWebApp`, `FileSystemAccess`, `HttpFSServerMetrics`, Hadoop metrics2, `JvmPauseMonitor`, `DefaultMetricsSystem`, and `FSOperations`.

## Risks
Double initialization throws a runtime exception. Metrics initialization and shutdown use static/default metrics systems also touched by `HttpFSServerWebServer`, so lifecycle order matters in tests. `SERVER` is set before `super.init()`, so a failed initialization can leave partial singleton state unless destroyed by the container.

## Test Signals
Tests should cover singleton behavior, admin group default/config override, metrics creation/shutdown, buffer-size propagation, and failure cleanup around repeated initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSServerWebApp.java -->
