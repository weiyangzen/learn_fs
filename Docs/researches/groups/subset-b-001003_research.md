# subset-b-001003

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_cmdq_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_cmdq_masks.h

## Purpose

`tpc0_cmdq_masks.h` is the generated bitfield companion for the Goya TPC0 command queue register block. It gives callers the `_SHIFT` and `_MASK` values needed to compose or decode fields in the addresses exported by `tpc0_cmdq_regs.h`.

## Important APIs, Types, and Constants

The exported API is preprocessor constants only. Global command queue fields cover enable, stop, flush, protection, error interrupt/message routing, stop-on-error policy, secure and non-secure ASID/MMBP properties, idle/stop status, and read/write/message error status. CQ fields cover credit limits, max in-flight counts, ARUSER nosnoop/word flags, command pointer/transfer/control fields, status mirrors, FIFO counts, read rate limiter tokens/saturation/timeout, and buffer debug access. CP fields cover four message base address pairs, LDMA source/destination/size/commit offsets, fence read-data increments, fence counters, CP readiness/status, current instruction, barrier guard, and debug byte fields.

## Control Flow

There is no executable control flow. Driver code combines these masks with `WREG32`/`RREG32` register accesses when enabling the command queue, stopping or flushing engines, routing faults, setting message bases, and polling CQ/CP state.

## State and Persistence Behavior

The macros do not hold state. The referenced hardware fields persist in MMIO registers until reset or reprogramming; status and error fields are live hardware observations.

## Dependencies and Integration Points

This header pairs directly with `tpc0_cmdq_regs.h` and follows the generated CMDQ schema also used by other TPC command queues. It integrates with the HabanaLabs Goya queue setup, fault handling, MMU/ASID programming, CP message handling, and fence synchronization paths.

## Risks

Incorrect masks can silently enable the wrong sub-engine, clear or assert the wrong stop/flush bit, misroute errors, or corrupt address fields. The CP status and fence fields are especially sensitive because readiness and synchronization decisions depend on exact bit positions.

## Test Signals

Useful signals are readback of configured enable/protection/error bits, CQ credit and in-flight counters changing under command traffic, rate limiting behavior when enabled, correct CP fence counter increments, and expected idle/stop/error bits during reset and fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_cmdq_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_cmdq_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_cmdq_regs.h

## Purpose

`tpc0_cmdq_regs.h` is the generated MMIO address map for the Goya TPC0 command queue block. It assigns `mmTPC0_CMDQ_*` symbols to command queue global, completion queue, command processor, fence, and debug registers from `0xE09000` through `0xE0930C`.

## Important APIs, Types, and Constants

The file exports register address constants. The global block includes `GLBL_CFG0`, `GLBL_CFG1`, `GLBL_PROT`, `GLBL_ERR_CFG`, captured error address/data registers, secure/non-secure property registers, and global status registers. The CQ region includes configuration, ARUSER, pointer low/high, transfer size, control, status mirror, credit/free/in-flight status, read rate limit controls, IFIFO count, and CQ buffer debug address/data registers. CP addresses include four message base address pairs, LDMA register offsets, four fence read-data/count pairs, CP status, current instruction, barrier config, and debug register.

## Control Flow

This header has no functions. Runtime flow is in the Goya driver: queue initialization writes base/size/control values, CP message base registers, LDMA offsets, and global enable/protection; reset paths write stop/flush controls and poll idle/status addresses; diagnostics read captured error and debug registers.

## State and Persistence Behavior

The file is static generated source. The mapped registers are persistent device state until hardware reset or driver reinitialization, while pointer/status/error registers mutate as the command queue executes work.

## Dependencies and Integration Points

It is consumed with `tpc0_cmdq_masks.h` and common HabanaLabs MMIO helpers. The address map aligns with the replicated TPC command queue layout used by TPC1, TPC2, and TPC3, shifted by each TPC's base address.

## Risks

Address drift breaks command submission or diagnostics. Offsets around CQ pointer/control and CP message/fence registers are high risk because writes may be accepted by hardware but target the wrong queue mechanism.

## Test Signals

Readback after initialization, successful command completion through TPC0 CMDQ, CP fence progress, idle/stop transitions during reset, and valid error-capture addresses/data after injected queue faults are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_cmdq_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_eml_cfg_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_eml_cfg_masks.h

