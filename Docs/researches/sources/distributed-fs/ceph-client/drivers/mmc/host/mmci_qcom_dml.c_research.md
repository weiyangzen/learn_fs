# sources/distributed-fs/ceph-client/drivers/mmc/host/mmci_qcom_dml.c Research

## sources/distributed-fs/ceph-client/drivers/mmc/host/mmci_qcom_dml.c

### Purpose
`mmci_qcom_dml.c` supplies the Qualcomm-specific Data Mover Lite glue for the common MMCI driver. Qualcomm SDCC integrations use the normal MMCI DMA-engine path plus an SDCC-local DML block at `host->base + 0x800` to connect producer/consumer CRCI signaling and BAM pipe IDs for read/write DMA transfers.

### Important APIs, Types, And Functions
The only externally visible function is `qcom_variant_init(struct mmci_host *host)`, which installs `qcom_variant_ops`. The callback table overrides `.prep_data`, `.unprep_data`, `.get_datactrl_cfg`, `.get_next_data`, `.dma_setup`, `.dma_release`, `.dma_start`, `.dma_finalize`, and `.dma_error`. Key helpers are `qcom_dma_setup()`, `qcom_dma_start()`, `of_get_dml_pipe_index()`, and `qcom_get_dctrl_cfg()`. Register definitions cover `DML_CONFIG`, reset/start registers, producer/consumer pipe sizes, pipe IDs, and producer BAM block/transaction sizes.

### Control Flow
During MMCI probe, the Qualcomm `variant_data` calls `qcom_variant_init()`, replacing the base ops. `qcom_dma_setup()` first calls `mmci_dmae_setup()` to acquire standard `"rx"`/`"tx"` DMA channels. It then reads the DMA phandle arguments named `"tx"` and `"rx"` to derive the consumer and producer DML pipe IDs; missing IDs cause DMA release and setup failure. On success it resets DML, disables CRCI bypass/direct/infinite modes, programs producer/consumer logical pipe sizes to 4096 bytes, writes the pipe ID register, and uses `mb()` to order initialization. Per transfer, `qcom_dma_start()` delegates descriptor submission to `mmci_dmae_start()`, then programs DML for producer mode on reads or consumer mode on writes, sets block and transaction sizes for reads, toggles `PRODUCER_TRANS_END_EN`, starts the selected DML side, and finishes with `wmb()` before the MMCI data path is triggered by the core.

### State, Persistence, And Dependencies
This file stores no separate private structure; it uses `host->base`, `host->data`, `host->mmc`, and the DMA-engine private data allocated by `mmci_dmae_setup()`. Persistent hardware state is the DML configuration, pipe IDs, logical pipe sizes, block size, transaction size, and producer/consumer start registers. Dependencies are DT `"dmas"`/`"dma-names"` properties, the DMA engine path in `mmci.c`, MMC data flags, and Qualcomm SDCC hardware layout with DML at offset `0x800`.

### Integration Points
The file integrates through the MMCI variant hook selected by the Qualcomm AMBA ID in `mmci.c`. It assumes both the standard MMCI DMA channels and DML pipe IDs refer to the same hardware data path. `qcom_get_dctrl_cfg()` differs from classic MMCI by encoding the block size directly as `host->data->blksz << 4`, matching the Qualcomm variant flag that accepts arbitrary block sizes.

### Risks
DML and DMA ordering is the core risk: the BAM/DML producer or consumer must be configured before the MMCI data-control register starts the transfer. Pipe ID extraction assumes the first DMA phandle argument is the BAM pipe ID; malformed DT silently disables DMA. The setup path returns `-EINVAL` for several distinct failures, reducing diagnosability. Read and write paths use different CRCI and producer-end semantics; swapping `"rx"`/`"tx"` names or pipe IDs can hang DMA rather than fail cleanly. There is no PIO-specific DML bypass programming here, so fallback behavior depends on reset/default DML state after failed setup.

### Test Signals
Validate with Qualcomm SDCC hardware using DMA reads and writes, including multi-block transfers and arbitrary block sizes. DT tests should cover missing `"rx"`/`"tx"` names, bad phandles, and swapped pipe IDs. Instrumentation should confirm DML reset/setup occurs once at probe, producer registers are used for reads, consumer start is used for writes, `mmci_dmae_start()` errors abort before DML starts, and PIO fallback still works when DML setup fails.
