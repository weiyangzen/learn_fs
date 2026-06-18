# subset-b-004243

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel-lpss-acpi.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/intel-lpss-acpi.c

Purpose: ACPI transport wrapper for Intel LPSS multifunction devices. It matches LPSS ACPI IDs, attaches per-generation clock rates and software-node properties for SPI, I2C, and UART child drivers, and delegates common initialization to `intel_lpss_probe()`.

Important APIs/types/functions: `intel_lpss_acpi_ids`, `intel_lpss_acpi_probe()`, `intel_lpss_acpi_remove()`, `platform_driver`, and `struct intel_lpss_platform_info`. Software nodes provide properties such as `intel,spi-pxa2xx-type`, I2C timing values, `reg-io-width`, `reg-shift`, and `snps,uart-16550-compatible`.

Control flow: probe obtains match data with `device_get_match_data()`, duplicates immutable platform info, fills MEM and IRQ resources from the ACPI platform device, calls the LPSS core, then marks and enables runtime PM. Remove calls the shared LPSS cleanup and disables runtime PM.

State and persistence: no persistent storage. Runtime state is devres-managed and owned by the LPSS core after probe. Runtime PM state is configured on the platform device.

Dependencies and integration: depends on ACPI/platform bus matching, Linux property/software-node APIs, `pxa2xx` SPI type definitions, and the shared `intel-lpss` core exported in namespace `INTEL_LPSS`.

Risks: ACPI ID table data must match the actual controller type and timing requirements. Bad firmware resources or missing IRQs surface in the shared core. Timing property mistakes can break I2C/SPI/UART child probing or board-level electrical timing.

Test signals: useful checks are ACPI modalias binding, successful child creation under `intel-lpss`, runtime PM suspend/resume, and boot logs on SPT/CNL/BXT/APL systems with I2C, SPI, and UART LPSS instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel-lpss-acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel-lpss-pci.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/intel-lpss-pci.c

Purpose: PCI transport wrapper for Intel LPSS controllers across many Intel SoC generations. It maps PCI IDs to LPSS platform descriptions and invokes the common LPSS MFD core.

Important APIs/types/functions: `intel_lpss_pci_probe()`, `intel_lpss_pci_remove()`, `intel_lpss_pci_ids`, `quirk_ids`, and per-family `intel_lpss_platform_info` records. Quirks include `QUIRK_IGNORE_RESOURCE_CONFLICTS` for specific Surface Go I2C resource conflicts and `QUIRK_CLOCK_DIVIDER_UNITY` for a Dell XPS clock-divider firmware bug.

Control flow: probe enables the PCI function with managed PCI helpers, allocates one IRQ vector, copies the matched platform info, fills BAR0 and IRQ vector, applies subsystem quirks, disables D3cold delay, enables bus mastering/MWI, calls `intel_lpss_probe()`, and allows runtime PM. Remove forbids runtime PM, synchronously resumes, and calls `intel_lpss_remove()`.

State and persistence: per-device LPSS state is allocated by the core. This file maintains only static match/property data. PCI power policy is adjusted through runtime PM and `d3cold_delay`.

Dependencies and integration: integrates PCI enumeration with the LPSS core, software-node properties, clock connector names, DesignWare I2C/UART, PXA2xx SPI, and idma64 child support through the core.

Risks: the huge PCI ID table is easy to regress when adding new platforms; wrong info records affect clock rate, SPI type, I2C timings, or UART clock lookup. Quirk matching is subsystem-specific, so overbroad IDs could hide real resource conflicts or force wrong dividers.

Test signals: PCI modalias binding, successful MFD child registration, runtime PM transitions, I2C/SPI/UART functional tests on affected generations, and targeted tests for Surface Go and Dell XPS quirk paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel-lpss-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel-lpss.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/intel-lpss.c

Purpose: shared Intel LPSS MFD core. It maps controller private registers, determines whether the device is I2C/UART/SPI, creates iDMA and host-controller child devices, builds clock lookup trees, exposes latency tolerance controls, and implements suspend/resume context handling.

Important APIs/types/functions: exported `intel_lpss_probe()`, `intel_lpss_remove()`, and `intel_lpss_pm_ops`; internal `struct intel_lpss`; MFD cells for `i2c_designware`, `dw-apb-uart`, `pxa2xx-spi`, and `idma64`; clock helpers; LTR/debugfs helpers.

Control flow: probe validates resources, ioremaps private registers, reads capabilities, selects the child cell by type, initializes reset/remap/DMA registers, allocates a stable MFD id, registers clocks, exposes PM QoS latency tolerance, adds debugfs, optionally registers idma64 first, then adds the host-controller child. Remove reverses child registration, debugfs, PM QoS, clocks, and ID allocation.

State and persistence: stores private register context in `priv_ctx` during system/runtime suspend and restores it on resume. Latency-tolerance values are cached for debugfs. No persistent disk state exists.

