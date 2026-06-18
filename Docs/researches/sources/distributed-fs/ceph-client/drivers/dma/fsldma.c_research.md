# sources/distributed-fs/ceph-client/drivers/dma/fsldma.c

## Purpose
`fsldma.c` is the dmaengine platform driver for Freescale/NXP Elo, EloPlus, and Elo3 DMA controllers on MPC83xx/MPC85xx-style systems. It exposes MEMCPY and limited slave-DMA services, discovers OF child channels, and supports either one controller IRQ or per-channel IRQs.

## Important APIs, Types, And Functions
It uses `fsldma_device`, `fsldma_chan`, and `fsl_desc_sw` from `fsldma.h`. Register helpers hide endian-aware MMIO, descriptor helpers build 32-byte aligned link descriptors, and dmaengine callbacks include `fsl_dma_prep_memcpy`, `fsl_dma_tx_submit`, `fsl_dma_memcpy_issue_pending`, `fsl_tx_status`, `fsl_dma_device_config`, and `fsl_dma_device_terminate_all`. `fsl_dma_external_start()` is exported for external-start users.

## Control Flow
Probe maps controller registers, initializes dmaengine capabilities, probes child channel nodes, requests interrupts, and registers the device. Transfers are prepared as chained link descriptors, queued to `ld_pending`, moved to `ld_running`, and started by programming CDAR plus mode bits. IRQs clear status and schedule a tasklet; the tasklet marks the channel idle, completes running descriptors up to the current hardware pointer, invokes callbacks, frees acked descriptors, and starts the next pending chain.

## State And Persistence Behavior
Runtime state is volatile: MMIO registers, DMA-pool descriptors, pending/running/completed lists, cookies, tasklets, and PM state. Suspend saves only the mode register and refuses to suspend active channels.

## Dependencies And Integration Points
The driver depends on dmaengine/async_tx, DMA pools, OF address/IRQ parsing, platform driver registration, and endian helpers in `fsldma.h`. OF match data supplies address width; child compatible strings select 83xx or 85xx behavior.

## Risks And Test Signals
Risks include resource-offset channel ID derivation, 83xx/85xx bit semantics, halt timeouts, request-count `BUG_ON(size > 1024)`, and incomplete suspend if active. Test with OF probe logs, `dmatest` over large copies, IRQ/tasklet completion, terminate-all, external start, and idle suspend/resume.
