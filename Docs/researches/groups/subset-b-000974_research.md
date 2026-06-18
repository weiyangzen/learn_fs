# Research: subset-b-000974

Grouped research report for Gaudi TPC0 configuration and queue-manager register headers. Each section preserves the original source path and is intended to be split into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc0_cfg_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc0_cfg_masks.h

## Purpose

`tpc0_cfg_masks.h` is an auto-generated GPL-2.0 hardware description header for the Gaudi TPC0 configuration block. It exports preprocessor constants for bit shifts and masks used to compose, extract, and validate 32-bit MMIO register values for the Tensor Processing Core configuration aperture. It contains no functions, structs, enums, or executable control flow; its API surface is the macro namespace `TPC0_CFG_*_{SHIFT,MASK}`.

The header is paired with `tpc0_cfg_regs.h`, which supplies the `mmTPC0_CFG_*` register addresses. Driver code combines both families through helpers such as `WREG32`, `RREG32`, `WREG32_FIELD`, and `FIELD_GET` to program kernel descriptors, issue TPC commands, inspect status, handle interrupts, and manage queue-manager supplied kernel launches.

## Important APIs, Types, And Macros

The largest macro group describes 16 `KERNEL_TENSOR_N` descriptors. Each tensor descriptor has low/high base address registers, a padding value register, a `TENSOR_CONFIG` bitfield, and five dimension size/stride pairs. Address, padding, size, and stride values are full-width `V_MASK 0xFFFFFFFF` fields. `TENSOR_CONFIG` uses `DATA_TYPE` bits 0-2, `VALID_DIM_MASK` bits 8-12, `LAST_DIM` bits 16-18, `RMW_SET` bit 19, `RMW_RESERV` bit 20, and `RMW_OP` bits 21-22.

After the kernel tensor block, the file defines execution-context fields: sync-object message/value/operation fields, sync-object address, kernel base low/high address, five TID base and size registers, `KERNEL_CONFIG`, `KERNEL_ID`, and 32 scalar register file (`SRF`) values. `KERNEL_CONFIG` contains `SMALL_VLM`, `ASO_EVICT_L0`, `NUM_VALID_SRFS`, and read/write rate-limit reset token fields.

Core TPC control fields include `ROUND_CSR_MODE`, AXI protection (`PROT_AWPROT`, `PROT_ARPROT`), semaphore, vector/scalar flags, LFSR polynomial, and `STATUS` bits for scalar/vector pipe empty, instruction queue empty, scoreboard empty, queue-manager idle, and queue-manager ready. `TPC_CMD` exposes cache invalidation and prefetch command bits plus `QMAN_STOP`; `TPC_EXECUTE` and `TPC_STALL` are single-bit controls.

Memory-system and diagnostic groups include instruction-cache base addresses, read/write rate-limit enable/saturation/timeout fields, `MSS_CONFIG` cache and exposed-pipe settings, TPC interrupt cause/mask fields, work-queue credits, ARUSER/AWUSER split low/high fields, per-pipe opcode execution fields (`SPU`, `VPU`, `LD`, `ST` operation and enable bits), LUT base address pairs for function sizes 32/64/128/256, TSB sizing/configuration, debug-memory address/data/control/read-complete fields, in-flight and total work-queue counters, IRQ occupancy, and functional MBIST control/pattern/memory result fields.

The final large group mirrors the kernel launch descriptor layout under `TPC0_CFG_QM_*`: 16 `QM_TENSOR_N` descriptors, QM sync-object message/address, QM kernel base address, QM TID ranges, QM kernel config/id, and 32 QM SRF registers. These fields are used when a kernel is launched by the queue manager rather than through direct kernel descriptor programming.

## Control Flow And State

There is no local control flow. The apparent structure is a generated register schema: repeated tensor descriptors first, singleton TPC controls in the middle, then repeated queue-manager kernel descriptors. Runtime state lives entirely in the hardware registers described by the masks. Writes to these fields configure persistent device state until overwritten, reset, or consumed by hardware; reads observe hardware state such as pipe idle bits, interrupt cause bits, debug-memory read-complete status, in-flight counters, MBIST completion/failure state, and queue-manager readiness.

