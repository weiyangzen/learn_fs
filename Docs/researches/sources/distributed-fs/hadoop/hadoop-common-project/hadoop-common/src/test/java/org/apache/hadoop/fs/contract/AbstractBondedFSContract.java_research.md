# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractBondedFSContract.java

Purpose: abstract filesystem contract that "bonds" tests to an externally configured filesystem URI for a given scheme.

Important APIs/types/functions: `AbstractFSContract`, `Configuration`, `FileSystem.get(URI, conf)`, `Path`, `FSNAME_OPTION` pattern `test.fs.%s`, `init`, `loadFilesystemName`, `getFilesystemConfKey`, `getTestFileSystem`, and `getTestPath`.

Control flow/state/persistence: `init` delegates to the base contract, reads a scheme-specific filesystem option, disables the contract when absent, otherwise parses the URI and initializes a `FileSystem`. Invalid URI or initialization arguments are wrapped as `IOException`. The test path defaults to `/test`; `toString` reports scheme and configured FS name.

Dependencies/integration points: used by concrete contract suites for remote/object filesystems that require explicit test endpoints. Integrates with `AbstractFSContract` option lookup and enabled/disabled test gating.

Risks/test signals: key risk is misconfiguration leading to skipped tests or accidental execution against the wrong filesystem. URI parsing and exception wrapping are important for clear test setup failures.
