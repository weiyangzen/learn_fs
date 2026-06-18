# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme_qm_regs.h

## Purpose

`mme_qm_regs.h` provides generated MMIO offsets for the Goya MME queue manager, whose prototype is `QMAN`. It names the registers used to configure MME producer queues, completion queues, command processor message bases, LDMA offsets, fences, status, and debug buffer access.

## Important APIs, types, and data

The exported surface is the `mmMME_QM_*` offset namespace. The block starts at `0xD8000` with global config/protection/error/status registers. PQ registers from `0xD8060` include base low/high, size, producer/consumer indices, PQ config, ARUSER, push words, status, and read-rate limiter controls. CQ registers from `0xD80B0` include config, pointer/size/control, mirrored status, credit/busy/free status, rate limiting, and IFIFO count. CP registers from `0xD8120` include four message-base address pairs, LDMA offset registers, fence read-data/count pairs, CP status/current instruction/barrier/debug, and debug buffer windows from `0xD8300` to `0xD830C`.

There are no functions, data objects, or type declarations.

## Control flow

The file is declarative. Driver queue setup code writes the offsets in a hardware-defined sequence: global policy, PQ ring state, CQ state, CP message/LDMA metadata, and enable bits. Doorbell paths update PQ producer-related registers. Reset paths stop/flush through global config and poll status registers. Diagnostics use current-instruction, fence, and buffer readback offsets.

## State and persistence behavior

The addressed registers hold live queue-manager state in hardware. Ring bases and indices, CP message bases, LDMA offsets, and fences persist across submissions until reset or reprogramming. Debug buffer address/data registers expose transient internal state. The header itself stores nothing.

## Dependencies and integration points

This header must be used with `mme_qm_masks.h`. It integrates with Goya queue allocation constants such as `MME_QMAN_LENGTH`, common QMAN submission helpers, MMU ASID setup, and reset/error handling. It is structurally related to `mme_cmdq_regs.h`, but includes PQ-specific registers at the `0xD8xxx` base.

## Risks and edge cases

Confusing QMAN and CMDQ address windows would send writes to the wrong block. Queue-base low/high pairs and size/index registers must be coherent. The push registers encode a descriptor as several consecutive words; partial programming can create malformed work. CP message base and LDMA offset registers must match the firmware/packet format expected by the command processor.

## Test signals

Successful driver build and Goya probe are the first checks. Runtime validation should submit MME work through the QMAN, verify producer/consumer progress, observe fence completion, reset while queues are active, and confirm status/error registers match expected masks when invalid descriptors are injected.
