# subset-b-004276 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-dwcmshc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-dwcmshc.c

Purpose: this is the platform driver for Synopsys DesignWare Cores Mobile Storage Host Controller variants. It wraps the generic SDHCI platform layer and dispatches SoC-specific behavior through `struct dwcmshc_pltfm_data`, covering generic `snps,dwcmshc-sdhci`, Rockchip RK35xx/RK3576/RK3588, T-Head TH1520, Sophgo CV18xx/SG2042, Eswin EIC7700, Canaan K230, HPE GSC, and ACPI BlueField-3.

Important APIs, types, and functions: `struct dwcmshc_priv` stores common clocks, vendor-area offsets, match data, delay line, flags, and a SoC private pointer. `struct dwcmshc_pltfm_data` embeds `sdhci_pltfm_data` plus optional `init`, `postinit`, and CQHCI ops. The central ops are `dwcmshc_set_uhs_signaling`, `dwcmshc_reset`, `dwcmshc_adma_write_desc`, `dwcmshc_execute_tuning`, `dwcmshc_request`, and `dwcmshc_cqe_irq_handler`. Major variant paths include `dwcmshc_rk3568_set_clock`, `th1520_execute_tuning`, `cv18xx_sdhci_execute_tuning`, `sdhci_eic7700_executing_tuning`, `dwcmshc_k230_phy_init`, and HPE GSC syscon setup.

Control flow: `dwcmshc_probe()` selects match data, initializes SDHCI platform storage, expands ADMA descriptors for 128 MiB boundary splitting, enables core/bus/aux clocks, parses MMC/OF properties, reads vendor area pointers, overrides MMC ops, calls variant init, enables SDHCI v4 where supported, sets runtime PM active, runs `sdhci_setup_host()`, optionally initializes CQHCI from vendor area 2, calls postinit, and finally `__sdhci_add_host()`. Remove and PM paths reverse this: runtime PM is stopped, the SDHCI host is removed, card clock and clocks are disabled; suspend/resume handles CQHCI and clocks around `sdhci_suspend_host()`/`sdhci_resume_host()`.

State and persistence: persistent driver state is all in devm/platform allocations and hardware registers. The file preserves no filesystem state. Hardware state includes vendor-area controls, PHY/DLL delay values, CQHCI config, clock rates, resets, syscon bits, and private flags such as fixed 1.8 V signaling. Runtime suspend only gates the card clock, while system suspend disables core, bus, and auxiliary clocks.

Dependencies and integration points: it depends on SDHCI core, `sdhci-pltfm`, MMC host ops, common clock/reset/regmap/syscon APIs, runtime PM, ACPI/SMCCC for BlueField, and CQHCI. Device-tree/ACPI match tables are the main integration contract; properties such as `supports-cqe`, `rockchip,txclk-tapnum`, `eswin,hsp-sp-csr`, `eswin,drive-impedance-ohms`, `hpe,gxp-sysreg`, and Canaan USB PHY phandles affect behavior.

Risks: tuning and clock code is highly timing-sensitive. Incorrect vendor-area offsets, missing clocks, or wrong reset sequencing can break enumeration or high-speed modes. ADMA/CQHCI 128 MiB boundary splitting must remain consistent with descriptor sizing. Several functions intentionally clear command-complete, buffer, or data-reset state to work around silicon issues; changing ordering can reintroduce spurious interrupts or low-power failures. K230/EIC7700/HPE paths depend on syscon side effects outside the SDHCI register block.

Test signals: useful tests include probe/remove on each compatible, eMMC/SD/SDIO enumeration, HS200/HS400/HS400ES tuning, CQE enable/disable/recovery, suspend/resume and runtime PM, DMA transfers crossing 128 MiB boundaries, and fault injection for missing clocks/resets/syscon phandles. Kernel logs for DLL lock timeouts, tuning failures, CQE init failures, and clock-stability warnings are strong diagnostic signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-dwcmshc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-esdhc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-esdhc.c

Purpose: this driver adapts Freescale/NXP eSDHC OF controllers to the SDHCI core. eSDHC exposes mostly 32-bit registers with non-standard bit layouts, so the file provides endian-specific read/write shims, clock/tuning workarounds, voltage switching, DMA setup, and SoC errata handling.

