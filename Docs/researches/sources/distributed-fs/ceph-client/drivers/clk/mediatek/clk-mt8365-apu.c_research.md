# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-apu.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-apu.c

### Purpose
`clk-mt8365-apu.c` provides MT8365 AI Processing Unit gate clocks for AHB, EDMA, interface, JTAG, AXI, and IPU/APU core clocks.

### Important APIs, Types, And Functions
It defines one set/clear gate bank, `GATE_APU`, `apu_clks`, `apu_desc`, and an OF match table for `mediatek,mt8365-apu`. The driver uses `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()`.

### Control Flow, State, And Persistence
The simple probe registers the APU gate descriptors and exposes them as an OF clock provider. Gate state is stored in the APU CG register block at offsets 0x0/0x4/0x8. There is no custom runtime state or persistence.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parents `ifr_apu_axi`, `apu_sel`, `apu_if_sel`, and `clk26m`, plus APU/IPU consumers. Risks include missing infra parent clocks, incorrect bit positions for core versus bus gates, and APU probe ordering. Test signals include APU driver probe, EDMA/interface clock enables, clk summary parent links, and module unbind/rebind.
