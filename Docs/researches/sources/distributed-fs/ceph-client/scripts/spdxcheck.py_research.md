# sources/distributed-fs/ceph-client/scripts/spdxcheck.py

Purpose: `spdxcheck.py` validates SPDX license identifier expressions in source files against the in-tree `LICENSES` metadata and can report directory/file coverage.

Important APIs, types, and functions: `SPDXdata` stores license and exception sets. `read_spdxdata()` walks `LICENSES/preferred`, `dual`, `deprecated`, and `exceptions` from the Git tree and validates exception license lists. `id_parser` uses PLY lex/yacc to parse license expressions with `AND`, `OR`, `WITH`, and parentheses, validating license IDs and exception applicability. `pattern` implements exclude-file matching, while `scan_git_tree()`, `scan_git_subtree()`, and `read_exclude_file()` drive repository traversal.

Control flow: command-line parsing supports paths, stdin, directory statistics, depth, excludes, missing-file output, max scan lines, and verbose stats. It initializes a GitPython repo, loads SPDX metadata, reads exclude rules, then parses stdin, specified files/directories, or the full Git tree. Per file, `parse_lines()` scans up to `maxlines` for `SPDX-License-Identifier:`, strips comment closures for C/XML/Jinja/list forms, parses the expression, and updates coverage counters.

State and persistence: no file writes. Runtime state includes parser counters and per-directory missing-file summaries.

Dependencies and integration points: depends on Python 3, GitPython, PLY, locale decoding, and the kernel `LICENSES` tree. Used by licensing checks and developer validation.

Risks: only the first matching SPDX line is parsed. File existence checks use `os.path.isfile(el.path)` against Git tree paths, so invocation must occur from a compatible worktree. Parser precedence treats `AND` and `OR` at the same non-associative level, matching the script's grammar expectations but requiring tests for complex expressions.

Test signals: `spdxcheck-test.sh`, known valid/invalid expressions, exception-license mismatch cases, stdin binary input, exclude rules, and verbose directory reports.
