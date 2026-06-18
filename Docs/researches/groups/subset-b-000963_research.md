# Research: subset-b-000963

Grouped research for generated HabanaLabs Gaudi DMA register headers. Each section is source-path aligned for reconciliation into the per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma1_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma1_qm_regs.h

## Purpose

`dma1_qm_regs.h` is an auto-generated GPL-2.0 register map for the Gaudi `DMA1_QM` block, identified in the file as prototype `QMAN`. It exports C preprocessor constants for memory-mapped register offsets in the DMA1 queue manager window. The file contains 406 `mmDMA1_QM_*` macros spanning `0x528000` through `0x528D00`; `gaudi_blocks.h` maps the corresponding full block base as `mmDMA1_QM_BASE` at `0x7FFC528000ull`.

## Important APIs, Types, And Register Groups

The header defines no C functions, structs, enums, or inline APIs. Its API surface is the macro namespace. The important groups are global configuration and protection (`GLBL_CFG0`, `GLBL_CFG1`, `GLBL_PROT`, secure/non-secure property banks), producer queue registers for four exposed queues (`PQ_BASE_*`, `PQ_SIZE_*`, `PQ_PI_*`, `PQ_CI_*`, `PQ_CFG*`, `PQ_STS*`), completion queue registers for five queues (`CQ_CFG*`, `CQ_PTR_*`, `CQ_TSIZE_*`, `CQ_CTL_*`, status mirrors, IFIFO counters), command processor message base registers, LDMA offset registers, fence data/count/status/current-instruction registers, arbitration registers (`ARB_*`), CGM and rate-limit registers, indirect APB gateway registers, and global error message registers.

## Control Flow And State

The file has no executable control flow. Runtime control flow is created by Gaudi driver users that program these offsets with `WREG32`/`RREG32`. `gaudi_init_pci_dma_qman()` initializes DMA QMAN instances by calculating `dma_id * DMA_QMAN_OFFSET` and programming the common DMA0-relative QMAN layout; the DMA1 constants also appear directly in reset paths such as `gaudi_disable_pci_dma_qmans()` and `gaudi_stop_pci_dma_qmans()`. DMA1 is treated as a PCI DMA queue manager: the PCI stop path stops four upper CPs with `0xF << DMA0_QM_GLBL_CFG1_CP_STOP_SHIFT`.

The persistent state represented by this header is hardware state, not software storage. Queue base addresses, queue sizes, producer/consumer indexes, command processor message bases, fence counters, ARB credits, error causes, and MMU ASID bits remain in device registers until reset, reinitialization, context preparation, or explicit driver writes. `gaudi_mmu_prepare()` writes `mmDMA1_QM_GLBL_NON_SECURE_PROPS_0..4` for ASID/MMU setup. `gaudi_restore_qm_registers()` restores QMAN ARB configuration by offset arithmetic after user register reset.

## Dependencies And Integration Points

This header is included through `gaudi_regs.h`, which aggregates Gaudi ASIC register maps. Bit definitions live in sibling shift/mask headers; users combine this file's offsets with field macros such as `DMA0_QM_GLBL_CFG1_CP_STOP_SHIFT`. Address spacing is tied to `DMA_QMAN_OFFSET` in `gaudiP.h`, defined from `mmDMA1_QM_BASE - mmDMA0_QM_BASE`. Queue diagnostics use the same layout to derive queue IDs for `GAUDI_EVENT_DMA0_QM ... GAUDI_EVENT_DMA7_QM`; fence lookup directly uses `mmDMA1_QM_CP_FENCE2_RDATA_0..3` for DMA1 queue fences.

## Risks And Test Signals

Because this is generated hardware ABI, the main risk is stale or incorrect offsets. A single wrong constant can route queue programming, MMU properties, error messages, or fence reads to the wrong block. Particular risk areas are the four-queue PCI behavior, the fifth CQ slot used internally, and the distinction between absolute per-instance constants and DMA0-relative offset arithmetic. Test signals are successful Gaudi driver build, PCI DMA queue initialization without RAZWI/error interrupts, idle-state reporting from `QM_GLBL_STS0` and `CGM_STS`, fence address reads for DMA1 queues, debugfs/engine idle output, and reset/stall paths that leave DMA1 idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma1_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma2_core_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma2_core_regs.h

