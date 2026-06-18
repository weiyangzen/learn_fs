# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-scp_adsp.c

## Purpose
`clk-mt8195-scp_adsp.c` registers the MT8195 SCP/ADSP clock gate.

## Important APIs, Types, And Functions
It defines `scp_adsp_cg_regs`, one `scp_adsp_clks` entry, `scp_adsp_desc`, and the OF compatible `mediatek,mt8195-scp_adsp`.

## Control Flow, State, And Persistence
The simple helper registers the gate and publishes the provider. No custom state, reset support, or policy is implemented.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers are SCP/ADSP firmware and remoteproc/audio DSP paths. Risks include firmware boot failure if the gate bit or parent clock is wrong. Test signals include SCP/ADSP boot, DSP workload execution, and suspend/resume.
