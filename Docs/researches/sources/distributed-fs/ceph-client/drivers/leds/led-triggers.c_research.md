# sources/distributed-fs/ceph-client/drivers/leds/led-triggers.c

## Purpose
Implements the LED trigger core. It manages trigger registration, sysfs trigger selection, default-trigger matching, trigger activation/deactivation, per-trigger LED lists, trigger-driven brightness events, multicolor events, blink events, and devres/simple trigger helpers.

## Important APIs, Types, And Functions
Exports include `led_trigger_read`, `led_trigger_write`, `led_trigger_set`, `led_trigger_remove`, `led_trigger_set_default`, `led_trigger_register`, `led_trigger_unregister`, `devm_led_trigger_register`, `led_trigger_event`, `led_mc_trigger_event`, `led_trigger_blink`, `led_trigger_blink_oneshot`, `led_trigger_register_simple`, and `led_trigger_unregister_simple`.

Global state is `trigger_list` protected by `triggers_list_lock`; each trigger owns an RCU-protected LED list protected by `leddev_list_lock`.

## Control Flow
Sysfs writes under `led_access` accept `none`, `default`, or a registered trigger name relevant to the LED trigger type. Setting a trigger removes the old trigger, deletes RCU list membership, synchronizes RCU, cancels brightness work, stops software blinking, removes trigger sysfs groups, calls deactivate, clears trigger fields, and turns the LED off. For a new trigger, it adds list membership, synchronizes so activate can emit events, flushes pending brightness work, calls activate or sets default trigger brightness, adds trigger groups, and emits a uevent.

Trigger registration rejects duplicate compatible names, adds the trigger globally, and applies it to LEDs with matching unresolved default triggers. Unregistration removes the trigger globally and detaches it from every LED.

## State And Persistence
State persists in registered `struct led_trigger` objects, their LED lists, `led_cdev->trigger`, `trigger_data`, `activated`, and default-trigger flags. RCU is used for event dispatch while rwsems serialize structural changes.

## Dependencies And Integration Points
Depends on LED class global lists, sysfs binary attributes, device groups, RCU, module autoloading, and kobject uevents. It integrates with trigger providers and all LED class devices that enable `CONFIG_LEDS_TRIGGERS`.

## Risks
Lock ordering is explicit: global trigger list lock nests outside each LED trigger lock. Activation failures require careful unwind to remove list membership and turn the LED off. The trigger sysfs read path uses a dynamically sized binary attribute because CPU triggers can be numerous. Event dispatch walks RCU lists and must not rely on sleeping operations outside LED helpers.

## Test Signals
Runtime tests should register/unregister triggers, select them via sysfs, verify `none` and `default`, observe uevents, confirm default trigger autoloading, exercise trigger attributes, and dispatch brightness/blink/multicolor events while concurrently unregistering LEDs and triggers.
