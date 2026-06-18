# Research: subset-b-005041

This grouped report covers the requested Linux PHY driver slice under `sources/distributed-fs/ceph-client/drivers/phy/`. Each file section is bounded by reconciliation markers so the per-file reports can be split into source-tree-aligned outputs.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-samsung-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-samsung-usb2.c

Purpose: core Samsung S5P/Exynos USB 1.1/2.0 generic PHY provider. It binds DT compatibles to SoC-specific `samsung_usb2_phy_config` tables defined elsewhere, allocates one `struct phy` per configured sub-PHY, and provides shared clock, regulator, syscon, and MMIO plumbing.

Important APIs, types, and functions: `samsung_usb2_phy_power_on()` and `samsung_usb2_phy_power_off()` implement the exported `phy_ops`; `samsung_usb2_phy_xlate()` maps the phandle argument index to `drv->instances[index].phy`; `samsung_usb2_phy_probe()` maps the PHY MMIO resource, PMU syscon, optional system syscon, clocks named `phy` and `ref`, optional `vbus`, and registers the provider. The OF table selects configs for Exynos3250, Exynos4210, Exynos4x12, Exynos5250, Exynos5420, and S5PV210 behind Kconfig guards.

Control flow: probe requires DT, match data, MMIO resource 0, a `samsung,pmureg-phandle`, and clocks. If `cfg->rate_to_clk` exists it converts the reference clock rate into `drv->ref_reg_val`. It then creates each instance with `devm_phy_create()`, sets bus width to 8, attaches instance driver data, and registers the custom xlate. Power-on enables optional VBUS, prepares main and ref clocks, then calls the SoC-specific `power_on()` callback under `drv->lock`; errors unwind regulator and clocks in reverse order. Power-off runs the callback under the same spinlock, disables clocks, and disables VBUS.

State and persistence: runtime state is per-platform-device in `struct samsung_usb2_phy_driver` plus a flexible array of instances. Persistent hardware state is in PMU/sysreg/PHY registers written by the SoC callbacks. `ref_rate` and `ref_reg_val` cache derived clock information. The spinlock serializes register sequences shared by multiple PHY instances.

Dependencies and integration points: generic PHY framework, platform driver core, common clock, optional regulator, regmap/syscon, and SoC-specific config objects declared in the sibling header. DT consumers use an index cell to choose a sub-PHY. `suppress_bind_attrs` prevents runtime bind/unbind from sysfs, reducing risk around shared hardware state.

Risks: `samsung_usb2_phy_xlate()` directly reads `args->args[0]` and assumes a valid cell count from DT binding. Optional VBUS failures other than probe deferral are silently treated as no regulator. Callback failures during power-off leave clocks/regulator enabled because the function returns early. Hardware callback code must be IRQ-safe enough for spinlock context and must not sleep.

Test signals: build coverage for each Kconfig combination; DT binding tests for phandle cell count and compatible match data; boot/probe logs for missing syscons/clocks; USB host/device enumeration across each SoC config; suspend/resume or repeated power cycle tests to catch unbalanced clocks/regulators and shared-register races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-samsung-usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-samsung-usb2.h -->
# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-samsung-usb2.h

Purpose: shared interface and data model for the Samsung USB2 PHY core and its SoC-specific configuration files.

Important APIs, types, and functions: defines `KHZ`/`MHZ`; forward declarations; `struct samsung_usb2_phy_instance`, `struct samsung_usb2_phy_driver`, `struct samsung_usb2_common_phy`, and `struct samsung_usb2_phy_config`; extern declarations for Exynos and S5PV210 config tables. The common PHY object carries per-instance callbacks, ID, and label; the config table carries the PHY array, reference-rate conversion callback, number of PHYs, and feature flags.

Control flow: the header itself has no executable flow, but it defines how the core driver discovers per-instance behavior. `samsung_usb2_phy_probe()` consumes `num_phys`, `phys`, `has_mode_switch`, `has_refclk_sel`, and `rate_to_clk`; power operations consume the instance callbacks.

State and persistence: `struct samsung_usb2_phy_driver` owns all mutable runtime state: clock/regulator handles, MMIO base, PMU/sysreg regmaps, cached reference clock values, lock, and flexible instance array. `struct samsung_usb2_phy_instance` keeps counters (`int_cnt`, `ext_cnt`) that SoC-specific code can use for shared internal/external PHY users.

Dependencies and integration points: includes Linux clock, generic PHY, device, regmap, spinlock, and regulator APIs. The extern config symbols are supplied by companion Samsung PHY implementation files selected by Kconfig.

Risks: ABI is internal but tightly shared across several SoC files; changing field semantics can break callbacks. `label` is mutable `char *` although tables likely hold string literals. The shared counters are not manipulated by the core file, so correctness depends on callback discipline and locking.

Test signals: compile all Samsung USB2 PHY variants together and individually; static analysis for missing config symbols under Kconfig combinations; runtime tests that exercise callbacks relying on `int_cnt`, `ext_cnt`, `has_mode_switch`, and `has_refclk_sel`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-samsung-usb2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/socionext/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/socionext/Kconfig

Purpose: Kconfig menu entries for Socionext UniPhier PHY drivers: USB2, USB3, PCIe, and AHCI.

Important APIs, types, and functions: declares `PHY_UNIPHIER_USB2`, `PHY_UNIPHIER_USB3`, `PHY_UNIPHIER_PCIE`, and `PHY_UNIPHIER_AHCI`. All depend on UniPhier or compile-test, OF, and MMIO support; all select `GENERIC_PHY`; USB2 also selects `MFD_SYSCON`. PCIe defaults to `PCIE_UNIPHIER`; AHCI defaults to `SATA_AHCI_PLATFORM`.

Control flow: not executable, but it determines which object files appear in the build and which framework dependencies are enabled. `PHY_UNIPHIER_USB3` builds both HS and SS PHY drivers through the Makefile.

State and persistence: no runtime state. Configuration state affects built modules and automatic defaults when matching controller drivers are enabled.

Dependencies and integration points: ties these drivers to generic PHY consumers in UniPhier USB, PCIe, and SATA/AHCI controller stacks. Help text documents SoC coverage and the special Pro4 USB2-versus-USB3-HS PHY selection.

Risks: defaulting PCIe/AHCI PHYs from controller symbols can surprise minimal builds. USB3 symbol controls two separate object files, so partial HS/SS build selection is not possible.

Test signals: `allyesconfig`, `allmodconfig`, and compile-test builds; dependency checks that syscon support is present for USB2; controller smoke tests with matching PHY symbols built-in and modular.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/socionext/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/socionext/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/socionext/Makefile

Purpose: maps Socionext UniPhier PHY Kconfig symbols to object files.

Important APIs, types, and functions: `obj-$(CONFIG_PHY_UNIPHIER_USB2)` builds `phy-uniphier-usb2.o`; `CONFIG_PHY_UNIPHIER_USB3` builds both `phy-uniphier-usb3hs.o` and `phy-uniphier-usb3ss.o`; `CONFIG_PHY_UNIPHIER_PCIE` builds `phy-uniphier-pcie.o`; `CONFIG_PHY_UNIPHIER_AHCI` builds `phy-uniphier-ahci.o`.

