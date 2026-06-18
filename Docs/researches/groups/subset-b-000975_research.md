# Research: subset-b-000975

Grouped research for Gaudi TPC1/TPC2/TPC3 configuration and queue-manager register maps under `sources/distributed-fs/ceph-client`. Each section preserves the source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc1_cfg_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc1_cfg_regs.h

## Purpose
`tpc1_cfg_regs.h` is an auto-generated Gaudi ASIC register map for the configuration register space of TPC engine 1. It exposes C preprocessor symbols for the TPC1 tensor descriptors, kernel launch descriptors, scalar register file, execution controls, protection and MMU user attributes, status, interrupt, rate-limit, debug-memory, and MBIST registers. The driver includes these symbols through the generated Gaudi register aggregation headers and uses them as absolute MMIO/config-space offsets for direct `RREG32()`/`WREG32()` access.

## Important APIs, types, and functions
This header defines no functions or types. Its API surface is 603 `#define` constants guarded by `ASIC_REG_TPC1_CFG_REGS_H_`. The register window starts at `mmTPC1_CFG_KERNEL_TENSOR_0_BASE_ADDR_LOW` (`0xE46400`) and ends at `mmTPC1_CFG_QM_SRF_31` (`0xE46E3C`).

The main register families are:
- `mmTPC1_CFG_KERNEL_TENSOR_{0..15}_*`: 16 software-programmed tensor descriptors, each with low/high base address, padding value, tensor config, and five size/stride dimension pairs.
- `mmTPC1_CFG_KERNEL_*`: direct kernel launch metadata, including sync-object message/address, kernel base address, five TID base/size pairs, kernel config/id, and `SRF_{0..31}` scalar register slots.
- `mmTPC1_CFG_ROUND_CSR`, `PROT`, `SEMAPHORE`, `VFLAGS`, `SFLAGS`, `LFSR_POLYNOM`, and `STATUS`: core execution, protection, flag, randomization, and status controls.
- `mmTPC1_CFG_CFG_BASE_ADDRESS_HIGH`, `CFG_SUBTRACT_VALUE`, and `SM_BASE_ADDRESS_HIGH`: address-base controls used to align TPC accesses with the Gaudi config and sync-manager address model.
- `mmTPC1_CFG_TPC_CMD`, `TPC_EXECUTE`, and `TPC_STALL`: command, execute, and halt/stall controls.
- `mmTPC1_CFG_ARUSER_*` and `AWUSER_*`: AXI user/security/MMU attribute registers updated when the driver assigns an ASID.
- `mmTPC1_CFG_LUT_FUNC{32,64,128,256}_BASE_ADDR_*`, `TSB_*`, `DBGMEM_*`, inflight/traffic counters, interrupt cause/mask, and MBIST registers.
- `mmTPC1_CFG_QM_TENSOR_{0..15}_*` and `mmTPC1_CFG_QM_*`: the queue-manager-fed shadow/kernel descriptor area used when QMAN launches work rather than a direct driver-written kernel launch.

## Control flow
The file does not contain executable control flow. It participates in driver control flow whenever Gaudi code computes a TPC configuration offset or programs TPC1-specific state. During TPC QMAN initialization, Gaudi code computes the per-TPC configuration delta from TPC0/TPC1 symbols, then writes `mmTPC0_CFG_SM_BASE_ADDRESS_HIGH + tpc_id * delta`; this file is therefore part of the stride contract that maps TPC ids to their configuration blocks.

Runtime and reset paths use direct TPC configuration symbols when the operation is engine-specific. `gaudi_tpc_stall()` writes `mmTPC1_CFG_TPC_STALL` to stop the TPC execution pipe during teardown/error handling. MMU context setup calls `gaudi_mmu_prepare_reg()` on `mmTPC1_CFG_ARUSER_LO` and `mmTPC1_CFG_AWUSER_LO` to bind non-secure TPC traffic to the selected ASID. State dump support uses TPC0 symbols plus the TPC0/TPC1 delta so TPC1 register spacing must remain identical to the other TPC configuration blocks.

