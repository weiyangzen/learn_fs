# sources/distributed-fs/ceph-client/tools/perf/tests/expr.c

## Purpose
Validates perf's expression parser, ID discovery, topology constants, CPUID string matching, and ID-set union behavior used by metric expression evaluation.

## Important APIs, Types, and Functions
- `test_ids_union()` exercises `ids__new()`, `ids__insert()`, `ids__union()`, `ids__free()`, and `hashmap__size()` across empty, duplicate, and overlapping ID sets.
- `test(struct expr_parse_ctx *ctx, const char *e, double val2)` wraps `expr__parse()` and exact-value assertions for arithmetic and logical expressions.
- `test__expr()` builds an `expr_parse_ctx`, adds `FOO` and `BAR`, runs parse/evaluation checks, clears/reuses the context for `expr__find_ids()`, queries topology constants, tests CPUID matching via `strcmp_cpuid_str()`, and verifies `has_event()`.
- Key types include `struct expr_parse_ctx`, `struct expr_id_data`, `struct hashmap`, `struct perf_cpu`, and topology helpers from `cputopo`, `header`, and `smt`.

## Control Flow
The suite starts by obtaining a CPUID string, runs ID union checks, then evaluates arithmetic, modulo, unary minus, bitwise-style logical operators, `min`, `max`, nested ternaries, floating literals, ratios, and comparisons. It separately checks division by zero returns a parsed NaN while malformed syntax fails. It then repeatedly clears the context and tests ID extraction, including escaped event parameters using `ctx->sctx.runtime`, escaped dashes, conditional expressions involving `#smt_on` and `#core_wide`, and short-circuit cases that should not collect unused IDs. Finally it parses topology constants, validates ordering relationships, handles `#system_tsc_freq` architecture behavior, checks `source_count(EVENT1)`, escapes the real CPUID string for parser syntax, and tests `has_event(cycles)`.

## State and Persistence
All state is process-local. The expression context is allocated, mutated with IDs and scalar values, cleared several times, and freed. CPUID strings are dynamically allocated and transformed with `strreplace_chars()`. No persistent files are created.

## Dependencies and Integration Points
This file exercises `util/expr` and its support code, including hash maps, topology queries, SMT/core-wide helpers, CPUID environment override behavior, and test-suite registration through `DEFINE_SUITE("Simple expression parser", expr)`.

## Risks and Edge Cases
- Floating comparisons use exact equality for expected decimal results such as `3.2`; this relies on the parser and compiler producing stable double representations for these simple cases.
- `#system_tsc_freq` behavior is architecture-specific and Intel-specific; the test tolerates zero on non-Intel but asserts support on x86 if parsing fails.
- Short-circuit ID discovery is heavily semantically coupled to expression optimizer behavior.
- Global system topology affects some expected branches, though the assertions are framed as ordering constraints rather than fixed counts.

## Test Signals
Pass signals include correct numeric parser behavior, correct ID extraction and short-circuiting, valid topology constants, CPUID comparison support for escaped strings, and event-presence helper behavior. Failures are emitted through `TEST_ASSERT_VAL`/`TEST_ASSERT_EQUAL`.
