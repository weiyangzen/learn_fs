## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_perf_data_converter_json.sh

Purpose: tests `perf data convert --to-json` for file and stdin input and validates JSON syntax.
Important functions: `test_json_converter_command`, `test_json_converter_pipe`, and `validate_json_format`.
Control flow: records `noploop`, converts the perf.data to JSON, checks non-empty output, validates with Python `json.load`, then repeats by piping a saved perf.data file to converter with `-i -`.
State and persistence: temp perf.data and JSON result are cleaned.
Dependencies and integration: Python, perf data converter, perf record, and `noploop`.
Risks: syntax validation does not check event content; cleanup uses quoted wildcard for perfdata companions and may not remove `.old`.
Test signals: non-empty valid JSON after each conversion mode.
