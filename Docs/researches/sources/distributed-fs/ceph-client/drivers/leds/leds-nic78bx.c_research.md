# sources/distributed-fs/ceph-client/drivers/leds/leds-nic78bx.c

Purpose: National Instruments PXI user LED driver for ACPI device `NIC78B3`.

Important APIs/types/functions: static `nic78bx_leds[]` defines green/yellow LEDs for user1/user2 with bit and mask fields. `nic78bx_brightness_set()` and `nic78bx_brightness_get()` access I/O ports under a spinlock. `lock_led_reg_action()` relocks the LED register on managed cleanup.

Control flow: probe validates I/O resource size, requests the region, records base port, installs cleanup action, registers four LEDs, then unlocks the LED register. Setting a color clears the whole user LED color mask then sets the chosen bit, making green/yellow mutually exclusive per user LED.

State and persistence: no cache; state is read from I/O port. Register lock state is restored on device cleanup.

Dependencies and integration: depends on ACPI matching, I/O port resources, `inb/outb`, LED class, spinlocks, and devm cleanup.

Risks: cleanup action is registered before the unlock write, so failures after action registration relock as intended. Hardware access assumes the platform resource points to a two-byte lock/data region. Only one color per user LED can be active due to mask clearing.

Test signals: ACPI enumeration, I/O resource validation, register unlock/lock sequence, four LED get/set callbacks, and mutual exclusion of green/yellow bits.