## Purpose

`tpc0_eml_cfg_masks.h` defines the generated bitfields for the TPC0 EML/debug configuration block. The fields describe core debug entry/exit, cache invalidation, breakpoints/watchpoints, trace predicates, timestamp tracing, and debug instruction insertion.

## Important APIs, Types, and Constants

The API is `_SHIFT` and `_MASK` macros. `DBG_CNT` controls debug enter, debug enable, core reset, dcache/icache invalidation, debug exit, single-step, and debug software breakpoint enable. `DBG_STS` exposes debug mode, core ready, during-kernel, cache/QM/WQ/MSS idle, and debug cause. Address/data watch families include program address (`PADD`), vector/scalar pointer address (`VPADD`, `SPADD`), AGU address, AXI HBW/LBW address, scalar data, AXI HBW write data, and AXI LBW write data, each with count, match, enable, and read/write selector fields. RTT fields control tracing predicates, interval generation, timestamp generation, and compression. `DBG_INST_INSERT` and `DBG_INST_INSERT_CTL` define injected instruction and insert trigger fields.

## Control Flow

There are no functions. Debug tooling or driver diagnostics writes enable/match registers, asks the core to enter or leave debug, optionally invalidates caches, and reads status/counters to detect breakpoint or trace events.

## State and Persistence Behavior

The macros are static. The underlying registers configure persistent debug hardware state and counters; status bits and watch counts change as TPC0 executes kernels or debug sequences.

## Dependencies and Integration Points

This header pairs with `tpc0_eml_cfg_regs.h` and complements the general TPC CFG register maps. It integrates with TPC kernel execution, cache control, debug stop/single-step handling, RTT trace collection, and low-level silicon bring-up flows.

## Risks

Bad masks can leave TPC0 held in debug/reset, invalidate the wrong cache path, miss or spuriously trigger watchpoints, or generate malformed trace predicates. Address-width differences across PADD, VPADD, SPADD, AGU, and AXI fields are a common source of truncation bugs.

## Test Signals

Signals include debug enter/exit status, single-step progress, cache-idle status after invalidation, watchpoint counts and match registers updating at expected events, RTT interval/timestamp output, and instruction insertion taking effect only when the insert control bit is asserted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_eml_cfg_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_eml_cfg_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_eml_cfg_regs.h

## Purpose

`tpc0_eml_cfg_regs.h` is the generated MMIO map for the TPC0 EML/debug configuration block at `0x3040000` through `0x3040334`. It names debug control, watchpoint, trace, and instruction insertion registers.

## Important APIs, Types, and Constants

The file exports `mmTPC0_EML_CFG_*` address constants. It starts with debug control/status, eight program-address watch registers and their count/match registers, vector and scalar address watch pairs, AGU address watch pairs, AXI HBW/LBW address watch pairs, scalar data watch registers, 32 AXI HBW write-data watch registers, AXI LBW write-data watch registers, D0 program counter, RTT config/predicate/interval/timestamp registers, and eight debug instruction insertion slots plus an insertion control register.

## Control Flow

This header has no executable logic. A diagnostic path programs watch registers, enables selected match channels, controls debug entry/exit or single-step through the control register, reads status and program counter, and optionally configures trace predicate/timestamp registers.

## State and Persistence Behavior

The source is generated and immutable during runtime. Hardware register contents persist until reset or reconfiguration. Watch counters, debug status, program counter, and trace-related state change as kernels run and debug events occur.

## Dependencies and Integration Points

It is used with `tpc0_eml_cfg_masks.h` and sits alongside TPC CFG/QM/CMDQ registers for Goya TPC0. It is relevant to low-level debugging, silicon validation, kernel tracing, cache reset/invalidation flows, and any tooling that needs TPC0 execution observability.

## Risks

Wrong addresses can program the wrong watch channel or trace control and make debug behavior nondeterministic. The dense sequential watchpoint layout raises off-by-one risk, especially for 0/1 pairs and the 32-entry AXI HBW data array.

## Test Signals

Validation should read back programmed watchpoint addresses/counts, verify debug status changes after enter/exit/single-step, confirm D0 PC sampling, observe trace predicate/timestamp output, and check instruction insertion only through the documented insertion slots and control address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_eml_cfg_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_nrtr_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_nrtr_masks.h

## Purpose

