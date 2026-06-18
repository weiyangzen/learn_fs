# Research: subset-b-000968

Grouped research for Gaudi ASIC register definition headers under `sources/distributed-fs/ceph-client`. Each section preserves the source path and is wrapped for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/gaudi_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/gaudi_regs.h

## Purpose
`gaudi_regs.h` is the aggregate Gaudi ASIC register include for the HabanaLabs Gaudi driver. It pulls together generated register address headers for PSOC, CPU interface, MMU/STLB, DMA, MME, TPC, DMA/NIF/SIF routers, CoreSight/ETR, PLL, and NIC QMAN blocks, then adds a small set of hand-maintained Gaudi-specific address aliases and offsets that are not present in the generated block files. In practice this is the single register-map contract included by Gaudi implementation files that need broad MMIO coverage.

## Important APIs, types, and functions
This header exports C preprocessor symbols rather than functions or types. The include list is the primary API: it brings in `gaudi_blocks.h`, per-block `_regs.h` files, and selected `_masks.h` files such as `mme0_qm_masks.h`, `dma0_qm_masks.h`, `tpc0_qm_masks.h`, and `nic0_qm0_masks.h`. The locally defined symbols cover ECC diagnostic offsets, synchronization-manager SOB/monitor bases, SIF/NIF router LBW range-protection hit/min/max registers, DMA interface response weights, selected MME1 QMAN aliases, MME SBAB/ACC protection/stall registers, PCIe/GIC/EFUSE/PLL registers, and PCIe wrapper control registers.

The most important local macros are:
- `GAUDI_ECC_*` offsets and ECC clear masks, used as common offsets from block bases for ECC memory diagnostics.
- `mmSYNC_MNGR_*` SOB, monitor payload, arm, and status base addresses for synchronization-object programming.
- `mmSIF_RTR_*` and `mmNIF_RTR_*` range-protection registers, used by security/protection paths and fault diagnostics.
- `mmMME*_SBAB_*` and `mmMME*_ACC_*` aliases for MME stall, AXI user, WBC, and protection registers.
- `mmMME1_QM_GLBL_CFG0` and `mmMME1_QM_GLBL_STS0`, which fill a gap for the second MME QMAN address region.
- PCIe, EFUSE, PLL, MSI, GIC, and PSOC addresses consumed by initialization, interrupt, and hardware-management paths.

## Control flow
The file has no executable control flow. Its control-flow role is compile-time composition: including this header makes the generated `mm...` address symbols and field masks available to driver code that performs register reads and writes through `RREG32()`, `WREG32()`, and related helpers. Gaudi initialization uses these symbols to configure queues, protection bits, PLLs, interrupts, memory-management properties, CoreSight debug blocks, and ASIC security state. Error paths use the same symbols to acknowledge ECC/protection events and to report idle or fault state.

## State and persistence behavior
The header owns no runtime state. Its constants are persistent ABI-like contracts between the Linux driver, generated ASIC register descriptions, firmware expectations, and the Gaudi hardware layout. Any register address in this file persists as a compile-time address baked into the driver image. The hardware state reached through these addresses persists according to the target block: queue pointers and enable bits persist until reset or reprogramming, sync-manager SOB/monitor state persists across command submissions, PLL/PCIe/EFUSE state follows platform initialization rules, and protection registers persist until security setup or reset changes them.

## Dependencies and integration points
`gaudi_regs.h` depends on the generated Gaudi register header set in the same `asic_reg` directory. Downstream integration is broad: `gaudi.c` uses the MME/QMAN/sync-manager/PCIe/GIC symbols during hardware init, reset, idle checks, and queue programming; `gaudi_security.c` computes protection-bit windows from MME and QMAN addresses; `gaudi_coresight.c` uses block bases from the included headers for STM/ETF/ETR/funnel/BMON/SPMU programming; MMU setup uses the MMU/STLB and QMAN security property registers; interrupt code uses GIC/MSI addresses.

