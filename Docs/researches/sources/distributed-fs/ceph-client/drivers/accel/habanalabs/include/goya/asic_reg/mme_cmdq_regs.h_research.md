# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme_cmdq_regs.h

## Purpose

`mme_cmdq_regs.h` provides generated MMIO offsets for the Goya `MME_CMDQ` block, whose prototype is `CMDQ`. It is the register-address companion to `mme_cmdq_masks.h` and identifies where the driver programs the MME command queue, command processor, LDMA offsets, fences, and debug buffer.

## Important APIs, types, and data

The file defines only `mmMME_CMDQ_*` offset macros. The global register range starts at `0xD9000` with `GLBL_CFG0`, `GLBL_CFG1`, protection, error capture, secure/non-secure properties, and global status. The CQ area begins at `0xD90B0` and includes configuration, ARUSER, pointer low/high, transfer size, control, status mirrors, credit/busy/free status, and read-rate limiter registers. The CP section from `0xD9120` includes four message-base address pairs, LDMA source/destination/size/commit offset registers, four fence read-data/count pairs, CP status, current instruction, barrier config, and debug. The debug CQ buffer access registers live at `0xD9308` and `0xD930C`.

There are no functions, structs, or side-effecting macros.

## Control flow

The header is read-only metadata. Device code uses these offsets to program queue state in a specific order: configure global protection/error policy, initialize CQ descriptors and limits, configure CP message and LDMA metadata, enable the relevant frontends, and later poll status or fence registers. Reset/teardown paths write stop/flush bits through `GLBL_CFG1` and check idle/stop status through the matching masks.

## State and persistence behavior

The file itself has no state. The addressed registers hold live queue state, including command buffer pointers, current instruction, CP message bases, LDMA offsets, fence counters, and error captures. These values persist in hardware across command submissions until reset or reinitialization.

## Dependencies and integration points

It depends on the Goya generated-register include model and pairs with `mme_cmdq_masks.h` for field composition. It integrates with HabanaLabs queue initialization, command submission, reset, and debug code using `RREG32()`/`WREG32()`. It is closely related to `mme_qm_regs.h`; the QMAN block includes both PQ and CQ, while this command-queue block exposes the command/CQ side at the `0xD9xxx` window.

## Risks and edge cases

Pointer and size registers are split and must be programmed consistently. Enabling the CP or DMA before message bases and LDMA offsets are valid can cause memory errors. Debug buffer reads must use the buffer address/data protocol rather than arbitrary MMIO assumptions. Because this file has only offsets, consumers must use the matching mask header to avoid writing reserved or mispositioned bits.

## Test signals

Build the driver, run Goya queue initialization, submit MME commands, verify CP current-instruction and fence status change as expected, and validate reset paths stop and flush the queue without leaving busy bits stuck. Error injection should populate `GLBL_ERR_ADDR_*`, `GLBL_ERR_WDATA`, and `GLBL_STS1` consistently with the masks.
