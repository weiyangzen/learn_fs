# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-vdec.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-vdec.c

### Purpose
`clk-mt8365-vdec.c` registers MT8365 video decoder gates for the decoder core and LARB1.

### Important APIs, Types, And Functions
It defines two inverted set/clear gate banks, `GATE_VDEC0`, `GATE_VDEC1`, `vdec_clks`, and `vdec_desc`. OF matching selects the descriptor for `mediatek,mt8365-vdecsys`; probe/remove use the common simple helpers.

### Control Flow, State, And Persistence
The simple probe registers two gates and exposes the OF clock provider. Both gates use `mtk_clk_gate_ops_setclr_inv`, so enable/disable interpretation is inverted relative to normal gates. State is stored in the VDEC hardware registers only.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parent `mm_sel`, video decoder consumers, and SMI/LARB. Risks include inverted gate semantics, minimal table size masking missing decoder clocks, and LARB gating leading to DMA faults. Test signals include V4L2 decode, LARB access during decode, clock enable-count checks, and suspend/resume.
