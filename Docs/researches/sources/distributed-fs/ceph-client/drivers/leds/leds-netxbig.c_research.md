# sources/distributed-fs/ceph-client/drivers/leds/leds-netxbig.c

Purpose: LaCie 2Big/5Big Network series LED driver using a GPIO extension latch with LED mode, brightness, timer, and SATA-activity modes.

Important APIs/types/functions: `struct netxbig_gpio_ext` models address/data/enable GPIO latch lines. `netxbig_led_data` stores LED class state, mode values, timer table, SATA flag, and lock. `gpio_ext_set_value()` writes latch address/data under a global spinlock. `netxbig_led_set()`, `netxbig_led_blink_set()`, and `sata` sysfs handlers control modes.

Control flow: probe parses a `gpio-ext` phandle, obtains unmanaged GPIO descriptors from that device with managed cleanup, parses optional `timers`, parses per-LED mode/brightness addresses and mode-value pairs, allocates runtime LED data, and registers each LED. Brightness chooses OFF, SATA, ON, or existing timer mode and writes mode and brightness latch registers.

State and persistence: per-LED software state tracks current mode and SATA flag because the GPIO extension bus cannot read back registers. Initial hardware state is intentionally not reprogrammed, so sysfs brightness/SATA may not match bootloader state until first write.

Dependencies and integration: depends on OF phandles, platform device lookup, GPIO descriptors from a sibling device, LED class, spinlocks, and board-specific mode tables.

Risks: shared brightness register for SATA LEDs means one LED brightness write affects others. GPIO descriptors are intentionally not devm-owned by their original device, so cleanup correctness is important. Mode tables can omit modes; missing SATA or blink modes return `-EINVAL`.

Test signals: DT parser validation for `gpio-ext`, `timers`, and `mode-val`; latch GPIO sequencing; SATA sysfs mode transitions; unsupported blink period rejection; shared brightness behavior; and cleanup of externally acquired GPIOs.