`tpc0_nrtr_masks.h` defines bitfields for the Goya TPC0 north-router/interface router block. The fields configure HBW/LBW credits, debug arbitration, split/rate behavior, address range matching, regulator control, and scrambling.

## Important APIs, Types, and Constants

The exported macros are `_SHIFT` and `_MASK` constants. HBW/LBW max credit fields split write request, write response, read request, and read response credits into 6-bit lanes. Debug arbitration fields encode route weights for east, west, north, south, and local directions, with separate max-credit fields. Split controls include ten split coefficient registers, default mesh selection, forced weak/strong ordering, read/write rate limiter enables, back-to-back optimization, saturation, reset token, and timeout fields. Range fields cover HBW hit bitmap, 8 HBW mask/base low/high pairs, LBW hit bitmap, and 16 LBW mask/base pairs. Regulator fields expose read/write enable and result values. Scrambler fields enable linear and non-linear scrambling.

## Control Flow

There is no code. Initialization or performance-tuning paths write credit/arbitration/range/split fields, while diagnostics read result and range hit fields to understand routing decisions.

## State and Persistence Behavior

Macros are static constants. Router configuration persists in hardware until reset or reprogramming; hit/result fields reflect live or latched routing behavior.

## Dependencies and Integration Points

This header pairs with `tpc0_nrtr_regs.h`. It relates to mesh routing, memory fabric access, HBW/LBW address decoding, QoS/credit tuning, and low-level register programming for TPC0 traffic.

## Risks

Misprogrammed credits or arbitration can deadlock or starve traffic. Incorrect range masks/bases can route memory transactions to the wrong fabric path. Scrambler and ordering bits affect correctness and performance and should be changed only with silicon guidance.

## Test Signals

Test signals include expected HBW/LBW range hit bits for known addresses, no starvation under mixed read/write load, rate limiter saturation/token behavior, regulator result values after read/write enable, and stable traffic behavior with scrambling enabled or disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_nrtr_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_nrtr_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_nrtr_regs.h

## Purpose

`tpc0_nrtr_regs.h` is the generated address map for the Goya TPC0 north router block, covering `0xE00100` through `0xE00604`. It exposes credit, debug arbitration, split/range, regulator, and scrambling registers.

## Important APIs, Types, and Constants

The file exports `mmTPC0_NRTR_*` MMIO addresses. Key groups are HBW/LBW max credit registers, debug arbitration registers for east/west/north/south/local routes and their max-credit controls, ten split coefficient registers, split config and read/write rate limit registers, 8-entry HBW range hit/mask/base tables using low/high components, 16-entry LBW range hit/mask/base tables, regulator control and result registers, and scrambler enable/non-linear scrambler registers.

## Control Flow

There are no functions. Driver or bring-up code writes addresses from this map to configure router topology and address decoding, then reads hit/result/debug registers while validating traffic flow.

## State and Persistence Behavior

Register values are hardware state. Credit/range/split/scrambler configuration remains active until reset or update. Range hit and regulator result registers expose state derived from recent or active routing operations.

## Dependencies and Integration Points

This map is consumed with `tpc0_nrtr_masks.h` and integrates with the Goya TPC0 memory path, mesh/router programming, address range partitioning, and performance or debug controls. It is conceptually related to the later TPC RTR maps, which add fuller HBW/LBW arbitration families.

## Risks

Address-map mistakes can cause traffic misrouting or fabric stalls. Dense range-table addresses are especially risky because an index error may still program a valid neighboring range.

## Test Signals

Validation includes readback of configured credit/range tables, expected range hit indicators for HBW and LBW accesses, successful high-bandwidth and low-bandwidth traffic through TPC0, regulator result changes, and no unexpected timeout/starvation when split rate controls are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_nrtr_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_qm_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_qm_masks.h

## Purpose

`tpc0_qm_masks.h` is the generated bitfield map for the Goya TPC0 queue manager. It defines how to compose and decode fields in TPC0 QM global, producer queue, completion queue, command processor, fence, and debug registers.

## Important APIs, Types, and Constants

