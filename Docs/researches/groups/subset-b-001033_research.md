# Research Report: subset-b-001033

Grouped research for AHCI PCI and platform SATA drivers under `sources/distributed-fs/ceph-client/drivers/ata`. Each source file has a delimited section for deterministic reconciliation into source-tree-aligned per-file research reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci.c -->
## sources/distributed-fs/ceph-client/drivers/ata/ahci.c

Purpose: implements the PCI AHCI SATA low-level driver, binding a large PCI ID table to `ata_port_info` profiles, board quirks, power management, interrupt-vector setup, and libata/libahci host activation. It is the PCI edge driver over the shared AHCI core declared in `ahci.h`.

Important APIs and functions include `module_pci_driver(ahci_pci_driver)`, `ahci_init_one`, `ahci_remove_one`, `ahci_shutdown_one`, `ahci_pci_save_initial_config`, `ahci_pci_reset_controller`, `ahci_pci_init_controller`, `ahci_init_irq`, `ahci_configure_dma_masks`, `ahci_update_initial_lpm_policy`, and quirk-specific reset paths such as `ahci_vt8251_hardreset`, `ahci_p5wdh_hardreset`, and `ahci_avn_hardreset`. The `ahci_port_info[]` board table maps feature/chipset IDs to flags like `AHCI_HFLAG_NO_MSI`, `AHCI_HFLAG_NO_PMP`, `AHCI_HFLAG_INTEL_PCS_QUIRK`, 32/43-bit DMA restrictions, and custom port operations.

Control flow: probe rejects unsupported Marvell/PATA-overlap and ICH6 combined-mode cases, chooses a nonstandard BAR for selected vendors, enables and maps PCI resources, allocates `ahci_host_priv`, applies chipset/DMI/remapped-NVMe quirks, saves AHCI capabilities, allocates an `ata_host`, chooses MSI/MSI-X/INTx mode, annotates implemented ports, marks external/hotplug ports, computes initial LPM policy, applies DMI workarounds, configures DMA masks, resets and initializes the controller, prints AHCI capability info, sets bus mastering, and calls `ahci_host_activate`. Remove/shutdown undo sysfs state and delegate to libata PCI teardown.

State and persistence: persistent driver state is in `ahci_host_priv`, `ata_host`, PCI config registers, AHCI BAR registers, saved caps/port maps, module parameters (`marvell_enable`, `mobile_lpm_policy`, `mask_port_map`, `mask_port_ext`), runtime PM state, and a `remapped_nvme` sysfs attribute. Hardware-facing state includes PCS port enables, DMA mask selection, interrupt vectors, LPM policy, external-port flags, and DMI quirk decisions.

Dependencies and integration points: depends on PCI core, libata, libahci, SCSI host templates, DMI, PM runtime/system sleep, DMA mapping, sysfs, and Intel remap register definitions. Integration is through `ahci_ops`, `ahci_pmp_retry_srst_ops`, `ahci_host_activate`, exported AHCI helpers, PCI modalias matching, and libata error handling.

Risks: the PCI ID table and DMI quirk tables are high-regression surfaces; changing flags can break old chipsets, suspend/resume, LPM, MSI, PMP, DMA addressing, or hotplug. Module port masks can hide hardware. Remapped NVMe detection intentionally disables MSI. Reset quirks rely on timing and saved register semantics. Test signals include device probe logs, libata link bring-up, `remapped_nvme` sysfs value, interrupt mode in `/proc/interrupts`, suspend/resume cycles, hotplug/LPM behavior, and dmesg quirk messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci.h -->
## sources/distributed-fs/ceph-client/drivers/ata/ahci.h

Purpose: central AHCI header for register offsets, bit definitions, command/FIS/DMA layout sizes, host and port private structures, HBA flags, SCSI host template wiring, and function prototypes shared by PCI and platform AHCI edge drivers.

Important types and constants include `AHCI_MAX_PORTS`, `AHCI_MAX_CMDS`, command table/FIS sizes, `HOST_*` and `PORT_*` register offsets and bit masks, enclosure-management masks, `AHCI_HFLAG_*`, `AHCI_FLAG_COMMON`, `struct ahci_cmd_hdr`, `struct ahci_sg`, `struct ahci_em_priv`, `struct ahci_port_priv`, and `struct ahci_host_priv`. `AHCI_SHT()` builds the common SCSI template fields for AHCI drivers. Inline helpers `ahci_ignore_port`, `__ahci_port_base`, `ahci_port_base`, and `ahci_nr_ports` encode common addressing and port-filter behavior.

Control flow role: this file has no runtime flow itself, but it defines the shared ABI that lets libahci, PCI AHCI, and SoC-specific platform drivers coordinate. Edge drivers fill `ahci_host_priv` with MMIO, flags, clocks, resets, regulators, PHYs, IRQ handlers, and optional engine hooks before calling shared activation helpers.

