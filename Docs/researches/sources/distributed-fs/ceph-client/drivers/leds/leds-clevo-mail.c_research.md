# sources/distributed-fs/ceph-client/drivers/leds/leds-clevo-mail.c

## Purpose
Implements the mail LED found on selected older Clevo laptops through i8042 controller commands. It registers one LED class device named `clevo::mail` after DMI detection or with the `nodetect` module parameter.

## Important APIs, Types, And Functions
The static classdev `clevo_mail_led` provides `brightness_set`, `blink_set`, and `LED_CORE_SUSPENDRESUME`. Key functions are the DMI callback/table, `clevo_mail_led_set`, `clevo_mail_led_blink`, platform probe/remove, module init, and module exit.

## Control Flow
Module init checks the DMI table unless `nodetect` is set, registers a simple platform device, and probes a platform driver that registers the LED. Brightness off sends `CLEVO_MAIL_LED_OFF`; brightness up to `LED_HALF` sends 0.5 Hz blink; higher brightness sends 1 Hz blink. Blink supports default 0/0 by selecting 0.5 Hz, exact 500/500 for 1 Hz, and exact 1000/1000 for 0.5 Hz; other delays return `-EINVAL`.

Exit unregisters platform objects and explicitly turns the LED off.

## State And Persistence
No private state is stored except the global platform device pointer and module parameter. Hardware state is the laptop controller LED mode. i8042 access is protected with `i8042_lock_chip`.

## Dependencies And Integration Points
Depends on DMI, platform devices, i8042 command locking, and LED class. It integrates with known Clevo DMI identities and allows risky forced probing with `nodetect`.

## Risks
i8042 commands are platform-specific; false-positive probing can affect keyboard-controller behavior. Brightness maps to blink modes rather than steady intensity. Only two blink rates are supported. The `nodetect` parameter intentionally bypasses safety checks.

## Test Signals
On matched hardware, registration should create `clevo::mail`; brightness values should issue off/slow/fast commands; supported blink delays should update returned delays and succeed; unsupported delays should fall back through `-EINVAL`; module exit should turn the LED off.
