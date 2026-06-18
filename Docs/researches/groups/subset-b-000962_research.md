# Research Report: subset-b-000962

Grouped research for HabanaLabs Goya/Gaudi security, queue-manager, CPU-interface, and DMA register interface files. Each section is delimited for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/goya/goya_security.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/goya/goya_security.c

## Purpose

`goya_security.c` programs the Goya ASIC security model during device bring-up. It configures two related mechanisms: address-range protection for DMA/MME/TPC routing paths, and per-register protection bits inside 4 KiB configuration-register blocks. The exported entry point is `goya_init_security()`, which writes low-bandwidth and high-bandwidth range filters, then calls the protection-bit initializers. `goya_ack_protection_bits_errors()` exists as an exported hook but is currently empty.

## Important APIs, Types, and Functions

The file depends on `struct hl_device` and `struct goya_device` from the HabanaLabs driver, register definitions from `goya_regs.h`, and MMIO helpers/macros such as `WREG32`, `lower_32_bits`, `upper_32_bits`, `CFG_BASE`, `DRAM_PHYS_BASE`, `PROT_BITS_OFFS`, and `DMA_MACRO_LBW_RANGE_BASE_R_MASK`.

`goya_pb_set_block()` computes the protection-bit shadow address for a register block from `base - CFG_BASE + PROT_BITS_OFFS` and writes zeroes through the protection-bit area until the address reaches a 4 KiB boundary. In this hardware model, a protection bit value of zero marks the corresponding register as protected.

`goya_init_mme_protection_bits()`, `goya_init_dma_protection_bits()`, and `goya_init_tpc_protection_bits()` carve out large lists of MME, DMA, and TPC registers. They protect whole routing/regulator/memory blocks using `goya_pb_set_block()`, then compute word offsets and bit masks for selected registers such as queue-manager globals, PQ/CQ descriptors, CP message base registers, debug-memory registers, semaphore/status/config registers, ARUSER/AWUSER controls, and interrupt mask/status registers.

`goya_init_protection_bits()` is the top-level per-register protection setup. It protects PCIe, SRAM banks, PCIe subblocks, TPC PLL, MME, DMA, and TPC areas, and documents the bit layout used to map a register address to a protection-bit word and bit.

`goya_init_security()` programs range-protection registers for the DMA macro, MMEs, and TPC routers. It defines 14 low-bandwidth register ranges and high-bandwidth host/DDR ranges, taking `HW_CAP_MMU` into account for DMA host protection.

## Control Flow

Initialization starts in `goya_init_security()`. It derives DRAM low/high address words from `DRAM_PHYS_BASE` and masks each hard-coded LBW range through `DMA_MACRO_LBW_RANGE_BASE_R_MASK`. It first enables range-hit blocking on DMA macro LBW/HBW paths. If the MMU capability is not initialized, DMA HBW range 0 is used to protect host space; range 1 protects the first 512 MiB of DDR. It then writes all LBW range base/mask pairs into the DMA macro.

The same host/DDR/LBW range pattern is repeated for MME router blocks 1 through 6 and TPC router blocks 0 through 7. Each engine gets LBW hit blocking (`0xFFFF`) and HBW hit blocking (`0xFE`) plus host range 0, DDR range 1, and all 14 LBW ranges. After range setup, `goya_init_security()` calls `goya_init_protection_bits()`, which dispatches to the MME, DMA, and TPC protection-bit helpers.

The protection-bit helpers are mostly straight-line MMIO writes. For individual allow-list words, the code computes `pb_addr = (reg & ~0xFFF) + PROT_BITS_OFFS`, `word_offset = ((reg & PROT_BITS_OFFS) >> 7) << 2`, and `mask = 1 << ((reg & 0x7F) >> 2)` for each register in the same protection word. It then writes `~mask`, meaning the selected registers remain unprotected while other bits in that word are protected. Whole-block protection writes zeroes over the block's protection-bit tail.

## State and Persistence Behavior

