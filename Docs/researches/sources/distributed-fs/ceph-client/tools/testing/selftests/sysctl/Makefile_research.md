# sources/distributed-fs/ceph-client/tools/testing/selftests/sysctl/Makefile

## Purpose
Registers the sysctl selftest shell script with kselftest.

## Important APIs, Types, And Functions
Defines a no-op `all` target so plain `make` does not run tests, sets `TEST_PROGS := sysctl.sh`, includes `../lib.mk`, and defines an empty `clean` target. Comments document the expectation that `kernel.sysctl_writes_strict=1`.

## Control Flow
Build-time control is delegated to kselftest `lib.mk`; runtime is entirely in `sysctl.sh`.

## State And Persistence
No state is persisted by the Makefile.

## Dependencies And Integration Points
Pairs with `config`, which requests `CONFIG_TEST_SYSCTL=m`, and with the shell script that modprobes `test_sysctl` when needed.

## Risks
The no-op `all` target is deliberate; changing it could make sysctl tests run during build by accident. The tests require root and can mutate production sysctls during execution.

## Test Signals
`make kselftest` discovers `sysctl.sh` as a test program and does not build binaries for this directory.