The driver-side control flow that uses these masks is visible in Gaudi integration code. Initialization masks TPC interrupts and sets MSS config fields. Reset/stop paths write stall and queue-manager stop fields. Kernel launch paths program `QM_KERNEL_BASE_ADDRESS`, icache/LUT bases, sync-object address, command bits, poll `STATUS`, then write `TPC_EXECUTE`. Error and interrupt paths read interrupt cause and status masks, then clear latched causes.

## Dependencies And Integration Points

This header depends only on the C preprocessor and include guards. It is consumed through Gaudi ASIC register include trees and driver code under `drivers/accel/habanalabs/gaudi/`. It must remain synchronized with `tpc0_cfg_regs.h`; a field mask is only useful when applied to its matching `mmTPC0_CFG_*` address.

The TPC0-specific names are also used as a prototype for other TPC instances: Gaudi code computes instance offsets such as `mmTPC1_CFG_BASE - mmTPC0_CFG_BASE` or `mmTPC1_CFG_STATUS - mmTPC0_CFG_STATUS` and adds those offsets to TPC0 addresses while continuing to use TPC0 field masks where bit layouts are shared.

Important consumers include interrupt setup (`TPC_INTR_MASK`), TPC status polling (`STATUS_VECTOR_PIPE_EMPTY`, `QM_IDLE`, `QM_RDY`), TPC command issue (`TPC_CMD_ICACHE_INVALIDATE`, `TPC_CMD_ICACHE_PREFETCH_64KB`), execution start (`TPC_EXECUTE`), stall control (`TPC_STALL`), ASID/user-bit preparation (`ARUSER_*`, `AWUSER_*`), and MMIO error/debug paths.

## Risks And Edge Cases

Because this is generated hardware ABI, the main risk is silent mismatch between masks and actual silicon or between masks and register addresses. A wrong shift or mask can corrupt adjacent hardware fields, which is especially risky for command, execute, stall, interrupt mask, ASID/user, and rate-limit fields.

Several fields are full-width and provide no software-side range validation. Callers must enforce semantic constraints such as aligned addresses, valid dimension counts, allowed data-type encodings, valid opcode encodings, and acceptable rate-limit tokens/timeouts. Reserved fields, including sync-object reserved bits and high ARUSER/AWUSER reserved ranges, should not be set accidentally by broad writes.

The generated name `ICACHE_BASE_ADDERESS` is misspelled consistently. Callers must use the generated spelling; attempts to "fix" it locally would break compile-time references unless the register generator is changed everywhere.

Duplicated layouts between `KERNEL_*` and `QM_*` descriptor groups invite off-by-offset mistakes. Direct-kernel and queue-manager launches target different register ranges and should not be interchanged. Polling and clearing status/interrupt fields also requires care because some hardware status bits may be latched or write-one-to-clear according to hardware behavior not represented in this header.

## Test Signals

Build coverage should compile all Gaudi users after any regeneration and catch missing macro names. Static checks can compare every `*_SHIFT`/`*_MASK` pair against generator output and ensure no masks overlap unexpectedly within the same register.

Runtime test signals include successful TPC initialization, correct masking/unmasking of TPC interrupts, queue-manager kernel launch completion, `STATUS` polling reaching vector/scalar/queue idle states, command bits invalidating/prefetching icache without timeout, ASID/user fields matching MMU setup, and error paths reporting expected interrupt causes. Hardware bring-up or emulator tests should validate MBIST result interpretation, debug-memory read completion, and rate-limit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc0_cfg_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc0_cfg_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc0_cfg_regs.h

## Purpose

`tpc0_cfg_regs.h` is an auto-generated register-address map for the Gaudi TPC0 configuration block. It exports `mmTPC0_CFG_*` preprocessor constants that give absolute MMIO addresses for tensor descriptors, kernel launch state, TPC control/status, debug, MBIST, and queue-manager kernel descriptor registers. It contains no functions, types, or runtime logic; the macros are the API.