## Purpose

`dma2_core_regs.h` is the generated register-offset contract for the Gaudi `DMA2_CORE` block, prototype `DMA_CORE`. It defines 67 `mmDMA2_CORE_*` constants from `0x540000` through `0x540238`; `gaudi_blocks.h` identifies `mmDMA2_CORE_BASE` as `0x7FFC540000ull`. DMA2 is one of the HBM DMA engines in the driver reset and stop paths.

## Important APIs, Types, And Register Groups

The file exposes only macros. The register groups cover core enable/configuration (`CFG_0`, `CFG_1`, `LBW_MAX_OUTSTAND`), source and destination base addresses, multidimensional transfer sizes and strides for dimensions 0..4, `COMMIT`, write-completion data/address/AWUSER registers, tensor-engine row count, protection and secure/non-secure properties, read and write outstanding/cache/user/inflight tuning, read/write rate limit configuration, error configuration/cause/message payload registers, status registers, read debug memory access registers, and debug counters/status for HBW/LBW AXI and descriptors.

## Control Flow And State

The header has no executable code. Driver code creates DMA2 control flow by writing these offsets directly or through DMA0-relative arithmetic. `gaudi_init_dma_core()` initializes each DMA core by programming max outstanding reads, the H3-2116 `LBW_MAX_OUTSTAND` workaround, error message routing, protection bits, secure MMU bypass, and `CFG_0` enable. HBM reset code stalls DMA2 via `mmDMA2_CORE_CFG_1` with `DMA0_CORE_CFG_1_HALT_SHIFT`. `gaudi_dma_core_transfer()` uses the common core layout to program source/destination, size, and `COMMIT`, then polls `STS0` and checks `ERR_CAUSE`.

The state is device-resident. Transfer descriptors, inflight counters, error causes, rate limits, ASID/MMU properties, and debug memories persist in hardware until reset or driver writes. `gaudi_restore_dma_registers()` restores write-completion address/data and rewrites `WR_AWUSER_31_11` for DMA2 because HBM DMA channels can be modified by user SRAM-reduction flows. `gaudi_mmu_prepare()` writes `mmDMA2_CORE_NON_SECURE_PROPS` during ASID preparation.

## Dependencies And Integration Points

The header is pulled into `gaudi_regs.h`; users depend on matching shift/mask definitions from Gaudi field headers. Its address spacing participates in `DMA_CORE_OFFSET`, derived from DMA1 and DMA0 core bases in `gaudiP.h`. It integrates with HBM DMA initialization, engine idle diagnostics (`DMA_CORE_STS0`), debugfs DMA read fallback, MMU ASID programming, reset restoration, and stop/stall flows for HBM DMA channels.

## Risks And Test Signals

Offset drift is high risk because core registers trigger real DMA transactions. Misprogramming `SRC_BASE`, `DST_BASE`, `DST_TSIZE_0`, or `COMMIT` can corrupt memory; stale `NON_SECURE_PROPS` or AWUSER values can break address translation/security; wrong error-message registers can hide RAZWI conditions. Test signals include successful HBM DMA initialization, DMA2 idle detection, no timeout in `gaudi_dma_core_transfer()`, zero `ERR_CAUSE` after transfers, restored write completion behavior after reset, and correct ASID behavior under MMU-enabled contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma2_core_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma2_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma2_qm_regs.h

## Purpose

`dma2_qm_regs.h` is the generated register map for Gaudi `DMA2_QM`, prototype `QMAN`. It defines 406 `mmDMA2_QM_*` register offsets from `0x548000` to `0x548D00`; `gaudi_blocks.h` maps the full base as `0x7FFC548000ull`. DMA2 is an HBM DMA queue manager.

## Important APIs, Types, And Register Groups

