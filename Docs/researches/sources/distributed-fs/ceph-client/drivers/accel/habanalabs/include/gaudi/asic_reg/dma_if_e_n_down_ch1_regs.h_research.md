<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_e_n_down_ch1_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_e_n_down_ch1_regs.h

### Purpose
`dma_if_e_n_down_ch1_regs.h` is the auto-generated Gaudi register map for east-north DMA interface downstream channel 1 router-control registers. It mirrors the channel 0 `RTR_CTRL` layout with 437 `mmDMA_IF_E_N_DOWN_CH1_*` constants, shifted into the `0x4E2108` through `0x4E2CBC` channel-1 MMIO window.

### Important APIs, Types, And Functions
There are no functions or data types. The exported API is the include guard `ASIC_REG_DMA_IF_E_N_DOWN_CH1_REGS_H_` and symbolic MMIO offsets. The same functional groups as channel 0 are present: permission selection, HBM/SRAM polynomial and scrambling controls, HBM/PCI/SRAM rate limiters, E2E HBM/PCI size and counter controls, non-linear SRAM/HBM selector and offset registers, 16-entry AW/AR secure and privileged range base/mask tables, range-hit status, RGL expected-latency/token/bank/watchdog registers, and HBM read/write counter wrap/count registers.

### Control Flow
The header has no runtime logic. It supports the second east-north downstream-channel setup path, where driver code configures scrambling, rate limiting, E2E tracking, non-linear addressing, and security windows for channel 1 independently from channel 0. `gaudi.c` programs the channel's `SCRAM_*` and E2E size/enable registers in parallel with the other downstream channels. Security setup uses the channel-1 range and hit registers alongside channel 0 to cover both read/write DMA lanes.

### State, Persistence, And Dependencies
State lives in hardware registers under the east-north channel 1 downstream block. It persists until reset or explicit reprogramming and includes range tables, non-linear mapping tables, E2E counter state, and rate-limiter configuration. The generated layout is mechanically identical to channel 0 after replacing `DOWN_CH0` with `DOWN_CH1` and changing the base from `0x4E1xxx` to `0x4E2xxx`; consumers rely on that symmetry when applying common setup loops or security tables across channels.

### Integration Points
`gaudi.c` writes `mmDMA_IF_E_N_DOWN_CH1_SCRAM_SRAM_EN`, `SCRAM_HBM_EN`, E2E size registers, and E2E enable registers. `gaudi_security.c` includes channel 1 in secure range hit arrays, base/mask arrays, and protection-block setup. This header integrates with `dma_if_e_n_regs.h`, which holds the top-level east-north DMA interface protection and credit windows for SOB/DMA0/DMA1 traffic.

### Risks
The highest-risk bug class is channel confusion: using channel 0 constants against channel 1 setup, or vice versa, silently configures a different downstream lane. Range table errors are security-critical because AW/AR secure and privileged windows define allowed DMA access. E2E counter and size misprogramming can hide data-path errors or create false diagnostics. Generated-file drift against the ASIC specification would affect every consumer, and manual edits can easily break the precise base stride.

### Test Signals
Test signals include successful traffic on east-north downstream channel 1 independent of channel 0, correct E2E HBM/PCI counter behavior, secure/privileged range hits on intentionally blocked DMA reads and writes, no range hits for allowed windows, and reset/reinitialization returning all channel-1 controls to expected values. Static validation should confirm the normalized channel 1 map matches channel 0 and that all constants remain in the `0x4E2xxx` range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_e_n_down_ch1_regs.h -->