The address map starts at `0xE06400` for `mmTPC0_CFG_KERNEL_TENSOR_0_BASE_ADDR_LOW` and ends at `0xE06E3C` for `mmTPC0_CFG_QM_SRF_31`. It is paired with `tpc0_cfg_masks.h`, which describes the bitfields stored at these addresses.

## Important APIs, Types, And Macros

The first contiguous region maps 16 direct kernel tensor descriptors. Each tensor occupies 0x38 bytes: base low/high, padding value, tensor config, and five dimension size/stride pairs. Tensor 0 starts at `0xE06400`; tensor 15 ends at `0xE0677C`. The layout is regular and lets code compute descriptor offsets where appropriate, although this header exposes every address as a distinct macro.

Following the tensor descriptors are direct kernel singleton registers: sync-object message/address at `0xE06780` and `0xE06784`, kernel base address low/high, TID base/size pairs for dimensions 0-4, `KERNEL_CONFIG`, `KERNEL_ID`, and `KERNEL_SRF_0` through `KERNEL_SRF_31` at `0xE067C0` through `0xE0683C`.

The central control/status region includes `ROUND_CSR`, `PROT`, `SEMAPHORE`, vector/scalar flags, LFSR polynomial, `STATUS`, config and shared-memory base registers, `TPC_CMD`, `TPC_EXECUTE`, `TPC_STALL`, icache base address registers, read/write rate-limit registers, `MSS_CONFIG`, TPC interrupt cause/mask, work-queue credits, ARUSER/AWUSER low/high registers, `OPCODE_EXEC`, LUT base address pairs, TSB config, debug-memory registers, in-flight/total counters, IRQ occupancy, and MBIST control/pattern/memory registers.

The final region maps queue-manager supplied kernel state. `mmTPC0_CFG_QM_TENSOR_0_BASE_ADDR_LOW` starts at `0xE06A00`, with the same 16-tensor descriptor stride through tensor 15 ending at `0xE06D7C`. It then maps `QM_SYNC_OBJECT_*`, `QM_KERNEL_BASE_ADDRESS_*`, `QM_TID_*`, `QM_KERNEL_CONFIG`, `QM_KERNEL_ID`, and `QM_SRF_0` through `QM_SRF_31` ending at `0xE06E3C`.

## Control Flow And State

There is no local control flow. The header defines stable addresses for hardware state. Software writes these addresses to configure TPC execution and reads them to observe status, counters, interrupts, and debug/MBIST results. Hardware state persists outside the driver and may be modified by hardware execution, reset, queue-manager activity, or direct MMIO writes.

Typical driver flow uses these addresses with offsets for each TPC instance. Gaudi code writes TPC0 addresses directly for TPC0 and computes per-instance offsets for TPC1-TPC7. For queue-managed launches, driver code writes `QM_KERNEL_BASE_ADDRESS`, icache base, LUT base, sync-object address, command bits, waits on `STATUS`, then writes `TPC_EXECUTE`. Initialization and reset flows program interrupt masks, MSS config, shared-memory base high values, stall bits, and queue-manager stop bits.

## Dependencies And Integration Points

The header depends on no other header besides its include guard. It is included by Gaudi driver code through generated ASIC register headers. The paired field definitions in `tpc0_cfg_masks.h` are required for safe read-modify-write operations.

Integration points include `gaudiP.h`, where `TPC_CFG_OFFSET` is derived from TPC instance base-address differences; `gaudi.c` initialization paths that program TPC interrupt masks, MSS configuration, queue-manager sync-object addresses, and shared-memory base values; TPC kernel launch support that writes QM kernel and icache/LUT registers; reset/stall paths that write `TPC_STALL`; and monitoring/error paths that read `STATUS`, `TPC_INTR_CAUSE`, and work-queue counters.

## Risks And Edge Cases

The constants are a hardware ABI. Any accidental address change, truncation, or local edit can direct writes to the wrong hardware register. That is especially hazardous for `TPC_EXECUTE`, `TPC_STALL`, `TPC_CMD`, interrupt registers, protection/user fields, and MBIST/debug controls.

