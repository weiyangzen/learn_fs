# sources/distributed-fs/alluxio/underfs/wasb/src/main/java/alluxio/underfs/wasb/WasbUnderFileSystem.java

## Purpose
`WasbUnderFileSystem` adapts Azure Blob Storage through Hadoop's WASB/WASBS filesystem by extending Alluxio's `HdfsUnderFileSystem`.

## APIs and Control Flow
`createConfiguration` starts with HDFS UFS configuration, copies Alluxio Azure account keys matching `UNDERFS_AZURE_ACCOUNT_KEY` templates, and sets Hadoop implementation classes for secure `wasbs` or plain `wasb`. `createInstance` detects the URI scheme and constructs the UFS. `getUnderFSType` returns `wasb`. `getBlockSizeByte` returns Alluxio's default block size. `getStatus` delegates to HDFS UFS, then rewrites file statuses to use object-store block size instead of Azure's reported 512 MiB.

## State, Dependencies, and Integration
State is inherited from `HdfsUnderFileSystem`; this class mainly supplies the Hadoop `Configuration`. It depends on Hadoop Azure classes by class-name string, Alluxio property keys, and HDFS UFS behavior. File locations are unsupported and return null.

## Risks and Test Signals
Returning null for file locations requires callers to tolerate unsupported locality. The status rewrite preserves most metadata but substitutes last-modified null with `0L`. Tests only verify factory registration for schemes; configuration rewriting and status replacement are not covered here.
