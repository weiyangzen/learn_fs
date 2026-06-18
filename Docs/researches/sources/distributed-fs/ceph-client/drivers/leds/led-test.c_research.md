# sources/distributed-fs/ceph-client/drivers/leds/led-test.c

## Purpose
Provides KUnit tests for selected LED framework behavior. The tests validate core LED class registration semantics, brightness initialization from a `brightness_get` callback, name collision handling, conflict rejection, lookup registration, and devm lookup.

## Important APIs, Types, And Functions
`struct led_test_ddata` holds a test classdev and KUnit device. `led_test_brightness_get` returns a fixed post-registration brightness. Test cases are `led_test_class_register` and `led_test_class_add_lookup_and_get`; setup/teardown are `led_test_init` and `led_test_exit`.

## Control Flow
The KUnit init allocates test data and registers a synthetic device named `led_test`. `led_test_class_register` registers `led-test`, verifies default `LED_FULL` max brightness, verifies brightness was updated to `LED_TEST_POST_REG_BRIGHTNESS`, registers a copied classdev with the same name to confirm suffixing to `led-test_1`, then enables `LED_REJECT_NAME_CONFLICT` and confirms another registration fails with `-EEXIST`.

`led_test_class_add_lookup_and_get` registers an LED, adds a `struct led_lookup_data` mapping the test device and connection ID to the provider name, resolves it with `devm_led_get`, verifies the returned provider, and removes the lookup entry.

## State And Persistence
State is KUnit-scoped and devres-managed. The lookup entry is stack-local but explicitly removed before the test exits. The class devices are released through devm cleanup tied to the synthetic KUnit device.

## Dependencies And Integration Points
Depends on KUnit device helpers and the LED class APIs. It directly tests functionality in `led-class.c` and indirectly exercises `led_update_brightness`.

## Risks
Coverage is focused and does not test triggers, blink work/timers, suspend/resume, fwnode naming, or flash/multicolor subclasses. The lookup test depends on provider names remaining stable during registration.

## Test Signals
Run the KUnit suite named `led`. Passing assertions confirm registration success, default max brightness, brightness-get initialization, name collision suffixing, conflict rejection, lookup insertion/removal, and `devm_led_get` resolution.
