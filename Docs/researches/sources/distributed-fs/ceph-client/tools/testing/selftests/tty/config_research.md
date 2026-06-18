# sources/distributed-fs/ceph-client/tools/testing/selftests/tty/config

## Purpose
This kselftest config fragment requests kernel support needed by the TIOCSTI legacy behavior test.

## Important APIs, Types, and Functions
It contains `CONFIG_LEGACY_TIOCSTI=y`.

## Control Flow
No runtime control flow exists. The config is consumed by selftest/kernel config tooling.

## State and Persistence
It does not mutate runtime state.

## Dependencies and Integration Points
It integrates with kselftest config checks to indicate that legacy TIOCSTI support should be enabled for this test area.

## Risks
If kernels are built without this option, parts of `tty_tiocsti_test` may skip or behave differently.

## Test Signals
The signal is configuration intent rather than executable behavior.
