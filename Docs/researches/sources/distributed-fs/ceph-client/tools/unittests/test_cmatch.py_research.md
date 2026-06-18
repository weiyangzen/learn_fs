# sources/distributed-fs/ceph-client/tools/unittests/test_cmatch.py

## Purpose

`test_cmatch.py` tests `kdoc.c_lex.CMatch`, especially matching and rewriting C-like macro invocations with nested parentheses and kernel-doc transform patterns.

## Important APIs, Types, and Functions

Test classes include `TestSearch`, `TestSubMultipleMacros`, `TestSubSimple`, and `TestSubWithLocalXforms`. Helpers include `TestCaseDiff.assertLogicallyEqual()` and `apply_transforms()`, which mimics selected `kdoc_parser` transform passes. It imports `CMatch`, `KernRe`, and `run_unittest`.

## Control Flow and Data Flow

Search tests call `CMatch(...).search()` on sample lines. Substitution tests call `.sub()` with replacement strings containing backreferences like `\0`, `\1`, and greedy `+` suffixes. Transform tests apply ordered CMatch rules for structs, functions, and variables to realistic kernel snippets.

## State and Persistence Behavior

The tests are pure in-memory transformations. No files are written.

## Dependencies and Integration Points

The suite protects the parser transform layer used by kernel-doc. It covers annotations such as `__acquires`, `__guarded_by`, `struct_group*`, bitmap declarations, KFIFO macros, flex arrays, DMA unmap macros, and list heads.

## Risks and Edge Cases

The test file includes duplicate `TestCaseDiff` class definitions and duplicate `test_struct_kcov` names, so Python's later definitions shadow earlier ones. Some comments document known limitations around `struct_group_tagged` with extra commas. Whitespace normalization can mask formatting-only differences but improves semantic matching.

## Test Signals

Passing tests indicate nested macro matching, backreference substitution, count limiting, invalid greedy replacements, and kernel transform examples are stable.
