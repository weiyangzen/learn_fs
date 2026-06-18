<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/fio.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/fio.rs

Purpose: Builder-based wrapper for running fio workloads from Rust tests and mapping fio JSON output back to per-job results.

Important APIs/types: `FioJobResult` tracks not-run/ok/error errno. `FioJob` is a serializable builder with job name, ioengine, filename, rw, direct, block size, offset, iodepth, runtime, size, verification, and randomization options. `FioJob::as_fio_args()` serializes non-null fields into CLI args, converting booleans to 1/0 and adding `--time_based=1` when runtime is set. `Fio` groups jobs and execution options; `Fio::run()` builds `sudo LD_PRELOAD=$FIO_SPDK $FIO --output-format=json ...`, runs it with `run_script`, records duration/exit/stderr, and parses job errors. `spawn_fio_task()` runs fio on a blocking Tokio task and converts nonzero exit to `io::Error`.

State and dependencies: depends on environment variables `FIO` and `FIO_SPDK`, sudo, fio JSON format, and `derive_builder`.

Risks and test signals: command is assembled as a shell string, so filenames are sensitive to quoting; NVMf filenames are explicitly quoted elsewhere. `update_result` filters `fio: ` lines before JSON parsing. Healthy tests inspect `exit`, `err_messages`, and each job result.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/fio.rs -->