The exported interface is macro-only. Register groups mirror the QMAN layout: global config/protection/error routing, five secure and five non-secure property registers, global status/message enable, four producer queues, five completion queues, CP message bases, LDMA source/destination/size offsets, fence read data/counts, CP status and current-instruction registers, barrier and debug registers, ARUSER/AWUSER fields, arbitration credit/choice/status/error registers, CGM controls, local range, strict-priority and rate limit configuration, indirect APB gateway, and global error address/data registers.

## Control Flow And State

No control flow is present in the header. The driver initializes HBM DMA QMANs through `gaudi_init_hbm_dma_qman()`, using `dma_id * DMA_QMAN_OFFSET` to program the same layout. DMA2-specific macros are used directly in `gaudi_disable_hbm_dma_qmans()` and `gaudi_stop_hbm_dma_qmans()`, where HBM QMANs stop five CPs via `0x1F << DMA0_QM_GLBL_CFG1_CP_STOP_SHIFT`. `gaudi_mmu_prepare()` writes `mmDMA2_QM_GLBL_NON_SECURE_PROPS_0..4`.

Hardware state covered by this header includes PQ/CQ base pointers and indexes, CP message and fence registers, ARB credits and status, CGM status, local range and rate-limit configuration, and error address/data payloads. These values persist in the device until reset, restore, or explicit driver writes. `gaudi_restore_qm_registers()` resets ARB configuration across DMA QMANs by common offset.

## Dependencies And Integration Points

The header is included by `gaudi_regs.h` and shares field definitions with DMA0 QMAN masks/shifts. `DMA_QMAN_OFFSET` depends on the regular spacing of QMAN bases. DMA2 participates in HBM DMA queue setup, MMU context preparation, queue disable/stop flows, engine idle reports, and event descriptions derived from `GAUDI_EVENT_DMA0_QM ... GAUDI_EVENT_DMA7_QM`.

## Risks And Test Signals

The largest risks are incorrect HBM queue programming and ASID/security mismatches. The fifth CQ/CP slot and `0x1F` stop mask matter for HBM DMA, unlike PCI DMA queue managers that expose four CP queues. Regression signals include HBM DMA initialization success, absence of QMAN RAZWI messages, `QM_GLBL_STS0` and `CGM_STS` becoming idle after stop, correct MMU ASID switching, and no queue corruption after reset/restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma2_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma3_core_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma3_core_regs.h

## Purpose

`dma3_core_regs.h` defines the generated register offsets for Gaudi `DMA3_CORE`. It exports 67 `mmDMA3_CORE_*` macros from `0x560000` through `0x560238`, with `mmDMA3_CORE_BASE` in `gaudi_blocks.h` at `0x7FFC560000ull`. DMA3 is part of the HBM DMA set.

## Important APIs, Types, And Register Groups

There are no functions or data types. Macro groups cover core configuration/halt/enable, source and destination base registers, transfer sizes and strides for dimensions 0..4, commit and write-completion registers, protection/security property registers, read/write outstanding and cache controls, ARUSER/AWUSER settings, rate limit registers, error cause/config/message registers, status, read debug memory access, and AXI/descriptor debug counters.

## Control Flow And State

The header has no runtime logic. DMA3 control is driven by common Gaudi DMA routines that add `3 * DMA_CORE_OFFSET` to DMA0 core register offsets, plus direct writes in HBM stall paths to `mmDMA3_CORE_CFG_1`. `gaudi_init_dma_core()` enables and configures the core, `gaudi_dma_core_transfer()` programs source/destination/size/commit and polls status, and reset restoration rewrites completion and AWUSER state for HBM DMA channels including DMA3.

The state represented is persistent device register state: active transfer addresses, multidimensional geometry, inflight counters, error status, completion writeback target, MMU/security properties, and debug state. `gaudi_mmu_prepare()` refreshes `mmDMA3_CORE_NON_SECURE_PROPS` when switching ASID context.

## Dependencies And Integration Points

