<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/conf/NfsConfigKeys.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/conf/NfsConfigKeys.java

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/conf/NfsConfigKeys.java` centralizes configuration key names and defaults for the HDFS NFS gateway. The source was read as a complete 95-line file for this report.

## Important APIs, Types, and Functions

`NfsConfigKeys` is a constants-only class. It defines server and mountd ports, transfer limits (`nfs.rtmax`, `nfs.wtmax`, `nfs.dtmax`), open-file cache size, stream timeout, export points, Kerberos keytab/principal, registration and port-monitoring settings, AIX compatibility, large upload behavior, HTTP/HTTPS addresses, metrics percentile intervals, NFS superuser, and UDP portmap timeout.

## Control Flow

There is no runtime flow beyond class loading. Other gateway components read these constants when constructing RPC programs, HTTP servers, caches, metrics, and security login state.

## State and Persistence Behavior

The file owns no mutable state. Values are defaults and lookup keys; actual configuration state lives in Hadoop `Configuration` instances and XML resources.

## Dependencies and Integration Points

It is consumed by `NfsConfiguration`, `Mountd`, `RpcProgramMountd`, `Nfs3`, `DFSClientCache`, `Nfs3HttpServer`, and metrics setup.

## Risks and Edge Cases

Changing defaults can alter exposed ports, security posture, transfer sizing, cache behavior, or HTTP binding. The default `nfs.port.monitoring.disabled=true` allows insecure ports unless deployment overrides it.

## Test Signals

Configuration-deprecation tests, gateway startup tests with overridden ports and export points, HTTP address tests, and export/superuser access tests exercise these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/conf/NfsConfigKeys.java -->
