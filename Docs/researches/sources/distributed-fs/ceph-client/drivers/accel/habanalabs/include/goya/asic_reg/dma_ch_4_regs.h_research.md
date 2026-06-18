# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_4_regs.h

Purpose: auto-generated Goya register-address map for DMA channel 4, another `DMA_CH` instance. It gives the driver the offsets needed to program the fifth DMA channel's linear and tensor transfer engines.

Important APIs/types/functions: no functions or structs are present. The API is the `mmDMA_CH_4_*` macro set rooted at `0x421000`: global configs, error-message and read/write completion message registers, LDMA source/destination address and size registers, transfer commit, status registers, rate limiting controls, TDMA source/destination base and five ROI dimensions, and `MEM_INIT_BUSY`.

Control flow: the file is declarative. Driver control flow writes these registers via MMIO: initialize configuration and notification targets, stage LDMA or TDMA fields, commit, then observe status/completion/error registers. Stop/reset/protection logic targets the block through `goya_blocks.h`.

State and persistence: channel state is hardware-resident. Descriptors, rate-limiter configuration, error-message configuration, and in-flight transfer state remain in the channel until changed or reset. `goya_blocks.h` defines `mmDMA_CH_4_BASE` and a wider section than channels 0-3, so callers must use the block table instead of inferring layout solely from channel 3.

Dependencies and integration: included by `goya_regs.h`. `goya_security.c` protects `mmDMA_CH_4_BASE`; `goya_coresight.c` exposes channel 4 trace, CTI, ETF, SPMU, and bus-monitor bases. The queue-manager 4 register window in `dma_qm_4_regs.h` is adjacent and typically feeds this channel.

Risks: channel 4 is structurally similar to channel 3 but has a different base (`0x421000`) and block section size, so copy-paste errors can program or protect the wrong engine. Incorrect LDMA/TDMA address fields can corrupt device or host memory, and stale completion/error target registers can send notifications to the wrong queue.

Test signals: compile inclusion through `goya_regs.h`, DMA channel 4 transfer smoke tests, error-path tests that force message writes, security block protection validation, status/idle polling after stop/reset, and CoreSight/bus-monitor activity for channel 4.
