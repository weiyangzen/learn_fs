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
