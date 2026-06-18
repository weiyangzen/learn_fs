# Research: subset-b-001159

Grouped research for Rockchip CRU clock drivers. Each section preserves the source path expected by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3328.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3328.c

## Purpose

`clk-rk3328.c` is the common clock framework provider for the Rockchip RK3328 clock/reset unit. It describes RK3328 PLLs, CPU clock rate transitions, mux/divider/gate topology, MMC delay/phase clocks, critical clocks, soft resets, and restart handling. The driver is instantiated through `CLK_OF_DECLARE(rk3328_cru, "rockchip,rk3328-cru", rk3328_clk_init)`, so it runs during early OF clock initialization rather than through a normal loadable platform-driver probe path.

The file is almost entirely declarative. Its data tables tell the shared Rockchip clock core how to expose hardware clocks to device tree consumers via dt-binding IDs from `include/dt-bindings/clock/rk3328-cru.h`.

## Important APIs, Types, And Functions

Key local data:

- `enum rk3328_plls` indexes APLL, DPLL, CPLL, GPLL, and NPLL entries.
- `rk3328_pll_rates` and `rk3328_pll_frac_rates` define integer and fractional PLL programming tables using `RK3036_PLL_RATE`.
- `rk3328_cpuclk_rates` plus `rk3328_cpuclk_data` describe valid ARM clock parent rates and divider register writes for `rockchip_clk_register_armclk`.
- `PNAME(...)` arrays define parent-name lists consumed by mux/composite macros.
- `rk3328_pll_clks` describes PLL hardware blocks with `PLL(pll_rk3328, ...)`.
- `rk3328_clk_branches` describes branch clocks with Rockchip helper macros such as `COMPOSITE`, `COMPOSITE_FRACMUX`, `COMPOSITE_NOMUX`, `COMPOSITE_NODIV`, `MUX`, `DIV`, `FACTOR`, `GATE`, `GATE_GRF`, `MMC`, and `SGRF_GATE`.
- `rk3328_critical_clocks` lists names that must be protected from disable.
- `rk3328_clk_init()` is the only executable initialization function.

Shared dependencies come from `drivers/clk/rockchip/clk.h` and `clk.c`: `rockchip_clk_init`, `rockchip_clk_register_plls`, `rockchip_clk_register_branches`, `rockchip_clk_register_armclk`, `rockchip_clk_protect_critical`, `rockchip_register_softrst`, `rockchip_register_restart_notifier`, and `rockchip_clk_of_add_provider`.

## Control Flow

Initialization is linear:

1. `rk3328_clk_init()` maps the CRU register block with `of_iomap(np, 0)`.
2. It sizes the provider clock table by calling `rockchip_clk_find_max_clk_id(rk3328_clk_branches, ARRAY_SIZE(...)) + 1`.
3. It creates a `struct rockchip_clk_provider` with `rockchip_clk_init`.
4. It registers PLLs, then branch clocks, then protects critical clocks.
5. It registers the ARM CPU clock as `ARMCLK` using `mux_armclk_p`, `rk3328_cpuclk_data`, and `rk3328_cpuclk_rates`.
6. It registers 12 soft-reset registers at `reg_base + RK3328_SOFTRST_CON(0)` using hiword-mask reset writes.
7. It registers a restart notifier using `RK3328_GLB_SRST_FST`.
8. It publishes the provider to OF with `rockchip_clk_of_add_provider`.

If the CRU region cannot be mapped or provider allocation fails, the function logs an error and returns early; the provider is not registered. On provider allocation failure it unmaps the register block.

## State And Persistence Behavior

There is no persistent filesystem or firmware state. Runtime state is in MMIO CRU/GRF registers and in common-clock-framework objects allocated during boot. PLL rates, mux selections, dividers, and gates persist only as hardware register programming until reset or suspend/resume code outside this file changes them.

The branch table writes use hiword-update masks (`MFLAGS`, `DFLAGS`, `GFLAGS`) so register updates can modify selected fields without read-modify-write hazards. Several gates are marked `CLK_IGNORE_UNUSED` or named in `rk3328_critical_clocks` to keep essential buses, DDR-related paths, GRF/SGRF access, PMU, OTG PMU, and debug/NIU paths alive even when no explicit consumer holds them.

## Dependencies And Integration Points

The driver depends on:

