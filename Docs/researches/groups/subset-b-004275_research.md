# Research: subset-b-004275

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-milbeaut.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-milbeaut.c

Purpose: this is the Socionext/Fujitsu Milbeaut SDHCI host driver for the f_sdh30-derived controller. It wraps the generic SDHCI platform core with Milbeaut bridge setup, vendor register programming, two input clocks, and f_sdh30-specific voltage, reset, and delay handling.

Important APIs, types, and functions: `struct f_sdhost_priv` stores the interface clock, core clock, device, and `enable_cmd_dat_delay` device-property state. `sdhci_milbeaut_ops` supplies `.voltage_switch`, `.get_min_clock`, `.reset`, `.set_clock`, `.set_bus_width`, `.set_uhs_signaling`, and `.set_power`. Bridge helpers program `MLB_SOFT_RESET`, `MLB_CR_SET`, `MLB_CDR_SET`, and `MLB_WP_CD_LED_SET`. `sdhci_milbeaut_vendor_init()` configures f_sdh30 IO voltage select, AHB burst behavior, endian/bus-lock bits, and optional command/data delay.

Control flow: probe allocates an `sdhci_host`, parses MMC DT properties, records SDHCI quirks, maps the MMIO resource, enables `iface` and `core` clocks, calls `sdhci_milbeaut_init()`, and registers the host with `sdhci_add_host()`. Initialization deasserts bridge reset, disables card/internal clocks, asserts reset while writing bridge timing fields from the core clock rate, deasserts reset, and applies vendor register defaults. Reset preserves the internal clock enable, runs `sdhci_reset()`, reenables the card clock, waits up to 10 ms for `SDHCI_CLOCK_INT_STABLE`, and reapplies command/data delay.

State and persistence: state is almost entirely hardware register state plus the enabled clock handles. The only persistent software flag is the DT-derived delay selection. Suspend/resume is not custom here; remove unregisters the host and disables both clocks.

Dependencies and integration points: the file depends on `sdhci-pltfm.h`, `sdhci_f_sdh30.h`, common clock APIs, OF/device properties, and the standard MMC/SDHCI host registration path. DT matching is limited to `socionext,milbeaut-m10v-sdhci-3.0`; the optional `fujitsu,cmd-dat-delay-select` property changes ESD control programming.

Risks: bridge clock calculations clamp values but assume a sane, enabled core clock. Probe error paths rely on clock pointer validity after optional OF setup; this driver is effectively DT-oriented. Reset failure only logs and dumps registers, leaving recovery to upper layers. Voltage switch sequencing is fixed delays and direct register writes, so board-specific electrical timing problems may surface as tuning or IO errors.

Test signals: useful signals are successful probe and `sdhci_add_host()`, absence of "Internal clock never stabilised" logs, correct 1.8 V switching in UHS modes, card detect/write-protect polarity, and reliable tuning with and without `fujitsu,cmd-dat-delay-select`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-milbeaut.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-msm.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-msm.c

Purpose: this is the Qualcomm SDHCI platform driver. It supports older MCI-backed and newer v5 register layouts, Qualcomm clock/OPP control, DLL tuning and HS400 calibration, PMIC-backed bus and IO voltage handshakes, runtime PM, CQHCI, and optional Qualcomm Inline Crypto Engine integration.

Important APIs, types, and functions: `struct sdhci_msm_host` is the central state object, carrying MMIO variant data, clocks, power IRQ state, DLL/tuning flags, saved tuning phase, regulator state, CQE/ICE state, and capability bits. `struct sdhci_msm_offset`, `struct sdhci_msm_variant_ops`, and `struct sdhci_msm_variant_info` abstract register offsets and accessors for `qcom,sdhci-msm-v4`, `qcom,sdhci-msm-v5`, and SDM845-derived variants. Major paths include `msm_set_clock_rate_for_bus_mode()`, `msm_init_cm_dll()`, `sdhci_msm_execute_tuning()`, `sdhci_msm_hs400_dll_calibration()`, `sdhci_msm_handle_pwr_irq()`, `sdhci_msm_cqe_add_host()`, and the ICE keyslot/profile helpers under `CONFIG_MMC_CRYPTO`.

