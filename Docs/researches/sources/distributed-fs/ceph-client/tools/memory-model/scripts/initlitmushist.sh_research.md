# sources/distributed-fs/ceph-client/tools/memory-model/scripts/initlitmushist.sh

Purpose: Initializes a litmus history run by obtaining the external litmus-test corpus if needed, selecting C-language litmus tests up to a process-count threshold, and running herd7 on the selected set without judging results.

Important APIs and functions: The script sources `scripts/parseargs.sh` for `LKMM_DESTDIR`, `LKMM_PROCS`, jobs, timeout, hardware options, and herd options. It uses `mselect7 -arch C` to select C tests and `scripts/runlitmushist.sh` to execute them.

Control flow: After argument parsing it creates a temporary directory, ensures a `litmus` checkout exists by cloning `https://github.com/paulmckrcu/litmus` if absent, mirrors new litmus directories into `LKMM_DESTDIR` when a separate destination is used, creates a list of C tests, filters out tests containing process `P${LKMM_PROCS}` or above, then pipes that list into the parallel runner.

State and persistence behavior: It can persist a cloned `litmus` repository and `.litmus.out` result files under `LKMM_DESTDIR`. Temporary lists are deleted by trap.

Dependencies and integration points: Requires git, herdtools commands (`mselect7`, later herd7 through `runlitmushist.sh`), and the local LKMM scripts. It is the baseline-producing counterpart to `newlitmushist.sh`.

Risks: The clone path is unauthenticated network state and checkout is `origin/master`, so results depend on current upstream content. Process-count filtering via `grep -L "^P${LKMM_PROCS}"` is a convention rather than a parser. Runs can be CPU-expensive and timeout-heavy.

Test signals: Run with a small `--procs` value and temporary `--destdir`; verify directory mirroring, list construction, runner invocation, and no judged `!!!` output is required.