## State and persistence
The header stores no software state. It names hardware state that persists in the TPC1 configuration block until overwritten or reset: tensor descriptors, kernel launch addresses, TID geometry, scalar register file values, execution flags, protection attributes, interrupt masks/status, debug-memory access state, and MBIST controls. The driver's persistent software state is indirect: capability bits such as `HW_CAP_TPC_MASK` decide whether these registers may be touched, and ASID/MMU setup persists through the programmed `ARUSER`/`AWUSER` registers until the next context switch or reset.

## Dependencies and integration points
The header is generated and normally consumed through `include/gaudi/asic_reg/gaudi_regs.h` and related mask headers such as `gaudi_masks.h`. Important integration points include `gaudi.c` TPC initialization, TPC stall handling, state dump offset calculations, direct kernel execution through `gaudi_run_tpc_kernel()`, and MMU preparation through `gaudi_mmu_prepare_reg()`.

The symbols must stay aligned with other TPC configuration headers. TPC1 acts as the stride reference for several loops and offset calculations, such as `mmTPC1_CFG_SM_BASE_ADDRESS_HIGH - mmTPC0_CFG_SM_BASE_ADDRESS_HIGH` and `mmTPC1_CFG_STATUS - mmTPC0_CFG_STATUS`. A bad TPC1 base or a layout divergence would affect not just TPC1 but every loop that derives later TPC register addresses from that delta.

## Risks and edge cases
- The file is auto-generated and should not be edited manually. Any local edit can silently desynchronize the driver from ASIC documentation and generated masks.
- Register names encode hardware ABI. Renaming or deleting constants breaks compile-time references in Gaudi initialization, MMU, reset, and debug paths.
- TPC1 is used as a layout delta reference from TPC0. If only one register offset differs from the TPC0 layout, loop-based programming can write the wrong register for multiple TPC engines.
- `ARUSER`/`AWUSER` programming is security and MMU sensitive. Wrong offsets can make TPC1 issue transactions under the wrong ASID or security attributes.
- `TPC_STALL`, `TPC_EXECUTE`, and kernel base registers are hazardous if used outside reset/init sequencing, because they directly affect execution state.
- The address constants are absolute Gaudi config offsets. Callers that need offsets relative to `CFG_BASE` must subtract it consistently; mixing conventions can target the wrong MMIO location.

## Test signals
Useful signals include successful Gaudi probe with TPC capability bits set, TPC QMAN initialization completing for all engines, state dump reporting coherent TPC1 status, TPC workload submission through `GAUDI_QUEUE_ID_TPC_1_*`, successful reset/teardown without TPC1 stall errors, and MMU context switches that do not produce TPC1 RAZWI/security faults. Negative signals include kernel logs for TPC QMAN errors, TPC1 interrupt causes, invalid ASID/non-secure property behavior, hangs in `gaudi_run_tpc_kernel()`, or state dumps where TPC1 offsets appear shifted relative to TPC0/TPC2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc1_cfg_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc1_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc1_qm_regs.h

## Purpose
`tpc1_qm_regs.h` is an auto-generated Gaudi ASIC register map for the queue manager attached to TPC engine 1. It gives the driver symbolic offsets for global QMAN controls, security properties, producer and completion queues, command processors, fence counters, arbitration, error reporting, clock gating, local range, rate limiting, indirect gateway, and memory-init status. These constants are the hardware contract used by Gaudi command submission, queue initialization, doorbells, error handling, and reset paths.

## Important APIs, types, and functions
This header defines no functions or types. Its API surface is 407 `#define` constants guarded by `ASIC_REG_TPC1_QM_REGS_H_`. The register window starts at `mmTPC1_QM_GLBL_CFG0` (`0xE48000`) and ends at `mmTPC1_QM_GLBL_MEM_INIT_BUSY` (`0xE48D00`).

