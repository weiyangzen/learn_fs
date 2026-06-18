# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/Globber.java

Purpose: `Globber` implements `FileSystem.globStatus(Path, PathFilter)` and `FileContext` globbing, including brace expansion, component-wise filesystem traversal, optional symlink disambiguation, tracing, and deterministic result sorting.

Important APIs: constructors for `FileSystem`/`FileContext`, `glob`, `doGlob`, helper status/list/fixRelative/scheme/authority methods, `createGlobber`, and nested `GlobBuilder` with path pattern, path filter, and symlink resolution controls.

Control flow and state: `glob` opens a trace scope and delegates to `doGlob`. `doGlob` resolves scheme/authority, expands slash-containing brace groups, turns each flattened pattern into absolute components, seeds traversal at root, and iteratively builds candidate `FileStatus` lists. Non-terminal literal components are optimistically appended until a later stat/list is needed. Glob components list candidate directories, disambiguate one-entry listings when symlink resolution is enabled, filter children by `GlobFilter`, and avoid recursing into files. Final user filtering is applied only to complete paths. No matches for a plain non-wildcard single pattern returns null; other misses return an empty sorted array.

Dependencies and integration: integrates with `FileSystem`, `FileContext`, `GlobExpander`, `GlobFilter`, `FsTracer`, `TraceScope`, and `DurationInfo`. It is central to shell and API glob semantics.

Risks: object stores with inconsistent listings can surface warnings/misses. Symlink resolution adds extra status calls; disabling it changes one-entry listing semantics. The builder method name `withPathFiltern` appears misspelled but is the exposed API here. Null `filter` would fail at final accept unless callers supply a default upstream.

Test signals: wildcard and non-wildcard misses, root and Windows drive patterns, hidden HDFS directories like `.snapshot`, symlink one-entry disambiguation, object-store deleted directory behavior, result sorting, brace expansion ordering, and builder symlink toggle.