Dependencies and integration: used by ACPI and PCI wrappers. Integrates with MFD core, clk/clkdev, PM QoS, runtime/system PM, debugfs, idma64 DMA, and child serial/I2C/SPI drivers.

Risks: register ordering matters: DMA must appear before host controller, remap address must reflect parent resource, and non-UART devices are reset during suspend. Clock-tree unwind must match partial registration. Capability decoding errors create wrong child devices.

Test signals: child probe order, DMA fallback logs, clock lookup by child driver, latency tolerance sysfs/debugfs behavior, suspend/resume on UART console and non-UART controllers, and runtime PM under active transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel-lpss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel-lpss.h -->
# sources/distributed-fs/ceph-client/drivers/mfd/intel-lpss.h

Purpose: private interface shared by the Intel LPSS ACPI, PCI, and core source files. It defines platform data, quirk bits, and exported core entry points.

Important APIs/types/functions: `struct intel_lpss_platform_info`, `QUIRK_IGNORE_RESOURCE_CONFLICTS`, `QUIRK_CLOCK_DIVIDER_UNITY`, `intel_lpss_probe()`, `intel_lpss_remove()`, and `intel_lpss_pm_ops`.

Control flow: no executable flow. Bus-specific wrappers populate `intel_lpss_platform_info` with resources, IRQ, quirks, clock data, and software-node properties before calling the core.

State and persistence: the structure points to per-device MEM/IRQ resources and immutable board/platform properties. Runtime state is created by the implementation in `intel-lpss.c`.

Dependencies and integration: depends on `linux/pm.h`, `linux/bits.h`, and forward declarations for `struct device`, `struct resource`, and `struct software_node`. Namespaced exports are imported by ACPI/PCI modules.

Risks: this header is the contract between wrappers and core. Adding fields requires all platform-info initializers to be reviewed. Quirk semantics must stay narrow because they alter resource conflict and clock-divider behavior globally for a matched device.

Test signals: build coverage with both `CONFIG_MFD_INTEL_LPSS_ACPI` and `CONFIG_MFD_INTEL_LPSS_PCI`, module namespace import checks, and runtime validation that all platform-info fields are filled before core probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel-lpss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel-m10-bmc-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/intel-m10-bmc-core.c

Purpose: common Intel MAX 10 BMC core used by SPI and PMCI transports. It provides system-register access helpers, sysfs identification attributes, firmware-update handshake protection, and MFD child registration.

Important APIs/types/functions: `m10bmc_fw_state_set()`, `m10bmc_sys_read()`, `m10bmc_sys_update_bits()`, `m10bmc_dev_init()`, `m10bmc_dev_groups`, `struct intel_m10bmc`, and `struct intel_m10bmc_platform_info`.

Control flow: transport drivers initialize `intel_m10bmc` and call `m10bmc_dev_init()`. The core stores platform info, attaches drvdata, initializes `bmcfw_lock`, and registers configured child cells. Sysfs attributes read BMC firmware/build and MAC information through `m10bmc_sys_read()`.

State and persistence: `bmcfw_state` is protected by an rwsem and gates access to handshake register ranges during secure update phases. No persistent state is written; it exposes hardware state via sysfs.

Dependencies and integration: integrates with regmap, MFD core, MAX10 CSR maps, and downstream hwmon/retimer/security-update child drivers. Exported symbols use namespace `INTEL_M10_BMC_CORE`.

Risks: handshake register access must return `-EBUSY` during prepare/write secure-update phases to avoid firmware collisions. CSR maps must match hardware generation. MAC formatting assumes N3000 field layout for exposed registers.

Test signals: sysfs reads for version and MAC data, child-device creation per platform, secure-update transitions that block handshake registers, and regmap error propagation from both SPI and PMCI transports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel-m10-bmc-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel-m10-bmc-pmci.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/intel-m10-bmc-pmci.c

Purpose: DFL PMCI transport for Intel MAX 10 BMC on N6000-class FPGA devices. It implements indirect register access, flash FIFO bulk operations, flash host mux control, and registers MAX10 child devices.

Important APIs/types/functions: `m10bmc_pmci_probe()`, `indirect_reg_read()`, `indirect_reg_write()`, `m10bmc_pmci_flash_read()`, `m10bmc_pmci_flash_write()`, `m10bmc_pmci_flash_lock()`, `m10bmc_pmci_flash_unlock()`, and `m10bmc_pmci_flash_bulk_ops`.

Control flow: probe maps DFL MMIO, creates an indirect regmap over the controller command/address/data registers, initializes flash mutex state, attaches flash operations, and calls `m10bmc_dev_init()`. Register reads/writes issue commands and poll for ACK, then clear command state. Flash reads request host mux, use FIFO read commands, and release mux.

State and persistence: `flash_mutex` serializes flash reads and write sessions; `flash_busy` blocks reads during a locked write. Controller command completion is polling based; no persistent state is stored.

Dependencies and integration: depends on DFL bus, MMIO regmap custom read/write callbacks, MAX10 core, N6000 CSR constants, and child drivers `n6000bmc-hwmon` and `n6000bmc-sec-update`.

