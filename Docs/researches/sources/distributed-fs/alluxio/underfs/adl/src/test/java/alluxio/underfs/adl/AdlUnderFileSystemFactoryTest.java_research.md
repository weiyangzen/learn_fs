# Research: sources/distributed-fs/alluxio/underfs/adl/src/test/java/alluxio/underfs/adl/AdlUnderFileSystemFactoryTest.java

Purpose: registry discovery test for the ADL underfs module.

Important APIs and control flow: it calls `UnderFileSystemFactoryRegistry.find("adl://localhost/test/path", Configuration.global())` twice and asserts non-null, then asserts `alluxio://localhost/test/path` returns null. The duplicated ADL lookup appears intended to cover supported paths but does not test `adls://` despite the factory supporting it.

State, dependencies, integration, risks, tests: state is global factory registry. Dependencies include Alluxio configuration and registry classes. The test signal verifies service registration for at least `adl://`. Risk: it misses `adls://`, does not create a UFS, and does not validate credentials or Hadoop configuration translation.
