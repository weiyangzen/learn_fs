# sources/distributed-fs/ceph-client/drivers/mmc/host/mxs-mmc.c

## Purpose
`mxs-mmc.c` drives the Freescale MXS SSP-based MMC controller for i.MX23/i.MX28 platforms. It uses the MXS SSP block and DMAengine to submit command descriptor words and data scatterlists, supports polling or GPIO/native card detection, and exposes SD/MMC/SDIO-capable host operations.

## Important APIs, Types, And Functions
`struct mxs_mmc_host` embeds `struct mxs_ssp` and tracks the active MMC request, command, data, bus width, SDIO IRQ enable, and broken-card-detect flag. `mxs_mmc_probe()` maps registers, obtains the clock/regulator/DMA channel, resets the SSP, sets MMC caps and transfer limits, requests the IRQ, and registers the host. Request processing is divided by command type across `mxs_mmc_bc()`, `mxs_mmc_ac()`, `mxs_mmc_adtc()`, and `mxs_mmc_start_cmd()`. `mxs_mmc_prep_dma()` prepares both command PIO-word descriptors and data descriptors. IRQ and completion paths are `mxs_mmc_irq_handler()`, `mxs_mmc_dma_irq_callback()`, and `mxs_mmc_request_done()`.

## Control Flow
`mxs_mmc_request()` stores the request and starts CMD23 (`mrq->sbc`) first if present; otherwise it starts the main command. Command setup writes SSP PIO words and submits DMA descriptors. ADTC commands first submit command words, then attach the data SG DMA descriptor. The DMA callback reads responses, unmaps data, advances from CMD23 to the main command, optionally sends a stop command, and finally calls `mmc_request_done()`. The hardware IRQ mostly records error status and SDIO IRQ events; the DMA callback is the normal completion edge.

## State And Persistence
All state is transient in `mxs_mmc_host` and the embedded `mxs_ssp`. The driver remembers current bus width and SDIO IRQ enable across resets so `mxs_mmc_reset()` reprograms IRQ-check bits. There is no persistent storage.

## Dependencies And Integration Points
The driver depends on MXS SSP register definitions/helpers, `stmp_reset_block()`, DMAengine, the MMC core, OF compatibles, regulator and clock frameworks, GPIO card-detect helpers, and PM sleep hooks.

## Risks And Test Signals
Key risks are descriptor sequencing, mapping/unmapping on descriptor preparation failure, timeout tick calculation, SDIO IRQ interaction with continuous clocking, and card-detect polarity/polling behavior. Test signals include successful i.MX23/i.MX28 probe, DMA channel acquisition, command-only and data command completion, CMD23 flows, stop command issuance, SDIO interrupt signaling, broken-CD behavior, and suspend/resume clock state.