Risks: FIFO sizes, remainder handling, mux arbitration, and indirect command clearing are correctness-sensitive. Timeouts return errors but may leave hardware state needing cleanup. Write requires callers to hold the flash lock.

Test signals: DFL feature binding, regmap read/write smoke tests, flash read/write including sub-word remainders, concurrent read/write exclusion, host mux release on failures, and secure-update child flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel-m10-bmc-pmci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel-m10-bmc-spi.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/intel-m10-bmc-spi.c

Purpose: SPI transport for Intel MAX 10 BMC on N3000/D5005/N5010 boards. It builds an SPI AVMM regmap, rejects legacy unsupported BMC versions, and registers generation-specific MFD children.

Important APIs/types/functions: `intel_m10_bmc_spi_probe()`, `check_m10bmc_version()`, `m10bmc_spi_id`, `intel_m10bmc_regmap_config`, `m10bmc_n3000_csr_map`, and platform-info instances for N3000, D5005, and N5010.

Control flow: probe allocates `intel_m10bmc`, initializes `devm_regmap_init_spi_avmm()`, stores SPI drvdata, validates the legacy build register, then calls `m10bmc_dev_init()` with matched platform info. Platform info determines child cells and handshake register ranges.

State and persistence: no private runtime state beyond the common `intel_m10bmc` object. Firmware state and handshake locking are handled by the shared core when configured.

Dependencies and integration: depends on SPI device IDs, regmap SPI AVMM support, MAX10 core namespace, and child drivers for hwmon, retimer, and secure update.

Risks: `id->driver_data` must be valid for all matched devices. Legacy-version filtering is critical to avoid driving incompatible firmware. The regmap access table must cover system and flash address ranges required by children.

Test signals: SPI modalias binding for `m10-n3000`, `m10-d5005`, and `m10-n5010`, legacy rejection path, sysfs version reads, child device creation, and secure-update handshake behavior on N3000/D5005.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel-m10-bmc-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel_pmc_bxt.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/intel_pmc_bxt.c

Purpose: Intel Broxton/Apollo Lake PMC MFD driver. It exposes PMC GCR helpers, registers SCU IPC, and creates child devices for P-unit IPC, iTCO watchdog, and telemetry resources described by a single ACPI device.

Important APIs/types/functions: exported `intel_pmc_gcr_read64()`, `intel_pmc_gcr_update()`, `intel_pmc_s0ix_counter_read()`, `intel_pmc_probe()`, sysfs stores `simplecmd` and `northpeak`, `struct intel_pmc_dev`, and MFD cells `intel_punit_ipc`, `iTCO_wdt`, `intel_telemetry`.

Control flow: probe allocates PMC state, parses ACPI platform resources into SCU IPC/GCR/P-unit/TCO/telemetry resources, registers SCU IPC, stores drvdata, then adds available child devices. GCR helpers serialize MMIO access with `gcr_lock`.

State and persistence: GCR MMIO state lives in hardware. The driver stores mapped GCR base, optional telemetry base, and SCU IPC handle. S0ix residency is read from hardware counters and converted from 19.2 MHz ticks.

Dependencies and integration: relies on ACPI ID `INT34D2`, SCU IPC core, MFD core, iTCO watchdog platform data, telemetry child driver, and platform resources exported by IFWI.

Risks: resource index assumptions are firmware-contract sensitive. TCO registration is skipped when ACPI WDAT exists. `intel_pmc_gcr_update()` reads back to verify masked writes, so hardware side effects or locking bugs surface as `-EIO`.

Test signals: ACPI resource parsing, sysfs IPC commands, S0ix counter reads, child device enumeration, watchdog presence/absence with WDAT, and concurrent GCR helper callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel_pmc_bxt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel_quark_i2c_gpio.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/intel_quark_i2c_gpio.c

Purpose: PCI MFD splitter for Intel Quark I2C and GPIO controllers that share one PCI function. It creates DesignWare I2C and GPIO DW APB child devices with board-specific software-node properties.

Important APIs/types/functions: `intel_quark_mfd_probe()`, `intel_quark_i2c_setup()`, `intel_quark_gpio_setup()`, fixed I2C clock registration helpers, DMI table for Galileo/GalileoGen2/SIMATIC IOT2000, and two `mfd_cell` entries.

Control flow: probe enables PCI, allocates state, registers a 33 MHz fixed I2C clock lookup, enables bus mastering, allocates one IRQ vector, fills BAR/IRQ resources for I2C and GPIO cells, registers GPIO software-node group, and adds MFD devices. Remove reverses MFD devices, nodes, IRQ vectors, and clock.

State and persistence: only per-device clock lookup and software-node registration are retained. Static resource arrays are patched at probe time for the active PCI device.

Dependencies and integration: depends on PCI ID 0x0934, clk/clkdev, DMI, software-node APIs, `i2c_designware`, `gpio-dwapb`, and ACPI `_ADR` child matching.

