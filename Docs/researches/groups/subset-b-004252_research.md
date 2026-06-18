# subset-b-004252 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm8994-core.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/wm8994-core.c

Purpose: this is the I2C MFD core for the Wolfson WM8994 family, covering WM8994, WM8958, and WM1811 audio CODECs. It creates the regulator, codec, and GPIO child devices, selects the correct register cache model after reading the hardware ID, applies revision patches, configures board/DT defaults, wires the interrupt controller, and manages runtime suspend/resume around the shared regmap and bulk regulators.

Important APIs, types, and functions: the file defines `wm8994_regulator_devs`, `wm8994_devs`, codec/GPIO IRQ resources, type-specific supply name arrays, runtime PM callbacks `wm8994_suspend()` and `wm8994_resume()`, OF/platform-data import in `wm8994_set_pdata_from_of()`, main setup/teardown in `wm8994_device_init()` and `wm8994_device_exit()`, and the I2C driver entry points `wm8994_i2c_probe()` and `wm8994_i2c_remove()`. It depends on `struct wm8994`, `struct wm8994_pdata`, regmap configs declared in `wm8994.h`, and IRQ helpers from `wm8994-irq.c`.

Control flow: probe allocates `struct wm8994`, initializes a minimal I2C regmap with `wm8994_base_regmap_config`, then calls `wm8994_device_init()`. Device init copies platform data, overlays OF properties, registers LDO child devices first so internal regulators can satisfy later supply lookups, selects a bulk supply list by requested chip type, enables supplies, reads `WM8994_SOFTWARE_RESET` to verify and normalize chip identity, reads revision/customer ID, chooses a patch and full regmap config, reinitializes the regcache, resets the device, applies the patch, programs GPIO/pull/LDO discharge policy, initializes IRQs, registers codec/GPIO child devices, and enables runtime PM. Error paths unwind IRQs, regulators, and MFD children in reverse order.

State and persistence: persistent driver state lives in `struct wm8994`: chip type, revision, customer ID, regmap, supply array, IRQ bases, platform defaults, and suspend flags. Register state is cached by regmap with `REGCACHE_MAPLE` after device identification. Suspend may skip power-down for WM8958/WM1811 accessory detection if mic detect is active; otherwise it programs LDO pulldowns, resets the chip, marks the regcache dirty, syncs GPIO and interrupt-mask regions needed for wake behavior, switches the cache to cache-only, sets `suspended`, and disables supplies. Resume reenables supplies, exits cache-only mode, syncs the regcache, clears active LDO pulldowns, and clears `suspended`.

Dependencies and integration points: integrates with Linux I2C, MFD core, regulator bulk APIs, OF properties (`wlf,gpio-cfg`, `wlf,micbias-cfg`, lineout feedback/single-ended flags, pull flags), runtime PM, regmap, and child drivers named `wm8994-ldo`, `wm8994-codec`, and `wm8994-gpio`. The `MODULE_SOFTDEP("pre: wm8994_regulator")` expresses bootstrapping needs for internal regulators.

Risks and test signals: ID mismatch, missing supplies, probe deferral, regcache reinit failure, IRQ setup failure, and incomplete error unwind are the main probe risks. Suspend/resume risks include stale cache after reset, losing wake-capable GPIO/IRQ state, and powering down while accessory detection is still needed. Test signals include successful probe logs with device/revision/customer ID, MFD child creation, regulator enable/disable balance, runtime PM cycling, interrupt delivery to child resources, OF GPIO defaults taking effect, and regcache sync succeeding after suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm8994-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm8994-irq.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/wm8994-irq.c

Purpose: this file implements the WM8994-family interrupt controller glue used by the MFD core. It maps codec status bits and GPIO interrupt bits into Linux nested IRQs through regmap-irq and provides an extra GPIO-backed wrapper for platforms whose top-level interrupt is edge triggered.

Important APIs, types, and functions: `wm8994_irqs[]` maps `WM8994_IRQ_*` logical IRQ numbers to masks and register offsets. `wm8994_irq_chip` describes two status/mask/ack registers starting at `WM8994_INTERRUPT_STATUS_1`. `wm8994_irq_init()` and `wm8994_irq_exit()` are exported. Edge-trigger support uses `wm8994_edge_irq_chip`, `wm8994_edge_irq()`, `wm8994_edge_irq_map()`, and a one-entry irqdomain.