The map contains reserved-looking gaps, such as between SRF and `ROUND_CSR`, and between some singleton blocks. Tests or register walkers must not assume every 4-byte slot in the aperture is valid. Conversely, repeated regions have strict strides; an incorrect stride can land on the next tensor's base register or a different field.

Because other TPCs are addressed by adding offsets to TPC0 macros, the TPC0 map must remain layout-compatible with sibling generated maps. A mismatch in one instance breaks generic loops that assume `mmTPC1_* - mmTPC0_*` deltas are valid for all repeated registers.

## Test Signals

Compile-time signals include successful resolution of all `mmTPC0_CFG_*` references in Gaudi code. Regeneration tests should diff the address map against the authoritative hardware database and verify the direct and QM tensor descriptor strides.

Runtime signals include correct TPC initialization across all TPC instances, no MMIO access faults during register programming, successful TPC kernel launch using QM descriptor registers, status polling that observes expected idle/ready transitions, interrupt causes read and clear at the expected address, and reset/stall flows affecting only the intended TPC instance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc0_cfg_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc0_qm_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc0_qm_masks.h

## Purpose

`tpc0_qm_masks.h` is an auto-generated bitfield header for the Gaudi TPC0 queue manager (`TPC0_QM`, prototype `QMAN`). It exports `TPC0_QM_*_{SHIFT,MASK}` macros used to encode and decode queue-manager MMIO registers. The file contains no functions, types, or executable code; its public interface is the generated macro set.

The queue manager controls producer queues, completion queues, command processors, arbitration, error handling, security properties, rate limiting, clock gating, indirect APB access, and error capture for the TPC0 command path. It is paired with `tpc0_qm_regs.h`, which supplies the `mmTPC0_QM_*` addresses.

## Important APIs, Types, And Macros

Global configuration fields include `GLBL_CFG0` enables for four producer queues (`PQF_EN`), five completion queues (`CQF_EN`), and five command processors (`CP_EN`). `GLBL_CFG1` contains stop and flush fields for the same queue families. `GLBL_PROT` exposes protection fields for PQF, CQF, CP, error, and arbitration paths. `GLBL_ERR_CFG` controls error message enable and stop-on-error behavior for queue families and arbitration.

Security and MMU integration is represented by secure and non-secure property fields for five channels, each carrying a 10-bit `ASID` and an `MMBP` bit. Global status fields expose idle/stop state, read/command/message/write/fence errors, and per-channel message-enable fields. Channel 4 has specialized `GLBL_STS1_4` and `GLBL_MSG_EN_4` naming while sharing most CP/CQ error fields with other channels.

Producer queue fields cover base low/high, size, producer index, consumer index, credit and inflight limits, ARUSER bits, credit/free counts, inflight counts, empty state, and busy state. Completion queue fields mirror credit and inflight controls and add completion queue pointer low/high, target size, control/report fields, status copies of pointer/size/control, and internal FIFO count.

Command processor fields include message base address pairs for four message base regions across five CP channels, LDMA size/source/destination offset fields, four fence read-data increment values, four fence counters, CP status bits (`MSG_INFLIGHT_CNT`, ready bits, software stop, fence id, fence in-progress), current instruction low/high, barrier guard settings, debug state/stall bits, and CP ARUSER/AWUSER upper bits.

Arbitration fields include arbiter type/master/enable/mask/no-stall controls, choice queue push/head values, weighted round-robin weights, clear, master available credits, credit increment and choice offsets, slave enable/quiet/watchdog/id, message max-inflight and AWUSER/security properties, base addresses, state/fullness/message status, error cause/message-enable/drop status, and master credit status. The file uses the generated misspelling `CHOISE` in several macro names.

Power and system integration fields include clock-gating manager thresholds and status (`CGM_CFG`, `CGM_STS`, `CGM_CFG1`), local range base/size, CSMR strict-priority type, HBW/LBW rate-limit token/saturation/timeout/enable fields, global AXCACHE AR/AW fields, indirect gateway APB command/address/write/read/status fields, global error address/write-data capture fields, and memory-initialization busy bits.

## Control Flow And State