Risks: static resource/cell mutation assumes one active device instance. GPIO node group must be unregistered on all failure paths. DMI selection controls I2C speed and must match board wiring.

Test signals: PCI bind/unbind, fixed clock lookup by `i2c_designware.0`, GPIO software-node children, board-specific I2C frequency on Galileo variants, shared IRQ handling, and error-path cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel_quark_i2c_gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel_soc_pmic_bxtwc.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/intel_soc_pmic_bxtwc.c

Purpose: MFD core for Broxton Whiskey Cove PMIC accessed through Intel SCU IPC. It provides an IPC-backed regmap, multi-level regmap IRQ domains, sysfs register access, and PMIC child devices.

Important APIs/types/functions: `bxtwc_probe()`, `regmap_ipc_byte_reg_read()`, `regmap_ipc_byte_reg_write()`, `bxtwc_add_chained_irq_chip()`, `bxtwc_add_chained_devices()`, regmap IRQ chips for level1, power button, TMU, BCU, ADC, charger, and critical events.

Control flow: probe validates ACPI `_HRV`, obtains IRQ and SCU IPC handle, initializes custom regmap, registers the level1 IRQ chip, chains secondary chips off virtual level1 IRQs, adds child MFD devices with the relevant IRQ domains, and applies the charger level1 unmask workaround.

State and persistence: `struct intel_soc_pmic` holds regmap, IRQ chip data, and SCU handle. Global sysfs `addr` chooses the PMIC register for privileged `val` reads/writes. Suspend/shutdown disable the parent IRQ.

Dependencies and integration: depends on ACPI `INT34D3`, SCU IPC PMIC access command, regmap IRQ, MFD children for thermal/GPIO/region/TMU/BCU/GPADC/USBC/charger, and `intel_soc_pmic` shared data.

Risks: nested IRQ domain setup must use the right parent vIRQ and domain. The global debug register address is shared across devices. IPC register addressing encodes I2C address in high bits and defaults to device1 when absent.

Test signals: `_HRV` filtering, interrupt delivery through each chained domain, charger IRQ unmask workaround, sysfs admin register access, suspend/resume IRQ disable/enable, and child driver probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel_soc_pmic_bxtwc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel_soc_pmic_chtdc_ti.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/intel_soc_pmic_chtdc_ti.c

Purpose: I2C MFD driver for Cherry Trail Dollar Cove TI PMIC. It creates a byte regmap, maps level1 PMIC interrupts through regmap-irq, and registers functional child devices.

Important APIs/types/functions: `chtdc_ti_probe()`, `chtdc_ti_shutdown()`, simple suspend/resume PM ops, `chtdc_ti_regmap_config`, `chtdc_ti_irq_chip`, and child cells for power button, ADC, thermal, power source, battery, and region.

Control flow: probe allocates `intel_soc_pmic`, initializes an I2C regmap with single-register reads, stores the IRQ, registers the regmap IRQ chip with `IRQF_ONESHOT`, and adds MFD children using the IRQ domain produced by regmap-irq. Shutdown and suspend disable the PMIC IRQ; resume re-enables it.

State and persistence: per-device state is limited to regmap, IRQ, and irq-chip data. Hardware interrupt mask/status registers hold volatile PMIC state.

Dependencies and integration: matches ACPI `INT33F5`; depends on I2C, regmap, regmap-irq, MFD core, and child drivers named `chtdc_ti_*`.

Risks: hardware cannot read multiple registers, so regmap configuration must keep single reads. Missing or bad IRQ prevents child interrupt routing. Level1 bit definitions drive child resource numbering.

Test signals: ACPI/I2C binding, regmap single-read behavior, child IRQ delivery, battery/power-source events, suspend/resume IRQ behavior, and MFD child enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel_soc_pmic_chtdc_ti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel_soc_pmic_chtwc.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/intel_soc_pmic_chtwc.c

Purpose: MFD core for Cherry Trail Whiskey Cove PMIC on I2C. It handles multi-address PMIC register access, model quirks via DMI, level1 regmap IRQs, and child device registration.

Important APIs/types/functions: `cht_wc_probe()`, `cht_wc_byte_reg_read()`, `cht_wc_byte_reg_write()`, `cht_wc_regmap_cfg`, `cht_wc_regmap_irq_chip`, DMI model table, and child cells for power source, external charger, region, and LEDs.

Control flow: probe checks ACPI `_HRV` equals `CHT_WC_HRV`, validates IRQ, allocates `intel_soc_pmic`, records model from DMI, initializes a custom 16-bit-address regmap that temporarily switches `client->addr`, registers a shared oneshot regmap IRQ chip, and adds child devices with the IRQ domain.

State and persistence: stores detected model in `pmic->cht_wc_model` for child behavior. Register access mutates the I2C client's address around each SMBus operation and restores it immediately.

Dependencies and integration: ACPI ID `INT34D3`, I2C SMBus byte access, regmap-irq, DMI board quirks, and shared PMIC child drivers.

