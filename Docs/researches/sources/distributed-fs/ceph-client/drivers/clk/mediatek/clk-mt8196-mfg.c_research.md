# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-mfg.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-mfg.c

### Purpose
`clk-mt8196-mfg.c` registers MT8196 GPU manufacturing PLLs: the main MFG PLL and two shader-core PLL controls.

### Important APIs, Types, And Functions
Important objects are `mfg_ao_plls`, `mfgsc0_ao_plls`, `mfgsc1_ao_plls`, the local `PLL` macro, `clk_mt8196_mfg_probe()`, and `clk_mt8196_mfg_remove()`. PLL descriptors set parent `"mfg_eb"` and `PLL_PARENT_EN`, with 22 PCW bits and 8 integer bits.

### Control Flow, State, And Persistence
The OF compatible selects a single PLL array. Probe allocates one clock slot, registers the PLL, exposes the provider, and records driver data. Remove deletes the provider and unregisters the PLL. Hardware PLL control registers persist actual enable/rate state.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include topckgen parent `mfg_eb`, GPU devfreq/OPP consumers, `clk-pll.h`, and MT8196 bindings. Risks include missing parent enable during PLL operations, identical register offsets requiring separate resources, and bad GPU rate transitions. Test signals include GPU probe and devfreq changes, PLL parent enable count, rate readback, and clean provider removal.
