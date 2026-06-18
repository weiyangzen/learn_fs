# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_qm_4_regs.h

Purpose: auto-generated register-address map for DMA queue manager 4, the QMAN instance at `0x420000` that feeds DMA channel 4.

Important APIs/types/functions: exposes only `mmDMA_QM_4_*` macros. The register families are global enable/stop/protection/error/status, producer queue configuration and push/status/rate-limit, completion queue config/status/rate-limit/IFIFO, command processor message bases and LDMA offsets, fence read-data/count, CP status/current instruction/barrier/debug, and internal queue-buffer debug registers.

Control flow: declarative. Driver logic uses these addresses for queue-manager initialization, job push, completion handling, error routing, stop/flush, and diagnostic reads. Bitfields are shared with `dma_qm_0_masks.h`.

State and persistence: queue-manager configuration and status live in the DMA QMAN 4 hardware block. State survives until reset or rewrite; queue memory is external and referenced by base/size registers.

Dependencies and integration: included by `goya_regs.h`, block-base defined by `goya_blocks.h` as `mmDMA_QM_4_BASE`, and protected by `goya_security.c`. It is paired with `dma_ch_4_regs.h` and channel 4 debug/trace bases.

Risks: QMAN 4 and channel 4 are adjacent (`0x420000` and `0x421000`), so off-by-window mistakes are plausible. Incorrect secure properties or error configuration affect isolation and fault handling for this DMA channel.

Test signals: channel 4 queue execution, CQ completions, stop/idle polling, CP fence behavior, forced error-message generation, and protection-bit coverage of the QMAN 4 register window.
