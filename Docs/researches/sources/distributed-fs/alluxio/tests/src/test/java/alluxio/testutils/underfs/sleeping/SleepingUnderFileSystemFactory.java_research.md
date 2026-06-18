# Research: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/sleeping/SleepingUnderFileSystemFactory.java

Purpose: factory for creating `SleepingUnderFileSystem` instances in tests. It binds an options object to the `sleep://` scheme so tests can register predictable operation delays.

Important APIs and control flow: the factory stores `SleepingUnderFileSystemOptions`. `create` validates the path, constructs an `AlluxioURI`, and returns a new `SleepingUnderFileSystem` using that URI, options, and UFS configuration. `supportsPath` accepts non-null paths that start with the sleep scheme header.

State, dependencies, integration, risks, tests: state is the shared options instance used by all UFS instances created from the factory. Dependencies include Alluxio URI parsing and UFS factory registration infrastructure. Risk: mutating the options after factory construction can affect later operations if the same object is shared; this is useful in tests but should be deliberate.
