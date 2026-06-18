# sources/distributed-fs/ceph-client/arch/mips/bcm47xx/leds.c

Purpose: Broadcom BCM47xx board LED database and registration glue. It maps detected `enum bcm47xx_board` values to `struct gpio_led` arrays for many consumer router models, then exposes them through the kernel `leds-gpio` platform device.

Important APIs and functions: the `BCM47XX_GPIO_LED` and `BCM47XX_GPIO_LED_TRIGGER` macros build consistent LED names, GPIO numbers, active-low polarity, default state, and optional triggers. `bcm47xx_leds_register()` switches on `bcm47xx_board.board`, selects board-specific LED arrays with `bcm47xx_set_pdata()` or `_extra()`, and registers `bcm47xx_gpio_leds` when a matching table exists.

Control flow: initialization is data driven. Each board family contributes static `__initconst` LED tables; the final switch populates `gpio_led_platform_data` and conditionally calls `platform_device_register`. No runtime probing happens beyond consuming the global board detector result.

State and persistence: LED state is transient GPIO output state owned by the LED subsystem after registration. The static board tables are discarded after init; no NVRAM or filesystem persistence is performed.

Dependencies and integration points: depends on `bcm47xx_board` identification, Linux GPIO LED platform data, and board-private setup code calling `bcm47xx_leds_register()` from the BCM47xx bus/device setup path. It integrates with user space through normal LED class devices and trigger names.

Risks and test signals: correctness depends on hard-coded board/GPIO/polarity data. A wrong mapping can invert power LEDs, leave LEDs unavailable, or drive pins used by other hardware. Test signals are boot logs, presence of `/sys/class/leds/bcm47xx:*`, LED trigger behavior, and board-specific manual GPIO validation.
