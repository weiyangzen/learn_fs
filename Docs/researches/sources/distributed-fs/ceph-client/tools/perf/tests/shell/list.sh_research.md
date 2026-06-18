## sources/distributed-fs/ceph-client/tools/perf/tests/shell/list.sh

Purpose: validates that `perf list -j` emits syntactically valid JSON.
Important functions: `cleanup`, `trap_cleanup`, and `test_list_json`.
Control flow: discovers Python, creates a temp JSON file, runs `perf list -j -o`, and validates it using `$PYTHON -m json.tool`.
State and persistence: creates and removes one temp file under `/tmp`; no perf state is changed.
Dependencies and integration: depends on `lib/setup_python.sh`, `perf list`, and Python's standard JSON module.
Risks: only validates JSON syntax, not schema or field semantics; exits through trap on failures under `set -e`.
Test signals: successful JSON parse prints success and exits `0`; missing Python exits `2`.
