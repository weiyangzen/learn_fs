## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDelegateToFileSystem.java

Purpose: verifies that `AbstractFileSystem.get` for FTP normalizes a URI without an explicit port to the FTP default port regardless of the configured default filesystem URI.

Important APIs/types/functions: `AbstractFileSystem.get`, `FileSystem.setDefaultUri`, `FTP.DEFAULT_PORT`, `DelegateToFileSystem` indirectly through the FTP AFS implementation, and `Configuration`.

Control flow: `testDefaultUriInternal` sets the default filesystem to either `hdfs://dummyhost` or `hdfs://dummyhost:8020`, then resolves `ftp://dummyhost`. It asserts that the resulting AFS URI includes `FTP.DEFAULT_PORT`.

State and persistence: no local files are created. State is confined to a fresh `Configuration`.

Dependencies/integration points: integrates the AFS factory with Apache Commons Net's FTP default port constant and Hadoop's default URI handling. It guards against default-FS authority/port leakage into unrelated schemes.

Risks and test signals: a failure means delegated filesystem construction, URI default-port insertion, or default-FS isolation has regressed. The test uses a dummy FTP host and should not perform network I/O; unexpected network dependency would be a risk.