Control flow: `wm8994_irq_init()` returns early if no parent IRQ is available. Otherwise it selects platform IRQ flags or defaults to high-level oneshot. For rising/falling edge flags, it requests the platform IRQ GPIO, creates a linear irqdomain with one virtual IRQ, adds the regmap IRQ chip behind that nested virtual IRQ, then requests a threaded top-level IRQ that loops while the GPIO line is asserted and dispatches the nested IRQ. For level-triggered cases it adds the regmap IRQ chip directly on the parent IRQ. Finally it unmasks the top-level codec interrupt by writing zero to `WM8994_INTERRUPT_CONTROL`.

State and persistence: persistent state is stored in `wm8994->irq`, `wm8994->irq_base`, `wm8994->irq_data`, and, for edge mode, `wm8994->edge_irq`. Mask/cache state is maintained by regmap-irq over the hardware interrupt mask registers. `wm8994_irq_exit()` deletes the regmap IRQ chip.

Dependencies and integration points: depends on gpiolib, irqdomain, regmap-irq, nested threaded IRQ handling, and WM8994 register definitions. Codec and GPIO child MFD cells consume the logical IRQ resources published by the parent.

Risks and test signals: edge-mode setup assumes `pdata->irq_gpio` is valid and can be converted to the parent IRQ; irqdomain allocation failure is not checked before mapping. A table entry for `WM8994_IRQ_GPIO(9)` uses `WM8994_GP8_EINT`, which is suspicious because GPIO 9 would normally be expected to use a GP9 mask if one exists. Test signals include parent IRQ registration, child IRQ mappings, mask/unmask behavior through regmap, interrupt ack by status-register write, and edge-mode repeated dispatch while the GPIO line remains asserted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm8994-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm8994-regmap.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/wm8994-regmap.c

Purpose: this file supplies the device-specific regmap data for WM1811, WM8994, and WM8958 variants. It defines reset/default values, readable-register predicates, volatile-register predicates, and exported regmap configurations used by `wm8994-core.c` after the chip identity is known.

Important APIs, types, and functions: `wm1811_defaults[]`, `wm8994_defaults[]`, and `wm8958_defaults[]` are the cache seed tables. `wm1811_readable_register()`, `wm8994_readable_register()`, and `wm8958_readable_register()` define valid bus-visible registers by chip variant. `wm8994_volatile_register()`, `wm1811_volatile_register()`, and `wm8958_volatile_register()` prevent caching of reset, status, interrupt, DSP, firmware, and selected GPIO/status registers. Exported objects are `wm1811_regmap_config`, `wm8994_regmap_config`, `wm8958_regmap_config`, and minimal `wm8994_base_regmap_config`.

Control flow: there is no runtime control loop beyond regmap callbacks. The core driver starts with the base config for early ID access, then calls `regmap_reinit_cache()` with the full variant config. Read/write calls from codec, GPIO, regulator, IRQ, and core paths are filtered and cached through these callbacks. Variant readable predicates build on one another: WM8994 adds registers to WM1811, and WM8958 adds DSP/MBC/firmware registers to WM8994.

State and persistence: reset defaults cover power management, analog mixers, LDOs, MICBIAS, clocks, FLLs, AIFs, filters, DRC/EQ coefficients, routing, GPIOs, interrupt masks, and WM8958 DSP/MBC registers. Volatile lists keep live status from becoming stale in the regcache. WM1811 has a customer/revision-dependent volatile treatment for GPIO6, read from driver data.

Dependencies and integration points: depends on `linux/regmap.h`, `linux/mfd/wm8994/core.h`, and register macro definitions. The regmap configs are directly consumed by the WM8994 core and indirectly by all child MFD functions sharing the parent regmap.

Risks and test signals: stale or incomplete default tables can cause incorrect cache restore after reset or suspend. Missing readable entries can make valid hardware accesses fail; missing volatile entries can cache changing status. Test signals include regmap debugfs/default comparisons, successful cache sync after runtime resume, interrupt status reads not being served stale, and variant-specific register access for WM8958 DSP/MBC and WM1811 GPIO6 behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm8994-regmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm8994.h -->
## sources/distributed-fs/ceph-client/drivers/mfd/wm8994.h

