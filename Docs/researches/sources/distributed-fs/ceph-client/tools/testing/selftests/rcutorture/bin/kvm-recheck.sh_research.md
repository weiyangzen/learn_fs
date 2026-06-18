# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck.sh

Purpose: top-level result validator for rcutorture runs. It checks build artifacts, suite-specific progress, config conformance, oldconfig errors, build diagnostics, console diagnostics, KCSAN summaries, and aggregate failure counts.

Important APIs and functions: finds scenario dirs by `Make.defconfig.out`, sources `functions.sh`, dispatches to `kvm-recheck-$TORTURE_SUITE.sh`, calls `configcheck.sh`, `parse-build.sh`, `parse-console.sh`, `kvm-find-errors.sh`, and uses `print_bug`.

Control flow: for each supplied result tree, iterate scenario dirs, read suite name, remove stale diags, run suite-specific analysis, handle qemu retval and console cases, validate configs, parse logs, then summarize KCSAN. After all dirs, run `EDITOR=echo kvm-find-errors.sh` on the last result and infer return code from diagnostic file counts.

State and persistence: creates/removes `.diags` files and may leave parse outputs such as `Warnings`.

Dependencies and integration: final validation path for `kvm-end-run-stats.sh`.

Risks and test signals: variable `ret` may remain unset on full success, which shells treat as exit 0. It evaluates only the last argument in final `kvm-find-errors.sh` call.
