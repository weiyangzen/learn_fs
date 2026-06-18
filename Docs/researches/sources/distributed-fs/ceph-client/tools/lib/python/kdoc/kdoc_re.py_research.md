# sources/distributed-fs/ceph-client/tools/lib/python/kdoc/kdoc_re.py

Purpose: Provides `KernRe`, a small wrapper around Python `re` that centralizes regex compilation, optional caching, match-result storage, concatenation, and common regex operations for the kernel-doc Python code.

Important APIs/types/functions: `re_cache` is the module-level pattern cache. `KernRe.__init__()` compiles or reuses a pattern. `__add__()` concatenates two `KernRe` patterns and ORs their flags. `match()`, `search()`, `finditer()`, `findall()`, `split()`, and `sub()` delegate to the compiled regex while `match()`/`search()` store `last_match`. `group()` and `groups()` read the last match.

Control flow: Construction calls `_add_regex()`, which first looks up the raw pattern string in `re_cache`, then compiles with flags if missing and stores it only when `cache=True`. Calls to `match()` or `search()` mutate `last_match`, after which callers can request groups without keeping the match object.

State and persistence: Regex cache and last match are in-memory only. The cache key is only the pattern string, not the flags, so the first cached compilation for a pattern determines the flags used by later cached construction of the same string.

Dependencies/integration: Wraps Python `re` and is used heavily by `kdoc_parser.py`, `xforms_lists.py`, and related tokenizer/parser code to make regex definitions composable and cacheable.

Risks: Cache keys ignore flags, which can produce wrong behavior if the same string is compiled with different flags and caching enabled. `group()`/`groups()` assume a successful prior match and will raise on `None`. `__add__()` assumes `other` is a `KernRe` with `cache` and `regex` attributes.

Test signals: Add tests for cache reuse, same-pattern-different-flags behavior, concatenation flags, `last_match` replacement, and failed `group()` behavior.
