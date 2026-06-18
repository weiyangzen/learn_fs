# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8qxp.c

## Purpose
Registers SCU-managed clocks for i.MX8QXP-family SoCs, including i.MX8DXL and i.MX8QM variants. It describes resource/clock-type pairs and SCU GPR helper clocks for CPU, LSIO, DMA, audio, connectivity, display, MIPI/LVDS, CSI, parallel interface, GPU, M4, HDMI TX, and HDMI RX domains.

## Important APIs, Types, And Functions
`imx8qxp_clk_probe()` calls `imx_clk_scu_init()` with match-data resource tables, then creates clocks with `imx_clk_scu()`, `imx_clk_scu2()`, `imx_clk_divider_gpr_scu()`, `imx_clk_mux_gpr_scu()`, and `imx_clk_gate_gpr_scu()`. `clk_on_imx8dxl()` gates registration of ENET RX clocks unavailable on DXL. Module init registers the platform driver and the underlying `imx-scu-clk` driver through `imx_clk_scu_module_init()`.

## Control Flow
Probe initializes the SCU IPC-backed clock subsystem, then registers clock declarations in subsystem order. Each `imx_clk_scu*()` call allocates a platform device that later binds to the SCU clock driver. At the end, `of_clk_add_hw_provider()` publishes `imx_scu_of_clk_src_get` over `imx_scu_clks`. If provider registration fails, `imx_clk_scu_unregister()` cleans registered clocks.

## State And Persistence Behavior
Clock state mostly lives in SCFW, not Linux MMIO. Linux keeps lists of registered `clk_hw` objects by resource ID. The module registers two platform drivers and suppresses bind attributes to avoid unsafe clock removal.

## Dependencies And Integration Points
Depends on SCU firmware IPC, `clk-scu.c`, resource allowlists, `dt-bindings/firmware/imx/rsrc.h`, and DT compatibles `fsl,scu-clk`, `fsl,imx8dxl-clk`, `fsl,imx8qxp-clk`, and `fsl,imx8qm-clk`.

## Risks
Because registration is mostly a sequence of side-effecting SCU clock allocations, missing ownership or resource-table entries silently skip clocks. Parent selector arrays with dummy slots must match SCFW parent indexes. CPU clocks use ATF-mediated rate setting, while other SCU clocks use SCFW PM RPCs.

## Test Signals
Boot each compatible variant, inspect `clk_summary`, run CPU frequency changes, validate UART/I2C/SPI/CAN/USDHC/ENET/display/MIPI/LVDS/HDMI/GPU consumers, and test SCFW resource partitioning where unowned resources are absent rather than fatal.
