# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_cfg_regs.h

Purpose: maps 432 TPC0 configuration register addresses from `0xE06400` to `0xE06E2C`. The block contains kernel-side tensor descriptors, kernel base/TID/SRF/config registers, runtime control/status/cache/interrupt registers, queue-manager descriptor mirrors, ARUSER/AWUSER attributes, and functional MBIST registers.

Important APIs/types/functions: macro-only `mmTPC0_CFG_*` address API. Major ranges include `KERNEL_TENSOR_0..7`, `KERNEL_BASE_ADDRESS_*`, `KERNEL_TID_*`, `KERNEL_SRF_0..31`, `TPC_CMD`, `TPC_EXECUTE`, `TPC_STALL`, `STATUS`, `MSS_CONFIG`, `TPC_INTR_CAUSE/MASK`, `QM_TENSOR_0..7`, `QM_KERNEL_*`, `ARUSER`, `AWUSER`, and `FUNC_MBIST_*`.

Control flow: workload setup writes descriptors and kernel addresses, prepares instruction/cache state, waits for idle, starts execution with `TPC_EXECUTE`, monitors `STATUS`, and handles interrupts through cause/mask registers. Driver code derives per-TPC offsets from neighboring TPC0/TPC1 register addresses to reuse this layout across all TPCs.

State and persistence: descriptors, SRFs, MMU attributes, cache configuration, and stall/execute controls persist in TPC hardware until reset or the next command. Status and counters reflect live execution.

Dependencies and integration: included by `goya_regs.h` and used with field masks in `tpc0_cfg_masks.h`. Goya code uses TPC0 as the canonical address layout for all eight TPCs, while security code computes protection-bit locations from these register addresses.

Risks: this header has a large generated surface, so off-by-one offsets in repeated tensor/SRF/QM ranges are a central risk. Address typos such as the existing `ADDERESS` spelling are part of the ABI and should not be renamed independently. Mixing Goya and Gaudi TPC maps can break offset arithmetic.

Test signals: TPC bring-up, per-TPC launch on all engines, descriptor programming, interrupt cause/mask handling, idle checks, protection-bit audits, MMU ASID setup, and MBIST coverage.
