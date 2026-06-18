# File Research: sources/block-storage/lvm2/libdm/regex/parse_rx.c

Purpose: parses libdm's small regex dialect into `rx_node` trees and performs a tree rewrite optimization that hoists common OR prefixes or suffixes.

Read coverage: complete file read, 683 lines.

Key responsibilities:
- Tokenizes regex input with support for character classes, negated classes, ranges, escapes, grouping, alternation, closures, `.` wildcard, `^`, and `$`.
- Represents literal tokens as 256-bit charset nodes and maps `^`/`$` to internal non-printable sentinels from `parse_rx.h`.
- Parses with recursive descent: term, closure term, concatenation, and OR expression.
- Allocates all parser state, charset bitsets, and nodes from a `dm_pool`.
- Implements optional DEBUG regex printing for inspecting generated trees.
- Optimizes alternations by finding common leftmost or rightmost CAT branches and converting forms like `(fa)|(fb)` into `f(a|b)`.
- Rotates nested OR nodes to expose common factors before exchange.
- Avoids considering charsets containing `TARGET_TRANS` as equal, preserving matcher-inserted pattern boundary markers.

Important entry points:
- `rx_parse_tok(struct dm_pool *mem, const char *begin, const char *end)`
- `rx_parse_str(struct dm_pool *mem, const char *str)`

Grammar and behavior:
- Closure operators `*`, `+`, and `?` apply repeatedly to the preceding term.
- Concatenation is implicit and right-recursive.
- Alternation is also parsed recursively with `|`.
- Character classes support escaped `n`, `r`, `t`, arbitrary escaped characters, and reversed ranges by swapping endpoints.
- `.` matches all nonzero bytes except newline and carriage return.

Dependencies:
- Includes `parse_rx.h`, which brings in libdm bitset/pool/logging helpers.
- Uses libdm allocation and bitset operations throughout.

Risk and edge cases:
- The parser is purpose-built, not a full POSIX/PCRE engine; unsupported regex syntax is either treated literally or rejected depending on token shape.
- Unterminated classes, incomplete ranges, trailing escapes, missing right parentheses, and malformed OR expressions return parse failure with log messages.
- Recursive parse and optimization passes can be deep for pathological regexes.
- The optimizer rewrites nodes in place using `memcpy()` over existing nodes, so tree ownership is pool-based and assumes no external node aliases.
- Comments note possible inefficiency and a FIXME about avoiding left/right OR rotation bouncing.
