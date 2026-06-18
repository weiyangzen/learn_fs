# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_arena_strsearch.h

Purpose: supplies arena-string helpers, notably `bpf_arena_strlen()` and non-recursive shell-style `glob_match()` for BPF arena tests.

Important APIs and functions: `bpf_arena_strlen()` scans an arena string with `cond_break`; `glob_match(pat, str)` supports `?`, `*`, character classes, `!` class inversion, ranges, and backslash escaping over arena strings.

Control flow: `glob_match()` consumes pattern and string tokens in one loop. A single saved `*` backtrack point handles mismatch retries, making runtime at most quadratic without recursion. Character classes iterate ranges until `]`, falling back to literal handling on malformed input.

State and persistence: function-local pointers only; no persistent state.

Dependencies and integration points: depends on `bpf_arena_common.h` and `cond_break` for verifier-friendly loops.

Risks: intended semantics match `fnmatch(..., 0)` but do not special-case `/` or leading `.`; malformed brackets are literal; worst-case patterns can be quadratic; no preprocessing/cache for repeated patterns.

Test signals: string tests should include wildcard, class, inverted class, escaped literal, malformed class, trailing `*`, and mismatch backtracking cases.
