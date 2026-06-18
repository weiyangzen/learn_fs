# sources/distributed-fs/ceph-client/drivers/leds/leds.h

Purpose: private LED core header used inside the LED subsystem. It exposes internal helpers and global LED lists to LED core implementation files, not to generic driver consumers.

Important APIs, types, and functions: `led_get_brightness()` inline returns `led_cdev->brightness`. Declarations include `led_init_core()`, `led_stop_software_blink()`, `led_set_brightness_nopm()`, `led_set_brightness_nosleep()`, and binary attribute handlers `led_trigger_read()`/`led_trigger_write()`. It also declares `leds_list_lock` and `leds_list`.

Control flow: there is no executable control flow beyond the inline getter. Including source files use these declarations to initialize LEDs, manage software blink, perform non-PM brightness updates, and expose trigger data through sysfs/bin attributes.

State and persistence: the header declares subsystem-global LED registry state: an RW semaphore and list head. Actual storage and lifetime are defined elsewhere.

Dependencies and integration points: includes `linux/rwsem.h` and public `linux/leds.h`. It is an internal integration point between LED core files and trigger code.

Risks and test signals: risks are ABI/API internal consistency rather than runtime behavior. Build tests should catch signature drift. LED core tests should verify list locking, brightness updates in sleep/nosleep contexts, and trigger read/write paths that rely on these declarations.
