# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc2_cfg_regs.h

## Purpose

`tpc2_cfg_regs.h` is the generated configuration register map for Goya TPC2, covering `0xE86400` through `0xE86E2C`. It is the TPC2 instance of the TPC core descriptor/control schema.

## Important APIs, Types, and Constants

The file exports `mmTPC2_CFG_*` addresses. It contains kernel and QM tensor descriptor banks for tensors 0 through 7, each with base address, padding, tensor config, and five dimensions of size/stride/base offset. It also maps kernel/QM base addresses, TID base and size for five dimensions, 32 SRF registers, kernel config, sync object message, round CSR, TBUF base, semaphore, vector/scalar flags, LFSR polynomial, status, config and SM base registers, TPC command/execute/stall, icache base, MSS config, interrupt cause/mask, TSB config, ARUSER/AWUSER, and functional MBIST registers.

## Control Flow

There is no code. Driver launch flow programs descriptors and execution registers before TPC2 work is run, while interrupt/reset flows use status, interrupt, stall, and execute registers.

## State and Persistence Behavior

The mapped registers hold TPC2 kernel launch state and core configuration until overwritten or reset. Status and interrupt cause fields are live hardware state.

## Dependencies and Integration Points

It integrates with Goya TPC queue execution, sync object messaging, MMU AXUSER/ASID preparation, TPC reset/stall handling, and offset-based multi-TPC programming derived from the TPC0/TPC1 layout.

## Risks

Descriptor or address mistakes can point TPC2 at wrong tensor, kernel, or shared memory regions. Incorrect sync object or interrupt mapping can make command completion unreliable.

## Test Signals

Signals include descriptor readback, TPC2 kernel execution, correct sync object completion, interrupt cause/mask behavior, TPC stall/execute transitions, AXUSER-tagged memory access, and MBIST control/memory register diagnostics.
