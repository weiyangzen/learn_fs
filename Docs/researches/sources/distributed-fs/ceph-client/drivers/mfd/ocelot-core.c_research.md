# sources/distributed-fs/ceph-client/drivers/mfd/ocelot-core.c

Purpose: Bus-agnostic MFD core for externally controlled Microchip/MSCC Ocelot switch chips. It resets the chip, constructs per-resource regmaps for child register windows, and registers child devices for pinctrl, SGPIO, MIIM, SERDES, and switch functionality.

Important APIs, types, and functions: `ocelot_chip_reset()` writes the GCB soft reset bit and polls until it self-clears. Resource arrays describe VSC7512 register windows for MIIM, GPIO, SIO, HSIO, switch blocks, VCAPs, and ports. `vsc7512_devs[]` lists child cells with OF compatibles and resources. `ocelot_core_try_add_regmap()` creates a named regmap for a resource if one is not already registered. `ocelot_core_init()` ensures all child resource regmaps exist and calls `devm_mfd_add_devices()`.

Control flow: a bus front end such as SPI sets `struct ocelot_ddata` and core regmaps, resets/configures the chip, then calls `ocelot_core_init()`. Core init walks all child cell resources and asks the SPI helper to create regmaps named after each resource, then registers children.

State and persistence: `struct ocelot_ddata` lives in the bus front end and contains GCB/CPUORG regmaps used here. Reset writes hardware global state and can clear prior bus configuration. Child regmaps are devm-managed and attached to the parent device by name.

Dependencies and integration points: imports namespace `MFD_OCELOT_SPI` for `ocelot_spi_init_regmap()`, exports `ocelot_chip_reset()` and `ocelot_core_init()` under `MFD_OCELOT`, and integrates with the generic MFD core plus Ocelot SoC child drivers.

Risks: despite being described as bus-agnostic, `ocelot_core_try_add_regmap()` directly calls the SPI regmap initializer, so other buses need refactoring. Regmap creation failures are ignored in `ocelot_core_try_add_regmap()`, so child probe may fail later with less context. Test signals include reset timeout, child resource regmap name lookup, OF reg matching for MIIM0/MIIM1, switch resource coverage, and failure propagation when a regmap cannot be created.
