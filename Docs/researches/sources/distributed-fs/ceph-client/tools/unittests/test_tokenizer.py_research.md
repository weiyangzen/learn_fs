# sources/distributed-fs/ceph-client/tools/unittests/test_tokenizer.py

## Purpose

`test_tokenizer.py` tests the C tokenizer used by kernel-doc, including token kinds, nesting-level accounting, unexpected-token logging, and removal of private struct sections.

## Important APIs, Types, and Functions

Helpers include `tokens_to_list()`, `make_tokenizer_test()`, `make_private_test()`, `setUp()`, and `build_test_class()`. Data tables `TESTS_TOKENIZER` and `TESTS_PRIVATE` define dynamically generated unittest classes. It imports `CToken`, `CTokenizer`, and `run_unittest`.

## Control Flow and Data Flow

For token tests, the file tokenizes source snippets, strips space tokens, and compares `(kind, value, level)` tuples. For private/public tests, it stringifies the tokenizer output and compares whitespace-normalized trimmed source. Dynamic class creation turns table entries into methods at import time.

## State and Persistence Behavior

Tests are pure in-memory operations. Unexpected-token tests use `assertLogs()` to verify logging output.

## Dependencies and Integration Points

It depends on `kdoc.c_lex` and Python unittest. It protects parser behavior for nested braces/parentheses/brackets, comments, illegal tokens, and kernel-doc `private:`/`public:` comment trimming used before item extraction.

## Risks and Edge Cases

Dynamic method names are derived from human-readable keys that include spaces, which works but is unusual. Whitespace normalization can hide formatting differences. Private-section tests cover balanced and unbalanced cases, including nested structs and `struct_group_tagged`.

## Test Signals

Passing tests indicate token classification, nesting levels, illegal-token logging, and private/public trimming behavior are stable.