This header also bridges generated and hand-added register coverage. Some symbols are offsets relative to repeated block layouts, while others are absolute config-space addresses. Callers must know whether to pass a value directly to `RREG32/WREG32` or subtract `CFG_BASE` for paths that expect a config offset.

## Risks and edge cases
- The file mixes generated includes with hand-maintained address aliases. Address drift can compile cleanly while silently programming the wrong hardware register.
- Repeated router and MME symbols rely on regular address strides. A future ASIC stepping with a non-uniform layout would break arithmetic based on these constants.
- The `mmMME1_QM_*` aliases in this file are only partial, while full QMAN register coverage exists for MME0 and MME2. Consumers must not assume this header provides every MME1 QMAN register.
- ECC offsets are generic offsets, not full addresses. Callers must add them to the correct block base and use the right clear masks for single-bit versus double-bit errors.
- Absolute versus base-relative address expectations are easy to confuse in CoreSight, protection-bit, and register-access code.
- Because this aggregate header includes many generated files, small register-map changes can have a large rebuild and behavioral surface.

## Test signals
Useful validation signals are successful Gaudi probe, hardware initialization, reset, and removal; absence of invalid register access or protection-bit errors during init; working MMU/STLB setup; successful internal queue setup for DMA/MME/TPC/NIC paths; correct idle reports for MME/TPC/DMA engines; working CoreSight debug operations; and expected PCIe/MSI/GIC interrupt delivery. Negative signals include RAZWI/protection errors after security setup, stuck queue or sync-manager state, invalid ECC clear behavior, failed PLL/PCIe initialization, or idle checks reading nonsensical MME/QMAN status values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/gaudi_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme0_ctrl_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme0_ctrl_regs.h

## Purpose
`mme0_ctrl_regs.h` is an auto-generated Gaudi register address map for the `MME0_CTRL` block, whose prototype is `MME`. It names the MMIO offsets for the first MME control block's architectural descriptor registers, command/status/control registers, power/rate/debug controls, and four shadow descriptor banks. The driver uses these symbols to inspect MME idle state, configure security/protection access, program debug infrastructure through block bases, and coordinate MME execution through QMAN-submitted descriptors.

## Important APIs, types, and functions
The header exports only `#define` register address symbols. The important groups are:
- `mmMME0_CTRL_ARCH_*`: live architectural descriptor registers for base addresses, tensor S/L/O valid elements, loop strides, ROI sizes, spatial strides, AGU local and remote offsets, sync-object addresses/data, performance events, padding, metadata, and rate-limiter saturation.
- `mmMME0_CTRL_CMD`, `STATUS1`, `RESET`, `QM_STALL`, `SYNC_OBJECT_FIFO_TH`, `INTR_CAUSE`, `INTR_MASK`, and `PROT`: operational control, interrupt, reset, stall, and protection controls.
- `mmMME0_CTRL_PCU_*`, `EU_POWER_SAVE_DISABLE`, `TE_CLOSE_CGATE`, `AGU_*_CNTR`, `EZSYNC_OUT_CREDIT`, and `QM_SLV_LBW_CLK_EN`: performance-control, power, clock-gate, AGU accounting, and sync-message controls.
- `mmMME0_CTRL_CS_DBG_*`: CoreSight/debug status drop controls.
- `mmMME0_CTRL_SHADOW_0_*` through `SHADOW_3_*`: four replicated descriptor snapshots with the same tensor/AGU/sync/perf/padding/metadata layout as the live `ARCH_*` region.

There are no C functions or structs in this file. The "API" is the stability of the macro names and addresses.