Risks: changing `client->addr` requires serialized regmap access; callers must include high address bits or receive `-EINVAL`. `_HRV` separates Whiskey Cove variants sharing ACPI IDs. DMI matches affect device-specific behavior.

Test signals: `_HRV` rejection/acceptance, multi-address regmap reads/writes, interrupt mapping to children, DMI-specific model paths, LED/charger child probing, and suspend/resume IRQ handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel_soc_pmic_chtwc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel_soc_pmic_crc.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/intel_soc_pmic_crc.c

Purpose: Crystal Cove PMIC I2C MFD driver for Bay Trail and Cherry Trail Intel SoCs. It chooses platform-specific child sets, registers a regmap IRQ domain, and adds a PWM lookup for backlight use by Intel graphics.

Important APIs/types/functions: `crystal_cove_i2c_probe()`, `crystal_cove_i2c_remove()`, `crystal_cove_irq_chip`, BYT/CHT `crystal_cove_config` records, `crc_pwm_lookup`, and child cell arrays for power, thermal, BCU, ADC, charger, GPIO, PMIC region, and PWM.

Control flow: probe selects BYT or CHT config using `soc_intel_is_byt()`, creates I2C regmap, registers regmap IRQ chip, enables IRQ wake, adds the PWM lookup table, updates IRQ-domain bus token, then registers configured MFD children. Remove deletes PWM lookup and children.

State and persistence: per-device state stores regmap and IRQ chip data. Wake-enable state is requested for the parent IRQ. PWM lookup is global while the device is bound.

Dependencies and integration: ACPI `INT33FD`, I2C ID `intel_soc_pmic_crc`, platform-data SoC detection, PWM lookup table, regmap-irq, and child PMIC/GPIO/PWM drivers.

Risks: global PWM lookup must be removed on failure/remove. BYT and CHT expose different child sets. IRQ wake enabling may fail non-fatally. Domain token update avoids conflicts with child domains.

Test signals: BYT versus CHT child enumeration, IRQ wake warning path, PWM backlight lookup by graphics, GPIO/charger IRQ domain behavior, and bind/unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel_soc_pmic_crc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel_soc_pmic_mrfld.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/intel_soc_pmic_mrfld.c

Purpose: Basin Cove PMIC MFD driver for Merrifield platforms using Intel SCU IPC register access and firmware-provided level2 IOAPIC IRQ resources.

Important APIs/types/functions: `bcove_probe()`, `bcove_ipc_byte_reg_read()`, `bcove_ipc_byte_reg_write()`, `bcove_regmap_config`, `irq_level2_resources`, and child cells for power button, TMU, thermal, BCU, ADC, charger/power source, GPIO, and region.

Control flow: probe allocates `intel_soc_pmic`, obtains SCU IPC handle, initializes a custom IPC-backed regmap, reads seven platform IRQs into static resource entries, and registers all Basin Cove child devices. There is no separate regmap-irq chip because firmware services level1 IRQs.

State and persistence: static IRQ resource array is populated from ACPI/platform IRQs at probe. Register state is in hardware and accessed through SCU IPC byte operations.

Dependencies and integration: ACPI `INTC100E`, SCU IPC device APIs, MFD core, and child drivers named `mrfld_bcove_*`.

Risks: all expected IRQ resources must be present and ordered. Static resources assume a single active device. `devm_intel_scu_ipc_dev_get()` returning NULL is treated as allocation/probe failure, not defer.

Test signals: platform IRQ count/order, IPC regmap reads/writes, child device resources, charger and power-source sharing of IRQ slot 5, and ACPI binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/intel_soc_pmic_mrfld.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ioc3.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/ioc3.c

Purpose: SGI IOC3 PCI MFD driver. It configures the IOC3 multifunction ASIC, demultiplexes internal interrupts through an IRQ domain, and creates platform children for Ethernet, serial, keyboard, one-wire, RTC, and LEDs depending on subsystem ID.

Important APIs/types/functions: `ioc3_mfd_probe()`, `ioc3_setup()`, `ioc3_irq_domain_setup()`, `ioc3_irq_handler()`, per-subsystem setup functions, `ioc3_infos`, and `struct ioc3_priv_data`.

Control flow: probe enables PCI, sets latency and DMA mask, maps BAR0, clears interrupts, reads PCI subsystem ID, selects a board-specific setup routine, optionally creates an IRQ domain/chained handler, and adds child devices. Remove clears IRQs, removes MFD children/domain, unmaps BAR, and disables PCI.

State and persistence: tracks mapped IOC3 registers, PCI device, IRQ domain, and chained parent IRQ. Hardware IRQ enables/status and GPIO mode registers are programmed during setup.

Dependencies and integration: depends on SGI IOC3 register definitions, PCI bridge `map_irq`, Linux IRQ domains, MFD core, and child drivers such as `ioc3-serial8250`, `ioc3-eth`, `ioc3-kbd`, RTC drivers, `sgi_w1`, and `ip30-leds`.

