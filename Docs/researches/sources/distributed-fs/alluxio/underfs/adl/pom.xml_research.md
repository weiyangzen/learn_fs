# Research: sources/distributed-fs/alluxio/underfs/adl/pom.xml

Purpose: Maven module descriptor for Alluxio's Azure Data Lake Gen1 underfs implementation.

Important APIs and control flow: artifact `alluxio-underfs-adl` inherits from `alluxio-underfs`, sets `ufs.hadoop.version` to `3.3.4`, depends on Hadoop `hadoop-azure-datalake`, provided core common, and `alluxio-underfs-hdfs`. Test dependencies include commons-lang3 and the core-common test jar. Shade configuration removes license/signature files and excludes HDFS factory implementation/service metadata to avoid factory collisions.

State, dependencies, integration, risks, tests: build state is Maven dependency graph and shaded artifact contents. Integration is through Hadoop ADL and the HDFS underfs base. Risks include ADL Gen1 library lifecycle/compatibility, factory service exclusion correctness, and duplicated build-path properties required for submodule builds.
