# sources/distributed-fs/ceph-client/drivers/leds/leds-da9052.c

Purpose: Dialog DA9052 PMIC LED driver for two GPIO-backed LED outputs described by MFD platform data.

Important APIs/types/functions: `struct da9052_led` stores classdev, PMIC pointer, LED index, and id. `led_reg[]` maps logical LED indices to DA9052 LED control registers. `da9052_set_led_brightness()` writes brightness plus continuous-dim mode. `da9052_configure_leds()` configures GPIO14/15 nibbles as high-level open-drain LED outputs. Probe iterates `led_platform_data`.

Control flow: probe obtains parent `da9052`, validates `da9052_pdata->pled`, allocates an array sized to `num_leds`, registers each LED classdev on the parent, initializes brightness to OFF, then configures the shared GPIO register. Remove turns each LED off and unregisters it.

State and persistence: per-LED index and PMIC pointer are software state; brightness lives in hardware registers. GPIO output configuration remains until changed by another driver or PMIC reset.

Dependencies/integration: relies on DA9052 MFD core, DA9052 platform data, DA9052 register-update helpers, and LED class callbacks.

Risks: `led_index` comes from platform-data flags and is used as an array index into a two-entry `led_reg[]`; bad board data can address invalid memory. Registration uses manual cleanup. Errors during initial brightness writes are logged but probing continues for that LED.

Test signals: validate platform-data bounds, GPIO14/15 nibble configuration, brightness max `0x5f`, cleanup after mid-loop registration failure, and remove-time OFF writes.
