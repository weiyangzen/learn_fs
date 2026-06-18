# subset-b-001162 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rv1126b.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rv1126b.c

Purpose: RV1126B clock controller description and init code. It declares PLL rate tables, CPU clock rate/divider tables, parent-name arrays, and a large `rv1126b_clk_branches[]` topology for top, bus, peri, core, PMU, PMU1, DDR, VI, VEPU, NPU, VDO, and VCP CRU islands.

Important APIs/types/functions: uses Rockchip CCF macros from `clk.h`: `PLL`, `COMPOSITE`, `COMPOSITE_FRAC`, `COMPOSITE_FRACMUX_NOGATE`, `COMPOSITE_NODIV`, `GATE`, `DIV`, `FACTOR`, `MUX`, and `PNAME`. `rv1126b_clk_init()` is the central entry point. `clk_rv1126b_probe()` dispatches platform-device probing through `device_get_match_data()`. `CLK_OF_DECLARE()` and `builtin_platform_driver_probe()` provide early DT and platform-driver registration.

Control flow: init computes the onecell size with `rockchip_clk_find_max_clk_id()`, maps the CRU registers with `of_iomap()`, creates a provider with `rockchip_clk_init()`, registers PLLs, branches, the multi-PLL ARM clock, reset lookup table, restart handler, and OF clock provider, then writes five PVTPLL source-select registers.

State and persistence: state is hardware-backed CRU register state plus the in-memory onecell clock lookup table. PLLs and gates marked `CLK_IS_CRITICAL` are expected to stay enabled. No runtime persistence exists beyond programmed registers.

Dependencies and integration: depends on `dt-bindings/clock/rockchip,rv1126b-cru.h`, `rv1126b_rst_init()`, Rockchip common clock helpers, Linux CCF, OF, platform-device, and restart notifier integration. Consumers bind through compatible `rockchip,rv1126b-cru`.

Risks: the branch table is dense and register-bit oriented; a wrong parent array, divider width, gate bit, or `CLK_IS_CRITICAL` flag can break boot, display, storage, DDR, NPU/video, or PMU operation. The final direct `writel_relaxed()` PVTPLL selects bypass normal CCF registration and need hardware validation.

Test signals: boot on RV1126B with clock provider present, `/sys/kernel/debug/clk/clk_summary` parent/rate checks, reset-controller phandle use, restart path, UART/storage/display/audio operation, and exercising rate changes on CPU, fractional UART/audio clocks, and PVTPLL-rooted domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rv1126b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk.c

Purpose: shared Rockchip common-clock registration engine. It translates declarative `struct rockchip_clk_branch` and `struct rockchip_pll_clock` tables from SoC files into Linux CCF clocks and providers.

Important APIs/types/functions: `rockchip_clk_register_branch()` builds composite mux/divider/gate clocks. `rockchip_clk_register_frac_branch()` builds fractional divider clocks and optional child muxes. `rockchip_clk_register_factor_branch()` builds fixed-factor plus optional gate clocks. Exported provider APIs include `rockchip_clk_init()`, `rockchip_clk_init_early()`, `rockchip_clk_finalize()`, `rockchip_clk_of_add_provider()`, `rockchip_clk_register_plls()`, `rockchip_clk_register_branches()`, `rockchip_clk_register_late_branches()`, `rockchip_clk_register_armclk()`, `rockchip_clk_register_armclk_multi_pll()`, `rockchip_clk_protect_critical()`, and `rockchip_register_restart_notifier()`.

Control flow: SoC init allocates a provider, then registers PLLs and branches. Branch registration switches on `branch_type`, chooses CRU or auxiliary GRF regmap, creates the relevant CCF object, logs failures, and installs successful clocks in the onecell lookup. Late linked gates become platform devices. Restart uses a reboot notifier that writes the configured reset register.

State and persistence: allocates provider context, onecell clock table, branch helper objects, fractional notifier state, GRF regmap references, and static restart notifier globals. Hardware state persists in CRU/GRF registers.

Dependencies and integration: Linux CCF, syscon regmap, OF clock provider API, restart handlers, platform devices, and Rockchip-specific PLL/CPU/MMC/DDR/inverter/half-divider helpers.

Risks: allocation failures during composite registration can leave partially registered clocks. Fractional child muxes rely on matching parent names; if not found, rate changes may not work. Restart globals support one active Rockchip restart base. Auxiliary GRF selection depends on correct `grf_type`.

