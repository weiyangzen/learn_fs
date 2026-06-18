# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rv1108.c

## Purpose

`clk-rv1108.c` is the Rockchip CRU driver for RV1108. It publishes PLLs, the ARM clock, clock branches, critical-clock protection, soft resets, restart support, and MMC phase clocks to Linux. The clock tree covers a compact multimedia SoC with CPU/core, bus, PMU wrapper, DDR, peripheral, video input/output, video encode/decode, DSP, audio, storage, USB, GMAC, crypto, ADCs, PWM/I2C/SPI/UART, and camera interface clocks.

The file is structured as one OF-declared init routine plus static data tables. Consumers use IDs from `dt-bindings/clock/rv1108-cru.h`; the hardware programming is handled by generic Rockchip CCF helpers.

## Important APIs, Types, And Data

- `enum rv1108_plls` declares APLL, DPLL, and GPLL. `rv1108_pll_clks[]` registers them as `pll_rk3399` PLLs with per-PLL control/mode offsets and lock status at `RV1108_GRF_SOC_STATUS0`. DPLL is registered with a null rate table, reflecting a more fixed or firmware/DDR-owned role.
- `rv1108_pll_rates[]` is a broad RK3036-style rate table from 1.608 GHz to 96 MHz, used by APLL and GPLL.
- `rv1108_cpuclk_rates[]` maps CPU parent rates to core/peripheral dividers, while `rv1108_cpuclk_data` describes the single-core ARM mux/divider fields.
- Parent arrays model PLL variants for core and DDR, USB480M and HDMI PHY inputs, video/display pixel parents, VIO/VIP external clocks, I2S fractional/external parents, GMAC external reference selection, CVBS/HDMI/DSI/CIF sources, DSP parents, MMC parents, and common peripheral roots.
- Fractional mux branches exist for UART0-2 and I2S0-2. They select integer source, fractional source, external IO source where supported, or 12/24 MHz fallback.
- `rv1108_clk_branches[]` describes the full clock tree with Rockchip macros. It includes gate-only PLL domain outputs, core/debug clocks, RKVENC/RKVDEC/VPU roots, PMU clocks, WiFi/CIF/MIPI clocks, DSP clocks, VIO/VOP/HDMI/DSI/CVBS/RGA/ISP clocks, I2S/audio clocks, bus/peripheral roots, UART/SPI/I2C/PWM/timer/watchdog/GPIO/ADC/crypto/DMAC clocks, DDR clocks, SDMMC/SDIO/eMMC/NAND/SFC clocks, USB, GMAC, and MMC drive/sample phase controls.
- `rv1108_critical_clocks[]` names fabric, DDR, PMU, and PHY clocks that are protected after branch registration.
- `MFLAGS`, `DFLAGS`, `GFLAGS`, and `IFLAGS` request hiword-mask writes for muxes, dividers, gates, and inverter controls.

## Control Flow

`CLK_OF_DECLARE(rv1108_cru, "rockchip,rv1108-cru", rv1108_clk_init)` registers the init hook. `rv1108_clk_init()` maps the CRU register range with `of_iomap()`, creates a provider sized to `CLK_NR_CLKS`, registers PLL descriptors, registers all branch descriptors, protects critical clocks by name, registers the ARM clock with `rockchip_clk_register_armclk()`, registers 13 banks of soft resets starting at `RV1108_SOFTRST_CON(0)`, registers the restart notifier at `RV1108_GLB_SRST_FST`, and adds the OF provider.

After init, all operational paths run through the CCF. PLL operations change APLL/GPLL rates, CPU clock operations perform safe mux/divider transitions, composite clocks program mux/divider/gate fields, fractional muxes handle precise audio/serial rates, MMC clocks program sampling/drive phases, reset consumers use the registered soft reset controller, and restart uses the Rockchip notifier.

## State And Persistence Behavior

The driver has no dynamic private state. Persistent state for the booted kernel lives in CCF registrations and reset-controller registration; mutable hardware state lives in CRU registers. This includes PLL mode/config/status, clock-select mux and divider registers, fractional divider registers, gate registers, inverter fields for VIP input, MMC phase registers, soft reset registers, and the global soft reset register used for restart.

Important state choices include:

- Many core, bus, DDR, PMU, and NIU clocks are `CLK_IGNORE_UNUSED`, reflecting clocks needed by firmware, debug, memory, or interconnect paths even without explicit consumers.
- Critical-clock protection by name is applied after branch registration, adding an additional guard around fabric and DDR paths.
- Read-only dividers are used for CPU/debug-derived clocks and DDR-derived paths where the driver should expose the rate without reprogramming the divider.
- DPLL has no rate table in this driver, so consumers should not expect normal dynamic DPLL rate changes through this file.

## Dependencies And Integration Points

The file depends on Linux OF/IO mapping, CCF provider APIs, Rockchip clock and reset helpers, and `dt-bindings/clock/rv1108-cru.h`. Device tree must provide `rockchip,rv1108-cru` plus external parent clocks named in the parent arrays, including USB PHY, HDMI PHY, external GMAC, external I2S, VIP/CIF/HDMI/CVBS inputs, and oscillator inputs.

Consumer integration includes CPUfreq, UART0-2, I2C1-3 plus PMU I2C0, SPI, PWM, timers, watchdogs, GPIO, TSADC/SARADC, crypto, DMAC, DDR controller/monitor, PMU wrapper, USB host/OTG/PHY, SDMMC/SDIO/eMMC/NAND/SFC, GMAC, I2S audio, VOP/HDMI/DSI/CVBS display, CIF/MIPI/ISP camera paths, RGA/IEP, RKVENC/RKVDEC/VPU media engines, DSP, reset consumers, and restart.

## Risks And Edge Cases

- Several clocks have ID `0` because they are internal-only. Accidentally assigning public IDs or changing names can alter provider ABI or debugfs expectations.
- DPLL is likely DDR-sensitive. Adding a rate table or allowing ordinary consumers to retune it could destabilize memory.
- External parents (`usbphy`, `hdmiphy`, `ext_gmac`, `ext_i2s`, `ext_vip`, CIF/HDMI/CVBS inputs) must exist and match DT naming; missing parents can break media, Ethernet, or display.
- The file contains hardware-specific muxes and even an inverter for `pclk_vip`; incorrect polarity or mux values can produce hard-to-debug capture/display failures.
- Several critical paths are protected by both `CLK_IGNORE_UNUSED` and `rv1108_critical_clocks[]`. Removing either can cause late boot failures when unused clocks are disabled.
- MMC drive/sample phase clocks must match the controller tuning registers. Wrong phase register offsets can cause intermittent SD/eMMC data corruption.

## Test Signals

Good test signals include clean boot with `rockchip,rv1108-cru`, no missing parent messages, visible APLL/GPLL/ARM/bus/peripheral clocks in clk summary, and registered reset lines. Functional validation should cover CPU rate changes, serial baud rates, I2S fractional audio, SDMMC/SDIO/eMMC tuning and data transfer, NAND/SFC access, USB, GMAC, display through VOP/HDMI/DSI/CVBS, camera CIF/MIPI/ISP capture, video encode/decode, DSP clocks if used, crypto, ADCs, timers/watchdogs, suspend/resume, soft reset toggles, and restart.
