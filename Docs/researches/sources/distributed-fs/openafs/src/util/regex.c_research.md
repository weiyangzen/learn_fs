# sources/distributed-fs/openafs/src/util/regex.c

Purpose: Provides a historical V6 ed-style regular expression compiler and executor for platforms or code paths that use `re_comp()` / `re_exec()`.

Important APIs and state: `re_comp(const char *sp)` compiles into static `expbuf[512]`; `re_exec(const char *p1)` matches the last compiled expression. Static state includes capture start/end arrays, compiled buffer, and anchor flag.

Control flow: Compilation tokenizes special constructs for dot, character classes, anchors, grouping, backreferences, and `*`, emitting bytecode-like opcodes. Execution clears capture arrays, optionally enforces leading anchor, applies a fast first-character scan for literal-leading regexes, and recursively advances through the compiled program with greedy star handling and backreference comparison.

Dependencies and integration: Only depends on OpenAFS platform config. It supplies old libc-compatible entry points.

Risks and test signals: All regex state is static and non-thread-safe. Pattern size and capture count are fixed (`ESIZE`, `NBRA`). The syntax is not POSIX extended regex, so users must expect old ed semantics. Malformed internal state can return `-1` from matching. There are no local tests in this subset; consumers should test representative legacy patterns.
