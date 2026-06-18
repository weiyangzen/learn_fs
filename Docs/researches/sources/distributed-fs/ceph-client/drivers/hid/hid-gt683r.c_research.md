# sources/distributed-fs/ceph-client/drivers/hid/hid-gt683r.c

Implements LED class support for the MSI GT683R laptop LED panel. It exposes three binary zones and a sysfs mode selector, then sends vendor feature reports to control enabled zones and animation mode.

`struct gt683r_led` stores the HID pointer, three `led_classdev`s, mutex, work item, per-panel brightness, and current mode. `gt683r_brightness_set()` updates zone state and schedules work. `mode_show()`/`mode_store()` expose shared mode as values `0..2`. `gt683r_led_snd_msg()` sends 8-byte feature reports. `gt683r_led_work()` computes the zone bitmask and sends LED/mode messages. Probe registers `back`, `side`, and `front` LEDs; remove unregisters, flushes work, and stops HID.

Brightnesses and mode are runtime memory only, while hardware state is changed by live feature reports. Dependencies include HID raw requests, LED class, workqueues, mutexes, and MSI IDs from `hid-ids.h`.

Risks include shared mode being exposed under each LED, coalesced work hiding intermediate changes, feature report failures only being logged, and careful partial-probe unwind. Test signals include LED names, each zone bit, all-off behavior, valid/invalid mode writes, feature report length checking, and removal with queued work.