The file enters the build through `gaudi_regs.h`. Its layout must remain isomorphic with DMA0/DMA1 core maps because `DMA_CORE_OFFSET`-based loops address it indirectly. Integration points include HBM DMA initialization and stall, debugfs DMA transfer helper paths, engine idle reporting through `DMA_CORE_STS0`, reset restore, and MMU preparation. Field-level interpretation depends on sibling Gaudi shift/mask headers.

## Risks And Test Signals

Risks are wrong MMIO offsets for transfer-control registers, broken HBM DMA reset restoration, and security regressions if `NON_SECURE_PROPS` or AWUSER registers move. Transfer size/stride register errors can corrupt multidimensional copies. Test evidence should include successful HBM DMA operation on DMA3, idle detection after stop/stall, zero `ERR_CAUSE`, successful reset restore of completion writebacks, and no ASID mismatch in MMU-enabled workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma3_core_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma3_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma3_qm_regs.h

## Purpose

`dma3_qm_regs.h` is the generated QMAN register map for Gaudi DMA3. It defines 406 `mmDMA3_QM_*` offsets over `0x568000..0x568D00`; `gaudi_blocks.h` maps `mmDMA3_QM_BASE` at `0x7FFC568000ull`. DMA3_QM is used as an HBM DMA queue manager.

## Important APIs, Types, And Register Groups

The API is the macro namespace. The layout includes global configuration/status/protection/error registers, secure and non-secure property banks, PQ and CQ configuration/base/index/status registers, CP message base and LDMA offset registers, fence data/counts/status, CP status/current instruction/barrier/debug registers, ARUSER/AWUSER controls, ARB credit and selection registers, ARB error/status registers, CGM controls, local range and CSMR priority, HBW/LBW rate limits, AXCACHE, indirect APB gateway, and global error payload registers.

## Control Flow And State

No code executes in the header. The driver uses the common QMAN layout through `DMA_QMAN_OFFSET` and direct HBM QMAN stop/disable writes. During HBM QMAN setup, `gaudi_init_hbm_dma_qman()` programs queue memory, queue indexes, command-processor message bases, barriers, error message routing, ARB watchdog, global protection, and enable state. HBM stop code writes DMA3's `GLBL_CFG1` with a five-CP stop mask.

Hardware state includes queue producer/consumer positions, CQ state, command processor message routing, fence counters, ARB credits, rate limits, ASID bits, and error-capture state. `gaudi_mmu_prepare()` updates all five DMA3 QMAN non-secure property registers. `gaudi_restore_qm_registers()` resets ARB configuration by common DMA index.

## Dependencies And Integration Points

`gaudi_regs.h` includes the header. `gaudiP.h` requires the address spacing to match `DMA_QMAN_OFFSET`. Integration points are HBM DMA queue setup, HBM disable/stop, MMU ASID preparation, QMAN idle diagnostics, event-to-QMAN-base reporting, and reset restoration. Field semantics are provided by DMA0 QMAN mask/shift headers.

## Risks And Test Signals

Risks center on HBM QMAN command processor control: wrong queue or CP offsets can stall work, lose completions, misroute sync object messages, or leave queues active during reset. ASID property drift can create translation faults. Tests/signals include HBM queue workloads using DMA3, clean QMAN idle output, no ARB/QMAN error causes, correct ASID updates, and successful reset/stall behavior with all five CPs stopped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma3_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma4_core_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma4_core_regs.h

## Purpose

`dma4_core_regs.h` is the generated register map for `DMA4_CORE`, a Gaudi DMA core block. It provides 67 `mmDMA4_CORE_*` offsets from `0x580000` to `0x580238`; `gaudi_blocks.h` lists `mmDMA4_CORE_BASE` as `0x7FFC580000ull`. DMA4 is managed as an HBM DMA engine.

## Important APIs, Types, And Register Groups

