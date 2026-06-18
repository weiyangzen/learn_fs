# sources/distributed-fs/ceph-client/drivers/mfd/wm831x-spi.c

`wm831x-spi.c` is the SPI frontend for WM831x PMICs. It matches supported devices, allocates shared core state, forces SPI mode 0, initializes SPI regmap access, copies platform data, and delegates to the WM831x core.

`wm831x_spi_probe()` obtains enum match data, allocates `struct wm831x`, sets `spi->mode = SPI_MODE_0`, stores driver data, initializes `devm_regmap_init_spi()` with `wm831x_regmap_config`, copies `wm831x_pdata`, and calls `wm831x_device_init(wm831x, spi->irq)`. PM wrappers call core suspend/shutdown helpers. `wm831x_spi_pm` wires freeze, suspend, and poweroff; `wm831x_spi_ids[]`, `wm831x_spi_driver`, and `wm831x_spi_init()` provide matching and registration.

Bus-local state is devres allocation, SPI driver data, and bus mode. Persistent PMIC state is established by the common core. Dependencies include SPI, regmap SPI support, OF match data, platform data, and WM831x core APIs.

Risks: `wm831x_spi_init()` logs registration failure but returns 0, hiding initcall failure; probe fails without match data; forcing mode 0 may override board assumptions. Test signals include SPI ID/OF matching, regmap allocation and child creation, freeze/suspend/poweroff callbacks, and forced registration-failure logging.
