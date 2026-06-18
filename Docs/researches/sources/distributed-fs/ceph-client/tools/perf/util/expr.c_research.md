# sources/distributed-fs/ceph-client/tools/perf/util/expr.c

## Purpose

`expr.c` backs perf metric expression parsing. It manages expression contexts, event ID maps, metric references, formula evaluation, ID discovery, literal reads, event-existence checks, and CPUID string comparisons.

## Important APIs, Types, and Functions

The hidden `struct expr_id_data` represents either a numeric event value, a referenced metric expression, or a resolved referenced metric value. Public APIs include `expr__ctx_new`, `expr__ctx_clear`, `expr__ctx_free`, `expr__add_id`, `expr__add_id_val`, `expr__add_id_val_source_count`, `expr__add_ref`, `expr__get_id`, `expr__resolve_id`, `expr__parse`, `expr__find_ids`, `expr__get_literal`, `expr__has_event`, and `expr__strcmp_cpuid_str`. Hashmap helpers implement string-keyed ID maps.

## Control Flow

Contexts hold an ID hashmap and scanner options. Evaluation calls `__expr__parse`, initializes the flex scanner with `ctx->sctx`, scans the expression string, invokes the bison parser in compute or evaluate mode, then destroys scanner buffers. ID resolution finds value entries directly or recursively parses referenced metric expressions, marking references as `REF_VALUE` to cache results. ID discovery parses with `compute_ids=true` and optionally removes one excluded ID.

## State and Persistence Behavior

Expression state is per `expr_parse_ctx`. The hashmap owns duplicated keys and allocated `expr_id_data` values. Metric references borrow `metric_ref` strings from PMU event metadata but store a duplicated hashmap key. Numeric duplicate inserts accumulate values and source counts. Scanner context stores runtime substitution, test mode, system-wide mode, and requested CPU list.

## Dependencies and Integration Points

It integrates with generated `expr-bison` and `expr-flex`, perf metric groups, evlist parsing, tool PMU events/literals, SMT/header helpers, PMU parsing, CPUID helpers, debug logging, and the generic hashmap. Metric code uses it to determine required events and compute final derived metric values.

## Risks and Edge Cases

Recursive metric references can fail if a referenced expression is invalid or cycles back before a value is available. Duplicate value insertion accumulates, which is intentional for aggregation but risky if callers expected replacement. `expr__has_event` creates a temporary evlist and rewrites `@` to `/`; malformed encodings return false or NAN. Literal reads can fail depending on platform/tool PMU support. Memory ownership differs between value IDs and borrowed metric expressions.

## Test Signals

Tests should cover arithmetic, conditionals, ID discovery, duplicate aggregation and `source_count`, referenced metrics, literal tool PMU reads, `has_event`, CPUID comparisons, runtime `?` substitutions, missing IDs, invalid expressions, and context clear/free leak checks.