The API is macro constants. Global fields cover PQF/CQF/CP/DMA enable, stop, flush, protection, error interrupt/message routing, stop-on-error behavior, error capture data, secure and non-secure ASID/MMBP, idle/stop status, and queue error status. PQ fields cover base low/high, size, PI/CI, credit limit, max in-flight, ARUSER flags, push descriptors (`PUSH0` pointer low, `PUSH1` pointer high, `PUSH2` transfer size, `PUSH3` repeat/control), status counters, busy/empty bits, and read-rate limiter controls. CQ fields mirror config, pointer/size/control, status mirror, credit/free/in-flight counters, busy/empty bits, rate limiter, and IFIFO count. CP fields cover message bases, LDMA offsets, fences, status readiness, current instruction, barrier guard, and debug byte. Buffer debug fields expose PQ/CQ buffer address and read data masks.

## Control Flow

No code is present. Goya queue setup combines these masks with addresses from `tpc0_qm_regs.h` while initializing queues, doorbells, CP messages, fences, protection, and reset stop/flush behavior.

## State and Persistence Behavior

The macros are immutable source. The referenced registers carry persistent queue configuration and live queue/CP state; PI/CI, counters, busy bits, errors, and fences change as workloads run.

## Dependencies and Integration Points

This file pairs with `tpc0_qm_regs.h` and the HabanaLabs QMAN command ABI. It is integrated by Goya queue initialization, MMU ASID setup, command submission, error reporting, reset, and synchronization paths.

## Risks

Field mistakes can break command queueing without a compile error: doorbells can target wrong pointer bits, stop/flush may affect the wrong sub-engine, and ASID/protection masks can compromise isolation. Counter masks must remain aligned with diagnostics.

## Test Signals

Readback after queue setup, working PQ pushes and CQ completions, PI/CI movement, CP fence completion, correct ASID/protection values, expected idle/stop status during reset, and error bits after injected PQ/CQ/CP/DMA faults validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_qm_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_qm_regs.h

## Purpose

`tpc0_qm_regs.h` is the generated MMIO address map for the Goya TPC0 queue manager block. It exports `mmTPC0_QM_*` register addresses from `0xE08000` through `0xE0830C`.

## Important APIs, Types, and Constants

The constants cover global configuration/protection/error/status, PQ base/size/PI/CI/config/ARUSER/push/status/rate-limiter registers, CQ config/pointer/transfer/control/status/rate-limiter/IFIFO registers, CP message base pairs, LDMA offsets, fence read-data and counters, CP status/current instruction/barrier/debug registers, and PQ/CQ buffer debug address/data registers.

## Control Flow

There are no functions. Runtime queue flow is implemented in the Goya driver: allocate/program PQ memory, clear PI/CI, configure credit limits, program CP LDMA and message base addresses, enable the queue manager, ring doorbells through PI or push registers, then poll or interrupt on completion and fence state.

## State and Persistence Behavior

The header is static generated source. MMIO register values persist across driver operations until reset or reconfiguration. Queue pointers, status counters, CP readiness, fences, and error captures are live state tied to command execution.

## Dependencies and Integration Points

It is used with `tpc0_qm_masks.h`, common `WREG32`/`RREG32` accessors, Goya QMAN setup code, MMU ASID programming, interrupt/error routing, and device reset logic. TPC1/TPC2 QM maps replicate the same layout at shifted base addresses.

## Risks

Wrong addresses can corrupt queue state or prevent TPC0 work submission. The tightly packed PQ/CQ/CP regions make incorrect offset derivation dangerous because neighboring registers are valid and side-effecting.

## Test Signals

Signals include readback of queue configuration, successful TPC0 command execution, PI/CI and in-flight counter movement, completion queue status updates, fence counter progress, correct reset idle/stop transitions, and valid global error capture on fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc1_cfg_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc1_cfg_regs.h

## Purpose

`tpc1_cfg_regs.h` is the generated MMIO map for the Goya TPC1 core configuration block, from `0xE46400` through `0xE46E2C`. It describes kernel descriptor, execution control, memory base, interrupt, AXUSER, and MBIST registers for TPC1.

## Important APIs, Types, and Constants

The exported constants are `mmTPC1_CFG_*` addresses. The largest groups are `KERNEL_TENSOR_0..7` and `QM_TENSOR_0..7`, each with base low/high, padding, tensor config, and five dimension size/stride/base-offset triples. Kernel and QM descriptor groups also include kernel base address, five TID base/size pairs, 32 SRF registers, kernel config, and sync object message. The central config area includes round CSR, TBUF base, semaphore, vector/scalar flags, LFSR polynomial, status, config base/subtract, SM base, TPC command/execute/stall, icache base, MSS config, interrupt cause/mask, and TSB config. Tail registers include ARUSER, AWUSER, functional MBIST control/pattern, and ten MBIST memory registers.

