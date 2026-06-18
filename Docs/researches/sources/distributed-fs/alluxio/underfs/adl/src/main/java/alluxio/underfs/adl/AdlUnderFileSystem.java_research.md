# Research: sources/distributed-fs/alluxio/underfs/adl/src/main/java/alluxio/underfs/adl/AdlUnderFileSystem.java

Purpose: Azure Data Lake Gen1 UFS implementation built on `HdfsUnderFileSystem`, translating Alluxio ADL credential properties into Hadoop configuration and adjusting object-store-like metadata.

Important APIs and control flow: `createConfiguration` copies HDFS config, forwards template-matched Azure client id, secret, and refresh URL keys, logs the Hadoop configuration object, and sets `fs.adl.oauth2.access.token.provider.type` to `ClientCredential`. `createInstance` constructs the UFS. `getUnderFSType` returns `adl`. `getBlockSizeByte` returns default Alluxio block size. `getStatus` rewrites file statuses with normalized block size. Owner/mode setters are no-ops; file locations are unsupported and return null.

State, dependencies, integration, risks, tests: state is inherited Hadoop filesystem state and Hadoop config. Dependencies include Hadoop ADL libraries, Alluxio property templates, and status classes. Risks include logging sensitive config, no locality, no ACL/mode mutation, and deprecated Gen1 backend constraints.