There is no heap allocation, persisted kernel state, or software data structure mutation beyond reading `goya->hw_cap_initialized`. The meaningful state is hardware state in memory-mapped registers. Once written, the range and protection-bit registers persist in the device until reset or later reprogramming. Because most writes are one-way configuration during initialization, ordering matters: later protection-bit writes can make future software access to some registers impossible unless the intended allow-list is correct.

## Dependencies and Integration Points

This file integrates with Goya ASIC initialization through the exported `goya_init_security()` symbol, and it assumes the register map in `include/goya/asic_reg/goya_regs.h` matches the silicon. It also depends on common HabanaLabs device capability tracking: if `HW_CAP_MMU` is absent, DMA host protection is programmed explicitly; otherwise the MMU path is expected to provide the host isolation. The range values also integrate with the driver's DRAM base model and with firmware/security settings that define accessible host and device address windows.

## Risks

The highest risk is stale or incorrect register constants. A wrong address, mask, or engine copy-paste entry can either expose privileged registers or block a register required for normal initialization, queue operation, interrupt handling, debug, or error recovery. The repeated MME/TPC/DMA blocks are difficult to audit and easy to drift across engines. The inverted protection-bit writes are also subtle: a mistaken mask polarity changes the security meaning. `goya_pb_set_block()` relies on block-aligned assumptions and the protection-bit tail layout; if `base` is outside the expected CFG window or the hardware layout changes, it can write unintended registers. `goya_ack_protection_bits_errors()` being empty means there is no visible recovery path here for protection-bit fault acknowledgement.

## Test Signals

Useful validation signals include successful device probe after `goya_init_security()`, working DMA/MME/TPC queue bring-up, no unexpected RAZWI/security faults during normal workloads, and expected faults when protected host/register/DDR ranges are accessed by unauthorized engines. Hardware or simulator tests should read back representative range registers and protection-bit words, especially for each repeated MME/TPC/DMA engine. Regression tests should cover both MMU-enabled and MMU-disabled initialization paths, and should include negative tests for register access that should be blocked after protection-bit programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/goya/goya_security.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/common/qman_if.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/common/qman_if.h

## Purpose

`qman_if.h` defines the host-visible queue-manager data structures shared by HabanaLabs software and hardware queue managers. It describes the primary queue buffer descriptor (`struct hl_bd`) and completion queue entry (`struct hl_cq_entry`) layouts, along with the bit fields used by software and hardware in their control/status words.

## Important APIs, Types, and Constants

`struct hl_bd` contains a little-endian 64-bit pointer, 32-bit length, and 32-bit control word. `HL_BD_SIZE` exposes the descriptor size for queue allocation and hardware programming. The BD software control fields include `BD_CTL_REPEAT_VALID_*` and `BD_CTL_SHADOW_INDEX_*`; hardware completion-related fields include `BD_CTL_COMP_OFFSET_*` and `BD_CTL_COMP_DATA_*`.

`struct hl_cq_entry` contains one little-endian 32-bit data word. `HL_CQ_ENTRY_SIZE` exposes its size. Completion fields include `CQ_ENTRY_READY_*`, `CQ_ENTRY_SHADOW_INDEX_VALID_*`, and `CQ_ENTRY_SHADOW_INDEX_*`, with the shadow-index location deliberately matching the BD shadow-index field.

The use of `__le64` and `__le32` is part of the ABI: queue memory is little-endian regardless of host CPU representation, and driver code must use the corresponding conversion helpers when constructing or reading descriptors.

## Control Flow

This header has no executable control flow. Runtime behavior appears in users such as Gaudi queue setup and submission paths. For example, `gaudi_pqe_write()` treats a `struct hl_bd` as two 64-bit words and copies it into a primary queue entry because the queue lives in host memory. Producer code fills BD fields, rings a queue doorbell or writes a PI register, and hardware later consumes the BD. Completion consumers read `struct hl_cq_entry`, check the ready bit, optionally use the shadow-index-valid and shadow-index fields, and then advance queue state.

## State and Persistence Behavior

The structures define persistent queue memory content shared between the host driver, firmware/CP, and ASIC queue hardware. The header itself owns no state, but any layout change would alter the hardware ABI for in-memory descriptors. BD and CQ words persist in coherent DMA buffers or CPU-accessible memory until overwritten by producer/consumer queue logic.

