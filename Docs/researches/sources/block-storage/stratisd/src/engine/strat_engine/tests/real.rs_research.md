# File Research: sources/block-storage/stratisd/src/engine/strat_engine/tests/real.rs

## Purpose
Implements the real-block-device test harness for strat-engine tests. It consumes destructive-device configuration, optionally slices large devices into linear DM devices, runs tests, and wipes/cleans up devices.

## Main Components
- `RealTestDev` wraps either a direct device path or a generated `LinearDev`.
- `RealTestDev::new()` wipes the first MiB to clear metadata.
- `RealTestDev::teardown()` wipes again, settles udev, and tears down generated linear devices.
- `DeviceLimits` supports:
  - `Exactly(count, min_size, max_size)`
  - `AtLeast(count, min_size, max_size)`
  - `Range(lower, upper, min_size, max_size)`
- `get_device_runs()` selects or synthesizes device lists from configured device sizes.
- `make_linear_test_dev()` creates a DM linear target over a segment of a larger physical device.
- `test_with_spec()` reads `tests/test_config.json`, selects devices, runs the test, and performs cleanup.

## Behavior
The harness reads `ok_to_destroy_dev_array_key` from `tests/test_config.json`; devices listed there are considered safe to wipe. It measures block-device sizes, filters by minimum and maximum sizes, and can split oversized devices into multiple fixed-size linear devices when additional test devices are needed.

Before each run it calls cleanup, constructs `RealTestDev` wrappers, converts them to paths, catches panics, then optionally cleans up and tears down devices unless `NO_TEST_CLEAN_UP=1`.

## Research Notes
This harness is explicitly destructive. Its device-selection logic allows the same tests to run on varying real hardware availability while preserving minimum/maximum size requirements.
