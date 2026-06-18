# subset-b-004237 Research

Grouped research for the requested source files. Each section preserves the source path for downstream splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/mptspi.c -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/mptspi.c

Purpose: Fusion MPT SPI SCSI host driver for LSI/ATTO 53C1030/53C1035 PCI adapters. It binds the common Fusion MPT core to the Linux SCSI mid-layer and the SPI transport class, manages target negotiation, domain validation, RAID virtual/physical channels, reset recovery, and event-driven rescans.

Important APIs, types, and functions: `mptspi_driver_template` supplies the `Scsi_Host` callbacks; `mptspi_transport_functions` exposes SPI transport attributes; `mptspi_probe()` attaches the MPT IOC, allocates `Scsi_Host`, initializes lookup state, and starts `scsi_scan_host()`. Target/device state is carried in `VirtTarget`, `VirtDevice`, `MPT_SCSI_HOST`, and `MPT_ADAPTER`. Negotiation and config-page code centers on `mptspi_setTargetNegoParms()`, `mptspi_read_spi_device_pg0()`, `mptspi_write_spi_device_pg1()`, `mptspi_getRP()`, and setters such as `mptspi_write_period()`, `mptspi_write_width()`, `mptspi_write_qas()`.

Control flow: module init attaches the SPI transport, registers MPT completion/event/reset callbacks, then registers the PCI driver. Probe calls `mpt_attach()`, validates operational initiator-capable firmware, allocates the host, sets queue/SG limits, optionally enables the SPI transport, issues a bus reset if firmware requested it, and scans. SCSI target allocation establishes RAID-component mapping and initial SPI limits. Device configure initializes inquiry-based negotiation and runs DV unless an initial DV already occurred. I/O is delegated to `mptscsih_qcmd()` after local validity checks.

State and persistence: negotiation state lives in target SPI transport attributes and `VirtTarget` flags; firmware config pages persist requested/negotiated parameters. `ioc->spi_data` holds NVRAM, bus width, sync factors, IOC page data, SAF-TE policy, and global QAS disable. Workqueue wrappers asynchronously run RAID DV/rescan and reset renegotiation.

Dependencies and integration: depends on Fusion MPT core/scsih helpers, PCI, DMA coherent memory, SCSI mid-layer, SPI transport, RAID class, and firmware config/RAID action messages. It integrates with MPT event/reset dispatch and SCSI sysfs transport attributes.

Risks: config-page DMA sizes rely on firmware-provided page lengths; RAID quiesce timeout can hard-reset the IOC; target/channel remapping must stay consistent for RAID passthrough; global QAS disable for mixed targets affects all devices; asynchronous DV work races need valid host/target lifetime; `mptspi_read_parameters()` ignores read errors before decoding the stack struct.

Test signals: build with Fusion MPT SPI enabled, bind supported PCI IDs, verify host scan and `scsi_transport_spi` attributes, exercise tagged/wide/sync/DV negotiation, RAID volume and physical-disk channel behavior, integrated RAID domain-validation events, suspend/resume renegotiation, IOC reset recovery, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/mptspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/88pm800.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/88pm800.c

Purpose: MFD core for the Marvell 88PM800 PMIC. It initializes the shared 88PM80x I2C/regmap core, creates extra dummy I2C pages for power and GPADC blocks, configures GPADC and interrupt handling, then registers onkey, RTC, and regulator child devices.

Important APIs, types, and functions: `pm800_probe()` and `pm800_remove()` are the I2C driver lifecycle. `pm80x_init()`/`pm80x_deinit()` come from `88pm80x.c`. `pm800_pages_init()` creates `power_page` and `gpadc_page` dummy clients and regmaps. `device_800_init()` sequences RTC wake readout, `device_gpadc_init()`, `device_irq_init_800()`, and MFD child registration. `pm800_irq_chip` maps 20 logical interrupts over four status/enable registers.

Control flow: probe initializes the common chip, allocates `pm80x_subchip`, derives page addresses from the base I2C address, initializes page regmaps, initializes GPADC automatic measurements and bias, installs regmap-irq support, registers child cells, then calls optional platform configuration. Remove reverses child devices, IRQ chip, dummy pages, and common deinit.