## Dependencies and Integration Points

The file depends only on `<linux/types.h>`. It is integrated into device-specific queue code through the common HabanaLabs queue abstraction and is used by Gaudi/Goya-style queue managers that program PQ/CQ base addresses and sizes using ASIC register headers. The shadow-index fields tie software bookkeeping to hardware completions, while completion offset/data fields let command processors emit completion writes.

## Risks

The key risk is ABI mismatch. Structure packing, endianness, or bit-field constant changes can break descriptor parsing by hardware. The file intentionally avoids C bitfields, which is good for ABI stability, but callers must still mask and shift correctly. Because `gaudi_pqe_write()` copies the descriptor as raw 64-bit words, any future change to descriptor size or alignment would need coordinated updates.

## Test Signals

Queue-submission tests should verify that BD sizes match hardware expectations, descriptors are written little-endian, completions set `CQ_ENTRY_READY_MASK`, and shadow-index values round-trip correctly. Stress tests should cover queue wraparound, repeated BD handling when `BD_CTL_REPEAT_VALID_MASK` is set or clear, and mixed command streams that generate completion data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/common/qman_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/cpu_if_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/cpu_if_regs.h

## Purpose

`cpu_if_regs.h` is an auto-generated Gaudi CPU interface register map. It gives symbolic names to MMIO offsets under the CPU_IF block so driver code can configure host/firmware queues, AXI attributes, counters, and interrupt/status registers without embedding raw addresses.

## Important APIs, Types, and Constants

The header exports only `#define` constants. Major groups are AXI/user override registers (`mmCPU_IF_ARUSER_OVR`, `AWUSER_OVR`, `AXCACHE_OVR`, `LOCK_OVR`, `PROT_OVR` and enable controls), outstanding and response controls (`MAX_OUTSTANDING`, `EARLY_BRESP_EN`, `FORCE_RSP_OK`, `CPU_MSB_ADDR`), queue interface registers (`PF_PQ_PI`, PQ/CQ/EQ base low/high, lengths, EQ read offset, and `QUEUE_INIT`), and error/interrupt groups for TPC, DMA, SRAM, NIC, DMA_IF, HBM, PLL, and SEI paths.

## Control Flow

The header has no runtime control flow. It is consumed by Gaudi initialization code. CPU bring-up writes `mmCPU_IF_CPU_MSB_ADDR` when firmware security does not own that setting. CPU queue initialization writes PQ, EQ, and CQ base addresses, queue lengths, EQ read offset, PF PQ producer index, and `mmCPU_IF_QUEUE_INIT`, then polls `QUEUE_INIT` until firmware reports host readiness. Runtime event handling updates `mmCPU_IF_EQ_RD_OFFS` as the event queue consumer index advances.

## State and Persistence Behavior

The constants map to hardware registers that persist until reset or reinitialization. The queue base/length registers define shared-memory queue placement, `PF_PQ_PI` is mutable queue producer state, and `EQ_RD_OFFS` is mutable event-queue consumer state. Interrupt status/mask/clear registers hold fault and error state for multiple hardware blocks. The header itself holds no software state.

## Dependencies and Integration Points

This generated file is included by Gaudi driver code through the ASIC register include set. It integrates with firmware loader data (`cpu_dyn_regs`), queue allocation (`hdev->kernel_queues`, `hdev->event_queue`, and CPU-accessible memory), and GIC/MSI interrupt setup. It also sits next to mask headers that define bit positions for related control/status registers.

## Risks

Generated register maps are high blast-radius dependencies: an incorrect address silently redirects MMIO writes. Queue base/length mistakes can make firmware read or write the wrong memory, while wrong interrupt status or clear addresses can mask real hardware faults. Security-sensitive override registers can alter AXI attributes and protection behavior, so writes to those registers must be tightly controlled by initialization policy.

## Test Signals

