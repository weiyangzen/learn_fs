<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_e_n_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_e_n_regs.h

### Purpose
`dma_if_e_n_regs.h` is an auto-generated Gaudi register-address catalog for the top-level east-north DMA interface block, identified as `DMA_IF_E_N` with prototype `DMA_IF`. It exports 419 `mmDMA_IF_E_N_*` constants from `0x4E0000` through `0x4E0834` that cover HBM credit controls, SOB/DMA0/DMA1 protection windows, protection hit status, binning/debug bases, CoreSight base addresses, and HBM I2C/miscellaneous registers.

### Important APIs, Types, And Functions
The file contains only macro definitions behind include guard `ASIC_REG_DMA_IF_E_N_REGS_H_`. Important groups include HBM0/HBM1 read/write credit counters and limiter/almost/enable registers; 16-entry min/max read/write protection and privilege windows for SOB, DMA0, and DMA1; read/write protection and privilege hit registers for each master; bin/debug registers such as `HBM_BIN`, `MME_BIN`, `TPC_BIN`, `DMA_BIN`; `SOB_CG_EN`; HBM I2C address and misc registers; and CoreSight/monitoring bases such as `STM_BASE`, `ETF_BASE`, `FUNNEL_BASE`, and HBM/SOB BMON bases referenced by Gaudi tracing code.

### Control Flow
The header has no executable logic. Its implied programming flow is top-level DMA interface setup: program HBM credit counters and limiters, enable credit enforcement, set protection/privilege min/max windows for SOB and both DMA masters, clear or inspect hit registers, then expose debug/trace/bus-monitor base addresses to the monitoring stack. `gaudi.c` writes HBM credit count and enable registers during DMA interface initialization, while `gaudi_security.c` consumes protection-window and hit-register constants when installing DMA access policy.

### State, Persistence, And Dependencies
The header persists no software state. Hardware state named by these constants includes credit counters/limits, per-master protection and privilege windows, protection-hit latches, clock-gating enablement, and debug/monitoring configuration. The file depends on the generated ASIC register source and on bitfield definitions elsewhere for values written into these addresses. It is paired with downstream-channel headers for per-channel routing/range controls; the top-level file protects SOB/DMA master interfaces, while `*_down_ch*` files protect and route downstream lanes.

### Integration Points
`gaudi.c` writes `HBM0/1_WR_CRED_CNT`, `HBM0/1_RD_CRED_CNT`, and `HBM_CRED_EN_0/1` for both north and south DMA interfaces. `gaudi_security.c` builds arrays from `SOB`, `DMA0`, and `DMA1` hit/protection windows to set secure access policies. `gaudi_coresight.c` maps `STM_BASE`, `ETF_BASE`, `FUNNEL_BASE`, and BMON base constants to CoreSight device IDs for tracing and performance monitoring.

### Risks
Wrong top-level protection addresses can allow forbidden DMA reads/writes or block valid firmware/kernel traffic. Credit-counter and limiter mistakes can produce hangs or throughput collapse on HBM paths. The SOB/DMA0/DMA1 protection tables are structurally similar, so off-by-one or wrong-master references can be hard to detect without negative security tests. Debug base constants used by CoreSight and bus monitors must match hardware exactly or diagnostic tools will read unrelated registers.

### Test Signals
Signals include correct HBM credit programming during probe, sustained HBM DMA without credit starvation, negative DMA security tests setting the expected `*_HIT_*` registers, allowed DMA traffic avoiding false protection hits, CoreSight STM/ETF/funnel/BMON enumeration for `DMA_IF_E_N`, and static comparison against the ASIC register database. A useful structural check is that the normalized north map matches `dma_if_e_s_regs.h` except for prefix and `0x4E` versus `0x4A` base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_e_n_regs.h -->