State and persistence: per-device state is in `pm80x_chip` and `pm80x_subchip`; register changes persist in PMIC hardware. The RTC platform data is mutated with `rtc_wakeup` if `PM800_ALARM_WAKEUP` was set before IRQ setup cleared wake state. Static `mfd_cell` arrays are updated with platform data before registration.

Dependencies and integration: depends on I2C, regmap I2C, regmap IRQ, MFD core, `linux/mfd/88pm80x.h`, and child drivers named `88pm80x-onkey`, `88pm80x-rtc`, and `88pm80x-regulator`.

Risks: partial failures after adding child devices do not consistently remove every previously added device; static child descriptors can retain platform data across instances; dummy page creation has multiple exit paths but cleanup is only caller-driven; GPADC policy is platform-data-sensitive and can affect modem/battery readings.

Test signals: compile with `CONFIG_MFD_88PM800`, probe hardware with base plus page addresses, verify regmap IRQ domain and named child IRQs, confirm child driver binding, test RTC alarm wake propagation, GPADC measurement enablement, removal/unbind cleanup, and suspend/resume via shared PM ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/88pm800.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/88pm805.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/88pm805.c

Purpose: MFD core for the Marvell 88PM805 companion/audio PMIC. It initializes the common 88PM80x register layer, configures the PM805 interrupt block, and registers an `88pm80x-codec` child with microphone/headphone-short IRQ resources.

Important APIs, types, and functions: `pm805_probe()` and `pm805_remove()` implement the I2C lifecycle. `device_805_init()` validates the common regmap, sets `chip->regmap_irq_chip`, installs the IRQ chip through `device_irq_init_805()`, and adds the codec MFD cell. `pm805_irqs[]` maps 12 interrupt sources across two registers; `pm805_irq_chip` supplies status/mask/ack bases.

Control flow: probe calls `pm80x_init()`, retrieves the common chip from client data, initializes IRQs, registers the codec child, optionally calls platform `plat_config`, then returns the child init status. Remove removes children, deletes the regmap IRQ chip, and deinitializes shared 88PM80x state.

State and persistence: state is mostly in `pm80x_chip`, `chip->irq_data`, and hardware interrupt mask/status registers. PM805 also participates in the `88pm80x.c` companion-link workaround, where the first and second probed 88PM80x chips store each other as companions.

Dependencies and integration: depends on I2C, regmap, regmap IRQ, MFD core, and common 88PM80x helpers. Child integration is the `88pm80x-codec` platform device with `micin`, `audio-short1`, and `audio-short2` resources.

Risks: the probe path unconditionally reaches `pm80x_deinit()` after `device_805_init()` even on success because there is no success return before `err_805_init`, which can clear the global companion/shared state while the device remains bound. Some interrupt enum names and masks look cross-wired, so tests should validate actual IRQ routing against hardware. The 32 kHz-domain delay is essential after status-mode writes.

Test signals: build with `CONFIG_MFD_88PM805`, probe with an IRQ line, verify regmap IRQ registration, check codec child creation and named IRQ delivery, test companion linkage with PM800, exercise remove/unbind, and inspect probe success for unintended common-state deinit effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/88pm805.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/88pm80x.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/88pm80x.c

Purpose: Shared helper layer for Marvell 88PM800/805/860-family drivers. It provides the common 8-bit I2C regmap configuration, chip ID detection, companion-chip workaround, and suspend/resume wake IRQ handling used by `88pm800.c` and `88pm805.c`.

Important APIs, types, and functions: `pm80x_regmap_config` is exported. `pm80x_init()` allocates `pm80x_chip`, creates the regmap, reads `PM80X_CHIP_ID`, maps hardware ID fields through `chip_mapping[]`, stores client data, enables wake capability, and links companion clients. `pm80x_deinit()` tears down the global companion relation. `pm80x_pm_ops` is exported through `EXPORT_GPL_SIMPLE_DEV_PM_OPS`.

Control flow: child chip drivers call `pm80x_init()` from their I2C probe before device-specific initialization. Suspend/resume checks `chip->wu_flag` and `device_may_wakeup()` to toggle IRQ wake. Deinit assumes the global `g_pm80x_chip` points at the surviving shared relationship.

State and persistence: per-device state is devm-managed, but `g_pm80x_chip` is process-global mutable state. Companion pointers connect PM800/PM805 clients so one chip can access registers defined on the other. Hardware state is not reset here beyond wake capability.