- Linux CCF APIs from `linux/clk-provider.h`.
- OF address mapping from `linux/of_address.h`.
- RK3328 dt-binding clock IDs.
- Rockchip shared PLL, CPU clock, reset, restart, mux, divider, gate, MMC phase, GRF gate, and SGRF helper code.
- External clock parents named by device tree or other providers, including `xin24m`, `jtag_clkin`, `gmac_clkin`, `clkin_i2s1`, `clkin_i2s2`, `usb480m_phy`, and `hdmi_phy`.

Important integration areas:

- CPU frequency scaling uses `ARMCLK`, the APLL/GPLL/DPLL/NPLL core parent mux, and the CPU divider table.
- Audio serial blocks use fractional muxes for I2S0/I2S1/I2S2 and SPDIF.
- UARTs use divider plus fractional mux paths for baud-rate generation.
- MMC/SDIO/eMMC use `MMC(...)` phase clocks against `RK3328_*_CON` registers.
- Ethernet has both MAC2IO and MAC2PHY clocking, including GRF-backed muxes and reference output gates.
- USB, HDMI/LCDC, VOP/VIO, VPU/RKVDEC/RKVENC, GPU, crypto, timers, I2C, SPI, ADC, OTP/EFUSE, DDR, and bus/peripheral domains get CCF-visible clocks.

## Risks And Edge Cases

- The clock IDs must match `rk3328-cru.h` and the SoC TRM. Any wrong ID or register bit silently misroutes consumers.
- The driver assumes all named external parents exist or may be tolerated as unresolved/dummy parents by the CCF. Missing real parent providers can prevent expected rate propagation.
- Critical-clock selection is safety-sensitive. Removing DDR, GRF, PMU, or bus roots from the list can hang the SoC when unused-clock cleanup runs.
- GRF/SGRF-backed clocks are not simple CRU bits. Incorrect GRF offsets or `grf_type_sys` use would affect Ethernet/ref-output muxing or watchdog accessibility.
- Fractional PLL and fractional branch tables must remain within hardware limits and parent-rate assumptions; bad values can break audio/UART rates.
- `clk_nr_clks` is derived only from branch IDs. PLL-only IDs are expected to fit the same ID space through the binding; a future binding addition with a larger PLL-only ID would require care.

## Test Signals

Useful validation signals include:

- Boot on RK3328 with no `could not map cru region` or `rockchip clk init failed` errors.
- `/sys/kernel/debug/clk/clk_summary` shows expected PLLs, `armclk`, bus roots, audio/UART/MMC clocks, and critical clocks enabled where expected.
- CPU frequency transitions exercise `rk3328_cpuclk_rates` without lockups.
- Serial consoles and high baud rates validate UART fractional muxes.
- I2S/SPDIF playback validates fractional audio paths.
- SDMMC/SDIO/eMMC tuning validates `MMC` phase clocks.
- Ethernet MAC2IO/MAC2PHY modes validate GRF muxes and reference clocks.
- Reboot validates `rockchip_register_restart_notifier`.
- Reset-controller consumers validate the 12 hiword soft-reset registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3328.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3368.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3368.c

## Purpose

`clk-rk3368.c` implements the RK3368 CRU clock provider. It exposes PLLs, separate big/little CPU clocks, bus and peripheral roots, display/video/audio/network/storage clocks, phase clocks for MMC-family controllers, critical clocks, soft resets, and restart support.

The driver is registered through `CLK_OF_DECLARE(rk3368_cru, "rockchip,rk3368-cru", rk3368_clk_init)`, so it is an early OF clock provider. It is structurally similar to other Rockchip CRU files but has two ARM clock domains: `ARMCLKB` and `ARMCLKL`.

## Important APIs, Types, And Functions

Key data and APIs:

- `enum rk3368_plls` indexes APLLB, APLLL, DPLL, CPLL, GPLL, and NPLL.
- `rk3368_pll_rates` provides PLL settings using the `RK3066_PLL_RATE` format.
- `rk3368_pll_clks` registers RK3066-style PLLs, with CPLL/GPLL/NPLL marked `ROCKCHIP_PLL_SYNC_RATE`.
- `rk3368_cpuclkb_data` and `rk3368_cpuclkl_data` describe the register layout for big and little CPU clusters.
- `rk3368_cpuclkb_rates` and `rk3368_cpuclkl_rates` define cluster rate/divider programming.
- `div_ddrphy_t` supplies a DDR PHY divider table for a non-linear divider mapping.
- `rk3368_clk_branches` is the main branch table for bus, DDR, audio, UART, video, VIO, GPU, peripheral, alive, and PMU clocks.
- `rk3368_critical_clocks` protects bus, PMU, DDR, OTG, and GRF/SGRF-adjacent clocks.
- `rk3368_clk_init()` performs CRU mapping and registration.