Important APIs, types, and functions: `struct sdhci_esdhc` records vendor/spec versions, errata booleans, peripheral clock, clock fixups, and the active divider ratio. `struct esdhc_clk_fixup` caps timing-specific clocks for affected LS/P-series SoCs. Register access is normalized by `esdhc_readl_fixup`, `esdhc_readw_fixup`, `esdhc_readb_fixup`, and matching write fixups used by BE/LE `sdhci_ops`. Other key functions are `esdhc_of_set_clock`, `esdhc_execute_tuning`, `esdhc_signal_voltage_switch`, `esdhc_reset`, `esdhc_of_enable_dma`, and `esdhc_irq`.

Control flow: `sdhci_esdhc_probe()` chooses big- or little-endian platform data from the `little-endian` property, installs MMC host callbacks for voltage switching, tuning, and HS400 DDR preparation, calls `esdhc_init()` to detect host version, SoC quirks, peripheral clock, and DMA clock source, applies OF/MMC properties and SoC-specific quirks, parses voltage ranges, then adds the host. During I/O, SDHCI register access flows through the fixup layer, which merges transfer mode with command writes, remaps host-control DMA bits, masks unsupported capabilities, and preserves old hardware layouts.

State and persistence: state is volatile in `struct sdhci_esdhc` plus hardware registers. `esdhc_proctl` is a static suspend scratch value for host-control restore. Tuning state includes `in_sw_tuning` and `div_ratio`; suspend can request retuning when the mode is not tuning mode 3. No persistent disk state is produced.

Dependencies and integration points: the driver integrates with `sdhci-pltfm`, `sdhci-esdhc.h` register definitions, OF matching, `soc_device_match()` errata tables, common clock API, DMA coherency from OF, SCFG syscon-like IO mapping for voltage select, and MMC tuning/HS400 callbacks.

Risks: the biggest risk is register translation drift: the core assumes standard SDHCI semantics while hardware uses eSDHC placement. Tuning errata paths mix hardware and software tuning, reduced clocks, tuning-block windows, and DLL setup; small order changes can cause false tuning success. Voltage switching maps a global matching SCFG node and ioremaps it dynamically, so platform description mistakes can affect unrelated hosts. The static `esdhc_proctl` is shared across instances, which is a multi-host suspend/resume risk.

Test signals: validate BE and LE systems, host-version fixups, clock fixups per compatible, P2020/P1010/LS errata, DMA coherent and non-coherent paths, HS200/HS400 tuning including erratum fallback, 1.8 V switching through SCFG and direct PROCTL, suspend/resume with retune, and ADMA block-gap workaround behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-esdhc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-hlwd.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-hlwd.c

Purpose: this is a compact OF platform driver for the Nintendo Wii Hollywood SDHCI controller. It reuses the big-endian 32-bit byte-swapped SDHCI accessors and adds a small post-write delay required by the hardware.

Important APIs, types, and functions: the file defines `sdhci_hlwd_writel`, `sdhci_hlwd_writew`, and `sdhci_hlwd_writeb`, each delegating to `sdhci_be32bs_*` and then calling `udelay(SDHCI_HLWD_WRITE_DELAY)`. `sdhci_hlwd_ops` supplies the SDHCI core callbacks, while `sdhci_hlwd_pdata` declares 32-bit DMA address and size quirks.

Control flow: `sdhci_hlwd_probe()` simply calls `sdhci_pltfm_init_and_add_host()` with the local platform data. Once registered, generic SDHCI handles clock, bus width, reset, and UHS signaling. Remove and PM use the shared `sdhci_pltfm_remove` and `sdhci_pltfm_pmops`.

State and persistence: the driver owns no private data and persists nothing. Runtime state is the generic SDHCI host plus hardware registers. The only behavioral state is the enforced delay after every write callback.

Dependencies and integration points: it integrates through compatible string `nintendo,hollywood-sdhci`, `sdhci-pltfm`, MMC core, and the platform bus. It depends on the existing big-endian byte-swapped accessor helpers.

