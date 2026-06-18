<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/spi.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/spi.c

## Purpose
This file is the SPI bus binding and protocol implementation for the Microchip WILC1000/WILC3000 wireless driver. It registers `wilc1000_spi`, manages optional power/reset GPIOs and RTC clocking, implements the WILC SPI command protocol including DMA transfers and command/data CRC support, and exposes the common WILC host-interface operations through `wilc_hif_spi`.

## Important APIs, Types, And Functions
Module parameters `enable_crc7` and `enable_crc16` control command and data checksum protection. `struct wilc_spi` stores bus initialization state, CRC probing state, active CRC mode, and optional enable/reset GPIO descriptors. Packed protocol structures `struct wilc_spi_cmd`, `struct wilc_spi_rsp_data`, `struct wilc_spi_read_rsp_data`, and `struct wilc_spi_special_cmd_rsp` describe the command/response wire layout.

Probe/remove are handled by `wilc_bus_probe()` and `wilc_bus_remove()`. Low-level transfer helpers are `wilc_spi_tx()`, `wilc_spi_rx()`, and `wilc_spi_tx_rx()`. Protocol helpers include `wilc_spi_single_read()`, `wilc_spi_write_cmd()`, `wilc_spi_dma_rw()`, `spi_data_write()`, `spi_data_rsp()`, `wilc_spi_special_cmd()`, `spi_internal_read()`, and `spi_internal_write()`. Host-interface callbacks are implemented by `wilc_spi_init()`, `wilc_spi_deinit()`, `wilc_spi_read_reg()`, `wilc_spi_write_reg()`, `wilc_spi_read()`, `wilc_spi_write()`, `wilc_spi_read_int()`, `wilc_spi_clear_int_ext()`, `wilc_spi_sync_ext()`, and `wilc_spi_reset()`.

## Control Flow
Probe allocates SPI private state, initializes common WILC cfg80211 state with `WILC_HIF_SPI`, records the SPI IRQ as `wilc->dev_irq_num`, parses optional `enable` and `reset` GPIOs, enables the optional RTC clock, powers the chip, configures the SPI protocol, reads the chip id, registers cfg80211, loads the MAC address from NVM, powers the chip back down, and creates the default station netdev.

The protocol starts by inferring the chip's current CRC7 setting in `wilc_spi_configure_bus_protocol()`: it tries internal reads with the requested CRC7 mode and then the opposite mode, disables CRC16 checks during probing, writes the desired CRC7/CRC16 and 8 KiB data packet size into the protocol register, and updates `struct wilc_spi` to match. Register reads/writes choose internal commands for clockless addresses and single read/write commands for normal registers. On non-clockless failures, the code retries up to `SPI_RETRY_MAX_LIMIT`, issuing a WILC reset command and short delay between attempts.

DMA block writes first send a DMA EXT WRITE command, stream one or more data packets tagged first/inner/last, optionally append CRC16 per data packet, then read and validate the final data response. DMA reads send a DMA EXT READ command, poll for each data-start header, read packet chunks, and optionally validate CRC16. Interrupt sync programs pin mux and interrupt-enable registers. Clear uses an internal write/read retry to ensure `EN_VMM` took effect.

## State And Persistence
The active bus state is `struct wilc_spi`: `isinit`, CRC mode booleans, and GPIOs. `wilc_wlan_power()` persists physical chip power state through enable/reset GPIO levels. Firmware-visible SPI protocol state persists in the WILC SPI protocol register and may survive module unload, which is why CRC probing is needed. The common WILC object owns cfg80211, netdev, chip id, and power-save state.

## Dependencies And Integration Points
This file integrates with Linux SPI, GPIO descriptor APIs, optional clock APIs, CRC7 and CRC-ITU-T helpers, WILC cfg80211/netdev setup, and the common WILC `wlan.c` core through `struct wilc_hif_func`. It relies on register constants and chip id helpers from `wlan.h`, and on board descriptions providing usable IRQ, reset, and optional enable pins.

## Risks
SPI command parsing is sensitive to undocumented response padding before the data start tag; the code searches a bounded extra header area. CRC probing can misdiagnose bus faults as CRC mismatch. TX/RX helper allocations per transfer are simple but can be expensive on high-rate paths. Retry/reset recovery is disabled for clockless registers and can still leave the chip in a partially configured protocol state. `wilc_spi_read()` and `wilc_spi_write()` reject transfers of four bytes or less, so callers must use register helpers for small accesses. Error unwind in probe must power down before freeing common objects.

## Test Signals
Test SPI probe with reset-only and enable+reset GPIO wiring, requested CRC7/CRC16 modes, module unload/reload without hardware reset, high SPI clock reads that trigger padded response handling, DMA transfers larger than 8 KiB, register access to clockless and normal addresses, interrupt clear/sync, and induced SPI transaction failures to exercise reset retry. Successful signals include stable chip id validation, NVM MAC load, cfg80211 registration, TX/RX traffic, and no CRC mismatch logs under clean wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/spi.c -->
