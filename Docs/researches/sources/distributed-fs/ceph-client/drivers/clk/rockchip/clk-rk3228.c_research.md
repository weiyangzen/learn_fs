# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3228.c

## Purpose
`clk-rk3228.c` is the CRU clock driver for RK3228. It models PLLs, CPU clock rates, bus dividers, peripheral and media clocks, HDMI PHY and USB480M clock inputs, GMAC/MACPHY clock paths, MMC phase controls, and a broad set of critical interconnect clocks. The SoC surface includes CPU, DDR, video encode/decode, VIO/VOP/RGA/IEP/HDCP, peripherals, UART/audio, GMAC/MACPHY, NAND/SFC/MMC, USB hosts/OTG, GPU, init memory, ROM, DDR monitor, analog codec PHY, and timers.

## Important APIs, Types, And Functions
Key data includes `rk3228_pll_rates`, `rk3228_cpuclk_rates`, `rk3228_cpuclk_data`, `rk3228_pll_clks`, `rk3228_clk_branches`, and fractional mux descriptors for I2S0/1/2, SPDIF, and UART0-2. Parent arrays encode APLL/GPLL/DPLL ARM choices, DPLL/GPLL/APLL DDR choices, CPLL/GPLL/HDMIPHY/USB480M source muxes, HDMI CEC, VOP DCLK selection, external GMAC and MACPHY paths, and audio/UART fractional alternatives. `rk3228_clk_init()` is the only init function and is declared for `rockchip,rk3228-cru`.

## Control Flow
The init hook maps the CRU, sizes the provider from the max branch ID, initializes the Rockchip clock provider, registers RK3036-type PLLs using `RK3228_GRF_SOC_STATUS0`, registers all branch clocks, protects the critical clock list, registers the ARM clock with the RK3228 CPU clock data/rates, registers 9 soft-reset registers, installs the restart notifier using `RK3228_GLB_SRST_FST`, and adds the provider. On mapping or provider initialization failure it logs an error and returns, unmapping only after provider-init failure.

## State And Persistence Behavior
No separate suspend/resume storage is implemented. Clock state lives in CRU registers and CCF structures. The critical list is unusually long and protects CPU/peripheral buses, RGA/IEP/VOP/HDCP/VIO NOCs, USB host arbiters, OTG PMU, GPU NOC, init memory/ROM, DDR controller/monitor/MSCH/PHY paths, analog codec PHY, and VPU/RKVDEC NOCs. This indicates heavy reliance on always-on interconnect clocks and careful unused-clock cleanup behavior. Hiword-mask flags are used for mux/divider/gate writes.

## Dependencies And Integration Points
The driver depends on `dt-bindings/clock/rk3228-cru.h`, Rockchip CCF helpers, OF mapping, reset helpers, and restart notifier support. Consumers include CPUfreq, video/display engines, HDMI/HDCP, VPU/RKVDEC, GPU, audio I2S/SPDIF, UART0-2, MMC/SDIO/eMMC with drive/sample phase clocks, SFC/NAND, USB host/OTG, GMAC and integrated MACPHY paths, analog codec PHY, timers, GPIO/I2C/PWM/SPI/WDT/SARADC, DDR monitor/control blocks, and reset-controller users.

## Risks
The main risks are parent encoding and critical-clock coverage. RK3228 can source several domains from HDMIPHY or USB480M, so mux ordering and `CLK_SET_RATE_PARENT` choices affect display, network, and peripheral stability. GMAC has both external-clock and MACPHY paths; selecting or gating the wrong branch can break Ethernet on only some board designs. The large critical list should not be casually pruned because many protected clocks are NOC/arbitration clocks that may not have direct leaf consumers. MMC phase register mistakes show up as storage tuning or high-speed-mode failures.

## Test Signals
Use `clk_summary` to verify HDMIPHY, USB480M, GMAC/MACPHY, VOP, and DDR/NOC clock parents. Exercise CPUfreq, HDMI/VOP modes, RGA/IEP/HDCP users where available, VPU/RKVDEC decode, GPU, I2S/SPDIF fractional audio, UART0-2, all MMC interfaces with tuning, SFC/NAND, USB host/OTG, GMAC link with internal and external reference configurations, reset controller consumers, late unused-clock cleanup, and restart through the RK3228 global soft reset path.
