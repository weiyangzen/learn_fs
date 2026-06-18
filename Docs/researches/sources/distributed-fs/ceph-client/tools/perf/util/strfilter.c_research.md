# sources/distributed-fs/ceph-client/tools/perf/util/strfilter.c

## Purpose

`strfilter.c` parses and evaluates glob-based boolean string filters. It supports rule expressions containing glob leaves, grouping parentheses, logical AND, OR, and NOT.

## Important APIs, Types, and Functions

Public functions are `strfilter__new()`, `strfilter__or()`, `strfilter__and()`, `strfilter__compare()`, `strfilter__delete()`, and `strfilter__string()`. Private functions tokenize (`get_token()`), allocate/delete AST nodes, parse expressions recursively, append new root operators, evaluate nodes, and reconstruct a string.

## Control Flow and Data Flow

`strfilter__new()` allocates a filter and parses rules into an AST. The parser reads tokens, builds operator nodes by adjusting the current/root right branch, recursively handles parentheses, and stores glob strings in leaf nodes. AND binds more tightly than OR through the parser's root/last-op manipulation. `strfilter__compare()` recursively evaluates the AST and calls `strglobmatch()` for leaves. Append functions parse a second rule and wrap the existing root and new subtree under an OR or AND node.

## State and Persistence Behavior

The filter owns its AST and duplicated glob strings. Operator node `p` pointers reference static operator strings and are not freed; leaf `p` strings are freed. Reconstructed rule strings are newly allocated and caller-owned.

## Dependencies and Integration Points

It depends on `string2.h` glob matching, Linux ctype/string helpers, zalloc, and errno. It can be used by perf filtering options that need simple boolean glob matching.

## Risks and Edge Cases

Parsing reports syntax errors by returning an error pointer into the input, or NULL for allocation failure. Escaped separators and `!` inside glob character classes receive special token handling. Recursion depth is unbounded by this code. `strfilter__string()` does not explicitly write the final NUL after reconstruction, relying on malloc contents would be unsafe if not otherwise terminated by copied leaf strings; callers should test this path carefully.

## Test Signals

Tests should cover precedence (`a|b&c`), parentheses, NOT, escaped operators, `!` in glob classes, syntax-error pointers, append OR/AND, AST deletion, string reconstruction, and glob match behavior.
