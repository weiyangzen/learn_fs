# Research: sources/distributed-fs/alluxio/underfs/cosn/src/main/java/alluxio/underfs/cosn/CosnUnderFileSystem.java

Purpose: thin HDFS-adapter UFS for Tencent COSN through Hadoop COS libraries.

Important APIs and control flow: `createInstance` calls inherited `createConfiguration(conf)` and constructs `CosnUnderFileSystem`. The constructor delegates URI, Alluxio UFS config, and Hadoop config to `HdfsUnderFileSystem`. `getUnderFSType` returns `cosn`.

State, dependencies, integration, risks, tests: runtime state and persistence are inherited from `HdfsUnderFileSystem` and Hadoop COSN. Dependencies include Hadoop `Configuration`, Alluxio URI/config types, and hadoop-cos library. Risks are mostly delegated: no custom block size, permission, locality, or error mapping appears here, so correctness relies on Hadoop COSN and HDFS base behavior.