The file contains macro definitions only. Functional groups are configuration and halt, LBW outstanding workaround control, source/destination base registers, source/destination multidimensional sizes and strides, commit, write completion data/address/user registers, tensor-engine rows, protection and secure/non-secure properties, read/write outstanding and cache controls, rate limits, error cause/config/message registers, status registers, read debug memory controls, and debug counters for HBW/LBW AXI plus descriptors.

## Control Flow And State

There is no local control flow. DMA4 is programmed by common DMA-core routines through `4 * DMA_CORE_OFFSET`, and by direct HBM stall writes to `mmDMA4_CORE_CFG_1`. Initialization enables the core and configures error-message routing and secure MMU bypass. Transfer code writes source/destination/size and commits, then polls `STS0` and reads `ERR_CAUSE`.

State is entirely in hardware: active transfer descriptors, completion writeback registers, outstanding/inflight counters, rate limit knobs, error state, and security/ASID properties. Reset restore rewrites completion target and `WR_AWUSER_31_11` for DMA4 as an HBM channel. MMU preparation updates `mmDMA4_CORE_NON_SECURE_PROPS`.

## Dependencies And Integration Points

The header is included by `gaudi_regs.h`. It depends on the shared DMA core register shape used by `DMA_CORE_OFFSET` in `gaudiP.h` and field definitions from sibling headers. Integration points include HBM DMA init/stall/disable flows, debugfs DMA read and transfer helper paths, engine idle reporting, reset restore, and MMU ASID setup.

## Risks And Test Signals

Critical risks are memory corruption from source/destination/commit offset errors, lost or misdirected write completions, and security faults from non-secure property drift. A wrong `CFG_1` halt offset can leave DMA4 running during reset. Test signals include DMA4 HBM traffic completing, no transfer timeouts, idle status after stop, zero error cause after operations, correct write-completion restoration after reset, and successful MMU-context workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma4_core_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma4_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma4_qm_regs.h

## Purpose

`dma4_qm_regs.h` defines the generated Gaudi `DMA4_QM` QMAN register offsets. It exposes 406 `mmDMA4_QM_*` constants in the `0x588000..0x588D00` range; `gaudi_blocks.h` places the full base at `0x7FFC588000ull`. DMA4_QM is part of the HBM DMA queue-manager group.

## Important APIs, Types, And Register Groups

No functions or types are declared. Macro groups cover global QMAN config/status/protection/error registers, secure and non-secure properties, message enables, producer queues, completion queues, CP message base banks, LDMA offsets, fences, CP current instruction/status/barrier/debug fields, AXI user controls, ARB credit/choice/status/error controls, CGM and local range registers, priority/rate-limit/AXCACHE controls, indirect gateway registers, and global error capture.

## Control Flow And State

The header itself has no control flow. `gaudi_init_hbm_dma_qman()` uses the common QMAN offsets to configure DMA4 queues, command processor message bases for monitor/SOB signaling, error messages, ARB watchdog, protection, and enable state. Direct HBM reset paths disable `mmDMA4_QM_GLBL_CFG0` and stop CPs with `mmDMA4_QM_GLBL_CFG1`.

State persists in device registers: queue base addresses and indexes, CQ descriptors, CP message and fence values, ARB credits, rate limits, MMU ASID properties, and error payloads. `gaudi_mmu_prepare()` writes `mmDMA4_QM_GLBL_NON_SECURE_PROPS_0..4`; `gaudi_restore_qm_registers()` resets DMA QMAN ARB configuration by offset.

## Dependencies And Integration Points

The header is aggregated by `gaudi_regs.h`. Address consistency is required by `DMA_QMAN_OFFSET`. It integrates with HBM DMA QMAN initialization, HBM disable/stop, MMU context preparation, queue event reporting, QMAN idle checks, and reset restoration. The field masks/shifts are defined in sibling generated headers and are typically referenced through DMA0 names.

## Risks And Test Signals

Risk areas are queue corruption, missed completions, incorrect fence data, misrouted monitor/SOB messages, and reset races if the five-CP stop mask does not hit the intended register. Test signals include HBM DMA4 queue execution, idle `QM_GLBL_STS0`/`CGM_STS` after drain, no QMAN/ARB error causes, correct ASID updates, and successful reinitialization after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma4_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma5_core_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma5_core_regs.h