Risks: the critical risk is write-posting or bus timing sensitivity; removing or shortening the delay can corrupt controller operation. The driver assumes generic SDHCI reset/clock/UHS handling is sufficient and does not parse custom OF properties. DMA behavior depends on the two 32-bit quirks matching the hardware.

Test signals: successful probe on Wii hardware or an accurate emulator, stable card detect/enumeration, PIO/DMA read/write tests, suspend/resume through platform PM, and absence of intermittent errors after register writes are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-hlwd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-k1.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-k1.c

Purpose: this is the SpacemiT K1/K3 SDHCI platform driver. It adds SoC-specific PHY, DLL, clock, reset, HS200/HS400, and enhanced-strobe handling around the generic SDHCI platform layer.

Important APIs, types, and functions: `struct spacemit_sdhci_host` holds `core` and `io` clocks, with `pltfm_host->clk` assigned to the IO clock. Helper functions `spacemit_sdhci_setbits`, `clrbits`, and `clrsetbits` perform read-modify-write on vendor registers. Key callbacks are `spacemit_sdhci_reset`, `spacemit_sdhci_set_uhs_signaling`, `spacemit_sdhci_set_clock`, `spacemit_sdhci_phy_dll_init`, HS400 transition callbacks, and `spacemit_sdhci_hs400_enhanced_strobe`.

Control flow: `spacemit_sdhci_probe()` selects K1 or K3 platform data from OF, initializes SDHCI private storage, parses MMC properties, applies SDHCI OF properties, installs HS400 callbacks when MMC is present, marks `MMC_CAP_NEED_RSP_BUSY`, enables required clocks and optional resets, then calls `sdhci_add_host()`. During reset-all, the PHY is enabled, pad drive and RX bias are configured, and MMC card mode is set when applicable. Clock changes select internal TX clock for slower SDR modes and normal TX path for faster modes.

State and persistence: state is volatile: enabled clocks, deasserted resets, vendor register bits for HS200/HS400/enhanced strobe, DLL lock state, and MMC caps. No persistent data is written. DLL configuration is reinitialized on HS400 transitions and enhanced-strobe enable.

Dependencies and integration points: the driver uses OF match data for `spacemit,k1-sdhci` and `spacemit,k3-sdhci`, clock names `core` and `io`, reset names `axi` and `sdh`, MMC HS400 callbacks, `sdhci-pltfm`, and standard SDHCI ops.

Risks: K1 marks broken 64-bit DMA while K3 does not; applying the wrong compatible can corrupt DMA. DLL lock waits only 100 us and warns on timeout but continues, so high-speed instability can be deferred to data errors. HS400 downgrade toggles PHY and mode bits with fixed delays, so ordering is important.

Test signals: probe with both compatibles, clock/reset failure paths, SDR/HS200/HS400 transitions, HS400 enhanced strobe on/off, eMMC and SDIO capability masking, DMA under K1 32-bit constraints, and warnings for failed DLL lock are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-k1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-ma35d1.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-ma35d1.c

Purpose: this platform driver supports the Nuvoton MA35D1 SDHCI controller. It adds command-conflict clock gating rules, 128 MiB ADMA boundary splitting, pinctrl-assisted voltage switching, reset-before-tuning behavior, syscon voltage-stable setup, and removal-time card clock disable.

Important APIs, types, and functions: `struct ma35_priv` stores reset control and optional pinctrl states. `restore_data[]` lists SDHCI and vendor registers saved around tuning reset. `ma35_adma_write_desc` splits descriptors crossing 128 MiB boundaries. `ma35_set_clock` toggles `MA35_SDHCI_CMD_CONFLICT_CHK` based on whether the target clock exceeds 52 MHz. `ma35_execute_tuning` saves registers, asserts/deasserts reset, restores registers, then delegates to `sdhci_execute_tuning()`.

Control flow: `ma35_probe()` initializes platform data, expands ADMA table count using DMA mask size, enables an optional unnamed clock, parses MMC/OF properties, gets reset control, initializes optional pinctrl states, optionally sets a system-controller voltage-stable bit and overrides voltage switching, overrides execute tuning, adds the host, and finally programs MBIU burst chunks. Voltage switch selects `state_uhs` or `default` before generic SDHCI voltage switching.

