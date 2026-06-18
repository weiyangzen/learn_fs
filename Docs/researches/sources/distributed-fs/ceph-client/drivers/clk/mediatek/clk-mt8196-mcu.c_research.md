# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-mcu.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-mcu.c

### Purpose
`clk-mt8196-mcu.c` registers per-control-block MT8196 CPU and interconnect PLLs: ARMPLL for big, little, and low-power clusters, plus CCI and PTP PLLs.

### Important APIs, Types, And Functions
The file defines one-PLL arrays (`cpu_bl_plls`, `cpu_b_plls`, `cpu_ll_plls`, `cci_plls`, `ptp_plls`), a `PLL` macro using 22 PCW bits and 8 integer bits, `clk_mt8196_mcu_probe()`, and `clk_mt8196_mcu_remove()`. OF match data directly points to the single-entry PLL array for each compatible.

### Control Flow, State, And Persistence
Probe fetches the match-data PLL array, allocates one clock slot, registers that PLL, adds the OF clock provider, and records driver data. Remove deletes the provider, unregisters exactly one PLL, and frees data. The hardware PLL registers hold rate and enable state; no software persistence is used.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include CPUfreq/OPP consumers, CCI interconnect users, PTP calibration, `clk-pll.h`, and MT8196 DT compatibles. Risks include using identical offsets across distinct register resources, always-on PLL semantics, and cluster PLL parent/rate changes destabilizing CPUfreq. Test signals include CPUfreq transitions, clock provider registration for each PLL node, rate readback, remove unwind, and suspend/resume on CPU clusters.
