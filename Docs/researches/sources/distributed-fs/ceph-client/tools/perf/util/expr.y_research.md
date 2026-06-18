# sources/distributed-fs/ceph-client/tools/perf/util/expr.y

## Purpose

`expr.y` is the bison grammar and evaluator for perf metric expressions. It supports arithmetic, comparisons, boolean-like operators, ternary-style `if/else`, min/max, denominator-safe ratio, source-count queries, event existence checks, CPUID string checks, literals, and ID collection.

## Important APIs, Types, and Functions

The parser receives `double *final_val`, `struct expr_parse_ctx *ctx`, `bool compute_ids`, and the scanner. Semantic values include numbers, strings, and an `{ids, val}` pair. Helpers include `expr_error`, `is_const`, `union_expr`, `handle_id`, and the `BINARY_OP` macro. `BOTTOM` is represented by `NAN` during ID discovery to mean a value depends on runtime event data.

## Control Flow

In evaluation mode, IDs resolve to numeric values through `expr__resolve_id`; constants compute directly; missing values propagate `NAN`. In ID-discovery mode, constants are folded and non-constant branches union required ID sets. Conditional expressions can avoid collecting unused branches when the condition is constant, while non-constant conditions union condition and both branch IDs as needed. Division by zero yields `NAN`; `d_ratio` returns `0` for constant-zero denominators.

## State and Persistence Behavior

Parser reductions own and free ID strings and temporary ID hashmaps through bison destructors and explicit `ids__free` calls. At the `start` rule, discovered IDs are unioned into `ctx->ids`, transferring ownership. No persistent parser state remains after parsing.

## Dependencies and Integration Points

It depends on `expr.h`, generated scanner hooks, debug logging, math classification, and ID-map helpers. Metric-group code relies on the grammar both to compute values and to know which perf events must be scheduled.

## Risks and Edge Cases

Using `NAN` as both invalid value and bottom marker makes mode-specific logic delicate. Boolean operators intentionally fold constants and may not behave like C bitwise operators for nonzero doubles. Modulo casts operands to `long`. Division and modulo by zero differ: division returns `NAN`, modulo aborts parsing. ID-discovery correctness depends on freeing unused branch ID sets.

## Test Signals

Golden parser tests should cover precedence, ternary branches, constant folding in compute-IDs mode, boolean operators, `d_ratio`, division/modulo zero, min/max, `source_count`, `has_event`, CPUID checks, literals, and memory-checker runs for parse failures.
