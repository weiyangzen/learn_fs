# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_qm_0_masks.h

Purpose: auto-generated bitfield definitions for DMA queue manager 0, the canonical Goya DMA `QMAN` mask header. Because queue-manager instances 1-4 share the same register layout, higher-level macros in `goya_masks.h` reuse many `DMA_QM_0_*` shifts and masks for all DMA QMAN instances.

Important APIs/types/functions: the public interface is `DMA_QM_0_*_SHIFT` and `DMA_QM_0_*_MASK`. Important groups are global enables/stops/flushes/protection/error configuration, secure and non-secure ASID/MMBP properties, idle/error status bits, producer queue base/size/PI/CI/config/push/status/rate-limit fields, completion queue config/pointer/size/control/status/rate-limit/IFIFO fields, command processor message-base addresses, LDMA offset registers, fence read-data/count fields, CP status/current-instruction/barrier/debug fields, and internal PQ/CQ buffer debug access.

Control flow: no local control flow. Driver code uses these masks with `dma_qm_0_regs.h` through `dma_qm_4_regs.h` to enable/stop the queue manager, configure queues, push work, set error messaging and protection, poll idle state, and debug CP/PQ/CQ state.

State and persistence: masks describe persistent device register fields. Queue bases, indices, credits, secure properties, fence counters, and error configuration remain programmed until reset or rewritten. Status fields reflect live hardware execution and error state.

Dependencies and integration: included by `goya_regs.h` and consumed by `goya_masks.h` to build aggregate constants such as `QMAN_DMA_ENABLE`, `QMAN_DMA_STOP`, `QMAN_DMA_ERR_MSG_EN`, and `DMA_QM_IDLE_MASK`. `goya_security.c` uses the queue-manager register addresses to calculate protection-bit masks for each DMA QMAN block.

Risks: this file is a layout authority for all DMA queue managers, not just instance 0. A wrong shift/mask can affect enable/stop semantics, security properties, queue indexing, or error handling across every DMA engine. The mixed global/PQ/CQ/CP/debug register groups make it easy to use a status mask on a control register or vice versa.

Test signals: compile coverage through `goya_masks.h`, queue-manager bring-up, queue push/completion tests, stop/flush/idle polling, secure/non-secure access validation, CP fence tests, error-message injection, and DMA stress tests that validate producer/completion queue accounting.
