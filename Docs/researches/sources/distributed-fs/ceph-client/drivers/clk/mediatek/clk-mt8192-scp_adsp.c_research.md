# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-scp_adsp.c

## Purpose
`clk-mt8192-scp_adsp.c` registers the MT8192 SCP/ADSP clock gate.

## Important APIs, Types, And Functions
The driver defines `scp_adsp_cg_regs`, a one-entry `scp_adsp_clks` table, `scp_adsp_desc`, and OF compatible `mediatek,mt8192-scp_adsp`.

## Control Flow, State, And Persistence
`mtk_clk_simple_probe()` registers the gate clock and OF provider. There is no custom state or reset handling.

## Dependencies, Integration Points, Risks, And Test Signals
Integration consumers are SCP and ADSP firmware/remoteproc paths. Risks include firmware boot failure if the gate parent or bit is wrong. Test signals include SCP/ADSP remoteproc boot, audio DSP use, and suspend/resume.
