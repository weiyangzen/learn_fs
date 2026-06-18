# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme_masks.h

## Purpose

`mme_masks.h` defines generated field masks and shifts for the Goya MME tensor-engine register block. It describes how to encode and decode the architectural descriptor, execution controls, debug memory, credit controls, interrupt masks/status, and four shadow descriptor banks defined by `mme_regs.h`.

## Important APIs, types, and data

The file exports only `MME_*_SHIFT` and `MME_*_MASK` macros. Key architectural fields include `ARCH_STATUS` bits for A, B, CIN, COUT, TE, load/store, scoreboard emptiness, AXI idle state, and free accumulators; high/low base-address fields for A/B/CIN/COUT/BIAS tensors; `ARCH_HEADER` controls for signaling, transpose/lower-A, accumulation mask, bias/CIN load, output store, accumulator increment disables, tensor advance bits, compressed B, convolution-end masking, and data types; kernel-size and associated-dimension fields; COUT/CIN scaling; GEMMLOWP zero points, exponents, multiply enables, accumulation, bias accumulation, and ReLU enable; ROI base offsets, valid elements, loop strides, ROI sizes, spatial starts/strides, and spatial sizes for A/B/C tensors; sync-object message value/address/operation; padding, iteration, and split-bubble fields.

Execution and infrastructure fields include `MME_CMD_EXECUTE`, reset, stall, shared-memory base, debug-memory address/data/control/read-complete flags, log-shadow masks, store/AGU/SBA/SBB/SBC/WBC credit controls, ASID/MMBP control data for MME memory clients, TE credits, and REI/SEI/SPI status and masks. The shadow sections repeat the descriptor field layout for shadow banks 0 through 3.

## Control flow

No control flow exists in the header. Runtime code uses these masks to build descriptor words, program the live architectural registers or shadow descriptor banks, issue `MME_CMD_EXECUTE`, then poll status/interrupt/debug state. Shadow-bank fields allow the hardware or driver to retain multiple pending/logged descriptor images while execution state advances.

## State and persistence behavior

The macros are stateless constants. The fields they describe are persistent hardware state until reset or overwrite. Tensor base addresses and ROI/stride/dimension fields define memory accesses for MME operations. Header fields control whether inputs are advanced, outputs are stored, quantization/ReLU is applied, and sync-object messages are emitted. Status and shadow registers are observability state and can be used after errors to reconstruct which descriptor was active or logged.

## Dependencies and integration points

This header must match `mme_regs.h` exactly. It integrates with Goya command submission, descriptor construction, reset/stall/debug paths, interrupt handling, and ASID/MMU programming. It also connects to common HabanaLabs memory-management behavior because ASID/MMBP fields and tensor base addresses determine how MME transactions are translated.

## Risks and edge cases

This is a high-blast-radius field map. Incorrect descriptor field packing can make the MME read or write the wrong tensor memory, apply wrong data types, fail to signal completion, or corrupt accumulators. Address fields are split high/low and must be coherent. The header contains many repeated shadow-bank macros; consumers must use the bank matching the hardware state they intend to inspect or program. Narrow fields such as signal mask, kernel dimensions, zero points, exponents, and credit counts can truncate silently if callers fail to validate inputs.

## Test signals

Static validation is a successful build and generated-header consistency checks between live and shadow field names. Runtime signals include correct MME numerical output for representative GEMM/convolution workloads, expected completion signaling through sync objects, clean reset/stall recovery, meaningful shadow descriptor dumps after injected failures, no unexpected REI/SEI/SPI interrupts, and MMU/ASID tests proving MME reads and writes occur in the intended address space.
