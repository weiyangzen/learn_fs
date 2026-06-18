# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_qm_2_regs.h

Purpose: auto-generated register-address map for DMA queue manager 2, the QMAN instance at `0x410000` associated with DMA channel 2.

Important APIs/types/functions: no C API beyond `mmDMA_QM_2_*` macros. It mirrors the QMAN register families: global enable/stop/protection/error/status, PQ base/size/index/push/status/rate-limit, CQ config/pointers/status/rate-limit/IFIFO, CP message-base and LDMA offset registers, fence counters, CP status/current instruction/barrier/debug, and internal PQ/CQ buffer debug access.

Control flow: declarative. The driver uses the constants during QMAN initialization, job submission, completion processing, stop/reset, and error handling. Field definitions come from the shared queue-manager mask layout in `dma_qm_0_masks.h`.

State and persistence: register state is persistent in the hardware block until reset or reprogramming. In-flight work and status are live hardware state; queue buffers are memory referenced by the base registers.

Dependencies and integration: included through `goya_regs.h`; `goya_blocks.h` defines `mmDMA_QM_2_BASE`; `goya_security.c` includes this instance when calculating protected QMAN register ranges.

Risks: address-copy errors between QMAN instances can make the driver poll or program the wrong engine. Since secure properties and error-message registers are per instance, wrong values can create isolation or diagnosability gaps for channel 2 traffic.

Test signals: DMA channel 2 submissions and completions, idle/stop polling, fence and CP status validation, error-injection with message delivery, and protection-bit validation for the `0x410000` register window.