Dependencies and integration: depends on I2C, regmap I2C, `linux/mfd/88pm80x.h`, and exported symbols consumed by sibling 88PM80x MFD cores.

Risks: global companion state is not protected by a lock and does not scale to multiple PM80x pairs; `pm80x_deinit()` dereferences `g_pm80x_chip` without a NULL check; incorrect probe/remove ordering can clear companion pointers while a sibling is active; ID detection error message names PM800 even for other chips.

Test signals: probe PM800 alone, PM805 alone, and paired PM800/PM805 in both orders; validate `chip->type`, companion pointers, wake IRQ enable/disable paths, remove ordering, and error behavior when chip ID reads fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/88pm80x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/88pm860x-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/88pm860x-core.c

Purpose: MFD core for Marvell 88PM8606/88PM8607 PMICs. It manages paired companion I2C chips, interrupt demultiplexing, oscillator reference voting, child-device registration for regulators, RTC, onkey, touch, power, codec, LEDs, and backlights, plus suspend wake handling.

Important APIs, types, and functions: `pm860x_probe()` allocates `pm860x_chip`, parses platform/DT data, creates primary and optional companion regmaps, and calls `pm860x_device_init()`. `device_8607_init()` verifies chip ID, configures BUCK/MISC registers, initializes IRQs, and registers PMIC children. `device_8606_init()` initializes oscillator, backlight, and LED children. Exported `pm8606_osc_enable()`/`pm8606_osc_disable()` implement vote-based oscillator control. Custom IRQ code includes `pm860x_irq()`, `pm860x_irq_sync_unlock()`, `pm860x_irq_domain_map()`, and `device_irq_init()`.

Control flow: probe requires platform data or DT-derived companion address/IRQ mode. It identifies 8606/8607 by I2C address, optionally creates a dummy companion client and regmap, initializes the primary role, then initializes the companion role if present. IRQ setup masks and clears status registers, allocates legacy IRQ descriptors/domain, and requests the threaded parent IRQ. Remove frees child devices/IRQ and unregisters the companion.

State and persistence: `pm860x_chip` stores primary/companion clients, regmaps, IRQ base/core IRQ, oscillator mutex/vote/status, BUCK3 mode, wake flag, and platform-derived mode. `pm860x_irqs[]` is a static table with mutable `enable` fields, so interrupt enable state is shared globally across device instances. Hardware mask/status and oscillator bits persist in the PMIC.

Dependencies and integration: depends on I2C, regmap, irqdomain, MFD core, charger-manager platform data, regulators, and exported low-level helpers from `88pm860x-i2c.c`. Child device names follow the `88pm860x-*` convention.

Risks: `pm860x_device_init()` returns 0 even if sub-initializers logged failures, so probe can succeed after partial child setup; static IRQ enable/cached mask state is not per-chip; `irq_domain_create_legacy()` return is not stored for removal; child registration failures are mostly logged and ignored; companion handling mixes devm and non-devm regmap lifetime.

Test signals: build with `CONFIG_MFD_88PM860X`, probe 8606, 8607, and paired companion setups; verify child devices, IRQ mask/unmask and nested IRQ dispatch, oscillator vote reference counting, suspend/resume wake IRQ, DT companion parsing, remove cleanup, and error-injection paths for companion/regmap/IRQ failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/88pm860x-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/88pm860x-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/88pm860x-i2c.c

Purpose: Low-level register access helpers for 88PM860x primary and companion I2C clients. It wraps regmap operations for normal registers and implements special page-mode read/write sequences with direct `i2c_msg` transfers.

Important APIs, types, and functions: exported helpers are `pm860x_reg_read()`, `pm860x_reg_write()`, `pm860x_bulk_read()`, `pm860x_bulk_write()`, `pm860x_set_bits()`, `pm860x_page_reg_write()`, and `pm860x_page_bulk_read()`. Internal `read_device()` and `write_device()` issue raw adapter `master_xfer` operations.

Control flow: normal helpers obtain `pm860x_chip` from client data, select `chip->regmap` or `chip->regmap_companion` by comparing the passed client to `chip->client`, and call regmap. Page helpers lock the I2C segment, perform the magic page-open register reads (`0xFA`, `0xFB`, `0xFF`), access the target register, perform page-close reads (`0xFE`, `0xFC`), and unlock.

