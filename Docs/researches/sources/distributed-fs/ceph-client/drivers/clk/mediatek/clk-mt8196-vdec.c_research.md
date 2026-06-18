# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-vdec.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-vdec.c

### Purpose
`clk-mt8196-vdec.c` provides MT8196 video decoder clock gates for the main VDEC system and VDEC SOC companion block. It covers VDEC core, active, engine, LAT, LARB, SOC IPS/APTV, and APTV top clocks.

### Important APIs, Types, And Functions
The file defines multiple CG and HWV register blocks and gate macros `GATE_HWV_VDE20/21/22` and `GATE_HWV_VDE10/11/12/13/14`. Descriptors `vde2_mcd` and `vde1_mcd` set `.need_runtime_pm = true`. Gates use inverted HWV set/clear ops, and LARB clocks carry `CLK_IGNORE_UNUSED`.

### Control Flow, State, And Persistence
OF matching selects `mediatek,mt8196-vdecsys` or `mediatek,mt8196-vdecsys-soc`. The simple helper registers the selected runtime-PM-aware descriptor. Clock state is controlled through hardware voter registers and underlying VDEC CG banks; no custom storage exists.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parent `vdec`, `ck_tck_26m_mx9_ck`, runtime PM, video decoder drivers, and SMI/LARB. Risks include inverted HWV semantics, `CLK_IGNORE_UNUSED` masking missing consumers, and runtime PM ordering around decoder power domains. Test signals include V4L2 decode, LAT/core dual-path operation, runtime PM transitions, HWV completion, and suspend/resume decode recovery.
