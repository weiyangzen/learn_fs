# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck-rcu.sh

Purpose: extracts rcutorture progress, grace-period rate, final GP state, forward-progress signal, and reader-batch close-call diagnostics.

Important APIs and functions: sources `functions.sh`, greps `console.log` for `ver:`, `End-test grace-period state`, `rcu_torture_fwd_prog`, and `torture: Reader Batch`; computes rates with awk and emits bug/warning via `print_bug`/`print_warning`.

Control flow: validate dir, collect latest counters, print summary, then if reader batch close calls are present, compute normalized rate and create `console.log.rcu.diags` for nonzero close calls.

State and persistence: may write `console.log.rcu.diags`.

Dependencies and integration: suite-specific analyzer called by `kvm-recheck.sh` for rcu runs.

Risks and test signals: progress extraction is format-dependent. Close-call thresholding is heuristic and warns or bugs based on rate and count.