State and persistence: no independent state is allocated here; it depends entirely on `pm860x_chip` client data and regmaps prepared by `88pm860x-core.c`. Page writes and normal writes persist in PMIC hardware registers.

Dependencies and integration: depends on I2C adapter operations, regmap, and `linux/mfd/88pm860x.h`. Symbols are exported for PMIC child drivers and the core.

Risks: `write_device()` uses a two-byte stack buffer but copies `bytes` payload plus one address byte, so callers must never pass `bytes > 1`; `read_device()` copies from `msgbuf1` even if `master_xfer` fails; page helpers ignore errors from page-open/page-close reads; direct `adap->algo->master_xfer` assumes the adapter algorithm is present and bypasses regmap locking/cache behavior.

Test signals: unit or hardware tests for primary versus companion regmap selection, single and bulk read/write, page open/close sequencing under concurrent I2C users, error propagation from `master_xfer`, and child-driver use of exported symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/88pm860x-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/88pm886.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/88pm886.c

Purpose: Modern devm-based MFD core for the Marvell 88PM886 PMIC. It validates the chip ID, initializes an 8-bit regmap, configures one regmap-irq chip, registers GPADC/onkey/regulator/RTC children, and installs a system power-off handler.

Important APIs, types, and functions: `pm886_probe()` is the only driver entry point. `pm886_setup_irq()` sets interrupt clear-on-write mode and calls `devm_regmap_add_irq_chip()`. `pm886_power_off_handler()` asserts `PM886_SW_PDOWN`. `pm886_devs[]` declares four MFD cells; `pm886_of_match[]` matches `marvell,88pm886-a1` and provides the expected ID.

Control flow: probe allocates `pm886_chip`, reads OF match data, creates regmap, reads and validates `PM886_REG_ID`, sets up IRQs, registers children with the regmap IRQ domain, registers power-off, and optionally initializes wakeup when `wakeup-source` is present.

State and persistence: device state is devm-managed in `pm886_chip`; interrupt configuration and powerdown bits live in PMIC registers. There is no explicit remove because devm tears down resources.

Dependencies and integration: depends on I2C, OF, regmap I2C, regmap IRQ, MFD core, sys-off registration, and child drivers named `88pm886-gpadc`, `88pm886-onkey`, `88pm886-regulator`, and `88pm886-rtc`.

Risks: only one compatible/ID variant is accepted; system poweroff behavior is registered unconditionally after child registration; IRQ setup assumes `client->irq` is valid enough for regmap-irq; child drivers depend on the regmap IRQ domain for their IRQ resources.

Test signals: probe through DT, validate ID mismatch failure, IRQ clear mode and onkey interrupt delivery, child binding, poweroff handler register write, wakeup-source behavior, and devm cleanup after probe-failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/88pm886.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/mfd/Kconfig

Purpose: Kconfig menu for Linux multifunction device drivers under `drivers/mfd`. It declares the selectable symbols, dependencies, and helper selections that decide which MFD core/interface drivers are built and which child subsystems can be reached.

Important APIs, types, and functions: this is declarative build configuration. Relevant symbols in this subset include `MFD_88PM800`, `MFD_88PM805`, `MFD_88PM860X`, `MFD_88PM886_PMIC`, `MFD_AAT2870_CORE`, `ABX500_CORE`, `AB8500_CORE`, and `MFD_AC100`. The file also defines common foundational symbols such as `MFD_CORE`, `MFD_AXP20X`, `MFD_ARIZONA`, and many bus-specific interface variants.

Control flow: the menu is gated by `HAS_IOMEM`. Each `config` block sets type (`bool`/`tristate`), prompts, dependency expressions, selected support libraries (`REGMAP_I2C`, `REGMAP_IRQ`, `IRQ_DOMAIN`, `MFD_CORE`, etc.), defaults, and help text. Downstream Makefiles consume these symbols through `obj-$(CONFIG_...)`.

State and persistence: no runtime state. The persistent effect is the kernel `.config`, which controls compilation, module/builtin form, and whether dependencies are forced through `select`.

