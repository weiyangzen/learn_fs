# sources/distributed-fs/ceph-client/drivers/leds/leds-net48xx.c

Purpose: Soekris net48xx error LED driver using the SCx200 GPIO infrastructure.

Important APIs/types/functions: static `net48xx_error_led` exposes `net48xx::error`; `net48xx_error_led_set()` writes GPIO 20 through `scx200_gpio_ops`; module init self-registers a platform driver and platform device.

Control flow: init first checks `scx200_gpio_ops.dev`, registers the platform driver, creates a simple platform device, and probe registers one LED class device. Brightness writes directly set GPIO 20 high or low.

State and persistence: no dynamic state except the created platform device pointer. Hardware GPIO level is the only LED state.

Dependencies and integration: depends on x86 SCx200/NSC GPIO support, platform-device self-registration, LED class, and suspend/resume LED core flag.

Risks: direct dependency on global `scx200_gpio_ops` makes probe order important. No GPIO reservation is performed in this file. Unsupported systems return `-ENODEV` at module init.

Test signals: load with and without SCx200 GPIO present, LED class registration, GPIO 20 polarity, and module unload cleanup.
