# sources/distributed-fs/ceph-client/drivers/mfd/rsmu_spi.c

### Purpose
`rsmu_spi.c` is the SPI bus glue for Renesas/IDT ClockMatrix and SABRE SMU devices. It implements shift-register-style SPI reads/writes, custom page-selection callbacks for the 7-bit offset window, creates a no-cache regmap, and registers common PHC/cdev children through `rsmu_core_init()`.

### Important APIs, Types, And Functions
Important functions are `rsmu_spi_probe()`, `rsmu_spi_remove()`, `rsmu_read_device()`, `rsmu_write_device()`, `rsmu_write_page_register()`, and regmap callbacks `rsmu_reg_read()` and `rsmu_reg_write()`. Static configs are `rsmu_cm_regmap_config` for 32-bit ClockMatrix addresses and `rsmu_sabre_regmap_config` for 16-bit SABRE addresses.

### Control Flow
Probe allocates `struct rsmu_ddata`, saves it as SPI drvdata, selects a config based on the SPI ID driver data, initializes a custom regmap with the SPI device as context, and calls `rsmu_core_init()`. Reads set the read bit in the first transmitted byte, send one dummy byte per requested byte, and copy received data after the first dummy response. Writes send register plus payload. Before every regmap access, `rsmu_write_page_register()` computes and writes the ClockMatrix or SABRE page selector unless the access does not require a page change or targets the SABRE page register itself.

### State, Persistence, And Dependencies
The bus state includes the cached `rsmu->page`; the core initializes the shared lock. Regmaps use no cache, so hardware is the source of truth. Persistent effects are page-register writes and target register writes. Dependencies include SPI synchronous transfer APIs, regmap custom buses, MFD core, OF/SPI ID matching, and RSMU headers.

### Integration Points
The SPI ID/OF tables cover ClockMatrix `8a34000`/`8a34001` and SABRE `82p33810`/`82p33811`. After the parent probes, `rsmu_core.c` creates the matching PHC and cdev children. Those children use the parent regmap and lock for device-specific timing functions.

### Risks
The page cache is not protected inside the low-level callback, so concurrent register access requires external serialization. SPI read/write helpers enforce max byte counts, but regmap callbacks only do one-byte accesses; future bulk operations would need careful limits. `rsmu_read_device()` relies on full-duplex dummy-byte behavior and copies `xfer.len - 1` bytes from the response; controller quirks could break this. Unsupported SnowLotus over SPI returns `-ENODEV`.

### Test Signals
SPI tests should read/write ClockMatrix and SABRE registers on different pages, verify no page write for SABRE page-register accesses, and validate dummy-byte handling with logic analyzer or mock SPI. Concurrent child access should be tested with PHC and cdev operations. Probe/remove tests should cover both supported types, unsupported type rejection, regmap allocation failures, and child creation failure.
