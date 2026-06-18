# sources/distributed-fs/orangefs/src/client/usrint/glob.c

## Purpose
`glob.c` is a bundled glibc-derived pathname glob implementation for the OrangeFS usrint library. It expands shell-style patterns into `glob_t.gl_pathv` results while supporting GNU extensions such as brace expansion, tilde expansion, alternate directory callbacks, mark-only-directory behavior, no-sort behavior, and metacharacter detection. The local changes make the file build outside glibc by mapping internal allocation, stat, readdir, and strdup helpers to normal libc/POSIX interfaces.

## Important APIs And Functions
The exported functions are `glob`, `globfree`, `__glob_pattern_type`, and `glob_pattern_p`/`__glob_pattern_p` when enabled. Major helpers include `next_brace_sub`, which finds comma or closing-brace boundaries while honoring nesting and escaping; `glob_in_dir`, which scans one directory for a final path component; `prefix_array`, which prepends directory names to matched base names; `collated_compare`, which sorts with `strcoll`; and `link_exists2_p`, which verifies symlink targets for directory entries that might be symlinks.

## Control Flow
`glob` first validates the pattern, flags, and result pointer. If `GLOB_BRACE` is set, it detects a brace expression, builds each alternative into a temporary pattern, recursively calls `glob` with `GLOB_APPEND`, and either returns matches or falls through according to `GLOB_NOCHECK`/`GLOB_NOMAGIC`. It initializes `gl_pathv` and offsets for non-append calls, splits the pattern into directory and filename portions, handles trailing slash patterns, expands `~` and `~user` using `HOME`, `getlogin_r`, and passwd lookups, then decides whether the directory portion itself contains magic. If the directory portion is magic, it recursively globs directories with `GLOB_ONLYDIR`, then runs `glob_in_dir` inside each directory and prefixes results. Otherwise it unescapes the directory when needed and calls `glob_in_dir` once. After matching, it appends slashes for `GLOB_MARK`, sorts unless `GLOB_NOSORT`, and returns POSIX/GNU status codes.

`glob_in_dir` handles the final component. If there is no magic and `GLOB_NOCHECK`/`GLOB_NOMAGIC` applies, it can return the literal name. Otherwise it stats a literal name or opens the directory, loops through `readdir`/alternate `gl_readdir`, applies `fnmatch` with `FNM_PERIOD` and `FNM_NOESCAPE` flags, filters `GLOB_ONLYDIR`, verifies symlink targets when needed, accumulates names in stack/heap `globnames` blocks, reallocates `gl_pathv`, appends results, and closes the stream preserving `errno`.

## State And Persistence Behavior
All state is caller-visible through `glob_t`. The implementation allocates `gl_pathv` and each matched path string; callers must release them with `globfree`. `GLOB_APPEND` preserves previous results and adds new entries after `gl_offs + gl_pathc`. No durable state is written, but environment/passwd lookups influence tilde expansion.

## Dependencies And Integration Points
The file includes `usrint.h`, `glob.h`, `fnmatch.h`, dirent/stat/pwd/unistd facilities, and libc compatibility macros. `GLOB_ALTDIRFUNC` allows callers to inject `gl_opendir`, `gl_readdir`, `gl_closedir`, `gl_stat`, and `gl_lstat`, which is the key integration hook for virtualized filesystems. Normal builds use `opendir`, `readdir`, `stat`, `strcoll`, `malloc/realloc/free`, `mempcpy`, and passwd lookup APIs.

## Risks
The implementation has many recursive paths, so brace expansion and globbed directory prefixes can amplify work and memory. The non-glibc portability layer disables glibc's dynamic alloca heuristics by making `__libc_use_alloca(n)` false, pushing more allocations to the heap. Alternate directory callbacks must exactly match expected `glob_t` signatures and return stable dirent/stat data. Several code paths free `pglob` on error, so append users must observe return codes carefully. Tilde expansion depends on environment and passwd state, which may make tests environment-sensitive.

## Test Signals
Tests should cover wildcard matching, bracket expressions, escaped metacharacters, `GLOB_NOESCAPE`, leading-dot behavior with and without `GLOB_PERIOD`, `GLOB_NOCHECK`, `GLOB_NOMAGIC`, `GLOB_DOOFFS`, `GLOB_APPEND`, sorting/locale collation, trailing slash handling, `GLOB_MARK`, `GLOB_ONLYDIR`, brace expansions including malformed braces, tilde expansion success/failure, `GLOB_TILDE_CHECK`, error callback behavior, directory read errors with `GLOB_ERR`, and `GLOB_ALTDIRFUNC` over a fake directory tree.
