# Research: sources/distributed-fs/alluxio/underfs/cosn/src/test/java/alluxio/underfs/cosn/CosNUnderFileSystemFactoryTest.java

Purpose: registry tests for COSN factory discovery and version gating.

Important APIs and control flow: `factory` asserts a factory is found for `cosn://test-bucket/path` using global configuration. `version` asserts discovery works with no explicit version, works when `UNDERFS_VERSION` is `3.1.0-5.8.5`, and returns null when `UNDERFS_VERSION` is `error-version`.

State, dependencies, integration, risks, tests: state includes global mutable `Configuration`, which the test modifies. Dependencies include UFS registry and property keys. Test signal is good for version-aware selection. Risk: global config mutation may leak if not reset by test framework; the test does not instantiate a COSN UFS or validate Hadoop credentials.