Control flow: probe initializes the generic SDHCI platform host, parses MMC DT properties and Qualcomm-specific DLL/DDR settings, performs an optional reset-control pulse, enables bus/core/iface/cal/sleep clocks, wires OPP/interconnect scaling, maps legacy `core_mem` when needed, resets vendor registers, detects SDCC revision features, registers regulators, drains pending power IRQ state, requests the threaded power IRQ, sets runtime PM, installs voltage-switch and tuning hooks, and then chooses either CQE registration or plain `sdhci_add_host()`. SDHCI register writes to power, reset, host-control2, transfer-mode, and command are intercepted through `.write_w`/`.write_b` so the driver can wait for PMIC power IRQ completion or toggle CDR around read commands.

State and persistence: runtime state includes `clk_rate`, `actual_clock`, `curr_pwr_state`, `curr_io_level`, `vqmmc_enabled`, saved DLL tuning phase, `tuning_done`, `calibration_done`, and CQE descriptor sizing. Runtime suspend marks the host suspended, drops the OPP rate, disables bulk clocks, and suspends ICE. Runtime resume reenables clocks, optionally restores SDR DLL configuration before restoring the requested OPP rate, resumes ICE, and clears the suspended flag. Remove unregisters the host and disables clocks.

Dependencies and integration points: the driver integrates with SDHCI, CQHCI, block crypto, `soc/qcom/ice`, regulators, pinctrl PM states, OPP/interconnect frameworks, reset controls, runtime PM, and Device Tree compatibles/properties such as `supports-cqe`, `qcom,ddr-config`, and `qcom,dll-config`.

Risks: power sequencing depends on threaded power IRQ completion and has a 5 s timeout, so missed IRQs can stall register writes. The write hooks may sleep, so assumptions in generic paths must remain valid. CQE temporarily changes ADMA descriptor sizing between pre-CQE legacy traffic and halted CQE. DLL tuning/calibration has many revision-dependent branches and short polling windows. Runtime resume restores DLL state while clocks/OPP are being brought back, making ordering important. ICE support depends on CQHCI crypto capability reporting and qcom ICE services.

Test signals: validate probe on v4 and v5 layouts, regulator voltage switches, pwr_irq timeout-free operation, SDR104/HS200 tuning phase selection, HS400 enhanced strobe and non-strobe calibration, CQE enable/disable and recovery, crypto keyslot program/evict paths when configured, runtime autosuspend/resume, and vendor register dumps on error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-msm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-npcm.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-npcm.c

Purpose: this is a compact Nuvoton NPCM SDHCI platform driver for NPCM7xx and NPCM8xx controllers. It mostly selects SoC-specific SDHCI quirks, enables the optional clock, exposes 8-bit capability when hardware advertises it, parses MMC DT properties, and registers the generic SDHCI host.

Important APIs, types, and functions: the two `struct sdhci_pltfm_data` instances are the primary configuration: NPCM7xx uses `SDHCI_QUIRK_DELAY_AFTER_POWER` plus `SDHCI_QUIRK2_STOP_WITH_TC` and `SDHCI_QUIRK2_NO_1_8_V`; NPCM8xx drops the no-1.8-V restriction. `npcm_sdhci_probe()` is the only custom control path. The platform driver uses `sdhci_pltfm_remove` and `sdhci_pltfm_pmops`.

Control flow: probe obtains match data, initializes an SDHCI platform host with the matched quirks, enables an optional unnamed clock through `devm_clk_get_optional_enabled()`, reads `SDHCI_CAPABILITIES`, sets `MMC_CAP_8_BIT_DATA` if `SDHCI_CAN_DO_8BIT` is present, parses MMC DT properties, and calls `sdhci_add_host()`. There is no custom reset, clock, tuning, voltage, or power code.