Control flow: kernel build system only. The single USB3 symbol intentionally produces two cooperating but independent modules/objects for high-speed and super-speed PHY blocks.

State and persistence: no runtime state. Build output state follows Kconfig.

Dependencies and integration points: consumed by `drivers/phy/Makefile` inclusion for Socionext platform PHY support.

Risks: USB3 HS and SS cannot be selected independently, which is correct for typical UniPhier USB3 designs but may overbuild in compile-test contexts.

Test signals: verify object inclusion with `make drivers/phy/socionext/`; module names and DT modaliases should match the platform drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/socionext/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-ahci.c -->
# sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-ahci.c

Purpose: generic PHY provider for UniPhier AHCI/SATA PHY blocks on Pro4, PXs2, and PXs3 SoCs.

Important APIs, types, and functions: `struct uniphier_ahciphy_priv` stores MMIO, clocks, resets, and SoC data. `struct uniphier_ahciphy_soc_data` supplies optional init/power callbacks and flags. Pro4 routines program MPLL/RX/TX parameters and manage PM/TX/RX resets; PXs2/PXs3 routines toggle `CKCTRL_REF_SSP_EN`/`CKCTRL_P0_RESET` and poll PLL ready. Generic `phy_ops` provide `.init`, `.exit`, `.power_on`, `.power_off`.

Control flow: probe maps one MMIO resource, obtains link and optional PHY/GIO clocks and resets depending on SoC flags, creates a single PHY, and registers simple xlate. `.init` enables parent GIO/link clocks, deasserts parent resets, and runs optional SoC parameter programming. `.power_on` enables the PHY clock when present, deasserts PHY reset, and runs SoC power-on. Error paths assert resets and disable clocks in reverse. `.power_off` runs SoC shutdown, asserts PHY reset, and disables PHY clock.

State and persistence: state is private per PHY. Hardware state persists in AHCI PHY registers and reset lines. `is_ready_high` changes PLL-ready polarity for PXs2 versus PXs3; `is_phy_clk` controls whether a dedicated PHY clock is managed.

Dependencies and integration points: generic PHY, clock/reset APIs, MMIO polling, platform DT compatibles `socionext,uniphier-*-ahci-phy`, and AHCI controller consumers.

Risks: PXs3 init appears to prepare TXCTRL1/RXCTRL values but does not visibly write them after modification, which may be intentional omission or a latent bug. Poll timeouts are short for PXs2/PXs3. Legacy Pro4 has multiple shared resets and clocks; any mismatch in DT reset names breaks probe.

Test signals: boot probe for each compatible, SATA link training at Gen speeds, PLL-ready timeout logs, suspend/resume power cycling, and register trace comparing PXs3 parameter writes with hardware programming expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-ahci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-pcie.c -->
# sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-pcie.c

Purpose: UniPhier PCIe PHY provider for legacy Pro5 and newer LD20/PXs3/NX1 PHY blocks.

Important APIs, types, and functions: `uniphier_pciephy_testio_write/read()` implement the indirect TESTI/TESTO register interface; `uniphier_pciephy_set_param()` modifies PHY internal registers; `uniphier_pciephy_assert/deassert()` control manual PHY reset. `struct uniphier_pciephy_soc_data` distinguishes legacy, dual-PHY, and syscon mode callbacks. `uniphier_pciephy_ld20_setmode()` and `_nx1_setmode()` write USB/PCIe mux syscon bits.

Control flow: probe maps MMIO, obtains either named legacy clocks/resets (`gio`, `link`) or unnamed clock/reset, creates one PHY, optionally sets syscon mux mode, and registers simple xlate. `.init` enables clocks, deasserts resets, selects port 1, and for non-legacy PHYs programs RX EQ, VCO, and clamp settings for one or two PHY IDs before deasserting PHY reset. `.exit` asserts PHY reset for non-legacy devices and unwinds resets/clocks.

State and persistence: private state keeps clock/reset handles and SoC feature flags. Hardware state includes mux selection in syscon and internal PHY TESTIO parameters.

Dependencies and integration points: generic PHY, syscon/regmap, clock/reset framework, DT compatibles for Pro5/LD20/PXs3/NX1, and UniPhier PCIe controller users.

Risks: the driver supports only one port through `PORT_SEL_1`; systems expecting other ports require different data or driver changes. Optional syscon lookup failure is ignored, so mux setup can be silently skipped on bad DT. TESTIO access requires dummy reads and tight sequencing; regressions can be hardware-specific.

Test signals: PCIe enumeration per compatible, DT validation for `socionext,syscon`, link stability on dual PHY NX1, register readback of TESTIO parameters, and compile coverage for legacy/non-legacy paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-usb2.c

Purpose: UniPhier USB2 PHY provider for USB2 controller-integrated PHYs, with child-node-per-port PHY creation and syscon register programming.

Important APIs, types, and functions: `struct uniphier_u2phy_soc_data` contains two register/value pairs per port. `uniphier_u2phy_init()` writes port configuration registers. `uniphier_u2phy_power_on/off()` manage optional VBUS. `uniphier_u2phy_xlate()` matches a consumer phandle node to a linked-list PHY instance.

Control flow: probe reads SoC data table, counts sentinel-terminated entries, obtains parent syscon regmap, iterates child nodes, allocates a `priv`, obtains optional `vbus`, creates a PHY bound to the child node, reads the child `reg` as data index, links instances, and registers custom xlate. Init writes `config0` and `config1` when data is present; power only toggles VBUS.

State and persistence: each child PHY has its own `priv`, optional data pointer, optional VBUS, and `next` pointer. Hardware state persists in parent syscon USBPHY control/PLL registers.

Dependencies and integration points: generic PHY, syscon parent node, child DT nodes with `reg`, optional regulator, Pro4 and LD11 compatible data tables.

Risks: `dev_set_drvdata(dev, priv)` stores the last allocated `priv`, but the linked list head is `next`; because `priv` remains the most recent node this works, but a no-child DT leaves null provider state. Optional VBUS is fetched from the parent device rather than child, so per-port supplies are not modeled. Out-of-range `reg` only warns and leaves the PHY unconfigured.

Test signals: DT with multiple child PHYs, phandle resolution by child node, VBUS enable/disable observation, syscon register write validation for Pro4/LD11, and warning coverage for invalid `reg` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-usb3hs.c -->
# sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-usb3hs.c

Purpose: UniPhier USB3 high-speed PHY provider, responsible for USB2/HS-side PHY clocks, resets, tuning, optional nvmem trim, and VBUS.

Important APIs, types, and functions: `struct uniphier_u3hsphy_soc_data` supplies legacy flag, parameter list, default config registers, and trim callback. `uniphier_u3hsphy_get_nvparam(s)` reads `rterm`, `sel_t`, and `hs_i` cells. `uniphier_u3hsphy_update_config()` applies trim or default disconnect threshold. `uniphier_u3hsphy_set_param()` writes indirect CFG1 fields. Generic PHY ops implement init/exit and power on/off.

Control flow: probe maps MMIO, obtains `phy`/optional `phy-ext` clock and `phy` reset for non-legacy devices or GIO parent clock/reset for legacy, always obtains `link` clock/reset, optional VBUS, creates one PHY, and registers simple xlate. Init enables parent clocks/resets, skips programming for legacy or zero configs, otherwise updates config0 from nvmem/defaults, writes config0/config1, and applies parameter table. Power-on enables ext and PHY clocks, deasserts PHY reset, then enables VBUS. Exit and power-off unwind.

