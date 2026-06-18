# sources/distributed-fs/glusterfs/libglusterfs/src/parse-utils.c

## Purpose
`parse-utils.c` wraps POSIX extended regular expressions in a small stateful parser object. It lets callers compile a regex once, set an input string, and repeatedly retrieve allocated copies of successive matches.

## Important APIs, Types, And Functions
The public functions are `parser_init(const char *regex)`, `parser_set_string(struct parser *parser, const char *complete_str)`, `parser_unset_string(struct parser *parser)`, `parser_deinit(struct parser *ptr)`, and `parser_get_next_match(struct parser *parser)`. The `struct parser` type is declared in `glusterfs/parse-utils.h` and contains the regex text, compiled `regex_t`, match array, owned `complete_str`, and moving `_rstr` cursor.

## Control Flow
`parser_init()` allocates the parser, duplicates the regex, compiles it with `REG_EXTENDED`, logs compilation failure, and initializes `complete_str` to NULL. `parser_set_string()` validates arguments, duplicates the target string, and points `_rstr` at the duplicate. `parser_get_next_match()` runs `regexec()` from `_rstr`, allocates a copy of the matched range with `gf_strndup()`, advances `_rstr` to the match end, and returns the copy. `parser_unset_string()` frees the current duplicated input and avoids a later double-free. `parser_deinit()` frees compiled regex state and all owned allocations.

## State And Persistence
Parser state is fully in-memory and owned by the parser object. The regex is persistent across input strings. The input string is copied, and `_rstr` is an internal cursor into that copy. Returned matches are newly allocated and must be freed by the caller.

## Dependencies And Integration Points
Dependencies include POSIX `<regex.h>`, Gluster memory wrappers, common validation/allocation macros, and logging message IDs. Callers use this as a low-level helper where repeated regex matching is needed without exposing POSIX regex details.

## Risks
`parser_set_string()` does not free an existing `complete_str` before replacing it, so repeated set calls without `parser_unset_string()` leak. `parser_get_next_match()` can infinite-loop on regexes that match zero-length strings because `_rstr` advances by `rm_eo`, which may be zero. The parser is stateful and not thread-safe. `parser_init()` does not validate NULL `regex` before `gf_strdup()` and `regcomp()` paths rely on allocation failure handling. Callers must free returned match strings.

## Test Signals
Tests should cover regex compile failure, basic repeated matching, no-match return, parser reset/unset/deinit, repeated `parser_set_string()` leak behavior under sanitizers, zero-length regex handling, NULL argument validation, and caller ownership of returned strings.
