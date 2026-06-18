<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_e_s_down_ch0_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_e_s_down_ch0_regs.h

### Purpose
`dma_if_e_s_down_ch0_regs.h` is the auto-generated register map for Gaudi's east-south DMA interface downstream channel 0 router-control block. It exposes 437 `mmDMA_IF_E_S_DOWN_CH0_*` constants from `0x4A1108` through `0x4A1CBC`, matching the north channel-0 layout but under the east-south MMIO base.

### Important APIs, Types, And Functions
The exported surface is the include guard `ASIC_REG_DMA_IF_E_S_DOWN_CH0_REGS_H_` plus macros for MMIO addresses. Register families include permission selection, HBM/SRAM hash polynomial tables, SRAM/HBM scrambling enables, HBM/PCI/SRAM rate-limit controls, E2E HBM/PCI read/write size and counter registers, non-linear SRAM/HBM bank/offset mapping, 16-entry AW and AR secure/privileged range base/mask tables, range-hit registers, regularizer latency/token/bank/watchdog controls, and HBM per-channel E2E counter wrap/count registers.

### Control Flow
The file contains no branches or functions. It supports the east-south channel-0 setup sequence: configure routing and scrambling, install rate limits and E2E sizes/enables, set non-linear memory mapping, program secure and privileged ranges for reads and writes, and read status counters/hit registers during diagnostics or fault handling. `gaudi.c` programs the same scrambling and E2E fields on this south channel that it programs for the corresponding north channels.

### State, Persistence, And Dependencies
All persistent state is hardware state in the east-south downstream channel 0 block. It includes address mapping tables, security/privilege windows, E2E counters, rate-limiter state, and hit latches. The file depends on the generated Gaudi register database and on exact symmetry with the north/south channel maps; normalized comparison shows this file matches `dma_if_e_n_down_ch0_regs.h` after replacing the direction prefix and `0x4A1xxx`/`0x4E1xxx` base.

### Integration Points
`gaudi.c` uses `mmDMA_IF_E_S_DOWN_CH0_SCRAM_SRAM_EN`, `SCRAM_HBM_EN`, E2E size registers, and E2E enables. `gaudi_security.c` includes this block in secure range hit arrays, base/mask arrays, and protection-block setup. The south top-level DMA interface register map provides companion master protection and HBM credit controls for this downstream channel.

### Risks
Risks mirror the north channel but on the south path: wrong register addresses can misroute DMA, disable required scrambling, hide E2E failures, or weaken secure/privileged DMA range enforcement. The repetitive AW/AR and secure/privileged tables are susceptible to index and family mix-ups. Since the file is generated, source edits should not be used to fix address problems; the register generator and upstream ASIC database need correction.

### Test Signals
Signals include successful east-south channel 0 DMA transfers, expected E2E HBM/PCI counts, correct scrambling behavior, secure/privileged range-hit reporting for blocked accesses, absence of false hits for allowed traffic, and channel reset/reprogramming behavior. Static checks should verify all definitions are in the `0x4A1xxx` window and that normalized contents match the north channel-0 map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_e_s_down_ch0_regs.h -->