Risks: board-specific wiring determines interrupt mapping and child composition. Error paths attempt to free IRQ/domain resources and must match setup state. Serial setup changes UART mode and waits for hardware. Only the first pending internal IRQ is handled per chained entry.

Test signals: boot on IP27/IP30/MENET/CAD DUO variants, child resource offsets, chained IRQ delivery for serial/kbd, Ethernet IRQ passthrough, RTC probing, and bind/unbind resource cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ioc3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ipaq-micro.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/ipaq-micro.c

Purpose: MFD driver for the Compaq iPAQ h3xxx Atmel microcontroller companion. It implements the custom serial protocol, queues synchronous messages, dispatches asynchronous keyboard/touchscreen events, and registers backlight, battery, key, touchscreen, and LED children.

Important APIs/types/functions: exported `ipaq_micro_tx_msg()`, `ipaq_micro_trigger_tx()`, `micro_process_char()`, `micro_rx_msg()`, `micro_serial_isr()`, `micro_reset_comm()`, and `micro_probe()`.

Control flow: probe maps UART and SDLC resources, resets serial communication, requests the shared IRQ, initializes queue/lock state, registers MFD cells, queries version, and dumps EEPROM data. TX messages are framed with SOF, id/length, payload, and checksum; RX is parsed by a small state machine and matched to pending synchronous messages or callbacks.

State and persistence: driver state includes current message, queued messages, RX/TX protocol state, callback hooks, and firmware version. EEPROM data is read for reporting and serial-number entropy but not written here.

Dependencies and integration: depends on SA1100-style UART registers, platform resources, `linux/mfd/ipaq-micro.h`, MFD child drivers, completions in message objects, and callbacks registered by input children.

Risks: locking spans callback dispatch and message completion; malformed checksum silently drops frames. `micro_tx_chars()` disables TX interrupts after each FIFO drain, so progress depends on the ISR/trigger model. EEPROM string conversion is simplistic.

Test signals: version request completion, queued synchronous message ordering, keyboard/touchscreen callback delivery, UART error logging, suspend/resume reinitialization, EEPROM dump, and child driver interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ipaq-micro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/iqs62x.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/iqs62x.c

Purpose: I2C MFD core for Azoteq IQS620A/621/622/624/625 sensors. It identifies calibrated device variants, optionally parses vendor firmware records, initializes event masks and ATI, broadcasts sensor events through a notifier chain, and registers keys/ALS/PWM/temp/position children.

Important APIs/types/functions: `iqs62x_probe()`, `iqs62x_firmware_parse()`, `iqs62x_dev_init()`, `iqs62x_irq()`, `iqs62x_firmware_load()`, exported `iqs62x_events`, `iqs62x_devs`, and `struct iqs62x_core`.

Control flow: probe initializes regmap and completions, reads product/software/hardware IDs, selects a descriptor after calibration checks, then requests firmware asynchronously. Firmware load parses records into write blocks, initializes registers, requests threaded IRQ, waits for ATI completion, and adds descriptor-specific children. IRQ reads the whole event window, maps bytes to event flags/data, handles reset/ATI, and notifies subscribers.

State and persistence: keeps firmware block list, device descriptor, UI selection, event cache, completions for firmware and ATI, notifier head, and hardware revision numbers. Power management waits for firmware completion and switches halt/normal modes.

Dependencies and integration: depends on firmware loader, regmap I2C, OF compatibles, notifier chain, MFD children, and `linux/mfd/iqs62x.h` event definitions used by child drivers.

Risks: async firmware means remove/suspend must wait for completion. Firmware parser bounds and product checks protect against bad blobs. ATI timing and communication-window delays are hardware-sensitive. Reset during IRQ reinitializes registers and may drop concurrent events.

Test signals: product/calibration detection, missing/invalid firmware paths, ATI completion timeout, notifier events to key/ALS/position children, reset recovery, suspend/resume power mode changes, and OF child compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/iqs62x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/janz-cmodio.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/janz-cmodio.c

Purpose: PCI MFD driver for Janz CMOD-IO MODULbus carrier boards. It exposes the carrier hex switch through sysfs and creates child devices for module slots selected by the `modules=` kernel parameter.

Important APIs/types/functions: `cmodio_pci_probe()`, `cmodio_probe_submodules()`, `cmodio_setup_subdevice()`, `modulbus_number_show()`, and `struct cmodio_device`.

Control flow: probe enables PCI, requests regions, maps PLX control BAR4, reads the hex switch, creates sysfs attributes, disables all module interrupt lines, then builds MFD cells/resources for non-empty module parameter entries and calls `mfd_add_devices()`. Remove unregisters children, sysfs, mapping, regions, and PCI state.

State and persistence: global module parameters name up to four slot drivers; `cmodio_id` provides unique child IDs. Per-device state stores control mapping, hex switch, cells, resources, and platform data.

Dependencies and integration: depends on PLX PCI IDs with Janz subsystem IDs, BAR3 MODULbus memory, BAR4 control registers, `linux/mfd/janz.h`, and downstream platform drivers named by user-supplied module strings.

