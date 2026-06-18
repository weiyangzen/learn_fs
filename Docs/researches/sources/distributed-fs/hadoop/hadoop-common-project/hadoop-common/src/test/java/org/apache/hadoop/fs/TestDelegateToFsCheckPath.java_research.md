## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDelegateToFsCheckPath.java

Purpose: verifies that `DelegateToFileSystem` derives its default port behavior from the child `FileSystem` when available, and that `AbstractFileSystem.checkPath` accepts paths with implicit default ports.

Important APIs/types/functions: `DelegateToFileSystem`, `AbstractFileSystem.checkPath`, `FileSystem.getDefaultPort`, `Path`, and dummy `FileSystem` subclasses. `DummyDelegateToFileSystem` wires a custom child filesystem into the delegate.

Control flow: `testCheckPathWithoutDefaultPort` constructs `dummy://dummy-host` with a child filesystem that does not override `getDefaultPort` and checks a matching path. `testCheckPathWithDefaultPort` constructs a URI with port `1234`, then checks a path omitting the port; the overridden child default port should make this acceptable.

State and persistence: no external state. Dummy filesystem methods are stubs returning null/false/empty arrays because only URI/path validation is under test.

Dependencies/integration points: protects the bridge between old `FileSystem` implementations and `AbstractFileSystem` delegates. This is important for schemes where legacy file systems define a meaningful default port.

Risks and test signals: if default-port propagation changes, checkPath may reject paths that should target the same FS. The dummy implementations intentionally avoid real I/O; accidental calls to methods beyond `getDefaultPort` would likely produce null behavior and expose a control-flow regression.
