## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_perf_data_converter_ctf.sh

Purpose: tests `perf data convert --to-ctf` for file and pipe-recorded perf.data.
Important functions: `check_babeltrace_support`, `test_ctf_converter_file`, and `test_ctf_converter_pipe`.
Control flow: skips if perf lacks libbabeltrace, records `noploop`, converts to a temp CTF directory with `--force`, and verifies the directory is non-empty; repeats after recording to stdout redirected to a file.
State and persistence: temp perf.data and CTF directory are removed.
Dependencies and integration: libbabeltrace support, perf data converter, and `noploop` workload.
Risks: only checks output existence, not CTF schema validity; pipe path still converts from a saved file, not direct stdin.
Test signals: non-empty CTF output directory for both modes.
