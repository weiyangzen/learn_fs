<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/levenshtein.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/levenshtein.c

## Purpose

`levenshtein.c` implements weighted Damerau-Levenshtein string distance for perf suggestion and fuzzy matching code.

## Important APIs, Types, and Functions

The sole API is `levenshtein(const char *string1, const char *string2, int w, int s, int a, int d)`, where weights are swap, substitution, insertion/addition, and deletion penalties.

## Control Flow

The function allocates three rows sized to `strlen(string2) + 1`, initializes insertion costs, then iterates over characters of `string1` and `string2`. For each cell it computes minimum cost among substitution, adjacent swap, deletion, and insertion. Rows rotate after each source character, and the result is the last row's final column.

## State and Persistence Behavior

All state is temporary heap memory. No persistent data is written.

## Dependencies and Integration Points

It depends on libc allocation/string functions and is declared by `levenshtein.h`. It is suitable for command/event-name suggestions.

## Risks and Edge Cases

The code does not check malloc failures before writing rows, so OOM can crash. The algorithm note says it calculates a true distance only when deletion and insertion weights are equal. Lengths are stored in `int`, so extremely long strings can overflow. It treats bytes, not Unicode characters.

## Test Signals

Tests should cover equal strings, insertion/deletion/substitution/swap, weighted penalties, empty strings, asymmetric add/delete penalties, long strings, and injected allocation-failure behavior if possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/levenshtein.c -->