State and persistence: `ahci_host_priv` caches immutable and mutable controller state such as saved caps, current caps, port maps, EM configuration, remapped NVMe count, resource handles, per-port PHY array, and optional callbacks. `ahci_port_priv` tracks command slots, DMA addresses, received FIS memory, FBS support/enabled state, interrupt mask, NCQ interrupt observations, and enclosure-management LED activity timers.

Dependencies and integration points: includes Linux PCI, clock, libata, PHY, regulator, and bit helpers. Declares exported/shared functions such as `ahci_save_initial_config`, `ahci_reset_controller`, `ahci_init_controller`, `ahci_do_softreset`, `ahci_do_hardreset`, `ahci_qc_issue`, `ahci_stop_engine`, `ahci_start_engine`, `ahci_host_activate`, `ahci_error_handler`, and `ahci_handle_port_intr`.

Risks: any change to register masks, structure layout, DMA sizing, or HFLAG semantics affects all AHCI drivers. Port filtering in `ahci_ignore_port` controls PHY/resource loops and can silently skip ports. Test signals are mostly integration-level: compile coverage of all AHCI edge drivers, successful libata probe, DMA command completion, FBS/PMP behavior, EM LED sysfs behavior, and suspend/resume resource handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_brcm.c -->
## sources/distributed-fs/ceph-client/drivers/ata/ahci_brcm.c

Purpose: Broadcom STB/NSP/BCM7216 AHCI platform driver that wraps `ahci_platform` with Broadcom top-control register setup, endian programming, PHY/reset handling, ALPM tuning, and a read-ID recovery sequence.

Important APIs and types include `struct brcm_ahci_priv`, `brcm_sata_readreg`, `brcm_sata_writereg`, `brcm_sata_init`, `brcm_sata_phy_enable`, `brcm_sata_phy_disable`, `brcm_sata_alpm_init`, `brcm_ahci_read_id`, `brcm_ahci_probe`, `brcm_ahci_suspend`, and `brcm_ahci_resume`. The custom `ahci_brcm_platform_ops` overrides `.host_stop` and `.read_id`.

Control flow: probe matches an OF compatible to a Broadcom version, maps the `top-ctrl` region, gets optional `rescal` and `ahci` resets, obtains AHCI resources, sets host flags (`WAKE_BEFORE_STOP`, `NO_WRITE_TO_RO`, and version quirks), resets/deasserts hardware, enables clocks and regulators, configures endianness before normal AHCI register access, reads implemented ports, enables Broadcom PHYs, tunes ALPM, enables libahci platform PHYs, and activates the host. Suspend disables PHYs, delegates AHCI suspend when available, asserts AHCI reset, and rearms rescal; resume reverses that ordering and resumes the host without double-counting resources.

State and persistence: private state tracks controller version, port mask, top-control base, quirk bits, and reset controls. Hardware state includes endian mode, PHY power/reset bits, ALPM timeout register values, clock/regulator/PHY enable counts, and per-port recovery changes. `brcm_ahci_read_id` can temporarily disable host interrupts, reset PHY/clock paths, recalibrate PHYs, and retry IDENTIFY.

Dependencies and integration points: depends on device tree compatibles, `linux/ahci_platform.h`, resets, Broadcom top-control registers, generic PHY APIs, libata read-ID flow, and libahci resource helpers.

Risks: resource ordering is strict because endian setup must precede AHCI MMIO use, and resume duplicates only part of `ahci_platform_resume`. The read-ID recovery path manipulates interrupts, clocks, and PHYs while probing devices, so failures can leave resources partially enabled if unwinding is wrong. Test signals include Broadcom registration logs, successful port-mask detection, IDENTIFY retry recovery, suspend/resume, ALPM wake behavior, and endian-correct operation on big-endian MIPS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_brcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_ceva.c -->
## sources/distributed-fs/ceph-client/drivers/ata/ahci_ceva.c

Purpose: CEVA/Xilinx AHCI platform driver that programs vendor-specific AXI/cache, OOB timing, PHY timing, Rx watermark, and speed policy registers from device tree before activating a two-port AHCI host.

Important APIs and types include `struct ceva_ahci_priv`, `ceva_ahci_read_id`, `ahci_ceva_setup`, `ceva_ahci_platform_enable_resources`, `ceva_ahci_probe`, `ceva_ahci_suspend`, and `ceva_ahci_resume`. `rx_watermark` is a module parameter, and `ceva,broken-gen2` plus multiple timing properties drive register programming.