Purpose: this private header declares the regmap configuration objects shared inside the WM8994 MFD implementation. It is intentionally narrow and avoids exposing implementation details beyond the regmap configs.

Important APIs, types, and functions: it includes `<linux/regmap.h>` and declares `extern struct regmap_config wm1811_regmap_config`, `wm8994_regmap_config`, `wm8958_regmap_config`, and `wm8994_base_regmap_config`.

Control flow and state: no executable code or state is defined here. The header provides compile-time linkage between `wm8994-core.c` and `wm8994-regmap.c`; the core chooses among the declarations at probe time.

Dependencies and integration points: local inclusion by WM8994 MFD source files. The full definitions are exported from `wm8994-regmap.c`, while early I2C probe uses the base config before selecting the chip-specific config.

Risks and test signals: risks are limited to declaration drift against definitions or unintended external exposure. Build and modpost checks catch missing or mismatched symbols; runtime probe confirms the base/full config handoff is linked correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm8994.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm8997-tables.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/wm8997-tables.c

Purpose: this file is the WM8997 data-table companion for the Arizona/Madera-style MFD core. It provides revision patch data, main and always-on interrupt chips, reset-default register cache data, readable/volatile register predicates, and the exported I2C regmap config for WM8997.

Important APIs, types, and functions: `wm8997_reva_patch[]` and `wm8997_patch()` apply a small Rev A register patch. `wm8997_aod_irqs[]`/`wm8997_aod` define always-on interrupts such as GP5 and jack-detect edges. `wm8997_irqs[]`/`wm8997_irq` define the five-register main IRQ chip for GPIO, speaker overheat, HP/mic detect, clock/FLL, AIF/control-interface, mixer, boot, and DCS events. `wm8997_reg_default[]` seeds the regcache. `wm8997_readable_register()` and `wm8997_volatile_register()` define access and cache behavior. `wm8997_i2c_regmap` is exported.

Control flow: the Arizona core can call `wm8997_patch()` after identifying revision 0. IRQ setup elsewhere consumes the exported regmap IRQ chips. Regmap uses the readable and volatile callbacks on each access and seeds `REGCACHE_MAPLE` from the default table. The default/readable blocks cover control interface, write sequencer, tone/PWM/haptics, clocking and FLLs, regulators/MICBIAS, jack and mic detect, input/output paths, AIF/SLIMbus interfaces, mixer routing, GPIO/pad/IRQ controls, AOD status/masks, EQ/DRC/HPLPF, and ISRC registers.

State and persistence: persistent register state is represented as reset defaults plus nonvolatile cached writes. Volatile status includes reset/revision, haptics and sample-rate status, FLL NCO tests, mic/headphone detect live status, input/output status, SLIMbus port status, main and secondary IRQ status/raw status, IRQ pin status, AOD wake/IRQ status, and `FX_CTRL2`. `WM8997_MAX_REGISTER` bounds legal access to `0x31ff`.

Dependencies and integration points: depends on Arizona core/register headers, regmap, and module exports. It integrates with the broader Arizona MFD core, codec, GPIO, regulator, interrupt, jack-detect, audio-routing, haptics, SLIMbus, and clocking drivers via shared register definitions.

Risks and test signals: table-driven code risks are mostly omissions or mismatches between default tables, readable predicates, volatile predicates, and hardware revisions. Rev A patch application must be confirmed only for revision 0. Test signals include regmap initialization with 32-bit big-endian register addresses and 16-bit big-endian values, successful IRQ chip registration for main/AOD domains, cache sync after suspend, jack/mic wake behavior, and valid access to audio routing/EQ/DRC/ISRC registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm8997-tables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm8998-tables.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/wm8998-tables.c

Purpose: this file provides WM8998-class data tables for the Arizona/Madera infrastructure. It is similar to the WM8997 table file but includes WM8998-specific patching, AOD wake configuration, additional audio interfaces/features, and distinct readable/volatile register coverage.

Important APIs, types, and functions: `WM8998_NUM_AOD_ISR` and `WM8998_NUM_ISR` name interrupt bank counts. `wm8998_rev_a_patch[]` and `wm8998_patch()` register the Rev A patch. `wm8998_aod_irqs[]`/`wm8998_aod` define always-on IRQs including mic-detect clamp and GP5/jack edges, with `wake_base = ARIZONA_WAKE_CONTROL` and inverted wake bits. `wm8998_irqs[]`/`wm8998_irq` define the five-bank main interrupt chip. `wm8998_reg_default[]`, `wm8998_readable_register()`, `wm8998_volatile_register()`, and exported `wm8998_i2c_regmap` define regmap behavior.

