<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/zram/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/zram/Makefile

## Purpose

The zram selftest `Makefile` registers the zram shell test entrypoint and support files with kselftest.

## Important APIs, Types, and Functions

It defines an empty `all` target, `TEST_PROGS := zram.sh`, `TEST_FILES := zram01.sh zram02.sh zram_lib.sh`, `EXTRA_CLEAN := err.log`, and includes `../lib.mk`.

## Control Flow and State

There is no runtime flow in the Makefile. Kselftest uses the variables to install or run `zram.sh` and copy helper scripts. `err.log` is declared as cleanup state produced by the shell tests.

## Dependencies and Integration Points

It depends on the kselftest `lib.mk` contract and the adjacent shell scripts. It integrates with `make kselftest` and packaging/install of selftests.

## Risks and Test Signals

Risks include omitting helper scripts from `TEST_FILES` or failing to clean `err.log`. A successful signal is that `zram.sh` is discoverable and both helper tests run under the kselftest harness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/zram/Makefile -->
