# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-kaanapali.c

## Purpose
This driver registers Kaanapali VIDEOCC, including four video PLLs, MVS0/MVS0A/MVS0B/MVS0C/VPP clocks, GDSCs, and resets.

## Important APIs, types, and functions
- `video_cc_pll0` through `video_cc_pll3` are Taycan EKO T PLLs configured for 360/480 MHz-class sources.
- RCGs generate AHB and MVS0/MVS0A/MVS0B/MVS0C rates; branches expose core, freerun, shift, and VPP clocks.
- `clk_mem_branch video_cc_mvs0_freerun_clk` indicates a memory-retention style branch for one freerun path.
- Five GDSCs cover MVS0A, MVS0, VPP1, VPP0, and MVS0C.
- `clk_kaanapali_regs_configure()` enables clk_on sync and sets `ACCU_CFG_MASK` on several GDSC CFG3 registers.
- Driver data lists all four PLLs and critical AHB/sleep/TS_XO/XO CBCRs.

## Control flow
On `"qcom,kaanapali-videocc"` match, `qcom_cc_probe()` maps the register block, configures PLLs, applies the hardware register configure callback, marks critical CBCRs, and registers clocks, resets, and GDSCs. Consumers then use CCF and genpd to drive video engines and VPP paths.

## State and persistence behavior
Hardware retains PLL programming, RCG settings, branch gates, reset bits, and GDSC power state. The configure hook writes persistent GDSC timing/sync bits. The driver keeps only static descriptors.

## Dependencies and integration points
It integrates with qcom CCF primitives, GDSC power domains, reset framework, regmap, and Kaanapali video dt-bindings. Consumers are video codec and VPP/display-adjacent blocks that request named clocks and power domains.

## Risks
This is a dense descriptor file with high risk in PLL config values, GDSC CFG3 offsets, and binding array order. The hardware recommendations in `clk_kaanapali_regs_configure()` are mandatory-looking; missing them may cause reset or power sequencing failures. Critical clocks affect idle power.

## Test signals
Video workloads should exercise all MVS/VPP domains. Rate tests should select entries from each MVS RCG table. Power-domain tests should verify GDSC on/off sequencing after the ACCU config writes. Reset lines and always-on critical clocks should be visible through debugfs and functional tests.