Control flow: patch registration is unconditional when `wm8998_patch()` is called. IRQ chips are data consumed by the parent MFD IRQ setup. The regmap config uses 32-bit big-endian register addresses, 16-bit big-endian values, `WM8998_MAX_REGISTER` of `0x31ff`, `REGCACHE_MAPLE`, the reset-default table, and access callbacks. Readable/default coverage includes wake/write-sequencer, clock/FLL, regulators/MICBIAS, accessory/mic clamp and mic-level detection, HPF, expanded output paths, DRE/EDRE, AIF1/2/3, SPDIF, SLIMbus, many mixer routes, ASRC/ISRC, GPIO/pads, IRQ/AOD, EQ/DRC/HPLPF, and ASRC status/rates.

State and persistence: default table entries persist as regcache seed values for nonvolatile registers. Volatile registers include reset/revision, write sequencer controls, live haptics/sample-rate status, async status, mic/headphone detect, input/output and SLIMbus status, all main/secondary/raw IRQ statuses, IRQ pin state, AOD wake/IRQ state, `FX_CTRL2`, and ASRC status. The AOD chip also carries wake-enable state through wake-control register integration.

Dependencies and integration points: depends on Arizona core/register headers and regmap-irq. It integrates with the common Arizona/Madera parent, codec, jack/mic-detect, haptics, DRE/EDRE, ASRC/ISRC, SPDIF, SLIMbus, GPIO, and interrupt subsystems.

Risks and test signals: risks are table drift, patch values applied to the wrong revision, missing volatile entries for live status, and incomplete readable coverage for expanded WM8998 features. The SPI-style `write then read` concern does not apply here; access is via regmap I2C. Test signals include patch registration, regmap endian correctness, main/AOD IRQ delivery and wake behavior, readable access to AIF3/SPDIF/ASRC/DRE registers, and cache restore across suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm8998-tables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm97xx-core.c -->
## sources/distributed-fs/ceph-client/drivers/mfd/wm97xx-core.c

Purpose: this is the AC97 MFD core for Wolfson WM9705, WM9712, and WM9713 devices. It identifies the AC97 codec by vendor ID, creates a regmap over the AC97 compatibility layer, and registers codec and touchscreen child devices with shared platform data.

Important APIs, types, and functions: `struct wm97xx_priv` holds the AC97 compatibility handle, regmap, device, and child platform data. `wm97xx_readable_reg()` and `wm97xx_writeable_reg()` define common AC97 register access policy. `wm9705_regmap_config`, `wm9712_regmap_config`, and `wm9713_regmap_config` define chip-specific defaults and volatility. `wm97xx_ac97_probe()` and `wm97xx_ac97_remove()` implement the AC97 codec driver, registered by `wm97xx_module_init()` and unregistered by module exit.

Control flow: probe allocates private state, obtains an `snd_ac97` compatibility object, stores driver data, fills `wm97xx_platform_data` with AC97 and optional battery platform data, selects regmap config and MFD cell list from vendor ID, attaches the same platform data to every child cell, initializes an AC97 regmap, then registers child devices (`wm9705-codec`, `wm9712-codec`, or `wm9713-codec`, plus `wm97xx-ts`). Remove releases the compatibility object.

State and persistence: persistent state lives in the AC97 codec device driver data and child platform data. Regcache defaults capture codec reset state for mixer volumes, powerdown, sample rates, GPIO, digitizer, and model-specific controls. Vendor ID registers are readable but not writable. WM9712 marks `AC97_REC_GAIN` volatile in addition to default AC97 volatility.

Dependencies and integration points: depends on AC97 codec core, AC97 compatibility helpers, regmap AC97 support, MFD core, and WM97xx public headers. Child codec/touchscreen drivers receive shared AC97/regmap access through platform data.

Risks and test signals: probe can fail on unsupported vendor IDs, compatibility allocation failure, regmap init failure, or MFD child registration failure. Because cell platform data is written into static cell arrays, repeated probe/remove paths should be checked for safe reuse. Test signals include AC97 ID match, child devices appearing, regmap reads/writes honoring stride 2 and vendor ID write protection, touchscreen child receiving digitizer registers, and compat release on failed probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/wm97xx-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/misc/Kconfig