Dependencies and integration: integrates with Kbuild and subsystem menus. It expresses hardware/bus constraints such as I2C-only PMICs, OF requirements, platform architecture requirements, and core helper dependencies.

Risks: `select` can force helper symbols without exposing all runtime prerequisites; `bool` choices such as `MFD_88PM860X`/`MFD_88PM886_PMIC` prevent modular builds; menu-wide `HAS_IOMEM` can hide drivers whose implementation is mostly I2C/RSB; Kconfig dependency drift can break builds if Makefile object mappings change without matching symbols.

Test signals: run `olddefconfig`, targeted `allyesconfig`/`allmodconfig`, and compile-test configurations; verify each symbol produces the expected objects; confirm dependency prompts appear/disappear correctly for I2C, OF, SUNXI_RSB, ARCH_U8500, and COMPILE_TEST cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/Makefile -->
# sources/distributed-fs/ceph-client/drivers/mfd/Makefile

Purpose: Kbuild object map for `drivers/mfd`. It translates Kconfig symbols into built-in or module objects, including composite object definitions for multi-file MFD drivers.

Important APIs, types, and functions: this file uses Kbuild variables such as `obj-$(CONFIG_...)`, `<module>-objs`, and conditional `ifeq` blocks. Relevant subset mappings include `88pm860x-objs := 88pm860x-core.o 88pm860x-i2c.o`, `obj-$(CONFIG_MFD_88PM860X) += 88pm860x.o`, `obj-$(CONFIG_MFD_88PM800) += 88pm800.o 88pm80x.o`, `obj-$(CONFIG_MFD_88PM805) += 88pm805.o 88pm80x.o`, `obj-$(CONFIG_MFD_88PM886_PMIC) += 88pm886.o`, `obj-$(CONFIG_ABX500_CORE) += abx500-core.o`, `obj-$(CONFIG_AB8500_CORE) += ab8500-core.o ab8500-sysctrl.o`, `obj-$(CONFIG_MFD_AAT2870_CORE) += aat2870-core.o`, and `obj-$(CONFIG_MFD_AC100) += ac100.o`.

Control flow: Kbuild evaluates configuration symbols and adds corresponding objects to the directory build. Composite object lists build several `.o` files into one module/built-in unit. Conditional table additions, such as Arizona/Madera codec tables, include variant-specific data only when their symbols are built in.

State and persistence: no runtime state. The persistent effect is the generated build graph and module composition.

Dependencies and integration: tightly coupled to `Kconfig` symbols and source filenames. It also encodes ordering notes, for example AB8500 must come after DB8500 PRCMU because the channel provider is needed first.

Risks: duplicate inclusion of shared helper objects such as `88pm80x.o` when both PM800 and PM805 are enabled can affect module composition and symbol ownership; Kconfig/Makefile mismatch causes silent missing drivers or build failures; ordering constraints are comments rather than enforceable dependency checks except by object order.

Test signals: build the MFD directory under configurations enabling each relevant symbol singly and together, inspect generated modules for composite contents, verify `modpost` symbol ownership, and test built-in link order for AB8500/DB8500 PRCMU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/aat2870-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/aat2870-core.c

Purpose: MFD core for the AnalogicTech AAT2870 backlight/regulator chip. It supplies raw I2C register access with a software cache, enable GPIO control, optional debugfs register access, child registration for backlight and LDO regulators, and suspend/resume register restore.

Important APIs, types, and functions: `aat2870_i2c_probe()` initializes `aat2870_data` and registers children. `__aat2870_read()`, `__aat2870_write()`, and `aat2870_update()` implement cached register access under `io_lock`. `aat2870_enable()`/`aat2870_disable()` drive the optional enable GPIO. Debugfs uses `aat2870_reg_read_file()` and `aat2870_reg_write_file()`. `aat2870_pm_ops` restores cached writeable registers on resume.

Control flow: probe requires platform data, copies pointers/callbacks, requests the enable GPIO, powers the chip, maps platform subdevice data onto static `aat2870_devs[]`, registers all cells, and creates debugfs when enabled. Suspend disables the chip; resume enables it and writes every cached writeable register.

State and persistence: `aat2870_data` stores client, callbacks, enable state, GPIO, mutex, and a pointer to static `aat2870_regs`. The register cache is static global storage, so values can persist across devices and probes. Hardware register state is restored from cache after resume.