The file uses the common Rockchip macros `PLL`, `PNAME`, `MUX`, `DIV`, `GATE`, `COMPOSITE`, `COMPOSITE_FRACMUX`, `COMPOSITE_NOGATE`, `COMPOSITE_NOMUX`, `COMPOSITE_NOGATE_DIVTBL`, `FACTOR`, `FACTOR_GATE`, `MMC`, and `SGRF_GATE`.

## Control Flow

`rk3368_clk_init()` performs:

1. `of_iomap` of the CRU register block.
2. Clock table sizing from the maximum branch ID.
3. Provider allocation through `rockchip_clk_init`.
4. PLL registration for all six PLLs.
5. Branch registration for all mux/divider/gate/composite/MMC clocks.
6. Critical-clock protection.
7. Registration of `ARMCLKB` and `ARMCLKL` through two calls to `rockchip_clk_register_armclk`.
8. Registration of 15 hiword soft-reset registers at `RK3368_SOFTRST_CON(0)`.
9. Restart notifier registration using `RK3368_GLB_SRST_FST`.
10. OF provider publication.

Failures are handled early. If MMIO mapping fails, no cleanup is required. If provider allocation fails, the register mapping is released before returning.

## State And Persistence Behavior

The file has no disk-backed state. Its durable effects during runtime are CRU register programming and CCF registrations. PLL sync flags matter because parent rates may need to be synchronized with hardware state. Gate and divider writes use hiword-mask flags to update individual fields safely.

The critical list intentionally leaves infrastructure clocks enabled, including `aclk_bus`, `pclk_bus`, PMU and DDR clocks, `pclk_grf`, `pclk_sgrf`, and OTG-related paths. `SGRF_GATE(PCLK_WDT, ...)` marks watchdog access as secure-GRF controlled and therefore not normally controllable by this non-secure clock provider.

## Dependencies And Integration Points

Dependencies:

- RK3368 dt-binding IDs from `include/dt-bindings/clock/rk3368-cru.h`.
- Common Rockchip clock, PLL, CPU clock, MMC phase, reset, and restart support.
- OF-provided parent clocks such as `xin24m`, `xin32k`, `ext_gmac`, `ext_jtag`, `ext_isp`, `ext_vip`, and `ext_hsadc_tsp`.

Important consumers and integration surfaces:

- CPUfreq and SMP cluster clocking use `ARMCLKB` and `ARMCLKL`, independent PLL source gates, and divider programming for `aclkm`, `atclk`, and debug PCLK.
- DDR clocking uses DPLL/GPLL parents, `ddrphy_src`, `sclk_ddr`, `sclk_ddr4x`, and DDR controller/PHY gates.
- Audio uses I2S 8-channel, I2S 2-channel, SPDIF, and fractional muxes.
- UART0/1/3/4 use fractional paths; UART2 uses a simpler mux from `uart2_src` or `xin24m`.
- Display/video paths include VOP, VIP, ISP, eDP, HDMI, HDCP, MIPI DSI/CSI, RGA, VEPU/VDPU, HEVC, and VIO gates.
- Peripheral integration includes SPI0-2, SDMMC/SDIO/eMMC with phase clocks, NANDC, SFC, USB OTG/HSIC, GMAC, I2C, PWM, timers, ADCs, GPIO, mailbox, EFUSE, PMU, and alive-domain clocks.

## Risks And Edge Cases

- Big/little CPU clock registration has duplicated but offset-specific register data. A wrong offset in `RK3368_CLKSEL0` or `RK3368_CLKSEL1` affects only one cluster and can be hard to diagnose.
- The DDR divider table is a special-case mapping; replacing it with a linear divider would program wrong rates.
- Parent-name arrays include dummy or external names. Device-tree or board-level mismatches can leave clocks with unresolved parents.
- Secure GRF controlled watchdog gating cannot be managed normally; consumers must not assume a regular gate can enable it.
- Critical-clock underprotection can hang NoC, PMU, DDR, or debug infrastructure during unused-clock cleanup.
- PLL sync-rate flags on shared PLLs affect rate changes across consumers; incorrect flags risk rate drift or unexpected reprogramming.

## Test Signals

Validation should include:

- Boot on RK3368 without CRU map/init failures.
- `clk_summary` contains both `armclkb` and `armclkl`, PLLs, DDR roots, and critical bus/PMU clocks.
- CPUfreq or manual rate changes exercise both cluster rate tables.
- DDR stability under memory stress confirms DDR-related roots and gates.
- Console and non-console UARTs validate fractional and non-fractional UART paths.
- I2S/SPDIF playback checks audio fractional muxes.
- SDMMC/SDIO/eMMC operation and tuning validate `MMC` delay/phase entries.
- Display, ISP/VIP, HDMI/eDP/MIPI, and video codec workloads validate VIO/video branch layout.
- Reset consumers and reboot validate soft-reset and restart registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3368.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3399.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3399.c

## Purpose

`clk-rk3399.c` provides clock/reset support for the RK3399 CRU and PMUCRU. It models a large RK3399 clock tree, including main-domain PLLs, PMU-domain PPLL, two CPU clusters, DDRC, CCI/debug, USB/PCIe/GMAC, audio, UART, display, ISP, VOP, video codecs, peripheral roots, critical clocks, soft resets, and restart support.

Unlike simpler early-only CRU files, this file includes both `CLK_OF_DECLARE` hooks and a built-in platform driver. The platform driver dispatches to the same init functions based on `rockchip,rk3399-cru` or `rockchip,rk3399-pmucru` match data, while the `CLK_OF_DECLARE` hooks preserve early clock-provider availability.

## Important APIs, Types, And Functions

Key structures:

- `enum rk3399_plls` indexes main CRU PLLs: LPLL, BPLL, DPLL, CPLL, GPLL, NPLL, and VPLL.
- `enum rk3399_pmu_plls` indexes PMUCRU PPLL.
- `rk3399_pll_rates` defines RK3399 PLL programming points.
- `rk3399_pll_clks` and `rk3399_pmu_pll_clks` describe main and PMU PLL blocks using `PLL(pll_rk3399, ...)`.
- `rk3399_cpuclkl_data`, `rk3399_cpuclkb_data`, `rk3399_cpuclkl_rates`, and `rk3399_cpuclkb_rates` describe little and big cluster ARM clocks.
- `rk3399_clk_branches` is the main CRU branch table.
- `rk3399_clk_pmu_branches` is the PMUCRU branch table.
- `rk3399_cru_critical_clocks` and `rk3399_pmucru_critical_clocks` protect essential infrastructure.
- `rk3399_clk_init()` initializes the main CRU.
- `rk3399_pmu_clk_init()` initializes the PMUCRU.
- `clk_rk3399_probe()` calls the proper init function from `device_get_match_data`.

The file uses advanced Rockchip branch helpers including `COMPOSITE_FRACMUX_NOGATE`, `COMPOSITE_DDRCLK`, `INVERTER`, `MMC`, `SGRF_GATE`, and many normal mux/divider/gate/composite macros.

## Control Flow

Main CRU initialization:

1. `rk3399_clk_init()` maps the CRU with `of_iomap`.
2. It sizes the provider from `rk3399_clk_branches`.
3. It allocates a provider and registers main PLLs.
4. It registers main branches.
5. It registers `ARMCLKL` and `ARMCLKB` with separate parent muxes, rate tables, and CPU register data.
6. It protects main critical clocks.
7. It registers 21 hiword soft-reset registers at `RK3399_SOFTRST_CON(0)`.
8. It registers the restart notifier at `RK3399_GLB_SRST_FST`.
9. It publishes the OF clock provider.

PMUCRU initialization:

1. `rk3399_pmu_clk_init()` maps the PMU CRU region.
2. It sizes and allocates a separate provider.
3. It registers PPLL and PMU branches.
4. It protects PMU critical clocks.
5. It registers two PMU soft-reset registers.
6. It publishes the PMU OF clock provider.

The platform driver has a tiny probe path: match data holds a function pointer, and probe invokes it for the node. The platform driver is marked `suppress_bind_attrs = true`, fitting the built-in clock-provider role.

## State And Persistence Behavior

Runtime state is held in CRU/PMUCRU registers and CCF registrations. The file creates two independent provider contexts when both CRU and PMUCRU are present. Register writes use hiword update flags for muxes, dividers, gates, and inverters. PLLs are synchronized to hardware via `ROCKCHIP_PLL_SYNC_RATE` for shared PLLs, while CPU PLLs are managed by CPU clock registration.