State and persistence: per-device private data holds clocks/resets/VBUS and SoC table. Hardware trim state is programmed into HSPHY CFG registers and indirect parameter fields. NVMEM values are read at init time and not cached separately.

Dependencies and integration points: generic PHY, clock/reset/regulator APIs, nvmem consumer API, platform DT compatibles for Pro5/PXs2/LD20/PXs3/NX1, USB3 controller HS side.

Risks: nvmem errors other than probe deferral are treated as debug fallback, so bad trim wiring may silently use defaults. Parameter writes use read-modify-write through a narrow indirect data field, sensitive to field masks. Legacy devices skip most programming, relying on external setup.

Test signals: USB2 HS enumeration through USB3 controller, nvmem trim present/absent cases, PLL/clock/reset sequencing under repeated init/exit, VBUS regulator balance, and register dumps of CFG0/CFG1 for LD20/PXs3.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-usb3hs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-usb3ss.c -->
# sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-usb3ss.c

Purpose: UniPhier USB3 super-speed PHY provider, programming SS PHY indirect trim/tuning registers and managing PHY/link clocks, resets, and optional VBUS.

Important APIs, types, and functions: `struct uniphier_u3ssphy_soc_data` has legacy flag and up to seven indirect parameters. `uniphier_u3ssphy_testio_write()` performs TESTI writes with required TESTO dummy reads. `uniphier_u3ssphy_set_param()` reads, masks, writes, pulses write-enable, and dummy-reads an internal PHY register. PHY ops provide init/exit and power on/off.

Control flow: probe obtains non-legacy `phy` clock, optional `phy-ext`, `phy` reset, or legacy GIO parent resources, plus common link clock/reset and optional VBUS. Init enables parent resources and applies non-legacy parameter table. Power-on enables optional external clock, PHY clock, deasserts reset, and enables VBUS. Shutdown reverses these operations.

State and persistence: SoC data tables encode CDR, TX PLL, bandgap, VCO, and VCOPLL settings. Runtime state is private resource handles. Hardware state persists in SS PHY internal TESTIO registers until reset/power loss.

Dependencies and integration points: generic PHY, clock/reset/regulator, MMIO, UniPhier USB3 controller, compatibles for Pro4/Pro5/PXs2/LD20/PXs3/NX1.

Risks: indirect writes require exact dummy-read sequencing. Legacy devices share the Pro4 data and skip SS parameter programming. Optional VBUS from the PHY device assumes a single supply. No explicit PLL-ready poll is done in this driver; failures surface through controller behavior.

Test signals: SuperSpeed link training on supported SoCs, register trace of parameter writes, VBUS and clock balance through bind/unbind or runtime PM, and compile coverage with `PHY_UNIPHIER_USB3` building both HS and SS objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-usb3ss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/sophgo/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/sophgo/Kconfig

Purpose: Kconfig gate for Sophgo CV18XX/SG200X USB2 PHY support.

Important APIs, types, and functions: `PHY_SOPHGO_CV1800_USB2` is visible when `ARCH_SOPHGO || COMPILE_TEST`, depends on `MFD_SYSCON` and `USB_SUPPORT`, and selects `GENERIC_PHY`.

Control flow: not executable; controls compilation of `phy-cv1800-usb2.o`.

State and persistence: build-time only.

Dependencies and integration points: enables a generic PHY used with the DWC2 USB controller on Sophgo CV18XX/SG200X SoCs.

Risks: no explicit `COMMON_CLK` dependency despite the driver using clocks; transitive platform configs may cover this, but compile-test coverage should verify it.

Test signals: compile-test for module and built-in forms, dependency checks, and DWC2 consumer DT boots on CV1800B/SG200x boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/sophgo/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/sophgo/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/sophgo/Makefile

Purpose: builds the Sophgo CV1800 USB2 PHY object when its Kconfig symbol is enabled.

Important APIs, types, and functions: `obj-$(CONFIG_PHY_SOPHGO_CV1800_USB2) += phy-cv1800-usb2.o`.

Control flow: kernel build inclusion only.

State and persistence: none beyond build output.

Dependencies and integration points: consumed by the parent PHY Makefile and matched to the Sophgo platform driver.

Risks: none beyond Kconfig-object mismatch risk.

Test signals: verify module name and object inclusion in `allmodconfig` and Sophgo defconfig builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/sophgo/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/sophgo/phy-cv1800-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/sophgo/phy-cv1800-usb2.c

Purpose: Sophgo CV1800/SG2000 USB2 PHY provider that controls USB mode ID override and required USB clocks through a parent syscon.

Important APIs, types, and functions: `struct cv1800_usb_phy` stores the generic PHY, parent syscon, three clocks, and OTG capability flag. `cv1800_usb_phy_set_mode()` implements host/device/OTG mode switching by setting ID override and VBUS power bits in `REG_USB_PHY_CTRL`. `cv1800_usb_phy_set_clock()` sets app, LPM, and standby clock rates.

Control flow: probe requires a parent device, obtains parent syscon regmap, enables clocks named `app`, `lpm`, and `stb` with devm helpers, creates the PHY, sets clock rates to 125 MHz, 12 MHz, and roughly 333 kHz, stores driver data, and registers simple xlate. `set_mode` clears VBUS power for device mode, sets it for host mode, and in OTG mode returns without change unless `support_otg` is true.

State and persistence: runtime mode is not cached, but syscon bits persist in hardware. `support_otg` is currently initialized false, so OTG mode is effectively a no-op success.

Dependencies and integration points: generic PHY, common clock, syscon parent MFD, DWC2 USB controller consumers, compatible `sophgo,cv1800b-usb2-phy`.

Risks: `devm_kmalloc()` leaves fields uninitialized unless assigned; most fields are assigned, but future fields may be unsafe. `spinlock_t lock` is initialized but unused. `dev_info()` logs every mode switch and may be noisy. OTG support flag is hardcoded false, so consumers expecting dynamic ID behavior will not get it.

Test signals: host/device mode switching with DWC2, syscon bit readback for ID and VBUS power bits, clock rate verification, compile-test warnings for unused lock/debugfs include, and probe deferral on missing clocks/syscon.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/sophgo/phy-cv1800-usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/spacemit/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/spacemit/Kconfig

Purpose: Kconfig entries for SpacemiT K1 PCIe/USB3 combo PHY and USB2 PHY drivers.

Important APIs, types, and functions: `PHY_SPACEMIT_K1_PCIE` depends on SpacemiT or compile-test, common clock, MMIO, and OF; selects `GENERIC_PHY`; defaults on `ARCH_SPACEMIT`. `PHY_SPACEMIT_K1_USB2` depends on SpacemiT/compile-test with OF, common clock, and USB common support; selects `GENERIC_PHY`.

Control flow: build-time selection for the two K1 PHY objects.

State and persistence: no runtime state.

Dependencies and integration points: the PCIe symbol covers one combo PCIe/USB3 PHY plus two PCIe-only PHYs; USB2 symbol supports K1 USB device/EHCI/OTG/xHCI consumers.