Control flow: probe obtains AHCI resources and an optional reset, enables regulators/clocks/resets/PHYs using a CEVA-specific sequence, parses required DT arrays for COMINIT, COMWAKE, burst, and retry timing for both ports, detects DMA coherency for CCI cache settings, stores private data, calls `ahci_ceva_setup`, and activates the host. Resume re-enables the same resources, reruns CEVA register setup before `ahci_platform_resume_host`, and updates PM runtime state.

State and persistence: private state stores per-port PP2C/PP3C/PP4C/PP5C timing values, AXI cache setting intent, CCI/coherency flag, and broken Gen2 flag. Hardware state includes AHCI enable, AXI IDs/outstanding transfer limits, cache-control bits, PHY timing registers, port SControl speed/IPM, and powered PHY/reset state. `ceva_ahci_read_id` clears the DEVSLP support bit in IDENTIFY data because the controller does not support device sleep.

Dependencies and integration points: depends on device tree properties, optional reset control, generic PHY, `ahci_platform` resource helpers, libata identify data handling, and SCSI template `AHCI_SHT`.

Risks: DT timing properties are mandatory and byte/halfword casts depend on expected property sizes and endian behavior. The custom resource enable path has several unwind labels and must not leave PHYs initialized on failure. Broken Gen2 forces Gen1, reducing performance. Test signals include probe failure/warnings for missing DT properties, negotiated link speed, IDENTIFY DEVSLP masking, resume after system sleep, and coherent DMA correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_ceva.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_da850.c -->
## sources/distributed-fs/ceph-client/drivers/ata/ahci_da850.c

Purpose: TI DaVinci DA850 AHCI platform driver that initializes the SATA PHY from a functional clock plus reference clock, handles a power-down register, and works around DA850 reset/PMP detection quirks.

Important functions include `da850_sata_init`, `ahci_da850_calculate_mpy`, `ahci_da850_softreset`, `ahci_da850_hardreset`, and `ahci_da850_probe`. The custom `ahci_da850_port_ops` overrides soft reset, hard reset, and PMP hard reset.

Control flow: probe gets AHCI resources, ensures both `fck` and `refclk` clocks are available when bulk clock discovery found fewer than two, computes the PHY PLL multiplier from the reference clock, enables platform resources, maps the second memory resource as the power-down register, initializes PHY control, and activates the AHCI host. Soft reset first tries the libahci PMP value and retries with PMP zero on `-EBUSY`; hard reset retries several times before giving up.

State and persistence: state is mostly hardware state in the power-down register, PHY control register, clocks, and AHCI host private resources. No large private struct is stored. Reset behavior persists only through port operation hooks.

Dependencies and integration points: depends on device tree compatible `ti,da850-ahci`, clock framework, platform memory resources, `ahci_platform_get_resources`, `ahci_platform_enable_resources`, and libahci reset helpers.

Risks: invalid or non-divisible reference clock rates prevent probe. The second memory resource is required for power control. Retry behavior can hide marginal PHY instability but is necessary for documented PLL changes. Test signals include valid multiplier logs/errors, link detection with direct-attached disks and PMP-enabled configs, repeated hard-reset stability, and suspend/resume through generic `ahci_platform` PM ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_da850.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_dm816.c -->
## sources/distributed-fs/ceph-client/drivers/ata/ahci_dm816.c

Purpose: TI DaVinci DM816 AHCI platform driver that computes SATA PHY PLL multiplier bits from a reference clock, programs both port PHY control registers, and applies the same PMP/direct-drive soft-reset workaround used by related TI hardware.

Important functions include `ahci_dm816_get_mpy_bits`, `ahci_dm816_phy_init`, `ahci_dm816_softreset`, and `ahci_dm816_probe`. `ahci_dm816_port_ops` inherits from `ahci_platform_ops` and overrides `.reset.softreset`.

Control flow: probe gets resources, enables platform resources, initializes the PHY based on the second clock's rate, then calls `ahci_platform_init_host`. PHY init validates that two clocks exist, checks that the refclock is divisible by 100, maps the multiplier against `pll_mpy_table`, writes PLL/LOS/RX/TX settings for port 0, and writes remaining PHY settings for port 1. Soft reset retries with PMP zero if a PMP-style reset fails with `-EBUSY`.

State and persistence: state lives in clock/resource handles owned by `ahci_host_priv` and in the AHCI PHY registers. There is no driver-specific private allocation. The PLL output target and multiplier table are static policy.

Dependencies and integration points: uses `ahci_platform`, libata reset helpers, clock framework, OF compatible `ti,dm816-ahci`, and generic platform PM.

Risks: missing second reference clock, unusual clock rates, or mismatched multiplier table entries fail probe. The port 1 PHY setup assumes fixed values without a second PLL enable. Test signals include probe success with two clocks, correct link bring-up on both ports, direct-drive detection with PMP-capable config, and suspend/resume through generic platform PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_dm816.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_dwc.c -->
## sources/distributed-fs/ceph-client/drivers/ata/ahci_dwc.c

