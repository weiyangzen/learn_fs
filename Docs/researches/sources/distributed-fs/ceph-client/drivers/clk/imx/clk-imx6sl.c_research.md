# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx6sl.c

## Purpose
`clk-imx6sl.c` provides the i.MX6 SoloLite clock tree. It registers ANATOP PLLs, PFDs, CCM muxes/dividers/gates, and display/e-paper/audio/peripheral roots for the `fsl,imx6sl-ccm` compatible. In addition to normal CCF provider setup, it exports `imx6sl_set_wait_clk()` to implement the ERR005311 low-power WAIT-mode workaround by temporarily reducing the ARM/IPG ratio.

## Important APIs, Types, And Functions
The clock provider uses `static struct clk_hw **hws`, `static struct clk_hw_onecell_data *clk_hw_data`, plus global `ccm_base` and `anatop_base` used by the WAIT workaround. `imx6sl_get_arm_divider_for_wait()` inspects the current PLL1 switch and ARM PLL divider to choose a safe CACRR divider. `imx6sl_enable_pll_arm()` temporarily powers/enables PLL1 and restores the saved register value. `imx6sl_set_wait_clk(bool enter)` saves the current ARM divider, writes a low-frequency WAIT divider on entry, restores it on exit, and waits for `CDHIPR` busy clearance.

`imx6sl_clocks_init()` registers fixed inputs, ANATOP PLL bypasses and gates, PFDs, fixed factors, CCM muxes, busy muxes/dividers, peripheral dividers, shared gates for SSI/SPDIF, and CCGR gates for CSI, LCDIF, EPDC, PXP, GPU2D, SDMA, UART, USDHC, and related blocks.

## Control Flow
The OF clock declaration maps ANATOP first, creates PLL/bypass/PFD/video/audio/enet reference clocks, then maps the CCM node and stores `ccm_base`. It registers roots and peripheral selectors, then creates busy muxes and busy dividers for bus domains where hardware reports handshake status. CCGR gates are created last. The driver masks MMDC CH0 handshaking, validates all `IMX6SL_CLK_END` entries, publishes the onecell provider, sets AHB to 132 MHz, optionally enables USB PHY dummy gates, assigns SPDIF0 to PLL3 PFD3, chooses PLL5 video for LCDIF pixel, chooses PLL2 PFD2 for LCDIF AXI, and registers UART clocks.

## State And Persistence
Provider state is the allocated `clk_hw_data` and `hws` table. WAIT-mode state is static local saved values in `imx6sl_enable_pll_arm()` and `imx6sl_set_wait_clk()`, backed by live PLL_ARM/CACRR register writes. Clock configuration is maintained in hardware registers; there is no disk persistence. Shared gate refcounts coordinate logical SSI/SPDIF clock users that map to the same CCGR bits.

## Dependencies And Integration Points
The file depends on Linux CCF `clk_hw` constructors, `dt-bindings/clock/imx6sl-clock.h`, i.MX helper APIs including `imx_clk_hw_fixup_mux()`, `imx_clk_hw_busy_mux()`, `imx_clk_hw_busy_divider()`, and `imx_mmdc_mask_handshake()`, and optional `CONFIG_USB_MXS_PHY`. Consumers include LCDIF, EPDC, PXP, CSI, GPU2D, USDHC, ECSPI, UART, SSI/SPDIF, GPT/EPIT, I2C, and memory-controller clocks.

## Risks
The WAIT workaround runs in idle-sensitive context and uses raw polling instead of sleepable clock APIs, so register choices and saved-state handling must be exact. If `anatop_base` or `ccm_base` is unavailable, later WAIT calls would be unsafe. Busy divider/mux bit positions must match the reference manual to avoid changing active bus rates while hardware is busy. Fixup mux/divider use implies shared register fields where naive writes could disturb adjacent selectors.

## Test Signals
Boot should provide all `IMX6SL_CLK_*` IDs without `imx_check_clk_hws()` warnings. Runtime validation includes successful suspend/idle WAIT transitions without cache corruption symptoms, AHB at 132 MHz, LCDIF pixel output from PLL5 video, EPDC/LCDIF/PXP operation, USB PHY enablement when configured, and consistent SSI/SPDIF shared gate behavior under audio playback/recording.