Risks: PCIe driver has cross-device calibration ordering, so build inclusion alone is not enough; DT must instantiate the combo PHY first or handle probe deferral. USB2 depends on USB_COMMON for `.disconnect` semantics.

Test signals: compile-test, module load ordering with port A calibration, and K1 board boot with PCIe-only and USB3 combo use cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/spacemit/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/spacemit/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/spacemit/Makefile

Purpose: builds SpacemiT K1 PHY objects.

Important APIs, types, and functions: `CONFIG_PHY_SPACEMIT_K1_PCIE` maps to `phy-k1-pcie.o`; `CONFIG_PHY_SPACEMIT_K1_USB2` maps to `phy-k1-usb2.o`.

Control flow: kernel build only.

State and persistence: none.

Dependencies and integration points: parent PHY make infrastructure.

Risks: none beyond Kconfig/object drift.

Test signals: object inclusion for K1 defconfig, module names, and modpost symbol checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/spacemit/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/spacemit/phy-k1-pcie.c -->
# sources/distributed-fs/ceph-client/drivers/phy/spacemit/phy-k1-pcie.c

Purpose: SpacemiT K1 PCIe and PCIe/USB3 combo PHY provider. It supports combo port A in PCIe or USB3 mode and PCIe-only ports B/C, including shared receiver/driver termination calibration.

Important APIs, types, and functions: `struct k1_pcie_phy` stores registers, private PLL clock, lane count, type, and PMU regmap for the combo PHY. Global `k1_phy_rterm` caches calibration results. `k1_pcie_phy_pll_prepare()` is a private clock `.prepare` callback that programs USB or PCIe PLL settings and polls `PLL_READY`. `k1_pcie_phy_init_pcie()` applies RX/TX termination and recalibration per lane; `k1_pcie_phy_init_usb()` selects USB3 mode. `k1_pcie_combo_phy_calibrate()` temporarily powers combo PCIe resources to get termination values. `k1_pcie_combo_phy_xlate()` requires one argument, `PHY_TYPE_PCIE` or `PHY_TYPE_USB3`, and enforces single use.

Control flow: non-port-A probes defer until global calibration is valid. Probe maps registers, deasserts the PHY reset permanently, calibrates combo port if applicable, determines lane count from `num-lanes`, creates the PHY, registers a private PLL clock, and registers an OF provider using either combo xlate or simple xlate. Init selects USB or PCIe path, then enables the private PLL clock. Exit disables it. Calibration clears an APMU hold-reset bit, reuses existing calibration when `R_TUNE_DONE` is set, otherwise enables PCIe app clocks/resets, polls `PCIE_RCAL_RESULT`, saves RX/TX rterm bits, and unwinds resources.

State and persistence: global static calibration state is shared by all instances and persists for module lifetime. Per-instance state includes selected combo type, lane count, and private PLL clock. Hardware state includes PMU combo mux, reset deassertion, PLL programming, lane termination, and refclock mode.

Dependencies and integration points: generic PHY, clock provider API, syscon/regmap APMU, reset/clock bulk APIs, DT phy type bindings, PCIe and USB3 controller consumers. Controller drivers must provide associated app clocks/resets for calibration and manage their own operational clocks/resets.

Risks: global `k1_phy_rterm` assumes one K1 SoC calibration domain and no hot-unplug multi-device ambiguity. Port B/C cannot probe before combo calibration, so missing port A DT causes permanent deferral. `k1_combo_phy_sel()` uses a compact boolean expression that is easy to misread. PHY reset is deasserted and left deasserted by design, which must match controller expectations.

Test signals: probe ordering with port A and B/C, PCIe link training on one- and two-lane ports, USB3 operation through combo xlate, repeated probe deferral, private PLL lock timeout behavior, and validation that calibration values are applied to all PCIe lanes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/spacemit/phy-k1-pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/spacemit/phy-k1-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/spacemit/phy-k1-usb2.c

Purpose: SpacemiT K1 USB2 PHY provider that programs PLL divider values, releases internal resets, enables internal clocks, and clears host-disconnect state.

Important APIs, types, and functions: `struct spacemit_usb2phy` stores PHY, prepared clock, and MMIO regmap. `spacemit_usb2phy_init()` enables the clock, waits for controller reset settling, programs `PHY_PLL_DIV_CFG` for 24 MHz, polls `PHY_PLL_RDY`, writes reset/clock/mode bits, enables HSTXP hardware, and sets host disconnect auto-clear. `spacemit_usb2phy_disconnect()` sets a host disconnect clear bit. `spacemit_usb2phy_exit()` disables the clock.

Control flow: probe gets a prepared clock, maps resource 0, wraps it in a 32-bit regmap, creates the PHY, and registers simple xlate. Init uses `clk_enable()` because the clock was already prepared. On PLL timeout it disables the clock and returns error.

State and persistence: no software mode cache. Hardware register state persists until reset/power. Clock enable state is held between init and exit.

Dependencies and integration points: generic PHY, regmap MMIO, common clock, USB core `.disconnect` PHY callback, compatible `spacemit,k1-usb2-phy`.

Risks: on `clk_enable()` failure the code calls `clk_disable()`, which may be harmless but is unusual for a failed enable. Error after `update_disc_vol` equivalent does not unwind reset bits because only PLL timeout can fail before writes. The `.disconnect` callback ignores port argument and assumes one hardware port.

Test signals: USB2 host/device enumeration, PLL-ready timeout injection, disconnect/reconnect behavior, clock enable balance, regmap register dump for PLL divider and reset mode registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/spacemit/phy-k1-usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/st/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/st/Kconfig

Purpose: Kconfig entries for STMicroelectronics PHY drivers in this subtree.

Important APIs, types, and functions: declares `PHY_MIPHY28LP`, `PHY_ST_SPEAR1310_MIPHY`, `PHY_ST_SPEAR1340_MIPHY`, `PHY_STIH407_USB`, `PHY_STM32_COMBOPHY`, and `PHY_STM32_USBPHYC`. Entries select `GENERIC_PHY`; STM32 USBPHYC also depends on `COMMON_CLK`; STiH407 USB depends on reset controller.

Control flow: build-time selection only.

State and persistence: no runtime state.

Dependencies and integration points: covers STiH407 MiPHY/picoPHY, SPEAr PCIe/SATA PHYs, STM32MP25 ComboPHY, and STM32 USBPHYC. Help text documents the controller/protocol relationships.

Risks: `PHY_MIPHY28LP` depends only on `ARCH_STI` and is not compile-test exposed, so broad build coverage is lower. Several drivers use syscon/regmap but do not all express `MFD_SYSCON` dependencies explicitly in this file.

Test signals: ST platform defconfigs, allmodconfig/compile-test where available, and dependency checking for reset, clock, and syscon APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/st/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/st/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/st/Makefile

Purpose: maps ST PHY Kconfig symbols to object files.

Important APIs, types, and functions: builds `phy-miphy28lp.o`, `phy-spear1310-miphy.o`, `phy-spear1340-miphy.o`, `phy-stih407-usb.o`, `phy-stm32-combophy.o`, and `phy-stm32-usbphyc.o` for their respective symbols.

Control flow: kernel build only.

State and persistence: none.

Dependencies and integration points: parent PHY make system.

