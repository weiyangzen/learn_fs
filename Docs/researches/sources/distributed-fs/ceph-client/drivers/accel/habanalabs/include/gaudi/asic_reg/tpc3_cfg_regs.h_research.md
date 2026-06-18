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
