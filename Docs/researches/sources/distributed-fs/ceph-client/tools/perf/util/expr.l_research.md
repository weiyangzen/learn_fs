# sources/distributed-fs/ceph-client/tools/perf/util/expr.l

## Purpose

`expr.l` is the flex scanner for perf metric expressions. It tokenizes numbers, event IDs, literals, keywords, operators, and punctuation for the bison parser.

## Important APIs, Types, and Functions

The scanner uses prefix `expr_`, reentrant mode, and bison bridge mode. Helpers include `value` for numeric conversion, `literal` for `#...` tool PMU literals, `nan_value`, `normalize`, and `str`. Tokens include `D_RATIO`, `MAX`, `MIN`, `IF`, `ELSE`, `SOURCE_COUNT`, `HAS_EVENT`, `STRCMP_CPUID_STR`, `NUMBER`, `ID`, `LITERAL`, and operator characters.

## Control Flow

For each token, the scanner writes semantic data to `YYSTYPE`: doubles for numbers/literals and normalized duplicated strings for IDs. `normalize` handles backslash escaping and replaces `?` with the runtime integer from `expr_scanner_ctx`. The ID pattern permits `@` so PMU event names can use `@` as a division-safe stand-in for `/`. Unknown characters are ignored by the `.` rule.

## State and Persistence Behavior

The scanner uses `expr_scanner_ctx` as extra state. ID strings are allocated and later freed by parser destructors or semantic handlers. Literal evaluation may read live tool PMU data unless test mode converts unrecognized literals to `1`.

## Dependencies and Integration Points

It includes `expr.h`, generated bison headers, Linux compiler annotations, errno, and math support. It is generated into `expr-flex` and called by `expr.c`.

## Risks and Edge Cases

`normalize` mutates strings in place; callers must pass owned storage. The number regex supports lowercase `e-` exponents but not `E` or explicit `e+`. The catch-all ignore rule can hide unexpected characters until the parser fails or produces surprising tokens. Literal failures are fatal outside test mode.

## Test Signals

Lexer tests should cover escaped symbols, `?` runtime substitution, PMU `@` names, keywords versus IDs, NaN, literals in normal/test mode, malformed numbers, and ignored punctuation.
