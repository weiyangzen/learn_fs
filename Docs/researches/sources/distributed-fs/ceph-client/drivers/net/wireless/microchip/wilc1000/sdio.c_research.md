<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/sdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/sdio.c

## Purpose
This file is the SDIO bus binding for the Microchip WILC1000/WILC3000 wireless driver. It registers the `wilc1000_sdio` driver, adapts Linux SDIO CMD52/CMD53 operations to the common `struct wilc_hif_func` host-interface table, probes the chip, registers cfg80211/wiphy state, creates the first station netdev, and handles SDIO suspend/resume.

## Important APIs, Types, And Functions
The private `struct wilc_sdio` tracks SDIO-specific state: whether out-of-band IRQ GPIO mode is used, the negotiated block size, initialization state, and a small global CMD53 bounce buffer for register-sized transfers. `struct sdio_cmd52` and `struct sdio_cmd53` are compact command descriptors consumed by `wilc_sdio_cmd52()` and `wilc_sdio_cmd53()`.

Driver entry points are `wilc_sdio_probe()`, `wilc_sdio_remove()`, `wilc_sdio_suspend()`, and `wilc_sdio_resume()`. The exported host-interface table `wilc_hif_sdio` supplies `hif_init`, `hif_deinit`, register read/write, block RX/TX, interrupt read/clear/size, interrupt sync, IRQ claim/release, reset, and init-status callbacks to the WILC core in `wlan.c`.

Core bus helpers include `wilc_sdio_set_func0_csa_address()` for AHB window selection through function-0 FBR CSA registers, `wilc_sdio_set_block_size()` for CCCR block-size programming, `wilc_sdio_read_reg()` and `wilc_sdio_write_reg()` for vendor register and AHB register access, and `wilc_sdio_read()`/`wilc_sdio_write()` for aligned CMD53 block and byte transfers.

## Control Flow
Probe allocates `struct wilc_sdio` and its CMD53 bounce buffer, calls `wilc_cfg80211_init()` with `WILC_HIF_SDIO` and `wilc_hif_sdio`, discovers optional out-of-band IRQ mapping from device tree when enabled, binds driver data to the `sdio_func`, enables the optional RTC clock, temporarily initializes the SDIO function, reads the chip id, registers cfg80211, loads the MAC address from chip NVM, deinitializes the SDIO function, and creates a default station interface through `wilc_netdev_ifc_init()`.

SDIO initialization enables function-1 CSA, programs 512-byte block size for functions 0 and 1, enables function 1, waits for IOR readiness, and enables master/function interrupt bits in `SDIO_CCCR_IENx`. Deinit disables interrupts, disables functions, clears function-1 CSA, and marks the bus uninitialized. Register access routes low vendor-specific addresses 0xf0-0xff through CMD52 and all other addresses through function-0 CSA plus CMD53 data register access. Bulk transfers use function 1 when `addr == 0` and function 0 CSA windows otherwise.

Interrupt handling either claims the SDIO IRQ and calls `wilc_handle_isr()` with the SDIO host temporarily released, or configures external IRQ bits through `wilc_sdio_sync_ext()`. `wilc_sdio_read_int()` combines the firmware DMA size and IRQ flags into the common interrupt status word. `wilc_sdio_clear_int_ext()` translates common clear/VMM bits to WILC1000 or WILC3000 SDIO control registers.

Suspend disables the optional RTC clock, notifies firmware of host sleep, disables SDIO IRQs, and requests `MMC_PM_KEEP_POWER`. Resume re-enables the RTC clock, reinitializes SDIO, reclaims IRQs, and sends host wake notification.

## State And Persistence
Persistent bus state is limited to `wilc->bus_data` (`struct wilc_sdio`), `wilc->dev`, `wilc->dev_irq_num`, the optional `wilc->rtc_clk`, and `sdio_set_drvdata()`. Firmware-visible state such as function enable, block size, CSA, IRQ enable, VMM table selection, and wake/sleep status is reprogrammed by init/resume and cleared by deinit. The wiphy/netdev objects created during probe persist until remove.

## Dependencies And Integration Points
This file depends on Linux MMC/SDIO core APIs, DT IRQ lookup, optional clock handling, WILC cfg80211/netdev setup, and the common WILC core bus contract in `wlan.h`. It is paired with `wlan.c` for actual TX/RX/VMM, firmware lifecycle, and power-save handshakes, and with `wlan_cfg.c` for configuration packet responses.

## Risks
The CMD52/CMD53 paths manually set `func->num` and `func->cur_blksize`, so concurrent or unexpected SDIO core use would be risky without the surrounding host claim. AHB register access depends on correct three-byte CSA programming and little-endian conversion. IRQ flag mapping differs between WILC1000 and WILC3000 and between SDIO IRQ and external GPIO modes. Probe error paths must pair wiphy registration, IRQ mapping disposal, netdev cleanup, and private buffer free without double-free. Suspend/resume assumes firmware sleep notification succeeds before SDIO IRQs are disabled.

## Test Signals
Useful validation includes SDIO probe/remove with and without out-of-band IRQ GPIO, successful chip-id read and NVM MAC load, block and byte CMD53 transfers around 512-byte boundaries, interrupt delivery and VMM clear for WILC1000 and WILC3000, suspend/resume with `MMC_PM_KEEP_POWER`, firmware wake/sleep notification, and error-injection on CMD52/CMD53 failures. Runtime signals are absence of SDIO core warnings, successful cfg80211 registration, RX/TX progress through `wilc_handle_isr()`, and clean module unload/reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/sdio.c -->