The main register families are:
- `mmTPC1_QM_GLBL_CFG*`, `GLBL_PROT`, `GLBL_ERR_CFG`, `GLBL_SECURE_PROPS_*`, `GLBL_NON_SECURE_PROPS_*`, `GLBL_STS*`, and `GLBL_MSG_EN_*`: QMAN enable/stop, protection, status, error, message, and security/MMU setup.
- `mmTPC1_QM_PQ_*`: four producer queue base, size, producer index, consumer index, config, AXI user, and status register sets. These include the doorbell registers used by the driver for `GAUDI_QUEUE_ID_TPC_1_0` through `GAUDI_QUEUE_ID_TPC_1_3`.
- `mmTPC1_QM_CQ_*`: five completion queue config, pointer, transfer-size, control, status, and FIFO count register sets.
- `mmTPC1_QM_CP_*`: command processor message base registers, local DMA offsets, fence read-data/counter registers, CP status/current-instruction registers, barrier config, debug, and AXI user attributes.
- `mmTPC1_QM_ARB_*`: arbitration config, WRR weights, master credit tables, choice queue offsets, watchdog, message AXI attributes, base registers, state/status, and error reporting.
- `mmTPC1_QM_CGM_*`, local range, CSMR priority, HBW/LBW rate-limit, global AXCACHE, indirect APB gateway, and global error address/data registers.

## Control flow
The file itself has no runtime branches, but its constants are used throughout TPC1 queue-manager control flow. During TPC QMAN initialization, Gaudi code commonly programs QMANs using TPC0 base symbols plus a per-engine QMAN delta. TPC1 symbols provide that delta through expressions such as `mmTPC1_QM_GLBL_CFG0 - mmTPC0_QM_GLBL_CFG0` and `mmTPC1_QM_CGM_CFG - mmTPC0_QM_CGM_CFG`. This makes the TPC1 QMAN layout the reference for iterating over all TPC QMAN instances.

For explicit TPC1 queue operations, `gaudi_get_dma_desc_list_size()`/doorbell selection logic maps `GAUDI_QUEUE_ID_TPC_1_0` through `GAUDI_QUEUE_ID_TPC_1_3` to `mmTPC1_QM_PQ_PI_{0..3}`. Stop/reset code writes `mmTPC1_QM_GLBL_CFG1` with command-processor stop bits. MMU setup writes the five `mmTPC1_QM_GLBL_NON_SECURE_PROPS_*` registers for ASID propagation. Error setup uses global error address/data and arbitration error-message registers so QMAN RAZWI or arbitration failures can interrupt firmware/CPU paths.

## State and persistence
The header contains no software state. It names persistent hardware state in TPC1_QM: PQ base DMA addresses and indices, CQ pointers and transfer sizes, command-processor fence counters, current instruction pointers, barrier state, arbitration credits, security properties, error targets, and clock-gating configuration. The driver also keeps mirrored software state in `struct gaudi_internal_qman_info` for the persistent queue DMA buffers; these registers bind that software allocation to the hardware QMAN until reset or reinitialization.

## Dependencies and integration points
The header is included through the Gaudi generated register set and paired with field definitions from generated mask headers. Major consumers are `gaudi.c` TPC QMAN initialization, stop, clock-gating disable, command submission doorbells, MMU ASID setup, event/error mapping, and state dump support. Event ids `GAUDI_EVENT_TPC1_QM` and async-id maps identify faults from this block.

The QMAN register layout must remain compatible with common QMAN programming logic shared across DMA, MME, TPC, and NIC blocks. Driver code assumes four external/internal PQ streams plus one lower CP path for TPC QMANs, and it assumes the offset from TPC0 to TPC1 applies cleanly to the rest of the TPC QMAN fleet.

