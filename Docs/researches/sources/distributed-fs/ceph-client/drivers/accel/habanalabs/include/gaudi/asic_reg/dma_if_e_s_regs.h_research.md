<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_e_s_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_e_s_regs.h

### Purpose
`dma_if_e_s_regs.h` is the auto-generated Gaudi top-level register map for the east-south DMA interface block, identified as `DMA_IF_E_S` with prototype `DMA_IF`. It defines 419 `mmDMA_IF_E_S_*` MMIO constants from `0x4A0000` through `0x4A0834`, matching the east-north top-level layout under the south DMA interface base.

### Important APIs, Types, And Functions
The header exports macro constants only, protected by include guard `ASIC_REG_DMA_IF_E_S_REGS_H_`. Important families include HBM0/HBM1 write/read credit counters, HBM limiter/almost/credit enables, 16-entry min/max protection and privilege windows for SOB, DMA0, and DMA1 read/write transactions, protection/privilege hit registers, bin/debug registers, SOB clock gating, HBM I2C address/misc registers, and CoreSight/bus-monitor base addresses such as `STM_BASE`, `ETF_BASE`, `FUNNEL_BASE`, SOB BMON, and HBM0/HBM1 read/write BMON bases.

### Control Flow
There is no direct executable control flow. Runtime consumers use the map to configure the south DMA interface: set HBM credits and limiters, enable credit checks, configure SOB/DMA0/DMA1 protection and privilege windows, inspect hit latches, and register tracing/monitoring components. `gaudi.c` programs the south credit counters and enables alongside the north equivalents. `gaudi_security.c` uses the protection window constants for access policy, and `gaudi_coresight.c` maps the CoreSight and BMON base constants into the tracing infrastructure.

### State, Persistence, And Dependencies
The file itself is stateless. It names persistent hardware state in the east-south DMA interface: credit/limiter registers, protection windows, hit status, clock-gating state, HBM I2C/misc configuration, and debug monitor blocks. It depends on the Gaudi register generator and on matching bitfield headers for value construction. Structurally it is identical to `dma_if_e_n_regs.h` after normalizing `DMA_IF_E_S` to `DMA_IF_E_N` and `0x4A` to `0x4E`, which is an important invariant for common north/south setup code.

### Integration Points
`gaudi.c` writes `HBM0/1_WR_CRED_CNT`, `HBM0/1_RD_CRED_CNT`, and `HBM_CRED_EN_0/1` for this block. `gaudi_security.c` includes the south SOB/DMA0/DMA1 protection and hit registers in global DMA security arrays and sets protection blocks for `mmDMA_IF_E_S_BASE` and related downstream bases. `gaudi_coresight.c` uses the south STM, ETF, funnel, and BMON base constants to expose DMA interface trace and performance-monitoring endpoints.

### Risks
Incorrect south top-level addresses can affect DMA throughput, HBM credit accounting, protection enforcement, and tracing. Because the north/south maps are symmetric, a mistaken north constant in south setup may still compile and can be missed unless tests exercise both directions. Protection windows are security-sensitive and can either over-permit DMA or break valid traffic if min/max ranges are wrong. Debug and CoreSight base drift can make diagnostics misleading during field failures.

### Test Signals
Signals include correct south HBM credit programming, stable DMA throughput through the east-south interface, expected protection/privilege hit latches under denied SOB/DMA0/DMA1 transactions, no false hits for allowed transactions, CoreSight/BMON discovery for `DMA_IF_E_S`, and static generated-register comparison against the ASIC database. North/south parity tests should confirm normalized equality with `dma_if_e_n_regs.h` while preserving distinct `0x4A` and `0x4E` MMIO bases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_e_s_regs.h -->
