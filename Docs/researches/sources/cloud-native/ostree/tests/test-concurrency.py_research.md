# sources/cloud-native/ostree/tests/test-concurrency.py

Purpose: Python stress test for concurrent commits and prunes against the same repository.

Important APIs/functions: `subprocess.Popen`, helper `mktree()`, `commit(v)`, `prune()`, `wait_check(proc)`, and `run(n_committers, n_pruners)`. It shells out to `ostree --repo=repo init`, `commit --fsync=0`, and `prune`.

Control flow: creates several small trees, starts an even number of committers against repeated trees and a configurable number of pruners, waits for processes, prints diagnostics, and fails if any child exits unsuccessfully.

State/persistence: creates `repo` and temporary tree directories named by serial. Dependencies include Python 3 and the `ostree` CLI on `PATH`.

Integration/risk/test signals: catches repository lock/transaction races under simultaneous write and prune workloads. Risks are timing sensitivity and limited corruption checks beyond child exit status. Failure prints process output and exits nonzero.