## Risks and edge cases
- TPC1 QMAN is a stride reference for all TPC QMAN loops. A wrong offset can corrupt programming for several engines, not only TPC1.
- Doorbell registers `PQ_PI_*` are directly exposed through queue-id mapping. An incorrect symbol causes submissions to ring the wrong stream or engine.
- Queue base/size registers bind DMA-coherent memory into hardware. Bad offsets or stale values can make the QMAN fetch commands from invalid host/device memory.
- Security registers `GLBL_NON_SECURE_PROPS_*`, `CP_*USER`, `PQ_*USER`, and `CQ_*USER` affect ASID and AXI attributes. Misprogramming can surface as RAZWI, data corruption, or isolation failures.
- Stop bits in `GLBL_CFG1` must be used with reset sequencing. Stopping CP/PQ/CQ at the wrong time can strand in-flight work and leave fence counters inconsistent.
- Arbitration credit/watchdog and error-message registers are low-level hardware controls. Incorrect values can hide QMAN hangs or flood error interrupts.

## Test signals
Positive signals include successful command submission on `GAUDI_QUEUE_ID_TPC_1_0` through `_1_3`, producer/consumer indices moving as expected, completion queues producing entries, TPC1 QMAN stop/reset completing, and absence of `GAUDI_EVENT_TPC1_QM` errors during workloads. Strong negative signals include QMAN RAZWI events, stuck `PQ_CI`/`PQ_PI`, unchanged CP current instruction after doorbells, fence counters not advancing, arbitration error causes, memory-init busy stuck, or failures that move with TPC1 queue-id mappings rather than with the workload itself.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc1_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc2_cfg_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc2_cfg_regs.h

## Purpose
`tpc2_cfg_regs.h` is an auto-generated Gaudi ASIC register map for the configuration register space of TPC engine 2. It mirrors the TPC prototype layout used by TPC1 and TPC3 while moving the window to the TPC2 address range. The file gives the driver symbolic access to TPC2 tensor descriptors, kernel launch descriptors, execution controls, MMU/security attributes, status, interrupts, debug-memory controls, traffic counters, and MBIST registers.

## Important APIs, types, and functions
This header defines no functions or types. Its API surface is 603 `#define` constants guarded by `ASIC_REG_TPC2_CFG_REGS_H_`. The register window starts at `mmTPC2_CFG_KERNEL_TENSOR_0_BASE_ADDR_LOW` (`0xE86400`) and ends at `mmTPC2_CFG_QM_SRF_31` (`0xE86E3C`).

The symbol families match the TPC configuration prototype:
- `mmTPC2_CFG_KERNEL_TENSOR_{0..15}_*`: direct tensor descriptors with base address, padding, config, and five dimension size/stride pairs.
- `mmTPC2_CFG_KERNEL_*`: direct kernel sync-object, kernel base, TID geometry, kernel config/id, and 32 scalar register file entries.
- `mmTPC2_CFG_ROUND_CSR`, `PROT`, `SEMAPHORE`, `VFLAGS`, `SFLAGS`, `STATUS`, `TPC_CMD`, `TPC_EXECUTE`, and `TPC_STALL`: execution and status controls.
- `mmTPC2_CFG_CFG_BASE_ADDRESS_HIGH`, `CFG_SUBTRACT_VALUE`, and `SM_BASE_ADDRESS_HIGH`: config/sync-manager addressing controls.
- `mmTPC2_CFG_ARUSER_*` and `AWUSER_*`: TPC2 MMU/security attributes set during ASID preparation.
- LUT base, TSB, debug memory, inflight/traffic counters, interrupt cause/mask, WQ credits, opcode execution, and MBIST symbols.
- `mmTPC2_CFG_QM_TENSOR_{0..15}_*` and `mmTPC2_CFG_QM_*`: QMAN-fed tensor and kernel descriptor state.

## Control flow
The file has no executable control flow. It is reached through Gaudi driver paths that need TPC2-specific register names or loop-derived TPC register addresses. Reset and teardown paths explicitly write `mmTPC2_CFG_TPC_STALL` to halt TPC2. MMU context setup calls `gaudi_mmu_prepare_reg()` for `mmTPC2_CFG_ARUSER_LO` and `mmTPC2_CFG_AWUSER_LO`. Initialization and state dump code generally use TPC0 plus the TPC0/TPC1 delta, so this file must maintain the same per-register layout as the neighboring TPC configuration headers.

