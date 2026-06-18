# Research: sources/distributed-fs/alluxio/underfs/cephfs-hadoop/src/main/java/alluxio/underfs/cephfshadoop/CephfsHadoopUnderFileSystem.java

Purpose: thin `HdfsUnderFileSystem` subclass for CephFS through the cephfs-hadoop adapter.

Important APIs and control flow: `createInstance` calls inherited `createConfiguration(conf)` and constructs `CephfsHadoopUnderFileSystem`. The constructor passes URI, Alluxio UFS config, and Hadoop config to the superclass. `getUnderFSType` returns `cephfs-hadoop`.

State, dependencies, integration, risks, tests: state and persistence are inherited from `HdfsUnderFileSystem` and the cephfs-hadoop Hadoop filesystem. Dependencies include Hadoop `Configuration`, Alluxio URI/config types, and the cephfs-hadoop module dependency. Risk is mostly delegated: this class does not customize permissions, block size, locality, or error mapping, so any Ceph-specific semantics must be correctly handled by the Hadoop adapter.