Risks: minor whitespace inconsistency is cosmetic. Object mapping is direct and low risk.

Test signals: module build and modpost coverage for each ST symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/st/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/st/phy-miphy28lp.c -->
# sources/distributed-fs/ceph-client/drivers/phy/st/phy-miphy28lp.c

Purpose: STiH407 MiPHY28LP multi-protocol PHY provider for SATA, PCIe, and USB3, including glue-logic syscfg selection, reset control, PLL calibration, protocol-specific analog programming, optional SSC, polarity, and impedance tuning.

Important APIs, types, and functions: `struct miphy28lp_phy` stores per-port resources, flags, syscfg offsets, reset, selected `type`, and SATA generation. `struct miphy28lp_dev` stores shared syscfg regmap, mutex, and port array. Key routines include `miphy28lp_set_reset()`, `miphy28lp_pll_calibration()`, protocol config functions for SATA/PCIe/USB3, `miphy28lp_compensation()`, SSC helpers, `miphy_is_ready()`, `miphy28lp_setup()`, and protocol init entry points. `miphy28lp_xlate()` chooses the child PHY by node, records the requested PHY type, maps type-specific resources, and returns the PHY.

Control flow: probe reads the shared `st,syscfg` regmap, allocates one PHY per child, parses child flags/properties/syscfg offsets, gets and deasserts the shared MiPHY reset, and registers custom xlate. Consumer xlate passes one type cell (`PHY_TYPE_SATA`, `PHY_TYPE_PCIE`, or `PHY_TYPE_USB3`), causing address mapping for `sata-up`, `pcie-up`, `usb3-up`, and optional `pipew`. Init is serialized by a mutex, then switches on type: SATA configures SATA/PCI glue, setup, SATA PLL/banks, compensation, optional RX polarity/SSC/impedance, and readiness; PCIe configures glue, setup, PCIe PLL/banks, PIPE wrapper, and readiness; USB3 performs setup with sync enable, USB3 PLL/RX/TX/PIPE writes, reset sequence, and readiness.

State and persistence: selected type is stored per port after xlate. Hardware programming persists across the PHY until reset/power cycle. Shared syscfg and child resets are protected by a mutex during init. DT properties control oscillator source/readiness, polarity inversion, SSC, impedance compensation, and SATA generation.

Dependencies and integration points: generic PHY, syscon/regmap, child-node resource naming, reset controller, dt-bindings PHY type cells, SATA/PCIe/USB3 controller consumers on STiH407.

Risks: extensive magic register recipes are hardware-sensitive and hard to validate without board testing. `miphy_dev->dev` is used in an error path before assignment if syscfg lookup fails. Type is mutable per xlate and not guarded against conflicting consumers. Resource mapping is delayed until xlate, so bad resource names fail at consumer lookup time rather than probe.

Test signals: per-protocol link bring-up, xlate with each type cell, syscfg bit readback, readiness and compensation timeout tests, DT property combinations for SSC/polarity/impedance, and repeated init calls across multiple child PHYs to validate mutex and shared reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/st/phy-miphy28lp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/st/phy-spear1310-miphy.c -->
# sources/distributed-fs/ceph-client/drivers/phy/st/phy-spear1310-miphy.c

Purpose: SPEAr1310 MiPHY provider for PCIe/SATA-capable PHY instances, with implemented initialization for PCIe mode.

Important APIs, types, and functions: `struct spear1310_miphy_priv` stores PHY ID, selected mode, misc syscon, and PHY pointer. `spear1310_miphy_pcie_init()` programs PLL ratio and port-specific PCIe/SATA config bits; `spear1310_miphy_pcie_exit()` clears them. `spear1310_miphy_xlate()` reads one mode cell (`SATA` or `PCIE`).

Control flow: probe obtains `misc` syscon and `phy-id`, creates one PHY, and registers custom xlate. Init checks selected mode and only performs PCIe programming when mode is `PCIE`; SATA mode returns success without register writes. Exit similarly only clears PCIe.

State and persistence: selected mode is stored in `priv->mode` after xlate, and PHY ID selects port-specific bit positions. Hardware state persists in misc syscon registers.

Dependencies and integration points: generic PHY, syscon/regmap, SPEAr1310 PCIe/SATA controller glue, DT `phy-id` and mode phandle cell.

Risks: SATA mode is accepted but not configured by this driver; that may reflect external SATA setup but can confuse consumers. A single `priv->mode` means conflicting consumers can overwrite mode. Macro-generated bit masks depend on valid ID 0..2.

Test signals: PCIe init/exit register readback for each ID, invalid ID handling, DT xlate mode validation, and SATA consumer behavior to confirm whether no-op is intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/st/phy-spear1310-miphy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/st/phy-spear1340-miphy.c -->
# sources/distributed-fs/ceph-client/drivers/phy/st/phy-spear1340-miphy.c

Purpose: SPEAr1340 MiPHY provider for SATA and PCIe modes, programming misc syscon registers and SATA power/reset sequencing.

Important APIs, types, and functions: `struct spear1340_miphy_priv` stores mode, misc regmap, and PHY pointer. `spear1340_miphy_sata_init/exit()` select SATA mode, set PLL config, power SATA domain, and deassert/assert SATA reset. `spear1340_miphy_pcie_init/exit()` select PCIe mode and clear it on exit. PM sleep ops reinitialize SATA on resume and shut it down on suspend.

Control flow: probe gets `misc` syscon, creates one PHY, and registers custom xlate. Xlate records a one-cell mode. Init/exit switch on the stored mode. SATA path includes fixed `msleep(20)` delays around power/reset transitions; PCIe path is immediate syscon programming.

State and persistence: mode is mutable per PHY object. Syscon bits and SATA power domain state persist until exit/suspend. PM callbacks use the last selected mode.

Dependencies and integration points: generic PHY, syscon/regmap, platform PM, SPEAr1340 SATA/PCIe consumers.

Risks: conflicting consumers can race mode changes. Fixed sleep delays are coarse and may hide timing issues. PM callbacks only handle SATA, so PCIe suspend behavior relies on other layers or retention.

Test signals: SATA link after init/resume, PCIe enumeration, syscon register readback, suspend/resume SATA power-cycle tests, and invalid mode phandle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/st/phy-spear1340-miphy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/st/phy-stih407-usb.c -->
# sources/distributed-fs/ceph-client/drivers/phy/st/phy-stih407-usb.c

Purpose: STiH407 USB2 picoPHY provider for per-port USB2 PHY initialization through syscfg and reset controls.

Important APIs, types, and functions: `struct stih407_usb2_picophy` stores PHY, syscfg regmap, global and port resets, and syscfg register offsets. `stih407_usb2_pico_ctrl()` deasserts global reset and writes port control bits. `stih407_usb2_init_port()` writes default PHY parameters and deasserts the port reset. `stih407_usb2_exit_port()` asserts only the port reset.

Control flow: probe gets shared `global` reset and exclusive `port` reset, asserts the port reset by default, parses `st,syscfg` phandle args into parameter/control register offsets, creates one PHY, and registers simple xlate. Init performs global control and port parameter programming before deasserting port reset; exit reasserts port reset.

State and persistence: syscfg offset state is stored in the device object. Hardware state persists in syscfg and reset lines. Global reset is deliberately not asserted on exit because other ports can share it.