Dependencies and integration: depends on I2C, legacy GPIO APIs, MFD core, regulator platform data, optional debugfs, and child drivers named `aat2870-backlight` and `aat2870-regulator`.

Risks: probe dereferences `pdata` without checking NULL; static register cache and static child descriptors are not per-device; debugfs write parsing attempts to parse the value from the same string position as the address, so writes may not behave as intended; no remove path disables hardware or removes MFD children except device core cleanup; legacy GPIO requirement limits portability.

Test signals: build with `CONFIG_MFD_AAT2870_CORE`, probe with complete platform data, verify child data mapping, register read/write/update locking, debugfs dump/write behavior, suspend/resume cache restore, enable GPIO polarity, and multiple-device behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/aat2870-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ab8500-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/ab8500-core.c

Purpose: Core MFD driver for ST-Ericsson AB8500/AB8505/AB9540/AB8540 mixed-signal power-management chips. It provides PRCMU-backed register access through the ABX500 abstraction, hierarchical interrupt demultiplexing, variant-specific child device creation, chip/status sysfs diagnostics, and suspend safety checks.

Important APIs, types, and functions: `ab8500_probe()` is the platform probe. Register access is implemented by `ab8500_prcmu_read()`, `ab8500_prcmu_write()`, `ab8500_prcmu_write_masked()`, and exposed through `ab8500_ops` registered with `abx500_register_ops()`. IRQ handling uses `ab8500_irq_chip`, `ab8500_irq_init()`, `ab8500_hierarchical_irq()`, `ab8500_handle_hierarchical_latch()`, and `ab8500_handle_hierarchical_line()`. Variant child arrays include `ab8500_devs`, `ab9540_devs`, `ab8505_devs`, `ab8540_devs`, and battery-management cells.

Control flow: probe allocates state, gets the parent IRQ, sets PRCMU accessors, detects version/revision, selects IRQ offset tables and latch hierarchy size, reads switch-off/turn-on reasons, masks/clears interrupt latches, registers ABX500 ops, creates an IRQ domain, requests the threaded parent IRQ, adds variant MFD cells and battery-management cells, then creates sysfs attribute groups depending on variant/cut.

State and persistence: `struct ab8500` holds locks, mask arrays, old masks, IRQ domain, transfer counter, version/chip ID, and access callbacks. `transfer_ongoing` blocks suspend while register/IRQ bus transfers are active. Static turn-on status override state is protected by `on_stat_lock` and affects AB9540 status reporting.

Dependencies and integration: depends on platform devices from DB8500 PRCMU, ABX500 core APIs, irqdomain, MFD core, OF matching for children, power supply children, and PRCMU ABB read/write functions.

Risks: sysfs group creation can overwrite `ret` and ignore earlier optional failures; ABX500 ops are not removed in this file; hierarchical IRQ mapping has variant-specific offset fixups that are easy to regress; register access relies on parent/child device relationships; mask arrays and GPIO rising/falling pairing require accurate IRQ type setup.

Test signals: probe each supported variant/cut, validate PRCMU register access, child creation, sysfs attributes, switch/turn-on status decoding, IRQ domain mappings and GPIO edge behavior, suspend rejection during transfers, and cleanup behavior on probe failure after ABX500 ops registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ab8500-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ab8500-sysctrl.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/ab8500-sysctrl.c

Purpose: AB8500 system-control child driver. It exposes read/write helpers for AB8500 system-control register banks and installs a platform power-off implementation that can reboot into charge-only mode when a charger and known battery are present.

Important APIs, types, and functions: exported `ab8500_sysctrl_read()` and `ab8500_sysctrl_write()` validate system-control banks and call ABX500 register helpers. `ab8500_power_off()` checks power supplies and writes `AB8500_STW4500CTRL1` shutdown/reset bits. `ab8500_sysctrl_probe()` sets the global device pointer and conditionally assigns `pm_power_off`.

Control flow: platform probe records `sysctrl_dev` and installs `pm_power_off` if empty. Poweroff checks AC/USB supply online state, checks battery technology, calls `machine_restart("charging")` when appropriate, otherwise blocks signals and sets software-off bits. Remove clears the global pointer and uninstalls the poweroff hook if it still owns it.

