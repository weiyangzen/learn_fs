# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-apmixedsys.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-apmixedsys.c

### Purpose
`clk-mt8196-apmixedsys.c` implements MT8196 APMIXEDSYS PLL providers for two PLL groups: main APMIXEDSYS and APMIXEDSYS_GP2. It provides root PLLs used by topckgen, multimedia, storage, network, display, image, and audio/video clock trees.

### Important APIs, Types, And Functions
Key definitions are `PLL_FENC`, `struct mtk_pll_desc`, `apmixed_plls`, `apmixed2_plls`, `clk_mt8196_apmixed_probe()`, and `clk_mt8196_apmixed_remove()`. PLLs use `mtk_pll_fenc_clr_set_ops`, shared enable/set/clear registers `PLLEN_ALL*`, `FENC_STATUS_CON0`, 22 PCW bits, and 8 integer bits. OF match data selects the descriptor.

### Control Flow, State, And Persistence
Probe obtains match data, allocates `clk_hw_onecell_data`, registers all PLLs, adds an OF clock provider, and stores clk data in platform driver data. Error paths unregister PLLs and free data. Remove deletes the provider, unregisters PLLs, and frees data. Persistent state is hardware PLL configuration and enable bits only.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include `clk-pll.h`, MT8196 clock bindings, OF matching, and topckgen consumers expecting names such as `mainpll`, `univpll`, `emipll`, `mainpll2`, and `tvdpll*`. Risks include fencing status bit mismatches, always-on PLL flag mistakes for EMI/main PLLs, and failure to unwind providers. Test signals include boot clock tree registration, PLL rate changes, topckgen parent resolution, OF provider failure injection, and suspend/resume PLL state.