## Control flow
No control flow executes in this header. Runtime control flow appears in Gaudi driver code that includes it. During hardware initialization, the driver enables MME-related capabilities and writes related QMAN registers, while MME control registers are used for protection setup and status/idle checks. During security initialization, `gaudi_security.c` computes protection-bit addresses and masks from `mmMME0_CTRL_RESET`, `mmMME0_CTRL_QM_STALL`, interrupt, PCU, protection, debug, AGU, and shadow-bank symbols, then writes protection-bit registers to restrict or permit access. During idle checks, `gaudi.c` reads `mmMME0_CTRL_ARCH_STATUS + offset` for each MME engine and combines it with QMAN status for master MMEs.

Command execution itself is descriptor-driven: userspace or firmware queues work through QMAN command streams, and MME hardware consumes descriptor fields whose live and shadow register addresses are named here. The header therefore defines the observable register layout for that flow but does not implement descriptor submission.

## State and persistence behavior
The file owns no software state. The addresses name hardware state inside MME0. Architectural descriptor registers represent the active descriptor context; shadow banks preserve snapshots for multiple descriptor slots or debug/visibility; command/status/reset/stall registers affect current engine control; interrupt cause/mask registers persist until acknowledged or reset; protection and power/clock controls persist until security setup, reconfiguration, or hardware reset changes them.

Because the file is generated, its values are expected to be treated as immutable for a given ASIC revision. Persistent driver behavior such as idle reporting, protection setup, and debug register routing depends on the exact spacing between the live region, control region, and shadow regions.

## Dependencies and integration points
The header is included by `gaudi_regs.h`, which is then included by Gaudi implementation files. It integrates with:
- `gaudi.c`, which reads `mmMME0_CTRL_ARCH_STATUS` with per-engine offsets to report idle state and writes MME rollup counters.
- `gaudi_security.c`, which derives protection-bit block addresses and masks from MME0 control and shadow symbols.
- `gaudi_coresight.c`, indirectly through generated block-base headers, where MME control block debug bases are used for STM/ETF/BMON/SPMU.
- QMAN register headers, because MME execution is driven by MME QMANs while control/status is observed through this MME control block.

The file assumes common Gaudi address conventions: symbols are absolute config-space register addresses, and repeated MME engines are reached by adding the appropriate MME block offset in consumers.

## Risks and edge cases
- This is generated hardware data. Manual edits would likely desynchronize the driver from ASIC documentation and firmware assumptions.
- Consumers rely on repeated layout. `gaudi.c` adds per-MME offsets to `mmMME0_CTRL_ARCH_STATUS`; if MME1/MME2/MME3 spacing changes, idle checks can read the wrong engine.
- Protection-bit code computes bit positions from the low address bits of these constants. Any register move across protection-bit word boundaries must be reflected in security logic.
- Shadow-bank layout is very large and repetitive. A missing or reordered shadow register can break debug or security behavior while still compiling.
- Register names do not encode access permissions. Writing a status, shadow, or reserved register from a new path can have hardware-specific side effects.
- The live `ARCH_*` descriptor layout overlaps conceptually with firmware/userspace descriptor formats; mismatches can appear as incorrect MME computation rather than a simple driver failure.

## Test signals
Positive signals include Gaudi MME initialization completing, `HW_CAP_MME` being set, idle checks reporting sane `ARCH_STATUS` values, successful workload execution through MME queues, correct interrupt masking/causes, and no protection-bit faults when accessing allowed MME control registers. Security validation should confirm protected registers remain inaccessible when expected. Negative signals include stuck MME idle status, queue submission timeouts, unexpected MME interrupts, protection-bit violations around `MME0_CTRL_*`, or debug/trace output tied to the wrong MME control block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme0_ctrl_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme0_qm_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme0_qm_masks.h

## Purpose
`mme0_qm_masks.h` is the auto-generated field mask and shift map for the Gaudi `MME0_QM` queue-manager block. It complements `mme0_qm_regs.h`: the register header names addresses, while this file names bit positions and masks for enabling/stopping/flushing queue-manager subblocks, configuring security properties, interpreting status and error bits, programming producer/consumer queues, command processors, arbitration, clock gating, range/rate controls, indirect APB access, and global error capture.

