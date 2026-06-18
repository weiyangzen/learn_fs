## sources/distributed-fs/ceph-client/tools/perf/tests/shell/record+zstd_comp_decomp.sh

Purpose: validates compressed perf.data recording with zstd and equivalent reporting after decompression.
Important functions: `skip_if_no_z_record`, `collect_z_record`, `check_compressed_stats`, and `check_compressed_output`.
Control flow: checks `perf record -h` for compression support, records a high-frequency workload using `-z`, verifies compressed stats in report headers, injects/decompresses, and diffs report output between compressed and decompressed files.
State and persistence: uses temp perf.data plus `.decomp` and output files; cleanup uses a glob-like quoted path that may not expand as intended.
Dependencies and integration: requires zstd-enabled perf, `dd`, `/dev/urandom`, `perf inject`, and report stability.
Risks: report output comparison strips only the last three lines; header/stat format or sample nondeterminism may affect diffs.
Test signals: compressed event stats and zero diff between selected report fields.
