# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_qm_3_regs.h

Purpose: auto-generated register-address map for DMA queue manager 3, the QMAN instance at `0x418000` that is adjacent to DMA channel 3.

Important APIs/types/functions: no functions or structs. The `mmDMA_QM_3_*` macros provide the same QMAN surface as instances 0-2: global config/protection/error/status, PQ and CQ setup/status/rate-limit registers, CP message and LDMA offset registers, fences, CP status/debug, and queue-buffer debug windows.

Control flow: this is a constants-only header. Runtime code uses it to set up channel 3's queue-manager state, push work, handle completions/errors, and stop or poll the QMAN. Shared bitfields are supplied by `dma_qm_0_masks.h` and aggregate helpers in `goya_masks.h`.

State and persistence: all state is device register state. Queue pointers, indices, credits, secure properties, and error handling remain until reset/rewrite; status and fence counters reflect live channel execution.

Dependencies and integration: included by `goya_regs.h`; protected through `goya_security.c` using QMAN register addresses; block base and section are in `goya_blocks.h`. It pairs with `dma_ch_3_regs.h` and DMA channel 3 CoreSight/bus-monitor block bases.

Risks: channel 3 has both a QMAN window and a separate DMA channel window. Confusing `0x418000` QMAN registers with `0x419000` channel registers can break queue submission or transfer programming. Protection-bit calculations assume these offsets remain aligned on the expected 4-KiB window.

Test signals: channel 3 queue submission/completion, CP fence progress, QMAN stop/idle bits, error-message delivery, protected register access checks, and CoreSight/bus-monitor confirmation during channel 3 workload.
