# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-qcs615.c

## Purpose
This driver registers QCS615 VIDEOCC for Venus/vcodec hardware, including one video PLL, sleep/Venus RCGs, branch clocks, resets, and two GDSCs.

## Important APIs, types, and functions
- `video_pll0` is an alpha PLL configured for a 600 MHz VCO setting.
- RCGs generate sleep and Venus clock sources.
- Branches expose sleep, vcodec0 AXI/core, Venus AHB, Venus CTL AXI/core.
- `vcodec0_gdsc` and `venus_gdsc` provide power domains.
- `video_cc_qcs615_resets[]` maps interface, vcodec0, and Venus resets.
- Driver data lists PLL0 and critical XO CBCR 0xab8.

## Control flow
The platform driver matches `"qcom,qcs615-videocc"` and calls `qcom_cc_probe()`. Common code maps registers, configures PLL0, keeps the critical XO clock enabled, and registers clocks, resets, and GDSCs for video consumers.

## State and persistence behavior
State is hardware-backed in VIDEOCC registers. The driver does not maintain dynamic state. GDSC power state persists in hardware and is managed by genpd via qcom GDSC callbacks.

## Dependencies and integration points
It uses qcom alpha PLL, PLL, branch, RCG, divider/mux headers, common CC, GDSC, reset, regmap, and `dt-bindings/clock/qcom,qcs615-videocc.h`. It integrates with Venus/vcodec drivers.

## Risks
PLL config and frequency tables must match supported video rates. Critical XO enable is required for stable access but affects power. Reset offsets are small and close together; binding/order mistakes can affect recovery operations.

## Test signals
Test Venus decode/encode, vcodec domain power toggles, clock-rate selection for Venus, reset assertion/deassertion, and debugfs visibility of PLL0 plus branch clocks. Probe should produce no qcom CC registration errors.
