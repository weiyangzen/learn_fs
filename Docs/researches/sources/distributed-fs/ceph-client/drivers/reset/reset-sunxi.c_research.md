# sources/distributed-fs/ceph-client/drivers/reset/reset-sunxi.c

Purpose: early Allwinner A31 AHB1 reset-controller registration using the shared simple reset implementation before regular drivers are available.

Important APIs/types/functions: `sunxi_reset_init()` allocates `reset_simple_data`, maps the OF resource manually, initializes `reset_simple_ops`, sets active-low behavior, and registers `size * 8` resets. `sun6i_reset_init()` scans `allwinner,sun6i-a31-ahb1-reset`.

Control flow: architecture init calls `sun6i_reset_init()`, which registers matching early reset providers for consumers needed before device-model probing.

State and persistence: allocation and ioremap are permanent early-boot state; hardware registers hold reset state. There is no cleanup path.

Dependencies and integration: OF address helpers, manual memory reservation, `reset_simple_ops`, and `linux/reset/sunxi.h`.

Risks and test signals: on ioremap failure the requested memory region is not released. No dummy platform driver is provided here, unlike SoCFPGA. Test early consumers, memory reservation conflicts, active-low polarity, and boot on systems with and without the compatible.
