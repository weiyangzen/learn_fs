# sources/distributed-fs/ceph-client/drivers/w1/slaves/Kconfig

## Purpose
Kconfig menu for 1-Wire slave family drivers. It exposes selectable drivers for thermal sensors, ROM-only memory, switches, EEPROM/EPROM devices, counters, battery monitors, and the DS28E17 1-Wire-to-I2C bridge.

## Important APIs, Types, and Functions
This is configuration metadata, not C code. Important symbols include `W1_SLAVE_THERM`, `W1_SLAVE_SMEM`, `W1_SLAVE_DS2405`, `W1_SLAVE_DS2406`, `W1_SLAVE_DS2408`, `W1_SLAVE_DS2413`, `W1_SLAVE_DS2423`, EEPROM symbols for DS2805/DS2430/DS2431/DS2433/DS2438/DS250X/DS28E04, battery monitor symbols `W1_SLAVE_DS2780` and `W1_SLAVE_DS2781`, and `W1_SLAVE_DS28E17`. Feature toggles include `W1_SLAVE_DS2408_READBACK` and `W1_SLAVE_DS2433_CRC`.

## Control Flow
The menu participates in kernel configuration. Selected tristate options cause corresponding objects to be built in or as modules through the sibling Makefile. `select CRC16` pulls CRC support for devices that validate bus transfers. `depends on I2C` prevents DS28E17 from building without the I2C core.

## State and Persistence
Configuration selections persist in the kernel build configuration. They do not create runtime state by themselves, but determine which family IDs can bind to discovered slaves and which optional behavior is compiled in.

## Dependencies and Integration Points
Integrated with kbuild and the W1 core module auto-loading scheme via module aliases in the C files. Options map directly to `obj-$(CONFIG_...)` entries in `slaves/Makefile`.

## Risks and Test Signals
Missing `select CRC16` or dependency declarations would fail builds or runtime CRC validation. Test signals are successful allmodconfig/allyesconfig builds, expected modules present, and module autoload for family aliases when slaves are discovered.