## Control Flow

This file has no code. Kernel launch/setup paths program tensor descriptors, kernel code address, TID geometry, SRF values, sync object messages, and execution controls; reset/debug paths use stall/status/interrupt registers.

## State and Persistence Behavior

Register contents are persistent TPC1 execution configuration. Descriptor, SRF, flags, memory base, interrupt mask, and MBIST settings remain until overwritten or reset; status and interrupt cause change as hardware executes.

## Dependencies and Integration Points

The map integrates with Goya TPC queue submission, MMU/ASID AXUSER setup, sync object messaging, interrupt handling, reset/stall logic, and derived `TPC_CFG_OFFSET` calculations that step between TPC instances.

## Risks

Address errors in descriptor tables can make kernels read wrong tensors or execute wrong code. Incorrect TID geometry, SRF, sync object, or AXUSER registers can cause data corruption, missed completions, or isolation faults.

## Test Signals

Signals include descriptor readback, successful kernels on TPC1, correct sync object message writes, expected interrupt cause/mask behavior, stall/execute transitions, memory access under programmed AXUSER values, and MBIST register readback in manufacturing diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc1_cfg_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc1_cmdq_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc1_cmdq_regs.h

## Purpose

`tpc1_cmdq_regs.h` is the generated command queue address map for Goya TPC1. It exports the same CMDQ schema as TPC0 at TPC1 addresses `0xE49000` through `0xE4930C`.

## Important APIs, Types, and Constants

The `mmTPC1_CMDQ_*` constants cover global enable/stop/protection/error/status registers, CQ configuration and pointer/transfer/control registers, CQ status mirrors and counters, read-rate limiter controls, IFIFO count, CP message base pairs, CP LDMA offsets, four CP fence read-data/count pairs, CP status, current instruction, barrier config, debug, and CQ buffer debug address/data registers.

## Control Flow

The header has no executable logic. Driver code uses these addresses when configuring or diagnosing the TPC1 command queue, programming CQ and CP state, enabling the queue, handling reset stop/flush, and reading completion or error state.

## State and Persistence Behavior

The source is generated and static. The mapped registers store TPC1 command queue configuration and live execution state; pointer/status/error/fence fields change as commands are processed.

## Dependencies and Integration Points

It pairs with the CMDQ bit definitions generated for the same prototype and with the Goya MMIO helpers. It aligns with TPC0/TPC2/TPC3 CMDQ maps, so multi-TPC code can derive per-core offsets rather than special-case register layouts.

## Risks

Using a TPC0 address for TPC1 or applying the wrong offset can control the wrong core. CP message base, LDMA offset, and fence addresses are high impact because they govern synchronization and message writes.

## Test Signals

Readback of TPC1 CMDQ configuration, TPC1 command completion, CQ counter movement, CP readiness/fence progress, reset idle/stop status, and captured error address/data after fault injection validate this address map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc1_cmdq_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc1_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc1_qm_regs.h

## Purpose

`tpc1_qm_regs.h` is the generated MMIO address map for the Goya TPC1 queue manager, covering `0xE48000` through `0xE4830C`. It is the TPC1 instance of the QMAN prototype.

## Important APIs, Types, and Constants

The `mmTPC1_QM_*` constants include global config/protection/error/status registers, PQ base/size/PI/CI/config/ARUSER/push/status/rate limit registers, CQ config/pointer/transfer/control/status/rate limit/IFIFO registers, CP message base pairs, LDMA offsets, fence read-data and counters, CP status/current instruction/barrier/debug, and PQ/CQ buffer debug access registers.

## Control Flow

This header contains no functions. Goya initialization and command submission code writes these addresses to configure TPC1 queues, program CP message and LDMA behavior, enable/stop/flush the QMAN, submit work, and read completion or fault state.

## State and Persistence Behavior

Register values hold persistent queue configuration and live queue state for TPC1. PI/CI, credit counters, CP status, fences, and error captures mutate during workload execution and reset.

## Dependencies and Integration Points

