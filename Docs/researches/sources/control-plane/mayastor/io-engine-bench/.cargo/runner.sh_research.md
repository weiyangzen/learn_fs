<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-bench/.cargo/runner.sh -->
# sources/control-plane/mayastor/io-engine-bench/.cargo/runner.sh

Purpose: Cargo runner for `io-engine-bench`, wrapping benchmark execution in the privileges needed by io-engine/SPDK and moving Criterion output between `target/criterion` and the repository-owned `io-engine-bench/results/criterion`.

Important flow: captures all runner args as `ARGS`, chooses `sudo -E` when not already root, restores existing git Criterion results into `target/criterion`, then executes the target via `capsh` with `cap_setpcap` plus ambient `cap_sys_admin`, `cap_ipc_lock`, `cap_sys_nice`, and `cap_sys_resource`. After execution it attempts to chown the criterion target back to `$USER` and moves it into the bench results folder.

State and dependencies: depends on `SRCDIR`, `USER`, `sudo`, `capsh`, and writable target/results directories. It mutates benchmark result directories with `mv`, so interrupted runs may leave output in the alternate location.

Integration points: used by Cargo target runner configuration for benchmarks requiring elevated capabilities.

Risks and test signals: command injection exposure is limited to Cargo-provided args but uses `-- -c "${ARGS}"`; quoting matters for unusual test args. `mv` overwrites behavior and sudo/chown failures can affect repeatability. Validate by running a benchmark and confirming Criterion history survives across runs.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-bench/.cargo/runner.sh -->