State and persistence: there is no private driver state beyond the generic `sdhci_pltfm_host` and its optional clock. Persistent behavior comes from static match data and hardware capabilities read at probe time.

Dependencies and integration points: the file depends on `sdhci-pltfm.h`, clock APIs, MMC host capability bits, and OF match data for `nuvoton,npcm750-sdhci` and `nuvoton,npcm845-sdhci`.

Risks: because probe returns directly on failures after `sdhci_pltfm_init()`, cleanup depends on devm/platform lifetime and generic remove behavior. The 8-bit capability is trusted from the hardware register rather than DT, so incorrect capability wiring could expose a bus width the board cannot use. NPCM7xx intentionally disables 1.8 V; regressions here would show as failed UHS negotiation.

Test signals: successful module probe, clock enable, `mmc_of_parse()` behavior for bus width/card-detect properties, correct absence or presence of 1.8 V modes by compatible, 8-bit eMMC enumeration when `SDHCI_CAN_DO_8BIT` is set, and suspend/resume via platform PM ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-npcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-arasan.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-arasan.c

Purpose: this is the OF/platform driver for Arasan SDHCI IP and many SoC integrations, including generic Arasan 4.9a/5.1/8.9a, Rockchip RK3399, Intel LGM/Keem Bay, Axiado, Xilinx ZynqMP, Versal, and Versal Net eMMC. It layers SDHCI quirks, optional CQE, SoC syscon capability programming, PHY handling, clock providers, phase-delay programming, and PM around the generic SDHCI core.

Important APIs, types, and functions: `struct sdhci_arasan_data` holds host, clocks, PHY, CQE flag, clock phase data, syscon map, and quirks. `struct sdhci_arasan_soc_ctl_map` describes syscon fields for base clock, multiplier, and 64-bit support. `struct sdhci_arasan_clk_data` registers card/sample clock providers and stores per-timing phase maps. Key functions include `sdhci_arasan_set_clock()`, `sdhci_arasan_reset()`, `sdhci_arasan_set_power_and_bus_voltage()`, `sdhci_arasan_cqe_enable()`, the ZynqMP/Versal phase setters, `arasan_zynqmp_execute_tuning()`, `sdhci_arasan_register_sdclk()`, `sdhci_zynqmp_set_dynamic_config()`, and `sdhci_arasan_add_host()`.

Control flow: probe selects match data, initializes an SDHCI platform host, obtains optional syscon, gets and enables `clk_ahb` and `clk_xin`, optionally adjusts `clk_xin` to `clock-frequency`, enables an optional DLL gate clock, applies DT quirks, updates syscon clock multiplier/base clock/64-bit support when needed, registers exported clocks for PHY consumers, installs ZynqMP tuning if applicable, parses clock phases and MMC DT, applies ZynqMP firmware dynamic config when supported, initializes an external PHY for `arasan,sdhci-5.1`, enables CQE for that path, marks internal PHY registers for Versal Net eMMC, and finally registers the host or CQHCI host.

State and persistence: persistent state includes whether the PHY is powered, whether CQE is enabled, registered clock providers, parsed phase maps, syscon-backed capability values, and quirk flags. Suspend marks retune needed except mode 3, suspends CQE, suspends SDHCI, powers off PHY, and disables clocks. Resume reenables clocks, powers PHY when needed, resumes SDHCI, and resumes CQE.

Dependencies and integration points: the driver uses SDHCI, CQHCI, common clock providers, generic PHY, regmap/syscon, reset controls, Xilinx firmware calls, OF clock phase parsing, and compatible-specific platform data. The exported card/sample clocks intentionally use `CLK_GET_RATE_NOCACHE` because SDHCI changes rates internally.

