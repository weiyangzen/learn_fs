# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/sdsi/sdsi.sh

## Purpose
Wrapper that prepares and runs pytest-based Intel SDSi driver tests.

## Important APIs, Types, And Functions
Uses `command -v python3`, `python3 -c "import pytest"`, `/sbin/modprobe -q -r intel_sdsi`, `/sbin/modprobe -q intel_sdsi`, and `python3 -m pytest sdsi_test.py`.

## Control Flow
It skips with exit 77 if python3, pytest, or module removal is unavailable. It then loads `intel_sdsi` and runs the pytest file, printing `[OK]` on success or `[FAIL]` with exit 1 on failure.

## State And Persistence
It unloads and reloads `intel_sdsi`, affecting live driver state. No files are written by the wrapper.

## Dependencies And Integration Points
Requires python3, pytest, modprobe, and the Intel SDSi driver/platform. It is the kselftest-facing entry point for `sdsi_test.py`.

## Risks
Exit code 77 is used as skip rather than the usual kselftest 4. Removing the driver can disrupt active SDSi devices.

## Test Signals
Wrapper-level signals are `[SKIP]`, `[OK]`, or `[FAIL]`; detailed assertions come from pytest.