State and persistence: persistent driver state is in devm-managed private data and hardware registers. The tuning path temporarily captures register values in a stack array and restores them after controller reset. Pinctrl state and syscon bits remain in hardware only; no filesystem state exists.

Dependencies and integration points: integrates with `sdhci-pltfm`, reset framework, optional clocks, DMA mask APIs, pinctrl, `mmc_of_parse`, syscon/regmap property `nuvoton,sys`, and compatible `nuvoton,ma35d1-sdhci`.

Risks: register restore coverage must match all registers reset by the tuning workaround; missing a register can cause subtle post-tuning failures. Boundary-splitting assumes two descriptors are enough per crossing and requires the expanded ADMA table count. Pinctrl lookup failures are tolerated, so boards relying on pin state must define names correctly. Probe error paths return without explicit host free, relying on devm/platform cleanup.

Test signals: tune at HS200/SDR104 speeds, transfers crossing 128 MiB DMA boundaries, voltage switch with and without `state_uhs`, command-conflict behavior across 52 MHz, syscon absence/presence, reset controller faults, and remove-time clock disable should be exercised.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-ma35d1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-sparx5.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-sparx5.c

Purpose: this is the Microchip Sparx5 SDHCI OF driver. It configures Sparx5-specific CPU syscon registers, eMMC mode/reset bits, optional card clock delay, DMA cache attributes, and ADMA descriptor splitting for 128 MiB boundaries.

Important APIs, types, and functions: `struct sdhci_sparx5_data` stores the host, CPU control regmap, and `delay_clock`. `sdhci_sparx5_adma_write_desc` mirrors other DWC-derived boundary splitting logic. `sparx5_set_cacheable` programs ACP cache attributes, `sparx5_set_delay` programs `MSHC_DLY_CC`, `sdhci_sparx5_set_emmc` maintains the `IS_EMMC` bit, and `sdhci_sparx5_reset_emmc` toggles eMMC reset with conservative delays.

Control flow: `sdhci_sparx5_probe()` initializes SDHCI platform data and private storage, increases ADMA descriptor capacity, enables the `core` clock, reads optional `microchip,clock-delay`, parses SDHCI/MMC properties, obtains a syscon regmap by compatible string, applies clock delay, performs eMMC reset and capability masking for non-removable media, adds the host, and optionally forces un-cached ACP access for DMA when coherent memory declaration is enabled.

State and persistence: all state is volatile hardware state plus devm-managed private data. Reset callbacks reapply `IS_EMMC` after generic SDHCI reset. The driver does not persist data outside registers.

Dependencies and integration points: uses `sdhci-pltfm`, OF compatible `microchip,dw-sparx5-sdhci`, syscon compatible `microchip,sparx5-cpu-syscon`, `devm_clk_get_enabled("core")`, DMA mask inspection, and MMC removable-card helpers.

Risks: the syscon lookup by global compatible rather than a phandle can be fragile if multiple system controllers exist. Delay-clock values outside 1..15 are silently ignored, and `delay_clock` is not explicitly initialized before the conditional test. Non-removable detection drives eMMC reset and SD/SDIO capability removal, so board descriptions must be accurate. DMA cache forcing is conditional on both DMA flags and `CONFIG_DMA_DECLARE_COHERENT`.

Test signals: verify non-removable eMMC reset and mode bit persistence, removable SD path without eMMC masking, `microchip,clock-delay` programming, DMA crossing 128 MiB boundaries, coherent-DMA cache setting, syscon lookup failure, reset behavior, and debug version/type register logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-sparx5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-omap.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-omap.c

Purpose: this driver supports TI OMAP-family SDHCI/MMCHS controllers, including OMAP2/3/4/5, DRA7, K2G, AM335, and AM437 variants. It adapts offset differences, voltage/PBIAS handling, iodelay pinctrl, temperature-aware tuning, runtime PM context save/restore, wake IRQs, and special reset behavior to the SDHCI core.

