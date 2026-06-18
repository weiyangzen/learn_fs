# sources/distributed-fs/ceph-client/drivers/mmc/host/davinci_mmc.c

Purpose: implements the TI DaVinci/DA8xx MMC/SD/SDIO host controller driver. It exposes classic `mmc_host_ops`, supports PIO and DMAEngine transfers, handles card-detect/write-protect/platform power hooks, SDIO IRQs, CPU-frequency clock recalculation, and platform/OF probing.

Important APIs and functions: module parameters tune `rw_threshold`, `poll_threshold`, `poll_loopcount`, and `use_dma`. MMC ops are `mmc_davinci_request`, `mmc_davinci_set_ios`, `mmc_davinci_get_cd`, `mmc_davinci_get_ro`, and `mmc_davinci_enable_sdio_irq`. Core helpers include `mmc_davinci_prepare_data`, `mmc_davinci_start_command`, `mmc_davinci_irq`, `mmc_davinci_xfer_done`, DMA helpers, `calculate_clk_divider`, `init_mmcsd_host`, probe/remove, and sleep PM callbacks.

Control flow: probe maps registers, enables the functional clock, parses OF or platform data, initializes the controller, optionally acquires TX/RX DMA channels, configures MMC limits, registers a cpufreq notifier, adds the MMC host, and requests normal plus optional SDIO IRQs. A request waits for the controller not busy, prepares data registers/FIFO/DMA or PIO scatterlist iteration, then starts the command and enables calculated interrupts. IRQ handling reads and clears one-shot status, services PIO FIFO thresholds, maps command/data timeouts and CRC errors, aborts/reset data on failures, finishes data, and optionally sends a stop command.

State and persistence: `struct mmc_davinci_host` stores current command/data pointers, clock, MMIO base, IRQs, bus mode, data direction, remaining bytes, DMA channels, active-request flags, scatterlist iterator, controller version, timeout cycle conversion, and optional cpufreq notifier. Hardware state is register-based and reinitialized on probe/resume; no persistent storage is kept.

Dependencies and integration points: depends on Linux MMC core, DMAEngine, clocks, platform data `linux/platform_data/mmc-davinci.h`, GPIO slot helpers, cpufreq notifier support, OF/platform matching, and platform power/card-detect callbacks.

Risks: the open-drain divider path uses a zeroed local `mmc_pclk`, which appears suspicious for initial-clock calculation. DMA only works for threshold-aligned total and segment lengths, otherwise it falls back to PIO. IRQ status is read-to-clear and race-prone if masks are changed after status reads; the driver explicitly masks during PIO loops to reduce spurious interrupts. Error paths reset command/data logic and may terminate DMA broadly. Platform-data parsing contains an oddly formatted brace, and many failures degrade to PIO rather than failing probe.

Test signals: build for DaVinci/DA8xx configs, probe via platform data and OF, PIO and DMA read/write including unaligned fallback, SDIO IRQ signaling, card-detect/write-protect GPIO behavior, cpufreq clock changes, suspend/resume, and forced timeout/CRC paths.
