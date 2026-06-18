# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme_regs.h

## Purpose

`mme_regs.h` is the generated MMIO offset map for the Goya MME tensor-engine block. It defines where software writes tensor descriptors, execution controls, debug-memory accesses, credit controls, interrupt registers, and four shadow descriptor banks.

## Important APIs, types, and data

The file exports only `mmMME_*` register offsets. The live architectural descriptor starts at `0xD0000` with `ARCH_STATUS`, high/low base addresses for A, B, CIN, COUT, and BIAS, descriptor header, kernel size, associated dimensions, scaling and GEMMLOWP fields, ROI base offsets, valid elements, loop strides, ROI sizes, spatial starts/strides/sizes for A/B/C, sync-object message, padding, iteration count, and split-bubble control. Execution and debug controls include `MME_CMD`, `DUMMY`, `RESET`, `STALL`, shared-memory base, debug-memory address/data/control/read-complete, and `LOG_SHADOW`.

Infrastructure registers include store max credit, AGU, SBA/SBB/SBC/WBC credit and control data, TE/TE2DEC credits, REI/SEI/SPI status and masks. Four shadow banks, `SHADOW_0` through `SHADOW_3`, repeat the descriptor/status layout from roughly `0xD0400` through `0xD0BAC`.

## Control flow

There is no executable code in the header. Runtime MME programming writes descriptor fields, programs memory/security controls, optionally writes shadow-related controls, then writes `MME_CMD` to execute. Status, interrupt, and shadow registers are read during completion, error handling, or debug. Reset and stall registers are used by recovery paths to quiesce or reinitialize the MME.

## State and persistence behavior

MME registers describe live tensor operation state in hardware. Base address, ROI, stride, data type, quantization, and sync-object fields persist until overwritten and directly determine the next MME execution. Shadow banks preserve hardware-visible copies of descriptor state for logging or in-flight tracking. Interrupt masks/status and debug-memory registers are volatile hardware state; the header itself has no storage.

## Dependencies and integration points

This file pairs with `mme_masks.h` for field-level packing. It integrates with Goya command submission and firmware packet formats, MMU/ASID setup, sync-object completion signaling, reset logic, and debug paths. It also interacts with QMAN/CMDQ headers because queue-submitted work ultimately causes descriptors to reach this MME block.

## Risks and edge cases

The register map controls memory reads and writes by an accelerator. Bad base addresses, strides, valid-element counts, data types, or store controls can corrupt device memory or produce incorrect computation. Shadow registers are repeated and easy to index incorrectly. Reset/stall/debug registers should not be written while active work is assumed to complete normally. The generated file must stay synchronized with `mme_masks.h`; offset/field mismatches are high-risk.

## Test signals

Validation should include a clean build, successful Goya probe/reset, MME numerical workloads covering A/B/CIN/COUT/BIAS paths, quantized GEMMLOWP/ReLU cases, sync-object completion, interrupt status/mask behavior, and debug/shadow dump correctness after injected faults or forced stalls.
