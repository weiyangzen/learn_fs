# sources/distributed-fs/ceph-client/drivers/mmc/host/wmt-sdmmc.c

## Purpose
This file implements the WonderMedia WM8505/WM8650 SD/MMC host controller driver (`wmt-sdhc`) as an OF/platform MMC host with a separate DMA engine.

## Important APIs, types, and functions
- `struct wmt_mci_priv` stores MMIO base, regular and DMA IRQs, coherent DMA descriptor buffer, command/data completions, active request/command, clock, device pointer, and polarity flags.
- `struct wmt_mci_caps` describes controller limits supplied through OF match data.
- `wmt_mci_ops` provides MMC `.request`, `.set_ios`, `.get_ro`, and `.get_cd`.
- `wmt_mci_probe()` reads OF match/device data, maps registers, requests regular and DMA IRQs, allocates coherent descriptors, obtains/enables the SDMMC clock, resets hardware, and registers the MMC host.
- `wmt_mci_regular_isr()` and `wmt_mci_dma_isr()` jointly complete command and data phases.
- DMA helpers initialize descriptors, configure direction, enable interrupts, and start the DMA controller.

## Control flow
`wmt_mci_request()` stores the active request and command, converts MMC response type values into controller encodings, and chooses a non-data or data path. Non-data commands are programmed by `wmt_mci_send_command()` and started; completion occurs in `wmt_mci_regular_isr()`. Data requests initialize a command completion, reset/enable DMA, program block length/count, map the SG list, create one descriptor per block-sized chunk, mark the last descriptor with `DMA_RBR_END`, configure DMA direction, send the command, initialize data completion, start DMA, and then start the command.

The regular ISR handles card insertion/removal/device-insertion status first, aborting active command/DMA completions when needed. For non-data and stop commands, it handles command-done and timeout bits, reads responses, clears active command, and calls `mmc_request_done()`. For data commands, it completes `comp_cmd` on command response or timeout and, if DMA has already completed, calls `wmt_complete_data_request()`. The DMA ISR checks the DMA completion event code, marks data timeout on non-success, disables DMA, completes `comp_dma`, and finishes the request when command completion is already done. `wmt_complete_data_request()` unmaps DMA, sets bytes transferred, reads the original command response, and sends a stop command when required.

## State and persistence
The driver keeps only volatile kernel/hardware state. `priv->req`, `priv->cmd`, `priv->comp_cmd`, and `priv->comp_dma` represent the active transaction. OF booleans `sdon-inverted` and `cd-inverted` configure polarity behavior. Suspend/resume reset selected hardware bits and gate the clock; there is no saved register image beyond reset-time defaults.

## Dependencies and integration points
The driver depends on platform/OF APIs, IRQ mapping, MMIO accessors, coherent DMA allocation, DMA mapping, Linux clock framework, and MMC core. Device-tree compatible `"wm,wm8505-sdhc"` selects `wm8505_caps`.

## Risks and edge cases
- Descriptor generation assumes block-sized chunks and enough coherent descriptor space for `mmc->max_blk_count`; malformed SG/block combinations could underdescribe data if lengths are not multiples of block size.
- Request state is global per host and not explicitly locked; MMC core serialization and interrupt ordering are assumed.
- `wmt_dma_init()` returns `1` on failure, but callers do not check it.
- Error handling maps any non-success DMA event to `-ETIMEDOUT`, losing event specificity.
- `wmt_mci_remove()` resets and frees DMA before `mmc_remove_host()`, which is a teardown ordering detail worth reviewing against active requests.

## Test signals
Test OF probe with both IRQs and clock present, card-detect polarity variants, read/write single and multi-block DMA transfers, stop-command handling, response parsing, card insertion/removal IRQs, DMA error event injection, suspend/resume, and clock-rate changes through `.set_ios()`.