Purpose: this Kconfig menu defines build-time configuration for Linux miscellaneous drivers. It includes direct driver options for bus adapters, management channels, sensors, FPGA/configuration devices, memory/security interfaces, synchronization emulation, PCI helper devices, and sources submenus for larger misc-driver families.

Important APIs, types, and functions: this is declarative Kconfig rather than C. Symbols include `AD525X_DPOT`, `AD525X_DPOT_I2C`, `AD525X_DPOT_SPI`, `IBM_ASM`, `IBMVMC`, `RPMB`, `TI_FPC202`, `TIFM_CORE`, `ATMEL_SSC`, `ENCLOSURE_SERVICES`, `SGI_XP`, `SMPRO_ERRMON`, `QCOM_FASTRPC`, `SRAM`, `OPEN_DICE`, `NTSYNC`, `VCPU_STALL_DETECTOR`, `TPS6594_ESM`, `NSM`, `MARVELL_CN10K_DPI`, and `MCHP_LAN966X_PCI`, plus multiple `source` statements for subdirectories.

Control flow: Kconfig evaluation presents `menu "Misc devices"`, applies `depends on`, `select`, `default`, and `help` clauses, then includes child Kconfig files. The resulting symbols drive object inclusion in the corresponding Makefile. The AD525X symbols illustrate layering: common `AD525X_DPOT` depends on I2C or SPI plus sysfs, while transport options refine that to I2C or SPI master support.

State and persistence: selected symbols persist in the kernel `.config` and determine built-in/module/disabled states. Help text documents module names and user-facing interfaces. Defaults such as `TIFM_7XX1 default TIFM_CORE`, `MISC_RTSX default MISC_RTSX_PCI || MISC_RTSX_USB`, and TPS6594 defaults couple choices to parent MFD support.

Dependencies and integration points: integrates with top-level Kconfig, `drivers/misc/Makefile`, and sourced subdirectory Kconfigs. Dependency expressions tie misc drivers to subsystems such as I2C, SPI, PCI, OF, GPIOLIB, LEDS, RPMSG, DMA-BUF, SCM, VIRTIO, HW_RANDOM, MFD, regmap, IRQ domains, fault injection, and architecture/platform symbols.

Risks and test signals: incorrect `depends on` can expose drivers without required APIs, while incorrect `select` can force hidden dependencies. Module-name help can drift from Makefile object names. Test signals are `make olddefconfig`, `make menuconfig`, randconfig/allmodconfig builds, and checking that each visible symbol maps to a valid object or sourced subtree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/Makefile -->
## sources/distributed-fs/ceph-client/drivers/misc/Makefile

Purpose: this Makefile maps misc-driver Kconfig symbols to built-in objects, loadable modules, and subdirectory descents. It is the build-side counterpart to `drivers/misc/Kconfig`.

Important APIs, types, and functions: it uses kernel kbuild variables such as `obj-$(CONFIG_SYMBOL) += object.o` and composite object declarations for `lan966x-pci-objs`. Entries include AD525X common/I2C/SPI objects, IBM/POWER management drivers, sensor drivers, enclosure, SGI subdirectories, Qualcomm FastRPC, SRAM, endpoint test, security/virt helpers, TPS6594 children, CN10K DPI, and always-descended subdirectories such as `eeprom/`, `cb710/`, `lis3lv02d/`, `cardreader/`, `keba/`, and `amd-sbi/`.

Control flow: during kernel build, kbuild expands each `obj-*` line according to the configured symbol. `obj-y` entries are always entered for this directory build, though child contents still depend on their own Kconfig/Makefile choices. The LAN966x PCI driver is composed from `lan966x_pci.o` and a DT overlay object before being attached to `CONFIG_MCHP_LAN966X_PCI`.

State and persistence: build outputs are determined by `.config` and source timestamps. The Makefile itself carries no runtime state; it persists build topology and module naming conventions.

Dependencies and integration points: integrates with `drivers/misc/Kconfig`, per-driver source files, subdirectory Makefiles, kbuild composite object rules, and module autoload naming. The AD525X entries connect the common core object to transport-specific wrappers researched in this subset.

