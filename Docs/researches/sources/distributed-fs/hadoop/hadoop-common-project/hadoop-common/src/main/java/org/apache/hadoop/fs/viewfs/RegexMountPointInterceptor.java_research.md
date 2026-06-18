# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/RegexMountPointInterceptor.java

`RegexMountPointInterceptor` is the limited-private unstable interface for plug-in transformations around regex mount resolution. It lets a regex mount transform the source string before matching, transform the resolved destination string after group replacement, and transform the remaining `Path` before the final `ResolveResult` is built.

The interface methods are `initialize()`, `interceptSource(String)`, `interceptResolvedDestPathStr(String)`, `interceptRemainingPath(Path)`, `getType()`, and `serializeToString()`. It has no state itself; implementations own validation, compiled patterns, and serialization format.

Integration is through `RegexMountPoint.initializeInterceptors`, which creates implementations with `RegexMountPointInterceptorFactory`, initializes them, and applies them in list order during `resolve`. `RegexMountPointResolvedDstPathReplaceInterceptor` is the only built-in implementation.

Risks are SPI and ordering risks: interceptors can produce invalid source strings, invalid destination URIs, or remaining paths that no longer correspond to the resolved prefix. Since initialization can throw `IOException`, bad settings fail mount-table construction. Tests should verify interceptor ordering, initialization failure propagation, serialization round trips, and behavior when transformed destination paths cannot initialize a target filesystem.