Purpose: Synopsys DesignWare AHCI platform driver that validates synthesized controller capabilities, initializes the 1 ms CCC/DevSlp timer, programs per-port DMA transaction sizes from DT child nodes, and preserves those settings across suspend/resume.

Important types and functions include `struct ahci_dwc_plat_data`, `struct ahci_dwc_host_priv`, `ahci_dwc_get_resources`, `ahci_dwc_check_cap`, `ahci_dwc_init_timer`, `ahci_dwc_init_dmacr`, `ahci_dwc_init_host`, `ahci_dwc_reinit_host`, `ahci_dwc_clear_host`, `ahci_dwc_probe`, `ahci_dwc_suspend`, and `ahci_dwc_resume`.

Control flow: probe allocates private data from OF match data, obtains resources with reset support, enables resources, optionally runs platform init, masks unsupported MPS/CPD/FBS capability bits based on DWC parameter registers, updates the 1 ms timer from `aclk`, parses available child ports for `snps,tx-ts-max` and `snps,rx-ts-max`, stores DMACR values, and activates the host. Suspend suspends the host then clears platform resources; resume re-enables resources, reruns optional reinit, restores timer and DMACR registers, and resumes the host.

State and persistence: private state records platform callbacks, the platform device, saved timer value, and saved per-port DMACR values. Hardware state includes DWC global parameter registers, timer, and port DMA control registers, some of which are not reset by HBA global reset and therefore need explicit persistence handling.

Dependencies and integration points: depends on OF match data for `snps,dwc-ahci` and `snps,spear-ahci`, `ahci_platform` reset/resource helpers, clock lookup by name, child-node DT properties, bitfield helpers, and libata host stop via custom `.host_stop`.

Risks: capability masking changes what libata exposes to users and devices. `ilog2` of invalid DT transaction sizes is not range-validated beyond hardware clamping. Timer correctness depends on the `aclk` clock rate. Test signals include warnings for unsupported synthesized features, DT child property parsing, preserved DMACR after resume, CCC/DevSlp timer behavior, and suspend/resume resource balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_dwc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_imx.c -->
## sources/distributed-fs/ceph-client/drivers/ata/ahci_imx.c

Purpose: Freescale/NXP i.MX AHCI platform driver for i.MX53, i.MX6Q, i.MX6QP, and i.MX8QM. It manages SoC-specific clocks, GPR PHY tuning, i.MX8 PHY calibration lanes, optional temperature reporting, no-device powerdown behavior, and custom reset/error handling.

Important types and functions include `struct imx_ahci_priv`, PHY CR helpers (`imx_phy_crbit_assert`, `imx_phy_reg_addressing`, `imx_phy_reg_write`, `imx_phy_reg_read`), `imx_sata_phy_reset`, temperature helpers (`__sata_ahci_read_temperature`, `sata_ahci_show_temp`), `imx8_sata_enable`, `imx_sata_enable`, `imx_sata_disable`, `ahci_imx_error_handler`, `ahci_imx_softreset`, `imx_ahci_parse_props`, `imx8_sata_probe`, `imx_ahci_probe`, suspend/resume hooks, and `ahci_imx_host_stop`.

Control flow: probe allocates private state, matches the SoC type, obtains SATA and reference clocks, for i.MX6 parses GPR13 PHY tuning properties from DT, for i.MX8 obtains SATA and calibration PHYs, gets AHCI resources, enables the SATA clock, optionally registers i.MX53 hwmon/thermal support, powers and configures SATA PHY resources, forces HWINIT bits for staggered spin-up and port 0 implementation, programs the 1 ms timer from the AHB clock on non-i.MX8, and activates the host. Error handling runs normal AHCI recovery, then on the first no-device result powers down non-i.MX8 links unless `ahci_imx.hotplug=1` is set.

State and persistence: `imx_ahci_priv` tracks clocks, GPR regmap, PHY handles, SoC type, first-time/no-device state, and computed PHY params. Persistent user-visible state includes hwmon `temp1_input`, thermal zone callbacks, and the `hotplug` module parameter. Hardware state includes GPR13 tuning, i.MX6QP reset/powerdown bits, i.MX8 PHY calibration/power, TIMER1MS, HOST_CAP/HOST_PORTS_IMPL edits, and PHY PDDQ powerdown.

Dependencies and integration points: depends on `ahci_platform`, libata, syscon/regmap, i.MX GPR definitions, clock framework, generic PHY, hwmon, thermal framework, device tree properties, and module params.

Risks: no-device powerdown makes later hotplug impossible without the module parameter. PHY register handshakes have short timeouts. Temperature reading temporarily rewrites PHY test registers and must restore them. DT tuning defaults may not fit all boards. Test signals include link bring-up per SoC, no-device powerdown log, hotplug behavior with module param, hwmon/thermal temperature reads, suspend/resume, and correct DT property validation messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_imx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_mtk.c -->
## sources/distributed-fs/ceph-client/drivers/ata/ahci_mtk.c

