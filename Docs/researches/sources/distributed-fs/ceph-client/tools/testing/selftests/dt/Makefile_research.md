# sources/distributed-fs/ceph-client/tools/testing/selftests/dt/Makefile

## Purpose
Build metadata for devicetree unprobed-device selftest. It conditionally enables the test only when python3 is available.

## Important APIs, Types, And Functions
Defines `PY3 = $(shell which python3 ...)`, `TEST_PROGS := test_unprobed_devices.sh`, generated `compatible_list`, and `TEST_FILES := compatible_ignore_list`. The `compatible_list` target runs `scripts/dtc/dt-extract-compatibles -d $(top_srcdir)`.

## Control Flow
With python3 present, kselftest builds the compatible list and installs/runs the script. Without python3, `all` prints a skip warning.

## State And Persistence
Generates `$(OUTPUT)/compatible_list` from the kernel source tree.

## Dependencies And Integration Points
Depends on `dt-extract-compatibles`, python3, and the runtime script’s ignore list.

## Risks
If the generated compatible list is stale or missing, the runtime test may skip/fail nodes incorrectly. The no-python path skips at build time rather than runtime.

## Test Signals
Successful build creates `compatible_list` and installs `compatible_ignore_list` with the test script.
