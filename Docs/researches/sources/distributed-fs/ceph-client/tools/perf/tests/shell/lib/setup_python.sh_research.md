## sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/setup_python.sh

Purpose: small shared setup library that discovers a Python interpreter for shell tests that validate JSON, metrics, or perf scripting.
Important behavior: if `$PYTHON` is unset it first tries `python3 --version`, then `python --version`; if neither exists it prints a skip message and exits `2`.
Control flow: sourced scripts inherit a populated `PYTHON` variable or terminate immediately with the perf test skip code.
State and persistence: only shell variable state is changed; no files are created.
Dependencies and integration: used by `list.sh`, `python-use.sh`, `script_dlfilter.sh`, JSON/stat metric tests, and data converter tests.
Risks: exits the caller when sourced, so callers must source it only after they are ready to skip; does not validate Python module availability beyond the interpreter command.
Test signals: downstream tests run `$PYTHON` successfully or are skipped with code `2`.