The critical lists are broad. The main CRU protects CCI, GIC, HDCP NoCs, peripheral roots, eMMC NoC, DDRC, and both ARM clocks. The PMUCRU protects PPLL, PMU PCLK source, CM0S source, timer source, and PMU PWM PCLK. These are safety guards against common-clock unused cleanup and runtime disable.

## Dependencies And Integration Points

Dependencies:

- RK3399 dt-binding clock IDs from `include/dt-bindings/clock/rk3399-cru.h`.
- Common Rockchip CCF helpers for PLLs, CPU clocks, DDR clocks, fractional muxes, MMC phase clocks, SGRF gates, reset, and restart.
- OF/platform bus matching through `CLK_OF_DECLARE`, `of_device_id`, and `builtin_platform_driver_probe`.
- Parent clocks and external inputs such as `xin24m`, `xin32k`, USB PHY 480 MHz outputs, PCIe PHY reference, GMAC input, and display/audio external parents.

Integration surfaces:

- CPUfreq uses `ARMCLKL` and `ARMCLKB`, with parent muxes over LPLL/BPLL/DPLL/GPLL-derived sources and per-cluster divider writes.
- DDR clocking uses `COMPOSITE_DDRCLK(SCLK_DDRC, ...)` and DPLL/BPLL/LPLL/GPLL paths.
- PMU island clocks serve GPIO0/1, PMU I2C/SPI/UART4, CM0S, timers, mailbox, PMU watchdog, PMU SRAM/NoC, and low-power infrastructure.
- High-speed I/O includes USB2/USB3, Type-C PHY reference/core clocks, PCIe, GMAC/RMII, HSIC, eMMC/SD/SDIO, SFC, and SPI.
- Media/display includes VOP0/VOP1 fractional display clocks, HDMI/DP/eDP/HDCP, ISP0/1, CIF, RGA, IEP, VDU, VCODEC, GPU, VIO, MIPI DPHY, and test clock outputs.
- Audio and serial include SPDIF, I2S0/1/2, I2S output muxing, UART0-4 fractional paths, and peripheral PCLK gates.

## Risks And Edge Cases

- Dual registration paths mean early OF init and platform-driver probing must not create harmful duplicate providers. The file intentionally points both mechanisms at the same init routines; any framework behavior change around duplicate init would need review.
- There are two provider contexts with separate reset-controller ranges and critical-clock lists. Cross-domain consumers must reference the right compatible node.
- Clock names and IDs are numerous. Misordered dt-binding IDs or branch IDs can break unrelated consumers.
- DDRC, CCI, GIC, NoC, and PMU clocks are critical. Removing protection can lead to hangs during boot, suspend, or unused-clock pruning.
- Fractional display/audio/UART paths depend on correct parent and divider programming; minor register-field errors surface as baud drift, audio clock drift, or display timing failures.
- `COMPOSITE_DDRCLK` and CPU clock transitions have hardware-specific ordering expectations hidden in common Rockchip helpers; table changes should be tested on hardware.

## Test Signals

Good validation coverage includes:

- Boot with both `rockchip,rk3399-cru` and `rockchip,rk3399-pmucru` present and no duplicate-provider warnings.
- `clk_summary` shows main CRU and PMUCRU PLLs, both ARM clocks, DDRC, PMU roots, and protected critical clocks.
- CPUfreq on little and big clusters validates rate tables.
- Suspend/resume or low-power testing checks PMUCRU, 32 kHz, CM0S, timer, and PMU peripheral clocks.
- Memory stress validates DDRC clocking.
- Display tests across HDMI/DP/eDP/VOP0/VOP1 validate fractional display clocks.
- UART, I2S, SPDIF, SD/eMMC/SDIO, USB3, PCIe, GMAC, GPU, ISP, and codec workloads exercise the broad branch table.
- Reset-controller consumers and reboot validate the main and PMU soft-reset registrations plus restart notifier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3399.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3506.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3506.c

## Purpose

`clk-rk3506.c` provides the RK3506 CRU clock provider. It describes a modern Rockchip clock tree with GPLL, V0PLL, V1PLL, a multi-PLL ARM clock, matrix/fractional roots, audio/voice/ASRC clocks, storage/network/display/video/peripheral roots, PMU clocks, 32 kHz generation, reset initialization, restart handling, and a PVTPLL source initialization write.

The file supports both early OF initialization through `CLK_OF_DECLARE(rk3506_cru, "rockchip,rk3506-cru", rk3506_clk_init)` and built-in platform-driver probing through `clk_rk3506_driver`. The platform path simply calls the same init routine selected from match data.

