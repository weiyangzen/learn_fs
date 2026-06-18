# Research Report: subset-b-004245

This grouped report covers Linux MFD driver sources under `sources/distributed-fs/ceph-client/drivers/mfd/`. Each section is delimited for deterministic splitting into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max8925-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/max8925-core.c

Purpose: Core MFD support for the Maxim MAX8925 PMIC. It defines child devices for RTC, onkey, regulators, backlight, power supply, and optional touchscreen, plus the nested interrupt controller that translates PMIC, RTC, and ADC/TSC interrupt status registers into Linux child IRQs.

Important APIs, types, and functions: `struct max8925_irq_data` maps logical IRQs to status and mask registers, bit offsets, component flags, and TSC ownership. `max8925_irq()` and `max8925_tsc_irq()` are threaded parent handlers that read grouped status registers and call `handle_nested_irq()`. `max8925_irq_lock()`, `max8925_irq_sync_unlock()`, `max8925_irq_enable()`, and `max8925_irq_disable()` implement an `irq_chip`. `max8925_irq_init()` allocates descriptors, creates a legacy IRQ domain, masks/clears hardware interrupts, and requests PMIC/TSC parent IRQs. `max8925_device_init()` registers MFD children, and `max8925_device_exit()` frees IRQs and removes children.

Control flow: the I2C front end allocates `struct max8925_chip`, creates dummy RTC/ADC clients, and calls `max8925_device_init()`. Initialization sets up the interrupt domain, optionally enables ADC reference/scheduler when power or touch support is present, enables momentary power loss control, then registers child platform devices with `mfd_add_devices()`. Errors after child registration call `mfd_remove_devices()`. Runtime IRQ masking is batched through the IRQ bus lock and sync-unlock path before status handlers dispatch nested IRQs.

State and persistence: persistent driver state lives in `struct max8925_chip` and in static child-cell arrays whose `platform_data` fields are patched from board data. IRQ mask cache variables in `max8925_irq_sync_unlock()` are static, so they are shared across device instances. Hardware mask registers, alarm control, ADC scheduler, and MPL control are programmed persistently until changed by this or child drivers.

Dependencies and integration points: depends on I2C register helpers exported by `max8925-i2c.c`, `linux/mfd/core.h`, `linux/mfd/max8925.h`, regulator init data, IRQ domains, and child drivers named `max8925-rtc`, `max8925-onkey`, `max8925-regulator`, `max8925-backlight`, `max8925-power`, and `max8925-touch`.