Purpose: MediaTek AHCI platform driver that enables the SoC SATA mode through a syscon phandle, sequences three optional resets, and then delegates normal host bring-up to `ahci_platform`.

Important types and functions include `struct mtk_ahci_plat`, `mtk_ahci_platform_resets`, `mtk_ahci_parse_property`, and `mtk_ahci_probe`. The port info uses generic `ahci_platform_ops`.

Control flow: probe allocates private data, gets AHCI resources, stores `plat_data`, parses optional `mediatek,phy-mode` to set `SYS_CFG_SATA_EN`, asserts and deasserts `axi`, `sw`, and `reg` reset controls in a fixed order, enables AHCI platform resources, and activates the host. PM is generic `ahci_platform_suspend`/`ahci_platform_resume`.

State and persistence: private state holds the syscon regmap and reset-control pointers. Hardware state includes the system configuration SATA enable bit and reset line states. No custom runtime state is kept after host activation.

Dependencies and integration points: depends on OF compatible `mediatek,mtk-ahci`, syscon/regmap phandle lookup, reset framework, `ahci_platform` resource handling, and libata/SCSI activation.

Risks: reset-control errors other than probe deferral are not explicitly checked for optional missing controls before assert/deassert calls, relying on reset framework behavior for optional handles. Incorrect `mediatek,phy-mode` phandle prevents SATA mode selection. Test signals include successful reset sequence, syscon bit programming, probe deferral on reset providers, link detection, and generic suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_mtk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_mvebu.c -->
## sources/distributed-fs/ceph-client/drivers/ata/ahci_mvebu.c

Purpose: Marvell EBU AHCI platform driver for Armada 380 and Armada 3700. It configures MBUS address windows or vendor-specific options and overrides engine stop to preserve FIS-based switching state across an erratum-prone stop transition.

Important types and functions include `struct ahci_mvebu_plat_data`, `ahci_mvebu_mbus_config`, `ahci_mvebu_regret_option`, `ahci_mvebu_armada_380_config`, `ahci_mvebu_armada_3700_config`, `ahci_mvebu_stop_engine`, `ahci_mvebu_probe`, and PM resume/suspend callbacks.

Control flow: probe selects platform data from OF, gets resources, ORs platform flags into `hpriv`, enables platform resources, installs `hpriv->stop_engine = ahci_mvebu_stop_engine`, runs the platform config callback, and activates the host. Armada 380 clears and reprograms up to four MBUS windows from `mv_mbus_dram_info` and enables the regret bit. Armada 3700 sets a vendor-specific bit and requests `AHCI_HFLAG_SUSPEND_PHYS`. Resume reruns platform config before resuming the host.

State and persistence: private state is static platform data attached through `hpriv->plat_data`. Hardware state includes MBUS window registers, vendor-specific regret/config bits, PHY suspend handling flags, and saved/restored `PORT_FBS` during engine stop.

Dependencies and integration points: depends on OF compatibles, Marvell MBUS API, `ahci_platform` resources, libahci engine hooks, and libata PM. The custom engine stop integrates through the callback stored in `ahci_host_priv`.

Risks: missing MBUS DRAM info fails Armada 380 probe. The engine-stop workaround is needed for PMP/FBS hot-swap erratum; changing it can break port multiplier behavior. Resume must restore vendor registers lost in low power. Test signals include MBUS window programming, PMP/FBS hot-swap stability, resume link recovery, and successful probe on both Armada compatible strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_mvebu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_octeon.c -->
## sources/distributed-fs/ceph-client/drivers/ata/ahci_octeon.c

Purpose: Cavium Octeon III SATA UCTL glue driver that programs endian and DMA read-command bits in a parent SATA shim, then populates child platform devices for the actual AHCI core.

Important function is `ahci_octeon_probe`; the driver binds OF compatible `cavium,octeon-7130-sata-uctl`. Register policy is concentrated in `CVMX_SATA_UCTL_SHIM_CFG` and endian/read-command bit definitions.

Control flow: probe maps the first platform resource, reads the UCTL shim config with Octeon CSR accessors, clears DMA and CSR endian fields, sets them according to compile-time CPU endianness, enables DMA read command behavior, writes the config back, validates that an OF node exists, and calls `of_platform_populate` to instantiate the child AHCI platform core.

State and persistence: state is entirely hardware shim configuration plus child devices created from the device tree. The driver itself does not keep private runtime state or implement remove/PM hooks.

Dependencies and integration points: depends on Octeon architecture CSR helpers, platform resource mapping, OF population, and a child `ahci-platform` node that performs actual SATA host operation.

