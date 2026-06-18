# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm186x-spi.c

Purpose: SPI bus glue for the TI PCM1862/PCM1863/PCM1864/PCM1865 ADC family. It does not implement codec policy itself; it binds OF/SPI IDs to `enum pcm186x_type`, creates a SPI regmap with `pcm186x_regmap`, and delegates initialization to `pcm186x_probe()`.

Important APIs and functions: `pcm186x_spi_probe()` uses `spi_get_device_id(spi)->driver_data`, `devm_regmap_init_spi()`, and `pcm186x_probe(&spi->dev, type, spi->irq, regmap)`. `pcm186x_of_match[]` and `pcm186x_spi_id[]` advertise all four compatible variants. `module_spi_driver()` registers the bus driver named `pcm186x`.

Control flow: kernel SPI matching calls probe; probe maps the SPI control plane into regmap; shared core probe owns supplies, reset, ASoC component registration, DAI, DAPM, and controls. There is no remove path because all allocations are devm-managed by the bus and core paths.

State and persistence: persistent state is only the SPI driver's match metadata and the shared core's `pcm186x_priv`. Register cache and power state live in `pcm186x.c`, not here.

Dependencies and integration points: depends on Linux SPI, regmap, module infrastructure, and `pcm186x.h`. It integrates with device tree compatibles `ti,pcm1862` through `ti,pcm1865` and with ALSA SoC through the shared probe.

Risks: probe assumes `spi_get_device_id()` is available for the matched device; OF-only instantiation relies on SPI core supplying a usable id. The `irq` argument is passed through but the core currently does not use it. Bus-specific failures are limited to regmap setup.

Test signals: compile with SPI support, instantiate each compatible, verify `devm_regmap_init_spi()` succeeds, and confirm the shared component exposes the expected PCM1863 two-channel or PCM1865 four-channel DAI/control set.