Dependencies and integration points: generic PHY, syscon/regmap phandle args, reset controller, STiH407 USB2/USB3 controller consumers.

Risks: `stih407_usb2_pico_ctrl()` return value is ignored in init, so control write errors may be masked until parameter write or reset. Shared global reset policy assumes consumers coordinate via per-port resets and power management.

Test signals: multi-port USB operation, syscfg args validation, reset line observation, init/exit cycles with another port active, and register readback of default parameter value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/st/phy-stih407-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/st/phy-stm32-combophy.c -->
# sources/distributed-fs/ceph-client/drivers/phy/st/phy-stm32-combophy.c

Purpose: STM32MP25 ComboPHY provider for USB3 or PCIe, configuring syscfg mode, PLL/refclock source, optional PCIe impedance/vswing, RX equalizer, runtime PM, and wake IRQ support.

Important APIs, types, and functions: `struct stm32_combophy` stores PHY, syscfg regmap, MMIO base, reset, bulk clocks (`apb`, `ker`, optional `pad`), type, init state, and wake IRQ. `stm32_combophy_xlate()` accepts one type cell (`PHY_TYPE_USB3` or `PHY_TYPE_PCIE`) and rejects pad clock use with USB3. `stm32_combophy_pll_init()` computes register fields for supported reference rates, deisolates the PHY, asserts/deasserts reset, polls PLL status, and applies PCIe-specific programming. `stm32_impedance_tune()` maps DT micro-ohm and microvolt values to discrete syscfg fields.

Control flow: probe maps MMIO, obtains clocks, reset, global syscfg regmap by compatible, creates the PHY, optionally requests wake IRQ, enables runtime PM, and registers custom xlate. Init increments runtime PM, enables clocks, sets mode, initializes PLL, marks active, and refreshes PM state. Exit clears mode-specific enable bits, isolates the PHY, disables clocks, and drops runtime PM. Noirq suspend/resume disables/re-enables clocks when initialized and toggles wake IRQ.

State and persistence: selected type and `is_init` persist in the driver object. Hardware state persists in syscfg CR registers and local analog loop control. Optional DT properties (`st,ssc-on`, output impedance, vswing, RX equalizer) shape configuration.

Dependencies and integration points: generic PHY, PM runtime, syscon/regmap, clock/reset frameworks, wake IRQ, USB3/PCIe consumers using dt-bindings PHY type cells.

Risks: only specific input clock rates are accepted; unsupported board clocks fail init. RX equalizer validation compares raw value to a bit mask rather than maximum field value, allowing values up to mask numeric value. `type` is mutable and single-consumer oriented. Wake IRQ handler only acknowledges, relying on system wake plumbing.

Test signals: USB3 and PCIe xlate modes, pad-clock rejection for USB3, PLL lock for each supported refclock, impedance/vswing DT bounds, suspend/resume wake behavior, and syscfg readback after init/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/st/phy-stm32-combophy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/st/phy-stm32-usbphyc.c -->
# sources/distributed-fs/ceph-client/drivers/phy/st/phy-stm32-usbphyc.c

Purpose: STM32 USB High-Speed PHY Controller provider managing the shared USBPHYC PLL, two UTMI+ PHY ports, per-port tuning, optional VBUS, UTMI switch selection, and an exported 48 MHz clock.

Important APIs, types, and functions: `struct stm32_usbphyc` stores shared MMIO, input clock, reset, regulators, PHY array, atomic PLL consumer count, clk48 hardware, and switch state. `struct stm32_usbphyc_phy` stores per-port PHY, index, VBUS, active flag, and tuning word. `stm32_usbphyc_pll_enable/disable()` manage regulators and PLL with `n_pll_cons`. `stm32_usbphyc_phy_tuning()` builds the per-port TUNE value from DT properties while preserving OTP compensation. `stm32_usbphyc_of_xlate()` validates port cell counts and configures the UTMI switch for port 1. `stm32_usbphyc_clk48_register()` exposes `ck_usbo_48m` backed by the same PLL.

Control flow: probe maps MMIO, enables input clock, resets or clears PLL, ensures PLL disabled, allocates child PHY state, obtains analog regulators, creates child PHYs, reads child `reg`, optional VBUS, applies tuning, registers OF provider, registers clk48, and logs version. PHY init enables the shared PLL and verifies port lock monitor; exit marks inactive and drops a PLL consumer. Power on/off toggles per-port VBUS. Remove exits active PHYs, unregisters clk48, and disables input clock. Resume reapplies switch and tuning registers.

State and persistence: `n_pll_cons` persists shared PLL ownership across PHY ports and clk48 consumers. Per-port active/tune state is kept in memory and replayed on resume. UTMI switch setup is stored and prevents conflicting second requests.

Dependencies and integration points: generic PHY, common clock provider, regulators `vdda1v1`/`vdda1v8`, optional VBUS per child, reset controller, USB host/OTG consumers, DT child nodes with port indices.

Risks: regulator disable returns can block PLL disable and leave partial state. `nphys` is child-count based but port `reg` can be sparse; `usbphyc->phys[port]` stores by iteration order while index selects registers, so assumptions in resume use iteration port for TUNE offset rather than stored index. Tuning validation warns and ignores invalid values rather than failing probe.

Test signals: both ports active simultaneously plus clk48 consumer, PLL reference counting under errors, UTMI switch conflict handling, tuning register readback, regulator failure injection, suspend/resume replay, and USB HS enumeration on host and OTG paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/st/phy-stm32-usbphyc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/starfive/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/starfive/Kconfig

Purpose: Kconfig entries for StarFive JH7110 D-PHY RX, D-PHY TX, PCIe/USB3 PHY, and USB2 PHY drivers.

Important APIs, types, and functions: under `ARCH_STARFIVE || COMPILE_TEST`, declares `PHY_STARFIVE_JH7110_DPHY_RX`, `PHY_STARFIVE_JH7110_DPHY_TX`, `PHY_STARFIVE_JH7110_PCIE`, and `PHY_STARFIVE_JH7110_USB`. D-PHY entries depend on MMIO and select `GENERIC_PHY` plus `GENERIC_PHY_MIPI_DPHY`; PCIe and USB select `GENERIC_PHY`, and USB depends on `USB_SUPPORT`.

Control flow: build-time selection only.

State and persistence: none.

Dependencies and integration points: MIPI CSI/DSI, PCIe/USB3, and Cadence USB controller PHY consumers on JH7110.

Risks: PCIe/USB drivers use clocks/syscon but Kconfig only expresses MMIO/USB support; compile-test should catch missing implicit dependencies.

Test signals: StarFive defconfig, allmodconfig, MIPI D-PHY framework availability, and consumer controller probe tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/starfive/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/starfive/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/starfive/Makefile

Purpose: object mapping for StarFive JH7110 PHY drivers.

Important APIs, types, and functions: maps DPHY RX/TX, PCIe, and USB Kconfig symbols to `phy-jh7110-dphy-rx.o`, `phy-jh7110-dphy-tx.o`, `phy-jh7110-pcie.o`, and `phy-jh7110-usb.o`.

Control flow: kernel build only.

State and persistence: none.

Dependencies and integration points: parent PHY build system.

Risks: low; direct mapping.