## Purpose

`dma5_core_regs.h` is the generated register map for Gaudi `DMA5_CORE`. It defines 67 `mmDMA5_CORE_*` offsets from `0x5A0000` through `0x5A0238`, with `mmDMA5_CORE_BASE` at `0x7FFC5A0000ull`. The driver treats DMA5 as part of the PCI DMA group together with DMA0 and DMA1.

## Important APIs, Types, And Register Groups

The exported surface is macro-only. Register groups include core configuration/halt/enable, LBW outstanding control, source/destination base addresses, transfer sizes and strides, commit, write-completion address/data/AWUSER, tensor row count, protection and secure/non-secure properties, read/write outstanding/cache/user/inflight controls, rate limits, error cause/config/message registers, status, read debug-memory registers, and debug counters/status.

## Control Flow And State

The header has no executable code. DMA5 core control is performed either by direct macros in PCI stall paths (`mmDMA5_CORE_CFG_1`) or through common offset arithmetic. `gaudi_init_dma_core()` configures all DMA cores, while PCI DMA setup may assign DMA5 as one of the PCI engines. `gaudi_dma_core_transfer()` can use the same layout to execute direct DMA reads and polls core status/error registers.

Hardware state includes active transfer address/size/commit state, write completion target, inflight counters, rate-limit and cache settings, protection/security bits, debug memory, and error cause/message payloads. `gaudi_mmu_prepare()` writes `mmDMA5_CORE_NON_SECURE_PROPS`; reset restoration rewrites write-completion configuration and AWUSER for channels above DMA1, including DMA5.

## Dependencies And Integration Points

The header is included by `gaudi_regs.h` and depends on regular DMA core spacing used by `DMA_CORE_OFFSET`. It integrates with PCI DMA init/stall/disable paths, debugfs DMA transfers, engine idle diagnostics, reset restoration, and MMU ASID setup. Field masks and shifts are supplied by sibling generated headers, generally named for DMA0 core.

## Risks And Test Signals

Risks include corrupting host/device memory through wrong transfer register offsets, leaving the PCI DMA engine active during reset, incorrect write completion after reset, or failing MMU/security setup. Test signals are successful PCI DMA operation when DMA5 is assigned, no timeout in transfer polling, clean `ERR_CAUSE`, idle status after stop/stall, valid completion SOB writes after restore, and correct ASID behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma5_core_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma5_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma5_qm_regs.h

## Purpose

`dma5_qm_regs.h` is the generated QMAN register-offset header for Gaudi DMA5. It defines 406 `mmDMA5_QM_*` macros from `0x5A8000` to `0x5A8D00`; `gaudi_blocks.h` maps `mmDMA5_QM_BASE` to `0x7FFC5A8000ull`. DMA5_QM is handled by the driver as a PCI DMA queue manager and is also named in collective-queue comments in `gaudiP.h`.

## Important APIs, Types, And Register Groups

The file has no functions or types. It provides global QMAN config/protection/status/error macros, secure and non-secure property banks, PQ/CQ registers, CP message base banks, LDMA offset registers, fence data/count/status registers, CP status/current instruction/barrier/debug registers, AXI user controls, ARB credit/choice/status/error macros, CGM/local-range/rate-limit controls, indirect APB gateway registers, and global error payload macros.

## Control Flow And State

No local control flow exists. `gaudi_init_pci_dma_qman()` can initialize DMA5 via common DMA QMAN offset arithmetic, programming queue memory, command processor message bases, barrier config, error message routing, ARB watchdog, protection, and `GLBL_CFG1`. Reset paths directly disable and stop DMA5 QMAN with PCI four-CP masks. `gaudi_get_fence_addr()` directly maps DMA5 queue IDs 0..3 to `mmDMA5_QM_CP_FENCE2_RDATA_0..3`.