## Important APIs, Types, And Functions

Important data:

- `PVTPLL_SRC_SEL_PVTPLL` is a hiword update value used after provider registration to select the PVTPLL source.
- `enum rk3506_plls` enumerates GPLL, V0PLL, and V1PLL.
- `rk3506_pll_rates` defines RK3328-style PLL rates.
- `rk3506_cpuclk_rates` defines ARM-clock parent rates and ACLK/PCLK divider writes.
- `rk3506_pll_clks` registers the three PLLs with `PLL(pll_rk3328, ...)`.
- `rk3506_armclk` is a branch-level ARMCLK mux over `"armclk_pll"` and `"clk_core_pvtpll"` with `CLK_IS_CRITICAL | CLK_SET_RATE_PARENT`.
- `rk3506_clk_branches` contains all branch descriptions.
- `rk3506_clk_init()` initializes the provider.
- `clk_rk3506_probe()` dispatches platform matches.

This driver uses `rockchip_clk_register_armclk_multi_pll` rather than the older single-PLL CPU clock registration. It also calls `rk3506_rst_init(np, reg_base)`, supplied by `rst-rk3506.c`, which registers a reset lookup table instead of a simple contiguous soft-reset block.

## Control Flow

`rk3506_clk_init()` performs:

1. Compute `clk_nr_clks` from the maximum ID in `rk3506_clk_branches`.
2. Map the CRU with `of_iomap`.
3. Allocate the Rockchip provider with `rockchip_clk_init`.
4. Register GPLL, V0PLL, and V1PLL.
5. Register the multi-PLL ARM clock with `rockchip_clk_register_armclk_multi_pll`.
6. Register all branch clocks.
7. Initialize resets through `rk3506_rst_init`.
8. Register restart at `RK3506_GLB_SRST_FST`.
9. Publish the provider.
10. Write `PVTPLL_SRC_SEL_PVTPLL` to `RK3506_CLKSEL_CON(15)` to select the PVTPLL source.

The platform probe obtains match data and calls this same init function. Error handling mirrors older CRU files for mapping and provider-allocation failures.

## State And Persistence Behavior

The driver stores no persistent state outside hardware registers and CCF objects. The final explicit `writel_relaxed` changes the core PVTPLL selection in CRU register state after CCF setup. Because this write is outside the declarative branch registration, it is an important side effect to preserve in refactors.

Several roots are `CLK_IS_CRITICAL`, including 24 MHz and PLL gates, core/bus roots, DDRC, high-speed and low-speed peripheral roots, PMU roots, 32 kHz clocks, CRU/PMU PCLKs, and IO-controller clocks. These clocks are expected to survive unused-clock cleanup.

## Dependencies And Integration Points

Dependencies:

- RK3506 dt-binding IDs from `include/dt-bindings/clock/rockchip,rk3506-cru.h`.
- Common Rockchip clock provider, PLL, branch, multi-PLL ARM clock, reset, and restart code.
- `rk3506_rst_init` from the matching reset driver.
- Device-tree parent clocks such as `xin24m`, external SAI MCLK/SCLK inputs, `dummy_vop_dclk`, and `clk_pll_ref_io`.

Integration surfaces:

- CPU clocking uses `armclk_pll`, `clk_core_pvtpll`, and the post-init PVTPLL source write.
- Matrix roots and fractional matrix clocks feed UART, voice, and common clock domains.
- Audio/voice includes SAI0-4, SPDIF TX/RX, PDM, ASRC MCLK/LRCK, DSM, audio ADC, and voice fractional matrices.
- Storage/network includes SDMMC, FSPI, dual MAC clocks, MAC PTP roots, USB OTG, USB PHY, and OTPC clocks.
- PMU/low-power includes 32 kHz muxing, RC clock, touch key, GPIO0, PMU HP timer, PMU CRU/GRF, PWM0, reference outputs, and PHY reference muxes.
- Display/video includes VOP, DSI host, DPHY, RGA, TSADC, and VIO roots.
- Resets are not a simple register count; reset IDs are mapped by `rst-rk3506.c`.

## Risks And Edge Cases

