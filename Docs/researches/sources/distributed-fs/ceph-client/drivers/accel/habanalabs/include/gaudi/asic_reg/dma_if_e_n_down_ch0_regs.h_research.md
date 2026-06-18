<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_e_n_down_ch0_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_e_n_down_ch0_regs.h

### Purpose
`dma_if_e_n_down_ch0_regs.h` is an auto-generated register-address catalog for Gaudi's east-north DMA interface downstream channel 0 router-control block, identified as `DMA_IF_E_N_DOWN_CH0` with prototype `RTR_CTRL`. It exposes 437 `mmDMA_IF_E_N_DOWN_CH0_*` constants from `0x4E1108` through `0x4E1CBC` for programming channel-local routing, scrambling, rate limiting, end-to-end counters, non-linear address mapping, and security/privilege range checks.

### Important APIs, Types, And Functions
The file exports only preprocessor constants behind include guard `ASIC_REG_DMA_IF_E_N_DOWN_CH0_REGS_H_`. Major register groups are `PERM_SEL`, HBM and SRAM polynomial registers, `SCRAM_SRAM_EN` and `SCRAM_HBM_EN`, rate-limit registers for HBM/PCI/SRAM (`RL_*`), E2E enable/size/counter registers, non-linear mapping selectors and offsets (`NL_*`), 16-entry secure and privileged base/mask tables for AW and AR traffic (`RANGE_SEC_*`, `RANGE_PRIV_*`), range-hit status registers, regularizer/latency-token registers (`RGL_*`), HBM end-to-end wrap/count counters, and HBM page/channel selection registers.

### Control Flow
There is no executable control flow in the header. The hardware-control sequence implied by its constants is: select permissions and hash/polynomial routing parameters, enable SRAM/HBM scrambling where required, configure rate-limit saturations/resets/timeouts, set E2E HBM/PCI write/read sizes and counters, enable non-linear address mapping and bank/offset tables, install secure and privileged address windows for writes and reads, then poll range-hit, E2E, and RGL status/counter registers. `gaudi.c` uses this channel's scrambling and E2E size/enable registers during DMA interface setup, while `gaudi_security.c` uses the channel range tables and hit registers to enforce DMA access policy.

### State, Persistence, And Dependencies
Persistent state is all hardware-local to east-north downstream channel 0: address-transform tables, secure/privileged range tables, rate-limiter settings, E2E counter state, and security hit latches. The file depends on the generated Gaudi register database and on consumers using the matching bitfield definitions for register contents. It also depends on symmetry with the other downstream-channel maps; normalized comparison shows the channel layout is mechanically identical to north channel 1 and the south downstream channels except for prefix and base-address stride.

### Integration Points
`gaudi.c` writes `mmDMA_IF_E_N_DOWN_CH0_SCRAM_SRAM_EN`, `SCRAM_HBM_EN`, E2E HBM/PCI read/write sizes, and E2E enables. `gaudi_security.c` references `RANGE_SEC_HIT_AW/AR`, all secure base/mask table families, and protection-block bases for this block. The top-level DMA interface headers provide companion credit/protection registers for the same east-north DMA path, so channel 0 configuration is only one part of the complete DMA interface setup.

### Risks
Address or index errors in this file can create security holes by programming the wrong secure/privileged range entry or leaving a DMA path unrestricted. The AW and AR tables are similar but separate; mixing read and write windows can break either security or legitimate DMA traffic. Non-linear mapping and HBM/SRAM polynomial registers affect address routing, so incorrect values can corrupt memory rather than fail cleanly. Because this file is generated and highly repetitive, copy/paste style manual repair is unsafe; regeneration plus diff validation is the right correction path.

### Test Signals
Signals include successful east-north channel 0 DMA transfers to HBM, SRAM, and PCI paths, expected behavior with SRAM/HBM scrambling enabled, E2E counter increments/wraps under read/write traffic, enforced secure/privileged range hits on illegal accesses, no false hits on legal DMA windows, and stable operation with non-linear HBM/SRAM mapping enabled. Static tests should verify the 16-entry range table spacing and that channel 0 addresses remain in the `0x4E1xxx` window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_e_n_down_ch0_regs.h -->
