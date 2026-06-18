# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractFSContract.java

Purpose: `AbstractFSContract` is the abstract configuration and capability model behind Hadoop filesystem contract tests. Concrete contract classes subclass it to provide the filesystem under test, scheme, and root test path.

Important APIs and types: it extends `Configured` and uses `Configuration`, `FileSystem`, `Path`, `URI`, `URL`, `ContractOptions`, and SLF4J. Abstract methods are `getTestFileSystem()`, `getScheme()`, and `getTestPath()`. Public helpers include `init()`, `teardown()`, `getFileSystem(URI)`, `isEnabled()`, `setEnabled()`, `isSupported()`, `getLimit()`, `getOption()`, and `getConfKey()`.

Control flow: the constructor stores the configuration and tries to load `ContractOptions.CONTRACT_OPTIONS_RESOURCE` through `maybeAddConfResource()`, logging whether it was found. `init()` and `teardown()` are no-ops for subclasses to override. `addConfResource()` asserts a named resource exists, while `maybeAddConfResource()` probes the classloader and adds the resource to the configuration if present. `getFileSystem(URI)` delegates to the standard `FileSystem.get(uri, conf)` factory. Feature and limit lookups build keys by appending a feature string to `ContractOptions.FS_CONTRACT_KEY`. `toURI()` constructs a URI from the contract scheme and path.

State and persistence behavior: persistent state is limited to the inherited `Configuration` and the mutable boolean `enabled`. Configuration resources and options determine which contract tests run and how they interpret filesystem-specific behavior.

Dependencies and integration points: every abstract contract test uses this class indirectly through `AbstractFSContractTestBase` to decide feature support, limits, test root, and filesystem instance. It is the bridge between concrete filesystems and generic contract tests.

Risks: `enabled` is a simple mutable flag without synchronization, which is fine for ordinary JUnit lifecycle but not a concurrent control plane. `toURI()` uses `new URI(getScheme(), path, null)`, so unusual schemes or path formats may need subclass care. A comment contains a typo ("norrmal") but no behavior issue.

Test signals: this is infrastructure, not a test. Correct behavior is evidenced by concrete contract suites being able to load optional resources, query feature flags and limits, construct test paths, and obtain configured filesystem instances.
