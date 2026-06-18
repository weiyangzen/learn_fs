<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-cpumux.h -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-cpumux.h

### Purpose
This header declares the CPU mux registration interface used by MediaTek SoC clock drivers.

### Important APIs, Types, And Functions
It forward-declares `struct clk_hw_onecell_data`, `struct device_node`, and `struct mtk_composite`, then declares `mtk_clk_register_cpumuxes()` and `mtk_clk_unregister_cpumuxes()`.

### Control Flow, State, And Persistence
The header has no runtime behavior. It defines the compile-time contract: callers provide a device, DT node, composite descriptors, count, and clock data container; unregister receives the same descriptor array and data container.

### Dependencies, Integration Points, Risks, And Test Signals
It integrates `clk-cpumux.c` with SoC drivers such as MT2701. Risks are signature drift between header and implementation or missing includes in users. Test signals are successful compilation of SoC drivers that include it and registration/unregistration coverage through those drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-cpumux.h -->