There is no local control flow. These masks describe how driver code controls hardware queue-manager state. Writes to enable, stop, flush, credit, pointer, security, rate-limit, and arbitration fields change queue-manager behavior until reset or later writes. Reads from status, counter, error, debug, and busy fields observe hardware progress and failure state.

Gaudi driver initialization programs PQ base/size/index registers, LDMA offsets, error handling, arbitration watchdogs, protection bits, CP message bases, and `GLBL_CFG0` enables. Command submission writes producer queue producer-index doorbells. Reset and stop paths write `GLBL_CFG1` stop bits. Error handling reads `GLBL_STS1_*`, `ARB_ERR_CAUSE`, CP status, and fence information. Power-management paths program or disable clock-gating manager fields.

## Dependencies And Integration Points

The header has only an include guard dependency but is semantically coupled to `tpc0_qm_regs.h` and the Gaudi QMAN driver code. It is used with Linux bitfield helpers and HabanaLabs register access helpers for field writes and reads.

TPC0 masks are reused with offsets for other TPC queue managers. `gaudiP.h` defines `TPC_QMAN_OFFSET` from TPC instance register bases, and `gaudi.c` adds offsets to TPC0 `mmTPC0_QM_*` addresses while using TPC0 bit layouts. This means TPC0 mask correctness affects all TPC queue-manager instances.

Important integration points include command queue initialization, doorbell selection for four TPC PQ streams, MMU ASID preparation through `GLBL_NON_SECURE_PROPS_*`, queue error reporting, completion queue pointer mapping, CP fence monitoring, clock-gating control, and security/protection-bit setup.

## Risks And Edge Cases

The largest risk is field/address mismatch with the hardware database. Queue manager registers often combine multiple queue-family bitmaps in one word, so an incorrect mask can enable, stop, flush, or stop-on-error the wrong queue. Security fields are particularly sensitive: wrong ASID/MMBP or AXUSER values can route DMA under the wrong address space or protection domain.

Several generated spellings, especially `CHOISE`, are part of the macro ABI and should not be normalized by hand. Some channel-specific fields omit producer-queue bits for channel 4, so generic code must respect per-register variants instead of assuming all status registers share identical fields.

Credit, inflight, fence, and counter fields are bounded by masks but not by semantic checks in this header. Driver code must avoid programming invalid queue sizes, overflowing producer indices, enabling queues before bases are valid, clearing errors before diagnostic capture, or interpreting transient busy/idle fields without appropriate polling rules.

The indirect APB gateway has command, ready, and error bits; callers need ordering and timeout logic not represented here. Clock-gating and rate-limit fields can degrade or stall queue progress if programmed incorrectly.

## Test Signals

Compile-time tests should catch missing macro references in Gaudi code. Generator validation should verify that related fields do not overlap and that channel variants match the hardware spec.

Runtime signals include successful TPC queue initialization, correct producer-index doorbell behavior for all four PQs, completion queue pointer/status mapping, CP message-base and fence handling, expected stop/flush behavior during reset, accurate ASID programming, usable arbitration under load, no unexpected `GLBL_STS1` or `ARB_ERR_CAUSE` bits during normal workloads, and clock-gating/rate-limit settings that do not introduce hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc0_qm_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc0_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc0_qm_regs.h

## Purpose

`tpc0_qm_regs.h` is an auto-generated MMIO address map for the Gaudi TPC0 queue manager. It defines `mmTPC0_QM_*` constants for global queue-manager control/status, producer queues, completion queues, command processors, arbitration, clock gating, local range, rate-limit, indirect gateway, error capture, and memory-initialization registers. It contains no functions, types, or executable control flow.

The map starts at `mmTPC0_QM_GLBL_CFG0` address `0xE08000` and ends at `mmTPC0_QM_GLBL_MEM_INIT_BUSY` address `0xE08D00`. Bitfield layout is defined by the paired `tpc0_qm_masks.h` header.

## Important APIs, Types, And Macros

The global register block starts with enable/stop/protection/error configuration and security properties at `0xE08000` through `0xE08034`, then status and message-enable registers through `0xE08068`. It exposes five secure and five non-secure property registers, five status/message-enable channels, and shared global queue state.

