# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc1_cfg_regs.h

## Purpose

`tpc1_cfg_regs.h` is the generated MMIO map for the Goya TPC1 core configuration block, from `0xE46400` through `0xE46E2C`. It describes kernel descriptor, execution control, memory base, interrupt, AXUSER, and MBIST registers for TPC1.

## Important APIs, Types, and Constants

The exported constants are `mmTPC1_CFG_*` addresses. The largest groups are `KERNEL_TENSOR_0..7` and `QM_TENSOR_0..7`, each with base low/high, padding, tensor config, and five dimension size/stride/base-offset triples. Kernel and QM descriptor groups also include kernel base address, five TID base/size pairs, 32 SRF registers, kernel config, and sync object message. The central config area includes round CSR, TBUF base, semaphore, vector/scalar flags, LFSR polynomial, status, config base/subtract, SM base, TPC command/execute/stall, icache base, MSS config, interrupt cause/mask, and TSB config. Tail registers include ARUSER, AWUSER, functional MBIST control/pattern, and ten MBIST memory registers.

## Control Flow

This file has no code. Kernel launch/setup paths program tensor descriptors, kernel code address, TID geometry, SRF values, sync object messages, and execution controls; reset/debug paths use stall/status/interrupt registers.

## State and Persistence Behavior

Register contents are persistent TPC1 execution configuration. Descriptor, SRF, flags, memory base, interrupt mask, and MBIST settings remain until overwritten or reset; status and interrupt cause change as hardware executes.

## Dependencies and Integration Points

The map integrates with Goya TPC queue submission, MMU/ASID AXUSER setup, sync object messaging, interrupt handling, reset/stall logic, and derived `TPC_CFG_OFFSET` calculations that step between TPC instances.

## Risks

Address errors in descriptor tables can make kernels read wrong tensors or execute wrong code. Incorrect TID geometry, SRF, sync object, or AXUSER registers can cause data corruption, missed completions, or isolation faults.

## Test Signals

Signals include descriptor readback, successful kernels on TPC1, correct sync object message writes, expected interrupt cause/mask behavior, stall/execute transitions, memory access under programmed AXUSER values, and MBIST register readback in manufacturing diagnostics.
