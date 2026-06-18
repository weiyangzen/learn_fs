# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/HarFs.java

Purpose: `HarFs` is the `AbstractFileSystem`/`FileContext` adapter for the `har` scheme.

Important APIs: package-private constructor and `getUriDefaultPort`.

Control flow and state: construction delegates to `DelegateToFileSystem` with a new `HarFileSystem`, scheme `har`, and authority-required flag false. It reports default port `-1`.

Dependencies and integration: bridges `FileContext` users to `HarFileSystem`; used through Hadoop filesystem service loading/configuration rather than direct public construction.

Risks: behavior is almost entirely inherited from `DelegateToFileSystem` and `HarFileSystem`, so adapter tests should catch initialization and URI translation regressions. Constructor visibility limits external direct use.

Test signals: `FileContext` resolution of `har` URIs, default port behavior, delegation to read-only HAR operations, and authority-less archive URI handling.
