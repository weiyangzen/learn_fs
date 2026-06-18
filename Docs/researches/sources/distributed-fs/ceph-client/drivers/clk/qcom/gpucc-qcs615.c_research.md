# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-qcs615.c

## Purpose

This QCS615 GPUCC driver provides two default alpha PLLs, CRC fixed-factor derivatives, GMU/GX graphics RCGs, CX/GX/CRC/SMMU/sleep branches, resets, and CX/GX GDSCs for the GPU subsystem.

## Important APIs, types, and functions

The file centers on `gpu_cc_pll0`, `gpu_cc_pll1`, `crc_div_pll0`, `crc_div_pll1`, `gpu_cc_gmu_clk_src`, `gpu_cc_gx_gfx3d_clk_src`, `gpu_cc_qcs615_clocks`, `gpu_cc_qcs615_resets`, `cx_gdsc`, `gx_gdsc`, `gpu_cc_qcs615_driver_data`, and `gpu_cc_qcs615_desc`. `qcom_cc_probe()` handles registration and driver-data applies PLL and critical CBCR setup.

## Control flow, state, and persistence

The compatible is `"qcom,qcs615-gpucc"`. Registration maps registers, configures PLL0/PLL1 through the generic qcom driver-data path, performs driver-data register updates for GMU and GX graphics clock control, registers clocks/resets/GDSCs, and publishes providers. All live state is MMIO clock/power state and kernel registrations.

## Dependencies and integration points

Dependencies are Qualcomm alpha PLL/RCG/branch/regmap helpers, `gdsc`, `reset`, and `dt-bindings/clock/qcom,qcs615-gpucc.h`. It integrates with GPU/GMU, SNOC DVM, SMMU, CRC, and power-domain consumers.

## Risks and test signals

Risks include default PLL parameter mistakes, shared RCG parent-enable semantics, voted halt checks, and POLL_CFG_GDSCR sequencing. The driver-data register writes are hard-coded hardware programming and should be validated on silicon. Test GPU probe, GMU firmware boot, graphics frequency changes, reset controls, and CX/GX domain collapse.