Risks: incorrect endian programming breaks all AHCI register or DMA transactions below the shim. Because this is a parent glue driver, failures in child node descriptions show up after `of_platform_populate`. Test signals include correct child device creation, endian-correct I/O on big/little-endian kernels, successful AHCI child probe, and absence of UCTL-related DMA errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_octeon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_platform.c -->
## sources/distributed-fs/ceph-client/drivers/ata/ahci_platform.c

Purpose: generic AHCI platform driver for simple DT/ACPI-described AHCI controllers that need standard resources, optional resets, and no SoC-specific register programming.

Important functions and objects include `ahci_probe`, `ahci_port_info`, `ahci_port_info_nolpm`, `ahci_platform_sht`, OF match table entries (`generic-ahci`, legacy compatibles, Hisilicon, Octeon child), ACPI matches, and generic PM/shutdown hooks.

Control flow: probe gets AHCI platform resources with reset support, enables resources, applies a Hisilicon quirk to disable FBS and NCQ, chooses ACPI/OF match-provided port info or the default, and activates the host through `ahci_platform_init_host`. On failure it disables resources. Remove, shutdown, suspend, and resume are delegated to generic libata/libahci-platform helpers.

State and persistence: driver-specific state is minimal; `ahci_host_priv` from `ahci_platform_get_resources` owns MMIO, clocks, resets, regulators, PHYs, and flags. The ACPI `APMC0D33` path uses `ATA_FLAG_NO_LPM` via alternate port info.

Dependencies and integration points: depends on platform bus, OF/ACPI matching, `ahci_platform` resource helpers, libata, SCSI host template setup, and PCI class-code ACPI matching.

Risks: as the generic fallback, overly broad matches can bind controllers that actually need SoC-specific sequencing. The Hisilicon quirk changes exposed features globally for that compatible. Test signals include generic DT/ACPI probe, reset handling, link discovery, LPM disabled on `APMC0D33`, and clean resource disable on failed activation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_qoriq.c -->
## sources/distributed-fs/ceph-client/drivers/ata/ahci_qoriq.c

Purpose: Freescale/NXP QorIQ AHCI platform driver for multiple Layerscape/QorIQ SoCs. It programs PHY, transaction, AXI cache/coherency, and ECC-disable registers, and applies an LS1021A hard-reset register preservation erratum.

Important types and functions include `enum ahci_qoriq_type`, `struct ahci_qoriq_priv`, global `ecc_initialized`, `ahci_qoriq_hardreset`, `ahci_qoriq_phy_init`, `ahci_qoriq_probe`, and `ahci_qoriq_resume`. It supports OF and ACPI matching.

Control flow: probe gets AHCI resources, determines SoC type from OF or ACPI, maps optional `sata-ecc` resource only until ECC has been initialized, records DMA coherency, enables resources, stores private data, runs `ahci_qoriq_phy_init`, and activates the host with NCQ-capable port info. PHY init writes SoC-specific PHY and transaction constants, disables ECC via different bits per family when required, and writes AXI cache config for DMA-coherent devices. Resume re-enables resources, reruns PHY init, resumes host, and refreshes PM runtime state.

State and persistence: private state tracks SoC type, ECC address, DMA coherency, and register base intent. `ecc_initialized` is a module-global guard to avoid repeated ECC setup across controllers. Hardware state includes ECC disable bits, PHY tuning registers, transaction config, and AXI cache config. Reset state includes saved/restored `PORT_CMD` and `PORT_IRQ_STAT` on LS1021A hard reset.

Dependencies and integration points: depends on OF/ACPI match tables, platform resources, `ahci_platform`, libata reset helpers, device DMA attributes, and PM runtime.

Risks: global `ecc_initialized` can affect multi-controller ordering. Missing ECC resource on SoCs requiring it causes `-EINVAL`. Hard-reset workaround touches port command/interrupt state around COMRESET. Test signals include SoC-specific probe, ECC setup once, DMA-coherent AXI config, LS1021A reset stability, resume link recovery, and NCQ operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_qoriq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_seattle.c -->
## sources/distributed-fs/ceph-client/drivers/ata/ahci_seattle.c

Purpose: AMD Seattle AHCI platform driver that adds ACPI-bound AHCI support and optional SGPIO LED/enclosure-management integration when an SGPIO control resource is present and reports ports.

Important types and functions include `struct seattle_plat_data`, `seattle_transmit_led_message`, `ahci_seattle_get_port_info`, and `ahci_seattle_probe`. Two port-info profiles exist: generic AHCI and LED-capable AHCI with `ATA_FLAG_EM` and `ATA_FLAG_SW_ACTIVITY`.

