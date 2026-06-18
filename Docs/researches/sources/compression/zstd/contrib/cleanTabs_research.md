# sources/compression/zstd/contrib/cleanTabs

Purpose: small maintenance script to replace tab characters with four spaces across selected zstd source and contrib files.

Important behavior: runs a single `sed -i ''` substitution over globbed headers/C files in `lib`, `programs`, `tests`, contrib headers/C++ files, examples, and zlibWrapper. The `$'...'` shell quoting is used to express a literal tab.

State, dependencies, and integration: it mutates source files in place and depends on shell glob expansion plus a BSD/macOS-style `sed -i ''` interface. The top-level `Makefile` exposes it through the `cleanTabs` target by running inside `contrib`.

Risks and test signals: this script is destructive formatting maintenance, not a test. It may fail on GNU sed unless compatible handling is available, and glob patterns may miss nested files or expand differently by shell. Review diffs after running it.
