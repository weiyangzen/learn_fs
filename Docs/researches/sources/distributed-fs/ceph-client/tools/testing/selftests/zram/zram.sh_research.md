<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/zram/zram.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/zram/zram.sh

## Purpose

`zram.sh` is the top-level zram selftest runner. It performs prerequisite checks and runs filesystem and swap zram scenarios.

## Important APIs, Types, and Functions

It sources `zram_lib.sh`, defines `TCID="zram.sh"`, and implements `run_zram()` to execute `./zram01.sh` and `./zram02.sh` with separators.

## Control Flow and State

The script calls `check_prereqs` first, then runs both child tests. It does not aggregate child exit codes explicitly, so visible pass/fail messages come from the child scripts and their cleanup behavior.

## Dependencies and Integration Points

It depends on root privileges, the current working directory containing the zram scripts, and kselftest invoking it from the installed selftest directory. It integrates with the Makefile via `TEST_PROGS`.

## Risks and Test Signals

Risks include child failures not being propagated as a final exit status and dependence on relative paths. Test signals are the printed `zram01` and `zram02` pass/fail lines plus kselftest process status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/zram/zram.sh -->