Risks: `max8925_device_init()` ignores the return from `max8925_irq_init()`, so missing or failed parent IRQ setup can continue into child registration. Static IRQ mask caches and static mutable `mfd_cell` platform data are unsafe for multiple simultaneous chips. `max8925_irq_init()` can return early after the core IRQ is requested if no TSC IRQ exists, with no explicit release path until remove. The ADC reference polling loop has no timeout. Test signals include probe/remove with and without `tsc_irq`, nested IRQ delivery per source register, regulator pdata propagation, wakeup IRQ behavior, and failure injection around descriptor allocation and `mfd_add_devices()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max8925-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max8925-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/max8925-i2c.c

Purpose: I2C transport and parent-driver binding for the MAX8925 PMIC. It supplies synchronized byte/block register accessors, creates secondary I2C clients for RTC and ADC address spaces, parses the minimal DT property for the touchscreen IRQ, and calls the core MFD initializer.

Important APIs, types, and functions: exported helpers `max8925_reg_read()`, `max8925_reg_write()`, `max8925_bulk_read()`, `max8925_bulk_write()`, and `max8925_set_bits()` serialize SMBus and master-send transfers behind `chip->io_lock`. `max8925_probe()` allocates `struct max8925_chip`, parses `maxim,tsc-irq`, creates dummy devices at `RTC_I2C_ADDR` and `ADC_I2C_ADDR`, enables wakeup, and invokes `max8925_device_init()`. `max8925_remove()` tears down children and dummy clients. Sleep PM hooks toggle `enable_irq_wake()` based on `chip->wakeup_flag`.

Control flow: probe requires platform data or DT data, allocates the chip, binds it to the main and dummy clients, and delegates most MFD/IRQ setup to `max8925-core.c`. Remove reverses that order. The driver registers at `subsys_initcall()` so child consumers may be available early in boot.

State and persistence: I2C clientdata points all address-space clients at the same chip object. Register writes directly mutate PMIC hardware; there is no regmap cache. The wakeup flag is maintained by other code through the shared chip structure. `device_init_wakeup()` persists device wake capability until remove.

Dependencies and integration points: integrates with the I2C core, DT matching for `maxim,max8925`, and the core functions declared in `<linux/mfd/max8925.h>`. Child drivers depend on the exported accessors and shared clientdata.

Risks: `max8925_probe()` does not check the return value from `max8925_device_init()`, so child registration failure can still result in a successful probe. `max8925_write_device()` uses a fixed 9-byte buffer and assumes callers never write more than 8 payload bytes. DT requires `maxim,tsc-irq`; boards without a touchscreen IRQ cannot bind via DT even if they only need other functions. Test signals include SMBus error propagation, dummy-client cleanup on ADC allocation failure, `set_bits()` read-modify-write behavior, suspend/resume wake toggling, and boot ordering with child drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max8925-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max8997-irq.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/max8997-irq.c

Purpose: Nested interrupt-controller support for MAX8997/MAX8966 PMIC functions. It groups PMIC, MUIC, GPIO, flash, and placeholder fuel-gauge interrupt sources, keeps per-group masks, and dispatches logical IRQs through an irqdomain.

Important APIs, types, and functions: `max8997_mask_reg[]` maps interrupt groups to mask registers. `get_i2c()` selects the PMIC or MUIC client per group. `struct max8997_irq_data` and `max8997_irqs[]` map child hwirqs to group masks. `max8997_irq_thread()` reads `MAX8997_REG_INTSRC`, pulls only asserted group status registers, synthesizes GPIO edge status from `GPIOCNTL` values, applies `irq_masks_cur`, and calls `handle_nested_irq()`. `max8997_irq_init()` initializes masks, samples GPIO baseline state, creates a linear irqdomain, and requests the primary and optional ONO IRQs. `max8997_irq_resume()` replays pending IRQ processing after resume.

Control flow: the parent driver calls `max8997_irq_init()` after dummy I2C clients are available. Child drivers mask/unmask through the irq chip, and the bus sync callback writes all valid group masks to hardware. The threaded parent IRQ fans out to mapped nested IRQs; resume invokes the same fanout path to handle latched sleep events.

State and persistence: `irq_masks_cur`, `irq_masks_cache`, `gpio_status`, `irq_domain`, and `irqlock` live in `struct max8997_dev`. Hardware masks persist in PMIC and MUIC registers. GPIO edge detection depends on the saved baseline sampled at IRQ init.

Dependencies and integration points: uses register helpers from `max8997.c`, definitions from `max8997-private.h`, the IRQ core, and the MUIC dummy client. It exposes the IRQ domain consumed indirectly by MFD child resources.

Risks: fuel-gauge interrupt relay is explicitly unimplemented. GPIO baseline handling appears to store boolean values but compares against raw register bytes, which can over-detect changes. `max8997_irq_init()` creates an irqdomain but does not remove it on request-IRQ failure. `max8997_irq_sync_unlock()` writes masks unconditionally, even if cache values did not change. Test signals include PMIC and MUIC interrupt fanout, ONO IRQ edge handling, GPIO rise/fall/both semantics, resume latch replay, and error injection for I2C status reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max8997-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max8997.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/max8997.c

Purpose: Parent MFD driver for Maxim MAX8997 and MAX8966 PMICs. It provides serialized SMBus accessors, creates auxiliary I2C clients for RTC, haptic, and MUIC address spaces, initializes interrupts, registers child devices, and saves/restores selected registers across hibernation.

Important APIs, types, and functions: exported helpers `max8997_read_reg()`, `max8997_bulk_read()`, `max8997_write_reg()`, `max8997_bulk_write()`, and `max8997_update_reg()` wrap SMBus access under `iolock`. `max8997_i2c_parse_dt_pdata()` extracts the optional ONO IRQ. `max8997_i2c_probe()` builds `struct max8997_dev`, dummy clients, runtime PM state, IRQ controller, and `max8997_devs`. PM callbacks `max8997_suspend()`, `max8997_resume()`, `max8997_freeze()`, and `max8997_restore()` manage wake IRQs and register dumps.

Control flow: probe allocates state, derives chip type from I2C/OF match data, optionally parses DT, creates dummy clients, initializes IRQ support, registers children, and enables wakeup. Hibernation freeze reads configured PMIC, MUIC, and haptic addresses into `reg_dump`; restore writes them back. The driver uses `subsys_initcall()` for early availability.

State and persistence: shared state is in `struct max8997_dev`, including dummy clients, masks, type, ONO IRQ, and hibernation dump storage. Register dump content is volatile memory used only across freeze/restore. Hardware state persists in multiple I2C address spaces.

Dependencies and integration points: child devices are `max8997-pmic`, `max8997-rtc`, `max8997-battery`, `max8997-haptic`, `max8997-muic`, and two `max8997-led` instances. It integrates with `max8997-irq.c`, DT compatible `maxim,max8997-pmic`, and PM runtime/wakeup infrastructure.

Risks: if neither platform data nor OF data exists, probe returns success without registering children, which can hide configuration errors. There is no remove callback, so cleanup relies on unbind suppression and device lifetime. The hibernation dump reads MUIC and haptic registers through the main I2C client instead of the MUIC/haptic dummy clients, which is suspicious for multi-address devices. Test signals include register accessor locking, dummy-client cleanup on failure, MFD child enumeration, freeze/restore register coverage, suspend/resume IRQ masking, and DT/platform-data differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max8997.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max8998-irq.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/max8998-irq.c

Purpose: Nested IRQ controller for MAX8998 and LP3974 devices. It maps four interrupt status registers into logical child IRQs, manages per-register mask caches, and dispatches nested interrupts to MFD children.

Important APIs, types, and functions: `struct max8998_irq_data` gives each logical IRQ a status register index and mask bit. `max8998_irq_lock()`, `max8998_irq_sync_unlock()`, `max8998_irq_mask()`, and `max8998_irq_unmask()` implement the irq chip. `max8998_irq_thread()` bulk reads `MAX8998_REG_IRQ1` through the configured register count, applies masks, and calls `handle_nested_irq()` on irqdomain mappings. `max8998_irq_init()` initializes mask/status registers, creates an irqdomain, and requests primary and optional ONO IRQs. `max8998_irq_exit()` frees non-devm IRQs.

Control flow: the MAX8998 parent calls init after creating the RTC dummy client. Mask updates are staged in memory and pushed to hardware at bus sync unlock. The parent IRQ thread reads, masks, and reports asserted child IRQs. Resume invokes the IRQ thread to clear or relay sleep-latched status.

State and persistence: `irq_masks_cur`, `irq_masks_cache`, `irq_domain`, `irq_base`, `ono`, and `irqlock` live in `struct max8998_dev`. Hardware masks and status masks are initialized to all masked. The irqdomain can be legacy/simple depending on `irq_base`.

Dependencies and integration points: uses `max8998_write_reg()` and `max8998_bulk_read()` from `max8998.c`, IRQ domain helpers, and definitions in `max8998-private.h`. The domain supplies child IRQ resources to PMIC, RTC, and battery children.

Risks: `max8998_irq_domain_map()` declares its chip pointer as `struct max8997_dev *`, likely a typo that compiles only if structure layouts are not dereferenced directly there. Request failures after irqdomain creation do not remove the domain. If `irq_find_mapping()` unexpectedly fails, the parent IRQ is disabled. Test signals include mask synchronization, ONO path, resume replay on LP3974, irqdomain mapping, and negative tests for missing parent IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max8998-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max8998.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/max8998.c

Purpose: Parent MFD driver for MAX8998 and LP3974 PMIC variants. It supplies synchronized SMBus accessors, creates the RTC dummy client, initializes the IRQ controller, selects variant-specific child devices, and handles suspend/resume plus hibernation register save/restore.

Important APIs, types, and functions: exported helpers `max8998_read_reg()`, `max8998_bulk_read()`, `max8998_write_reg()`, `max8998_bulk_write()`, and `max8998_update_reg()` are shared by children and IRQ code. `max8998_i2c_parse_dt_pdata()` parses ONO IRQ information. `max8998_i2c_probe()` fills `struct max8998_dev`, sets type/irq/wakeup fields, creates the RTC dummy client, calls `max8998_irq_init()`, and registers either `max8998_devs` or `lp3974_devs`. PM functions manage wake and hibernation dumps.

Control flow: probe performs transport setup before selecting children by chip type. On child-registration failure it removes children, exits IRQ support, and unregisters the RTC client. Suspend and resume only toggle wake on the parent IRQ and replay latched status through `max8998_irq_resume()`.

State and persistence: `struct max8998_dev` stores the parent and RTC clients, IRQ metadata, platform data, and wakeup state. `max8998_dump[]` is a static register/value table used for hibernation across all instances. Hardware masks and PMIC configuration persist across normal runtime.

Dependencies and integration points: integrates with DT compatibles `maxim,max8998`, `national,lp3974`, and `ti,lp3974`; child devices named `max8998-pmic`, `max8998-rtc`, `max8998-battery`, `lp3974-pmic`, and `lp3974-rtc`; and `max8998-irq.c`.

Risks: no remove callback is provided, relying on suppressed bind attrs and module lifetime. `max8998_irq_init()` return value is not checked, so child devices can register without IRQ support. The static hibernation dump is not instance-safe and includes a duplicated register entry. Test signals include chip-type child selection, RTC dummy cleanup, hibernation dump/restore, IRQ init failure behavior, DT ONO parsing, and wakeup propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/max8998.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mc13xxx-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/mc13xxx-core.c

Purpose: Bus-independent core for Freescale MC13xxx PMICs. It wraps regmap access, exports locking and IRQ helpers, performs revision detection, configures regmap-irq, provides ADC conversion support, and registers variant-named child devices.

Important APIs, types, and functions: exported `mc13xxx_lock()`, `mc13xxx_unlock()`, `mc13xxx_reg_read()`, `mc13xxx_reg_write()`, `mc13xxx_reg_rmw()`, `mc13xxx_irq_mask()`, `mc13xxx_irq_unmask()`, `mc13xxx_irq_status()`, `mc13xxx_irq_request()`, `mc13xxx_irq_free()`, `mc13xxx_get_flags()`, and `mc13xxx_adc_do_conversion()` form the shared API. Variant descriptors `mc13xxx_variant_mc13783`, `mc13xxx_variant_mc13892`, and `mc13xxx_variant_mc34708` format revision fields. `mc13xxx_common_init()` initializes watchdog-reset behavior, regmap IRQs, flags, and subdevices. `mc13xxx_common_exit()` removes devices and IRQ chip state.

Control flow: bus drivers initialize `regmap`, `irq`, and `variant`, then call `mc13xxx_common_init()`. The core reads the revision register, enables `WDIRESET`, configures 48 regmap IRQs over two 24-bit banks, chooses feature flags from DT or platform data, then adds children such as regulator, LED, power button, codec, touchscreen, ADC, and RTC. ADC conversions serialize with `mc13xxx_lock()`, request the ADCDONE IRQ, program ADC registers, wait for completion, read samples, and restore touchscreen mode when needed.

State and persistence: `struct mc13xxx` holds regmap, IRQ chip data, mutex, flags, variant pointer, and ADC busy flag. Hardware register state is not cached. ADC conversion temporarily changes ADC configuration and restores only selected fields.

Dependencies and integration points: depends on regmap, regmap-irq, MFD core, DT feature booleans (`fsl,mc13xxx-uses-*`), and transport-specific I2C/SPI files. Child names are constructed from the chip name, for example `mc13892-regulator`.

Risks: `BUG_ON(val & ~mask)` in `mc13xxx_reg_rmw()` can panic the kernel on bad callers. Many `mc13xxx_add_subdevice*()` return values are ignored, so partial child registration can go unnoticed. `snprintf()` length check uses `> sizeof(buf)` rather than `>=`, risking truncation acceptance. ADC conversion error paths require careful review because locks are manually released and reacquired. Test signals include revision parsing for all variants, DT flag selection, regmap IRQ domain child IRQs, ADC timeout and EBUSY handling, and partial MFD-add failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mc13xxx-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mc13xxx-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/mc13xxx-i2c.c

Purpose: I2C transport driver for MC13892 and MC34708 PMIC variants. It creates an 8-bit register, 24-bit value regmap and delegates all PMIC behavior to `mc13xxx_common_init()`.

Important APIs, types, and functions: `mc13xxx_i2c_device_id[]` and `mc13xxx_dt_ids[]` bind variants to `struct mc13xxx_variant`. `mc13xxx_regmap_i2c_config` defines regmap width and disables caching. `mc13xxx_i2c_probe()` allocates `struct mc13xxx`, sets `irq`, initializes regmap with `devm_regmap_init_i2c()`, stores the variant from match data, and calls the common core. `mc13xxx_i2c_remove()` calls `mc13xxx_common_exit()`.

Control flow: registered at `subsys_initcall()`, the driver probes early, sets driver data before common initialization, and relies on devm for memory/regmap cleanup while the common exit handles children and irqchip removal.

State and persistence: no transport-specific persistent state beyond the common `struct mc13xxx`. Hardware access is direct through regmap with no cache.

Dependencies and integration points: depends on the common local header `mc13xxx.h`, public `<linux/mfd/mc13xxx.h>`, I2C match tables, and MFD children registered by the common core. It does not support MC13783 over I2C in its match table.

Risks: lack of explicit `MODULE_DEVICE_TABLE(i2c/of)` coverage would be a risk, but both are present. Variant match data must exist for every ID, or common init dereferences a NULL variant. Test signals include I2C regmap read/write width, IRQ propagation from `client->irq`, OF and legacy ID matching, and remove path cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mc13xxx-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mc13xxx-spi.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/mc13xxx-spi.c

Purpose: SPI transport driver for MC13783, MC13892, and MC34708 PMICs. It supplies a custom regmap bus that keeps chip select asserted over full 4-byte transfers to avoid MC13783/i.MX31 SPI corruption issues.

Important APIs, types, and functions: `mc13xxx_regmap_spi_config` defines 7 register bits, 1 pad bit, 24 value bits, and write flag `0x80`. `mc13xxx_spi_read()` and `mc13xxx_spi_write()` implement custom regmap bus operations; writes to audio codec/DAC registers are deliberately duplicated for an erratum. `mc13xxx_spi_probe()` configures SPI mode `SPI_MODE_0 | SPI_CS_HIGH`, default speed, custom regmap, variant match data, and calls `mc13xxx_common_init()`.

Control flow: SPI probe configures the controller before regmap creation, then the common core handles revision, IRQs, ADC, and child creation. Remove calls common exit. Registration uses `subsys_initcall()`.

State and persistence: transport state is entirely the SPI device configuration and common `struct mc13xxx`. The custom bus performs single-transfer reads and writes without caching.

Dependencies and integration points: depends on SPI core, regmap custom bus support, local/common MC13xxx core, and variant DT compatibles. It integrates all child devices through `mc13xxx-core.c`.

Risks: `mc13xxx_spi_read()` copies response bytes even if `spi_sync()` failed. The duplicate audio write ignores the first write's return value. SPI mode and max speed are forcibly adjusted, which can conflict with board assumptions. Test signals include CS behavior on a controller with FIFO empty behavior, audio register erratum path, variant matching, common core IRQ setup, and removal cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mc13xxx-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mc13xxx.h -->
# sources/distributed-fs/ceph-client/drivers/mfd/mc13xxx.h

Purpose: Private header shared by the MC13xxx core and bus drivers. It defines chip-wide register/IRQ constants, variant descriptors, the private `struct mc13xxx`, and common init/exit prototypes.

Important APIs, types, and functions: `MC13XXX_NUMREGS`, `MC13XXX_IRQ_REG_CNT`, and `MC13XXX_IRQ_PER_REG` define regmap and IRQ geometry. `struct mc13xxx_variant` carries the variant name and revision printer. `struct mc13xxx` stores regmap, device, variant, regmap-irq arrays, mutex, physical IRQ, flags, and ADC busy flags. Extern variant symbols and `mc13xxx_common_init()`/`mc13xxx_common_exit()` are the private contract.

Control flow: I2C and SPI front ends allocate `struct mc13xxx`, set transport-specific fields, then pass the owning device into `mc13xxx_common_init()`, which consumes the fields defined here.

State and persistence: this header describes all core in-memory state, including child IRQ metadata and ADC serialization. It has no executable persistence behavior by itself.

Dependencies and integration points: includes mutex, regmap, and public MC13xxx MFD definitions. It is intentionally local to `drivers/mfd`, preventing child drivers from depending on private internals.

Risks: the public/private split means changing this structure affects both bus drivers and core code but not external child drivers. The fixed-size IRQ array assumes two 24-bit banks for all supported variants. Test signals are compile-time: all MC13xxx transport and core objects must agree on struct layout, variant declarations, and IRQ constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mc13xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mcp-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/mcp-core.c

Purpose: Generic Multimedia Communications Port bus layer. It registers a custom `mcp` bus, wraps MCP host operations with spinlock serialization, manages host device allocation/lifetime, and exposes MCP driver registration helpers.

Important APIs, types, and functions: `mcp_bus_type` has a match function that accepts all devices and probe/remove adapters that call `struct mcp_driver` callbacks. Exported functions include `mcp_set_telecom_divisor()`, `mcp_set_audio_divisor()`, `mcp_reg_write()`, `mcp_reg_read()`, `mcp_enable()`, `mcp_disable()`, `mcp_host_alloc()`, `mcp_host_add()`, `mcp_host_del()`, `mcp_host_free()`, `mcp_driver_register()`, and `mcp_driver_unregister()`.

Control flow: module init registers the bus. A host driver allocates an `mcp` object plus private tailroom, initializes `ops`, then calls `mcp_host_add()`, which publishes a device named `mcp0`. MCP client drivers register through `mcp_driver_register()`, and bus probe calls their `probe(mcp)` function. Operation wrappers spinlock around low-level callbacks.

State and persistence: state lives in `struct mcp`, including use count, spinlock, ops, attached device, and private host data. `mcp_enable()`/`mcp_disable()` maintain a reference-like `use_count` and only toggle hardware on transitions between zero and nonzero.

Dependencies and integration points: depends on `<linux/mfd/mcp.h>` and custom bus infrastructure. It is consumed by host drivers such as `mcp-sa11x0.c` and codec or peripheral MCP drivers.

Risks: `mcp_bus_match()` always returns true, so only one attached device and careful driver registration ordering make this safe. `mcp_disable()` decrements without underflow protection. Register access comments warn that callers must enable the interface first or hardware can hang. Test signals include bus registration, host add/remove, probe/remove callback dispatch, enable/disable reference counts, and lock coverage of all ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mcp-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mcp-sa11x0.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/mcp-sa11x0.c

Purpose: SA11x0 platform host driver for the MCP bus. It maps SA11x0 MCP registers, implements low-level MCP ops, initializes divisors and timeouts, and publishes an MCP host for an attached codec/peripheral.

Important APIs, types, and functions: `struct mcp_sa11x0` stores two mapped register bases and cached `MCCR0/MCCR1`. Ops include `mcp_sa11x0_set_telecom_divisor()`, `mcp_sa11x0_set_audio_divisor()`, `mcp_sa11x0_write()`, `mcp_sa11x0_read()`, `mcp_sa11x0_enable()`, and `mcp_sa11x0_disable()`. `mcp_sa11x0_probe()` requests memory regions, allocates an MCP host, maps IO, initializes hardware, computes `rw_timeout`, and calls `mcp_host_add()`. PM callbacks save/restore by disabling and rewriting cached control registers.

Control flow: platform probe validates board data and resources, claims both register ranges, allocates the host with private data, maps IO, writes initial control state, and registers the MCP device. Read/write ops busy-wait for completion bits after issuing register transactions. Remove unregisters the MCP host, unmaps IO, frees host memory, and releases regions.

State and persistence: cached control registers in `struct mcp_sa11x0` are the authoritative software view for divisor and enable state. Hardware register writes persist until suspend/remove or another writer changes them. The MCP core tracks host use count.

Dependencies and integration points: depends on SA11x0 machine headers, platform data `mcp_plat_data`, the generic MCP core, platform resources, and PM sleep hooks.

Risks: manual resource management has many failure labels and depends on both mappings being present before cleanup. Read/write timeout paths log warnings but still return an unsigned value, with read returning a negative error cast to unsigned. Probe uses legacy `ioremap()` and `request_mem_region()` rather than devm helpers. Test signals include resource failure injection, timeout behavior, suspend/resume while enabled, divisor programming, and codec platform-data propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mcp-sa11x0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/menelaus.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/menelaus.c

Purpose: I2C driver for the TI/Nokia Menelaus PMIC. It provides singleton board-level helper APIs for MMC slot control, regulator voltages, sleep configuration, interrupt callbacks, optional RTC support, and low-level I2C register access.

Important APIs, types, and functions: `struct menelaus_chip` stores the singleton client, mutex, work item, IRQ masks, callback table, MMC callback, VCORE mode, and optional RTC state. Exported helpers include `menelaus_set_mmc_opendrain()`, `menelaus_set_slot_sel()`, `menelaus_set_mmc_slot()`, `menelaus_register_mmc_callback()`, `menelaus_unregister_mmc_callback()`, `menelaus_set_vmem()`, `menelaus_set_vio()`, `menelaus_set_vmmc()`, `menelaus_set_vaux()`, `menelaus_get_slot_pin_states()`, and `menelaus_set_regulator_sleep()`. `menelaus_work()` is the deferred IRQ dispatcher, and optional RTC ops implement time/alarm access.

Control flow: probe enforces a single device, stores `the_menelaus`, verifies revision, masks and acknowledges all IRQs, programs output buffer strength, requests the parent IRQ, initializes work/mutex, detects VCORE mode, runs platform late init, and optionally registers RTC. The hard IRQ disables the parent line and schedules work because I2C cannot run in interrupt context. Work reads status registers, masks/acks each active IRQ, calls registered handlers, re-enables each source, then re-enables the parent IRQ.

State and persistence: state is global through `the_menelaus`, so all exported APIs assume a probed singleton. IRQ mask bytes mirror hardware masks. Regulator and MMC helpers directly program PMIC registers, and voltage changes include a stabilization sleep. RTC state includes cached control bits and can persist on backup battery.

Dependencies and integration points: depends on I2C, workqueues, RTC core when `CONFIG_RTC_DRV_TWL92330`, board platform data, MMC users of exported callbacks, and OMAP-era IRQ assumptions. It does not use the generic MFD child-device model despite living under MFD.

Risks: exported APIs dereference `the_menelaus` without NULL checks. Probe failure after assigning the singleton may leave stale global state on early errors. `menelaus_set_vdcdc()` is not exported while similar helpers are. Work handler calls registered handlers while holding the mutex, so callbacks that call back into Menelaus helpers can deadlock. Test signals include singleton probe/remove, IRQ deferral and callback ordering, MMC callback registration/unregistration, voltage table rejection, RTC alarm/update IRQs, and system behavior with no parent IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/menelaus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/menf21bmc.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/menf21bmc.c

Purpose: I2C MFD core for the MEN 14F021P00 Board Management Controller. It verifies SMBus support, reads firmware revision fields, exits watchdog production mode if needed, and registers watchdog, LED, and hwmon child devices.

Important APIs, types, and functions: `menf21bmc_cell[]` lists `menf21bmc_wdt`, `menf21bmc_led`, and `menf21bmc_hwmon`. `menf21bmc_wdt_exit_prod_mode()` reads production status and sends the exit command if active. `menf21bmc_probe()` checks adapter functionality, reads major/minor/main revision words, logs firmware version, exits production mode, and calls `devm_mfd_add_devices()`.

Control flow: probe performs all hardware checks before child registration. Because devm MFD add is used, child devices are removed automatically on parent teardown. There is no custom remove path.

State and persistence: the driver keeps no private runtime state. Exiting production mode changes BMC persistent or semi-persistent watchdog behavior. Firmware revision is only logged.

Dependencies and integration points: depends on I2C SMBus byte/word operations, MFD core, and child drivers with matching names. Binding is by I2C ID `menf21bmc`.

Risks: revision fields are read as SMBus words but printed as decimal two-digit values, which may not match firmware encoding if it is BCD or endian-sensitive. Exiting production mode is performed automatically at probe and may have operational effects. Test signals include functionality-mask failure, revision read errors, production-mode exit success/failure, and devm child registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/menf21bmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mfd-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/mfd-core.c

Purpose: Generic Linux MFD child-device registration core. It converts `struct mfd_cell` arrays into platform devices, translates resources, attaches OF/ACPI/software nodes, registers regulator supply aliases, and provides managed and unmanaged removal APIs.

Important APIs, types, and functions: public exports are `mfd_add_devices()`, `mfd_remove_devices_late()`, `mfd_remove_devices()`, and `devm_mfd_add_devices()`. Internal `mfd_add_device()` allocates a platform device, duplicates cell data, copies/translates resources, handles OF node allocation via `mfd_match_of_node_to_dev()`, attaches ACPI fwnodes via `mfd_acpi_add_device()`, adds platform data/software nodes, and registers the platform device. `mfd_of_node_list` tracks allocated OF child nodes to avoid multiple children claiming the same node.

Control flow: parent drivers call `mfd_add_devices()` with cells and optional memory/IRQ bases or an IRQ domain. Each cell is added in order; any failure removes already-added children. Removal walks child devices in reverse order and honors dependency levels. `devm_mfd_add_devices()` registers a devres release action that calls `mfd_remove_devices()`.

State and persistence: global state consists of the protected OF node allocation list. Child platform devices persist until explicit or devm removal. Regulator supply aliases and software nodes are installed per child and removed on teardown.

Dependencies and integration points: integrates with platform bus, OF, ACPI, property/fwnode APIs, regulator aliases, IRQ domains, PM runtime, and resource conflict checking. Almost every other MFD driver in this subset relies on this file.

Risks: global OF node tracking must be cleaned on all failure paths or stale entries can block future probes. Resource IRQ translation assumes single IRQ ranges when using domains and warns on ranges. Disabled OF children are silently skipped. `pm_runtime_no_callbacks()` is called only after successful platform-device add. Test signals include OF compatible/reg matching, ACPI HID/ADR matching, resource translation with mem base and irqdomain, rollback on mid-array failure, regulator alias cleanup, and managed removal ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mfd-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/motorola-cpcap.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/motorola-cpcap.c

Purpose: SPI MFD core for Motorola CPCAP PMICs. It initializes a 16-bit little-endian regmap, validates vendor/revision, builds three regmap IRQ chips, exports interrupt-sense helper functionality, and registers numerous CPCAP child devices.

Important APIs, types, and functions: `struct cpcap_ddata` stores SPI, regmap, IRQ arrays, and regmap configuration. `cpcap_sense_virq()` is exported so children can sample current interrupt sense state. `cpcap_check_revision()` reads vendor and revision through public CPCAP helpers. `cpcap_init_irq()` allocates regmap IRQ descriptors and initializes two macro IRQ chips plus one 64-IRQ child chip. `cpcap_probe()` sets SPI mode, initializes regmap, validates revision, initializes IRQs, adjusts DMA masks, and calls `devm_mfd_add_devices()`.

Control flow: probe configures SPI for 16-bit words and chip-select-high, sets up regmap, rejects unsupported old revisions, creates IRQ chips on the same parent IRQ, enables wake on the parent IRQ, then registers child cells for ADC, battery, charger, regulator, RTC, pwrbutton, USB PHY, LEDs, and codec. Suspend disables the parent IRQ; resume re-enables it.

State and persistence: all runtime state is devm-managed in `cpcap_ddata`. IRQ chip state is owned by regmap-irq. Hardware interrupt masks/acks persist in CPCAP registers. The parent IRQ is configured as a wake source.

Dependencies and integration points: depends on SPI core, regmap, regmap-irq, public `<linux/mfd/motorola-cpcap.h>`, and OF compatibles `motorola,cpcap` and `st,6556002`. Child matching uses many `of_compatible` strings.

Risks: `enable_irq_wake()` return value is ignored and there is no matching disable in remove. All three regmap IRQ chips share one physical IRQ with `IRQF_SHARED`, which requires careful child status handling. Older revisions are rejected entirely. Test signals include revision detection, three IRQ-chip mapping ranges, exported `cpcap_sense_virq()`, wake IRQ behavior, child OF node matching, and SPI endian/register-stride correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/motorola-cpcap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mp2629.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/mp2629.c

Purpose: Minimal I2C parent driver for the Monolithic Power Systems MP2629 battery charger/ADC device. It creates an 8-bit regmap and registers ADC and charger child devices.

Important APIs, types, and functions: `mp2629_cell[]` defines `mp2629_adc` and `mp2629_charger` with OF compatibles. `mp2629_regmap_config` sets 8-bit registers/values and max register `0x17`. `mp2629_probe()` allocates `struct mp2629_data`, stores dev/clientdata, initializes I2C regmap, and calls `devm_mfd_add_devices()`.

Control flow: the I2C core probes a DT-compatible `mps,mp2629` device. All setup happens in probe, and devm handles cleanup. There is no IRQ or PM path in this parent.

State and persistence: runtime state is only `struct mp2629_data` with `dev` and `regmap`. Hardware state is controlled by child drivers through the shared regmap.

Dependencies and integration points: depends on I2C, regmap, MFD core, public `<linux/mfd/mp2629.h>`, and child drivers for ADC and charger. Uses `PLATFORM_DEVID_AUTO` for children.

Risks: no chip ID validation is performed, so a misdescribed I2C device can bind. No IRQ domain or resources are provided. Test signals include regmap init failures, child OF matching, max-register access constraints, and correct propagation of `mp2629_data` to children through parent data/regmap lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mp2629.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mt6358-irq.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/mt6358-irq.c

Purpose: IRQ controller implementation for newer MediaTek PMICs in the MT6357/MT6358/MT6359/MT6366 family. It maps top-level interrupt groups and group status registers into a linear nested IRQ domain.

Important APIs, types, and functions: `mt6357_ints[]`, `mt6358_ints[]`, and `mt6359_ints[]` describe top groups generated by chip-specific macros. `struct pmic_irq_data` instances hold group counts, total IRQ count, top status register, and group descriptors. `pmic_irq_enable()`, `pmic_irq_disable()`, `pmic_irq_lock()`, and `pmic_irq_sync_unlock()` maintain per-hwirq enable/cache arrays and update hardware enable bits. `mt6358_irq_handler()` reads top status and delegates to `mt6358_irq_sp_handler()`, which reads group status, dispatches nested IRQs, and writes back status to ack. `mt6358_irq_init()` selects chip data, allocates state arrays, masks all IRQs, creates the domain, and requests the parent IRQ.

Control flow: `mt6397-core.c` selects this initializer for MT6357/MT6358/MT6359-class chips. Child IRQ enable requests update memory until bus sync unlock writes the appropriate enable register. Parent IRQ processing walks asserted top groups and then bit-scans each group status register.

State and persistence: `chip->irq_data`, `enable_hwirq`, `cache_hwirq`, `irqlock`, and `irq_domain` are parent runtime state. Hardware enable registers and status acks persist in PMIC regmap space.

Dependencies and integration points: depends on `struct mt6397_chip`, chip-specific register headers, IRQ domains, and parent regmap from the PMIC wrapper. Child devices receive mapped IRQ resources through `mt6397-core.c`.

Risks: `pmic_irq_data` templates are static and then populated with devm-allocated arrays per probe; multiple same-chip instances would race or overwrite shared pointers. `enable_irq_wake()` return value is ignored. No explicit domain removal on normal devm teardown is visible here. Test signals include chip ID dispatch, enable/cache synchronization, top-group status handling, status ack writes, nested IRQ mapping for all hwirqs, and multi-instance analysis.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mt6358-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mt6360-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/mt6360-core.c

Purpose: I2C MFD driver for the MediaTek/Richtek MT6360 PMU. It presents four I2C slave address spaces as one 16-bit regmap, handles PMIC/LDO CRC framing, validates vendor info, registers a regmap IRQ chip, and creates ADC, charger, LED, regulator, and TCPC child devices.

Important APIs, types, and functions: `struct mt6360_ddata` stores four I2C clients, regmap, IRQ data, chip revision, and CRC table. `mt6360_irqs[]` and `mt6360_irq_chip` describe 16 IRQ registers. `mt6360_xlate_pmicldo_addr()` encodes PMIC/LDO address size fields. `mt6360_regmap_read()` and `mt6360_regmap_write()` implement custom banked regmap access with CRC for PMIC and LDO banks. `mt6360_check_vendor_info()` validates vendor nibble. `mt6360_probe()` creates dummy clients, initializes CRC/regmap/irqchip, and registers children with an IRQ domain.

Control flow: probe maps TCPC, PMIC, LDO, and PMU I2C slave IDs, with the real client used for PMU. Regmap register high byte selects the bank. Reads/writes choose the client, optionally translate address and verify/append CRC, then issue SMBus block transfers. After vendor validation, regmap-irq provides child IRQ mappings to `devm_mfd_add_devices()`.

State and persistence: `ddata` owns slave clients and CRC table. Hardware register state is not cached. `chip_rev` is stored after validation. Child drivers access all banks through the shared regmap.

Dependencies and integration points: depends on I2C dummy devices, custom regmap bus, CRC8, regmap-irq, MFD cell macros, and DT compatible `mediatek,mt6360`. Child IRQ resources are named for charger, ADC, LED, and regulator events.

Risks: custom read/write code uses pointer arithmetic on `void *`, which relies on compiler extensions. Write buffer lifetime is manually freed, unlike the read path's cleanup attribute. CRC framing and block-size assumptions are complex and easy to regress. Suspend/resume only toggles wake if the device is wake-capable but probe never sets wake capability. Test signals include all bank translations, CRC mismatch handling, short SMBus transfers, IRQ resource mapping, vendor rejection, and child driver access across PMU/TCPC/PMIC/LDO banks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mt6360-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mt6370.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/mt6370.c

Purpose: I2C MFD driver for MT6370/MT6371/MT6372-family SubPMIC devices and RT5081 variants. It combines PMU and USB-C I2C address spaces into a custom regmap, validates vendor ID, registers a regmap IRQ chip, and creates common plus variant-exclusive child devices.

Important APIs, types, and functions: `mt6370_irqs[]` and `mt6370_irq_chip` describe up to 16 IRQ registers with many charger, Type-C, flashlight, regulator, display-bias, and backlight events. `mt6370_check_vendor_info()` reads `MT6370_REG_DEV_INFO` and accepts known vendor IDs. `mt6370_regmap_read()` and `mt6370_regmap_write()` route regmap transactions to `info->i2c[bank_idx]`. `mt6370_probe()` allocates `struct mt6370_info`, creates a USBC dummy client, initializes regmap and IRQ chip, selects `mt6370_exclusive_devices` or `mt6372_exclusive_devices`, then registers common devices.

Control flow: the base I2C client represents PMU bank and a dummy client represents the USBC bank. Vendor ID determines the backlight compatible string. Both exclusive and common child groups are registered with the same regmap IRQ domain.

State and persistence: `struct mt6370_info` holds two I2C clients and regmap IRQ data. Hardware state is direct through the custom regmap with no cache. Vendor ID only controls child enumeration.

Dependencies and integration points: depends on local `mt6370.h` for IRQ numbers and private state, I2C, regmap, regmap-irq, and MFD core. Child devices include ADC, charger, flashlight, indicator, TCPC, regulator, and backlight.

Risks: regmap bus read/write does not validate `bank_idx` against `MT6370_MAX_I2C`, so malformed regmap accesses could index outside the client array. The IRQ chip lacks explicit ack settings, so behavior depends on regmap-irq defaults and hardware status semantics. Two `devm_mfd_add_devices()` calls mean partial success can occur if exclusive devices register but common devices fail. Test signals include vendor-specific child selection, invalid bank access, IRQ mapping for regulator resources, dummy USBC client failure, and regmap short-transfer handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mt6370.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mt6370.h -->
# sources/distributed-fs/ceph-client/drivers/mfd/mt6370.h

Purpose: Private header for the MT6370 MFD driver. It centralizes IRQ hwirq numbers, I2C bank indices, and the private `struct mt6370_info` shared by the driver-local custom regmap bus.

Important APIs, types, and functions: macros `MT6370_IRQ_*` define sparse hwirq positions across 16 IRQ status/mask registers. The anonymous enum defines `MT6370_USBC_I2C`, `MT6370_PMU_I2C`, and `MT6370_MAX_I2C`. `struct mt6370_info` stores the two I2C client pointers and `regmap_irq_chip_data`.

Control flow: `mt6370.c` includes this header to build `regmap_irq` descriptors, child IRQ resources, and route custom regmap reads/writes to PMU or USBC clients.

State and persistence: the header declares in-memory parent state only. IRQ number definitions are ABI-like within the parent and child-resource mapping.

Dependencies and integration points: depends on I2C client and regmap-irq types included indirectly by the C file. It is private to `drivers/mfd`, while children consume resources by name or mapped IRQ rather than this private struct.

Risks: the closing comment says `__MFD_MT6375_H__` rather than `__MFD_MT6370_H__`, a harmless but confusing typo. Sparse IRQ numbering must stay synchronized with hardware and child resource names. Test signals are compile-time and integration-focused: all IRQ macros used by resources must fit under the regmap IRQ chip's register count, and bank indices must match the client array size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mt6370.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mt6397-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/mt6397-core.c

Purpose: Platform MFD core for MediaTek PMICs attached below the SoC PMIC wrapper. It selects chip-specific child device arrays and IRQ initialization routines for MT6323, MT6328, MT6331/MT6332, MT6357, MT6358, MT6359, and MT6397.

Important APIs, types, and functions: numerous resource arrays define RTC, key, power-controller, and accessory-detect resources. Chip-specific `mfd_cell` arrays enumerate child devices. `struct chip_data` ties chip ID register/shift, child cells, and IRQ initializer. `mt6397_probe()` obtains the parent regmap, match data, reads chip ID, gets the platform IRQ, initializes the selected IRQ controller, and registers children via `devm_mfd_add_devices()`.

Control flow: the platform device is created by the PMIC wrapper. Probe uses OF match data to choose the chip profile, reads the hardware ID from the wrapper-provided regmap, stores `struct mt6397_chip`, initializes either legacy `mt6397_irq_init()` or newer `mt6358_irq_init()`, then publishes child devices with the IRQ domain.

State and persistence: `struct mt6397_chip` is parent state, holding dev, regmap, chip_id, irq, irqdomain, and IRQ masks initialized by the selected IRQ file. Child device resources describe hardware register windows and IRQ numbers but are static const data.

Dependencies and integration points: depends on parent PMIC wrapper regmap, MediaTek register/core headers, `mt6397-irq.c`, `mt6358-irq.c`, platform bus, MFD core, and DT compatibles for each chip. Child drivers include RTC, regulator, codec/sound, clock, pinctrl, keys, auxadc, LEDs, power controller, and accdet depending on chip.

Risks: if `devm_mfd_add_devices()` fails, the irqdomain is removed manually, but normal devm removal does not unregister the PM notifier used by `mt6397-irq.c`. Some MT6359 cells reuse MT6358 RTC resources/compatible, which may be intentional compatibility but needs binding awareness. Test signals include all OF match profiles, chip ID extraction shifts, platform IRQ absence, correct IRQ initializer selection, child resource mapping through the domain, and rollback on child add failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mt6397-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mt6397-irq.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/mt6397-irq.c

Purpose: IRQ controller for older MediaTek PMICs in the MT6323/MT6328/MT6331/MT6391/MT6397 line. It maps one to three 16-bit status/control registers into a nested IRQ domain and adjusts wake masks around system suspend.

Important APIs, types, and functions: `mt6397_irq_chip` implements mask/unmask, bus lock/sync unlock, and optional wake control. `mt6397_irq_handle_reg()` reads one status register, dispatches set bits through `handle_nested_irq()`, and writes status back to ack. `mt6397_irq_thread()` handles configured status banks. `mt6397_irq_pm_notifier()` switches hardware masks to `wake_mask[]` during `PM_SUSPEND_PREPARE` and restores `irq_masks_cur[]` on `PM_POST_SUSPEND`. `mt6397_irq_init()` selects register addresses by chip ID, masks all sources, creates the domain, requests the parent IRQ, and registers the PM notifier.

Control flow: the parent core calls init after reading chip ID. Child mask/unmask changes update in-memory masks until sync unlock writes interrupt-control registers. Parent IRQ fanout reads each available status bank. Suspend notifier narrows enabled hardware sources to those marked wake-capable and enables parent IRQ wake.

State and persistence: `struct mt6397_chip` holds interrupt control/status register addresses, current masks, wake masks, irqdomain, mutex, parent IRQ, and PM notifier. Hardware masks are active state in PMIC registers.

Dependencies and integration points: depends on `mt6397-core.c`, register headers, PM notifier infrastructure, regmap, and IRQ domain mapping. The IRQ domain is passed to child devices by the parent.

Risks: `register_pm_notifier()` is not checked and there is no visible unregister path. `enable_irq_wake()`/`disable_irq_wake()` return values are ignored. Mask semantics use set bits as enabled, which differs from many PMICs and must remain consistent with child expectations. Test signals include all chip ID register layouts, wake mask transitions over suspend/resume, three-bank MT6328 handling, status ack writes, and notifier cleanup during probe/remove failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mt6397-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mxs-lradc.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/mxs-lradc.c

Purpose: MFD splitter for Freescale i.MX23/i.MX28 LRADC hardware. It claims the parent clock and memory resource, chooses SoC-specific ADC/touchscreen child resources, parses touchscreen wiring, and registers ADC plus optional touchscreen children.

Important APIs, types, and functions: SoC-specific IRQ enums and resource arrays define ADC and touchscreen resource sets. `mxs_lradc_dt_ids[]` maps compatibles to `IMX23_LRADC` or `IMX28_LRADC`. `mxs_lradc_probe()` allocates `struct mxs_lradc`, enables the clock, parses `fsl,lradc-touchscreen-wires`, copies the parent MEM resource into child resource slot 0, and uses `devm_mfd_add_devices()` for `mxs-lradc-adc` and optional `mxs-lradc-ts`. `mxs_lradc_remove()` disables the clock.

Control flow: probe must enable the delay-unit clock before children can use hardware. If touchscreen wiring is absent, all buffer virtual channels are available to the ADC child and only ADC is registered. If wiring is present, limited buffer channels and touchscreen mode are configured, then both ADC and touchscreen children are added.

State and persistence: parent state holds SoC type, clock, touchscreen wire mode, and buffer channel policy. Static resource arrays are mutated with the probed MEM resource, so they become instance-specific.

Dependencies and integration points: depends on platform resources, OF properties, clk API, MFD core, and public `<linux/mfd/mxs-lradc.h>`. Child drivers rely on the shared memory region and IRQ resources.

Risks: static mutable resource arrays make multiple LRADC instances unsafe. If touchscreen child registration fails after ADC registration, devm cleanup later removes ADC but the probe manually only disables the clock. Unsupported 5-wire mode on i.MX23 is rejected. Test signals include i.MX23/i.MX28 resource mapping, touchscreen property validation, clock enable/disable on all failure paths, ADC-only mode, and child resource IRQ names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/mxs-lradc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/nct6694.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/nct6694.c

Purpose: USB MFD core for the Nuvoton NCT6694 controller. It exports synchronized USB command read/write helpers, maps interrupt endpoint status bits into a simple IRQ domain, manages per-function ID allocators, and hotplugs many child devices.

Important APIs, types, and functions: `nct6694_devs[]` declares 16 GPIO, 6 I2C, 2 CAN-FD, 2 watchdog, one hwmon, and one RTC child. Exported `nct6694_read_msg()` and `nct6694_write_msg()` serialize USB bulk command/response/data transfers under `access_lock` and normalize response status through `nct6694_response_err_handling()`. `usb_int_callback()` processes interrupt URB status bits and calls `generic_handle_irq_safe()`. `nct6694_irq_chip` and domain ops map hardware bits to Linux IRQs. `nct6694_usb_probe()` allocates buffers/URB/domain/IDAs, submits the interrupt URB, and calls `mfd_add_hotplug_devices()`.

Control flow: USB probe validates the interrupt-in endpoint, submits a persistent interrupt URB, stores interface data, and registers hotplug child devices. The interrupt callback resubmits the URB after handling normal and recoverable statuses. Disconnect removes children, kills the URB, destroys IDAs, removes the domain, and frees the URB.

State and persistence: `struct nct6694` stores USB device/interface state, shared command buffer, interrupt buffer/URB, IRQ domain, enabled IRQ bitmap, spinlock, mutex, and IDAs. Hardware command state lives in the USB-attached controller. Child instance numbering is allocated through IDAs.

Dependencies and integration points: depends on USB bulk/int endpoints, IRQ domain APIs, MFD hotplug support, IDA, and public `<linux/mfd/nct6694.h>`. Children call exported message helpers and consume the IRQ domain.

Risks: `nct6694_irq_enable`/disable only update a software bitmap; the interrupt callback dispatches all status bits regardless of `irq_enable`, so disabled child IRQs may still be handled unless the generic IRQ layer suppresses them later. Probe assumes endpoint 0 is interrupt-in. Bulk command header transfers use `sizeof(*msg)` while passing `&msg->cmd_header`, which sends the full union-sized buffer from the header address. Test signals include USB short transfers, response status mapping, URB resubmission after errors, disconnect races with callbacks, child hotplug enumeration, and IRQ enable/disable semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/nct6694.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ntxec.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/ntxec.c

Purpose: I2C MFD core for Netronix embedded controllers used in e-book readers. It initializes big-endian 16-bit register access, detects firmware version, registers RTC/PWM children depending on firmware, and optionally provides system poweroff/restart handlers.

Important APIs, types, and functions: `ntxec_poweroff()` writes `NTXEC_REG_POWEROFF` and sleeps long enough for power loss. `ntxec_restart()` writes the reset register through a restart notifier. `regmap_config` defines normal I2C regmap access; `regmap_config_noack` stacks a wrapper regmap for firmware that does not ACK writes. `ntxec_probe()` reads `NTXEC_REG_VERSION`, selects child cells, enables `POWERKEEP` for system-power-controller nodes, assigns global poweroff/restart client state, and calls `devm_mfd_add_devices()`. `ntxec_remove()` unregisters global power handlers for the owning client.

Control flow: probe initializes regmap first, rejects unknown firmware versions, optionally wraps regmap for Tolino Shine 2, handles system power controller duties, stores clientdata, and registers children. Poweroff/restart callbacks bypass regmap and issue raw I2C transfers because they may run late in shutdown.

State and persistence: `struct ntxec` stores device and regmap. Global `poweroff_restart_client`, `pm_power_off`, and `ntxec_restart_handler` are process-wide state. `POWERKEEP` changes controller behavior to keep the host running.

Dependencies and integration points: depends on I2C, regmap, MFD core, reboot/poweroff infrastructure, OF `system-power-controller`, and public `<linux/mfd/ntxec.h>`. Children are `ntxec-rtc` and/or `ntxec-pwm`.

Risks: global poweroff handler assignment is only logged if already occupied; probe continues. `ntxec_remove()` sets `pm_power_off = NULL` without verifying that it still points to `ntxec_poweroff`. The no-ACK wrapper ignores write errors by design, which may hide hardware failures. Test signals include firmware-version matrix, no-ACK write wrapper, poweroff/restart raw I2C lengths, system-power-controller conflict behavior, and child selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ntxec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ocelot-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/ocelot-core.c

Purpose: Bus-agnostic MFD core for externally controlled Microchip/MSCC Ocelot switch chips. It resets the chip, constructs per-resource regmaps for child register windows, and registers child devices for pinctrl, SGPIO, MIIM, SERDES, and switch functionality.

Important APIs, types, and functions: `ocelot_chip_reset()` writes the GCB soft reset bit and polls until it self-clears. Resource arrays describe VSC7512 register windows for MIIM, GPIO, SIO, HSIO, switch blocks, VCAPs, and ports. `vsc7512_devs[]` lists child cells with OF compatibles and resources. `ocelot_core_try_add_regmap()` creates a named regmap for a resource if one is not already registered. `ocelot_core_init()` ensures all child resource regmaps exist and calls `devm_mfd_add_devices()`.

Control flow: a bus front end such as SPI sets `struct ocelot_ddata` and core regmaps, resets/configures the chip, then calls `ocelot_core_init()`. Core init walks all child cell resources and asks the SPI helper to create regmaps named after each resource, then registers children.

State and persistence: `struct ocelot_ddata` lives in the bus front end and contains GCB/CPUORG regmaps used here. Reset writes hardware global state and can clear prior bus configuration. Child regmaps are devm-managed and attached to the parent device by name.

Dependencies and integration points: imports namespace `MFD_OCELOT_SPI` for `ocelot_spi_init_regmap()`, exports `ocelot_chip_reset()` and `ocelot_core_init()` under `MFD_OCELOT`, and integrates with the generic MFD core plus Ocelot SoC child drivers.

Risks: despite being described as bus-agnostic, `ocelot_core_try_add_regmap()` directly calls the SPI regmap initializer, so other buses need refactoring. Regmap creation failures are ignored in `ocelot_core_try_add_regmap()`, so child probe may fail later with less context. Test signals include reset timeout, child resource regmap name lookup, OF reg matching for MIIM0/MIIM1, switch resource coverage, and failure propagation when a regmap cannot be created.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ocelot-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ocelot-spi.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/ocelot-spi.c

Purpose: SPI front end for externally controlled Ocelot/VSC7512 chips. It calculates SPI read padding, configures byte order and interface timing, creates regmaps over SPI register windows, resets and reinitializes the chip, then delegates child creation to `ocelot-core.c`.

Important APIs, types, and functions: `ocelot_spi_initialize()` writes CPUORG interface control and padding configuration, then verifies padding, interface status, and serial-interface selection. `ocelot_spi_regmap_config` defines 24-bit big-endian addresses, 32-bit native-endian values, stride/downshift, and single read/write behavior. `ocelot_spi_regmap_bus_read()` emits address, optional dummy padding, and data receive transfers. `ocelot_spi_init_regmap()` exports named regmap construction for any resource. `ocelot_spi_probe()` allocates `struct ocelot_ddata`, calculates padding from bus speed, initializes CPUORG/GCB regmaps, configures SPI, resets the chip, configures SPI again, and calls `ocelot_core_init()`.

Control flow: probe must configure the serial interface before any broad register access. Because chip reset clears SPI interface configuration, initialization is performed before and after `ocelot_chip_reset()`. Child registration only happens after the second successful initialization.

State and persistence: `ocelot_ddata` stores padding count, dummy buffer, and core regmaps. SPI interface configuration is hardware state and is lost on chip reset. Devm regmaps persist for child use until device removal.

Dependencies and integration points: depends on SPI core, custom regmap bus, Ocelot private header, `ocelot-core.c` exports, DT compatible `mscc,vsc7512`, and namespace imports/exports.

Risks: padding calculation is integer approximation and incorrect values cause `ocelot_spi_initialize()` to reject the interface or reads to fail. `ocelot_spi_regmap_bus_read()` relies on `dummy_data` support in SPI transfers. The regmap bus has no locking beyond regmap/SPI core behavior. Test signals include low-speed zero-padding path, high-speed padding verification, reset reinitialization, endian correctness, named resource regmap creation, and SPI transfer failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ocelot-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ocelot.h -->
# sources/distributed-fs/ceph-client/drivers/mfd/ocelot.h

Purpose: Private header shared by Ocelot MFD core and SPI front end. It defines the parent private data, exported core/SPI helper prototypes, and compile-time SPI byte-order constants.

Important APIs, types, and functions: `struct ocelot_ddata` stores GCB and CPUORG regmaps, SPI padding byte count, and dummy buffer pointer. Prototypes declare `ocelot_chip_reset()`, `ocelot_core_init()`, and `ocelot_spi_init_regmap()`. `OCELOT_SPI_BYTE_ORDER_LE`, `OCELOT_SPI_BYTE_ORDER_BE`, and `OCELOT_SPI_BYTE_ORDER` encode payload ordering based on host endianness.

Control flow: `ocelot-spi.c` fills `ocelot_ddata` and uses the byte-order macro during interface initialization. `ocelot-core.c` retrieves the same data with `dev_get_drvdata()` and calls the SPI regmap helper when creating child resource regmaps.

State and persistence: the header describes in-memory parent state only. The byte-order macro determines persistent hardware interface configuration written by the SPI driver.

Dependencies and integration points: includes `linux/kconfig.h` for endianness checks and forward-declares device/regmap/resource types to keep compile dependencies light. It is local to the Ocelot MFD implementation and namespace exports.

Risks: this private header currently bakes SPI-specific fields into the shared data structure, limiting the bus-agnostic goal of the core. Endianness macro correctness is critical because a wrong value makes all register payloads decode incorrectly. Test signals are compile-time for little- and big-endian builds plus runtime verification that SPI register reads match expected values after initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ocelot.h -->
