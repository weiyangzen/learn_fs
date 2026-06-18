# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestRegexMountPointInterceptorFactory.java

Purpose: verifies factory parsing for regex mount point interceptors. The tests focus on the serialized string format and ensure valid strings produce the correct interceptor implementation while malformed type names return `null`.

Important APIs and types: `RegexMountPointInterceptorFactory.create`, `RegexMountPointInterceptor`, `RegexMountPointResolvedDstPathReplaceInterceptor`, `RegexMountPointInterceptorType.REPLACE_RESOLVED_DST_PATH`, and `RegexMountPoint.INTERCEPTOR_INTERNAL_SEP`.

Control flow: `testCreateNormalCase` builds `replaceresolvedpath:<src>:<replace>` using the canonical config name and separator, calls the factory, and asserts the returned object is a replace interceptor. `testCreateBadCase` corrupts the config-name prefix and asserts no interceptor is built.

State and persistence: no persistent state; all inputs are strings. The factory is expected to parse without side effects.

Dependencies and integration: this protects regex mount configuration loading, where serialized interceptors are embedded in mount settings and must be instantiated dynamically.

Risks and test signals: failures indicate either an incompatible serialized config format, too-lenient parsing that accepts garbage, or too-strict parsing that rejects valid interceptor definitions.