It integrates with QMAN masks, Goya queue setup, MMU ASID programming, doorbell mapping, interrupt/fault handling, and reset logic. It shares layout with TPC0 and TPC2 queue manager maps at different base addresses.

## Risks

Wrong register addresses can submit commands to the wrong TPC, corrupt TPC1 queue pointers, or misconfigure CP message/fence handling. Because all addresses are valid MMIO, many mistakes surface as hardware hangs rather than immediate software failures.

## Test Signals

Signals include successful TPC1 queue initialization, PI/CI and credit counter movement, CQ completion updates, CP fence increments, expected global idle/stop states during reset, and correct ASID/protection readbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc1_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc1_rtr_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc1_rtr_regs.h

## Purpose

`tpc1_rtr_regs.h` is the generated address map for the Goya TPC1 router block, from `0xE40100` through `0xE40604`. It exposes HBW/LBW arbitration, split/rate, range decoding, regulator, and scrambling controls.

## Important APIs, Types, and Constants

The `mmTPC1_RTR_*` constants include HBW read-request, read-response, write-request, and write-response arbitration registers for east/west/north/south/local routes, plus HBW max-credit controls. LBW has equivalent route arbitration and max-credit groups. Debug arbitration and max-credit groups follow, then ten split coefficients, split config, read/write saturation, token and timeout controls, 8 HBW range mask/base low/high entries with hit indicator, 16 LBW range mask/base entries with hit indicator, regulator control/result registers, and scrambler enable/non-linear scrambler registers.

## Control Flow

No executable control flow is present. Router setup code writes arbitration weights, credits, range tables, rate controls, and scrambling options; diagnostics read hit/debug/result registers during traffic tests.

## State and Persistence Behavior

The registers retain routing configuration until reprogrammed or reset. Hit/result/debug fields expose live or latched router observations tied to memory traffic.

## Dependencies and Integration Points

This map integrates with Goya TPC1 memory fabric access, HBW/LBW routing, mesh topology, performance tuning, and silicon validation. It complements TPC1 CFG/QM/CMDQ maps by defining the memory path around the core.

## Risks

Incorrect arbitration or credits can starve directions or hang traffic. Range table mistakes can route transactions to the wrong memory path. Split and scrambling controls can affect ordering, latency, and data-path assumptions.

## Test Signals

Expected HBW/LBW range-hit bits, sustained bidirectional traffic without stalls, arbitration fairness under mixed route load, timeout behavior when rate limiters are enabled, regulator result readback, and correct operation with scrambling settings are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc1_rtr_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc2_cfg_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc2_cfg_regs.h

## Purpose

`tpc2_cfg_regs.h` is the generated configuration register map for Goya TPC2, covering `0xE86400` through `0xE86E2C`. It is the TPC2 instance of the TPC core descriptor/control schema.

## Important APIs, Types, and Constants

The file exports `mmTPC2_CFG_*` addresses. It contains kernel and QM tensor descriptor banks for tensors 0 through 7, each with base address, padding, tensor config, and five dimensions of size/stride/base offset. It also maps kernel/QM base addresses, TID base and size for five dimensions, 32 SRF registers, kernel config, sync object message, round CSR, TBUF base, semaphore, vector/scalar flags, LFSR polynomial, status, config and SM base registers, TPC command/execute/stall, icache base, MSS config, interrupt cause/mask, TSB config, ARUSER/AWUSER, and functional MBIST registers.

## Control Flow

There is no code. Driver launch flow programs descriptors and execution registers before TPC2 work is run, while interrupt/reset flows use status, interrupt, stall, and execute registers.

## State and Persistence Behavior

The mapped registers hold TPC2 kernel launch state and core configuration until overwritten or reset. Status and interrupt cause fields are live hardware state.

## Dependencies and Integration Points

It integrates with Goya TPC queue execution, sync object messaging, MMU AXUSER/ASID preparation, TPC reset/stall handling, and offset-based multi-TPC programming derived from the TPC0/TPC1 layout.

## Risks

Descriptor or address mistakes can point TPC2 at wrong tensor, kernel, or shared memory regions. Incorrect sync object or interrupt mapping can make command completion unreliable.

## Test Signals

Signals include descriptor readback, TPC2 kernel execution, correct sync object completion, interrupt cause/mask behavior, TPC stall/execute transitions, AXUSER-tagged memory access, and MBIST control/memory register diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc2_cfg_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc2_cmdq_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc2_cmdq_regs.h

