# sources/distributed-fs/ceph-client/drivers/leds/led-class.c

## Purpose
Implements the LED class device layer: `/sys/class/leds` devices, brightness and max-brightness sysfs files, trigger sysfs exposure, LED naming, provider lookup, suspend/resume hooks, and devres-managed registration.

## Important APIs, Types, And Functions
Public APIs include `led_classdev_register_ext`, `led_classdev_unregister`, `devm_led_classdev_register_ext`, `devm_led_classdev_unregister`, `led_get`, `devm_led_get`, `devm_of_led_get`, `devm_of_led_get_optional`, `led_put`, `led_add_lookup`, `led_remove_lookup`, `led_classdev_suspend`, `led_classdev_resume`, and `led_classdev_notify_brightness_hw_changed`.

The class object `leds_class` owns default groups for brightness, max brightness, and optional trigger binary attribute. `leds_lookup_list` supports non-DT lookup tables. `leds_wq` is the ordered workqueue used by the LED core.

## Control Flow
Subsystem init creates the ordered workqueue and registers the `leds` class. Registration composes a name from fwnode properties or legacy fields, resolves collisions by suffixing unless `LED_REJECT_NAME_CONFLICT` is set, creates the device with groups, attaches fwnode, optionally creates `brightness_hw_changed`, initializes work flags and trigger lock, sets default `max_brightness`, updates brightness from hardware, initializes core timer/work, adds the classdev to the global LED list, and applies the default trigger.

Unregister removes triggers, marks unregistering, stops software blinking, turns the LED off unless retain-at-shutdown is set, flushes work, removes optional attributes, unregisters the device, removes from the global list, and destroys `led_access`.

## State And Persistence
Per-LED state is in `struct led_classdev`: device pointer, brightness, max brightness, flags, work flags, trigger state, fwnode-derived metadata, and locks. Global persistent state includes the class, lookup list, LED list shared with trigger code, and ordered workqueue.

## Dependencies And Integration Points
Depends on the device model, sysfs, fwnode/OF, module references, triggers, the LED core, and `uapi/linux/uleds.h`. It integrates with all LED drivers through registration and with consumers through `led_get`/`devm_led_get` using DT phandles or lookup tables.

## Risks
Name composition and collision handling affect ABI-visible sysfs paths. Registration happens under `led_access`, so drivers that call back into LED APIs during probe need to avoid deadlocks. Provider lookup takes parent-driver module references; unusual parent/device ownership can make `led_get` fail. Unregistering while triggers or delayed brightness work are active depends on careful flush and trigger removal ordering.

## Test Signals
KUnit coverage in `led-test.c` exercises registration, brightness initialization, name collision suffixing, conflict rejection, lookup, and `devm_led_get`. Runtime signals include correct sysfs creation, default trigger application, suspend/resume off/restore behavior, and clean unregister with no pending work or trigger references.
