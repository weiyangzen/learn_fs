# Research: sources/distributed-fs/alluxio/underfs/cephfs-hadoop/pom.xml

Purpose: Maven descriptor for the CephFS Hadoop-backed UFS module, `alluxio-underfs-cephfs-hadoop`.

Important APIs and control flow: it depends on `io.github.opendataio:cephfs-hadoop` while excluding log4j and slf4j-log4j12, plus provided core common and `alluxio-underfs-hdfs`. The shade plugin excludes license/signature files and removes HDFS UFS factory service metadata, preserving this module's factory identity. Copy-rename plugin participates in packaging.

State, dependencies, integration, risks, tests: build state is dependency/shaded artifact output. Integration relies on cephfs-hadoop implementing a Hadoop-compatible filesystem used by `HdfsUnderFileSystem`. Risks include native/Hadoop Ceph library compatibility, logging dependency exclusions, and factory service conflicts if shading filters drift.
