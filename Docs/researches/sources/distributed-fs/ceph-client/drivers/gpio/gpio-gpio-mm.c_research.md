
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-gpio-mm.c

Purpose: supports Diamond Systems GPIO-MM ISA boards by adapting two Intel 8255 PPIs through the shared `gpio-i8255` regmap helper.

Important APIs/types/functions: `gpiomm_probe()` requests the I/O port region, maps it, creates an I/O-port regmap, fills `struct i8255_regmap_config`, and calls `devm_i8255_regmap_register()`. Module parameter `base[]` supplies board I/O base addresses.

Control flow: the ISA driver is instantiated for each configured base address. Probe reserves eight I/O ports, maps them, creates an 8-bit flat-cache regmap with volatile ranges for both PPIs, sets parent, PPI count, and line names, then delegates GPIO registration to the i8255 helper.

State and persistence behavior: GPIO direction/value state is managed by the shared i8255 regmap layer and hardware. The local file maintains only module parameter arrays. Regcache is flat with volatile tables for PPI register windows.

Dependencies and integration points: depends on ISA driver infrastructure, I/O port access, regmap, and the `I8255` namespace/helper from `gpio-i8255.h`. It exposes 48 named GPIO lines across two PPIs.

Risks: no automatic hardware discovery exists; users must provide correct `base` parameters. I/O port conflicts reject probe. There is no IRQ or PM support. Incorrect base values can target unrelated legacy hardware.

Test signals: module parameter parsing for one or more base addresses, region conflict handling, 48 GPIO names, i8255 direction/value behavior across both PPIs, and namespace/build linkage to the i8255 helper.
