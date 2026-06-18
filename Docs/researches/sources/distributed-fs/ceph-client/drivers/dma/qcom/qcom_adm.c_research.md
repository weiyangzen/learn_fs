# sources/distributed-fs/ceph-client/drivers/dma/qcom/qcom_adm.c

Purpose: Qualcomm ADM DMAEngine slave driver. It exposes 16 DMA slave channels, builds ADM command pointer/descriptor lists for flow-controlled and non-flow-controlled peripheral transfers, and integrates with OF DMA using channel and optional CRCI specifiers.

Important APIs/types/functions: hardware descriptor formats are `struct adm_desc_hw_box` and `struct adm_desc_hw_single`. Driver state is `struct adm_async_desc`, `struct adm_chan`, and `struct adm_device`. DMAEngine hooks are `adm_free_chan`, `adm_prep_slave_sg`, `adm_slave_config`, `adm_issue_pending`, `adm_tx_status`, and `adm_terminate_all`. Hardware helpers include `adm_process_fc_descriptors`, `adm_process_non_fc_descriptors`, `adm_start_dma`, `adm_dma_irq`, and `adm_dma_xlate`.

Control flow: probe maps registers, reads `qcom,ee`, enables core/interface clocks, toggles reset controls, initializes channels, resets CRCIs, configures client interfaces and low-power global control, requests the shared IRQ, registers DMAEngine, and registers OF DMA. Prep validates direction, derives burst/CRCI from `dma_slave_config` and optional `qcom_adm_peripheral_config`, counts needed box/single descriptors, allocates and maps a command-pointer-list buffer, fills descriptors for each SG entry, and returns a virt-dma descriptor. Issue pending starts the first queued descriptor if no current transfer is active. IRQ scans security-domain status for all channels, validates result registers, records errors on failed/flushed results, completes current virt-dma cookie, and starts the next descriptor.

State/persistence: per-channel `curr_txd`, `slave`, `crci`, `mux`, `error`, and `initialized` hold runtime state. Descriptor memory is allocated per transaction and DMA-mapped until virt-dma frees it. Hardware channel configuration is lazily initialized on first start.

Dependencies/integration: depends on clocks, resets, OF DMA, `linux/dma/qcom_adm.h` peripheral config, scatterlist DMA mappings, and virt-dma. Clients use one-cell or two-cell DMA specifiers.

Risks: `common.directions` uses `BIT(DMA_DEV_TO_MEM | DMA_MEM_TO_DEV)`, which is unusual because other drivers use `BIT(DMA_DEV_TO_MEM) | BIT(DMA_MEM_TO_DEV)`; this should be checked if direction capability reporting changes. Residue reporting is descriptor-granularity only. Flow-control descriptor count math depends on valid nonzero burst. IRQ loop scans fixed `ADM_MAX_CHANNELS` even if clients use fewer.

Test signals: OF DMA xlate with one and two args, flow-controlled transfer with valid/invalid CRCI and burst, non-flow-control large SG split at `ADM_MAX_XFER`, IRQ completion/error/flush results, clock/reset failure unwind, and remove while descriptors are active.
