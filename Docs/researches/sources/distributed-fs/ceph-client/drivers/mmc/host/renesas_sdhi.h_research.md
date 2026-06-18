# sources/distributed-fs/ceph-client/drivers/mmc/host/renesas_sdhi.h

## Purpose
`renesas_sdhi.h` is the shared private interface for the Renesas SDHI driver family. It defines SoC capability data, tuning/quirk structures, DMA-private state, the per-host private object, and exported lifecycle functions used by the DMA front-end drivers.

## Important APIs, Types, And Functions
`struct renesas_sdhi_of_data` describes TMIO flags, OCR/capabilities, DMA bus width and offsets, bus shift, SCC tuning offset/taps, block and segment limits, and SDHI flags. `struct renesas_sdhi_quirks` records HS400, tap correction, fixed-address DMA, one-RX-DMAC, and INFO1 layout quirks. `struct renesas_sdhi_dma` stores DMA end flags, bus width, DMA filter, core DMA-enable callback, completion, and work item. `struct renesas_sdhi` is the core private state containing clocks, TMIO data, DMA state, quirks, pinctrl/SCC/tuning data, reset control, TMIO host, and optional regulator device. The header declares `renesas_sdhi_probe()`, `renesas_sdhi_remove()`, `renesas_sdhi_suspend()`, and `renesas_sdhi_resume()`.

## Control Flow
There is no executable logic beyond the `host_to_priv()` container macro and `sdhi_has_quirk()` helper. Runtime flow is implemented by `renesas_sdhi_core.c` and the DMA variants using these contracts.

## State And Persistence
The structures define volatile in-kernel state for clocks, tuning decisions, DMA end coordination, card type, and regulator/reset handles. No persistent state exists.

## Dependencies And Integration Points
The header bridges the SDHI core, `tmio_mmc` core, system DMAC and internal DMAC front-ends, platform devices, DMAengine, workqueues, and MMC capabilities.

## Risks And Test Signals
Risks include ABI-like drift between the core and DMA front-ends, incorrect SoC data, and quirk fields changing semantics. Test signals are build coverage of all SDHI variants and runtime validation of tuning, DMA, suspend/resume, and voltage-switch behavior.