Control flow: probe obtains resources, enables them, calls `ahci_seattle_get_port_info`, and activates the host. The port-info helper allocates private data, maps resource 1 as SGPIO control, reads the control register, falls back to generic AHCI if unavailable or no ports are reported, otherwise initializes EM metadata (`em_loc`, `em_buf_sz`, `em_msg_type`), stores private data, and selects LED-capable operations. LED transmit decodes PMP slot, updates activity/locate/fault bits for the ATA port in the SGPIO register, and records LED state under the port lock.

State and persistence: private state stores the SGPIO control MMIO pointer. Per-slot LED state is stored in `ahci_port_priv.em_priv`. Hardware state is the SGPIO control register's per-port activity/locate/fault bits. PM state is handled by generic `ahci_platform` suspend/resume.

Dependencies and integration points: depends on ACPI ID `AMDI0600`, `ahci_platform`, AHCI EM constants from `ahci.h`, libata LED/enclosure hooks, and generic PM.

Risks: if SGPIO mapping fails the driver silently degrades to generic behavior, so LED coverage can be missed. Bit layout assumes three bits per port starting at bit 8. Test signals include "SGPIO LED control is enabled" log, libata LED sysfs operations changing SGPIO bits, activity LED state persistence, and normal AHCI probe without SGPIO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_seattle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_st.c -->
## sources/distributed-fs/ceph-client/drivers/ata/ahci_st.c

Purpose: STMicroelectronics AHCI platform driver that handles ST-specific power and reset controls plus OOB timing programming before delegating to generic AHCI platform activation.

Important types and functions include `struct st_ahci_drv_data`, `st_ahci_configure_oob`, `st_ahci_deassert_resets`, `st_ahci_probe_resets`, `st_ahci_host_stop`, `st_ahci_probe`, `st_ahci_suspend`, and `st_ahci_resume`.

Control flow: probe allocates private data, gets AHCI resources, stores reset data in `plat_data`, obtains optional reset controls (`pwr-dwn`, `sw-rst`, `pwr-rst`) while tolerating missing ones, deasserts them, enables platform resources, writes ST OOB timing through the write-enable bit sequence, and activates the host with custom `.host_stop`. Suspend suspends the host, asserts power-down reset if available, and disables resources. Resume re-enables resources, deasserts resets, reprograms OOB timing, and resumes the host.

State and persistence: private state is the three reset-control handles. Hardware state includes reset line assertions and the OOB register timing values. Host stop asserts power-down before disabling resources.

Dependencies and integration points: depends on OF compatible `st,ahci`, reset framework, `ahci_platform`, libata host stop and PM flows, and MMIO OOB register definitions.

Risks: reset controls are optional, so board descriptions can alter power behavior substantially. OOB timing must be restored after low-power states. Failed reset assertion during suspend can leave resources enabled after host suspend. Test signals include reset-control logs, link negotiation after OOB programming, suspend/resume recovery, and clean host stop resource disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_st.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_sunxi.c -->
## sources/distributed-fs/ceph-client/drivers/ata/ahci_sunxi.c

Purpose: Allwinner sunxi AHCI platform driver that performs magic PHY bring-up/calibration, custom DMA transaction setup before engine start, and conservative PMP/MSI/DMA feature flags for sun4i/sun8i controllers.

Important functions include register bit helpers, `ahci_sunxi_phy_init`, `ahci_sunxi_start_engine`, `ahci_sunxi_probe`, and `ahci_sunxi_resume`. `enable_pmp` is a module parameter that gates PMP support.

Control flow: probe gets resources with reset support, installs `hpriv->start_engine = ahci_sunxi_start_engine`, enables resources, initializes the PHY with timed power-up and calibration loops, sets host flags to 32-bit DMA, no MSI, and forced NCQ, disables PMP unless the module parameter requests it, and activates the host. Resume repeats resource enable and PHY init before resuming the host. The custom start engine programs `P0DMACR` transaction/burst fields then sets `PORT_CMD_START`.

State and persistence: driver state is mostly host flags and the start-engine callback. Hardware state includes PHY control/status registers, RWCR, P0DMACR, and resource enable state. The `enable_pmp` module parameter is persistent configuration for the module instance.

Dependencies and integration points: depends on OF compatibles `allwinner,sun4i-a10-ahci` and `allwinner,sun8i-r40-ahci`, `ahci_platform`, libahci engine callback, reset/resource framework, and libata feature flags.

Risks: PHY initialization uses undocumented magic values and tight timeout assumptions. Enabling PMP can break directly attached disks per the driver comments. DMA transaction settings are inferred from related TI documentation. Test signals include PHY power-up/calibration success, direct disk detection with default PMP disabled, PMP-specific testing when enabled, NCQ operation, and resume link recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_sunxi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_tegra.c -->
## sources/distributed-fs/ceph-client/drivers/ata/ahci_tegra.c