Risks: no autodetection of submodules; wrong module parameters create wrong children. Static `cmodio_id` monotonically increases. All children share one IRQ through resource offset semantics relative to `irq_base`.

Test signals: module parameter parsing, no-module `-ENODEV` path, sysfs `modulbus_number`, child BAR offsets per slot, shared IRQ routing, and PCI bind/unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/janz-cmodio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/kempld-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/kempld-core.c

Purpose: Kontron PLD MFD core. It discovers supported boards via DMI, forced module parameter, or ACPI; serializes access to the PLD hardware mutex; exposes register helpers; reads firmware/spec information; and registers feature-driven child devices.

Important APIs/types/functions: exported `kempld_get_mutex()`, `kempld_release_mutex()`, `kempld_read8/16/32()`, `kempld_write8/16/32()`, `kempld_probe()`, `kempld_detect_device()`, and `kempld_platform_data_generic`.

Control flow: module init may create a DMI-backed platform device, then registers the platform driver. Probe chooses ACPI or DMI platform data, maps two IO ports, initializes locks, detects non-empty IO space, releases stale hardware mutex, reads PLD info/feature mask, and registers cells for I2C/watchdog/GPIO/UART according to feature bits.

State and persistence: `struct kempld_device_data` stores IO base, index/data ports, PLD clock, firmware info, feature mask, and a software mutex. Sysfs exposes version/spec/type. Hardware mutex state is external and shared with firmware.

Dependencies and integration: depends on DMI/ACPI tables, platform devices, IO port mapping, `linux/mfd/kempld.h`, and child drivers `kempld-i2c`, `kempld-wdt`, `kempld-gpio`, and `kempld-uart`.

Risks: hardware mutex acquisition can block while firmware holds access. DMI and ACPI paths intentionally avoid double probing. Forced IDs use substring matching. Register helpers require callers to hold the mutex.

Test signals: DMI and ACPI discovery, forced-device-id path, sysfs info fields, feature-mask child enumeration, mutex behavior under firmware access, and child register helper use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/kempld-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/khadas-mcu.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/khadas-mcu.c

Purpose: I2C MFD core for Khadas system control MCU. It creates a cached regmap with readable/writeable/volatile policy and registers user-memory and optional fan-control child devices.

Important APIs/types/functions: `khadas_mcu_probe()`, `khadas_mcu_reg_volatile()`, `khadas_mcu_reg_writeable()`, `khadas_mcu_regmap_config`, and MFD cells `khadas-mcu-user-mem` and `khadas-mcu-fan-ctrl`.

Control flow: probe allocates `struct khadas_mcu`, initializes an I2C regmap using the register policy callbacks and maple cache, registers the user-memory child, then registers the fan-control child only when the device-tree node has `#cooling-cells`.

State and persistence: per-device state stores device and regmap. Some MCU registers are marked volatile, while factory identity/version/MAC/USID fields are marked read-only. Persistent user data is represented by child drivers, not directly written here.

Dependencies and integration: depends on OF compatible `khadas,mcu`, I2C regmap, `linux/mfd/khadas-mcu.h` register definitions, and MFD children for user memory and fan control.

Risks: incorrect register policy can cache volatile command/status data or allow writes to identity fields. Optional fan child depends solely on DT cooling-cell property.

Test signals: DT binding, regmap read/write policy, cache behavior for volatile registers, user-memory child probing, fan child creation on cooling-capable boards, and I2C error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/khadas-mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/lm3533-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/lm3533-core.c

Purpose: I2C MFD core for TI LM3533 lighting controller. It provides shared register helpers, configures boost/output routing, enables the chip through GPIO, creates ALS/backlight/LED children from platform data, and exposes output routing sysfs attributes.

Important APIs/types/functions: exported `lm3533_read()`, `lm3533_write()`, `lm3533_update()`, `lm3533_i2c_probe()`, `lm3533_device_init()`, `lm3533_set_boost_freq()`, `lm3533_set_boost_ovp()`, and output route setters for HVLED/LVLED.

Control flow: probe allocates core state, initializes I2C regmap, stores IRQ/device, then `lm3533_device_init()` validates platform data, obtains HWEN GPIO, enables the chip, configures boost settings, registers optional ALS/backlight/LED MFD children, and creates sysfs attributes. Remove removes sysfs/children and disables HWEN.

State and persistence: stores child availability flags, regmap, IRQ, and hardware-enable GPIO. Hardware brightness/routing/boost registers persist only while powered. Sysfs visibility depends on child availability.

Dependencies and integration: depends on platform data (`struct lm3533_platform_data`), GPIO descriptors, regmap, MFD child drivers `lm3533-als`, `lm3533-backlight`, and `lm3533-leds`.

Risks: no platform data is fatal. Child init return values are not all propagated before sysfs creation, so partial child failures can be easy to miss. Platform data counts are clamped by modifying the pdata counts.