Test signals: boot logs without failed clock registrations, correct onecell indexes for DT consumers, rate-change tests on fractional clocks with child muxes, late linked-gate runtime PM behavior, and reboot/reset operation through the registered notifier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk.h -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk.h

Purpose: shared header for Rockchip clock-controller drivers. It defines CRU register-offset macros for many SoCs, PLL/rate/provider data structures, branch construction macros, reset registration hooks, and exported common-clock helper prototypes.

Important APIs/types/functions: `HIWORD_UPDATE()`, SoC register macros such as `RV1126B_*`, `RK3506_*`, `RK3528_*`, `RK3562_*`, `RK3576_*`, and `RK3588_*`, `enum rockchip_pll_type`, `struct rockchip_pll_rate_table`, `struct rockchip_pll_clock`, `struct rockchip_clk_provider`, `struct rockchip_clk_branch`, `struct rockchip_cpuclk_rate_table`, `struct rockchip_cpuclk_reg_data`, and `struct rockchip_gate_link_platdata`. Branch macros include `PLL`, `PNAME`, `COMPOSITE*`, `MUX*`, `DIV*`, `GATE*`, `GATE_LINK`, `MMC*`, `INVERTER`, `FACTOR*`, and half-divider variants.

Control flow: the header does not execute logic, but it determines how SoC table initializers populate branch fields consumed by `clk.c`. Inline lookup helpers read and write `ctx->clk_data.clks[id]`. Reset init prototypes connect SoC clock init files to reset mapping files.

State and persistence: defines provider state shape: CRU MMIO base, onecell data, OF node, main and auxiliary GRF regmaps, and a spinlock. Branch entries encode hardware register offsets, shifts, flags, lookup IDs, linked IDs, and optional child muxes.

Dependencies and integration: Linux CCF, IO, hashtable support, reset controller optional compile path, and Rockchip dt-binding IDs. It is the ABI between SoC-specific table files and common Rockchip CCF implementation.

Risks: macro argument ordering is easy to misuse; mistakes silently map into wrong registers or flags. Register-offset definitions span many hardware generations, so overlapping naming and CRU base arithmetic must be kept exact. `SGRF_GATE()` intentionally models secure-only clocks as fixed factors, which can hide hardware control limitations.

Test signals: compile coverage for all SoC clock drivers, Coccinelle/static checks for macro initializers, boot-time clock registration on affected SoCs, and dt-binding ID to onecell lookup validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/gate-link.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/gate-link.c

Purpose: implements late Rockchip linked-gate clocks that need a second clock kept active through runtime PM while the gate exists.

Important APIs/types/functions: `rk_clk_gate_link_probe()`, `rk_clk_gate_link_register()`, `struct rockchip_gate_link_platdata`, `rockchip_clk_get_lookup()`, `rockchip_clk_set_lookup()`, `pm_clk_add_clk()`, `devm_pm_runtime_enable()`, `devm_pm_clk_create()`, and runtime PM ops using `pm_clk_suspend`/`pm_clk_resume`.

Control flow: `rockchip_clk_register_late_branches()` creates a platform device carrying provider and branch platform data. The gate-link driver probes, enables runtime PM, creates a PM clock list, looks up the linked clock by `linked_clk_id`, adds it to PM clocks, registers the actual gate with `clk_register_gate()`, and stores it in the provider lookup table. On registration failure it removes the linked PM clock.

State and persistence: state is devres-managed PM runtime resources, PM clock membership, one registered gate clock, and the shared provider lookup table. Hardware gate state is still stored in the CRU register selected by the branch.

Dependencies and integration: Linux platform bus, CCF gate registration, PM clock framework, runtime PM, firmware node reuse from the parent clock controller, and Rockchip branch metadata.

Risks: missing platform data is fatal. A bad `linked_clk_id` can add an error-valued or wrong clock to PM handling. Since linked gates are registered late, consumers may defer until the platform device probes. Runtime PM behavior depends on parent device integration.

Test signals: linked gate consumer probing without permanent `-EPROBE_DEFER`, runtime suspend/resume toggling the linked clock as expected, clk summary showing the late gate, and negative tests for invalid linked IDs or unavailable PM clock setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/gate-link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/rst-rk3506.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/rst-rk3506.c

Purpose: reset-controller lookup table for RK3506. It maps public `dt-bindings/reset/rockchip,rk3506-cru.h` reset IDs to CRU soft-reset register/bit positions.

