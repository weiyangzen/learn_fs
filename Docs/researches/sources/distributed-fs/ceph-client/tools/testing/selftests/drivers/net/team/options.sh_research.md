# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/options.sh

## Purpose
Validates basic team driver option get/set behavior through `teamnl`, including global team options, per-port options, invalid option lookup, and implicit synchronization between `enabled`, `rx_enabled`, and `tx_enabled`. The test runs inside a private network namespace via `in_netns.sh` when invoked directly.

## Important APIs, Types, And Functions
The script uses `ip link` to create a dummy member and a team device, `teamnl getoption/setoption` to exercise netlink option paths, and net selftest helpers from `net/lib.sh` such as `require_command`, `check_err`, `check_fail`, `log_test`, and `tests_run`. Key local helpers are `get_and_check_value()`, `set_and_check_get()`, `get_port_flag()`, port attach/detach helpers, `team_test_option()`, and the implicit-change tests.

## Control Flow
Startup re-execs under a private namespace, exports four `ALL_TESTS` entries, requires `teamnl`, creates `dummy0` and `team0`, then lets `tests_run` call each test. Generic option tests attach a member only for per-port options, set values in a value1/value2/value1 sequence, and verify reads after every write. Negative tests expect lookup failure. The implicit-change tests prove setting aggregate `enabled` updates RX/TX flags and setting either split flag changes aggregate `enabled`.

## State And Persistence
All state is transient kernel netdevice state inside the namespace. `RET` and `EXIT_STATUS` are the kselftest accounting state; no persistent files are written.

## Dependencies And Integration Points
Requires the team driver, dummy netdevice support, `teamnl`, namespace support, and `tools/testing/selftests/net/lib.sh`. It integrates with kselftest via `ALL_TESTS` and `tests_run`.

## Risks
The script assumes option string formatting from `teamnl` exactly matches requested values. Port cleanup is done only inside test functions, so an early fatal failure can leave namespace-local devices until namespace teardown. Per-port option coverage depends on successful enslaving of `dummy0`.

## Test Signals
Pass signals are `log_test` results for option round trips and implicit flag propagation. Failures identify the option name and expected versus observed value or unexpected success for fake options.
