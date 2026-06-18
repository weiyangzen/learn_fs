# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/conftest.py

## Purpose
`conftest.py` configures the HID pytest suite. It enforces hidtools version requirements, manages session-level udev rule cleanup, disables core dumps, optionally starts systemd-udevd, registers custom markers, and parameterizes tests over installed HID kernel modules.

## Important APIs, types, and functions
Autouse fixtures include `hidtools_version_check()`, `udev_rules_session_setup()`, `setup_rlimit()`, and `start_udevd()`. `pytest_configure()` registers `skip_if_uhdev`. `pytest_generate_tests()` detects a `usbVidPid` fixture and fills it from `modinfo` aliases in installed HID modules. `pytest_addoption()` adds `--udevd`.

## Control flow
Before every test, the hidtools version check skips if the package is missing or older than `0.12`. Session setup enters `HIDTestUdevRule.instance()` so the reference-counted rule manager can clean up after tests. If `--udevd` is set, a `systemd-udevd` subprocess is launched for the session and killed afterward. Parameter generation scans `/lib/modules/<release>/kernel/drivers/hid/*.ko`, parses HID USB modaliases, and creates ids for parametrized tests.

## State and persistence
The file changes process resource limits to disable core files. It can start a session subprocess and relies on the singleton udev-rule manager for temporary rule state. It does not write persistent repository files.

## Dependencies and integration points
It integrates pytest with packaging, platform, resource limits, subprocess tools, installed kernel modules, and the base udev rule helper.

## Risks and test signals
Risks include hard-coded udevd path, missing `modinfo`, compressed module names not matching `*.ko`, and broad exception handling in the version check. Signals include clean pytest collection, correct skip reasons, generated USB VID/PID parameter sets, and no core dump artifacts.
