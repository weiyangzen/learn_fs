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
