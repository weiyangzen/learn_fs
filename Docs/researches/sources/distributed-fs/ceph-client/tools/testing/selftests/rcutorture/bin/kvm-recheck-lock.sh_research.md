# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck-lock.sh

Purpose: extracts locktorture progress from a scenario result directory.

Important APIs and functions: greps `console.log` for `"Writes:  Total:"`, extracts acquisition/release count, reads `locktorture.shutdown_secs` from `qemu-cmd`, and computes per-second rate with awk.

Control flow: validate result dir, derive config name, print `-------` if no count, otherwise print count and optional rate.

State and persistence: read-only.

Dependencies and integration: invoked by `kvm-recheck.sh` when `TORTURE_SUITE=lock`.

Risks and test signals: log format changes can produce blank progress. It reports progress but does not detect correctness failures beyond absent output.