Important APIs, types, and functions: `struct sdhci_omap_data` holds register offsets and flags per compatible. `struct sdhci_omap_host` stores base pointers, regulators, current timing/power/bus state, pinctrl states, wake IRQ, tuning flag, and context registers. Key functions include `sdhci_omap_start_signal_voltage_switch`, `sdhci_omap_execute_tuning`, `sdhci_omap_card_busy`, `sdhci_omap_set_ios`, `sdhci_omap_set_clock`, `sdhci_omap_enable_dma`, `sdhci_omap_reset`, `sdhci_omap_irq`, and runtime PM context save/restore.

Control flow: `sdhci_omap_probe()` gets match data, creates an SDHCI platform host, adjusts `host->ioaddr` and `mapbase` to the SDHCI register offset while preserving OMAP base access, parses OF/MMC properties, applies DRA7 ES1.x frequency limits, configures clocks and PBIAS, enables runtime PM before setup so the PM domain can initialize registers, derives voltage capabilities from regulators, installs MMC callbacks, chooses external DMA if needed, configures caps, sets up host, builds iodelay pinctrl state table, adds the host, and registers optional wake IRQ.

State and persistence: driver state tracks bus mode, power mode, timing, PBIAS enabled status, tuning-in-progress, and context register snapshots. Runtime suspend saves OMAP registers, selects idle pinctrl, may request retune, and runtime resume restores registers before resuming SDHCI. No durable state is written.

Dependencies and integration points: integrates with `sdhci-pltfm`, PM runtime/autosuspend, TI PM domains, regulators `pbias` and `vqmmc`, pinctrl named by timing modes, thermal zone `cpu_thermal`, wake IRQ named `wakeup`, GPIO card-detect/write-protect helpers, and OF compatibles under `ti,*-sdhci`.

Risks: tuning depends on CPU thermal readings and a two-stage DLL search; unavailable thermal zone fails tuning. During tuning, data reset is suppressed and IRQ filtering manually handles command errors, so race-prone interrupt behavior is possible. PBIAS/vqmmc voltage capability derivation and 3.0 V/3.3 V quirk handling must match board regulators. Context restore order is explicitly important for HCTL and can break after register changes.

Test signals: cover every compatible offset, voltage switching with PBIAS/vqmmc, DRA7 iodelay state selection, high-speed tuning across temperatures, runtime suspend/resume with retune, wake IRQ behavior, external DMA selection, card busy detection, erase timeout handling, and special reset timeout logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-omap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pci-arasan.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pci-arasan.c

Purpose: this file provides `sdhci_pci_fixes` for Arasan PCI SDHCI controllers with an integrated PHY. It initializes and retunes the PHY across legacy, high-speed, HS200, DDR50, HS400, and enhanced-strobe modes.

Important APIs, types, and functions: `struct arasan_host` stores the last programmed clock. PHY access is via indirect registers `PHY_ADDR_REG` and `PHY_DAT_REG`. `arasan_phy_write`, `arasan_phy_read`, `arasan_phy_addr_poll`, and `arasan_phy_sts_poll` implement short timeout polling. `arasan_phy_init` powers/calibrates IO pads, enables command/data/strobe/clock paths, and sets legacy mode. `arasan_phy_set` programs mode, tap delays, drive type, trim, DLL enable, and waits for DLL ready.

Control flow: PCI core calls `arasan_pci_probe_slot()` from the fixup table. That marks the card non-removable and 8-bit capable, then initializes the PHY. The local `set_clock` callback first delegates to `sdhci_set_clock()` and then calls `arasan_select_phy_clock()`, which skips redundant programming when `ios.clock` has not changed, maps clock to DLL frequency select, and programs PHY mode according to MMC timing or enhanced-strobe callback presence.

State and persistence: the only software state is `chg_clk`, used to avoid repeated PHY programming. Hardware state is in the PHY registers and DLL. No persistent data is written.

Dependencies and integration points: this file is not a standalone module; it exports `const struct sdhci_pci_fixes sdhci_arasan` consumed by `sdhci-pci-core.c`. It depends on `sdhci-pci.h`, SDHCI core callbacks, PCI device ID matching, and MMC timing state.

