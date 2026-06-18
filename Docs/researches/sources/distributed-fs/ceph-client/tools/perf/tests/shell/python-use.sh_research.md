## sources/distributed-fs/ceph-client/tools/perf/tests/shell/python-use.sh

Purpose: validates that Python can import perf's Python binding.
Important behavior: discovers Python, tries to locate `$(dirname $(which perf))/python`, conditionally prepends that path to `sys.path`, imports `perf`, and prints `success!`.
Control flow: builds a small inline Python program and pipes it to `$PYTHON`; grep for `success!` decides pass/fail.
State and persistence: no files; only a shell heredoc command string.
Dependencies and integration: depends on perf's Python extension installation layout or Python path.
Risks: `which perf` path may not match source-tree module location; import-only coverage does not exercise binding APIs.
Test signals: interpreter output containing `success!` yields exit `0`; import failure exits `1`; missing Python exits `2`.
