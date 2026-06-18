# sources/distributed-fs/ceph-client/include/linux/leds.h

Purpose: declares the generic Linux LED class, trigger framework, naming/init data, brightness/blink/pattern operations, lookup APIs, GPIO/platform data helpers, and trigger-specific notification hooks.

Important APIs and types: `struct led_classdev` is the central device with name, brightness, max brightness, color, flags, work/timer blink state, brightness/blink/pattern callbacks, device/sysfs groups, trigger fields, optional hardware-control hooks, brightness-hardware-change support, and access mutex. Registration APIs include regular/devm and init-data forms. Control APIs set brightness, blink, oneshot blink, multicolor brightness, update brightness, read default patterns, compose names, and enable/disable sysfs. `struct led_trigger` and trigger APIs register simple/complex triggers and emit brightness/blink events. Platform structs cover lookup data, GPIO LEDs, generic LED info, properties, CPU/disk/MTD/camera/backlight trigger hooks, and patterns.

Control flow: LED drivers initialize a classdev and callbacks, register it, then callers use class APIs or triggers. Non-sleeping callbacks must be used from atomic paths; blocking callbacks are routed through work where needed. Trigger code attaches to LEDs under trigger locks and may use hardware-control hooks or software fallback.

State and persistence: state is in-memory class-device state plus deferred work/timers. Brightness and blink state are mirrored to hardware by driver callbacks; sysfs exposes current state but does not persist it.

Dependencies and integration points: depends on device model, fwnode/DT LED bindings, workqueues, timers, locks, GPIO, platform devices, and optional trigger configs. It is the shared integration surface for nearly all LED drivers, triggers, and userspace sysfs.

Risks and test signals: risks include sleeping in non-sleep callbacks, blink timer races, trigger-data lifetime bugs, name conflicts, multicolor count mismatches, sysfs disabled state drift, and hardware-control fallback errors. Test registration/unregistration/devm, brightness atomic and blocking paths, blink and oneshot timers, trigger attach/remove, suspend/resume flags, panic indicators, GPIO defaults, and config-disabled trigger stubs.
