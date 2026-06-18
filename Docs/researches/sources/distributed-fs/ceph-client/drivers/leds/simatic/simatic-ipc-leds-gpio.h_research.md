<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio.h -->
# sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio.h

Purpose: This header declares the shared SIMATIC GPIO LED helper API used by board-specific GPIO mapping modules.

Important APIs: `simatic_ipc_leds_gpio_probe()` accepts a platform device plus a primary and optional extra `gpiod_lookup_table`. `simatic_ipc_leds_gpio_remove()` removes the same resources. Both are implemented in the core helper and exported GPL-only.

Control flow and state: The header has no control flow or state. It defines the contract that board wrappers pass the same table pointers to probe and remove so lookup-table lifetime is balanced.

Dependencies and risks: The declarations require `struct platform_device` and `struct gpiod_lookup_table` to be visible through including C files. Test signal is compile coverage for every wrapper using this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio.h -->
