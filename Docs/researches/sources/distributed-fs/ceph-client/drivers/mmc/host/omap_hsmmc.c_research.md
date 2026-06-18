# sources/distributed-fs/ceph-client/drivers/mmc/host/omap_hsmmc.c

## Purpose
`omap_hsmmc.c` drives the OMAP2430/3430 and related TI high-speed MMC controller family. It provides DMA-backed request execution, regulator and pbias power handling, voltage switching, runtime PM, SDIO wake IRQ support, debugfs register visibility, and DT/platform-data compatibility.

## Important APIs, Types, And Functions
`struct omap_hsmmc_host` tracks the MMC host, active request/command/data, clocks, regulators, IRQ and wake IRQ, DMA channels, saved register context, power mode, flags such as `AUTO_CMD23`, and pre-request DMA cookie state. Probe path `omap_hsmmc_probe()` parses OF/platform data, maps registers, enables runtime PM, configures bus power, requests DMA/IRQ resources, installs wake IRQ if possible, and registers the host. Core ops include `omap_hsmmc_request()`, `omap_hsmmc_set_ios()`, `omap_hsmmc_enable_sdio_irq()`, `omap_hsmmc_pre_req()`, and `omap_hsmmc_post_req()`.

## Control Flow
Requests prepare DMA in `omap_hsmmc_prepare_data()` and `omap_hsmmc_setup_dma_transfer()`. If CMD23 is present and hardware auto-CMD23 is unavailable, the SBC is issued first; its command-complete path starts DMA and the real command. IRQ handling loops over `STAT`, delegates to `omap_hsmmc_do_irq()`, maps error bits to command/data errors, resets command/data FSMs on faults, and completes commands/transfers. DMA completion clears `dma_ch`, unmaps if needed, and may finish a request that already saw transfer complete.

## State And Persistence
Runtime state includes active request flags, saved `CON/HCTL/SYSCTL/CAPA` context, `power_mode`, regulator enable booleans, DMA cookie cache, SDIO IRQ enable, and context-loss count. State is restored after runtime resume but not persisted across driver unload.

## Dependencies And Integration Points
The driver integrates MMC core, DMAengine, OF matches, legacy `hsmmc-omap` platform data, regulators (`vmmc`, `vqmmc`/`vmmc_aux`, `pbias`), pinctrl idle/default states, runtime/system PM, wake IRQ infrastructure, GPIO slot helpers, and debugfs.

## Risks And Test Signals
Risk areas include DMA completion versus transfer-complete ordering, command/data FSM reset paths, runtime suspend while SDIO IRQ is pending, voltage switch sequencing, boot regulator usecount correction, and broken-multiblock-read quirks. Test signals include DMA read/write with pre/post request, CMD23 and auto-CMD23 paths, busy-response commands without data, SDIO wake from runtime suspend, context-loss restore, regulator/pbias transitions, debugfs register reads, and erratum-driven multi-IO quirk behavior.
