<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_e_s_down_ch1_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_e_s_down_ch1_regs.h

### Purpose
`dma_if_e_s_down_ch1_regs.h` is the generated register-address catalog for Gaudi's east-south DMA interface downstream channel 1 router-control block. It defines 437 `mmDMA_IF_E_S_DOWN_CH1_*` MMIO constants from `0x4A2108` through `0x4A2CBC`, providing the channel-1 south counterpart to the north and south channel-0 maps.

### Important APIs, Types, And Functions
There are no callable APIs or types. The constants behind include guard `ASIC_REG_DMA_IF_E_S_DOWN_CH1_REGS_H_` cover the full downstream router-control surface: permission selection, HBM/SRAM polynomial tables, scrambling enables, rate-limit configuration, E2E HBM/PCI sizes and counters, non-linear address mapping, 16 secure and 16 privileged range table entries for both AW and AR transactions, range-hit status, RGL latency/token/bank/watchdog registers, HBM channel counter wrap/count registers, and HBM PC select registers.

### Control Flow
The header itself does not execute. In the driver it supports channel-1 programming in the same sequence as the other downstream channels: configure address/routing behavior, enable error-detection and scrambling controls, install access-control ranges, then monitor hit/counter registers. `gaudi.c` treats this file's E2E and scrambling controls as part of the four-channel DMA interface initialization matrix.

### State, Persistence, And Dependencies
State is device-local to east-south downstream channel 1 and persists across normal operation until reset or reprogramming. It includes range tables, routing/non-linear mapping state, E2E counters, and rate-limiter configuration. This generated file depends on a consistent channel stride from south channel 0 and a consistent directional base from the north channel 1 map; normalized diffs confirm the layout is identical after prefix and base substitution.

### Integration Points
`gaudi.c` writes `mmDMA_IF_E_S_DOWN_CH1_SCRAM_SRAM_EN`, `SCRAM_HBM_EN`, E2E read/write size registers, and E2E enables. `gaudi_security.c` references this channel for secure range hits, base/mask arrays, and protection block setup. It is part of the same east-south DMA interface subsystem as `dma_if_e_s_regs.h`, which owns the top-level credits and SOB/DMA master protection windows.

### Risks
The largest risks are wrong base address, wrong channel constant, or read/write range-family confusion. Any of those can leave channel 1 with missing security windows while tests against channel 0 still pass. E2E size/counter mistakes can reduce diagnostic coverage for DMA data-path issues. Generated register maps should be validated mechanically because manual review of hundreds of repeated lines is error-prone.

### Test Signals
Signals include independent DMA traffic through east-south downstream channel 1, E2E counter changes for HBM and PCI read/write paths, expected secure/privileged hit status under denied accesses, clean traffic under allowed ranges, and reset/reinit of the channel-1 downstream block. Static validation should check the `0x4A2xxx` address range and normalized equality with north channel 1 and south channel 0 layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_e_s_down_ch1_regs.h -->
