# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/RegexMountPointInterceptorType.java

`RegexMountPointInterceptorType` is the enum registry for regex mount interceptors. It currently exposes one type, `REPLACE_RESOLVED_DST_PATH`, configured with the lowercase tag `replaceresolveddstpath`.

The enum stores a `configName` for each type and populates a static map from config name to enum instance. `get(String)` is the lookup API used by `RegexMountPointInterceptorFactory`; `getConfigName()` is used by interceptor serialization.

There is no persistence or mutable runtime state after static initialization. Integration is limited but important: this enum is the compatibility contract for serialized interceptor settings in configuration keys.

Risks are configuration compatibility and namespace collisions. Renaming `configName` would break existing mount tables. Adding new enum values requires factory support and tests for serialization/deserialization. Current tests should assert lookup of the known tag, null for unknown tags, and serialization by `RegexMountPointResolvedDstPathReplaceInterceptor`.
