# Research: sources/distributed-fs/alluxio/underfs/abfs/pom.xml

Purpose: Maven module descriptor for Alluxio's Azure Data Lake Storage Gen2 ABFS underfs implementation. It builds `alluxio-underfs-abfs` under the `alluxio-underfs` parent.

Important APIs and control flow: it sets `build.path` and `ufs.hadoop.version` to `3.3.4`, depends on Hadoop `hadoop-azure`, provided `alluxio-core-common`, and `alluxio-underfs-hdfs`, plus a test jar. The shade plugin excludes license/signature files and specifically excludes HDFS factory service metadata so the shaded artifact exposes the ABFS factory rather than accidentally registering HDFS. The copy-rename plugin participates in distribution packaging.

State, dependencies, integration, risks, tests: build state is Maven dependency/shade output. Integration is with Hadoop ABFS classes and Alluxio's HDFS underfs base. Risks include Hadoop Azure version compatibility, service provider metadata conflicts, and reliance on the parent POM for plugin versions.
