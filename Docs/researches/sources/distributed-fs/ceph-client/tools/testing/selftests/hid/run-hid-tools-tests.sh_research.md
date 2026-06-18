# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/run-hid-tools-tests.sh

## Purpose
`run-hid-tools-tests.sh` is the kselftest launcher for the Python hid-tools based HID test suite under `tests/`. It provides dependency checks and emits TAP output expected by the kernel selftest runner.

## Important APIs, types, and functions
The script is POSIX shell. It defines `KSELFTEST_SKIP_TEST=4`, checks `python3`, `pytest`, `pytest_tap`, and `hidtools`, sets `TARGET=${TARGET:=.}`, prints `TAP version 13`, and invokes `python3 -u -m pytest $PYTEST_XDIST ./tests/$TARGET --tap-stream --udevd`.

## Control flow
Execution is linear. Missing prerequisites produce a `[SKIP]` message and exit with the kselftest skip code. When dependencies exist, pytest is run on either the whole `tests` directory or a target selected by environment variable. `PYTEST_XDIST` is passed through for optional parallelism, and `--udevd` asks the pytest fixture to start udevd.

## State and persistence
The script persists no state. Runtime effects are delegated to pytest fixtures, which may create UHID devices, udev rules, and temporary kernel-facing objects during tests.

## Dependencies and integration points
It integrates kselftest TAP conventions with Python pytest, pytest-tap, hid-tools, and the local test package. It assumes tests are run from the HID selftest directory or another location where `./tests/$TARGET` resolves correctly.

## Risks and test signals
Risks include unquoted environment variables, dependency version mismatches handled later in `conftest.py`, and environment-specific udevd paths. Positive signal is TAP stream production; skip exits distinguish missing userspace dependencies from kernel/test failures.