## Purpose

`tpc2_cmdq_regs.h` is the generated command queue MMIO map for Goya TPC2. It exports `mmTPC2_CMDQ_*` addresses from `0xE89000` through `0xE8930C`.

## Important APIs, Types, and Constants

The address families include global configuration/protection/error/status, CQ configuration/ARUSER/pointer/transfer/control/status/rate-limiter/IFIFO registers, CP message base address pairs, LDMA offsets, fence read-data and counter registers, CP status/current instruction/barrier/debug, and CQ buffer debug address/data registers.

## Control Flow

No functions are defined. Goya queue code uses these constants to program and control the TPC2 command queue, including CQ setup, CP message/fence setup, stop/flush during reset, and error/status reads.

## State and Persistence Behavior

Hardware register values persist until reset or driver updates. CQ pointers/status, CP readiness, current instruction, fences, and error capture registers change while TPC2 commands execute.

## Dependencies and Integration Points

It pairs with CMDQ field masks and aligns with the replicated CMDQ layout for other TPC instances. Integration points are command submission, queue diagnostics, reset, fault handling, and synchronization paths.

## Risks

Using the wrong TPC command queue base can control another core. Misaddressing CP LDMA, message, or fence registers can break command processor progress and completion signaling.

## Test Signals

Readback of configured TPC2 CMDQ registers, command completion, CQ in-flight/free counter changes, CP fence progress, idle/stop status during reset, and expected captured error address/data under fault injection validate the map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc2_cmdq_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc2_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc2_qm_regs.h

## Purpose

`tpc2_qm_regs.h` is the generated address map for the Goya TPC2 queue manager block, spanning `0xE88000` through `0xE8830C`.

## Important APIs, Types, and Constants

`mmTPC2_QM_*` constants cover global QMAN control/protection/error/status, producer queue base/size/PI/CI/config/ARUSER/push/status/rate limit registers, completion queue config/pointer/transfer/control/status/rate limit/IFIFO registers, command processor message base pairs and LDMA offsets, four fence read-data/count pairs, CP status/current instruction/barrier/debug, and PQ/CQ buffer debug address/data registers.

## Control Flow

There is no executable code. The driver uses this map to initialize TPC2 queue memory, configure CP message and LDMA behavior, enable the queue manager, submit work through PI/push registers, and inspect completion/error state.

## State and Persistence Behavior

The MMIO registers hold persistent queue configuration and live execution state. Queue pointers, counters, CP state, fences, and global error status mutate as commands are submitted, completed, or reset.

## Dependencies and Integration Points

It is consumed with QMAN masks and common HabanaLabs MMIO routines. It integrates with TPC2 command submission, MMU ASID properties, doorbell lookup, synchronization, interrupt/fault reporting, and reset handling.

## Risks

Address mistakes can corrupt TPC2 queue metadata, send doorbells to the wrong register, or hide queue faults. CP message and fence registers are critical for completion signaling.

## Test Signals

Validation includes TPC2 queue initialization readback, successful command execution, PI/CI movement, PQ/CQ counter changes, CP fence increments, correct global idle/stop status, and expected error captures on injected queue faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc2_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc2_rtr_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc2_rtr_regs.h

## Purpose

`tpc2_rtr_regs.h` is the generated router register map for Goya TPC2, covering `0xE80100` through `0xE80604`. It provides the TPC2 HBW/LBW fabric arbitration and address routing controls.

## Important APIs, Types, and Constants

The file exports HBW read-request/read-response/write-request/write-response arbitration registers for east, west, north, south, and local directions, HBW max-credit registers, equivalent LBW arbitration and max-credit registers, debug arbitration and max-credit registers, split coefficient/config/rate registers, HBW range hit plus 8 mask/base low/high entries, LBW range hit plus 16 mask/base entries, regulator control/read/write result registers, and scrambler enable/non-linear scrambler addresses.

## Control Flow

There are no functions. Router setup code writes arbitration weights, credits, split parameters, range tables, and scrambling controls; validation code reads range-hit, debug, and regulator result registers while traffic runs.

## State and Persistence Behavior

The registers are persistent hardware configuration until reset or reprogramming. Hit/result registers are live or latched state generated by TPC2 router traffic.

