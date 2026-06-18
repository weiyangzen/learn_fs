# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kcsan-collapse.sh

Purpose: summarizes KCSAN reports across a result tree when a KCSAN run was requested.

Important APIs and functions: checks `TORTURE_KCONFIG_KCSAN_ARG`, finds all `console.log`, extracts `BUG: KCSAN:` lines, strips timestamps, counts unique reports, sorts by frequency, and writes `kcsan.sum`.

Control flow: exit immediately for non-KCSAN runs; otherwise process logs into a summary file in the result directory.

State and persistence: writes `$resultsdir/kcsan.sum`.

Dependencies and integration: called by `kvm-end-run-stats.sh`.

Risks and test signals: collapses only the headline line, not full stack traces, so distinct bugs with same headline may merge.
