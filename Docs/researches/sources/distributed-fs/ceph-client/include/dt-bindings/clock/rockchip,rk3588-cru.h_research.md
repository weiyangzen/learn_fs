# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rk3588-cru.h

## Purpose
`rockchip,rk3588-cru.h` defines the clock binding ABI for RK3588/RK3588S-class CRU consumers. It is one of the larger Rockchip clock headers, reflecting multiple CPU clusters, display/video islands, storage/network PHYs, and secure/SCMI clocks.

## Important APIs, types, and functions
The file exports PLL IDs (`PLL_B0PLL`, `PLL_B1PLL`, `PLL_LPLL`, `PLL_V0PLL`, `PLL_AUPLL`, `PLL_CPLL`, `PLL_GPLL`, `PLL_NPLL`, `PLL_PPLL`), CPU cluster clocks (`ARMCLK_L`, `ARMCLK_B01`, `ARMCLK_B23`), and hundreds of `CLK_*`, `ACLK_*`, `HCLK_*`, `PCLK_*`, `MCLK_*`, `SCLK_*`, `DCLK_*`, `TCLK_*`, and `DBCLK_*` constants. `SCMI_*` IDs cover secure/non-secure HCLK/PCLK, key ladder, crypto, SPLL, and SD host clocks.

## Control flow
Compile-time inclusion is the only header behavior. Runtime clock operations flow through the RK3588 CRU driver or SCMI firmware depending on the ID and DT provider. Reset and power-domain sequencing in consumers relies on these clock IDs being paired with matching domain descriptions elsewhere.

## State and persistence
The header has no state, but it is ABI. Real state is in CRU registers, firmware-managed secure clocks, and possibly retention domains across suspend.

## Dependencies and integration points
It is used by RK3588 DTS files, clock drivers, SCMI providers/clients, and drivers for CPU clusters, GPU/NPU, VOP and HDMI/DP, AV1/VPU/RKVDEC/RKVENC, ISP, PCIe/SATA/USB/pipe PHY, GMAC, SD/eMMC/SDIO, I2S/PDM/SPDIF, CAN, UART, SPI, I2C, PWM, watchdogs, and secure crypto/key ladder blocks.

## Risks and test signals
Risks include wrong ID selection between similar media islands, SCMI security policy mismatches, and breaking precompiled DTBs by renumbering. Test signals include `dtbs_check`, successful CRU and SCMI clock registration, no `-ENOENT` clock probe failures, display/video pipeline bring-up, PCIe/USB/storage/network operation, and suspend/resume clock retention checks.