Risks: PHY polling timeouts are only 100 us, and most callers collapse errors to `-EBUSY` or `-ENODEV`; marginal hardware may fail probe or high-speed switching. `arasan_select_phy_clock()` ignores return values from `arasan_phy_set()`, so runtime PHY programming failures after probe are not propagated. Enhanced-strobe selection is inferred from presence of the MMC callback, not directly from timing alone.

Test signals: probe on Arasan PCI eMMC, PHY calibration completion, each timing mode transition, 50/100/200 MHz clock changes, HS400 and enhanced-strobe operation, DLL-ready timeout behavior, and suspend/resume through PCI core are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pci-arasan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pci-core.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pci-core.c

Purpose: this is the main SDHCI PCI bus driver. It binds PCI SDHCI devices, creates one SDHCI host per slot/BAR, applies vendor fixup tables, manages power/runtime PM, optional CQHCI/UHS2 integration, card-detect GPIO overrides, DMA enablement, and many hardware-specific quirks for Ricoh, ENE, Intel, JMicron, SysKonnect, VIA, Realtek, AMD, Arasan, Synopsys, GLI, O2, and generic SDHCI devices.

Important APIs, types, and functions: the central integration object is `struct sdhci_pci_fixes` from `sdhci-pci.h`; this file defines many instances and the `pci_ids[]` dispatch table. Core lifecycle functions are `sdhci_pci_probe`, `sdhci_pci_probe_slot`, `sdhci_pci_remove`, and `sdhci_pci_remove_slot`. Shared PM helpers are `sdhci_pci_suspend_host`, `sdhci_pci_resume_host`, runtime suspend/resume variants, and CQHCI wrappers. Vendor-heavy areas include Intel DSM/LTR/HS400/CQE support, JMicron PMOS and duplicate-interface rejection, AMD manual tuning and hard reset, and card-detect DMI GPIO lookup.

Control flow: PCI probe reads slot count and first BAR, enables the device, allocates a chip, loads fixups from `driver_data`, runs chip-level probe, then probes each slot. Slot probe validates BAR memory and PCI interface, allocates `sdhci_host` plus slot/vendor private data, maps MMIO, runs `probe_slot`, configures PM caps and optional GPIO CD, adds the host through either fixup `add_host` or `sdhci_add_host`, and may disable runtime PM if a required own-card-detect GPIO is absent. Remove reverses this and calls vendor remove hooks.

State and persistence: `struct sdhci_pci_chip` tracks the PCI device, slots, quirk flags, and PM/retune policy; each `struct sdhci_pci_slot` tracks host, card-detect override, and optional reset hook. Intel private state caches DSM capabilities, drive strength, LTR registers, retune workarounds, and power-off needs. State is volatile and tied to PCI device lifetime; debugfs exposes cached Intel LTR values.

Dependencies and integration points: it integrates with PCI core, SDHCI/MMC core, CQHCI, UHS2 helpers, ACPI DSM, DMI, GPIO lookup tables, PM runtime/QoS, debugfs, IOSF MBI on x86, and many externally defined fixups such as `sdhci_arasan`, `sdhci_snps`, `sdhci_o2`, `sdhci_gl9750`, and related GLI/O2/Synopsys code.

Risks: vendor fixup behavior is dense and device-ID dependent, so changes can regress old hardware. Multi-slot error unwinding must remove already-added slots correctly. Runtime PM retune behavior is hardware-specific and can corrupt high-speed operation if wake/card-detect assumptions are wrong. Intel CQHCI and GLK retune workarounds depend on DMI exceptions. AMD hard reset deliberately cycles PCI power state, which is high impact. JMicron duplicate-interface filtering assumes PCI function ordering.

Test signals: enumerate representative generic and vendor PCI devices, verify multi-slot probe unwinding, DMA enable warnings, card-detect GPIO override fallback/defer, system and runtime suspend/resume, Intel eMMC HS200/HS400/HS400ES and CQE, LTR debugfs and PM QoS writes, JMicron power/interface behavior, AMD HS200 tuning and D3cold reset, and removal with dead-device MMIO returning all ones.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pci-core.c -->
