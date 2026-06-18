# File Research: sources/block-storage/lvm2/libdm/regex/matcher.c

Purpose: implements libdevmapper's regex matcher by compiling one or more parsed regex patterns into a lazy DFA and returning the index of the best matching pattern.

Read coverage: complete file read, 576 lines.

Key responsibilities:
- Defines `struct dm_regex`, DFA state storage, charset/node tables, scratch bitsets, character maps, and a ternary-tree lookup cache for DFA-state identity.
- Combines all input patterns into one alternation, wrapping each as `(.*(<pattern>)<TARGET_TRANS>)` so matches can report which original pattern accepted.
- Counts and enumerates regex tree nodes and charset leaves, then allocates `firstpos`, `lastpos`, and `followpos` bitsets for direct DFA construction.
- Computes nullable/firstpos/lastpos/followpos functions for CAT, OR, STAR, PLUS, QUEST, and CHARSET nodes.
- Builds DFA states on demand during matching, caching state transitions in `lookup[256]` and interning bitset keys in `ttree`.
- Handles artificial start/end matching via `HAT_CHAR` and `DOLLAR_CHAR`, and forces `TARGET_TRANS` transitions to discover accepting pattern numbers.
- Provides `dm_regex_fingerprint()` test/debug support by forcing all lazy states and hashing reachable DFA transitions.

Important entry points:
- `dm_regex_create(struct dm_pool *mem, const char * const *patterns, unsigned num_patterns)`
- `dm_regex_match(struct dm_regex *regex, const char *s)`
- `dm_regex_fingerprint(struct dm_regex *regex)`

Dependencies:
- Uses `parse_rx.h` for regex tree structure and sentinel characters.
- Uses `ttree.h` to intern DFA states by bitset key.
- Uses libdm pools, bitsets, logging, and allocation helpers from `libdm/misc/dmlib.h`.

Risk and edge cases:
- Matching mutates the compiled object by creating lazy states and filling transition tables, so a single `dm_regex` is not naturally immutable during first use.
- Pattern ordering matters: final numbers are assigned as target-transition charset leaves are encountered and `dm_regex_match()` returns `r - 1`.
- The generated combined regex depends on `snprintf()` into a pre-sized pool buffer; malformed user regexes fail during parsing.
- DFA state memory lives in the caller-supplied pool, while scratch structures also use that pool in this implementation, so freeing the pool invalidates the matcher.
- `dm_regex_match()` returns `-1` when no pattern matches.
- Fingerprinting is explicitly inefficient test code and forces all possible DFA transitions up front.
