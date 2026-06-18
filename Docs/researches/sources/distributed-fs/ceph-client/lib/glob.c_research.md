# sources/distributed-fs/ceph-client/lib/glob.c

## Purpose
`glob.c` implements small shell-style pattern matching for kernel users that need `fnmatch`-like matching without pathname-specific behavior. It is intended for denylist-style string matching and can be built as a module because ATA users may be modular.

## Important APIs, Types, and Functions
The only exported API is `bool glob_match(const char *pat, const char *str)`. Supported metacharacters are `?`, `*`, bracket classes, bracket ranges, leading `!` class inversion, backslash escapes, and literal fallback for malformed opening brackets.

## Control Flow, State, and Persistence
The matcher is iterative and non-recursive. It consumes one pattern token and one string character at a time. `*` stores a single backtracking point (`back_pat`, `back_str`) and later retries from one character later on mismatch. Character classes scan spans until `]`, support an initial literal `]`, and treat missing terminators as a literal `[`. Matching succeeds only when the whole pattern and whole string end together.

## Dependencies and Integration Points
It includes `<linux/glob.h>`, module metadata, and exports `glob_match()`. The comments call out ATA pattern users, but the function is generic and does not special-case `/` or leading `.`.

## Risks and Test Signals
Risks include quadratic worst-case behavior for repeated backtracking, no support for `[^...]` inversion syntax, literal behavior for malformed classes, and full-string rather than substring matching. Tests should include `*` zero/nonzero length matches, trailing-star optimization, `?` not matching NUL, ranges and inverted classes, escaped metacharacters, malformed brackets, and worst-case long patterns.
