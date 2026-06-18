# Research: sources/distributed-fs/alluxio/underfs/cos/src/main/java/alluxio/underfs/cos/COSUnderFileSystemFactory.java

Purpose: UFS factory for native Tencent COS paths.

Important APIs and control flow: `supportsPath` accepts paths starting with `Constants.HEADER_COS`. `create` null-checks path, calls `checkCOSCredentials`, and if access key, secret key, and region are present delegates to `COSUnderFileSystem.createInstance`. Otherwise it propagates an `IOException` stating credentials are unavailable. The factory itself checks fewer properties than `createInstance`, which also requires app id.

State, dependencies, integration, risks, tests: stateless and thread-safe. Dependencies include Alluxio constants, property keys, URI parsing, Guava `Throwables`, and COS UFS implementation. Risk: credential precheck mismatch can produce a later propagated exception for missing app id; `Throwables.propagate` style can obscure checked exception boundaries.