Risks: the driver covers many SoC variants, so quirk ordering and compatible matching are sensitive. PHY power-cycling is conditional on clock rate and can fail during clock changes. Syscon writes silently skip unavailable fields but warn on unexpected regmap errors. CQE enable drains `SDHCI_DATA_AVAILABLE` manually. ZynqMP firmware configuration and DLL reset paths depend on firmware support and clock-output names. The Arasan 5.1 voltage switch intentionally suppresses real 1.8 V switching semantics, so board assumptions matter.

Test signals: validate each compatible's quirks, clock phase programming across timings, PHY power transitions at low and high rates, CQE bring-up/recovery, ZynqMP firmware config and tuning reset, syscon baseclk/multiplier/support64b writes, suspend/resume with PHY and CQE, card-detect stability polling, and Versal Net internal PHY DLL readiness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-arasan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-aspeed-test.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-aspeed-test.c

Purpose: this KUnit companion file tests the ASPEED phase-to-tap conversion helper that is compiled from `sdhci-of-aspeed.c` when `CONFIG_MMC_SDHCI_OF_ASPEED_TEST` is enabled. It focuses on the arithmetic that maps requested phase degrees to ASPEED tap register values and the clock-inversion flag.

Important APIs, types, and functions: the tests call `aspeed_sdhci_phase_to_tap(NULL, rate, phase)` directly and compare against expected values with `KUNIT_EXPECT_EQ()`. `ASPEED_SDHCI_TAP_PARAM_INVERT_CLK` is included in expected outputs for phase requests at or above 180 degrees. The suite is named `sdhci-of-aspeed`.

Control flow: `aspeed_sdhci_phase_ddr52()` tests a 52 MHz DDR52-style rate around low-degree tap boundaries and around 180-degree inversion boundaries. `aspeed_sdhci_phase_hs200()` repeats equivalent boundary testing at 200 MHz, including maximum tap clamping near 90/270-degree requests. The `kunit_case` array registers both tests and `kunit_test_suite()` exposes the suite.

State and persistence: there is no persistent state. The test relies on a static helper included into the same translation unit as the production driver, so it can exercise a `static` function without exporting it.

Dependencies and integration points: this file depends on `<kunit/test.h>` and on being included from `sdhci-of-aspeed.c` after the helper and constants are defined. It is controlled by `CONFIG_MMC_SDHCI_OF_ASPEED_TEST`, not by runtime platform probing.

Risks: coverage is intentionally narrow: it verifies boundary arithmetic but not register writes, phase descriptor masks, DT phase parsing, or full clock programming. Passing `NULL` as device is safe for this helper because the device is only used for debug logging, but future helper changes could break that assumption.

Test signals: the direct signal is a passing KUnit suite named `sdhci-of-aspeed`. The selected values check off-by-one behavior, inversion at 180 degrees, and tap clamping for both 52 MHz and 200 MHz rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-aspeed-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-aspeed.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-aspeed.c

Purpose: this driver supports ASPEED SD/SDIO/SDHCI controllers. It has a parent SD controller driver that owns shared SDC registers and creates child SDHCI platform devices, plus a child SDHCI driver that programs per-slot clock division, 8-bit mode, card-detect polarity adjustment, capabilities mirrors, and AST2600 phase taps.

Important APIs, types, and functions: `struct aspeed_sdc` stores shared controller clock, resource, lock, and registers. `struct aspeed_sdhci` stores per-slot platform data, parent pointer, bus-width mask, clock phase map, and phase descriptor. `aspeed_sdhci_phase_to_tap()` converts degree/rate inputs into tap values and an inversion bit; `aspeed_sdhci_configure_phase()` applies DT phase maps. `aspeed_sdhci_set_clock()`, `aspeed_sdhci_set_bus_width()`, `aspeed_sdhci_readl()`, `aspeed_sdhci_probe()`, and `aspeed_sdc_probe()` are the main integration points.

