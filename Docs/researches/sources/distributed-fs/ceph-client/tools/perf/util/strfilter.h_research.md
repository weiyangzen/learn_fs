# sources/distributed-fs/ceph-client/tools/perf/util/strfilter.h

## Purpose

`strfilter.h` defines the AST structures and public API for glob-based boolean string filters.

## Important APIs, Types, and Functions

`struct strfilter_node` stores left/right children and an operator or rule string. `struct strfilter` stores the root. Declared functions create, append OR/AND rules, compare strings, delete filters, and reconstruct rule strings.

## Control Flow and Data Flow

Callers parse a rule string into a filter, evaluate candidate strings with `strfilter__compare()`, optionally append more rules, and delete the filter.

## State and Persistence Behavior

The filter owns its parsed tree. Error reporting from creation/append returns a pointer into the input rule or NULL on allocation failure.

## Dependencies and Integration Points

The header depends on Linux list inclusion and bool support. It is implemented by `strfilter.c` and uses glob behavior from `string.c`.

## Risks and Edge Cases

Callers must handle NULL filters and distinguish syntax from allocation failures through the error pointer. The AST is mutable when appending rules.

## Test Signals

Parser/evaluator unit tests with valid and invalid expressions are the main validation signal.