## Dependencies and Integration Points

It integrates with TPC2 memory traffic, HBW/LBW fabric routing, mesh topology tuning, performance debug, and low-level silicon validation. The schema matches TPC1 RTR with a TPC2 base address shift.

## Risks

Incorrect ranges can route memory traffic incorrectly. Credit or arbitration mistakes can starve traffic or create stalls. Split and scrambler settings may affect ordering and observability.

## Test Signals

Expected range-hit bits for known HBW/LBW addresses, sustained traffic under mixed directions, arbitration fairness, timeout/rate behavior, regulator result readback, and stable operation with selected scrambler settings validate the map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc2_rtr_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc3_cfg_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc3_cfg_regs.h

## Purpose

`tpc3_cfg_regs.h` is the generated TPC3 core configuration MMIO map, from `0xEC6400` through `0xEC6E2C`. It names descriptor, execution, memory, interrupt, AXUSER, and MBIST registers for the fourth Goya TPC instance.

## Important APIs, Types, and Constants

The `mmTPC3_CFG_*` constants include kernel tensor descriptors and QM tensor descriptors for tensors 0 through 7, with address, padding, tensor config, and five-dimensional geometry fields. It also includes kernel/QM kernel base, TID base/size for dimensions 0 through 4, 32 SRF registers, kernel config, sync object message, round CSR, TBUF base, semaphore, VFLAGS/SFLAGS, LFSR polynomial, status, config base/subtract, SM base, TPC command/execute/stall, icache base, MSS config, TPC interrupt cause/mask, TSB config, ARUSER/AWUSER, and functional MBIST control/pattern/memory registers.

## Control Flow

No executable logic is defined. Launch code programs descriptors and execution controls before TPC3 runs; reset and interrupt code uses stall, status, execute, interrupt cause, and mask addresses.

## State and Persistence Behavior

Register contents are persistent TPC3 launch and core state until reset or reprogramming. Status and interrupt-cause registers reflect live hardware execution.

## Dependencies and Integration Points

This map integrates with Goya TPC queue submission, MMU AXUSER/ASID setup, sync object completion, TPC interrupt handling, reset/stall control, and offset-based code that treats TPC CFG instances as replicated blocks.

## Risks

Wrong descriptor addresses can make TPC3 execute with incorrect tensors, code, TID geometry, or SRF data. Incorrect AXUSER, sync message, or interrupt registers can cause isolation failures or missed completion.

## Test Signals

Signals include descriptor readback, successful TPC3 kernels, expected sync object writes, interrupt cause/mask behavior, stall/execute transitions, correct memory access under programmed AXUSER settings, and MBIST diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc3_cfg_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc3_cmdq_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc3_cmdq_regs.h

## Purpose

`tpc3_cmdq_regs.h` is the generated command queue MMIO map for Goya TPC3. It exports `mmTPC3_CMDQ_*` addresses from `0xEC9000` through `0xEC930C`.

## Important APIs, Types, and Constants

The constants define global command queue configuration/protection/error/status registers, CQ configuration and pointer/transfer/control/status/rate-limiter/IFIFO registers, CP message base pairs, CP LDMA offsets, fence read-data and counters, CP status, current instruction, barrier config, debug register, and CQ buffer debug address/data registers.

## Control Flow

There is no code in this header. Driver paths use the addresses to configure the TPC3 command queue, enable or stop/flush it, program CP message and fence behavior, and read status or captured errors.

## State and Persistence Behavior

The generated file is static source. The mapped registers hold persistent queue configuration and live command processor/completion state for TPC3 until reset or reprogramming.

## Dependencies and Integration Points

It pairs with CMDQ field masks for the shared prototype and common HabanaLabs register accessors. It integrates with TPC3 command submission, reset, synchronization, and fault handling and mirrors the TPC0/TPC1/TPC2 CMDQ layout at the TPC3 base address.

## Risks

Address errors can control the wrong queue or leave TPC3 unable to process commands. CP message, LDMA, fence, and CQ pointer/control registers are high risk because they directly affect completion and synchronization.

## Test Signals

Validation includes readback of programmed TPC3 CMDQ registers, successful TPC3 command execution, CQ counter and pointer status changes, CP fence progress, idle/stop state during reset, and expected error capture on injected command queue faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc3_cmdq_regs.h -->
