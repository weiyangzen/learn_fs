# Research: sources/distributed-fs/alluxio/underfs/cephfs/pom.xml

Purpose: Maven descriptor for the native CephFS UFS module.

Important APIs and control flow: artifact `alluxio-underfs-cephfs` inherits from `alluxio-underfs`, sets `build.path`, and depends on provided `alluxio-core-common`, the CephFS Java/native binding dependency from the parent dependency management, and packaging plugins. Unlike Hadoop-backed modules, this module does not route through HDFS and therefore does not need HDFS factory service exclusions.

State, dependencies, integration, risks, tests: build state is the native CephFS adapter artifact. Integration risk is higher than pure Java adapters because runtime needs the Ceph native libraries and compatible Java binding. Packaging must ensure service discovery for `CephFSUnderFileSystemFactory` and no missing native classes at runtime.