Control flow: the parent probe deasserts optional reset, enables the SDC clock, maps shared registers, stores driver data, and creates child platform devices for each available child node. The child probe selects AST2400/2500/2600 pdata, initializes SDHCI, derives the slot from MMIO offset relative to the parent resource, selects phase descriptors, applies DT SDHCI properties, mirrors 1.8 V and SDR104 capabilities into shared registers when requested, enables the child clock, parses MMC properties and phase maps, then registers the host. Clock setting disables SDHCI clock control, chooses a one-hot-like divider from the parent clock, configures phase taps, and calls `sdhci_enable_clk()`.

State and persistence: shared state is the SDC register block guarded by `spinlock_t lock`, especially 8-bit and phase fields. Per-slot state is slot-derived masks and parsed clock phases. Clocks remain enabled while devices are bound and are disabled in remove. Optional KUnit tests are included at compile time.

Dependencies and integration points: the driver uses SDHCI platform helpers, OF child device creation, common clocks, reset controls, MMC DT parsing, and shared ASPEED SDC registers. Compatibles include `aspeed,ast2400-sd-controller`, `aspeed,ast2500-sd-controller`, `aspeed,ast2600-sd-controller`, and matching child `*-sdhci` compatibles.

Risks: slot calculation depends on 0x100-aligned child resources after the parent base. Shared phase and width registers require correct locking across slots. Capability mirroring is manually derived from SDHCI capability registers and DT properties. Phase conversion uses a measured maximum tap delay and clamps out-of-range requests, so board timing margins need validation. `aspeed_sdhci_readl()` flips card-present only when `MMC_CAP2_CD_ACTIVE_HIGH` is set, making card-detect polarity a key board property.

Test signals: probe should report configured slot numbers, SD/SDIO clocks should divide correctly on AST2400/2500 and AST2600, 8-bit mode should toggle shared SDC bits, SDR104/1.8 V caps should mirror, phase DT values should produce expected taps, card-detect polarity should be correct, and the optional KUnit suite should pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-aspeed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-at91.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-at91.c

Purpose: this is the Atmel/Microchip AT91 SDMMC SDHCI driver for SAMA5D2 and SAM9X60. It supplies controller-specific clock programming, capability/preset rewriting, force-card-detect handling, DDR52 mode setup, analog calibration behavior, and runtime PM clock management.

Important APIs, types, and functions: `struct sdhci_at91_soc_data` selects platform data and describes whether the base clock is internally generated. `struct sdhci_at91_priv` stores `hclock`, `gck`, `mainck`, restore state, and calibration behavior. Key functions are `sdhci_at91_set_clock()`, `sdhci_at91_set_uhs_signaling()`, `sdhci_at91_reset()`, `sdhci_at91_set_clks_presets()`, runtime suspend/resume, and probe/remove. `sdhci_at91_sama5d2_ops` wires custom clock/reset/UHS functions into SDHCI.

Control flow: probe selects SoC data, initializes SDHCI, gets base/hclock/multclk clocks, programs capabilities and presets through `sdhci_at91_set_clks_presets()`, reads the `microchip,sdcal-inverted` property, parses MMC and SDHCI DT properties, enables runtime PM, marks HS200 broken, registers the host, enables polling for removable non-GPIO card detect, forces card detect for nonremovable or GPIO-CD configurations, and autosuspends. Preset programming temporarily enables `hclock`, calculates base and multiplier from clock rates, unlocks capability writes with `SDMMC_CACR_KEY | SDMMC_CACR_CAPWREN`, updates capability registers and SDR/DDR presets, relocks, and enables `mainck` and `gck`.

State and persistence: persistent state includes clock handles, `restore_needed`, and `cal_always_on`. Runtime suspend calls `sdhci_runtime_suspend_host()`, marks retune needed where appropriate, and disables all clocks. System suspend sets `restore_needed`; runtime resume reprograms capabilities/presets after system sleep or simply reenables clocks, then resumes SDHCI. Reset reapplies force-card-detect and optional always-on calibration because full reset clears those bits.