- The explicit PVTPLL source write can be missed because most of the file is declarative. Removing or moving it may leave ARM clock muxing on the wrong source.
- `rockchip_clk_register_armclk_multi_pll` expects a branch description and rate table rather than CPU reg-data. Incorrect conversion to the older API would lose multi-parent behavior.
- The clock tree uses many matrix and fractional intermediate clocks. Parent-name mismatches can break UART/audio/ASRC rate propagation.
- Critical roots are numerous and power-domain sensitive. Over-aggressive cleanup can break DDR, PMU, core, CRU, IO-controller, or bus access.
- Reset handling is delegated to a lookup-table reset driver; replacing it with `rockchip_register_softrst` would not preserve non-contiguous reset IDs.
- Board files must provide external audio and VOP dummy/real parents consistently with the parent names.

## Test Signals

Recommended signals:

- Boot on RK3506 with no CRU map/init errors and with the platform driver not double-registering clocks after early init.
- `clk_summary` shows GPLL/V0PLL/V1PLL, `armclk`, matrix roots, PMU/32 kHz roots, and critical roots.
- CPU rate transitions validate the multi-PLL ARM clock and PVTPLL selection.
- Audio tests across SAI, SPDIF, PDM, ASRC, DSM, and audio ADC validate fractional/matrix parents.
- SDMMC/FSPI, USB, GMAC0/1, MAC PTP, OTPC, DSI/VOP/RGA, and ADC workloads validate peripheral clocks.
- Reset-controller consumers validate `rk3506_rst_init`.
- Reboot validates restart notifier registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3506.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3528.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3528.c

## Purpose

`clk-rk3528.c` is the RK3528 CRU platform driver. It registers PLLs, ARM clocking, matrix roots, UART/audio fractional clocks, bus/PMU/DDR/GPU/video/display/storage/network/peripheral clocks, optional VO/VPU GRF-backed MMC phase clocks, reset lookup-table support, restart handling, and OF provider publication.

The file is platform-driver only: `builtin_platform_driver_probe(clk_rk3528_driver, clk_rk3528_probe)` binds `rockchip,rk3528-cru`. This path uses managed MMIO mapping and device-managed allocation for auxiliary GRF table entries.

## Important APIs, Types, And Functions

Key data:

- `RK3528_GRF_SOC_STATUS0` is passed to PLL registration, likely for PLL lock/status handling through system GRF.
- `enum rk3528_plls` indexes APLL, CPLL, GPLL, PPLL, and DPLL.
- `rk3528_pll_rates` defines PLL programming points.
- `rk3528_cpuclk_rates` and `rk3528_cpuclk_data` define ARM clock rates and divider/mux register fields.
- `rk3528_pll_clks` registers PLLs, with PPLL marked `ROCKCHIP_PLL_FIXED_MODE` and DPLL using DDRPHY mode registers.
- `rk3528_clk_branches` is the main clock branch table.
- `rk3528_vo_clk_branches` contains VO-GRF MMC phase clocks for SDMMC.
- `rk3528_vpu_clk_branches` contains VPU-GRF MMC phase clocks for SDIO0/SDIO1.
- `clk_rk3528_probe()` performs all initialization.

The file uses many Rockchip macros: `COMPOSITE_NOMUX_HALFDIV`, `COMPOSITE_FRACMUX`, `COMPOSITE_NODIV`, `MUX`, `DIV`, `GATE`, `FACTOR`, `FACTOR_GATE`, and `MMC_GRF`. It also directly manipulates `ctx->aux_grf_table` via `hash_add` for auxiliary GRF regmaps.

## Control Flow

`clk_rk3528_probe()`:

1. Maps CRU MMIO with `devm_platform_ioremap_resource`.
2. Computes the base clock table size from `rk3528_clk_branches`.
3. Looks up optional `rockchip,rk3528-vo-grf`. If present, it expands `nr_clks` to cover `rk3528_vo_clk_branches`; if absent with `-ENODEV`, it continues; other errors abort probe.
4. Looks up optional `rockchip,rk3528-vpu-grf` with the same behavior for VPU clocks.
5. Allocates the Rockchip provider.
6. Registers PLLs with `RK3528_GRF_SOC_STATUS0`.
7. Registers `ARMCLK` from APLL/GPLL parents.
8. Registers main CRU branches.
9. If VO GRF exists, allocates a `rockchip_aux_grf`, stores `grf_type_vo`, adds it to `ctx->aux_grf_table`, and registers VO MMC phase branches.
10. If VPU GRF exists, repeats the process with `grf_type_vpu` and VPU MMC phase branches.
11. Initializes reset support through `rk3528_rst_init`.
12. Registers restart at `RK3528_GLB_SRST_FST`.
13. Publishes the OF clock provider.

All major failures return through `dev_err_probe`, making deferred-probe or error diagnosis visible to the device model.

