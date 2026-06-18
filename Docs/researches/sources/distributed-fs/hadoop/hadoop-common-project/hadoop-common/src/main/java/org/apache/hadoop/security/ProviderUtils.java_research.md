# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ProviderUtils.java


Purpose: `ProviderUtils` contains shared helpers for Hadoop credential/key provider integrations, especially provider URI nesting, recursive filesystem-provider exclusion, and password discovery.

Important APIs and types: Public APIs include `unnestUri(URI)`, `nestURIForLocalJavaKeyStoreProvider(URI)`, `excludeIncompatibleCredentialProviders(Configuration, Class<? extends FileSystem>)`, `locatePassword(String, String)`, `noPasswordWarning()`, and `noPasswordError()`.

Control flow: URI helpers convert nested provider URIs such as local JCEKS wrappers to underlying `Path` forms and validate that local keystore nesting only accepts file URIs without authority. Provider exclusion parses the configured credential provider path, resolves filesystem-backed providers, drops providers whose filesystem class is assignable from the target filesystem to avoid recursion, and returns either the original configuration or a cloned configuration with a rewritten/unset provider path. Password lookup prefers an environment variable, then a classpath resource file, trimming file content.

State and persistence: The class is stateless. It reads environment variables and classpath resources and may clone configuration, but does not write files.

Dependencies and integration: It depends on Hadoop `FileSystem`, `Path`, credential provider factory classes, keystore provider classes, commons IO, and SLF4J. Filesystems and credential providers call it to avoid bootstrapping cycles.

Risks and test signals: Tests should cover malformed provider URIs, non-filesystem providers, exclusion and non-exclusion cases, local URI validation, password env/file precedence, missing password files, and generated warning text. Risks include silently skipping invalid provider URIs and exposing default-password warnings too late in startup.
