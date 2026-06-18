<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterFsckServlet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterFsckServlet.java

## Purpose
`RouterFsckServlet` binds the router HTTP `/fsck` endpoint to `RouterFsck`. It authenticates the HTTP caller using the standard DFS servlet path and executes the federated FSCK under that `UserGroupInformation`.

## Important APIs, Types, and Functions
The servlet constants are `SERVLET_NAME = "fsck"` and `PATH_SPEC = "/fsck"`. `doGet` reads the request parameter map, response writer, remote address, servlet context, router configuration, and UGI, then calls `new RouterFsck(...).fsck()` inside `ugi.doAs`.

## Control Flow
On GET, the servlet resolves the caller address with `InetAddress.getByName`, retrieves `Configuration` and `Router` from `RouterHttpServer` context attributes, builds a `RouterFsck`, and delegates. If the privileged action is interrupted, it responds with HTTP 400 and the interruption message.

## State and Persistence Behavior
The servlet has no mutable state beyond serialization metadata. It relies on servlet-context attributes populated by `RouterHttpServer` and streams output through the response writer.

## Dependencies and Integration Points
It extends `DfsServlet`, uses `getUGI`, `RouterHttpServer.getConfFromContext`, `RouterHttpServer.getRouterFromContext`, `UserGroupInformation.doAs`, and `RouterFsck`. It is installed by `RouterHttpServer.setupServlets`.

## Risks
The response writer is obtained before delegated FSCK and is closed by `RouterFsck`. `InterruptedException` is the only caught exception; IO errors propagate through servlet handling. Remote address resolution may fail if the request remote address is not resolvable. Query parameter validation is delegated entirely to downstream NameNode FSCK handling.

## Test Signals
Tests should verify context attribute lookup, UGI execution, parameter and remote-address propagation to `RouterFsck`, servlet registration constants, and interrupted-action response status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterFsckServlet.java -->
