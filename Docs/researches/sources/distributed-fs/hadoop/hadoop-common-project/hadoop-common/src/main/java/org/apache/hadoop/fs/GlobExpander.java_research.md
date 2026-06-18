# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/GlobExpander.java

Purpose: `GlobExpander` rewrites path glob patterns so brace groups containing slashes are expanded into multiple path patterns before per-component glob matching.

Important APIs: public static `expand(String)`, internal `StringWithOffset`, `expandLeftmost`, and `leftmostOuterCurlyContainingSlash`.

Control flow and state: `expand` maintains a queue of patterns, repeatedly expanding the leftmost outer brace group that contains `/`, and emits fully expanded patterns when no such group remains. Escaped characters are consumed and validated; malformed trailing escapes throw `IOException`. No persistent state exists.

Dependencies and integration: called by `Globber.doGlob` before splitting paths into components, enabling brace alternatives that cross directory boundaries.

Risks: expansion can grow combinatorially with nested brace alternatives. Only brace groups containing slash are expanded here; other brace semantics are handled later by `GlobPattern`. Escaped-character handling must remain aligned with glob matching.

Test signals: examples with nested braces, slash-containing alternatives, escaped slash/characters, malformed trailing backslash, groups without slash, and ordering of expanded patterns.
