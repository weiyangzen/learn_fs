<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterNetworkTopologyServlet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterNetworkTopologyServlet.java

## Purpose
`RouterNetworkTopologyServlet` exposes a router-level network topology view by collecting federated datanode reports and reusing NameNode topology rendering in text or JSON form.

## Important APIs, Types, and Functions
`doGet` parses the Accept header through `NetworkTopologyServlet.parseAcceptHeader`, sets response content type, retrieves the `Router` from servlet context, gets an `ALL` datanode report from the router RPC server, converts the array to `List<Node>`, and calls `printTopology`.

## Control Flow
The servlet supports both sync and async router RPC servers. In async mode it calls `getDatanodeReportAsync` and then `syncReturn(DatanodeInfo[].class)`; in sync mode it calls `getDatanodeReport`. Output is written through a UTF-8 `PrintStream`. Any throwable while printing sends HTTP 410 and is rethrown as `IOException`; the response output stream is closed in `finally`.

## State and Persistence Behavior
The servlet has no persistent state. It reads current router datanode reports and streams a derived topology response.

## Dependencies and Integration Points
It extends `NetworkTopologyServlet`, uses `RouterHttpServer.getRouterFromContext`, `RouterRpcServer`, async `syncReturn`, HDFS `DatanodeInfo`, `HdfsConstants.DatanodeReportType.ALL`, Hadoop `Node`, and servlet response APIs. It is registered by `RouterHttpServer`.

## Risks
The method closes the servlet output stream explicitly after try-with-resources already manages the print stream. Async result handling wraps any exception in `IOException`. Large federations may produce expensive reports. Error handling sends HTTP 410 for all print failures, which may be semantically broad.

## Test Signals
Tests should cover Accept header handling and content types, sync and async datanode report paths, topology rendering calls, exception-to-HTTP-410 behavior, stream closure, and servlet context router lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterNetworkTopologyServlet.java -->
