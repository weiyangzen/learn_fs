# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck-scf.sh

Purpose: extracts scftorture handler invocation progress and rate from a scenario result directory.

Important APIs and functions: greps `console.log` for `scf_invoked_count ver:`, reads `scftorture.shutdown_secs` from `qemu-cmd`, and computes invocations per second.

Control flow: validate dir, print `-------` if no counter, otherwise print count plus optional rate.

State and persistence: read-only.

Dependencies and integration: used by `kvm-recheck.sh` when `TORTURE_SUITE=scf`.

Risks and test signals: output is purely progress-oriented. Missing or changed printk format produces no useful rate.