When TPC kernels are run during initialization or reset, `gaudi_run_tpc_kernel()` writes the corresponding `QM_KERNEL_BASE_ADDRESS_*` and execution registers via a per-TPC offset. TPC2 correctness depends on the TPC2 register window matching that computed offset for status, kernel-base, and execution-related fields.

## State and persistence
This file stores no software state. Its constants identify hardware state held in the TPC2 configuration block: tensor metadata, kernel launch data, scalar registers, flags, status, interrupt masks/causes, address translation attributes, debug-memory registers, counters, and MBIST state. Values persist in hardware until reset, context reprogramming, or direct register writes by the driver or firmware.

## Dependencies and integration points
The header is generated and consumed through Gaudi register aggregation headers. It integrates with `gaudi.c` TPC stall/reset handling, MMU ASID setup, TPC kernel execution, state dump support, and capability tracking via `HW_CAP_TPC_MASK`. It also depends structurally on the TPC prototype layout used by TPC0/TPC1/TPC3 and on mask definitions such as `TPC0_CFG_TPC_STALL_V_SHIFT`, which are reused across engines.

## Risks and edge cases
- TPC2 is one instance in a loop-programmed TPC array. A layout mismatch may be hard to diagnose because some code uses explicit TPC2 symbols while other code reaches TPC2 through a computed offset.
- Wrong `ARUSER`/`AWUSER` offsets can bind TPC2 traffic to the wrong ASID/security attributes.
- Wrong `TPC_STALL` or execution register offsets can leave TPC2 running during reset or can stall the wrong hardware block.
- Direct kernel and QMAN-fed kernel descriptor regions are adjacent but semantically distinct; using a direct `KERNEL_*` symbol where a `QM_*` symbol is expected, or the reverse, changes who owns the launch state.
- The generated address range is absolute. Callers must preserve the driver's convention for absolute config offsets versus `CFG_BASE`-relative accesses.

## Test signals
Useful validation includes successful workloads on `GAUDI_QUEUE_ID_TPC_2_*`, clean TPC2 stall/reset behavior, correct TPC2 entries in state dumps, ASID changes that do not trigger TPC2 RAZWI/security errors, and successful initialization kernels when TPC id 2 is exercised. Negative signals include TPC2-specific interrupt causes, queue submissions hanging only on TPC2, state dump offsets that look shifted from TPC1/TPC3, or reset paths reporting that TPC2 did not halt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc2_cfg_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc2_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc2_qm_regs.h

## Purpose
`tpc2_qm_regs.h` is an auto-generated Gaudi ASIC register map for the TPC2 queue manager. It provides the symbolic offsets that bind TPC2 command queues, completion queues, command processors, security properties, arbitration, error reporting, clock gating, rate limiting, local range, and indirect gateway registers to the Gaudi driver. It is the TPC2-specific companion to the shared QMAN programming model used by all TPC engines.

## Important APIs, types, and functions
This header defines no functions or types. Its API surface is 407 `#define` constants guarded by `ASIC_REG_TPC2_QM_REGS_H_`. The register window starts at `mmTPC2_QM_GLBL_CFG0` (`0xE88000`) and ends at `mmTPC2_QM_GLBL_MEM_INIT_BUSY` (`0xE88D00`).

The main register groups are:
- Global configuration, protection, secure/non-secure properties, status, and message enable registers.
- Four producer queue register sets: base low/high, size, producer/consumer index, config, AXI user, and status.
- Five completion queue register sets: config, AXI user, status, pointers, transfer sizes, control, and FIFO counts.
- Command processor message bases, local DMA offsets, fence read-data/counters, status, current instruction, barrier config, debug, and AXI user attributes.
- Arbitration configuration, WRR weights, master credits, choice queue offsets, watchdog, message attributes, base registers, status, and error registers.
- Clock gating, local range, strict priority, HBW/LBW rate limits, AXCACHE, indirect APB gateway, global error address/data, and memory-init busy status.

