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
