# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-mdpsys.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-mdpsys.c

### Purpose
`clk-mt8196-mdpsys.c` registers MT8196 MDP system clocks for mdpsys0 and mdpsys1. It covers MDP mutex, SMI, APB, RDMA, BIRSZ, HDR, AAL, RSZ, TDSHP, color, WROT, RROT, async links, image links, VPP RSZ, and 26 MHz gates.

### Important APIs, Types, And Functions
The file defines three gate banks, `GATE_MDP0/1/2`, two nearly parallel gate arrays (`mdp_clks` and `mdp1_clks`), and descriptors `mdp_mcd` and `mdp1_mcd`. Both descriptors set `.need_runtime_pm = true`, so the common helper integrates provider registration with runtime PM. Probe/remove use `mtk_clk_simple_probe()`.

### Control Flow, State, And Persistence
OF matching selects mdpsys0 or mdpsys1. The helper enables runtime PM as requested, registers gates, and publishes a provider. Gate state resides in the three hardware CG banks; runtime PM state is managed by the common MediaTek helper and device core, not by custom logic here.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parent `mdp`, parent `clk26m`, runtime PM, MDP/DRM/media consumers, and SMI. Risks include duplicated table drift between mdpsys0 and mdpsys1, runtime PM ordering around clock registration, and bus faults if SMI clocks are gated. Test signals include MDP jobs on both systems, runtime PM get/put cycles, clk debugfs state, and image/display pipeline tests.
