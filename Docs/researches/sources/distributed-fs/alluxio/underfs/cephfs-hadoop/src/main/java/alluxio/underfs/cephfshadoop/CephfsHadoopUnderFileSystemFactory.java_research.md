# Research: sources/distributed-fs/alluxio/underfs/cephfs-hadoop/src/main/java/alluxio/underfs/cephfshadoop/CephfsHadoopUnderFileSystemFactory.java

Purpose: factory for the cephfs-hadoop UFS implementation, extending HDFS factory behavior while narrowing path support to the CephFS Hadoop scheme.

Important APIs and control flow: `create` null-checks path and returns `CephfsHadoopUnderFileSystem.createInstance(new AlluxioURI(path), conf)`. `supportsPath(path)` checks `Constants.HEADER_CEPHFS_HADOOP`; `supportsPath(path, conf)` delegates to the path-only check.

State, dependencies, integration, risks, tests: stateless and thread-safe. Dependencies include Alluxio constants, URI parsing, HDFS UFS factory base, and CephfsHadoop UFS. Risk: configuration-aware support does not validate Ceph version or required properties, so discovery can succeed before runtime connection/configuration failure.