Test signals: module/object inclusion and DT modalias generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/starfive/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/starfive/phy-jh7110-dphy-rx.c -->
# sources/distributed-fs/ceph-client/drivers/phy/starfive/phy-jh7110-dphy-rx.c

Purpose: StarFive JH7110 MIPI D-PHY RX provider that configures lane enable/swap and clock pre-counters for receive-side MIPI operation.

Important APIs, types, and functions: `struct stf_dphy_info` holds six lane mapping entries. `struct stf_dphy` stores MMIO registers, cfg/ref/tx clocks, reset array, 0.9 V regulator, PHY, and match data. `stf_dphy_configure()` writes lane enables, lane swap, PLL clock select, and pre-counter fields. Power ops manage runtime PM, regulator, clock rates, and resets.

Control flow: probe maps resource 0, gets clocks `cfg`, `ref`, `tx`, reset array, regulator `mipi_0p9`, creates PHY, enables runtime PM, and registers simple xlate. Power-on resumes runtime PM, enables regulator, sets fixed clock rates (99 MHz, 49.5 MHz, 19.8 MHz), and deasserts reset. Power-off asserts reset, disables regulator, and drops runtime PM. Configure writes static timing and lane mapping values from match data.

State and persistence: lane mapping is constant per compatible. Hardware state persists in syscfg registers while powered. No configuration cache is kept.

Dependencies and integration points: generic PHY MIPI D-PHY consumers, PM runtime, regulator, clock/reset frameworks, compatible `starfive,jh7110-dphy-rx`.

Risks: clock rate set return values are ignored, so unsupported rates may go unnoticed. Runtime PM is enabled without a remove disable path. Configure does not validate `opts` mode or lane count.

Test signals: CSI receiver bring-up, lane mapping validation, regulator and runtime PM balance, clock rate readback, and MIPI D-PHY consumer configure sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/starfive/phy-jh7110-dphy-rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/starfive/phy-jh7110-dphy-tx.c -->
# sources/distributed-fs/ceph-client/drivers/phy/starfive/phy-jh7110-dphy-tx.c

Purpose: StarFive JH7110 MIPI D-PHY TX provider for DSI transmit, with a large bitrate-to-register timing table and PLL programming.

Important APIs, types, and functions: `reg_configs[]` maps aligned bitrates to PLL feedback and HS timing fields. `stf_dphy_get_config_index()` finds an exact bitrate entry, defaulting to index 0. `stf_dphy_configure()` rounds requested `hs_clk_rate` to 10 MHz, selects a table row, programs ref clock, termination, lane swap, PLL, and HS timing registers. `stf_dphy_hw_reset()` toggles reset and polls PLL lock. Ops include power, init/exit, configure, and validate.

Control flow: probe maps top syscfg, enables runtime PM, obtains `txesc` clock and `sys` reset, creates PHY, and registers simple xlate. Power-on/off only manage runtime PM. Init asserts hardware reset, writes ready/pre-zero defaults, enables txesc clock, and deasserts sys reset. Exit asserts sys reset, disables txesc, and clears hardware reset. Configure can be called with MIPI D-PHY options to program PLL/timing before or around init depending on consumer sequence.

State and persistence: current `phy_configure_opts_mipi_dphy config` field exists but is not used as a cache. Hardware timing state persists in top syscfg registers. Lane map is match-data constant.

Dependencies and integration points: generic MIPI D-PHY framework, DSI bridge/display consumers, PM runtime, clock/reset.

Risks: if bitrate is not exactly in the table after 10 MHz alignment, index 0 is used silently, likely misconfiguring many rates. `stf_dphy_hw_reset()` logs "PLL Locked" on timeout textually ambiguous. If reset deassert fails after txesc enable, the clock is not disabled in that error path.

Test signals: DSI panel modes across bitrate table, validation of unsupported bitrates, PLL lock timeout behavior, init error-path clock balance, and lane swap readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/starfive/phy-jh7110-dphy-tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/starfive/phy-jh7110-pcie.c -->
# sources/distributed-fs/ceph-client/drivers/phy/starfive/phy-jh7110-pcie.c

Purpose: StarFive JH7110 PCIe 2.0 PHY provider that can switch the shared PHY block between PCIe and USB3 modes using syscon bits and local PLL/KVCO registers.

Important APIs, types, and functions: `struct jh7110_pcie_phy` stores local registers, optional STG/sys syscon regmaps and offsets, current `enum phy_mode`, and PHY pointer. `phy_usb3_mode_set()` programs STG mode/bus width/enable, sys split, and spread-spectrum PLL enable. `phy_pcie_mode_set()` restores PCIe defaults. `phy_kvco_gain_set()` writes KVCO fine tune values. `jh7110_pcie_phy_set_mode()` dispatches mode changes.

Control flow: probe maps MMIO, creates PHY, optionally obtains syscon phandle args for system and STG registers, applies KVCO tuning, attaches driver data, and registers simple xlate. Set-mode accepts USB host/device/OTG as USB3 mode or `PHY_MODE_PCIE` as PCIe; repeated same mode is a no-op.

State and persistence: current mode is cached in `phy->mode`, initially zero. Hardware syscon and local register mode bits persist until changed.

Dependencies and integration points: generic PHY, syscon/regmap phandle args, StarFive PCIe/USB3 controller consumers.

Risks: USB3 mode requires both syscons; PCIe mode silently works without syscons because default is PCIe. `sys_phy_connect` and STG offsets depend on phandle arg order. The duplicate `PCIE_USB3_PHY_ENABLE` define is harmless but noisy.

Test signals: PCIe enumeration, USB3 mode switch from xHCI/dwc3 consumer, syscon readback, missing syscon DT behavior, and repeated set-mode transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/starfive/phy-jh7110-pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/starfive/phy-jh7110-usb.c -->
# sources/distributed-fs/ceph-client/drivers/phy/starfive/phy-jh7110-usb.c

Purpose: StarFive JH7110 USB2 PHY provider for the Cadence USB controller, handling 125 MHz clocks, low-speed keepalive, RX normal power, and syscon USB split selection.

Important APIs, types, and functions: `struct jh7110_usb2_phy` stores PHY, MMIO, sys syscon, `125m` and `app_125m` clocks, and current mode. `usb2_set_ls_keepalive()` toggles host keepalive. `usb2_phy_set_mode()` validates USB modes, updates keepalive, and sets `USB_PDRSTN_SPLIT` in syscon. `jh7110_usb2_phy_init/exit()` set clock rate, enable app clock, and toggle RX normal power.

Control flow: probe obtains clocks, maps MMIO, creates PHY, registers provider, and looks up sys syscon by compatible. Init sets the 125 MHz clock rate, enables app clock, and enables RX normal power. Set-mode handles host/device/OTG differences for keepalive. Exit disables app clock.

State and persistence: current mode is cached. Hardware state persists in local USB registers and syscon split bit. `usb_125m_clk` is rate-set but not explicitly enabled by this driver.

Dependencies and integration points: generic PHY, common clock, syscon/regmap, USB OF modes, Cadence USB controller on JH7110.

Risks: provider registration occurs before syscon lookup failure is returned, but devm cleanup handles probe failure. Syscon lookup by global compatible assumes one relevant syscon. Device mode clears keepalive but still sets split bit.