## Control flow
The header is passive but central to TPC2 queue control. The queue-id mapping in `gaudi.c` maps `GAUDI_QUEUE_ID_TPC_2_0` through `GAUDI_QUEUE_ID_TPC_2_3` directly to `mmTPC2_QM_PQ_PI_{0..3}`, so these constants are the doorbells for TPC2 submissions. Reset code stops TPC2 QMAN by writing `mmTPC2_QM_GLBL_CFG1`; clock-gating code reaches the block through the TPC QMAN stride; MMU setup writes all five `mmTPC2_QM_GLBL_NON_SECURE_PROPS_*` registers.

Initialization usually programs TPC QMAN instances by starting from TPC0 symbols and adding a per-TPC offset. TPC2 must therefore match the QMAN prototype layout exactly, even where explicit TPC2 symbols are not named in the initialization loop.

## State and persistence
The header does not persist software data. It names persistent hardware queue-manager state: producer queue DMA base/size/index values, completion queue pointers, command processor fence and instruction state, arbitration credit tables, security attributes, error targets, local range, rate limits, and clock-gating state. These values are established during device initialization and context setup, then updated by command submission and hardware execution until reset or reinitialization.

## Dependencies and integration points
The file integrates with common Gaudi QMAN setup and command submission in `gaudi.c`, event handling through `GAUDI_EVENT_TPC2_QM`, async id mapping, MMU preparation, state dump data, and reset/stop paths. It depends on generated field masks and on the common TPC QMAN layout shared with TPC0, TPC1, TPC3, and later TPC instances.

## Risks and edge cases
- Doorbell offsets are user-visible indirectly through command submission. A bad `PQ_PI_*` value can make TPC2 workloads appear submitted while no hardware stream is actually rung.
- Queue-memory base and size registers must match the DMA allocations in `struct gaudi_internal_qman_info`; stale or wrong offsets can cause command fetches from invalid memory.
- TPC2-specific explicit symbols and loop-derived offsets must agree. Divergence can create split-brain behavior where initialization succeeds but doorbells, stop, or ASID setup target the wrong block.
- Error-message target registers affect fault delivery. Incorrect global error address/data symbols can hide TPC2 QMAN failures from firmware or report them as another engine.
- Arbitration and clock-gating controls are sensitive during reset; wrong values can leave queues busy or starved.

## Test signals
Positive signals include producer index updates on `GAUDI_QUEUE_ID_TPC_2_*`, completions/fence counters advancing, no `GAUDI_EVENT_TPC2_QM` faults under load, clean QMAN stop during reset, and successful ASID programming without TPC2 RAZWI. Negative signals include TPC2-only queue hangs, CP current instruction stuck after a doorbell, arbitration error causes, memory-init busy never clearing, or completion queues not matching the submitted stream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc2_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc3_cfg_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc3_cfg_regs.h

## Purpose
`tpc3_cfg_regs.h` is an auto-generated Gaudi ASIC register map for the configuration register space of TPC engine 3. It exposes the TPC3 instance of the common TPC configuration prototype: direct and QMAN-fed tensor descriptors, kernel launch controls, scalar register file, execution and stall controls, status and interrupt registers, MMU/security attributes, debug-memory access, counters, and MBIST controls.

## Important APIs, types, and functions
This header defines no functions or types. Its API surface is 603 `#define` constants guarded by `ASIC_REG_TPC3_CFG_REGS_H_`. The register window starts at `mmTPC3_CFG_KERNEL_TENSOR_0_BASE_ADDR_LOW` (`0xEC6400`) and ends at `mmTPC3_CFG_QM_SRF_31` (`0xEC6E3C`).

