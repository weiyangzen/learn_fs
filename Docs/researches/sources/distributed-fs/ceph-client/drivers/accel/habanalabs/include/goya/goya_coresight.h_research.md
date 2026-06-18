## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/goya_coresight.h

### Purpose
`goya_coresight.h` names the Goya debug/trace fabric instances used by the HabanaLabs driver. It provides stable enum indexes for CoreSight-style STM, ETF, funnel, bus monitor, and SPMU register tables.

### Important APIs, Types, And Functions
The exported types are `enum goya_debug_stm_regs_index`, `enum goya_debug_etf_regs_index`, `enum goya_debug_funnel_regs_index`, `enum goya_debug_bmon_regs_index`, and `enum goya_debug_spmu_regs_index`. Each enum includes `FIRST` and `LAST` sentinels plus per-block names for CPU, DMA channels/macros, MME subblocks, MMU, PCIe, PSOC, and TPC EML/RTR blocks.

### Control Flow
There is no executable flow. Consumers use these enum values as array indexes into Goya debug register metadata or iteration bounds when enabling, reading, or dumping trace components.

### State, Persistence, And Dependencies
The header stores no state. Persistent effects occur only when caller code uses the indexes to program hardware trace registers. It depends only on consumers maintaining register arrays in the same order as these enums.

### Integration Points
The definitions integrate with HabanaLabs debugfs, coresight/trace collection, performance monitoring, and diagnostics paths for Goya. They bind logical block names to hardware-specific register descriptions.

### Risks
The main risk is index drift: changing enum order without updating the matching register tables would program or read the wrong debug block. Range loops must include `LAST` correctly and not assume all enum families have the same count.

### Test Signals
Useful signals include debug dumps naming the expected blocks, successful trace capture from CPU/DMA/TPC/MMU/PCIe sources, and bounds tests that iterate from `FIRST` through `LAST` without accessing past the matching table.