Risks and test signals: drift between Kconfig symbols and object names yields missing modules or dead options. Whitespace is mostly harmless but inconsistent entries can obscure review. Test signals are `make M=drivers/misc`, allmodconfig/randconfig link checks, and verifying module names match Kconfig help.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ad525x_dpot-i2c.c -->
## sources/distributed-fs/ceph-client/drivers/misc/ad525x_dpot-i2c.c

Purpose: this file is the I2C transport wrapper for the Analog Devices AD525x digital potentiometer core. It translates the common `ad525x_dpot` bus operations into SMBus byte/byte-data/word-data transactions and registers an I2C driver with a table of supported potentiometer part IDs.

Important APIs, types, and functions: bus callbacks `write_d8()`, `write_r8d8()`, `write_r8d16()`, `read_d8()`, `read_r8d8()`, and `read_r8d16()` populate `struct ad_dpot_bus_ops bops`. `ad_dpot_i2c_probe()` builds `struct ad_dpot_bus_data`, validates `I2C_FUNC_SMBUS_WORD_DATA`, and calls `ad_dpot_probe()`. `ad_dpot_i2c_remove()` calls `ad_dpot_remove()`. `ad_dpot_id[]` maps I2C modalias names to core chip IDs.

Control flow: I2C device matching invokes probe. Probe checks adapter SMBus word-data support, passes the client, ops table, `driver_data`, and part name to the shared core, then relies on the core for sysfs/state setup. Remove delegates cleanup to the shared core. `module_i2c_driver()` supplies module init/exit.

State and persistence: this wrapper holds no long-lived private state beyond what the shared core stores on the device. Hardware wiper/EEPROM state is accessed through SMBus transactions; sysfs persistence behavior is defined in the core.

Dependencies and integration points: depends on I2C/SMBus, module infrastructure, and local `ad525x_dpot.h`. It is built by `CONFIG_AD525X_DPOT_I2C` and paired with common `ad525x_dpot.o`.

Risks and test signals: requiring word-data support may reject adapters even for parts that only need byte operations. SMBus word endianness must match core expectations for 16-bit register values. Test signals include I2C modalias binding, SMBus functionality failure returning `-EIO`, core probe creating sysfs attributes, read/write operations on supported parts, and clean remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ad525x_dpot-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ad525x_dpot-spi.c -->
## sources/distributed-fs/ceph-client/drivers/misc/ad525x_dpot-spi.c

Purpose: this file is the SPI transport wrapper for the Analog Devices AD525x digital potentiometer core. It implements 8-, 16-, and 24-bit command/data exchanges with `spi_write()` and `spi_read()`, then registers a `spi_driver` for SPI-connected potentiometer parts.

Important APIs, types, and functions: bus callbacks `write8()`, `write16()`, `write24()`, `read8()`, `read16()`, and `read24()` populate `struct ad_dpot_bus_ops bops`. `ad_dpot_spi_probe()` constructs `struct ad_dpot_bus_data` and calls `ad_dpot_probe()` with `spi_get_device_id()` metadata. `ad_dpot_spi_remove()` delegates to `ad_dpot_remove()`. `ad_dpot_spi_id[]` maps SPI modalias strings to core IDs.

Control flow: probe passes SPI transport ops to the common core. Read helpers first issue a command write with the target register and zero data, then perform a separate SPI read of the expected transfer width; returned data is assembled big-endian from the receive buffer. Module lifecycle is generated by `module_spi_driver()`.

State and persistence: no wrapper-private runtime state is stored. Device state, sysfs attributes, and any nonvolatile wiper behavior are owned by the common AD525X core and the hardware. SPI transactions are immediate and synchronous.

Dependencies and integration points: depends on SPI core, module infrastructure, and `ad525x_dpot.h`; built by `CONFIG_AD525X_DPOT_SPI` with common `ad525x_dpot.o`. The driver advertises `MODULE_ALIAS("spi:ad_dpot")` in addition to the SPI ID table.

Risks and test signals: read helpers ignore errors from the preliminary command write, so a failed command phase can be masked by a later read result. Separate write/read transactions assume devices and controllers preserve command context across chip-select behavior; parts requiring full-duplex `spi_write_then_read()` semantics may be sensitive. Test signals include SPI modalias binding, correct command byte ordering for 16/24-bit operations, readback across supported chip IDs, sysfs core behavior, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/ad525x_dpot-spi.c -->
