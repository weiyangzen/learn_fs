# sources/distributed-fs/ceph-client/drivers/gpio/gpio-moxtet.c

Purpose: exposes fixed GPIO-like input/output signals on Turris MOX modules connected over the Moxtet bus. The current descriptor supports the SFP module.

Important APIs/types/functions: `struct moxtet_gpio_desc` defines valid input and output bitmasks. `struct moxtet_gpio_chip` holds the parent device, `gpio_chip`, and descriptor. GPIO callbacks implement get, set, get_direction, direction_input, and direction_output. The driver is a `struct moxtet_driver` with an OF table and module-id table.

Control flow: probe reads the Moxtet module id, rejects unsupported ids, allocates state, assigns the descriptor, fills a sleepable dynamic-base gpiochip, and registers it. Get reads either current input state via `moxtet_device_read()` or last written output state via `moxtet_device_written()`, shifting output state by `MOXTET_GPIO_INPUTS` to align with public offsets. Set reads the last written state, adjusts the output bit after subtracting the input offset, and writes it back.

State and persistence behavior: fixed direction is derived from descriptor masks, not mutable hardware configuration. Output state persists in the Moxtet device's written-state cache and hardware. The driver keeps no extra shadow besides the descriptor pointer. There is no PM hook.

Dependencies and integration points: depends on the Moxtet bus API, module id `TURRIS_MOX_MODULE_SFP`, OF compatible `cznic,moxtet-gpio`, and gpiolib. It marks the chip `can_sleep` because bus transactions can sleep.

Risks: only bits listed in descriptor masks are valid; all other offsets return `-EINVAL`. Direction attempts on hard-wired opposite-direction lines return `-ENOTSUPP`. Output bit shifting is subtle because public offsets include the four input slots while the written state stores outputs from bit 0.

Test signals: SFP module probe, unsupported module rejection, fixed-direction reporting, input reads, output write/readback through Moxtet cache, invalid offset behavior, and expected sleepable GPIO semantics.
