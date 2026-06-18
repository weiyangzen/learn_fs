<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/macro_checker.py -->
# sources/distributed-fs/ceph-client/scripts/macro_checker.py

## Purpose

`macro_checker.py` scans C and header files for function-like macros whose formal parameters are not referenced in the replacement text. It is a lightweight style/bug finder meant to catch stale macro arguments while avoiding common false positives.

## Important APIs, Types, and Functions

The script exposes command-line arguments `path` and `--verbose`. `check_macro()` parses one full macro definition, compares arguments to the macro body, prints diagnostics, and records names with at least one observed correct definition. `macro_strip()` removes simple comment/whitespace forms. `file_check_macro()` handles `.c` and `.h` files, including backslash continuations and conditional-compilation depth. `dir_check_macro()` recurses into directories.

## Control Flow

`main()` decides whether the target is a file or directory. Each file is first scanned in report-suppressed mode to populate `correct_macros`, then scanned in reporting mode. Non-verbose mode skips `.c` macros inside any conditional block and `.h` macros outside the usual outer include-guard depth. Verbose mode checks conditional macros too.

## State and Persistence Behavior

The only retained state is the process-global `correct_macros` list and parsed `args`. The script writes diagnostics to stdout and does not modify source files.

## Dependencies and Integration Points

It depends only on Python standard modules `argparse`, `os`, and `re`. It integrates as a developer/CI lint helper rather than a Kbuild build product.

## Risks and Edge Cases

Parsing is regex-based and does not fully understand C preprocessing, nested parentheses, stringification, token pasting, comments, or identifiers appearing inside strings. Substring matching can mistake `a` as used inside another token. Directory order affects `correct_macros`, and the error message has a typo for nonexistent paths.

## Test Signals

Tests should include single-line and multiline macros, variadic macros, empty `do {} while (0)`/`0`/`1` macros, include guards, conditional definitions, duplicate macro names with correct and incorrect variants, and macro arguments that appear only as token substrings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/macro_checker.py -->
