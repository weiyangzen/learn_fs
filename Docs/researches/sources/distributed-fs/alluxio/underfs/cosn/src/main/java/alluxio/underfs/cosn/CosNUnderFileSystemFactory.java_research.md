# Research: sources/distributed-fs/alluxio/underfs/cosn/src/main/java/alluxio/underfs/cosn/CosNUnderFileSystemFactory.java

Purpose: factory for Hadoop COSN-backed UFS instances, with optional version matching.

Important APIs and control flow: `create` null-checks path and delegates to `CosnUnderFileSystem.createInstance`. `supportsPath(path)` checks `Constants.HEADER_COSN`. `supportsPath(path, conf)` first checks the scheme; if `PropertyKey.UNDERFS_VERSION` is explicitly set by the user, it must exactly equal `getVersion()`, otherwise the bundled version is assumed compatible. `getVersion` returns `CosnUfsConstants.UFS_COSN_VERSION`.

State, dependencies, integration, risks, tests: stateless and thread-safe. Dependencies include generated constants, property keys, and UFS factory API. Risk: exact version matching can reject semantically compatible patch variants; templating/version drift directly affects discovery.
