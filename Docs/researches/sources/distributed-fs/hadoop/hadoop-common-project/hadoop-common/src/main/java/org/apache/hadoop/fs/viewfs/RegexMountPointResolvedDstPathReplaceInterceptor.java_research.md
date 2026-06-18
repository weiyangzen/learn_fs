# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/RegexMountPointResolvedDstPathReplaceInterceptor.java

`RegexMountPointResolvedDstPathReplaceInterceptor` is the built-in regex mount interceptor that applies a regex replacement to the resolved destination path string after capture-group substitution. It does not alter the source string or remaining path.

Important APIs are the constructor, `initialize()`, `interceptResolvedDestPathStr(String)`, `serializeToString()`, and `deserializeFromString(String)`. State consists of the source regex string, replacement string, and compiled `Pattern`. Initialization compiles the regex and wraps `PatternSyntaxException` as `IOException`. Interception uses `Matcher.replaceAll(replaceString)`.

The serialized format is `replaceresolveddstpath:<srcRegex>:<replaceString>`, using `RegexMountPoint.INTERCEPTOR_INTERNAL_SEP`. Deserialization splits on `:`, requires exactly three parts, and returns null for bad formats. The implementation assumes the regex and replacement do not contain `:`.

Dependencies include Java regex, Hadoop `Path`, the interceptor interface, and the interceptor type enum. Persistence is configuration serialization only; actual filesystem persistence occurs after the regex mount resolves to a target.

Risks include separator limitations, replacement syntax surprises from `Matcher.replaceAll` (`$` and backslash semantics), invalid regex initialization, and unexpected global replacement across the whole destination string. Tests should cover valid replacements, no-op unmatched replacements, invalid regex, serialization round trip, bad serialized lengths, and replacement strings with regex metacharacter behavior.
