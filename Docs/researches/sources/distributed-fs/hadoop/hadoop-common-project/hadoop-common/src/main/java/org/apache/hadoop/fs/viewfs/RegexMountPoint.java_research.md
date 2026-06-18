# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/RegexMountPoint.java

`RegexMountPoint<T>` implements regex-based mount entries for `InodeTree`. Instead of matching fixed path components, it compiles a source regex and maps captured groups into a destination URI/path string containing `$name`, `${name}`, or numeric group variables.

Important APIs and state include `initialize()`, `resolve(String, boolean)`, `getVarListInString`, `VAR_PATTERN_IN_DEST`, source/destination strings, compiled `Pattern`, destination variable map, and a list of `RegexMountPointInterceptor`s. Settings use `SETTING_SRCREGEX_SEP` between interceptor settings and source regex, `;` between interceptors, and `:` inside interceptor settings.

Resolution first chooses the source prefix to resolve, excluding the last path component when `resolveLastComponent` is false. It applies source interceptors, runs the source pattern, replaces all configured destination variables from named or indexed regex groups, computes the remaining path from the original source path, applies destination and remaining-path interceptors, and delegates to `InodeTree.buildResolveResultForRegexMountPoint` to create the target filesystem.

State is initialized once and then read during resolution. Persistence is indirect: matching produces a target filesystem URI and operations persist in that target. Dependencies include Java regex, Hadoop `Path`, `StringUtils`, SLF4J, `InodeTree`, and interceptor factory/type classes.

Risks include invalid regex syntax, missing named groups throwing from `Matcher.group`, multiple matches overwriting `resolvedPathStr`, null path-to-resolve when excluding the last component, separator collisions in settings, and target filesystem initialization failures returning null. Tests should cover named and numeric groups, `$x` and `${x}`, no-match behavior, bad regex, interceptor chains, `resolveLastComponent` true/false, remaining path construction, and invalid/missing capture groups.