Dependencies and integration points: the file depends on SDHCI platform helpers, clock APIs, runtime PM, MMC GPIO card detect helpers, DT compatibles `atmel,sama5d2-sdhci` and `microchip,sam9x60-sdhci`, and the SDMMC vendor registers `MC1R`, `CACR`, and `CALCR`.

Risks: capability and preset rewriting must match real clock rates; bad values can break preset mode and SDR104's degraded 120 MHz support. The custom clock path deliberately avoids disabling internal clock during changes due to known hardware behavior. Force-card-detect is required for several board wiring cases and must be restored after reset. Runtime-suspended controllers cannot wake on native card-detect IRQ, so GPIO CD or polling is required. Always-on calibration depends on board-specific SDCAL wiring.

Test signals: validate capability and preset registers after probe and resume, clock stability polling, DDR52 MC1R bit setting, card detection with nonremovable/GPIO/polling setups, runtime autosuspend/resume, calibration completion when `microchip,sdcal-inverted` is present, and absence of HS200 advertisement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-at91.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-bst.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-bst.c

Purpose: this is the Black Sesame Technologies C1200 SDHCI driver. It handles a Synopsys/BST controller with separate CRM registers, custom clock programming, eMMC reset handling, timeout and power hooks, delay-chain tuning, voltage-stable control, MBIU burst setup, and a reserved-memory SRAM bounce buffer for a 32-bit DMA-limited eMMC path.

Important APIs, types, and functions: `struct sdhci_bst_priv` stores the CRM MMIO base. `union sdhci_bst_rx_ctrl` models RX clock control bitfields. `sdhci_bst_ops` hooks custom `.set_clock`, `.reset`, `.set_power`, `.set_timeout`, `.platform_execute_tuning`, and `.voltage_switch`. Helpers `sdhci_bst_crm_read/write()`, `sdhci_bst_enable_clk()`, `sdhci_bst_execute_tuning()`, and bounce-buffer allocation/free implement the core behavior.

Control flow: probe initializes SDHCI with BST quirks, parses MMC DT properties, applies SDHCI OF properties, maps the second resource as CRM registers, allocates a 32 KiB coherent bounce buffer from reserved memory, then registers the host. Clock setting disables card/internal/PLL clock on zero rate; otherwise it computes a divider from a fixed 200 MHz maximum, programs timer and RX clock CRM fields, disables and reenables BCLK, writes the SDHCI divider bits, and enables PLL/card/internal clocks. Reset toggles eMMC reset via the vendor pointer-derived register when the host is eMMC-only, otherwise falls back to `sdhci_reset()`.

State and persistence: driver-specific state is the CRM base and the coherent bounce buffer address/size stored on `sdhci_host`. Hardware state includes CRM timer/BCLK/RX/voltage registers, MBIU burst bits, delay-chain selection, and eMMC reset. Remove frees the bounce buffer, releases reserved memory, and removes the platform host.

Dependencies and integration points: the driver uses SDHCI platform APIs, reserved-memory attachment, coherent DMA allocation, iopoll, bitfield helpers, and the `bst,c1200-sdhci` compatible. It relies on DT providing a second MMIO resource for CRM and a reserved-memory region suitable for the controller's 32-bit DMA limit.

Risks: the divider calculation is integer and written into a 10-bit CRM field and 8-bit SDHCI field; extreme requested clocks need hardware validation. Tuning selects the midpoint of the longer pass window but does not explicitly handle all-pass/all-fail edge cases beyond clamping negative best to zero. Bounce buffer allocation is mandatory, so missing reserved memory prevents probe. Power-off disables burst, BCLK, RX update, and voltage-stable bits; resume behavior depends on generic SDHCI reconfiguration.

Test signals: successful reserved-memory initialization and 32 KiB coherent allocation, correct clock rates and stable-clock polling, eMMC reset pulse during full reset on non-SD hosts, tuning pass-window selection over 32 delay-chain entries, voltage switch setting `BST_VOL_STABLE_ON`, MBIU burst enable/disable with power state, and DMA transfers constrained through the bounce buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-bst.c -->