Important APIs/types/functions: `RK3506_CRU_RESET_OFFSET(id, reg, bit)` computes LUT entries as `reg * 16 + bit`; `rk3506_register_offset[]` holds sparse indexed reset mappings; `rk3506_rst_init()` registers the LUT with `rockchip_register_softrst_lut()`.

Control flow: the clock driver calls `rk3506_rst_init(np, reg_base)`. That registers a reset controller at `reg_base + RK3506_SOFTRST_CON(0)` using `ROCKCHIP_SOFTRST_HIWORD_MASK`, so reset assert/deassert writes use Rockchip high-word mask semantics.

State and persistence: no mutable local state after init. Reset state is in hardware soft-reset registers. The common reset controller stores the LUT pointer and maps consumer reset IDs through it.

Dependencies and integration: Linux reset-controller framework through `softrst.c`, RK3506 reset dt-bindings, and RK3506 CRU offset macros from `clk.h`.

Risks: the table skips unused registers and IDs; an unlisted binding ID has a zero default if still within array bounds, which can accidentally target SOFTRST_CON00 bit 0 if bindings and table diverge. Wrong register/bit values can hold CPU, bus, DDR, USB, audio, GPIO, storage, or video blocks in reset.

Test signals: reset phandle users for UART/I2C/SPI/GPIO/audio/storage/USB/video probe successfully, targeted reset pulses affect only intended blocks, and dt-binding max ID coverage matches `ARRAY_SIZE(rk3506_register_offset)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/rst-rk3506.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/rst-rk3528.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/rst-rk3528.c

Purpose: RK3528 reset-controller LUT. It describes reset ID to CRU SOFTRST register/bit mappings for core, bus, VPU, PCIe, GPU, encoder/decoder, VO, HDMI, USB, DDR, and peripheral domains.

Important APIs/types/functions: `RK3528_CRU_RESET_OFFSET()` creates high-word reset bit indexes, `rk3528_register_offset[]` is the sparse binding-ID lookup table, and `rk3528_rst_init()` registers the table.

Control flow: SoC clock init invokes `rk3528_rst_init()`, which calls `rockchip_register_softrst_lut(np, rk3528_register_offset, ARRAY_SIZE(...), reg_base + RK3528_SOFTRST_CON(0), ROCKCHIP_SOFTRST_HIWORD_MASK)`. Common reset ops later translate reset IDs through the LUT before writing the soft-reset bank.

State and persistence: local state is immutable after registration. Asserted reset bits persist in CRU hardware until deasserted by reset consumers or firmware.

Dependencies and integration: RK3528 reset dt-binding IDs, `clk.h` RK3528 CRU macros, and `softrst.c`. It is consumed by device-tree reset phandles on RK3528 platforms.

Risks: table correctness is hardware critical; bad entries can reset unrelated blocks. The broad range through SOFTRST_CON46 increases risk of binding-table drift. PCIe, HDMI, USB PHY, DDR PHY, and media resets often have ordering requirements outside this file, so consumers must sequence clocks/resets/power domains correctly.

Test signals: compare against vendor TRM/register dumps, boot with all reset consumers enabled, exercise PCIe/USB/display/video/storage reset cycles, and verify no kernel warnings from missing reset IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/rst-rk3528.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/rst-rk3562.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/rst-rk3562.c

Purpose: RK3562 reset-controller LUT spanning multiple CRU address islands: main CRU, PMU0, PMU1, DDR, SUBDDR, and PERI.

Important APIs/types/functions: `RK3562_CRU_RESET_OFFSET()`, `RK3562_PMU0CRU_RESET_OFFSET()`, `RK3562_PMU1CRU_RESET_OFFSET()`, `RK3562_DDRCRU_RESET_OFFSET()`, `RK3562_SUBDDRCRU_RESET_OFFSET()`, and `RK3562_PERICRU_RESET_OFFSET()` encode island base offsets into one LUT value. `rk3562_rst_init()` registers `rk3562_register_offset[]`.

Control flow: reset consumers call common reset ops; common code looks up the ID, divides by 16 to choose the bank, and writes high-word mask bits. Because this file encodes island offsets as large bank values, one reset controller can cover all CRU islands from a single mapped base.

State and persistence: immutable LUT plus CRU hardware reset bits. No local runtime state.

Dependencies and integration: RK3562 reset bindings, common Rockchip reset controller, RK3562 CRU address layout from `clk.h`, and DT reset phandles for CPU, NPU, GPU, media, display, PHP, bus, PMU, DDR, storage, USB, serial, crypto, and GPIO blocks.

Risks: base offset arithmetic uses byte offsets multiplied by four to match the common reset bank calculation. Any mismatch with mapped CRU aperture layout corrupts target bank selection. Sparse missing IDs may default to zero if binding/table coverage diverges.

Test signals: hardware reset tests across every island, especially PMU and DDR resets; boot with broad peripheral coverage; binding-table consistency checks; and register trace validation that each ID writes the intended `*_SOFTRST_CON` register.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/rst-rk3562.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/rst-rk3576.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/rst-rk3576.c

Purpose: RK3576 reset-controller LUT for a large SoC with main, PHP, secure-nonsecure, and PMU1 CRU reset islands.

Important APIs/types/functions: `RK3576_CRU_RESET_OFFSET()`, `RK3576_PHPCRU_RESET_OFFSET()`, `RK3576_SECURENSCRU_RESET_OFFSET()`, and `RK3576_PMU1CRU_RESET_OFFSET()` encode reset IDs. `rk3576_register_offset[]` maps many domains: top/bus, audio, I2C/UART/SPI/PWM/timers, DDR channels, NPU/RKNN, storage/PHP/PCIe/SATA, SDGMAC, RKVDEC/VEPU/VPU, VI/CSI, VOP/display, VO0/VO1, GPU, center, PHY, secure, and PMU blocks.

Control flow: `rk3576_rst_init()` registers the LUT against `reg_base + RK3576_SOFTRST_CON(0)` with high-word mask reset semantics. The common `softrst.c` controller handles assert/deassert for all IDs by using the encoded bank/bit values.

State and persistence: reset state persists in CRU registers; the C file contributes only static mapping data after init.

Dependencies and integration: RK3576 reset dt-bindings, CRU offsets from `clk.h`, common reset-controller implementation, and device-tree reset users in complex subsystems such as PCIe/SATA/UFS/display/USB/DDR.

Risks: very broad hardware coverage makes off-by-one register indexes dangerous. PMU1 and secure-nonsecure offset encoding must align with the CRU MMIO mapping. Some high-speed PHY/display resets require sequencing with PHY, power-domain, and clock drivers.

Test signals: probe reset consumers across all domains, run suspend/resume and peripheral reset cycles, verify no unintended adjacent reset bits through register tracing, and compare LUT against RK3576 TRM and binding header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/rst-rk3576.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/rst-rk3588.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/rst-rk3588.c

Purpose: RK3588 reset-controller LUT. It maps reset IDs to main CRU, PHPTOPCRU, PMU1CRU, and SECURECRU soft-reset bits for one of the largest Rockchip clock/reset domains.

Important APIs/types/functions: `RK3588_CRU_RESET_OFFSET()`, `RK3588_PHPTOPCRU_RESET_OFFSET()`, `RK3588_SECURECRU_RESET_OFFSET()`, `RK3588_PMU1CRU_RESET_OFFSET()`, `rk3588_register_offset[]`, and `rk3588_rst_init()`. The table includes comments for several resets missing in the TRM but still exposed.

Control flow: SoC clock setup calls `rk3588_rst_init()`, registering the LUT with `rockchip_register_softrst_lut()` at `RK3588_SOFTRST_CON(0)` and high-word mask mode. Reset consumers later assert/deassert through common reset ops.

State and persistence: immutable mapping table plus hardware CRU reset bits. No local dynamic state.

Dependencies and integration: RK3588 reset dt-bindings, `clk.h` RK3588 offsets, common Rockchip reset controller, and DT consumers for USB/USBDP, DCPHY, audio, bus, UART/I2C/SPI/CAN, DDR, NPU, storage, PCIe/SATA, RKVDEC/RKVENC, VI/CSI, VOP/HDMI/DP, GPU, AV1, secure crypto, PMU, and TRNG blocks.

Risks: multi-island offsets and large sparse table are error-prone. Entries noted as missing from TRM require silicon/vendor validation. DDR and display/PHY reset sequencing is high impact. Wrong secure reset entries can affect boot/security services.

Test signals: comprehensive boot on RK3588 boards, reset API smoke tests for all active DT consumers, PCIe/USB/display/media/GPU/NPU exercise, suspend/resume, register tracing for missing-TRM entries, and binding coverage checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/rst-rk3588.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/rst-rv1126b.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/rst-rv1126b.c

Purpose: RV1126B reset-controller LUT spanning top, bus, peri, core, PMU, PMU1, DDR, SUBDDR, VI, VEPU, NPU, VDO, and VCP CRU islands.

Important APIs/types/functions: island-specific macros such as `TOPCRU_RESET_OFFSET()`, `BUSCRU_RESET_OFFSET()`, `PERICRU_RESET_OFFSET()`, `CORECRU_RESET_OFFSET()`, `PMUCRU_RESET_OFFSET()`, `PMU1CRU_RESET_OFFSET()`, `DDRCRU_RESET_OFFSET()`, `SUBDDRCRU_RESET_OFFSET()`, `VICRU_RESET_OFFSET()`, `VEPUCRU_RESET_OFFSET()`, `NPUCRU_RESET_OFFSET()`, `VDOCRU_RESET_OFFSET()`, and `VCPCRU_RESET_OFFSET()`. `rv1126b_rst_init()` registers `rv1126b_register_offset[]`.

Control flow: called by `rv1126b_clk_init()` after clocks are registered. The common reset controller uses the LUT to convert reset IDs to bank/bit writes under `ROCKCHIP_SOFTRST_HIWORD_MASK`.

State and persistence: static mapping data and hardware reset bits. Assert/deassert state persists in CRU registers until changed.

Dependencies and integration: RV1126B reset dt-bindings, RV1126B CRU offset macros from `clk.h`, common Rockchip `softrst.c`, and reset consumers across CPU, buses, crypto, serial, audio, PMU, DDR, image/video, NPU, and VCP domains.

Risks: the file covers many separately based CRUs by encoding byte offsets into the lookup value; incorrect base arithmetic can send reset writes to the wrong island. PVTPLL-related resets must align with clock source initialization in `clk-rv1126b.c`.

Test signals: reset phandle probes on RV1126B DTs, targeted reset toggles across every CRU island, NPU/VI/VEPU/VDO/VCP subsystem bring-up, and cross-check binding IDs against nonzero intended mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/rst-rv1126b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/softrst.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/softrst.c

Purpose: common Rockchip reset-controller implementation used by SoC-specific reset LUT files and simple contiguous reset banks.

Important APIs/types/functions: `struct rockchip_softrst`, `rockchip_softrst_assert()`, `rockchip_softrst_deassert()`, `rockchip_softrst_ops`, and exported `rockchip_register_softrst_lut()`. `rockchip_register_softrst()` is an inline wrapper in `clk.h`.

Control flow: registration allocates a reset-controller object, records optional LUT, base, register count, flags, and per-register bit count, then calls `reset_controller_register()`. Assert/deassert optionally remap `id = lut[id]`, compute `bank = id / num_per_reg` and `offset = id % num_per_reg`, then either write high-word mask values or perform locked read/modify/write.

State and persistence: one heap object per reset controller stores mapping and spinlock. Hardware CRU reset registers hold actual reset state. High-word mode treats each register as 16 reset bits; non-high-word mode treats each as 32 bits.

Dependencies and integration: Linux reset-controller framework, MMIO helpers, spinlocks, and Rockchip clock headers. SoC clock init calls this after mapping CRU registers.

Risks: LUT bounds are trusted by reset core via `nr_resets`; sparse C arrays with omitted IDs may contain zero entries. Non-high-word mode requires locking to avoid clobbering unrelated bits. High-word mode depends on Rockchip write-mask semantics and does not read back state.

Test signals: reset controller appears in DT provider lookup, assert/deassert writes expected values, concurrent reset users do not corrupt non-high-word registers, and invalid IDs are rejected by reset core based on `nr_resets`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/softrst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/samsung/Kconfig

Purpose: Kconfig menu for Samsung clock-controller support. It defines umbrella and SoC-specific symbols for Exynos, S3C64xx, S5PV210, Tesla FSD, audio subsystem, clock output, and ACPM firmware-controlled clocks.

Important APIs/types/functions: configuration symbols include `COMMON_CLK_SAMSUNG`, `S3C64XX_COMMON_CLK`, `S5PV210_COMMON_CLK`, `EXYNOS_3250_COMMON_CLK`, `EXYNOS_4_COMMON_CLK`, `EXYNOS_5250_COMMON_CLK`, `EXYNOS_5260_COMMON_CLK`, `EXYNOS_5410_COMMON_CLK`, `EXYNOS_5420_COMMON_CLK`, `EXYNOS_ARM64_COMMON_CLK`, `EXYNOS_AUDSS_CLK_CON`, `EXYNOS_CLKOUT`, `EXYNOS_ACPM_CLK`, and `TESLA_FSD_COMMON_CLK`.

Control flow: no runtime flow. Kconfig dependency and select logic controls which clock driver objects compile. `COMMON_CLK_SAMSUNG` depends on OF and selects the right SoC clocks based on architecture symbols.

State and persistence: build-time configuration only; no runtime state.

Dependencies and integration: architecture symbols such as `ARCH_EXYNOS`, `SOC_EXYNOS*`, `ARCH_S3C64XX`, `ARCH_S5PV210`, `ARCH_TESLA_FSD`, `ARM`, `ARM64`, `COMPILE_TEST`, and ACPM protocol availability.

Risks: `select` can force lower-level symbols, so dependency mistakes may compile drivers on unsupported architectures. `EXYNOS_ACPM_CLK` allows compile testing without `EXYNOS_ACPM_PROTOCOL`, so runtime users still need the firmware protocol. Help text contains minor typos but no behavior.

Test signals: `allyesconfig`/`allmodconfig`/`COMPILE_TEST` builds, Exynos platform defconfig builds, and ensuring `CONFIG_EXYNOS_ACPM_CLK=m/y` pulls `clk-acpm.o` only when intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/samsung/Makefile

Purpose: build manifest for Samsung common clock drivers. It maps Kconfig symbols to object files.

Important APIs/types/functions: core Samsung clock helpers `clk.o`, `clk-pll.o`, and `clk-cpu.o` build under `CONFIG_COMMON_CLK`. SoC-specific objects build under their corresponding symbols, including Exynos 3250/4/5250/5260/5410/5420, ARM64 Exynos/Artpec/GS101/Auto variants, audio subsystem, clock output, ACPM, S3C64xx, S5PV210, and Tesla FSD.

Control flow: no runtime logic. Kbuild appends objects to `obj-y`/`obj-m` according to the resolved configuration.

State and persistence: build artifact selection only.

Dependencies and integration: must match symbols from `Kconfig` and source files present in the Samsung clock directory. `CONFIG_EXYNOS_ARM64_COMMON_CLK` fans out to many ARM64-family SoC files, while `CONFIG_EXYNOS_ACPM_CLK` adds `clk-acpm.o`.

Risks: stale symbol/object mappings cause missing drivers or build failures. `CONFIG_COMMON_CLK` always building base Samsung helpers means compile errors there affect all configurations with common clock enabled. Shared objects such as `clk-exynos5-subcmu.o` are included by multiple SoC configs.

Test signals: Kbuild coverage for each symbol, `make drivers/clk/samsung/` under representative configs, and checking that new Kconfig entries update this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-acpm.c -->
# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-acpm.c

Purpose: Samsung Exynos ACPM firmware-backed clock driver. It exposes clocks whose rates are controlled through the ACPM DVFS protocol rather than direct clock-controller registers.

Important APIs/types/functions: `struct acpm_clk`, `struct acpm_clk_variant`, `struct acpm_clk_driver_data`, `ACPM_CLK()`, `gs101_acpm_clks[]`, `acpm_clk_gs101`, `acpm_clk_recalc_rate()`, `acpm_clk_determine_rate()`, `acpm_clk_set_rate()`, `acpm_clk_ops`, `acpm_clk_register()`, and `acpm_clk_probe()`. Platform ID is `"gs101-acpm-clk"`.

Control flow: probe obtains an ACPM handle from the parent OF node with `devm_acpm_get_by_node()`, allocates onecell hardware-clock data and `struct acpm_clk` array, assigns sequential firmware IDs, registers each `clk_hw`, then publishes an OF hardware-clock provider. Rate reads call `dvfs_ops.get_rate()`. Rate writes call `dvfs_ops.set_rate()`. `determine_rate()` accepts the requested rate because firmware is authoritative.

State and persistence: devres-managed clock objects retain ACPM handle, mailbox channel ID, and sequential clock ID. Actual rates persist in firmware/hardware managed through ACPM.

Dependencies and integration: Linux CCF, platform bus, Samsung Exynos ACPM protocol, GS101 clock names (`mif`, `int`, CPU clusters, GPU, TPU, camera/media/display/bo), and OF onecell provider consumers.

Risks: code currently hard-codes `acpm_clk_gs101` rather than selecting driver data from the platform ID entry, limiting variant extensibility. It assumes clock IDs are zero-based, sequential, and gapless. ACPM operation failures propagate through CCF rate calls and may affect DVFS-sensitive domains.

Test signals: GS101 probe with ACPM firmware, `clk_summary` showing all ACPM clocks, successful get/set rate through CCF consumers, firmware error injection, and adding another variant to verify data selection is generalized before reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-acpm.c -->