## Important APIs, types, and functions
The exported API is a set of `MME0_QM_*_SHIFT` and `MME0_QM_*_MASK` macros. Important groups include:
- Global enable/stop/flush/protection/error fields: `GLBL_CFG0`, `GLBL_CFG1`, `GLBL_PROT`, and `GLBL_ERR_CFG` cover PQF, CQF, CP, arbiter, error-message enable, and stop-on-error behavior.
- Secure and non-secure properties: per-queue `ASID` and `MMBP` fields for `GLBL_SECURE_PROPS_*` and `GLBL_NON_SECURE_PROPS_*`.
- Global status/error/message fields: idle, stopped, read errors, undefined command, stop op, message write error, WREG error, fence overflow/underflow, and message enable fields.
- PQ and CQ fields: base address, size, PI/CI, credit limit, max inflight, ARUSER, credit/free/inflight counts, empty/busy status, completion queue pointers, transfer size, and control.
- CP fields: message base address registers, LDMA offsets, fence read-data increments/counters, CP state, current instruction, barrier config, debug state, ARUSER/AWUSER attributes.
- Arbiter fields: master/slave configuration, WRR weights, credits, choice queues, watchdog, max inflight, error causes, error message enables, and credit status.
- CGM/range/rate/AXI/cache/indirect gateway/error-capture fields: clock gating status, local range, strict priority, read/write rate limiter, AXCACHE, APB gateway, and global error address/data.

There are no functions or data structures. Callers compose register values with these masks and shifts.

## Control flow
This header has no runtime control flow. It participates in driver control flow when Gaudi code writes MME QMAN registers. For example, initialization code builds global error configuration values using higher-level masks derived from these bit definitions, writes stop-on-error and message-enable behavior, configures protection trust, sets queue base/size/PI/CI values, and later checks idle or stopped status through masked status fields. Idle-check and reset paths use QMAN status fields to decide whether an MME master QMAN is quiescent.

## State and persistence behavior
The file owns no state. Its masks describe state stored in MME0 QMAN hardware registers. Enable, stop, flush, protection, security property, arbiter, clock-gating, rate-limiter, and queue pointer fields persist in hardware until reprogrammed or reset. Status and error fields reflect live hardware state; some error and dropped-status fields may be sticky until cleared by block-specific mechanisms.

The masks are persistent compile-time interpretation rules. If a mask is wrong, the driver may write the intended address but alter the wrong bits or misread valid hardware state.

## Dependencies and integration points
`mme0_qm_masks.h` is included by `gaudi_regs.h` and used with `mme0_qm_regs.h`. It integrates with Gaudi QMAN setup in `gaudi.c`, security and protection setup in `gaudi_security.c`, MMU ASID programming through `gaudi_mmu_prepare_reg()`, reset/idle flows, and error handling for RAZWI or arbiter failures.

The field layout also lines up with common QMAN logic used by DMA and TPC QMANs: PQF/CQF/CP naming, queue pointer fields, CP fence fields, arbiter fields, and clock-gating/status patterns are shared concepts across generated QMAN blocks. MME-specific consumers must still use the MME0 names and account for the MME0/MME2 master QMAN layout.

## Risks and edge cases
- Shift/mask errors are high impact because they do not change the register address, only the bits touched. Failures may appear as queue hangs, security faults, or missing interrupts.
- `GLBL_CFG0`, `GLBL_CFG1`, and `GLBL_STS0` pack PQF, CQF, CP, and arbiter fields into one register. Read/modify/write paths must preserve unrelated fields.
- Security properties expose ASID and MMBP fields for both secure and non-secure queues. Incorrect masking can route transactions through the wrong address space or bypass intended MMU behavior.
- Status field variants such as `GLBL_STS1` versus `GLBL_STS1_4` and `GLBL_MSG_EN` versus `_4` reflect different queue lanes; treating them as identical can miss lane-specific errors.
- Queue counters and credit fields are width-limited, commonly 16 bits or smaller. Larger software values must be range-checked before packing.
- Arbiter spelling in generated names uses `CHOISE`; consumers must match the generated spelling exactly.

