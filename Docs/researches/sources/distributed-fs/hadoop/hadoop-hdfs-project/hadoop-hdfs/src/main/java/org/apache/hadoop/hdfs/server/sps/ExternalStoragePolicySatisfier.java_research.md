<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalStoragePolicySatisfier.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalStoragePolicySatisfier.java

## Purpose

`ExternalStoragePolicySatisfier` is the standalone entry point for running HDFS Storage Policy Satisfier outside the NameNode process.

## Important APIs and types

The class is final with a private constructor. `main` creates configuration, performs secure login, constructs `StoragePolicySatisfier`, obtains a `NameNodeConnector`, creates `ExternalSPSContext`, starts SPS in `StoragePolicySatisfierMode.EXTERNAL`, registers metrics, and joins. `secureLogin` logs in using SPS keytab/principal config. `getNameNodeConnector` retries connector creation and exits if another external SPS instance is running.

## Control flow

Startup logs standard daemon messages, initializes security, connects to internal NameNode RPC URIs using `NameNodeConnector.newNameNodeConnectors`, then starts SPS. On any throwable it logs and terminates with exit code 1. The finally block closes the connector and metrics if initialized. Connector creation retries every three seconds unless it detects the "Another ExternalStoragePolicySatisfier is running" lock condition.

## State and persistence behavior

The process holds a NameNodeConnector lock/path (`MOVER_ID_PATH`) to prevent concurrent movers/SPS instances. It mutates HDFS block placement and SPS xattr hints through the context and service; no direct persistence happens in this wrapper.

## Dependencies and integration points

It integrates `HdfsConfiguration`, Kerberos `SecurityUtil`, `UserGroupInformation`, `DFSUtil.getInternalNsRpcUris`, `NameNodeConnector`, `StoragePolicySatisfier`, `ExternalSPSContext`, and metrics.

## Risks and test signals

Risks include infinite retry on misconfiguration, brittle string comparison for duplicate-instance detection, metrics/context cleanup ordering, and secure-login principal host resolution. Tests should cover secure and simple auth startup, duplicate instance exit, connector retry, external mode startup, and cleanup on initialization failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/sps/ExternalStoragePolicySatisfier.java -->