Purpose: NVIDIA Tegra AHCI platform driver that performs complex Tegra SATA power-gate, reset, regulator, IPFS, backdoor class-code/capability, PHY tuning, and interrupt-unmask initialization for Tegra124/210/186.

Important types and functions include `struct sata_pad_calibration`, `struct tegra_ahci_soc`, `struct tegra_ahci_priv`, `tegra_ahci_handle_quirks`, `tegra124_ahci_init`, `tegra_ahci_power_on`, `tegra_ahci_power_off`, `tegra_ahci_controller_init`, `tegra_ahci_controller_deinit`, `tegra_ahci_host_stop`, and `tegra_ahci_probe`.

Control flow: probe gets AHCI resources, allocates Tegra private state, maps SATA/IPFS registers and optional AUX registers, obtains reset controls, the special SATA clock, and SoC-specific regulators, then runs controller init. Controller init powers regulators and powergate/clock/reset paths, programs FPCI BAR/access and SATA enable, writes electrical stability settings, OOB/squelch/COMWAKE timing, optional Tegra124 fuse-based pad calibration, PCI config-space emulation registers, AHCI class code, LPM capability backdoor bits, clock-gating/IDDQ settings, devslp quirks, and interrupt unmasking before activating the host. Host stop deinitializes and powers off.

State and persistence: private state tracks MMIO bases, resets, SATA clock, regulator bulk data, and SoC capability tables. Hardware state includes powergate state, reset lines, PHY/electrical tuning, emulated PCI config registers, AHCI capability backdoor bits, AUX DevSlp support bits, and interrupt masks. There is no implemented LP0 suspend support.

Dependencies and integration points: depends on Tegra fuse and PMC APIs, regulator bulk APIs, reset and clock frameworks, SoC-specific OF match data, `ahci_platform` resources, and libata host stop.

Risks: initialization order is strict; missing optional vs required resets vary by SoC. Fuse pad calibration affects signal integrity. The driver advertises/changes capabilities via backdoor registers, so regressions can alter LPM/NCQ behavior. Lack of suspend support is an operational limitation. Test signals include regulator/reset acquisition, powergate transition, SATA link stability at Gen speeds, interrupt delivery, fuse-calibrated PHY values, and clean deinit on failed host activation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_tegra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_xgene.c -->
## sources/distributed-fs/ceph-client/drivers/ata/ahci_xgene.c

Purpose: AppliedMicro/APM X-Gene AHCI platform driver for v1/v2 controllers, handling IP memory release, mux selection, PHY/channel programming, coherency/error registers, broken edge-triggered IRQ handling, PMP/FBS errata, IDENTIFY/SMART engine restart workarounds, and DEVSLP masking.

Important types and functions include `struct xgene_ahci_context`, `xgene_ahci_init_memram`, `xgene_ahci_restart_engine`, `xgene_ahci_qc_issue`, `xgene_ahci_read_id`, `xgene_ahci_set_phy_cfg`, `xgene_ahci_do_hardreset`, `xgene_ahci_hardreset`, `xgene_ahci_softreset`, `xgene_ahci_pmp_softreset`, `xgene_ahci_handle_broken_edge_irq`, `xgene_ahci_irq_intr`, `xgene_ahci_hw_init`, `xgene_ahci_mux_select`, and `xgene_ahci_probe`.

Control flow: probe obtains AHCI resources and extra core/diag/AXI/optional mux MMIO regions, resolves controller version from OF or ACPI, selects SATA on the mux, optionally skips clock/PHY init if memory is already initialized, otherwise toggles clocks, enables resources, releases IP RAM, configures both PHY channels, clears/enables interrupt and coherency registers, sets v1/v2 flags and IRQ handler, and activates the host. v1 port ops include custom soft/PMP reset, QC issue, read ID, and hard reset; v2 uses custom hard reset/read ID and the broken-edge IRQ handler.

State and persistence: private state stores last command per channel, last classified device class per channel, resource MMIO bases, and host pointer. Hardware state includes diagnostic RAM shutdown/readiness, PHY config registers, AXI coherency/error masks, mux selection, FBS.DEV/PxFBS state, saved port command/list/FIS registers across hard reset, and custom interrupt clearing order.

Dependencies and integration points: depends on OF/ACPI matching, `ahci_platform`, generic PHY/resource handling, libata command issue/reset/classification flows, and AHCI FBS/PMP data structures.

Risks: numerous hardware errata make command issue, reset, and interrupt ordering fragile. `xgene_ahci_hw_init` return is not checked in probe after call, so initialization errors can be masked. Version detection through ACPI CID can change behavior. Test signals include v1/v2 probe, mux selection, IP RAM readiness, PMP detection, IDENTIFY/SMART command stability under stress, broken-edge IRQ delivery, DEVSLP bit masking, and hard-reset recovery after link-down retries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/ahci_xgene.c -->
