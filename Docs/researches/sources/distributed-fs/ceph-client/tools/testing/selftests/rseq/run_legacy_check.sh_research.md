# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/run_legacy_check.sh

Purpose: `run_legacy_check.sh` is a small wrapper that runs the `legacy_check` binary with glibc rseq auto-registration disabled.

Important APIs, types, and functions: it sets `GLIBC_TUNABLES="${GLIBC_TUNABLES:-}:glibc.pthread.rseq=0"` for the command invocation and executes `./legacy_check`.

Control flow: straight-line shell execution. The script's exit status is the binary's exit status.

State and persistence: it mutates only the environment for the child process; no files are written.

Dependencies and integration points: depends on the built `legacy_check` executable and glibc honoring the `glibc.pthread.rseq=0` tunable. It is part of the kselftest generated runner set for rseq.

Risks and test signals: if glibc ignores the tunable or the shell does not preserve intended environment syntax, the test may check the wrong ownership path. A zero exit from `legacy_check` is the signal.
