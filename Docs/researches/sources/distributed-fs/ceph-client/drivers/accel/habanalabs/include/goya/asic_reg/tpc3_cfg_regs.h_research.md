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