State persists as queue pointers, CP message/fence state, ARB credits, CGM status, rate-limit configuration, non-secure ASID bits, and error-capture payloads. `gaudi_mmu_prepare()` writes all five DMA5 QMAN non-secure property registers, even though PCI-visible queues use four CP streams. `gaudi_restore_qm_registers()` resets ARB config across all DMA QMANs.

## Dependencies And Integration Points

The header is included via `gaudi_regs.h`; its spacing must match `DMA_QMAN_OFFSET`. It integrates with PCI DMA queue setup, PCI QMAN disable/stop, queue fence address resolution, engine idle checks, MMU context preparation, event reporting, and reset restoration. Field-level semantics are imported from sibling QMAN shift/mask headers.

## Risks And Test Signals

Risk concentrates around PCI DMA queue and fence behavior: wrong offsets can make user-visible queues fail, return wrong fence addresses, or miss completions. Errors in global error routing can hide PCI DMA faults. Test signals include DMA5 queue submissions completing, correct fence readback for DMA5 queues, clean PCI DMA stop/disable, no QMAN/ARB error status, idle status after reset, and ASID updates not breaking DMA5 work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma5_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma6_core_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma6_core_regs.h

## Purpose

`dma6_core_regs.h` is the generated register-offset header for Gaudi `DMA6_CORE`. It exports 67 `mmDMA6_CORE_*` macros in the `0x5C0000..0x5C0238` range, and `gaudi_blocks.h` maps `mmDMA6_CORE_BASE` at `0x7FFC5C0000ull`. DMA6 is part of the HBM DMA engine group.

## Important APIs, Types, And Register Groups

No executable APIs or types are defined. Register groups cover configuration/halt/enable, LBW outstanding controls, source and destination base addresses, transfer sizes/strides, commit, write-completion address/data/AWUSER, TE rows, protection and secure/non-secure properties, read/write outstanding/cache/user/inflight controls, rate limits, error configuration/cause/message payload, status, debug memory controls, and AXI/descriptor debug counters.

## Control Flow And State

The header has no control flow. HBM DMA code directly stalls DMA6 through `mmDMA6_CORE_CFG_1`, while initialization, transfers, status polling, and error handling use DMA0-relative offset arithmetic. `gaudi_init_dma_core()` configures error routing, protection, secure MMU bypass, and enable; `gaudi_dma_core_transfer()` writes source/destination/size and commits work.

Device state includes transfer descriptors, inflight counters, write-completion target, error cause, rate limits, debug data, and MMU/security properties. Reset restoration rewrites completion and AWUSER state for DMA6. `gaudi_mmu_prepare()` updates `mmDMA6_CORE_NON_SECURE_PROPS` during ASID preparation.

## Dependencies And Integration Points

`gaudi_regs.h` includes this file. Correct operation depends on `DMA_CORE_OFFSET` and the shared DMA core field definitions. DMA6 integrates with HBM DMA init/stall, reset restore, debugfs DMA transfer paths, idle reporting, and MMU context setup.

## Risks And Test Signals

Wrong offsets can corrupt DMA transfers, prevent halting during reset, or break ASID/security properties. `WR_AWUSER_31_11` restoration is a known sensitivity for HBM channels. Test signals include clean DMA6 HBM transfers, no timeout or error cause, idle status after stop/stall, reset restore preserving completion behavior, and MMU-enabled workloads running without DMA6 translation faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma6_core_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma6_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma6_qm_regs.h

## Purpose

`dma6_qm_regs.h` is the generated QMAN map for Gaudi DMA6. It defines 406 `mmDMA6_QM_*` offsets from `0x5C8000` through `0x5C8D00`; `gaudi_blocks.h` lists `mmDMA6_QM_BASE` as `0x7FFC5C8000ull`. DMA6_QM belongs to the HBM DMA queue-manager set.

## Important APIs, Types, And Register Groups

The header exposes macros only. It includes global QMAN config/status/protection/error registers, secure/non-secure property banks, message enables, PQ and CQ registers, CP message base banks, LDMA offset registers, fence data/counts, CP status/current instruction/barrier/debug controls, ARUSER/AWUSER controls, ARB configuration/credits/choice/status/error registers, CGM/local-range/priority/rate-limit controls, indirect APB gateway registers, and global error payload fields.

