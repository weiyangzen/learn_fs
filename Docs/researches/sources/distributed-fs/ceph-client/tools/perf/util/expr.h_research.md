# sources/distributed-fs/ceph-client/tools/perf/util/expr.h

## Purpose

`expr.h` declares the public context and API for perf metric expression evaluation and ID discovery.

## Important APIs, Types, and Functions

`struct expr_scanner_ctx` carries scanner/runtime options: requested CPU list, runtime integer substitution, system-wide mode, and test mode. `struct expr_parse_ctx` contains the ID hashmap and scanner context. The header declares ID-map lifecycle, context lifecycle, ID insertion/deletion/value/reference APIs, subset checks, ID resolution, parsing, ID discovery, value/source-count accessors, literal evaluation, event-existence checks, and CPUID string comparisons.

## Control Flow

Metric callers create a context, add values or references, call `expr__find_ids` to discover needed events or `expr__parse` to compute a value, then clear or free the context. Scanner context fields must be set before parsing when expressions use runtime literals, system-wide tool PMUs, or test behavior.

## State and Persistence Behavior

The context owns its hashmap and `user_requested_cpu_list`. ID data is opaque to callers except through accessor functions. `ids__union` consumes and frees its input maps while returning the merged result, a notable ownership contract.

## Dependencies and Integration Points

It forward-declares `struct hashmap` and `struct metric_ref` to keep dependencies light. Implementations integrate with generated lexer/parser code and perf metric/event parsing.

## Risks and Edge Cases

Callers must not inspect opaque `expr_id_data` directly. Passing maps to `ids__union` transfers ownership. Context clear/free must match any inserted IDs or references to avoid leaks.

## Test Signals

Compile coverage for metric code, ownership tests around `ids__union`, context lifecycle tests, and parser golden tests for expressions using scanner context are useful.
