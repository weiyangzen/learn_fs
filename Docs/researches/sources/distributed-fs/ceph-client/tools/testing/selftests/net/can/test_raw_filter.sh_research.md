# sources/distributed-fs/ceph-client/tools/testing/selftests/net/can/test_raw_filter.sh

Purpose: this shell wrapper prepares a CAN interface, runs the compiled `test_raw_filter` binary, and reports the result through common net selftest helpers.

Important APIs/functions: it sources `../lib.sh`, sets `ALL_TESTS` to `test_raw_filter`, and uses `setup`, `cleanup`, `tests_run`, `check_err`, and `log_test`. It exports `CANIF`, defaulting to `vcan0`, and `BITRATE`, defaulting to `500000` for physical CAN devices.

Control flow: `setup` creates a vcan link when `CANIF` starts with `vcan`; otherwise it configures the named device as CAN with the requested bitrate. It then brings the device up. `test_raw_filter` executes `./test_raw_filter`, checks the exit code, and logs the test. `cleanup` brings the device down and deletes it if it was a vcan created by this script. A trap ensures cleanup runs at exit.

State and persistence: the script mutates netdevice state by adding/deleting or reconfiguring a CAN link. It persists no files. State is scoped by the interface name and cleaned on normal exit.

Dependencies and integration points: depends on `ip`, CAN/vcan kernel support, root privileges or equivalent net admin capability, the generated `test_raw_filter` binary, and `lib.sh` kselftest functions.

Risks and test signals: non-vcan mode reconfigures a user-specified physical CAN device and may disrupt external state. `pwd` in `setup` is a noisy diagnostic. Successful signals are link setup, zero exit from the binary, and final `EXIT_STATUS` from `tests_run`.
