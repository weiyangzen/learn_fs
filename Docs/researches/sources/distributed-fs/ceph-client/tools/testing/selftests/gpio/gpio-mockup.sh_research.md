<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-mockup.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-mockup.sh

## Purpose
This main GPIO mockup test validates module range parsing, line read/write behavior, active-low handling, optional bias behavior, deprecated ABI modes, and overlap/error handling.

## Important APIs, Types, And Functions
Key functions are `usage()`, `skip()`, `prerequisite()`, `remove_module()`, `cleanup()`, `fail()`, `try_insert_module()`, `release_line()`, `get_line()`, `set_line()`, `assert_line()`, `assert_mock()`, `set_mock()`, `test_line()`, `test_no_line()`, and `insmod_test()`. It uses debugfs `/sys/kernel/debug/gpio-mockup`, `modprobe gpio-mockup gpio_mockup_ranges=...`, and helper `gpio-mockup-cdev`.

## Control Flow
After parsing `-f`, `-r`, `-t`, and `-v`, the script requires root/debugfs, selects cdev v2, cdev v1, or sysfs line helpers, removes existing module state, optionally skips full tests when `/dev/gpiochip0` exists, then runs dynamic allocation tests and optional manual/overlap tests. Each `insmod_test()` loads the module, discovers debugfs chips, tests fencepost and optional random lines, checks one-past-end absence, and unloads the module.

## State And Persistence
It loads/unloads `gpio-mockup`, creates line request processes, manipulates line values/biases, reads debugfs mockup state, and uses traps to release lines and kill background jobs.

## Dependencies And Integration Points
It depends on root, debugfs, `gpio-mockup`, GPIO cdev helper, optional sysfs override, and optional existing gpiochip constraints for full tests.

## Risks
The test is invasive to GPIO module state and skips full manual allocations when physical gpiochip0 exists. Background output helper processes must be killed to release lines. Random-line mode adds nondeterministic coverage.

## Test Signals
Expected final signal is `GPIO gpio-mockup test PASS`; line tests verify input reads, output writes, active-low inversion, optional bias pull behavior, fencepost absence, and range overlap handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-mockup.sh -->