## State And Persistence Behavior

Runtime state is in CRU/GRF registers, optional auxiliary GRF regmaps, the provider lookup table, and CCF objects. Optional VO/VPU GRF state affects only MMC phase clocks backed by those GRF regions; the main provider still registers when these optional GRFs are absent.

The driver marks many matrix, bus, PMU, DDR, GPU, VPU, VO, CRU, GRF, IOC, and PCLK roots as `CLK_IS_CRITICAL` or `CLK_IGNORE_UNUSED`. PPLL is fixed-mode, DPLL is associated with DDRPHY mode control, and DDR-related gates are critical.

## Dependencies And Integration Points

Dependencies:

- RK3528 dt-binding IDs from `include/dt-bindings/clock/rockchip,rk3528-cru.h`.
- Common Rockchip clock, PLL, CPU clock, auxiliary GRF, reset, and restart support.
- `rk3528_rst_init` from `rst-rk3528.c`.
- Syscon regmaps for optional `rockchip,rk3528-vo-grf` and `rockchip,rk3528-vpu-grf`.
- Device-tree parent clocks such as `xin24m`, `gmac0`, and PLL-derived parents.

Integration surfaces:

- CPUfreq uses `ARMCLK` over APLL/GPLL with ACLK_M_CORE and PCLK_DBG divider programming.
- DDR uses DPLL, DDRPHY mode registers, critical DDR controller/PHY/upctl/scramble/split clocks, and DDR monitor clocks.
- Matrix roots derive standard 50/100/150/200/250/300/339/400/500/600 MHz clocks for broad SoC consumers.
- UART0-7 use fractional muxes. I2S0-3/SAI and SPDIF use fractional muxes and MCLK gates.
- PMU domain includes MCU, PMU SRAM, I2C2, PMU HP timer, PMU IOC/CRU/GRF, watchdog, GPIO0, oscillator checker, mailbox, SCR key generator, PVTM, refout, 32 kHz, and DDR fail-safe clock.
- Media/peripheral domains include GPU, RKVDEC, RKVENC, VOP, VO, VPU, JPEG, VDPP, RGA2E, HDCP, HDMI/CVBS, USB host/OTG, PCIe, eMMC, SDMMC0, SDIO0/1, SFC, GMAC0/1, CAN, SPI, I2C, PDM, ACODEC, ADCs, TSADC, and GPIO debounce.
- MMC phase clocks for SDMMC/SDIO are split into optional VO/VPU GRF-backed branch arrays rather than the main CRU table.

## Risks And Edge Cases

- Optional VO/VPU GRFs are deliberately tolerated when absent only for `-ENODEV`. Other syscon errors abort probe. Board DTS errors can therefore remove MMC phase clocks or fail the entire clock provider depending on error type.
- `nr_clks` must include optional branch IDs before provider allocation. Forgetting to expand it would cause lookup-table overflows or missing phase clocks.
- Auxiliary GRF entries must use the correct `grf_type_vo`/`grf_type_vpu`; otherwise `MMC_GRF` branches write to the wrong regmap or fail to register.
- PPLL fixed mode and DPLL DDRPHY mode are hardware-specific. Treating them as normal PLLs can destabilize PCIe/network or DDR.
- Many clocks are marked critical because disabling them can break register access, memory, or power-management infrastructure. Cleanup changes require hardware testing.
- Duplicate clock names such as domain-local `clk_tsadc`/`clk_saradc` style entries should be reviewed with dt-binding consumers to avoid lookup confusion.

## Test Signals

Useful validation:

- Probe succeeds with and without optional VO/VPU GRF nodes; only non-`ENODEV` lookup failures should abort.
- `clk_summary` shows APLL/CPLL/GPLL/PPLL/DPLL, ARMCLK, matrix roots, DDR roots, PMU roots, and optional MMC phase clocks when GRFs exist.
- CPU rate changes validate `rk3528_cpuclk_rates`.
- DDR stress validates DPLL/DDR critical clocks.
- UART0-7 baud tests validate fractional muxes.
- I2S/SAI/SPDIF audio validates fractional audio clocks.
- SDMMC0/SDIO0/SDIO1 tuning validates VO/VPU `MMC_GRF` phase clocks.
- Display/video/GPU/VPU/RKVDEC/RKVENC/HDMI/CVBS/USB/PCIe/GMAC workloads exercise domain roots.
- Reset consumers validate `rk3528_rst_init`; reboot validates restart notifier registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3528.c -->