## Test signals
Positive signals include successful MME QMAN initialization, expected `QMAN_MME_ENABLE` behavior, clean idle status after reset, no CP/PQ/CQ read errors, correct stop-on-error behavior when enabled, valid ASID programming after MMU setup, and working command submission through MME queues. Negative signals include stuck `PQ_BUSY` or `CQ_BUSY`, CP undefined-command or WREG errors, fence overflow/underflow bits, arbiter watchdog/overflow errors, RAZWI interrupts from QMAN transactions, unexpected clock-gating state, or idle checks that disagree with actual queue progress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme0_qm_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme0_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme0_qm_regs.h

## Purpose
`mme0_qm_regs.h` is the auto-generated register address map for the Gaudi `MME0_QM` queue-manager block. It defines the MMIO addresses used to configure and inspect MME0's queue-manager global state, producer queues, completion queues, command processors, arbitration, clock gating, local range, rate limiting, indirect APB gateway, and global error capture. This is one of the core contracts behind MME command submission in the Gaudi driver.

## Important APIs, types, and functions
The header exports `mmMME0_QM_*` address macros. Important address groups are:
- Global QMAN registers: `GLBL_CFG0`, `GLBL_CFG1`, `GLBL_PROT`, `GLBL_ERR_CFG`, secure/non-secure property registers, global status registers, and global message-enable registers.
- Producer queue registers for four PQs: `PQ_BASE_LO/HI_0..3`, `PQ_SIZE_0..3`, `PQ_PI_0..3`, `PQ_CI_0..3`, `PQ_CFG0/1_0..3`, `PQ_ARUSER_31_11_0..3`, and PQ status registers.
- Completion queue registers for five CQs: `CQ_CFG0/1_0..4`, `CQ_ARUSER_31_11_0..4`, CQ status, CQ pointer/size/control, pointer/size/control status, and IFIFO counts.
- Command processor registers for five CP lanes: message base address sets 0..3, LDMA offsets, fence read data and counts, CP status, current instruction, barrier config, debug, ARUSER, and AWUSER registers.
- Arbiter registers: configuration, choice queue push/head, WRR weights, master credits and credit increments, slave/master offsets, quiet period, watchdog, slave id, max inflight, AWUSER attributes, base addresses, state/status, error cause/message/drop, and credit status.
- Control tail: CGM config/status, local range base/size, CSMR strict priority, HBW/LBW rate limiters, AXCACHE, indirect APB gateway config/data/status, global error address/data, and memory-init busy.

There are no C functions or types.

## Control flow
The file does not execute code, but `gaudi.c` uses these symbols directly in MME QMAN initialization and runtime support. `gaudi_init_mme_qman()` writes queue base addresses, queue sizes, producer/consumer indices, CP LDMA offsets, error interrupt destination addresses/data, arbiter error message enables, arbiter watchdog timeout, global stop/protection settings, and monitor/SOB message base addresses. `gaudi_init_mme_qmans()` maps MME queue IDs to master QMAN blocks, initializes four upper queues and lower CP lanes, then writes `GLBL_CFG0` to enable MME QMANs. Doorbell logic selects `PQ_PI_0..3` as producer-index registers. Reset and stop paths clear or stop QMANs through `GLBL_CFG0/CFG1`, and idle reporting reads `GLBL_STS0` plus `CGM_STS`.

## State and persistence behavior
The addressed hardware registers hold MME QMAN runtime state. PQ base/size/PI/CI registers describe persistent queue buffers allocated by the driver; CP message bases point at sync-manager monitor and SOB registers; global error address/data persists as the configured interrupt message target; global security properties persist ASID/MMBP setup; arbiter and rate-limiter registers persist scheduling policy and timeout behavior. Status registers expose live queue, CP, arbiter, CGM, and memory-init state.

