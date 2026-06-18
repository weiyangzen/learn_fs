# sources/distributed-fs/ceph-client/drivers/clk/rockchip/rst-rk3576.c

Purpose: RK3576 reset-controller LUT for a large SoC with main, PHP, secure-nonsecure, and PMU1 CRU reset islands.

Important APIs/types/functions: `RK3576_CRU_RESET_OFFSET()`, `RK3576_PHPCRU_RESET_OFFSET()`, `RK3576_SECURENSCRU_RESET_OFFSET()`, and `RK3576_PMU1CRU_RESET_OFFSET()` encode reset IDs. `rk3576_register_offset[]` maps many domains: top/bus, audio, I2C/UART/SPI/PWM/timers, DDR channels, NPU/RKNN, storage/PHP/PCIe/SATA, SDGMAC, RKVDEC/VEPU/VPU, VI/CSI, VOP/display, VO0/VO1, GPU, center, PHY, secure, and PMU blocks.

Control flow: `rk3576_rst_init()` registers the LUT against `reg_base + RK3576_SOFTRST_CON(0)` with high-word mask reset semantics. The common `softrst.c` controller handles assert/deassert for all IDs by using the encoded bank/bit values.

State and persistence: reset state persists in CRU registers; the C file contributes only static mapping data after init.

Dependencies and integration: RK3576 reset dt-bindings, CRU offsets from `clk.h`, common reset-controller implementation, and device-tree reset users in complex subsystems such as PCIe/SATA/UFS/display/USB/DDR.

Risks: very broad hardware coverage makes off-by-one register indexes dangerous. PMU1 and secure-nonsecure offset encoding must align with the CRU MMIO mapping. Some high-speed PHY/display resets require sequencing with PHY, power-domain, and clock drivers.

Test signals: probe reset consumers across all domains, run suspend/resume and peripheral reset cycles, verify no unintended adjacent reset bits through register tracing, and compare LUT against RK3576 TRM and binding header.
