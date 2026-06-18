# Research: sources/distributed-fs/alluxio/underfs/abfs/src/main/java/alluxio/underfs/abfs/AbfsUnderFileSystemFactory.java

Purpose: factory registering ABFS paths with Alluxio's UFS factory registry.

Important APIs and control flow: the public no-arg constructor has no state. `create` asserts the path is non-null and delegates to `AbfsUnderFileSystem.createInstance(new AlluxioURI(path), conf)`. `supportsPath` accepts paths beginning with `Constants.HEADER_ABFS` or `Constants.HEADER_ABFSS`.

State, dependencies, integration, risks, tests: this class is stateless and thread-safe. Dependencies include Alluxio URI parsing, constants, UFS factory interface, and `AbfsUnderFileSystem`. Integration occurs through Java service discovery in the module packaging. Risk is limited: it does not implement the configuration-aware `supportsPath(path, conf)` overload, so selection is based only on URI scheme.
