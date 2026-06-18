# subset-b-000964 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma7_qm_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma7_qm_regs.h

### Purpose
`dma7_qm_regs.h` is an auto-generated Gaudi ASIC register-address catalog for the DMA7 queue manager block, identified in the file as `DMA7_QM` with prototype `QMAN`. It exposes 406 `mmDMA7_QM_*` constants spanning `0x5E8000` through `0x5E8D00`, so driver code can program DMA7 queue-manager MMIO registers by symbolic name instead of hard-coded offsets.

### Important APIs, Types, And Functions
There are no functions, structs, enums, or executable control-flow APIs. The public surface is the include guard `ASIC_REG_DMA7_QM_REGS_H_` plus `#define` constants. Important register families include `GLBL_*` configuration/status/security properties, `PQ_*` producer queue base/size/index/config/status registers, `CQ_*` completion queue config/pointer/status registers, `CP_*` command processor message bases, LDMA offsets, fence counters, current-instruction/status/debug registers, `ARB_*` arbitration and credit registers, `CGM_*` clock-gating/management registers, local range, rate-limiter, indirect APB gateway, and global error/memory-init status registers.

### Control Flow
The file has no runtime branches. Its implicit control flow is the queue-manager programming sequence used by consumers: configure global queue-manager properties, set producer queue base/size and producer/consumer indexes, configure completion queues, program command-processor message bases and LDMA offsets, tune arbitration/credits/rate limiting, then read status/error/fence/current-instruction registers while queues execute. Initialization code references `mmDMA7_QM_GLBL_CFG0` and `mmDMA7_QM_GLBL_CFG1` to reset/stop parts of the block, and MMU/security code uses the secure/non-secure property registers and protection-bit offsets.

### State, Persistence, And Dependencies
The header itself persists no state, but each macro names device-resident state in the Gaudi MMIO aperture. Persistent hardware state includes queue bases and indexes, CQ pointers and sizes, secure/non-secure ARUSER/AWUSER properties, command processor fence counters and message-base addresses, arbitration credits, and error/status latches. The file depends on the hardware register-generation pipeline remaining synchronized with the Gaudi DMA7 QMAN specification. Consumers depend on common Habanalabs register access helpers such as `WREG32()`/`RREG32()`, bitfield headers for shifts and masks, and the broader Gaudi security/MMU initialization code.

### Integration Points
`gaudi.c` writes `mmDMA7_QM_GLBL_CFG0` and `mmDMA7_QM_GLBL_CFG1` during block initialization/shutdown and prepares `mmDMA7_QM_GLBL_NON_SECURE_PROPS_0..4` for ASID/MMU handling. `gaudi_security.c` derives protection-bit addresses from `mmDMA7_QM_BASE` and many `mmDMA7_QM_*` offsets, including global, PQ, CQ, and CP ranges, so this map is also part of the driver's security programming surface. Queue-manager command submission and diagnostics elsewhere include this generated header indirectly through the Gaudi ASIC register umbrella headers.

### Risks
The main risk is register drift: a wrong address silently directs MMIO writes to the wrong hardware register. DMA7 queue-manager errors can corrupt command queues, completion queues, arbitration fairness, or security attributes. The repeated per-engine arrays are index-sensitive; using a DMA0/DMA1 or PQ/CQ index with the wrong constant can misconfigure a different queue. Because this is generated, manual edits are especially risky and should be replaced by regenerating from the ASIC database. Security-sensitive constants such as secure/non-secure properties, AXUSER fields, and protection-bit locations need extra scrutiny because incorrect values can overexpose privileged DMA paths.

### Test Signals
Useful signals include successful Gaudi probe and DMA7 queue-manager initialization, queue submission/completion through DMA7, no unexpected values in `GLBL_ERR_*` or `ARB_ERR_*`, stable producer/consumer/CQ pointer movement under DMA load, command processor fence-counter progress, suspend/reset recovery without stale queue state, and security tests showing DMA7 protected registers and non-secure properties are programmed as intended. Static validation should compare all generated addresses against the authoritative ASIC register database and ensure no duplicate or out-of-range `mmDMA7_QM_*` definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma7_qm_regs.h -->

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
