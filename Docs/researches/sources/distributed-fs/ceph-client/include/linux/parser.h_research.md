# Research: sources/distributed-fs/ceph-client/include/linux/parser.h

Purpose: `parser.h` declares the generic simple option parser used primarily by filesystem mount/argument parsing.

Important APIs/types/functions: `struct match_token` maps integer tokens to pattern strings, `match_table_t` is an array of those mappings, `MAX_OPT_ARGS` limits captured substrings to three, and `substring_t` records a matched range. Functions include `match_token()`, numeric converters for signed, unsigned, u64, octal, and hex, `match_wildcard()`, `match_strlcpy()`, and `match_strdup()`.

Control flow and state: callers define a match table, pass an option string to `match_token()`, and receive a token plus substring captures for later conversion. State is transient in caller-provided strings and `substring_t` arrays; `match_strdup()` allocates a copy.

Dependencies and integration points: implemented by `lib/parser.c` and used by filesystem option parsers, module options, and other kernel components needing small pattern matching without a full parser.

Risks and test signals: risks include modifying input strings unexpectedly, failing to handle missing captures, overflow or invalid numeric conversion, and wildcard overmatch. Tests should cover table fall-through, malformed numbers, max argument count, substring copy bounds, allocation failure, and representative filesystem mount option strings.