The important symbol groups are:
- `mmTPC3_CFG_KERNEL_TENSOR_{0..15}_*`: 16 direct tensor descriptors with base, padding, tensor config, and five dimension size/stride pairs.
- `mmTPC3_CFG_KERNEL_*`: direct sync object, kernel base, TID geometry, kernel config/id, and scalar register file entries.
- Core execution and state registers such as `ROUND_CSR`, `PROT`, `SEMAPHORE`, `VFLAGS`, `SFLAGS`, `STATUS`, `TPC_CMD`, `TPC_EXECUTE`, and `TPC_STALL`.
- Addressing and MMU registers including `CFG_BASE_ADDRESS_HIGH`, `CFG_SUBTRACT_VALUE`, `SM_BASE_ADDRESS_HIGH`, `ARUSER_*`, and `AWUSER_*`.
- LUT, TSB, debug-memory, inflight, WQ/HBW/LBW counter, interrupt, WQ credit, opcode, and MBIST registers.
- `mmTPC3_CFG_QM_TENSOR_{0..15}_*` and `mmTPC3_CFG_QM_*`: descriptor and kernel-launch registers used when the QMAN feeds TPC3 work.

## Control flow
No code executes in this header. It supports Gaudi control flow by providing explicit register names for TPC3-specific operations and by preserving the common layout expected by loop-based TPC programming. `gaudi_tpc_stall()` writes `mmTPC3_CFG_TPC_STALL` during stall/reset. MMU setup calls `gaudi_mmu_prepare_reg()` on `mmTPC3_CFG_ARUSER_LO` and `mmTPC3_CFG_AWUSER_LO`. Other paths, including TPC initialization and state dump, can reach TPC3 through offsets derived from TPC0/TPC1 layout assumptions.

Direct TPC kernel execution writes kernel base and execution registers using a per-TPC offset. For TPC3, those computed locations must land on the `QM_KERNEL_BASE_ADDRESS_*`, `STATUS`, and related execution symbols described by this file.

## State and persistence
The file itself is stateless. It describes hardware state that persists in the TPC3 configuration block: descriptors, scalar registers, launch metadata, flags, status, interrupt masks/causes, debug-memory state, counters, ASID/security attributes, and MBIST controls. Driver-owned persistence is indirect through capability bits and current MMU context; hardware register contents are reset or reprogrammed as part of device initialization, context switch, workload launch, and reset.

## Dependencies and integration points
The header is consumed through Gaudi generated register includes and field-mask headers. Integration points include Gaudi TPC stall/reset code, MMU ASID preparation, state dump logic, TPC kernel execution, and workload submission through the TPC3 QMAN. The layout must remain aligned with TPC0/TPC1/TPC2/TPC4+ because the driver frequently uses a single prototype offset to address multiple TPC engines.

## Risks and edge cases
- A TPC3-only base address error can manifest as failures only on `GAUDI_QUEUE_ID_TPC_3_*`, while loop-derived initialization may obscure the source.
- A layout mismatch against TPC0/TPC1 breaks offset-based status, kernel, or sync-manager programming.
- Wrong `TPC_STALL` or execution offsets can leave TPC3 active during reset or prevent initialization kernels from completing.
- Wrong `ARUSER`/`AWUSER` symbols can produce TPC3-specific MMU faults or security violations.
- Direct and QMAN-fed descriptor regions use very similar names; confusing `KERNEL_*` and `QM_*` regions can corrupt the launch path.

## Test signals
Useful validation includes successful command execution on `GAUDI_QUEUE_ID_TPC_3_*`, clean TPC3 stall/reset, no TPC3 RAZWI or interrupt-cause errors during MMU context changes, coherent TPC3 state dump output, and successful initialization kernel execution for TPC id 3. Negative signals include TPC3-only hangs, TPC3 status not changing while queues are rung, shifted state dump offsets, or reset logs indicating TPC3 did not stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc3_cfg_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc3_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc3_qm_regs.h