Producer queue addresses cover four PQ lanes: base low/high, size, producer index, consumer index, cfg0/cfg1, ARUSER, and status registers. This region runs roughly from `0xE08070` through `0xE0810C` and is used to back command queue storage and doorbell updates.

Completion queue addresses cover five CQ lanes: config, ARUSER, status, pointer low/high, target size, control, status copies of pointer/size/control, and internal FIFO counts. The CQ region starts at `0xE08110` and extends through `0xE08224`.

Command processor addresses cover five CP channels for four message base address pairs, LDMA offsets, four fence read-data and count groups, CP status, current instruction low/high, barrier config, debug, and ARUSER/AWUSER fields. This region spans `0xE08228` through `0xE08440`.

The arbitration block starts at `0xE08A00` and contains arbiter config, choice queue control, WRR weights, clear, 32 master available-credit registers, credit increment, 32 choice push offsets, slave/master controls, message AWUSER/security properties, base addresses, state/fullness/status registers, error cause/message-enable/drop status, and 32 master credit status registers. Later singleton blocks map clock-gating manager registers, local range, CSMR strict priority, HBW/LBW rate limits, global AXCACHE, indirect gateway APB registers, global error capture registers, and memory-init busy.

## Control Flow And State

There is no control flow in the header. These constants name hardware state locations. Driver code writes them to initialize and control the queue manager and reads them for status, debug, and error handling. Hardware updates many of these locations asynchronously as queues drain, command processors fetch commands, fences progress, arbitration credits change, clock-gating state changes, and errors are captured.

Gaudi initialization code uses these addresses to program PQ bases/sizes/indices, CP LDMA offsets and message bases, error registers, arbiter watchdogs, protection, and queue enables. Submission code selects PQ producer-index addresses as doorbells. Monitoring code maps CQ pointer/status registers and PQ consumer indices. Error paths read global status and arbitration error registers and examine CP status/fence fields.

## Dependencies And Integration Points

The header has no compile-time dependency beyond the include guard, but it is semantically coupled to `tpc0_qm_masks.h`. It integrates with register-access helpers and Gaudi per-instance offset logic. `TPC_QMAN_OFFSET` is derived from TPC queue-manager base differences so the TPC0 map acts as the base template for all TPC QMAN instances.

Important integration points include command queue allocation and initialization, PQ doorbell dispatch, CQ mmap/status reporting, CP fence monitoring, MMU ASID property programming, queue-manager stop/reset flows, error reporting, clock-gating configuration, and debug collection. The same address families appear in Gaudi code paths for initialization, reset, command submission, MMU preparation, interrupt/error handling, and idle checks.

## Risks And Edge Cases

The constants are hardware ABI. A wrong address can corrupt unrelated queue-manager state or cause MMIO faults. The risk is highest for producer indices, queue bases/sizes, global enable/stop registers, security properties, CP message bases, fence counters, and arbitration controls.

The register map is not fully contiguous. There are visible gaps before the arbitration block and around selected singleton registers, so generic register dumping or validation must use the explicit macro list rather than assuming every offset is valid. Repeated regions have different lane counts: four PQs, five CQs/CPs, and 32 arbitration master-credit entries. Code that assumes one lane count everywhere can read or write the wrong address.

Some generated names preserve hardware-generator spelling such as `CHOISE`; renaming would break consumers. The map is also used as a base for offsetting other TPC instances, so TPC0 layout mistakes propagate beyond TPC0.

## Test Signals

Compile tests should resolve all `mmTPC0_QM_*` references in Gaudi code. Generator tests should compare the address map against the hardware specification and verify strides for PQ, CQ, CP, and arbitration arrays.

Runtime signals include successful QMAN initialization without MMIO faults, correct command submission through PQ producer indices, CQ status updates at expected addresses, CP fence and current-instruction reporting, expected queue stop/flush behavior, ASID/security properties taking effect, idle checks observing global and clock-gating status, and error handlers reading the intended `GLBL_STS1`, `ARB_ERR_CAUSE`, and global error capture registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc0_qm_regs.h -->