Strong signals include successful CPU firmware initialization, `QUEUE_INIT` reaching the ready-for-host state within timeout, working command and event queues, correct PI-update interrupt delivery, and no spurious ECC/SEI interrupt storms. Register readback tests in simulation or bring-up should confirm all queue base/length registers and `CPU_MSB_ADDR` match expected DMA addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/cpu_if_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma0_core_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma0_core_masks.h

## Purpose

`dma0_core_masks.h` is an auto-generated bit-field map for the Gaudi DMA0 core register block. It defines shifts and masks for enabling the DMA engine, programming transfers, configuring write completions, security properties, rate limits, errors, status, and debug registers.

## Important APIs, Types, and Constants

The file exports shift/mask pairs for every DMA0 core field. Important groups include `DMA0_CORE_CFG_0_EN` for core enable, `DMA0_CORE_CFG_1_HALT/FLUSH/SB_FORCE_MISS`, source and destination base/stride/transfer-size fields, `DMA0_CORE_COMMIT_*` fields for linear DMA, transpose, data type, memset, compression/decompression, write completion, and context ID, and write-completion address/data/AWUSER fields.

Security and protection fields include `DMA0_CORE_PROT_VAL`, `DMA0_CORE_PROT_ERR_VAL`, `DMA0_CORE_SECURE_PROPS_ASID/MMBP`, and `DMA0_CORE_NON_SECURE_PROPS_ASID/MMBP`. Error fields include `DMA0_CORE_ERR_CFG_ERR_MSG_EN`, `STOP_ON_ERR`, `ERR_CAUSE_*`, and error-message address/write-data fields. Status/debug fields include request counters, `DMA0_CORE_STS0_BUSY`, halt state, debug memory controls, descriptor counters, and FIFO/buffer fullness indicators.

## Control Flow

The header has no executable control flow. The masks are applied in driver initialization and runtime paths. `gaudi_init_dma_core()` uses the error config, protection, secure-props, and enable shifts to configure each DMA engine and sets workarounds such as LBW outstanding limits. DRAM scrubbing and device-memory memset paths write DMA0 core source/destination/size registers and set `DMA0_CORE_COMMIT_LIN` plus `DMA0_CORE_COMMIT_MEM_SET`, then poll `DMA0_CORE_STS0_BUSY`. Error handling reads and clears `DMA0_CORE_ERR_CAUSE`.

## State and Persistence Behavior

The masks describe mutable hardware state in DMA core registers. Transfer programming state is transient per operation. Configuration state such as enable, protection, secure properties, outstanding limits, rate limits, and error-message settings persists across DMA jobs until reset or reconfiguration. Error-cause and debug registers expose state that must be read and cleared by the driver.

## Dependencies and Integration Points

This file pairs with `dma0_core_regs.h` for addresses and is reused across DMA channels by adding `DMA_CORE_OFFSET` computed from DMA0 and DMA1 core base addresses. Gaudi code applies the same DMA0 field definitions to DMA1 and other channels because they share the DMA_CORE prototype. It also integrates with queue-manager command processing, since QMAN LDMA offset registers point into the DMA core register layout.

## Risks

Mask mistakes can misprogram DMA operations, a severe risk because DMA can read/write host and device memory. Context ID, ASID, MMBP, and protection fields are security-critical. The commit register has multiple independent operation modifiers, so accidental bit overlap can turn a copy into a memset, enable compression, or suppress expected completions. Busy polling and error handling depend on correct status and error masks.

## Test Signals