Software persistence is indirect: `struct gaudi_device.internal_qmans[]` owns the coherent PQ buffers whose DMA addresses are programmed through this register map. If these registers are reset, the driver must reinitialize them before command submission resumes.

## Dependencies and integration points
This header is included by `gaudi_regs.h` and paired with `mme0_qm_masks.h`. Important consumers include:
- `gaudi.c` for MME QMAN initialization, enable/disable, doorbells, idle checks, and error routing.
- `gaudi_security.c` for protection-bit setup over QMAN configuration/status/pointer windows.
- MMU setup code that calls `gaudi_mmu_prepare_reg()` on `GLBL_NON_SECURE_PROPS_0..4`.
- Common command-submission paths that rely on queue PI/CI and persistent queue configuration.

The register map is also used as a template for related MME QMAN blocks. Driver code computes offsets such as `mmMME2_QM_GLBL_CFG0 - mmMME0_QM_GLBL_CFG0` and `MME_QMAN_OFFSET` to reach other MME QMAN instances, so the MME0 layout defines the stride assumptions for more than one hardware block.

## Risks and edge cases
- Address stride assumptions are central. The driver adds queue-lane offsets of `qman_id * 4` and MME-block offsets to MME0 base symbols; any non-uniform register spacing breaks those calculations.
- The header defines four PQ lanes but five CP/CQ lanes. Initialization treats `qman_id < 4` differently from the lower CP lane; new code must preserve that distinction.
- Global error routing writes `GLBL_ERR_ADDR_*`, `GLBL_ERR_WDATA`, and arbiter error enables. Wrong addresses can drop or misroute hardware error interrupts.
- Doorbell code writes `PQ_PI_*`; a wrong PI address can make command submissions invisible or corrupt another queue lane.
- `GLBL_CFG1` stop/flush and `GLBL_CFG0` enable are shared global registers. Uncoordinated writes can stop active CP/PQ/CQ units.
- Protection-bit setup depends on the low bits and page grouping of these addresses. Register relocation can invalidate security masks.
- Indirect APB gateway registers expose secondary access semantics; polling must respect `IND_GW_APB_STATUS` ready/error fields.

## Test signals
Positive signals include successful allocation/programming of internal MME persistent queues, enabled `GLBL_CFG0` for master MME QMANs, command submission advancing PI/CI as expected, lower CP message paths generating sync-manager monitor/SOB writes, valid idle reports from `GLBL_STS0` and `CGM_STS`, clean reset/reinitialize cycles, and MMU ASID programming on non-secure property registers. Negative signals include MME command timeouts, stale PI/CI values, CP current instruction stuck, CP/PQ/CQ read errors, arbiter `CHOISE` watchdog or overflow errors, RAZWI interrupts from QMAN accesses, or protection faults during QMAN setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme0_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme1_ctrl_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme1_ctrl_regs.h

## Purpose
`mme1_ctrl_regs.h` is the auto-generated register address map for the Gaudi `MME1_CTRL` block. It has the same MME prototype and register schema as `mme0_ctrl_regs.h`, but at the MME1 control base around `0xE0000`. The header names MME1 architectural descriptor, command/status/control, rate/power/debug, and shadow descriptor registers so the driver can address the second MME control block explicitly or through per-MME offset arithmetic.

## Important APIs, types, and functions
The exported API is the `mmMME1_CTRL_*` macro namespace. Important groups mirror MME0:
- `ARCH_*` live descriptor registers for tensor S/L/O base addresses, headers, convolution dimensions, iterations, loop strides, ROI sizes, spatial strides, AGU local/remote offsets, sync-object addresses/data, performance events, padding, metadata, and rate limiter saturation.
- Operational registers such as `CMD`, `STATUS1`, `RESET`, `QM_STALL`, `SYNC_OBJECT_FIFO_TH`, `EUS_ROLLUP_CNT_ADD`, `INTR_CAUSE`, `INTR_MASK`, `LOG_SHADOW`, and `PROT`.
- PCU, power, CoreSight debug, TE clock-gate, AGU counter, EZSync, and slave LBW clock-enable registers.
- Four replicated `SHADOW_0` through `SHADOW_3` descriptor banks with the same field families as the live architecture descriptor region.

