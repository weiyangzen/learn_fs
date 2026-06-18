# sources/distributed-fs/ceph-client/drivers/input/tests/input_test.c

## Purpose
`input_test.c` is a KUnit suite for selected input-core helpers. It creates a virtual input device for each test and verifies polling setup, timestamp access, device-ID matching, and grab exclusivity behavior.

## Important APIs, types, and functions
`input_test_init()` allocates and registers a virtual input device with left/right button capabilities; `input_test_exit()` unregisters it. Test cases are `input_test_polling()`, `input_test_timestamp()`, `input_test_match_device_id()`, and `input_test_grab()`. The suite is registered with `kunit_test_suite(input_test_suite)`.

## Control flow
Each test starts with a registered `struct input_dev` in `test->priv`. Polling verifies `input_get_poll_interval()` fails before `input_setup_polling()` and succeeds after `input_set_poll_interval()`. Timestamp verifies a valid default monotonic timestamp and a set/get round trip. Device-ID matching toggles match flags and fields. Grab testing creates synthetic handles and confirms only one handle can hold an input grab until release.

## State and persistence
State is per KUnit test instance and cleaned up in `exit`. The grab test temporarily increments input device references through `input_get_device()` and balances with `input_put_device()`.

## Dependencies and integration points
The suite depends on KUnit, input core allocation/registration, input polling APIs, timestamp APIs, device ID matching, and grab/release semantics. It is built by the local tests Makefile under `CONFIG_INPUT_KUNIT_TEST`.

## Risks
The synthetic `struct input_handler`, `input_handle`, and `input_device_id` objects are stack/local and only partially initialized, so changes in input core expectations could require more complete setup. The grab test is sensitive to reference balancing and shared device state. The suite covers only a small part of input core behavior.

## Test signals
Run the `input_core` KUnit suite, especially after changes to polling, timestamp initialization, input ID matching flags, or grab locking. Add negative tests if future input core changes add validation to handlers or handles.
