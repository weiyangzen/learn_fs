# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx6sx.c

## Purpose
`clk-imx6sx.c` registers the i.MX6 SoloX clock provider. It models a broad mixed application/MCU SoC topology: PLLs/PFDs, AXI/AHB/MMDC/OCRAM buses, display/LDB/LCDIF clocks, GPU clocks, M4 core clocking, PCIe, dual ENET references, QSPI, GPMI, audio, CAN/CANFD, and standard peripheral gates. It publishes `IMX6SX_CLK_*` IDs through a `clk_hw` onecell provider.

## Important APIs, Types, And Functions
The central function is `imx6sx_clocks_init()`, backed by `hws` and `clk_hw_data`. Static parent arrays encode mux input order for all major clock roots. Shared counter variables coordinate ASRC, ESAI, audio/SPDIF, SSI1/2/3, and SAI1/2 gates. The driver uses i.MX constructors for PLLv3, PFD, fixed-factor, mux, divider, busy mux/divider, gate2, shared gate2, and exclusive LVDS gates. It also uses `of_find_node_by_path()` to inspect whether LCDIF1 has assigned clock parents before applying a default display parent policy.

## Control Flow
The init path obtains fixed clocks and external display inputs, maps `fsl,imx6sx-anatop`, creates PLL bypass sources, PLLs, bypass muxes, PLL gates, USB PHY dummy gates, PCIe/ENET reference roots, LVDS exclusive gates, PFDs, fixed factors, and audio/video post dividers. It then maps CCM, registers a large set of muxes for bus, GPU, LDB, QSPI, ENET, M4, display, CSI, CLKO, and peripheral roots, followed by dividers and busy bus dividers. CCGR gate registration covers critical bus fabric, security, DMA, CAN, display, M4, ENET, QSPI, GPMI, ROM, audio, SAI, UART, USDHC, PWM, I2C, and USB blocks. Final policy masks MMDC handshakes, publishes the provider, enables USB PHY gates when configured, sets EIM, LCDIF1 defaults, PCIe LVDS parent, ENET rates, audio rates, VADC/CAN/GPU/QSPI parents, and UART aliases.

## State And Persistence
State is the `clk_hw` table, shared gate refcounts, OF node lookup result for LCDIF policy, and live hardware register contents. No disk persistence exists. Initial clock rates and parent choices persist as hardware state for the running system and are later mutable through normal CCF calls and assigned-clock processing.

## Dependencies And Integration Points
The file depends on `dt-bindings/clock/imx6sx-clock.h`, CCF, OF address lookup, `CONFIG_USB_MXS_PHY`, `imx_mmdc_mask_handshake()`, and board DT properties for external inputs and assigned display clocks. Consumers include Linux drivers for Cortex-M4 integration, PCIe, ENET/ENET2/PTP, LCDIF1/2, LDB, GPU, QSPI, GPMI NAND, ESAI/SSI/SAI/SPDIF, CANFD, USDHC, UART, ECSPI, I2C, PWM, and timers.

## Risks
This driver has many mux parent lists where ID order must exactly match hardware encoding. The LCDIF1 default policy depends on a hard-coded DT path, so alternative DT layouts may skip or misapply defaults. PCIe reference setup assumes LVDS1 and logs only on parent failure. Shared-gate groupings must match CCGR bit sharing. Rate changes for ENET, audio, GPU, and QSPI can affect board-specific constraints if assigned clocks are absent or incomplete.

## Test Signals
Good signals include no `imx_check_clk_hws()` warnings, ENET and ENET2 reference clocks at 125 MHz, ENET AHB at 200 MHz, EIM at 132 MHz, audio roots at 393.216 MHz/98.304 MHz/24.576 MHz where configured, working LCDIF1 fallback when DT lacks assigned parents, PCIe reference availability, M4 clock visibility, QSPI boot/storage operation, and GPU parent updates reflected in `clk_summary`.
