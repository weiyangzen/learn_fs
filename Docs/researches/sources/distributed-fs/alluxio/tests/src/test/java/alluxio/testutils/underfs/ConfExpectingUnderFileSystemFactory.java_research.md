# Research: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/ConfExpectingUnderFileSystemFactory.java

Purpose: test-only UFS factory that validates mount-specific configuration before returning a local UFS. It is useful for tests that must prove configuration propagation into `UnderFileSystemFactory.create`.

Important APIs and control flow: constructor stores a custom scheme and expected config map. `supportsPath` accepts paths beginning with `<scheme>:///`. `create` checks non-null path, asserts `conf.getMountSpecificConf()` equals the expected map, strips the custom scheme down to a local path using nested `AlluxioURI`, and returns `LocalUnderFileSystem`.

State, dependencies, integration, risks, tests: state is immutable expected configuration. Dependencies include Guava `Preconditions`, local UFS, and Alluxio URI parsing. Risk: exact map equality is strict about keys/values and ignores defaults outside mount-specific config, which is intended for targeted propagation tests but not realistic factory matching.
