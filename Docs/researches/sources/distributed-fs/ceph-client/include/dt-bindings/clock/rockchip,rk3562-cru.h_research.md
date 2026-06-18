# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rk3562-cru.h

## Purpose
`rockchip,rk3562-cru.h` defines RK3562 clock IDs for device-tree consumers of the CRU. It covers PLLs, CPU/GPU/NPU/DDR roots, bus gates, media/display clocks, and secure crypto clocks.

## Important APIs, types, and functions
The header exports `PLL_DMPLL0`, `PLL_APLL`, `PLL_GPLL`, `PLL_VPLL`, `PLL_HPLL`, `PLL_CPLL`, `PLL_DPLL`, `PLL_DMPLL1`, followed by `ARMCLK`, `CLK_GPU`, `ACLK_RKNN`, `CLK_DDR`, and peripheral families `CLK_*`, `ACLK_*`, `HCLK_*`, `PCLK_*`, `SCLK_*`, `DCLK_*`, `MCLK_*`, `CCLK_*`, `FCLK_*`, and `TMCLK_*`. The tail includes display and secure crypto IDs such as `DCLK_VOP`, `DCLK_VOP1`, `ACLK_CRYPTO_S`, and `CLK_PKA_CRYPTO_S`.

## Control flow
The only control path is inclusion into DTS or C driver code. Runtime requests travel from DT clock specifiers to the RK3562 CRU provider, which maps IDs to hardware gates, muxes, and dividers.

## State and persistence
The file is stateless. Numeric assignments are persistent ABI; CRU hardware contains the real state. Secure clock IDs may be subject to firmware or trust-zone policy outside the header.

## Dependencies and integration points
It integrates with RK3562 board descriptions, Rockchip CRU clock tables, power domains, and drivers for RKNN, GPU, DDR, crypto, VOP, CSI/DSI PHYs, audio, UART/I2C/SPI/CAN, SD/eMMC, USB, GMAC, and timers.

## Risks and test signals
Risks include mixing RK3562 IDs with RK3568 IDs, misdescribing secure crypto clocks, and assigning display or PHY clocks to the wrong consumer. Test signals include `dtbs_check`, clk-summary inspection, boot with console and storage, GPU/RKNN/display probe logs, CSI/DSI PHY initialization, and crypto self-tests when secure clocks are available.
