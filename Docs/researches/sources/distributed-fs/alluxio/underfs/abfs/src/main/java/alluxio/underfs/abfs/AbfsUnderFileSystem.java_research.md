# Research: sources/distributed-fs/alluxio/underfs/abfs/src/main/java/alluxio/underfs/abfs/AbfsUnderFileSystem.java

Purpose: Azure Data Lake Storage Gen2 ABFS implementation built on `HdfsUnderFileSystem`. It adapts Alluxio configuration into Hadoop ABFS authentication settings and normalizes object-store-like behavior.

Important APIs and control flow: `createAbfsConfiguration` starts from HDFS config, prefers account-key `SharedKey`, otherwise client credentials OAuth, otherwise managed identity OAuth with optional endpoint/tenant/client id. `createInstance` builds the Hadoop config. `getUnderFSType` returns `abfs`. `getBlockSizeByte` returns Alluxio default block size. `getStatus` rewrites `UfsFileStatus` to use this block size and non-null last-modified time. Owner/mode setters are no-ops; file locations return null.

State, dependencies, integration, risks, tests: state is Hadoop configuration and inherited HDFS filesystem state. Dependencies include `PropertyKey` templates, Hadoop Azure ABFS, and Alluxio UFS status types. Risks include auth precedence mistakes, secret logging through generic config handling, no POSIX ACL/mode support, and no locality reporting.