Tests should cover DMA core initialization readback, successful linear copy and memset operations, correct busy-bit transitions, RAZWI/error-message generation, stop-on-error behavior, and security-prop behavior for secured and non-secured channels. HBM scrubbing is a practical integration signal because it exercises source/destination/size/commit fields over every DMA channel and polls `STS0_BUSY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma0_core_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma0_core_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma0_core_regs.h

## Purpose

`dma0_core_regs.h` is the auto-generated address map for the Gaudi DMA0 core block. It gives MMIO offsets for control, transfer descriptor, completion, protection, security, rate-limit, error, status, and debug registers starting at the DMA0 core region around `0x500000`.

## Important APIs, Types, and Constants

The header exports `mmDMA0_CORE_*` register offsets. The core programming sequence uses `CFG_0`, `CFG_1`, `SRC_BASE_*`, `DST_BASE_*`, multi-dimensional source/destination transfer-size and stride registers, `DST_TSIZE_0`, and `COMMIT`. Completion support uses `WR_COMP_WDATA`, `WR_COMP_ADDR_*`, and `WR_COMP_AWUSER_31_11`. Security/protection uses `PROT`, `SECURE_PROPS`, and `NON_SECURE_PROPS`. Runtime tuning and observability use read/write max outstanding, max size, AXCACHE/AXUSER, inflight counters, rate-limit config, error config/cause/message, `STS0`, `STS1`, and debug memory/status registers.

## Control Flow

The header is passive. In Gaudi code, DMA channel code computes `dma_offset = dma_id * DMA_CORE_OFFSET` and adds it to DMA0 addresses to target each channel. Initialization writes error-message routing, protection, secure props, and `CFG_0` enable. Scrubbing and memset paths write source/destination registers, size, and `COMMIT`, then poll `STS0` for `BUSY` to clear. Error paths read and clear `ERR_CAUSE`.

## State and Persistence Behavior

These addresses refer to device registers. Configuration registers persist across commands, descriptor registers hold the currently programmed DMA operation, status registers reflect live engine state, and error-cause registers persist fault state until cleared. The header itself is generated source and should not be edited manually.

## Dependencies and Integration Points

This file depends on the matching mask file for field definitions. It integrates with `gaudiP.h` offsets such as `DMA_CORE_OFFSET`, `QMAN_LDMA_SRC_OFFSET`, `QMAN_LDMA_DST_OFFSET`, and `QMAN_LDMA_SIZE_OFFSET`, which are derived from DMA0 addresses. Queue manager code uses those offsets to teach the CP where DMA core source, destination, and size registers live relative to the DMA core base.

## Risks

Incorrect address definitions can make every DMA channel write the wrong register. Because DMA1 and other channel offsets are derived from the DMA0/DMA1 layout, an incorrect DMA0 address or offset can break all channels, not just DMA0. Address drift also affects CP LDMA command execution through the QMAN offset constants.

## Test Signals

Useful signals are successful DMA channel enable, correct register readback after initialization, passing DRAM scrub and device-memory memset, expected error interrupt routing, and correct derived offsets in `gaudiP.h`. Hardware simulation can validate that `mmDMA0_CORE_* + dma_id * DMA_CORE_OFFSET` lands on matching registers for all DMA channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma0_core_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma0_qm_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma0_qm_masks.h

## Purpose

`dma0_qm_masks.h` is the auto-generated bit-field map for the Gaudi DMA0 queue-manager block. It defines how to enable, stop, flush, protect, monitor, and debug primary queue fetchers, completion queue fetchers, command processors, the QMAN arbiter, clock-gating logic, APB indirect gateway, and related error paths.

## Important APIs, Types, and Constants

Global QMAN fields include `DMA0_QM_GLBL_CFG0_*` enable bits for PQF, CQF, and CP units; `GLBL_CFG1_*` stop/flush bits; `GLBL_PROT_*`; `GLBL_ERR_CFG_*`; secure and non-secure ASID/MMBP properties per stream; `GLBL_STS0` idle/stop indicators; `GLBL_STS1` and `GLBL_MSG_EN` error/status bits for fetch and CP failures.

Queue fields describe PQ base, size, PI, CI, credit/inflight status, CQ base/size/control/status, and CQ internal FIFO counts. CP fields cover message base addresses, LDMA source/destination/size offsets, fence read-data and counters, CP status, current instruction address, barrier guard config, debug state, and CP ARUSER/AWUSER attributes. Arbiter fields cover arbitration type, master/slave enable, WRR weights, credit counters, message limits, error causes, watchdogs, and status. Later groups cover clock gating, local ranges, strict priority, HBW/LBW rate limiting, AXCACHE, indirect APB gateway, global error capture, and memory-init busy state.

## Control Flow

The header has no code flow. Gaudi initialization applies these fields when configuring each DMA QMAN. Queue setup writes PQ base/size/PI/CI, CP LDMA offsets, CP message base registers, and barrier config. Per-QMAN setup writes global error config, error-message address/data, arbiter error-message enable, watchdog timeout, global protection, stop/flush reset, and finally global enable masks. Stop/reset paths use `GLBL_CFG1_CP_STOP` masks, and clock-gating paths use CGM registers.

## State and Persistence Behavior

The masks describe persistent QMAN configuration and live queue state. PQ/CQ base and size registers persist while queues are active; PI/CI and status registers change as commands flow. CP fence counters and current-instruction registers expose live execution state. Error and arbiter status fields persist until cleared by the appropriate driver or hardware flow. Security property fields define how QMAN-generated AXI transactions are tagged.

## Dependencies and Integration Points

This file pairs with `dma0_qm_regs.h` and with the common queue ABI in `qman_if.h`. It is reused for multiple DMA QMANs by adding `DMA_QMAN_OFFSET`. It also integrates with synchronization manager registers through CP message-base programming, with DMA core registers through LDMA offset fields, and with interrupt routing through global and arbiter error-message fields.

## Risks

Queue-manager bit fields are concurrency- and security-sensitive. Wrong enable/stop/flush masks can leave engines running during reset or disabled during submission. Wrong PQ/CQ or CP message semantics can corrupt host queues, lose completions, or generate interrupts to the wrong target. Secure/non-secure ASID/MMBP fields and protection bits affect address translation and isolation. Arbiter watchdog and credit fields can create starvation or deadlocks if misprogrammed.

## Test Signals

Signals include successful QMAN initialization across all DMA channels, working command submission and completion for every stream, correct CP fence behavior, correct stop/flush during reset, no unexpected QMAN global/arbiter errors under stress, and expected error-message interrupts for RAZWI or malformed commands. Queue wraparound and multi-stream arbitration stress tests are especially valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma0_qm_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma0_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma0_qm_regs.h

## Purpose

`dma0_qm_regs.h` is the auto-generated address map for the Gaudi DMA0 queue-manager block starting around `0x508000`. It gives symbolic offsets for global QMAN control, per-stream PQ/CQ registers, CP message/fence/debug registers, arbiter registers, clock-gating registers, rate-limit controls, indirect gateway registers, and error-capture registers.

## Important APIs, Types, and Constants

The exported constants are `mmDMA0_QM_*` addresses. The global region includes `GLBL_CFG0`, `GLBL_CFG1`, `GLBL_PROT`, `GLBL_ERR_CFG`, secure/non-secure props for streams 0 through 4, status, and message-enable registers. The PQ region has four primary queues with base low/high, size, PI, CI, config, ARUSER, and status. The CQ region has five completion queues with config, ARUSER, status, pointer, transfer-size, control, pointer/status mirrors, and FIFO counts. CP registers include four message base pairs for five CP streams, LDMA register offsets, fence data/counters, status, current instruction, barrier config, debug, and ARUSER/AWUSER. Arbiter and CGM blocks follow, then local range, strict priority, rate limit, AXCACHE, APB indirect gateway, global error address/write-data, and memory-init busy registers.

## Control Flow

The header has no executable logic. Gaudi queue initialization computes `dma_qm_offset = dma_id * DMA_QMAN_OFFSET`, and per-stream code adds `qman_id * 4` to the base stream-0 registers. It programs PQ bases and indices, CP LDMA offsets derived from DMA core addresses, CP message bases for monitor and sync-object areas, and barrier config. Per-QMAN setup writes error routing and global protection, while `gaudi_enable_qman()` writes `mmDMA0_QM_GLBL_CFG0 + dma_qm_offset` with an enable mask.

## State and Persistence Behavior

The mapped registers are persistent hardware state. Queue base/size/config registers persist until reprogrammed, PI/CI/status registers mutate as the queue runs, CP/fence/debug registers expose live command processor state, and error/arbiter registers persist fault or arbitration state. The generated header itself is static source and should not be hand-edited.

## Dependencies and Integration Points

This file pairs with `dma0_qm_masks.h` and uses the common QMAN descriptor ABI from `qman_if.h`. `gaudiP.h` derives `DMA_QMAN_OFFSET` from DMA0/DMA1 QMAN bases and derives CP LDMA offsets from DMA0 QMAN and DMA core addresses. The register map also integrates with sync manager monitor/SOB addresses, interrupt/GIC error routing, and reset/clock-gating code.

## Risks

Wrong addresses can corrupt queue state, break command submission, or make queue-manager faults impossible to diagnose. Because stream registers are laid out at 4-byte strides for many fields, off-by-one stream offsets can silently program the wrong queue. The map is also part of derived constants, so address drift affects DMA and CP command execution even outside direct QMAN writes.

## Test Signals

Signals include readback of QMAN base/size/PI/CI after initialization, command completion on all DMA QMAN streams, correct fence counter behavior, correct reset stop/flush behavior, working arbiter arbitration under concurrent streams, and expected global/arbiter error captures. Offset-derived tests should verify that `DMA_QMAN_OFFSET` and `qman_id * 4` addressing match the silicon register layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma0_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma1_core_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma1_core_regs.h

## Purpose

`dma1_core_regs.h` is the auto-generated address map for the Gaudi DMA1 core block. It mirrors the DMA0 core register layout but starts at the DMA1 core base around `0x520000`. The driver uses it both as a concrete DMA1 address map and as evidence for deriving per-channel DMA core offsets.

## Important APIs, Types, and Constants

The header exports `mmDMA1_CORE_*` constants for the same DMA_CORE prototype groups as DMA0: enable/control, source/destination base registers, multi-dimensional transfer sizes and strides, commit, write completion, transfer engine rows, protection, secure/non-secure properties, read/write outstanding and AXI attributes, rate limiting, error config/cause/message, status, debug memory, debug counters, debug status, and descriptor IDs.

## Control Flow

The header has no executable control flow. In Gaudi code, `DMA_CORE_OFFSET` is computed as `mmDMA1_CORE_BASE - mmDMA0_CORE_BASE`, and most multi-channel programming uses `mmDMA0_CORE_* + dma_id * DMA_CORE_OFFSET`. Reset paths may also write concrete DMA1 registers, such as halting DMA1 core through `mmDMA1_CORE_CFG_1`. This means the DMA1 register map participates in both direct access and generalized per-channel addressing.

## State and Persistence Behavior

The registers hold DMA1 hardware configuration, transfer state, status, debug state, and errors. Configuration persists until reset/reprogramming, transfer descriptor registers are overwritten per DMA operation, and error/status registers reflect live or latched hardware state. The generated header itself should remain static and synchronized with the hardware database.

## Dependencies and Integration Points

This file pairs conceptually with the DMA0 core register and mask headers. It integrates with `gaudiP.h` offset derivation and with channel-generic initialization in `gaudi_init_dma_core()`. Because the field layout is shared with DMA0, DMA0 mask constants are applied to DMA1 register addresses. It also participates in reset, halt, scrubbing, memset, error routing, and queue-manager LDMA integration.

## Risks

If the DMA1 base or any DMA1 offset diverges from DMA0 unexpectedly, the `DMA_CORE_OFFSET` channel abstraction can misaddress every channel after DMA0. A generated-map mismatch can break DMA1 specifically or all DMA channels that rely on the derived offset. Since the mask file is DMA0-named but shared by prototype, a hardware layout difference between DMA0 and DMA1 would be dangerous.

## Test Signals

Validation should include direct readback of DMA1 control/status registers, successful DMA1 initialization through channel-generic code, DMA1 participation in DRAM scrubbing and memory copy/memset operations, correct halt/reset behavior via `mmDMA1_CORE_CFG_1`, and no DMA1-specific error-cause bits under normal transfers. Offset tests should confirm that DMA0 plus `DMA_CORE_OFFSET` reaches every DMA1 register defined here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma1_core_regs.h -->