There are no functions or structs. The file provides stable register names and absolute config-space addresses.

## Control flow
No executable control flow exists in the header. Runtime flow is in consumers. Gaudi initialization and tuning code writes MME rollup counters for MME0 and MME1. Idle reporting in `gaudi.c` reaches MME1 by adding `MME_QMAN_OFFSET`-based offsets to MME0 control/status addresses, then treats MME1 and MME3 as slave MMEs that require MME architecture idle status but not QMAN idle status. Security setup in `gaudi_security.c` includes `mmMME1_CTRL_BASE` in protection-block initialization and uses the MME0 schema to compute register protection masks that apply to corresponding MME control blocks.

Like MME0, actual work execution is descriptor and QMAN driven. This file names the control and descriptor visibility registers for MME1; it does not implement descriptor creation or queue scheduling.

## State and persistence behavior
The file owns no software state. It addresses hardware state in MME1: active descriptor fields, shadow descriptor snapshots, command/status/reset/stall state, interrupt cause/mask state, protection settings, PCU/rate/power controls, debug counters, and AGU/sync counters. Those hardware fields persist until MME reset, device reset, security reprogramming, or explicit driver writes.

The MME1 map is persistent generated data for the ASIC revision. The consistency between `MME0_CTRL` and `MME1_CTRL` layouts is especially important because driver code often reasons about MMEs as repeated engines.

## Dependencies and integration points
This header is included through `gaudi_regs.h`. It integrates with:
- `gaudi.c`, which writes `mmMME1_CTRL_EUS_ROLLUP_CNT_ADD` and reports MME idle state for repeated engines.
- `gaudi_security.c`, which configures protection blocks for `mmMME1_CTRL_BASE`.
- `gaudi_coresight.c`, indirectly through MME1 control block debug bases for STM, ETF, BMON, and SPMU operations.
- MME QMAN setup and reset flows, because MME1 is a slave MME paired with a master QMAN block rather than owning a distinct full QMAN path in the same way as master MMEs.

Consumers must preserve the distinction between MME control block numbering and QMAN master/slave topology. MME1 control status is real even when QMAN status is checked only for master MME indices.

## Risks and edge cases
- The file is almost entirely parallel to MME0 with a different base. Copy/paste assumptions are useful but dangerous if a future generated map introduces a real MME1-only deviation.
- Idle reporting treats odd MMEs as slaves and skips QMAN status for them. If topology changes, this assumption can hide a stuck QMAN or misclassify idle state.
- Security/protection setup relies on block-base protection and MME0-derived field groupings. Register movement in MME1 could require dedicated masks.
- CoreSight register-index arrays must map MME1 debug bases to MME1, not MME0. Base-address drift would make debug tools inspect or program the wrong MME.
- Shadow descriptor registers are repetitive and large; errors can affect debug visibility and protected-register windows without obvious compile-time failures.
- As with MME0, writes to descriptor/control registers are hardware-sensitive and need reset/debug-mode discipline.

## Test signals
Positive signals include MME1 rollup counter programming during initialization, idle reports showing plausible MME1 `ARCH_STATUS`, successful MME workloads involving paired MME engines, no protection faults for allowed MME1 accesses, correct CoreSight targeting of MME1 blocks, and clean reset behavior. Negative signals include MME1 stuck non-idle while its paired master QMAN is idle, protection-bit errors under `MME1_CTRL`, wrong-engine CoreSight trace data, unexpected MME1 interrupts, or mismatched behavior between MME0/MME1 on symmetric workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme1_ctrl_regs.h -->
