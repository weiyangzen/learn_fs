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
