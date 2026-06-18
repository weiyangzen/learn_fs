# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-mdp.c

## Purpose
`clk-mt8192-mdp.c` registers MT8192 Media Data Path clocks for MDP RDMA, Rsz, WROT, TDSHP, mutex, and related processing blocks.

## Important APIs, Types, And Functions
The driver defines two MDP gate banks, `mdp_clks`, `mdp_desc`, and an OF match for `mediatek,mt8192-mdpsys`. It uses `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()`.

## Control Flow, State, And Persistence
Probe registers the MDP gate table and publishes the provider. No additional software state is kept.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers include MDP and multimedia pipeline drivers. Risks include wrong gate-bank offsets affecting only specific processing units and parent mismatch with top MDP muxes. Test signals include MDP transform workloads, probe of all MDP blocks, and runtime PM transitions.
