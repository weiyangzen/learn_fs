# sources/distributed-fs/ceph-client/drivers/leds/leds-menf21bmc.c

Purpose: LED driver for the MEN 14F021P00 board management controller, exposing four binary LEDs.

Important APIs/types/functions: static `struct menf21bmc_led leds[]` defines status, hotswap, user1, and user2 LEDs. `menf21bmc_led_set()` performs a locked read-modify-write of BMC command `0xA0`. `menf21bmc_led_probe()` registers all four LED class devices.

Control flow: platform child uses parent I2C client, assigns names and brightness callback to static LED descriptors, then registers each with devm. Brightness writes read the current LED bitfield, set or clear one bit, and write it back.

State and persistence: driver has no per-device dynamic state besides the I2C client pointer in static descriptors. Hardware BMC state persists outside the driver until changed.

Dependencies and integration: depends on platform device under an I2C-backed BMC, SMBus byte read/write, LED class, and a global mutex for register serialization.

Risks: static LED descriptors and global lock make multiple device instances unsafe. Brightness set ignores I2C write errors and cannot report failure because it uses non-blocking callback signature.

Test signals: registration of all four LEDs, bit preservation across read-modify-write, I2C read error behavior, and multiple-instance avoidance.
