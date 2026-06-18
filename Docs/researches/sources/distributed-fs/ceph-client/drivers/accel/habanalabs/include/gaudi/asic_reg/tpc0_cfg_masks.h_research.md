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
