<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_coresight.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_coresight.h

## Purpose
Defines Gaudi2 CoreSight/debug component index spaces. The enums assign dense indices for STM, ETF, funnel, BMON, and SPMU blocks across compute dcores, TPCs, MMEs, HMMUs, DMA engines, video decoders, PCIe, PSOC, PMMU, rotators, HBM controllers, and NIC debug blocks.

## Important APIs, Types, And Functions
- `enum gaudi2_debug_stm_regs_index` indexes STM register-base tables.
- `enum gaudi2_debug_etf_regs_index` indexes embedded trace FIFO register-base tables.
- `enum gaudi2_debug_funnel_regs_index` indexes trace funnel blocks, including dcore routing, xbar, HBM, and NIC debug funnels.
- `enum gaudi2_debug_bmon_regs_index` indexes bus monitor instances, often with several monitors per engine or interface.
- `enum gaudi2_debug_spmu_regs_index` indexes SPMU performance monitor blocks.
- Each enum provides `FIRST` and `LAST` sentinels for array sizing and bounds checks.

## Control Flow
The header has no executable code. `gaudi2_coresight.c` uses these enum constants as designated initializers for arrays of MMIO base addresses. Debugfs or driver debug paths can then select a logical component index and operate on the corresponding register base without embedding device topology in each access path.

## State And Persistence Behavior
No runtime state is stored here. The enums define compile-time ordering contracts. Runtime state is in CoreSight register programming, debug sessions, and performance monitor configuration. Because `LAST` sizes arrays, adding, removing, or reordering entries changes ABI-like expectations inside the driver.

## Dependencies And Integration Points
Depends on generated Gaudi2 register symbols such as `mmDCORE*_TPC*_EML_STM_BASE`, `mmNIC*_DBG_*`, and similar base definitions in generated ASIC register headers. Integrates with Gaudi2 CoreSight support, debugfs register access, performance tracing, bus monitor setup, and low-level diagnostics.

## Risks And Edge Cases
The dominant risk is index/base mismatch: if enum order diverges from the arrays in `gaudi2_coresight.c`, debug tooling may program the wrong block. Some entries are placeholders or have zero bases in implementation arrays, so callers must tolerate unavailable debug blocks. The BMON enum is especially dense and nonuniform, with repeated per-engine monitors and ordering quirks.

## Test Signals
Builds catch missing enum names in designated initializers. Runtime signals include successful CoreSight/debugfs enumeration, valid MMIO reads for each exposed component, trace collection from selected STM/ETF/funnel paths, and BMON/SPMU counter reads that match traffic on the selected engine.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_coresight.h -->