Test signals: platform-data variants with ALS/backlights/LEDs, HWEN GPIO behavior, boost register values, sysfs output route reads/writes, child probing, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/lm3533-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/lm3533-ctrlbank.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/lm3533-ctrlbank.c

Purpose: shared LM3533 control-bank helper library used by LM3533 backlight/LED children. It abstracts per-bank enable, current limit, brightness, and PWM-mask registers.

Important APIs/types/functions: exported `lm3533_ctrlbank_enable()`, `lm3533_ctrlbank_disable()`, `lm3533_ctrlbank_set_max_current()`, `lm3533_ctrlbank_set_brightness()`, `lm3533_ctrlbank_get_brightness()`, `lm3533_ctrlbank_set_pwm()`, and `lm3533_ctrlbank_get_pwm()`.

Control flow: helpers compute register offsets from the control-bank id and call parent `lm3533_read()`, `lm3533_write()`, or `lm3533_update()`. Enable/disable update one bit in the global control-bank enable register. Brightness and PWM access bank-specific registers.

State and persistence: no private state; it operates on `struct lm3533_ctrlbank`, which references the parent core, device, and bank id. Hardware registers hold brightness/current/PWM/enable state.

Dependencies and integration: depends on `linux/mfd/lm3533.h` parent helpers and is consumed by LM3533 child drivers rather than registering a device itself.

Risks: bank id validity is assumed for most helpers and must be established by callers/platform data. Current and PWM setters validate ranges; brightness does not constrain beyond `u8`.

Test signals: backlight/LED child calls for enable/disable, max-current boundary values, PWM values above `0x3f` returning `-EINVAL`, brightness readback, and regmap failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/lm3533-ctrlbank.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/lochnagar-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/lochnagar-i2c.c

Purpose: I2C core for Cirrus Logic Lochnagar audio accessory boards. It resets and identifies Lochnagar1/2, initializes board-specific regmaps and register patches, exports analogue-configuration synchronization, and populates child nodes from device tree.

Important APIs/types/functions: `lochnagar_i2c_probe()`, exported `lochnagar_update_config()`, `lochnagar_wait_for_boot()`, readable/volatile register callbacks, `lochnagar_configs`, and OF match data.

Control flow: probe obtains reset and optional present GPIOs, holds reset briefly, releases the board, creates the matched regmap, waits for boot by reading the reset/device-ID register, validates ID, reads firmware ID words, registers a regmap patch, and calls `devm_of_platform_populate()`. `lochnagar_update_config()` toggles Lochnagar2 analogue update and polls for acknowledgement while caller holds `analogue_config_lock`.

State and persistence: core state stores device, type, regmap, and analogue config mutex. Regmap cache is maple-backed; volatile callbacks prevent stale dynamic Lochnagar2 readings.

Dependencies and integration: depends on DT compatibles `cirrus,lochnagar1`/`2`, GPIOs, regmap, OF platform population, and `linux/mfd/lochnagar*.h` register maps used by child audio/GPIO/regulator components.

Risks: boot wait is fixed to 10 retries at 350 ms. Wrong OF match data or ID mismatch aborts probing. Analogue config update requires external lock discipline and only applies to Lochnagar2.

Test signals: reset/present GPIO behavior, ID and firmware logging, regmap patch application, OF child population, cache/volatile behavior, and analogue update polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/lochnagar-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/loongson-se.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/loongson-se.c

Purpose: Loongson Security Engine MFD controller. It allocates shared DMA command/data memory, initializes the controller, exposes engine command helpers, handles controller/engine interrupts, and registers RNG/TPM child devices.

Important APIs/types/functions: exported `loongson_se_init_engine()`, `loongson_se_send_engine_cmd()`, internal `loongson_se_send_controller_cmd()`, `loongson_se_poll()`, `se_irq_handler()`, `loongson_se_init()`, and `loongson_se_probe()`.

Control flow: probe allocates controller state, initializes completion/locks, reads `dmam_size`, allocates coherent DMA memory, maps MMIO, enables interrupts, requests all platform IRQs, starts the controller and passes DMA address/size, then registers `loongson-rng` and `tpm_loongson` children. Engine init divides DMA memory per engine, assigns command/return buffers, and sends a controller command describing the engine command buffer.

State and persistence: stores MMIO base, spinlock, controller completion, DMA base/size, engine-init mutex, and per-engine command/data buffers/completions. Hardware interrupt status is cleared in the ISR.

Dependencies and integration: ACPI ID `LOON0011`, platform property `dmam_size`, coherent DMA, MMIO register definitions in `loongson-se.h`, MFD core, and child RNG/TPM drivers.

Risks: `devm_kmalloc()` leaves fields uninitialized unless all paths set them; controller command struct fields beyond assigned values should be considered carefully. IRQ request failures are logged but do not abort. DMA partitioning assumes engine0 buffer can serve as command space.

Test signals: ACPI/property binding, DMA allocation size, controller start/set-DMA command completion, IRQ completion for controller and engines, child RNG/TPM engine initialization, timeout/error paths, and concurrent engine init serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/loongson-se.c -->
