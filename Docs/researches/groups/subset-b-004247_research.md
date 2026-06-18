# subset-b-004247 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rohm-bd71828.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/rohm-bd71828.c

### Purpose
`rohm-bd71828.c` is the MFD parent driver for ROHM BD71815, BD71828, and BD72720 PMIC families. It selects chip-specific regmap, IRQ, clock, power-key, RTC, power-supply, regulator, GPIO, LED, and clock child devices from device-tree match data, then exposes those children through Linux MFD. It also handles the unusual BD72720 register topology, where one logical PMIC spans two I2C slave addresses.

### Important APIs, Types, And Functions
Key entry points are `bd71828_i2c_probe()`, `bd72720_do_regmaps()`, `set_clk_mode()`, `bd71828_power_off()`, and `bd72720_set_type_config()`. Static data includes `bd71815_mfd_cells[]`, `bd71828_mfd_cells[]`, `bd72720_mfd_cells[]`, `struct resource` IRQ arrays for power and RTC children, regmap configs for BD71815/BD71828/BD72720, and regmap IRQ chips `bd71815_irq_chip`, `bd71828_irq_chip`, and `bd72720_irq_chip`. `struct bd72720_regmaps` stores the real 0x4b and 0x4c regmaps behind the wrapper map.

### Control Flow
Probe requires an I2C IRQ, derives the ROHM chip type from `of_device_get_match_data()`, chooses the MFD cells, regmap config, IRQ chip, clock-mode register, and optional power-key IRQ, then creates a regmap. BD72720 takes the special path through `bd72720_do_regmaps()`, which creates a dummy secondary I2C client at address `0x4c`, initializes real cached regmaps for the 0x4b and 0x4c register banks, and returns an uncached wrapper regmap with custom read/write callbacks that unwrap addresses at `0x100` and above. Probe registers the regmap IRQ chip, optionally enables the BD72720 main IRQ mask, maps the power-key virtual IRQ into the shared `gpio_keys_button`, applies the optional `rohm,clkout-open-drain` clock output mode, adds MFD children, and for BD71828 system-power-controller nodes installs `pm_power_off`.

### State, Persistence, And Dependencies
Runtime state is mostly device-managed regmaps, IRQ chip data, MFD children, and the global `bd71828_dev`/`pm_power_off` hook. Persistent hardware effects include interrupt mask/unmask programming, output clock mode updates, and BD71828 hibernate-state writes during poweroff. Regmap cache state is maple-cached for direct maps; the BD72720 wrapper intentionally has no cache to avoid duplicating the real cached regmaps. Dependencies include I2C, regmap, regmap-irq, MFD core, gpio-keys, input event constants, OF matching, and ROHM chip register headers.

### Integration Points
Children consume named IRQ resources and the regmap exposed by the MFD parent: regulator/PMIC, power-supply, RTC, GPIO, LED, clock, and gpio-keys children all depend on this file's IRQ numbering and regmap topology. The regmap IRQ domain is passed to `devm_mfd_add_devices()` so child resources can resolve virtual IRQs. The BD72720 wrapper lets child drivers use one logical register address space while still reaching the charger registers on the secondary I2C address.

### Risks
The file relies on large static IRQ maps and sub-IRQ offset tables; wrong offsets silently route fault, charger, RTC, or power-button events to the wrong child. `button` is a static mutable object shared across probed instances, so multi-instance systems could overwrite `button.irq`. The BD72720 wrapper requires all secondary-bank register constants to include the `0x100` offset; direct access to the secondary real regmap with wrapped addresses would hit the wrong hardware register. The poweroff loop intentionally never returns and uses raw SMBus because regmap may sleep; failures only retry after `mdelay(500)`. Clock mode accepts only `0` or `1`, so binding mistakes fail probe.

### Test Signals
Useful tests include DT probe for all three compatibles with a valid IRQ, regmap read/write checks on BD72720 registers below and above `0x100`, IRQ delivery for RTC, power, charger, GPIO, and short-push events, and verification that `gpio-keys` receives the mapped power-button IRQ. Suspend/resume should exercise regcache behavior for volatile IRQ/status ranges. A BD71828 system-power-controller test should confirm `pm_power_off` writes hibernate state using SMBus. Bad DT tests should cover missing IRQ, invalid `rohm,clkout-open-drain`, unavailable secondary I2C address, and MFD child creation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rohm-bd71828.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rohm-bd718x7.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/rohm-bd718x7.c

### Purpose
`rohm-bd718x7.c` is the MFD parent driver for ROHM BD71837, BD71847, and BD71850-compatible PMICs. It creates chip-specific clock and regulator children plus a `gpio-keys` power-button child, and it centralizes one-byte regmap and IRQ setup for the BD718xx PMIC interrupt register.

### Important APIs, Types, And Functions
The main entry point is `bd718xx_i2c_probe()`, registered early through `subsys_initcall()` so power rails and clocks are available during boot. `bd718xx_init_press_duration()` parses optional `rohm,short-press-ms` and `rohm,long-press-ms` DT properties and programs `BD718XX_REG_PWRONCONFIG0/1`. Static data includes `bd71837_mfd_cells[]`, `bd71847_mfd_cells[]`, `bd718xx_irqs[]`, `bd718xx_irq_chip`, and `bd718xx_regmap_config`.

### Control Flow
Probe rejects devices without an IRQ, selects the BD71837 or BD71847 cell table from OF match data, initializes an 8-bit maple-cached I2C regmap, registers a one-register regmap IRQ chip over `BD718XX_REG_IRQ`, applies optional power-button duration configuration, maps `BD718XX_INT_PWRBTN_S` to a Linux virtual IRQ, stores it into the static `gpio_keys_button`, and adds MFD children using the regmap IRQ domain.

### State, Persistence, And Dependencies
Runtime state is device-managed regmap, regmap IRQ chip data, and child devices. Hardware persistence includes programmed power-button short/long press thresholds and interrupt mask/ack state. The regmap treats IRQ through power-state registers as volatile and caches the rest with `REGCACHE_MAPLE`. Dependencies include I2C, OF match data, regmap, regmap-irq, MFD core, gpio-keys/input, and `linux/mfd/rohm-bd718x7.h`.

### Integration Points
The clock and PMIC child names are chip-specific (`bd71837-clk`, `bd71847-clk`, `bd71837-pmic`, `bd71847-pmic`), while the power-key child is the generic `gpio-keys` device with platform data. Downstream regulator and clock drivers expect the parent regmap and IRQ domain to exist before they probe.

### Risks
The static mutable power-key button can be overwritten if multiple PMIC instances probe. Press-duration rounding is simple: short presses are rounded by `(ms + 250) / 500` and long presses by `(ms + 500) / 1000`, then capped at 15; DT values outside hardware expectations may be accepted but rounded. Missing IRQ aborts the whole driver. BD71850 is treated as BD71847-compatible, so any register or child difference must be handled elsewhere or added here.