## Purpose
`tpc3_qm_regs.h` is an auto-generated Gaudi ASIC register map for the TPC3 queue manager. It names the QMAN global, producer queue, completion queue, command processor, arbitration, error, security, clock-gating, local-range, rate-limit, indirect-gateway, and memory-init registers used by the HabanaLabs Gaudi driver to submit and control work on TPC engine 3.

## Important APIs, types, and functions
This header defines no functions or types. Its API surface is 407 `#define` constants guarded by `ASIC_REG_TPC3_QM_REGS_H_`. The register window starts at `mmTPC3_QM_GLBL_CFG0` (`0xEC8000`) and ends at `mmTPC3_QM_GLBL_MEM_INIT_BUSY` (`0xEC8D00`).

The main register families are:
- Global QMAN configuration, protection, error configuration, secure/non-secure properties, status, and message enable registers.
- Four producer queue sets for base, size, producer/consumer index, config, AXI user attributes, and status.
- Five completion queue sets for configuration, AXI user attributes, status, pointers, transfer sizes, control, and FIFO counts.
- Command processor registers for message base addresses, local DMA offsets, fences, status/current instruction, barriers, debug, and AXI user attributes.
- Arbitration registers for WRR weights, master credits, choice queue offsets, watchdog, message attributes, base, state/status, and error status/reporting.
- Clock gating, local range, priority/rate-limit, AXCACHE, indirect APB gateway, global error address/data, and memory-init busy symbols.

## Control flow
The header is passive, but the constants are used directly in TPC3 queue control flow. Command submission maps `GAUDI_QUEUE_ID_TPC_3_0` through `GAUDI_QUEUE_ID_TPC_3_3` to `mmTPC3_QM_PQ_PI_{0..3}` doorbell registers. Reset/stop paths write `mmTPC3_QM_GLBL_CFG1` with CP stop bits. MMU setup writes `mmTPC3_QM_GLBL_NON_SECURE_PROPS_{0..4}`. Error paths rely on TPC3 QMAN error and arbitration message registers to route faults to the CPU/firmware event model.

Initialization logic often reaches TPC3 by applying the common TPC QMAN stride rather than by spelling out every TPC3 symbol. This file must therefore preserve exact prototype register spacing for all queue, CP, arbitration, and global registers.

## State and persistence
The header has no software persistence. It identifies hardware state that lives in TPC3_QM: queue bases and indices, completion pointers and sizes, CP fence/current-instruction state, barrier/debug state, arbitration credits, ASID/security attributes, error routing, rate limits, clock gating, and local range configuration. This state is programmed during initialization and MMU setup, changes as queues run, and is cleared or reinitialized during reset.

## Dependencies and integration points
The file integrates with `gaudi.c` queue initialization, doorbell selection, QMAN stop/reset, clock-gating disable, MMU ASID programming, state dump support, and event handling through `GAUDI_EVENT_TPC3_QM`. It depends on generated mask headers and on the common Gaudi QMAN programming assumptions used for TPC0 through TPC7.

## Risks and edge cases
- Incorrect `PQ_PI_*` symbols can break only TPC3 submissions while leaving other TPC engines healthy.
- Queue base, size, and CP local DMA offset registers must match the command-buffer layout expected by QMAN initialization.
- Security/non-secure property mistakes can show up as TPC3-specific RAZWI or isolation bugs.
- If explicit TPC3 symbols disagree with loop-derived offsets, initialization, doorbells, stop, and ASID setup can target different hardware blocks.
- Arbitration watchdog and error-message registers are critical for diagnosing QMAN stalls; bad offsets can suppress or misroute the errors needed for recovery.

## Test signals
Positive signals include successful execution and completions on `GAUDI_QUEUE_ID_TPC_3_*`, moving producer/consumer indices, advancing CP/fence counters, clean QMAN stop during reset, and no `GAUDI_EVENT_TPC3_QM` errors under representative TPC workloads. Negative signals include TPC3-only queue hangs, stuck CP current instruction, arbitration error causes, memory-init busy stuck, missing completions, or QMAN errors reported under an unexpected engine id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc3_qm_regs.h -->
