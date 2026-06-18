# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/RegexMountPointInterceptorFactory.java

`RegexMountPointInterceptorFactory` is a private factory that deserializes one interceptor settings string into a `RegexMountPointInterceptor`. The expected format is `<type>:<payload>`, with the concrete built-in replace interceptor using `replaceresolveddstpath:<regex>:<replacement>`.

Control flow finds the first internal separator `:`, lowercases the type tag, resolves it with `RegexMountPointInterceptorType.get`, and switches on the enum. The only supported type is `REPLACE_RESOLVED_DST_PATH`, which is delegated to `RegexMountPointResolvedDstPathReplaceInterceptor.deserializeFromString`. Unknown types, missing separators, or empty payloads return null; callers turn null into an `IOException` during regex mount initialization.

There is no mutable state or persistence. Dependencies are the interceptor type enum, regex mount separator constants, and the replace interceptor implementation.

Risks are format rigidity and silent nulls. Regex or replacement strings containing `:` are not supported by the replace interceptor deserializer, and bad configs surface as a generic illegal settings error. Tests should cover unknown types, missing separators, trailing separators, case-insensitive type tags, valid replace interceptors, and payloads with unsupported separators.