Test signals: host/device/OTG mode switching, LS device keepalive behavior, app clock balance, syscon split bit readback, and USB2 enumeration through Cadence controller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/starfive/phy-jh7110-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/sunplus/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/sunplus/Kconfig

Purpose: Kconfig entry for Sunplus SP7021 USB2 PHY support.

Important APIs, types, and functions: `PHY_SUNPLUS_USB` depends on OF and `SOC_SP7021 || COMPILE_TEST`, selects `GENERIC_PHY`, and describes USB2 features including battery charger, synchronous signals, power modes, and speed support.

Control flow: build-time only.

State and persistence: none.

Dependencies and integration points: enables `phy-sunplus-usb2.o` for SP7021 USB controller consumers.

Risks: driver uses clocks, resets, and nvmem but Kconfig only selects generic PHY; compile-test should ensure implicit dependencies are adequate.

Test signals: SP7021 defconfig and compile-test builds, plus USB2 controller probe with the PHY symbol enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/sunplus/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/sunplus/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/sunplus/Makefile

Purpose: object mapping for Sunplus USB2 PHY support.

Important APIs, types, and functions: `obj-$(CONFIG_PHY_SUNPLUS_USB) += phy-sunplus-usb2.o`.

Control flow: kernel build only.

State and persistence: none.

Dependencies and integration points: parent PHY make system.

Risks: low; direct mapping.

Test signals: module/object inclusion and modpost checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/sunplus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/sunplus/phy-sunplus-usb2.c -->
# sources/distributed-fs/ceph-client/drivers/phy/sunplus/phy-sunplus-usb2.c

Purpose: Sunplus SP7021 USB2 PHY provider that initializes UPHY and MOON4 register blocks, applies OTP-derived disconnect voltage, battery-charger settings, chirp mode, and PLL power cycling.

Important APIs, types, and functions: `struct sp_usbphy` stores device, two MMIO resource regions (`phy`, `moon4`), reset, clock, and OTP bit offset. `update_disc_vol()` reads nvmem cell `disc_vol`, extracts `J_DISC` bits, and programs disconnect level with a default fallback. `sp_uphy_init()` enables clock/reset and writes many certification and charger settings. `sp_uphy_power_on/off()` toggle PLL power bits with 1 ms delays. `sp_uphy_exit()` asserts reset and disables clock.

Control flow: probe maps named `phy` and `moon4` resources, obtains clock/reset, reads `sunplus,disc-vol-addr-off`, creates one PHY, and registers simple xlate. Init enables resources, writes MOON4 defaults, updates disconnect voltage, disables ECO/power-saving bits, programs charger and chirp settings. Power-on cycles PLL off/on twice then clears override; power-off powers down PLL and clears override.

State and persistence: hardware state persists in UPHY/MOON4 registers. OTP-derived disconnect level is not cached. Clock/reset state is held from init to exit.

Dependencies and integration points: generic PHY, clock/reset frameworks, nvmem consumer, named MMIO resources, SP7021 USB controller.

Risks: `update_disc_vol()` can call `nvmem_cell_read()` even when `nvmem_cell_get()` returned an error other than defer, which is risky. If `update_disc_vol()` returns an error after clock/reset enable, init returns without unwinding. Non-posted write note suggests ordering matters, but the driver uses ordinary writes without readbacks except delays.

Test signals: OTP present/missing/defer cases, disconnect threshold register readback, USB certification tests, PLL power-cycle timing, init error unwind testing, and USB enumeration at LS/FS/HS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/sunplus/phy-sunplus-usb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/tegra/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/phy/tegra/Kconfig

Purpose: Kconfig entries for NVIDIA Tegra XUSB pad controller and Tegra194/Tegra234 P2U PHY driver.

Important APIs, types, and functions: `PHY_TEGRA_XUSB` depends on `ARCH_TEGRA && USB_SUPPORT`, selects USB common/connector/PHY helpers, and builds the XUSB pad controller. `PHY_TEGRA194_P2U` depends on Tegra or compile-test and selects `GENERIC_PHY`.

Control flow: build-time selection only.

State and persistence: none.

Dependencies and integration points: XUSB pad controller supports multiple Tegra SoC files; P2U supports PIPE-to-UPHY blocks for PCIe on Tegra194 and Tegra234.

Risks: XUSB is not compile-test enabled outside Tegra, while P2U is. Consumers require correct SoC object selection in the Makefile.

Test signals: Tegra defconfig builds, compile-test for P2U, and module alias checks for Tegra194/Tegra234 compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/tegra/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/tegra/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/tegra/Makefile

Purpose: builds Tegra XUSB composite objects and the standalone Tegra194 P2U object.

Important APIs, types, and functions: `phy-tegra-xusb.o` includes common `xusb.o` plus SoC-specific `xusb-tegra124.o`, `xusb-tegra210.o`, or `xusb-tegra186.o` based on ARCH symbols; `CONFIG_PHY_TEGRA194_P2U` builds `phy-tegra194-p2u.o`.

Control flow: kernel build composition only.

State and persistence: none.

Dependencies and integration points: ties multiple SoC implementations into one XUSB module and builds P2U separately.

Risks: Tegra186 implementation is reused for Tegra194 and Tegra234, so SoC-specific differences must be handled in that source. Multiple ARCH symbols can add multiple object files to the composite.

Test signals: build matrices for Tegra124/132/210/186/194/234 and standalone P2U module builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/tegra/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/tegra/phy-tegra194-p2u.c -->
# sources/distributed-fs/ceph-client/drivers/phy/tegra/phy-tegra194-p2u.c

Purpose: NVIDIA Tegra194/Tegra234 P2U (PIPE to UPHY) generic PHY driver that applies PCIe PIPE-side tuning at power-on and L2 exit rate-change calibration.

Important APIs, types, and functions: `struct tegra_p2u` stores MMIO base, optional skip-size-protection flag, and match data. `struct tegra_p2u_of_data` carries `one_dir_search` for Tegra234. `tegra_p2u_power_on()` programs skip size protection, Gen3/Gen4 preset EQ training, RX debounce timer, and optionally disables Gen4 fine-grain search-twice. `tegra_p2u_calibrate()` enables L2 exit rate change. Probe maps named `ctl` resource, reads `nvidia,skip-sz-protect-en`, creates one PHY, and registers simple xlate.

Control flow: platform probe selects match data, maps registers, records DT boolean, creates PHY. Consumers call power-on before using the link; they may call calibrate to enable L2 exit behavior. There is no power-off path.

State and persistence: only the DT boolean and match data are cached. Hardware tuning bits persist until reset. Tegra194 and Tegra234 differ by `one_dir_search`.

Dependencies and integration points: generic PHY framework, platform MMIO resource named `ctl`, Tegra PCIe controller consumers, compatibles `nvidia,tegra194-p2u` and `nvidia,tegra234-p2u`.

Risks: no explicit reset/clock management, assuming parent/controller handles those resources. No power-off means settings are not reverted. Optional skip-size-protection is board-specific and needed for two-retimer topologies; incorrect DT can affect link training.

Test signals: PCIe Gen3/Gen4 link training, retimer topology tests with skip-size protection, L2 exit behavior after calibrate, Tegra234 directional search register readback, and resource-name DT validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/tegra/phy-tegra194-p2u.c -->