### Test Signals
Probe tests should cover BD71837, BD71847, and BD71850 compatibles, IRQ chip registration, short and long power-button events through `gpio-keys`, and DT press-duration programming. Regmap tests should verify volatile handling for IRQ/status registers and cached reads elsewhere. Boot-order tests are valuable because the driver is registered with `subsys_initcall()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rohm-bd718x7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rohm-bd9576.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/rohm-bd9576.c

### Purpose
`rohm-bd9576.c` is the MFD parent driver for ROHM BD9576MUF and BD9573MUF PMICs. It creates regulator and watchdog child devices and conditionally exposes BD9576 regulator IRQ resources when a usable PMIC IRQ is present.

### Important APIs, Types, And Functions
The central function is `bd957x_i2c_probe()`. Static definitions include `bd9573_mfd_cells[]`, `bd9576_mfd_cells[]`, `bd9576_regulator_irqs[]`, volatile regmap ranges, `bd957x_regmap`, `bd9576_irqs[]`, and `bd9576_irq_chip`. The enum indexes the regulator and watchdog cells so resources can be attached to the regulator cell before MFD registration.

### Control Flow
Probe reads chip type from OF match data. BD9576 uses IRQs only if `i2c->irq` is populated; BD9573 always disables usable IRQs because its fatal IRQs cannot be serviced before SoC power loss. The driver initializes an 8-bit maple-cached regmap. If IRQs are usable, it attaches named thermal/overvoltage/undervoltage resources to the regulator cell, registers a one-register regmap IRQ chip, and passes its domain to MFD children. Otherwise it masks all main interrupts in hardware and registers children without an IRQ domain.

### State, Persistence, And Dependencies
Runtime state is device-managed regmap, optional regmap IRQ data, and MFD children. Persistent hardware state includes the interrupt mask register and any IRQ masking done by regmap-irq. Volatile regmap ranges cover SMRB assert, PMIC internal status, thermal status, OVP through system status, and main interrupt status. Dependencies are I2C, OF matching, regmap, regmap-irq, MFD core, and ROHM BD957x register definitions.

### Integration Points
The regulator child names differ by chip (`bd9573-regulator` or `bd9576-regulator`) and the watchdog child name is `bd9576-wdt` for both. Regulator notification behavior depends on whether this parent provides IRQ resources; without a valid IRQ, the child can still regulate but should omit interrupt-driven notifiers.

### Risks
The driver intentionally tolerates missing BD9576 IRQs because the PMIC can hold the IRQ line asserted for the whole fault condition. That avoids interrupt storms but loses notification coverage. BD9573 fatal IRQs are never exposed. If `bd9576_mfd_cells` is shared across instances, modifying the regulator cell resources during one probe can affect later probes. Masking all IRQs on the no-IRQ path must succeed or probe fails.

### Test Signals
Test BD9576 with and without a DT IRQ: with IRQ, regulator child resources should include thermal, OVD, and UVD IRQs; without IRQ, `BD957X_REG_INT_MAIN_MASK` should have all bits masked and child creation should still succeed. BD9573 tests should confirm no IRQ domain is exposed. Fault-injection should cover regmap init failure, IRQ chip add failure, and MFD add failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rohm-bd9576.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rohm-bd96801.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/rohm-bd96801.c

### Purpose
`rohm-bd96801.c` is the MFD parent for ROHM BD96801, BD96802, BD96805, and BD96806 scalable PMICs. It provides basic PMIC unlock, regmap setup, INTB/ERRB interrupt controller setup, watchdog and regulator child registration, and child IRQ resource mapping. The driver explicitly does not implement STBY-state safety-limit configuration because that requires system-specific coordination of PMIC state transitions.

### Important APIs, Types, And Functions
The main entry point is `bd96801_i2c_probe()`. `struct bd968xx` is the chip descriptor carrying INTB/ERRB resource arrays, regmap IRQ chips, regmap config, MFD cells, and unlock register/value. Static chip descriptors are `bd96801_data`, `bd96802_data`, `bd96805_data`, and `bd96806_data`. IRQ topology is represented by resource arrays, regmap IRQ arrays, sub-IRQ maps, and four IRQ chips: BD96801/BD96802 INTB and ERRB.

### Control Flow
Probe selects a descriptor from device match data, requires a firmware node and a named `intb` IRQ, optionally accepts a named `errb` IRQ unless it is deferred, allocates a combined regulator resource array sized to INTB plus optional ERRB resources, creates the I2C regmap, writes the PMIC unlock value, and registers the INTB regmap IRQ chip. Because MFD core only accepts one IRQ domain, the driver maps each child IRQ itself with `irq_create_mapping()` and stores concrete Linux IRQ numbers in the regulator resource array. It also maps the watchdog error IRQ from INTB and stores it in the watchdog cell. If ERRB exists, a second regmap IRQ chip/domain is registered and its events are appended to regulator resources. Finally, watchdog and regulator children are added without passing an IRQ domain.

### State, Persistence, And Dependencies
Runtime state is largely device-managed regmap, IRQ chip data, mapped IRQ resources, and child devices. Persistent hardware state includes the unlock register write and IRQ mask/ack programming. Regmap volatile tables deliberately include status registers and STBY-only configuration registers whose writes may not latch unless the PMIC is in standby; this reduces stale regcache risks. Dependencies include I2C, firmware-node named IRQs, regmap, regmap-irq, MFD core, IRQ domain mapping, and ROHM BD96801/BD96802 register headers.

### Integration Points
The watchdog child is `bd96801-wdt` or `bd96806-wdt`; regulator child names are chip-specific. Regulator children receive concrete IRQ resources from both INTB and optional ERRB lines, including regulator overcurrent, over/under-voltage, thermal warning, shutdown, and fatal fault resources. Systems that wire only INTB still get nonfatal regulator/thermal events; systems that wire ERRB get additional fatal fault reporting if the SoC remains alive.

### Risks
INTB and ERRB share the same main status register. The source comments call out that simultaneous INTB/ERRB assertions for different sub-status offsets could make regmap-irq read a sub-status register with no active bits and potentially return repeated `IRQ_NONE`. ERRB may be omitted on systems powered by the PMIC, so fatal fault observability can be absent by design. Several chip variants reuse descriptor data from BD96801 or BD96802; mismatched register maps or resources would break event routing. `bd96806_data` is non-const while the others are const, and static MFD cell resource mutation can be sensitive to multiple instances.

### Test Signals
Probe tests should cover all four compatibles, required `intb`, optional `errb`, ERRB `-EPROBE_DEFER`, unlock write failure, and MFD creation. IRQ tests should confirm INTB and ERRB resource mapping produces usable Linux IRQs for watchdog and regulator children, with BD96801/BD96805 seven-regulator maps and BD96802/BD96806 two-regulator maps. Regcache tests should verify volatile STBY-only and status ranges are not stale. Hardware tests should inject thermal, overcurrent, OVD/UVD, watchdog, and fatal ERRB events where safe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rohm-bd96801.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rsmu.h -->
## sources/distributed-fs/ceph-client/drivers/mfd/rsmu.h

### Purpose
`rsmu.h` is the private MFD header shared by the Renesas Synchronization Management Unit core and bus drivers. It declares the common core init/exit functions and defines the ClockMatrix SCSR base address used by bus-specific paged register access.

### Important APIs, Types, And Functions
The header includes the public `linux/mfd/rsmu.h`, defines `RSMU_CM_SCSR_BASE` as `0x20100000`, and declares `rsmu_core_init(struct rsmu_ddata *rsmu)` plus `rsmu_core_exit(struct rsmu_ddata *rsmu)`. It relies on `struct rsmu_ddata` and `enum rsmu_type` from the public header.

### Control Flow
There is no executable control flow. I2C and SPI bus drivers include this file so they can decide when ClockMatrix page registers must be changed and call the shared MFD child registration path after their regmap has been initialized.

### State, Persistence, And Dependencies
The header owns no state. `RSMU_CM_SCSR_BASE` influences persistent hardware register access by telling bus glue not to alter the page register for non-SCSR addresses. Dependencies are the public RSMU MFD header and include guards.

### Integration Points
This is the bridge between `rsmu_core.c`, `rsmu_i2c.c`, and `rsmu_spi.c`. Any change to the SCSR base or core function prototypes affects both bus drivers and all RSMU child devices registered by the core.

### Risks
An incorrect `RSMU_CM_SCSR_BASE` would make I2C/SPI page-selection code write page registers for the wrong address ranges or skip page writes for SCSR registers, causing silent register corruption or failed reads. Since the file only declares APIs, mismatch with public `struct rsmu_ddata` layout would surface at compile time in the bus/core files.

### Test Signals
Compile coverage across `rsmu_core.c`, `rsmu_i2c.c`, and `rsmu_spi.c` is the primary signal. Runtime tests should indirectly validate the base constant by reading and writing ClockMatrix registers below and above `0x20100000` over both I2C and SPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rsmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rsmu_core.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/rsmu_core.c

### Purpose
`rsmu_core.c` is the bus-independent MFD core for Renesas/IDT Synchronization Management Unit devices. It chooses PHC and character-device child names for ClockMatrix, SABRE, and SnowLotus style devices and registers those children once a bus driver has created the appropriate regmap.

### Important APIs, Types, And Functions
Exported functions are `rsmu_core_init()` and `rsmu_core_exit()`. Static cell tables are `rsmu_cm_devs[]` with `8a3400x-phc` and `8a3400x-cdev`, `rsmu_sabre_devs[]` with `82p33x1x-phc` and `82p33x1x-cdev`, and `rsmu_sl_devs[]` with `8v19n85x-phc` and `8v19n85x-cdev`.

### Control Flow
`rsmu_core_init()` switches on `rsmu->type`, selects the matching two-cell table, initializes `rsmu->lock`, and calls `devm_mfd_add_devices()` with two children. Unsupported device types return `-ENODEV`. `rsmu_core_exit()` destroys the mutex on bus-driver remove.

### State, Persistence, And Dependencies
The core initializes the shared `rsmu->lock`, but otherwise stores no private state. Child devices persist for the device-managed lifetime of the parent. Dependencies include MFD core, regmap through the public RSMU data, mutex support, and the bus drivers that populate `rsmu->dev`, `rsmu->type`, and `rsmu->regmap`.

### Integration Points
Both `rsmu_i2c.c` and `rsmu_spi.c` call `rsmu_core_init()` after regmap setup and `rsmu_core_exit()` on remove. The PHC and cdev children consume the parent `struct rsmu_ddata`, regmap, and lock to expose timing/clock synchronization functions.

### Risks
Child names are the binding between this core and downstream PHC/cdev drivers; renaming them breaks autoload/probe. The mutex is destroyed even though MFD children are device-managed, so remove ordering must ensure children are gone or quiesced before `rsmu_core_exit()` returns. Unsupported new RSMU types require adding a cell table here and bus match entries elsewhere.

### Test Signals
Probe tests should validate that each type creates exactly two children with expected names. Error tests should cover unsupported `rsmu->type` and `devm_mfd_add_devices()` failure. Remove/unbind tests should exercise mutex destruction after child teardown on both I2C and SPI parent paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rsmu_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rsmu_i2c.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/rsmu_i2c.c

### Purpose
`rsmu_i2c.c` is the I2C bus glue for Renesas/IDT SMU devices. It builds the right regmap for ClockMatrix, SABRE, or SnowLotus devices, implements custom paged register access for ClockMatrix over either full I2C or SMBus block operations, and then delegates child registration to `rsmu_core_init()`.

### Important APIs, Types, And Functions
Main functions are `rsmu_i2c_probe()`, `rsmu_i2c_remove()`, `rsmu_write_page_register()`, low-level I2C/SMBus block helpers, and custom regmap callbacks `rsmu_i2c_reg_read/write()` plus `rsmu_smbus_i2c_reg_read/write()`. Static configs include ClockMatrix full-I2C and SMBus regmaps, SABRE range-window regmap, and SnowLotus 16-bit big-endian regmap.

### Control Flow
Probe allocates `struct rsmu_ddata`, stores it as I2C client data, assigns device and type from the I2C ID table, selects a regmap config, initializes the regmap, and calls `rsmu_core_init()`. For ClockMatrix, it prefers full I2C transfer support and falls back to SMBus I2C block support; custom callbacks set the page register when the target register is in SCSR space, then access the low byte offset. For SABRE and SnowLotus, standard `devm_regmap_init_i2c()` is used with range or 16-bit register formatting.

### State, Persistence, And Dependencies
Runtime state includes `rsmu->page`, which caches the last selected ClockMatrix page, and `rsmu->lock` initialized by the core. ClockMatrix regmaps use `REGCACHE_NONE`; SABRE uses maple cache with all registers volatile except the page selector, and SnowLotus uses no cache. Dependencies include I2C/SMBus APIs, regmap, MFD core, OF/I2C ID tables, and the public/private RSMU headers.

### Integration Points
The I2C ID and OF tables cover `8a34000`, `8a34001`, `82p33810`, `82p33811`, `8v19n850`, and `8v19n851`. The core exposes PHC and char-device children after bus setup. Child drivers depend on correct bus-specific regmap behavior, especially for paged ClockMatrix SCSR registers.

### Risks
`rsmu_i2c_write_device()` does not verify that `i2c_master_send()` wrote `bytes + 1`, so partial positive sends are treated as success. The page cache is per parent and not guarded in the bus callback itself; correctness relies on higher-level locking by child users. Casting `(u8 *)val` for reads assumes one-byte values and host memory layout is acceptable for regmap's use here. Adapter capability selection can choose SMBus fallback with smaller transfer semantics, so bulk access limits need coverage.

### Test Signals
Test ClockMatrix reads/writes below and above `RSMU_CM_SCSR_BASE`, page transitions, repeated same-page accesses, and both full I2C and SMBus block paths. Test SABRE virtual range access across the 128-byte windows and SnowLotus 16-bit big-endian addressing. Fault tests should cover unsupported adapters, regmap init failures, partial transfers, and child registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rsmu_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rsmu_spi.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/rsmu_spi.c

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rsmu_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rt4831.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/rt4831.c

### Purpose
`rt4831.c` is the MFD core for the Richtek RT4831 display bias/backlight device. It optionally enables the chip with a GPIO, verifies the vendor ID, enables an I2C safety timer, creates backlight and regulator children, and disables outputs on remove.

### Important APIs, Types, And Functions
The main functions are `rt4831_probe()` and `rt4831_remove()`. Static data includes `rt4831_subdevs[]`, `rt4831_is_accessible_reg()`, and `rt4831_regmap_config`. Register constants cover revision, enable, and I2C protection registers; bit masks cover vendor ID, reset, and safety timer.

### Control Flow
Probe requests optional `"enable"` GPIO as output high, initializes an 8-bit I2C regmap limited to the accessible revision-through-I2CPROT range, reads `RT4831_REG_REVISION`, validates the low two vendor ID bits against Richtek ID `0x03`, sets the I2C safety timer bit, and adds backlight/regulator MFD children. Remove fetches the regmap and sets the enable reset bit to disable WLED and DSV outputs.

### State, Persistence, And Dependencies
Runtime state is device-managed GPIO, regmap, and child devices. Persistent hardware state includes the enabled safety timer and output reset bit on remove. There is no regcache configuration. Dependencies include I2C, GPIO descriptors, regmap, MFD core, OF matching, and Richtek child drivers.

### Integration Points
The backlight child uses OF compatible `richtek,rt4831-backlight`; the regulator child uses the MFD cell name `rt4831-regulator`. Both rely on the parent regmap. Boards may supply an enable GPIO that must be asserted before the revision register can be read.

### Risks
The vendor-ID mask only checks two bits, so it is a minimal identity check. If the enable GPIO is absent but hardware requires it, probe fails later at revision read. Remove assumes `dev_get_regmap()` succeeds and does not null-check the regmap. Setting the reset bit during remove may affect shared display rails if child teardown ordering or board design expects rails to remain on.

### Test Signals
Tests should cover probe with and without enable GPIO, correct vendor ID, mismatched vendor ID, safety timer bit programming, and child creation. Remove should be tested to confirm WLED/DSV outputs are disabled and failures log a warning. Regmap access tests should verify inaccessible addresses are rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rt4831.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rt5033.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/rt5033.c

### Purpose
`rt5033.c` is the MFD core for the Richtek RT5033 PMIC. It creates regulator, charger, and LED children, exposes PMIC interrupt events through regmap-irq, and enables device wakeup support.

### Important APIs, Types, And Functions
The main function is `rt5033_i2c_probe()`. Static data includes `rt5033_irqs[]`, `rt5033_irq_chip`, `rt5033_devs[]`, and `rt5033_regmap_config`. It allocates and stores `struct rt5033_dev`, which contains the device, IRQ, wakeup flag, regmap, and IRQ chip data.

### Control Flow
Probe allocates parent state, stores I2C client data, records `i2c->irq`, creates an 8-bit regmap, reads `RT5033_REG_DEVICE_ID`, logs the chip revision, registers a falling-edge one-shot regmap IRQ chip, adds regulator/charger/LED children using the regmap IRQ domain, and initializes wakeup if `rt5033->wakeup` is true.

### State, Persistence, And Dependencies
Runtime state is `struct rt5033_dev`, regmap, regmap IRQ data, MFD children, and wakeup capability. Persistent hardware effects are IRQ masking/ack state configured by regmap-irq. Dependencies include I2C, regmap, regmap-irq, MFD core, device wakeup, and RT5033 public/private headers.

### Integration Points
Child devices are `rt5033-regulator`, `rt5033-charger` with compatible `richtek,rt5033-charger`, and `rt5033-led` with compatible `richtek,rt5033-led`. The IRQ domain gives children access to PMIC events such as buck overcurrent, low voltage, LDO low voltage, overtemperature, and VDDA undervoltage.

### Risks
The driver does not reject missing `i2c->irq` before calling `devm_regmap_add_irq_chip()`, so a zero IRQ path depends on regmap-irq behavior and platform data correctness. The chip ID read only logs revision; it does not validate a model ID. Wakeup is hardcoded true rather than parsed. Any mismatch in private header masks affects child IRQ delivery.

### Test Signals
Probe tests should verify device ID read, regmap IRQ registration, child creation, and wakeup initialization. IRQ tests should trigger each PMIC interrupt bit and confirm child-visible virqs. Fault tests should cover missing/invalid IRQ, regmap init failure, device ID read failure, IRQ chip failure, and MFD add failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rt5033.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rt5120.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/rt5120.c

### Purpose
`rt5120.c` is the MFD core for the Richtek RT5120 PMIC. It exposes regulator and power-key children and routes hot-die and power-key press/release interrupts through a one-register regmap IRQ chip.

### Important APIs, Types, And Functions
The main function is `rt5120_probe()`. Static data includes readable and writable regmap access tables, `rt5120_regmap_config`, `rt5120_irqs[]`, `rt5120_irq_chip`, child resource arrays, and `rt5120_devs[]`.

### Control Flow
Probe initializes an I2C regmap constrained by explicit readable/writable ranges, registers a regmap IRQ chip using `i2c->irq`, and creates two MFD children. The regulator child gets the hot-die IRQ resource. The power-key child uses OF compatible `richtek,rt5120-pwrkey` and receives named press and release IRQ resources. The IRQ chip uses status, unmask, and ack registers with `use_ack = true`.

### State, Persistence, And Dependencies
Runtime state is device-managed regmap, IRQ data, and child devices. Persistent hardware effects are interrupt mask/ack updates. There is no regcache. Dependencies include I2C, regmap, regmap-irq, MFD core, OF matching, and Richtek child drivers.

### Integration Points
The parent IRQ domain maps `RT5120_INT_HOTDIE`, `RT5120_INT_PWRKEY_PRESS`, and `RT5120_INT_PWRKEY_REL` into resources for regulator and pwrkey children. Regmap access restrictions protect undefined register ranges while allowing interrupt, regulator/control, and FZC mode registers.

### Risks
Probe does not explicitly validate that `i2c->irq` is nonzero. The access tables are narrow, so a future child needing a register outside listed ranges will fail regmap access until this file is updated. The IRQ definitions use `REGMAP_IRQ_REG_LINE(..., 8)`, so incorrect bit-line assumptions would break event routing.

### Test Signals
Tests should cover regmap access permission boundaries, IRQ registration, hot-die event delivery to regulator, power-key press/release delivery to the pwrkey child, and probe behavior with missing IRQ. Fault injection should cover regmap init, IRQ chip add, and MFD add failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rt5120.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rz-mtu3.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/rz-mtu3.c

### Purpose
`rz-mtu3.c` is the MFD parent and shared register-access layer for the Renesas RZ/G2L MTU3a multi-function timer. It maps timer MMIO, controls reset and clock references, initializes per-channel metadata, exports register read/write/start/stop helpers for child drivers, and creates counter and PWM children.

### Important APIs, Types, And Functions
Exported APIs include `rz_mtu3_shared_reg_read/write/update_bit()`, `rz_mtu3_8bit_ch_read/write()`, `rz_mtu3_16bit_ch_read/write()`, `rz_mtu3_32bit_ch_read/write()`, `rz_mtu3_is_enabled()`, `rz_mtu3_enable()`, and `rz_mtu3_disable()`. Static helpers map channel/register enum offsets to physical MMIO offsets and compute timer start-register offsets and bit positions. `struct rz_mtu3_priv` stores `mmio`, reset control, and a spinlock.

### Control Flow
Probe allocates public and private state, maps MMIO resource 0, gets an exclusive reset control and clock, deasserts reset, initializes the spinlock and nine channel locks/metadata entries, and adds `rz-mtu3-counter` and `pwm-rz-mtu3` children. A device-managed cleanup action removes children and asserts reset. Exported channel read/write helpers look up the channel-specific offset table and issue `readb/readw/readl` or `writeb/writew/writel`. Start/stop and shared bit-update paths lock around shared registers, modify the correct bit, and write back.

### State, Persistence, And Dependencies
Runtime state is MMIO mapping, reset state, clock handle, shared spinlock, per-channel locks, busy flags, and child devices. Hardware persistence is all MTU3 register programming by children and start/stop bits in shared timer start registers. Dependencies include platform device resources, reset, clock, MFD core, spinlocks, bit operations, MMIO accessors, and public `linux/mfd/rz-mtu3.h` definitions.

### Integration Points
The counter and PWM child drivers use exported helpers and `struct rz_mtu3_channel` objects from parent drvdata. The parent abstracts nonuniform channel register layouts: channel 8 lacks 16-bit registers, only channels 1 and 8 have 32-bit register tables, and shared start registers differ by channel group.

### Risks
Offset arrays are indexed by enum offsets from the public header; a mismatch between public enum values and private array dimensions would yield wrong MMIO addresses. Some helpers return zero or do nothing for unsupported channel widths instead of failing, which can hide misuse by children. Shared register updates are protected by a spinlock, but raw channel register access is not globally serialized. Cleanup asserts reset only through the devm action after child removal; failures before action registration must assert reset through the error path.

### Test Signals
Tests should validate probe/reset sequencing, child creation, and cleanup reset assertion. Register-access tests should sample every channel's 8-bit offsets, valid 16-bit channels, valid 32-bit channels 1 and 8, and unsupported-width behavior. PWM/counter integration tests should verify start/stop bits for channel groups 0-4/8, 5, and 6-7, plus concurrent shared register bit updates under interrupt-disabled spinlock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rz-mtu3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rz-mtu3.h -->
## sources/distributed-fs/ceph-client/drivers/mfd/rz-mtu3.h

### Purpose
`rz-mtu3.h` is the private macro table header used by the RZ/G2L MTU3 MFD parent to define channel-specific register offset arrays. It encodes the irregular 8-bit, 16-bit, and 32-bit register layouts for MTU channels without duplicating index assignments in the C file.

### Important APIs, Types, And Functions
The header defines initializer macros `MTU_8BIT_CH_0`, `MTU_8BIT_CH_1_2`, `MTU_8BIT_CH_3_4_6_7`, `MTU_8BIT_CH_5`, `MTU_8BIT_CH_8`, `MTU_16BIT_CH_0`, `MTU_16BIT_CH_1_2`, `MTU_16BIT_CH_3_6`, `MTU_16BIT_CH_4_7`, `MTU_16BIT_CH_5`, `MTU_32BIT_CH_1`, and `MTU_32BIT_CH_8`. Each macro assigns supplied physical offsets to indices named by public `RZ_MTU3_*` register enums.

### Control Flow
There is no runtime control flow. The macros expand at compile time into sparse-ish initializer lists for `rz_mtu3_8bit_ch_reg_offs`, `rz_mtu3_16bit_ch_reg_offs`, and `rz_mtu3_32bit_ch_reg_offs` in `rz-mtu3.c`.

### State, Persistence, And Dependencies
The header owns no state. Its values become persistent compiled-in mapping data used for all child MMIO accesses. It depends on the public `RZ_MTU3_*` enum/index definitions already visible to the including C file.

### Integration Points
This file is tightly coupled to `rz-mtu3.c` and the public `linux/mfd/rz-mtu3.h` register-index enums. Counter and PWM child behavior indirectly depends on these macros because every exported parent read/write helper resolves logical registers through arrays initialized with them.

### Risks
Any enum-index drift, missing initializer, or wrong offset argument causes silent access to the wrong timer register. The macros do not perform bounds checking, and unsupported registers default to zero-filled entries if accessed incorrectly. Formatting has trailing backslashes on some macro definitions, so edits should be checked carefully by compilation.

### Test Signals
Build tests catch syntax and missing enum names. Runtime tests should compare logical register accesses against the hardware manual for each channel family, especially channels 5 and 8 with distinct layouts, channels 4/7 with ADC trigger registers, and the 32-bit-only mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/rz-mtu3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/sec-acpm.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/sec-acpm.c

### Purpose
`sec-acpm.c` is the Samsung S2MPG10/S2MPG11 PMIC bus driver for systems where PMIC register access goes through Exynos ACPM firmware instead of direct I2C. It builds firmware-backed regmaps for common, PMIC, RTC, and meter access types, then calls the shared Samsung SEC PMIC MFD core.

### Important APIs, Types, And Functions
Key functions are `sec_pmic_acpm_probe()`, `sec_pmic_acpm_shutdown()`, `sec_pmic_acpm_regmap_init()`, and regmap bus callbacks `sec_pmic_acpm_bus_write()`, `sec_pmic_acpm_bus_read()`, and `sec_pmic_acpm_bus_reg_update_bits()`. `struct sec_pmic_acpm_platform_data` identifies the device type, ACPM channel, Speedy channel, and regmap configs. The file defines detailed regmap access tables for S2MPG10 and S2MPG11 common, PMIC, RTC, and meter register spaces.

### Control Flow
Probe reads platform data from OF match, obtains the ACPM handle from the parent node, gets platform IRQ 0, allocates a shared bus context, and initializes the common regmap with device attachment. It then creates the PMIC regmap without attachment, optional RTC regmap, and meter regmap. Each regmap uses the custom ACPM regmap bus; reads/writes validate register/value lengths and call ACPM PMIC operations with the configured access type and Speedy channel. Finally, probe calls `sec_pmic_probe()` with the PMIC regmap and IRQ and optionally initializes wakeup if `wakeup-source` is present.

### State, Persistence, And Dependencies
Runtime state includes ACPM handle, channel IDs, Speedy channel, small bus contexts, regmap caches, SEC PMIC core state, and optional wakeup state. Persistent effects are all PMIC register writes routed through ACPM and interrupt/wakeup configuration in the core. Regmaps use `REGCACHE_FLAT` and carefully mark interrupt registers precious, read-only data, nonvolatile masks, volatile meter data, and RTC time/update fields. Dependencies include Exynos ACPM protocol, platform devices, regmap custom bus, MFD SEC core, Samsung S2MPG headers, device properties, and PM ops exported by `sec-common.c`.

### Integration Points
The common regmap is later found by `sec-irq.c` as `"common"` for S2MPG chained interrupt setup. The PMIC regmap is passed to the shared MFD core. The RTC and meter regmaps are attached by name for child drivers. S2MPG10 registers an RTC child through the core; S2MPG11 omits RTC config and child support in this driver.

### Risks
ACPM bulk transfer size is capped at eight data bytes, so callers requiring larger raw transfers must split them. The PMIC regmap is not attached to the device by name, which is intentional for core passing but may surprise code expecting `dev_get_regmap(dev, "pmic")`. Correctness depends on ACPM firmware implementing `bulk_read`, `bulk_write`, and `update_reg` semantics. Access-table mistakes can block valid child accesses or cache volatile firmware-backed status. Missing parent ACPM node or IRQ aborts probe.

### Test Signals
Tests should cover S2MPG10 and S2MPG11 probe, ACPM handle deferral/failure, common/RTC/meter named regmap lookup, PMIC core child creation, chained S2MPG IRQ setup, and wakeup-source behavior. Regmap tests should validate read/write/readonly/precious/volatile policy and raw transfer size limits. Firmware-integration tests should compare ACPM register reads/writes against expected PMIC state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/sec-acpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/sec-common.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/sec-common.c

### Purpose
`sec-common.c` is the shared Samsung SEC/S5M/S2M PMIC MFD core. It parses common DT properties, initializes IRQ handling, selects child MFD cells for each supported PMIC family, applies small device-specific configuration, exposes shutdown handling, and exports suspend/resume PM operations.

### Important APIs, Types, And Functions
Exported APIs are `sec_pmic_probe()`, `sec_pmic_shutdown()`, and `sec_pmic_pm_ops`. Static helpers include `sec_pmic_parse_dt_pdata()`, `sec_pmic_configure()`, `sec_pmic_dump_rev()`, `sec_pmic_suspend()`, and `sec_pmic_resume()`. Static MFD cell tables cover S5M8767, S2DOS05, S2MPA01, S2MPG10, S2MPG11, S2MPS11/13/14/15, and S2MPU02/05, including RTC, clock, GPIO, meter, and regulator children where supported.

### Control Flow
`sec_pmic_probe()` allocates `struct sec_pmic_dev`, stores device type, client, IRQ, and PMIC regmap, parses common DT flags, calls `sec_irq_init()`, marks runtime PM active, selects a child-cell table by device type, and adds MFD children using the regmap IRQ domain. It then applies S2MPS13 WRSTBI disable configuration if requested and dumps revision for direct-register PMICs. Shutdown checks `manual_poweroff` and, currently only for S2MPS11, clears PWRHOLD. Suspend optionally enables IRQ wake and disables the PMIC IRQ so RTC alarm handling does not race a suspended I2C controller; resume reverses that.

### State, Persistence, And Dependencies
Runtime state is `struct sec_pmic_dev`, parsed `struct sec_platform_data`, IRQ chip data, child devices, PM runtime active state, and wake IRQ status. Persistent hardware effects include optional S2MPS13 WRSTBI configuration and S2MPS11 PWRHOLD clearing on shutdown. Dependencies include regmap, MFD core, Samsung core/irq/PMIC headers, OF properties, runtime PM, and `sec_irq_init()` from `sec-irq.c`.

### Integration Points
`sec-i2c.c` and `sec-acpm.c` both call `sec_pmic_probe()` after creating a bus-specific PMIC regmap. `sec-irq.c` supplies the IRQ domain consumed by RTC/regulator/clock/GPIO children. The PM ops are used by both direct I2C and ACPM platform drivers.

### Risks
`sec_irq_init()` may return NULL for devices without IRQ support, but `sec_pmic_probe()` unconditionally calls `regmap_irq_get_domain(irq_data)`, so devices like S2DOS05 or no-IRQ configurations depend on regmap helper behavior or may be fragile. Suspend always disables `sec_pmic->irq`; if the IRQ is zero or already disabled, platform behavior needs care. Manual poweroff only supports S2MPS11 despite parsing the property generically. Child table names include shared historical names such as `s2mps14-rtc`, so renaming would affect child binding.

### Test Signals
Tests should probe every supported device type through both direct and ACPM paths where applicable, verifying selected children and IRQ domain behavior. DT tests should cover `samsung,s2mps11-acokb-ground` and `samsung,s2mps11-wrstbi-ground`. Suspend/resume tests should verify RTC alarm wake with I2C suspended. Shutdown tests should confirm S2MPS11 PWRHOLD clearing and warnings for unsupported manual poweroff devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/sec-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/sec-core.h -->
## sources/distributed-fs/ceph-client/drivers/mfd/sec-core.h

### Purpose
`sec-core.h` is the private header joining the Samsung SEC PMIC bus drivers, shared core, and IRQ implementation. It declares the shared probe/shutdown/IRQ APIs and PM ops used across direct I2C and ACPM-backed variants.

### Important APIs, Types, And Functions
The header forward-declares `struct i2c_client`, declares `extern const struct dev_pm_ops sec_pmic_pm_ops`, `sec_pmic_probe()`, `sec_pmic_shutdown()`, and `sec_irq_init()`. It references `struct sec_pmic_dev`, `struct device`, and `struct regmap` through included translation-unit context rather than including all type headers itself.

### Control Flow
There is no runtime control flow. Bus drivers include this header to invoke the common core and shutdown paths; the common core includes it to call `sec_irq_init()`; the IRQ file includes it to expose that implementation.

### State, Persistence, And Dependencies
The header owns no state. Its declarations define the linkage contract for shared SEC PMIC runtime state managed in `struct sec_pmic_dev`. Dependencies are compile-time type declarations from the including files and the Samsung public core header.

### Integration Points
`sec-i2c.c` and `sec-acpm.c` consume `sec_pmic_pm_ops`, `sec_pmic_probe()`, and `sec_pmic_shutdown()`. `sec-common.c` consumes `sec_irq_init()`. `sec-irq.c` implements the IRQ initializer declared here.

### Risks
Because this is a private API boundary, signature changes require synchronized edits in all SEC MFD files. Minimal includes keep it light but mean include ordering matters; missing type definitions in a new user could cause compile errors.

### Test Signals
Compile tests across `sec-i2c.c`, `sec-acpm.c`, `sec-common.c`, and `sec-irq.c` are the main validation. Runtime signals are indirect: successful probe, IRQ setup, PM suspend/resume, and shutdown through both bus paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/sec-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/sec-i2c.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/sec-i2c.c

### Purpose
`sec-i2c.c` is the direct I2C bus driver for Samsung SEC/S5M/S2M PMICs. It selects a device-specific regmap configuration from OF match data, initializes the PMIC regmap over I2C, and delegates common MFD, IRQ, child, PM, and shutdown behavior to `sec-common.c`.

### Important APIs, Types, And Functions
The main functions are `sec_pmic_i2c_probe()` and `sec_pmic_i2c_shutdown()`. `struct sec_pmic_i2c_platform_data` carries a regmap config and SEC device type. Volatile helpers `s2mpa01_volatile()`, `s2mps11_volatile()`, and `s2mpu02_volatile()` keep interrupt mask registers cacheable while treating most other registers as volatile. Static platform data entries cover S2DOS05, S2MPA01, S2MPS11/13/14/15, S2MPU02/05, and S5M8767.

### Control Flow
Probe gets match data, initializes an I2C regmap using the matched config, and calls `sec_pmic_probe()` with the device type, `client->irq`, PMIC regmap, and I2C client pointer. Shutdown calls the shared `sec_pmic_shutdown()`. The I2C driver uses shared sleep PM ops from `sec_pmic_pm_ops`.

### State, Persistence, And Dependencies
Runtime state is managed by the common core after probe; this file owns only the device-managed regmap initialization path. Persistent hardware effects are performed by the common core and child drivers. Regmap configs use `REGCACHE_FLAT` for most larger PMICs, with interrupt mask registers considered nonvolatile/cacheable and most status/control registers volatile. Dependencies include I2C, regmap, device match data, Samsung PMIC headers, and `sec-core.h`.

### Integration Points
This file is the direct-register counterpart to `sec-acpm.c`. It maps OF compatibles to common SEC device types consumed by `sec_pmic_probe()` and `sec_irq_init()`. Child drivers use the PMIC regmap and IRQ domain set up by the shared core.

### Risks
Devices with simple configs such as S2DOS05 and S2MPU05 have no explicit max register or volatile policy here, so child behavior depends on default regmap semantics. Missing or zero `client->irq` is passed through to common IRQ setup, which warns for most devices but may interact poorly with unconditional IRQ-domain use in the core. Volatile helper reuse across S2MPS13/14/15 assumes compatible interrupt-mask layouts.

### Test Signals
Probe tests should cover every OF compatible, regmap init failure, shared core failure, and shutdown. Regcache tests should verify interrupt mask registers remain cacheable while interrupt/status reads are fresh. Suspend/resume tests should use the shared PM ops with RTC alarm wake on direct I2C systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/sec-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/sec-irq.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/sec-irq.c

### Purpose
`sec-irq.c` defines the regmap IRQ topology for Samsung SEC/S5M/S2M PMIC families and exports `sec_irq_init()` for the shared core. It supports classic single PMIC IRQ chips and the newer S2MPG1x two-stage common-to-PMIC chained IRQ design.

### Important APIs, Types, And Functions
The exported entry point is `sec_irq_init(struct sec_pmic_dev *sec_pmic)`. S2MPG-specific helpers are `sec_irq_init_s2mpg1x()` and `s2mpg1x_add_chained_pmic()`. Static data includes regmap IRQ arrays for S2MPG10/11 common and PMIC events, S2MPS11/14-style events, S2MPU02/05, and S5M8767, plus corresponding `struct regmap_irq_chip` definitions.

### Control Flow
For S2MPG10/11, `sec_irq_init()` delegates to `sec_irq_init_s2mpg1x()`, which obtains the named `"common"` regmap, registers a one-register common IRQ chip on the parent IRQ, maps the PMIC-source parent virq, and registers a second PMIC regmap IRQ chip on that virq with `IRQF_SHARED`. For classic devices, `sec_irq_init()` chooses a single regmap IRQ chip by device type and registers it against `sec_pmic->regmap_pmic` and `sec_pmic->irq`. S2DOS05 returns NULL because it has no interrupt setup here; missing IRQs also return NULL after warning.

### State, Persistence, And Dependencies
Runtime state is regmap IRQ chip data and generated IRQ domains. Persistent hardware state includes interrupt masks and acknowledgements managed by regmap-irq. Dependencies include regmap-irq, Samsung PMIC register headers, `struct sec_pmic_dev`, and the common regmap created by `sec-acpm.c` for S2MPG devices.

### Integration Points
`sec-common.c` calls `sec_irq_init()` during parent probe and passes the resulting IRQ domain to MFD children. S2MPG10/11 meter/regulator/RTC/GPIO children rely on the chained PMIC domain, while classic S2MPS/S2MPU/S5M children use direct PMIC IRQ domains.

### Risks
Returning NULL for S2DOS05 or missing IRQs requires callers to avoid blindly dereferencing IRQ data; the current common code's IRQ-domain handling should be scrutinized. S2MPG chained setup depends on the `"common"` regmap being attached before `sec_pmic_probe()`. Large hand-written IRQ tables can drift from datasheets. Some S2MPS-family chips share the S2MPS14 IRQ table through a macro, which assumes compatible bit assignments.

### Test Signals
Tests should validate classic IRQ delivery for S5M8767, S2MPS11/13/14/15, S2MPA01, S2MPU02, and S2MPU05, plus no-IRQ behavior. S2MPG tests should verify the common IRQ source maps to the chained PMIC chip and that PMIC child events are delivered from the second domain. Fault tests should cover missing `"common"` regmap, parent virq mapping failure, and regmap IRQ add failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/sec-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/si476x-cmd.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/si476x-cmd.c

### Purpose
`si476x-cmd.c` implements the command protocol for Silicon Labs Si476x AM/FM tuner chips. It serializes command bytes over the core I2C transfer primitive, waits for command-complete and tune-complete signals maintained by the I2C core, parses responses into typed reports, and exports command helpers used by radio/audio child drivers and the MFD core.

### Important APIs, Types, And Functions
The key internal engine is `si476x_core_send_command()`, with helpers `si476x_core_parse_and_nag_about_error()`, `si476x_cmd_tune_seek_freq()`, and `si476x_cmd_clear_stc()`. Exported APIs include property get/set, pinmux commands, power up/down, AM/FM tune and seek, AM/FM RSQ status, ACF status, FM RDS status/blockcount, phase diversity, AGC status, and FUNC_INFO. A revision vtable selects A10, A20, or A30 implementations for commands with firmware-specific argument/response layouts.

### Control Flow
Each command helper builds an argument byte array, calls `si476x_core_send_command()`, and optionally parses response bytes. The send path validates argument count, sends command plus arguments through `si476x_core_i2c_xfer()`, clears CTS after the write, waits on `core->command` for CTS, performs an extra POWER_UP wait in polling mode, reads the response, checks the device error bit, optionally fetches an extended error code, and returns success only if CTS is set. Tune/seek helpers clear STC, send the command with tune timeout, wait on `core->tuning`, then acknowledge STC through RSQ status.

### State, Persistence, And Dependencies
This file owns no long-lived state but mutates `core->cts` and `core->stc` through command flow and writes persistent tuner properties, pinmux, power, tune, seek, and diversity settings. Dependencies include wait queues and atomics from the core, I2C transfer exported by `si476x-i2c.c`, unaligned big-endian helpers, V4L2 RDS block constants, Si476x public structures/enums, and firmware revision stored in `core->revision`.

### Integration Points
`si476x-i2c.c` uses power and FUNC_INFO commands during startup and revision detection, and uses RDS/status commands in interrupt and worker paths. Radio child drivers use exported tune, seek, status, RDS, AGC, ACF, property, and diversity helpers. Codec support depends on pinmux configuration commands issued by the core startup path.

### Risks
The exported revision-dispatch functions use `BUG_ON()` if `core->revision` is unset or above A30, so bad revision detection can crash the kernel rather than returning an error. `si476x_core_cmd_func_info()` fills the output structure even if the command failed, using response buffer contents. `argn > CMD_MAX_ARGS_COUNT` returns `-ENOMEM` even though the condition is an argument-size error. Wait timeouts only warn; the code still reads a response and may then fail later. Large response parsers are hand-coded and susceptible to byte-offset mistakes.

### Test Signals
Tests should mock I2C transfers for each command revision path, including error-bit responses and extended error codes. Hardware tests should cover power up/down on A10/A20/A30 firmware, FM/AM tune and seek STC handling, property read/write, pinmux commands, RDS FIFO reads, AGC/RSQ/ACF parsing, and phase diversity status. Negative tests should cover timeout, short I2C send/receive, busy/error codes, null report arguments, and unsupported revisions before vtable dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/si476x-cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/si476x-i2c.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/si476x-i2c.c

### Purpose
`si476x-i2c.c` is the MFD core and I2C transport driver for Si4761/Si4764/Si4768 tuner devices. It owns power sequencing, regulator and reset control, IRQ or polling status handling, RDS FIFO draining, revision detection, feature predicates, and registration of radio and optional codec children.

### Important APIs, Types, And Functions
Exported APIs include `si476x_core_start()`, `si476x_core_stop()`, `si476x_core_set_power_state()`, `si476x_core_i2c_xfer()`, feature predicates such as `si476x_core_has_am()`, and `si476x_core_is_powered_up()`. Internal functions include `si476x_core_config_pinmux()`, RDS drainer helpers, `si476x_core_pronounce_dead()`, status polling/IRQ handlers, firmware revision mapping, `si476x_core_get_revision_info()`, probe, and remove.

### Control Flow
Probe allocates `struct si476x_core`, initializes a Si476x regmap, requires platform data, requests optional reset GPIO, gets four regulators, initializes locks, wait queues, FIFO, RDS worker, IRQ or polling mode, and chip ID. It powers the device up temporarily to issue FUNC_INFO and map firmware major/function to A10/A20/A30 revision, powers it back down, then creates the `si476x-radio` child and optional `si476x-codec` child when ALSA support and pinmux conditions match. Runtime power-up enables regulators, asserts reset high, enables IRQ or polling, sends POWER_UP, configures pinmux, and enables tuner interrupt sources. Runtime stop clears alive state, optionally sends POWER_DOWN, disables IRQ/polling, and may assert reset low.

### State, Persistence, And Dependencies
Runtime state includes power state, alive/CTS/STC atomics, command and tuning wait queues, command lock, regulator array, reset GPIO, revision, chip ID, platform power/pinmux/diversity parameters, RDS FIFO and worker state, optional delayed polling work, and MFD cells. Persistent hardware effects include power state, pinmux, interrupt enables, tuner mode/frequency/properties via command helpers, and reset state. Dependencies include I2C, regulator bulk APIs, legacy GPIO APIs, regmap helper `devm_regmap_init_si476x()`, kfifo, workqueues, wait queues, MFD core, Si476x command exports, and platform data.

### Integration Points
`si476x-cmd.c` depends on `si476x_core_i2c_xfer()` and the CTS/STC signaling set by this file. The radio child consumes RDS FIFO, tune/status commands, and power-state helpers. Optional codec child creation depends on chip ID and digital-audio pinmux. Systems can run either interrupt-driven mode or polling mode when no IRQ is supplied.

### Risks
The driver requires platform data and has no OF-property parsing in this file. `si476x_core_i2c_xfer()` uses a static `io_errors_count`, so I/O error accounting is shared across all device instances. IRQ/polling startup has delicate ordering around CTS clearing and POWER_UP; polling mode has an explicit workaround for a false first CTS. Remove disables IRQ after `si476x_core_pronounce_dead()`, which wakes waiters, but active child operations still require correct teardown ordering. GPIO uses legacy request/free APIs. If revision detection fails, probe returns `-ENODEV`.

### Test Signals
Tests should cover probe with valid and missing platform data, IRQ and polling modes, regulator failures, reset GPIO paths, revision detection for FM/AM/WB firmware majors, and child creation with/without codec pinmux. Runtime tests should validate power-state transitions, command wait wakeups, RDS drainer FIFO behavior and wakeups, device-dead behavior after repeated I2C errors, and clean remove. Hardware tests should exercise Si4761/Si4764/Si4768 feature predicates, AM availability, diversity mode, and IRQ-source configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/si476x-i2c.c -->