## Control Flow And State

There is no local code. HBM queue setup uses the shared layout through `DMA_QMAN_OFFSET`; direct reset paths write `mmDMA6_QM_GLBL_CFG0` and `mmDMA6_QM_GLBL_CFG1`. Initialization configures queues, command processor message bases for sync manager signaling, ARB watchdog, error messages, protection, and enable state. HBM stop writes a five-CP stop mask.

State is maintained in hardware: PQ/CQ pointers and status, CP message/fence registers, ARB credits, CGM state, rate-limit settings, non-secure ASID fields, and error-capture registers. `gaudi_mmu_prepare()` updates all five DMA6 QMAN non-secure property registers; `gaudi_restore_qm_registers()` resets ARB config.

## Dependencies And Integration Points

The file is included by `gaudi_regs.h` and relies on the regular QMAN block spacing used by `DMA_QMAN_OFFSET`. Integration points include HBM DMA queue init, disable/stop, MMU ASID preparation, engine idle diagnostics, event-to-QMAN-base descriptions, and reset restoration. Field-level bits are interpreted through sibling generated mask/shift headers.

## Risks And Test Signals

Risks include queue initialization to the wrong address, failure to stop all HBM CP streams, broken sync-manager message routing, and ASID/security mismatches. Test signals are successful DMA6 HBM queue submissions, idle QMAN/CGM status after stop, no ARB or global QMAN error causes, correct ASID updates, and stable behavior after reset/restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma6_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma7_core_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma7_core_regs.h

## Purpose

`dma7_core_regs.h` is the generated register map for the Gaudi `DMA7_CORE` block. It provides 67 `mmDMA7_CORE_*` macros from `0x5E0000` through `0x5E0238`; `gaudi_blocks.h` maps `mmDMA7_CORE_BASE` at `0x7FFC5E0000ull`. DMA7 is an HBM DMA engine in the driver.

## Important APIs, Types, And Register Groups

The file defines no functions, structs, or enums. Its macro groups represent core config/halt/enable, LBW max outstanding, source and destination bases, source/destination size and stride registers, commit, write completion payload and address, TE row count, protection and security properties, read/write outstanding/cache/user/inflight tuning, read/write rate limits, error configuration/cause/message registers, status, debug memory access, and AXI/descriptor debug counters.

## Control Flow And State

The header has no executable control flow. DMA7 core behavior is driven through common DMA core offset arithmetic and direct HBM stall writes. `gaudi_init_dma_core()` configures the core, `gaudi_dma_core_transfer()` uses the shared register layout for programmed transfers, and HBM reset/stall code writes `mmDMA7_CORE_CFG_1`.

State persists in hardware registers: transfer address and geometry, commit state, inflight counters, completion writeback target, error cause, rate controls, debug memory, and MMU/security properties. Reset restoration rewrites completion and AWUSER registers for DMA7. `gaudi_mmu_prepare()` writes `mmDMA7_CORE_NON_SECURE_PROPS`.

## Dependencies And Integration Points

The header is aggregated by `gaudi_regs.h`. It depends on the common DMA core block layout and `DMA_CORE_OFFSET` in `gaudiP.h`; bit-level use depends on sibling shift/mask headers. Integration points include HBM DMA initialization and stall, DMA transfer helper paths, debugfs reads, engine idle reporting, reset restoration, and MMU ASID setup.

## Risks And Test Signals

Risk areas are incorrect transfer-control offsets causing corruption, failed halt during reset, lost write completions, hidden errors due to wrong error-message offsets, and MMU/ASID property drift. Test signals include successful DMA7 HBM transfers, no `gaudi_dma_core_transfer()` timeout, zero `ERR_CAUSE`, idle status after HBM stop/stall, valid completion restoration after reset, and correct operation under MMU-enabled contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma7_core_regs.h -->
