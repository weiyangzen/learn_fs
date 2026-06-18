# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-ovl0.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-ovl0.c

### Purpose
`clk-mt8196-ovl0.c` registers the first MT8196 overlay clock provider. It gates OVLSYS config, fake engines, mutex, EXDMA, blenders, output processors, MDP RSZ, WDMA, UFBC WDMA, MDP RDMA, BWM, DLI/DLO async links, relay, inline rotation, and SMI.

### Important APIs, Types, And Functions
All gates are HWV-aware through `GATE_HWV_OVL0` and `GATE_HWV_OVL1`, each carrying direct CG registers and HWV set/clear/done registers. The provider descriptor is `ovl_mcd`, selected through the platform ID table and registered by `mtk_clk_pdev_probe()`.

### Control Flow, State, And Persistence
The platform probe registers a single descriptor containing two hardware banks. Clock enable and disable operations go through `mtk_clk_gate_hwv_ops_setclr`, which coordinates with the hardware voter. No local state is persisted beyond clock framework registration.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parent `disp`, display overlay consumers, HWV gate support, and MT8196 clock IDs. Risks include HWV offset/bit mistakes, display pipeline stalls from overlay async gates, and SMI gating errors. Test signals include overlay composition, DRM page flips, HWV completion status, clock debugfs gate toggles, and suspend/resume.
