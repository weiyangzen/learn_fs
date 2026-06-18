
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/k3dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/k3dma.c

Purpose: implements a HiSilicon K3 platform DMAEngine controller with physical channels multiplexed across virtual request channels. It supports memcpy, slave scatter-gather, cyclic DMA, runtime pause/resume/terminate, residue reporting, OF DMA translation, and suspend/resume.

Important APIs and control flow: `k3_dma_probe()` maps MMIO, reads `dma-channels`, `dma-requests`, and optional `dma-channel-mask`, gets the clock unless a SoC flag disables it, requests the shared IRQ, creates an LLI DMA pool, initializes physical and virtual channels, registers DMAEngine, and registers an OF DMA controller. `k3_dma_issue_pending()` moves virtual descriptors to the issued queue and adds channels to `chan_pending`; `k3_dma_tasklet()` assigns free physical channels and starts queued work with `k3_dma_start_txd()`. `k3_dma_int_handler()` processes TC1 completion, TC2 cyclic period callbacks, error bits, acknowledges raw interrupt registers, and schedules the tasklet. Preparation functions build hardware LLI chains for memcpy, slave SG, and cyclic transfers. `k3_dma_tx_status()` computes residue from queued descriptors or current hardware LLI/count registers.

State and persistence behavior: `struct k3_dma_dev` stores global MMIO, tasklet, lock, pending virtual-channel list, physical channel array, virtual channel array, clock, LLI pool, and masks. Each virtual channel stores configuration, physical assignment, status, cyclic flag, and slave config. Each physical channel tracks current and completed descriptors. Descriptor state persists in DMA-pool-allocated LLI blocks until virt-dma frees them.

Dependencies and integration points: depends on `virt-dma`, DMAEngine, OF DMA, platform IRQ/resources, clocks, DMA pools, and DT compatibles `hisilicon,k3-dma-1.0` and `hisilicon,hisi-pcm-asp-dma-1.0`. Clients acquire channels by request ID through `k3_of_dma_simple_xlate()`.

Risks and test signals: risks include `clk_prepare_enable()` on an optional/NOCLK clock pointer, channel-mask width assumptions, residue math based on current LLI address, status not always transitioned for paused/completed cases, cyclic chain size limits, and shared tasklet scheduling races between physical and virtual channel locks. Test signals include OF channel lookup by request, memcpy splitting at `DMA_MAX_SIZE`, SG and cyclic audio transfers, TC1/TC2 interrupt behavior, pause/resume removing and requeueing channels, suspend rejection while hardware is active, and no LLI pool leaks after terminate/free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/k3dma.c -->