State and persistence: `sysctrl_dev` is global singleton state. Register writes persist to AB8500 hardware and may power off or reset the PMIC/system.

Dependencies and integration: depends on ABX500 core register ops, AB8500 sysctrl register definitions, platform bus, power_supply class, reboot/poweroff hooks, and signal-mask helpers.

Risks: singleton state supports only one sysctrl instance; `pm_power_off` is a global legacy hook and can conflict with other poweroff providers; poweroff depends on specific power-supply names (`ab8500_ac`, `ab8500_usb`, `ab8500_btemp`); exported helpers return `-EPROBE_DEFER` until probe.

Test signals: probe as AB8500 child, call exported read/write before and after probe, verify invalid-bank rejection, simulate charger/battery states for poweroff path, confirm charge-only restart, and test remove restores `pm_power_off`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ab8500-sysctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/abx500-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/abx500-core.c

Purpose: Generic ABX500 mixed-signal IC register-access dispatch layer. It lets specific chip cores register an `abx500_ops` implementation and lets child drivers call stable ABX500 helper functions without knowing the physical access backend.

Important APIs, types, and functions: `abx500_register_ops()` stores a devm-managed `abx500_device_entry` in a global list. `abx500_remove_ops()` deletes entries for a device. Exported dispatch functions include `abx500_set_register_interruptible()`, `abx500_get_register_interruptible()`, `abx500_get_register_page_interruptible()`, `abx500_mask_and_set_register_interruptible()`, `abx500_get_chip_id()`, `abx500_event_registers_startup_state_get()`, and `abx500_startup_irq_enabled()`.

Control flow: a chip core such as `ab8500-core.c` registers ops for its parent device. Child drivers pass their device; dispatch looks up `dev->parent` in the global list and invokes the matching callback if present, otherwise returns `-ENOTSUPP`.

State and persistence: state is the global `abx500_list`, containing copied ops and device pointers. Entries are devm-allocated but must be removed from the list explicitly or only remain valid as long as the parent device is live.

Dependencies and integration: depends on Linux device hierarchy, list APIs, devm allocation, exported symbols, and chip-specific `struct abx500_ops` providers.

Risks: global list has no locking, so concurrent registration/removal/lookup can race; devm-managed entries can become stale list nodes if not removed before device cleanup; child lookup assumes exactly one parent level; unsupported callbacks are reported as `-ENOTSUPP`, which callers must handle.

Test signals: register and remove ops, exercise all exported dispatchers from child devices, validate parent lookup failure, run concurrent child access during remove, and use KASAN/lockdep-style tests for stale list entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/abx500-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ac100.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/ac100.c

Purpose: MFD core for the X-Powers AC100 audio codec and RTC IC on Allwinner/Sunxi systems. It creates a 16-bit-value regmap over the Sunxi RSB bus and registers separate codec and RTC child devices.

Important APIs, types, and functions: `ac100_regmap_config` defines 8-bit registers, 16-bit values, writeable/volatile access tables, max register, and `REGCACHE_MAPLE`. `ac100_rsb_probe()` allocates `ac100_dev`, initializes the RSB regmap, and calls `devm_mfd_add_devices()` for `ac100-codec` and `ac100-rtc`. `ac100_of_match[]` matches `x-powers,ac100`.

Control flow: the `module_sunxi_rsb_driver()` macro registers the RSB driver. Probe stores driver data, creates the regmap with access constraints, then devm-registers child devices with OF-compatible names. There is no explicit remove path because devm owns allocations and child removal.

State and persistence: `ac100_dev` holds the device and regmap. Register cache state is managed by regmap; hardware state is owned by the codec/RTC children after registration.

Dependencies and integration: depends on `SUNXI_RSB`, regmap RSB support, MFD core, OF, and child drivers for `x-powers,ac100-codec` and `x-powers,ac100-rtc`.

Risks: access tables must exactly match AC100 register semantics or child drivers can see blocked writes/stale cached reads; no IRQ resources are declared here, so child interrupt support must come from elsewhere or polling; the driver only supports RSB transport.

Test signals: probe through DT on Sunxi RSB, verify regmap endianness/value width and cache behavior, bind codec and RTC children, run register access tests across writeable/volatile ranges, and inject regmap/MFD-add failures for devm cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ac100.c -->
