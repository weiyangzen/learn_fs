<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3HttpServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3HttpServer.java

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3HttpServer.java` encapsulates the HTTP/HTTPS info server for the NFSv3 gateway. The source was read as a complete 110-line file for this report.

## Important APIs, Types, and Functions

`Nfs3HttpServer` stores `infoPort`, `infoSecurePort`, `HttpServer2 httpServer`, and `NfsConfiguration conf`. Key methods are constructor, `start`, `stop`, `getPort`, `getSecurePort`, `getServerURI`, and `getHttpAddress`.

## Control Flow

`start` resolves HTTP and HTTPS socket addresses from config, uses `DFSUtil.getHttpServerTemplate` with NFS Kerberos key/principal settings, builds and starts `HttpServer2`, then records connector ports according to `DFSUtil.getHttpPolicy`. `stop` wraps server stop exceptions in `IOException`.

## State and Persistence Behavior

Server/socket state is process-local. No durable state is written by this class; exposed metrics/status are served from other runtime components.

## Dependencies and Integration Points

It integrates Hadoop HTTP policy, `HttpServer2`, `DFSUtil`, `NetUtils`, and NFS HTTP/HTTPS configuration keys.

## Risks and Edge Cases

Connector index ordering depends on HTTP policy. Binding to wildcard addresses and deriving client URI scheme need tests for HTTP_ONLY, HTTPS_ONLY, and mixed policies.

## Test Signals

`TestNfs3HttpServer` covers configured ports, secure policy behavior, and server URI exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3HttpServer.java -->
