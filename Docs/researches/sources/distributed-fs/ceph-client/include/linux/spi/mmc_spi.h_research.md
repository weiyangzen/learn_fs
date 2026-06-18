<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/mmc_spi.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/mmc_spi.h

Purpose: This header defines platform glue for managing MMC/SD card slots over SPI.

Important APIs/types/functions: `mmc_spi_platform_data` provides optional `init()` and `exit()` hooks for card-detect IRQ setup, MMC capability masks, card-detect debounce delay, power-up delay, OCR voltage mask, and `setpower()` callback. Accessors are `mmc_spi_get_pdata()` and `mmc_spi_put_pdata()`.

Control flow: The mmc_spi driver obtains platform data at probe, calls `init()` with an IRQ callback if needed, sets MMC host capabilities/voltage, handles power changes through `setpower()`, and calls `exit()` on teardown.

State and persistence: Platform data is static; card detect, power, and host state are owned by the MMC/SPI driver. The accessor pair may allocate or reference firmware-derived data.

Dependencies/integration: Depends on SPI, interrupt handling, MMC host core, device power callbacks, and board-specific card slot wiring.

Risks and test signals: Risks include wrong voltage OCR, missing debounce causing card flaps, sleeping in IRQ callbacks, and unbalanced pdata get/put. Test card insertion/removal, power cycling, voltage negotiation, suspend/resume, and polling-capable slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/mmc_spi.h -->
