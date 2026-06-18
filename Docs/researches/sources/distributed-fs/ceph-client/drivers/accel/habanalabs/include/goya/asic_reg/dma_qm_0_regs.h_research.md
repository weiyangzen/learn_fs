# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_qm_0_regs.h

Purpose: auto-generated register-address map for DMA queue manager 0, the QMAN instance at `0x400000` that schedules and feeds DMA channel 0.

Important APIs/types/functions: no C functions or types. The `mmDMA_QM_0_*` macros describe global config/protection/error/status registers, producer queue base/size/indices/config/push/status/rate-limit registers, completion queue configuration and status registers, command processor message-base and LDMA offset registers, fence counters, CP status/current instruction/barrier/debug registers, and PQ/CQ buffer debug windows.

Control flow: declarative register map. Runtime driver flow uses these addresses to configure queue memory, enable the QMAN, push DMA jobs, process completions, poll idle/stop status, and handle errors. Bitfield operations use `dma_qm_0_masks.h`.

State and persistence: queue configuration, PI/CI indices, CP message bases, security properties, and rate limits live in hardware registers until changed or reset. Queue contents live in memory referenced by the base/size registers; this header only names the control registers.

Dependencies and integration: included by `goya_regs.h`. `goya_security.c` calculates protection bit words from many `mmDMA_QM_0_*` addresses, so address alignment and offsets are part of the security model. `goya_masks.h` uses the companion mask header to create DMA QMAN aggregate constants.

Risks: wrong offsets can corrupt queue state or protection-bit calculations. The QMAN register window is cloned across instances, so instance-specific code should not hard-code `DMA_QM_0` when programming channels 1-4 unless deliberately using shared layout masks.

Test signals: queue bring-up, producer/completion queue accounting, command processor fence behavior, error-message generation, stop/idle polling using `DMA_QM_IDLE_MASK`, and protection-bit tests in secure/non-secure execution paths.
