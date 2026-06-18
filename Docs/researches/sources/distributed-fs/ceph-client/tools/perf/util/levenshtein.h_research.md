<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/levenshtein.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/levenshtein.h

## Purpose

`levenshtein.h` declares perf's weighted Damerau-Levenshtein distance helper.

## Important APIs, Types, and Functions

It declares `levenshtein()` with parameters for the two strings and swap, substitution, insertion, and deletion penalties. The parameter name `substition_penalty` contains a spelling mistake but is ABI-neutral in C declarations.

## Control Flow

The header has no control flow; callers invoke the implementation in `levenshtein.c`.

## State and Persistence Behavior

No state is defined.

## Dependencies and Integration Points

The header has only include guards and can be used by suggestion/fuzzy-match utilities.

## Risks and Edge Cases

Callers must pass valid NUL-terminated strings and nonnegative weights. The spelling typo should not be changed casually if external references depend on the name in documentation.

## Test Signals

Compile tests should include the header from C files, and functional tests should validate the implementation's distance values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/levenshtein.h -->
