# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_qm_1_regs.h

Purpose: auto-generated register-address map for DMA queue manager 1, a QMAN clone at `0x408000` that schedules DMA channel 1 work.

Important APIs/types/functions: no functions or types. The `mmDMA_QM_1_*` macros mirror queue manager 0's global, producer queue, completion queue, command processor, fence, status, rate-limit, and debug register layout with instance-1 addresses.

Control flow: no executable flow. Driver code writes these addresses to initialize queues and security properties, pushes descriptors through PQ push registers, observes CQ/CP status, handles errors, and stops/flushes the engine. Bit shifts and masks are reused from `dma_qm_0_masks.h` through `goya_masks.h`.

State and persistence: hardware registers hold queue bases, indices, CP message addresses, credits, fences, error configuration, and status. The state persists until reset or explicit reconfiguration. Queue backing memory is external to this header.

Dependencies and integration: included by `goya_regs.h`. `goya_security.c` enumerates `mmDMA_QM_1_*` offsets to set protection bits for the instance-1 QMAN window. The block base is `mmDMA_QM_1_BASE` in `goya_blocks.h`.

Risks: the file is a generated clone, so any divergence from queue manager 0 must be intentional. Using instance-0 addresses when configuring instance 1 would target the wrong channel, while using instance-1 addresses with instance-0 block math would break protection calculations.

Test signals: channel 1 queue execution, stop/idle status, CQ completions, CP fence status, error-message delivery, and security protection readback for the `mmDMA_QM_1_BASE` block.
