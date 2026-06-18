<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-crag6410-module.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-crag6410-module.c

### Purpose
Implements plug-in Wolfson/Speyside module probing for the Cragganmore S3C6410 board. It reads module IDs from small I2C identification devices and registers the matching audio codec SPI/I2C devices plus GPIO lookup tables.

### Important APIs, Types, And Functions
The central data structure is `gf_mods[]`, mapping module `id`, `rev`, display name, optional I2C devices, SPI devices, and GPIO lookup table. `wlf_gf_module_probe()` reads byte 0 over SMBus, decodes `id` and `rev`, logs the detected module, registers child I2C clients with `i2c_new_client_device()`, registers SPI devices with `spi_register_board_info()`, and adds lookup tables. `wlf_gf_module_register()` installs the I2C driver only on S3C64xx via `device_initcall`.

### Control Flow
At device init, the driver binds to `"wlf-gf-module"` entries registered by the main Crag board file. Probe reads the module EEPROM/ID latch, searches `gf_mods[]`, pre-adds shared Arizona/WM8994 GPIO tables, then conditionally registers the module-specific devices. Unknown IDs are warned but not fatal.

### State, Persistence, And Dependencies
State is mostly static board data: codec platform data, regulator supply data, retune tables, SPI/I2C board-info arrays, and GPIO lookup tables. No persistent storage is modified. Dependencies include the I2C core, SPI board info, gpiod lookup tables, Wolfson MFD/audio platform-data headers, `soc_is_s3c64xx()`, and Crag IRQ/GPIO base definitions.

### Integration Points
The main Crag board registers multiple `"wlf-gf-module"` I2C devices on bus 1. This file expands those module IDs into codec devices such as WM0010, WM5100, WM8996, WM8994/WM8958, WM5102, WM5110, WM2200, and WM9081.

### Risks
The ID decode uses `(ret & 0xfe) >> 2`, so hardware encoding assumptions are critical. Some revisions use `.rev = -1` in a `u8` field, effectively matching 255 rather than a wildcard unless intended through conversion. GPIO lookup tables are globally registered and not removed on probe failure. Duplicate codec addresses on the same bus depend on only one physical module being present.

### Test Signals
Module insertion boot logs, I2C client creation, SPI device enumeration, codec probe success, IRQ routing through the PMIC GPIO IRQ base, and GPIO descriptor lookup by codec drivers are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-crag6410-module.c -->
