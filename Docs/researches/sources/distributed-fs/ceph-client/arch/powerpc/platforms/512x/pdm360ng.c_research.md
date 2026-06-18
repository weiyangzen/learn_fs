# sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/pdm360ng.c

## Purpose
`pdm360ng.c` registers the IFM PDM360NG/AC14xx MPC512x board and provides board glue for the ADS7846 touchscreen pendown GPIO.

## Important APIs, Types, and Functions
`pdm360ng_probe()` excludes non-`"ifm,ac14xx"` systems and calls `mpc512x_init_early()`. `pdm360ng_init()` runs common MPC512x init and touchscreen setup. When `CONFIG_TOUCHSCREEN_ADS7846` is enabled, `pdm360ng_touchscreen_init()` maps `"fsl,mpc5121-gpio"`, registers an SPI bus notifier, and injects `ads7846_platform_data` for `spi32766.1`.

## Control Flow, State, and Persistence
The file keeps a permanent GPIO mapping in `pdm360ng_gpio_base` for pendown reads and a notifier block in the SPI bus notifier chain. The pendown callback tests GPIO bit 29 from the simple GPIO input register area.

## Dependencies and Integration Points
It integrates shared MPC512x setup, OF compatible `"ifm,ac14xx"`, the SPI bus notifier path, ADS7846 platform data, and board-specific GPIO wiring.

## Risks and Test Signals
Risks include hard-coded SPI device name `"spi32766.1"`, permanent GPIO mapping, fragile GPIO offset/bit assumptions, and no notifier unregister path for init-only board code. Test signals are touchscreen probe receiving platform data, pendown interrupt/value correctness, generic MPC512x machine not matching AC14xx, and normal shared device population.
