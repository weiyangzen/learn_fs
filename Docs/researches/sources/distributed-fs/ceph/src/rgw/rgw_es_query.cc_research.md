# sources/distributed-fs/ceph/src/rgw/rgw_es_query.cc

## Purpose
Implements RGW's small Elasticsearch query compiler. It tokenizes a restricted infix expression language, converts infix to prefix, builds a query-node tree, and emits Elasticsearch JSON through Ceph's `Formatter`/`encode_json` APIs.

## Important APIs, Types, And Functions
Core helpers include `operator_map`, `is_operator()`, `operand_value()`, `check_precedence()`, and `infix_to_prefix()`. Query tree classes are local to the implementation: `ESQueryNode`, `ESQueryNode_Bool`, typed leaf value adapters for string/int/date, comparison nodes for equality, inequality, and ranges, plus nested custom-field wrappers. `ESInfixQueryParser::*` parses tokens. `ESQueryCompiler::compile()`, `convert()`, and `dump()` are the externally relevant implementation points.

## Control Flow
`compile()` parses the source query into infix tokens, converts to prefix, recursively allocates the node tree with `alloc_node()`, then prepends any forced equality predicates by wrapping the existing root in `and` boolean nodes. `dump()` serializes the root as a `query` object. Boolean nodes emit `bool.must` or `bool.should`; equality emits `term`; inequality emits `bool.must_not.term`; range emits `range` with `lt/lte/gte/gt`.

## State And Persistence Behavior
The compiler owns an in-memory tree rooted at `query_root`; there is no persistence. Type interpretation is driven by caller-provided generic/custom `ESEntityTypeMap`s, field aliases, restricted-field sets, and a custom-field prefix. Custom fields are transformed into nested `meta.custom-{type}` queries.

## Dependencies And Integration Points
Uses Ceph JSON formatting, `strict_strtoll()`, `parse_time()`, `rgw_to_iso8601()`, and Boost string prefix matching. It integrates with RGW metadata search callers that provide field maps and then pass the compiled JSON to Elasticsearch.

## Risks
The parser is intentionally narrow: values cannot contain spaces or `)`, `and`/`or` matching is not word-boundary checked, and parse failures collapse into broad errors. The infix-to-prefix algorithm mutates the source token list by appending `)`. Unknown generic fields are rejected, while unknown custom fields silently become strings. Node ownership depends on careful handoff when nested nodes wrap existing operator nodes.

## Test Signals
Useful tests include precedence/parentheses cases, invalid operators, malformed expressions, int/date parse failures, restricted generic fields, alias expansion, custom nested string/int/date fields, and prepended equality predicates.
